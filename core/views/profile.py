from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.utils.timezone import make_aware
from datetime import datetime
from ..models import UserProblem, Platform, Problem, Topic, UserProfile
from ..cf_api import validate_cf_handle, fetch_cf_submissions, fetch_cf_user_info, rating_to_difficulty
from ..utils.priority import calculate_review_priority


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "save_handle":
            _handle_save(request, profile)
            return redirect("profile")
        elif action == "sync":
            _handle_sync(request, profile)
            return redirect("profile")

    return render(request, "core/profile.html", {"profile": profile})


def _handle_save(request, profile):
    handle = request.POST.get("cf_handle", "").strip()

    if not handle:
        messages.error(request, "Handle cannot be empty.")
        return

    if not validate_cf_handle(handle):
        messages.error(request, f"'{handle}' does not exist on Codeforces. Please double-check.")
        return

    if profile.cf_handle != handle:
        profile.last_cf_submission_id = None
        profile.last_synced = None
        UserProblem.objects.filter(user=request.user).delete()

    profile.cf_handle = handle
    profile.save()
    messages.success(request, f"Handle '{handle}' saved successfully!")


def _handle_sync(request, profile):
    if not profile.cf_handle:
        messages.error(request, "Please save a Codeforces handle before syncing.")
        return

    cf_rating, cf_rank = fetch_cf_user_info(profile.cf_handle)
    if cf_rating:
        profile.cf_rating = cf_rating
        profile.cf_rank = cf_rank

    problems, latest_id, error = fetch_cf_submissions(
        profile.cf_handle,
        since_id=profile.last_cf_submission_id
    )

    if error:
        messages.error(request, f"Sync failed: {error}")
        return

    cf_platform, _ = Platform.objects.get_or_create(
        slug="codeforces",
        defaults={"name": "Codeforces"}
    )

    new_count = 0
    updated_count = 0

    for p_data in problems:
        topic_objs = []
        for tag_name in p_data["tags"]:
            tag_name_clean = tag_name.strip().title()
            if tag_name_clean:
                topic_obj, _ = Topic.objects.get_or_create(name=tag_name_clean)
                topic_objs.append(topic_obj)

        problem, created = Problem.objects.get_or_create(
            platform=cf_platform,
            problem_code=p_data["problem_code"],
            defaults={
                "title": p_data["title"],
                "difficulty": rating_to_difficulty(p_data["rating"]),
                "rating": p_data["rating"],
                "link": p_data["link"],
            }
        )

        if not created and p_data["rating"] is not None and problem.rating != p_data["rating"]:
            problem.rating = p_data["rating"]
            problem.difficulty = rating_to_difficulty(p_data["rating"])
            problem.save()

        if topic_objs:
            problem.topics.add(*topic_objs)

        if p_data["solved"]:
            new_status = "solved"
            practiced_at = make_aware(datetime.fromtimestamp(p_data["solved_at"]))
        else:
            new_status = "unsolved"
            practiced_at = None

        user_problem, up_created = UserProblem.objects.get_or_create(
            user=request.user,
            problem=problem,
            defaults={
                "status": new_status,
                "last_practiced": practiced_at,
                "wrong_attempts": p_data["wrong_attempts"],
            }
        )

        if up_created:
            new_count += 1
        else:
            user_problem.wrong_attempts += p_data["wrong_attempts"]
            if practiced_at:
                user_problem.last_practiced = practiced_at
            if new_status == "solved" and user_problem.status == "unsolved":
                user_problem.status = "solved"
            updated_count += 1

        user_problem.review_priority = calculate_review_priority(user_problem)
        user_problem.save()

    profile.last_synced = timezone.now()
    if latest_id:
        profile.last_cf_submission_id = latest_id
    profile.save()

    messages.success(
        request,
        f"Sync complete! {new_count} new problems added, {updated_count} updated."
    )