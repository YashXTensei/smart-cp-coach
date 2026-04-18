from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from ..models import UserProblem, Platform, Problem, Topic
from ..forms import ManualProblemForm, UserProblemForm
from ..utils.priority import calculate_review_priority
from django.urls import reverse

@login_required
def add_problem(request):
    if request.method == 'POST':
        form = ManualProblemForm(request.POST)
        if form.is_valid():
            manual_platform, _ = Platform.objects.get_or_create(
                slug="manual",
                defaults={"name": "Manual"}
            )
            problem_code = form.cleaned_data['name'].strip().lower().replace(' ', '-')
            problem, created = Problem.objects.get_or_create(
                platform=manual_platform,
                problem_code=problem_code,
                defaults={
                    "title": form.cleaned_data['name'],
                    "difficulty": form.cleaned_data['difficulty'],
                    "rating": form.cleaned_data.get('rating'),
                    "link": "",
                }
            )
            tags_raw = form.cleaned_data.get('tags', '')
            if tags_raw:
                for tag_name in tags_raw.split(','):
                    tag_name_clean = tag_name.strip().title()
                    if tag_name_clean:
                        topic_obj, _ = Topic.objects.get_or_create(name=tag_name_clean)
                        problem.topics.add(topic_obj)

            user_problem, up_created = UserProblem.objects.get_or_create(
                user=request.user,
                problem=problem,
                defaults={
                    "status": form.cleaned_data['status'],
                    "notes": form.cleaned_data.get('notes', ''),
                }
            )
            if not up_created:
                messages.warning(request, "This problem has already been added.")
            else:
                user_problem.review_priority = calculate_review_priority(user_problem)
                user_problem.save()
                messages.success(request, f"'{problem.title}' added successfully!")

            return redirect('problem_list')
    else:
        form = ManualProblemForm()

    return render(request, 'problems/add.html', {'form': form})


@login_required
def problem_list(request):
    active_tab = request.GET.get('tab', 'cf')
    base_qs = UserProblem.objects.filter(user=request.user)\
        .select_related('problem', 'problem__platform')\
        .prefetch_related('problem__topics')

    if active_tab == 'manual':
        qs = base_qs.filter(problem__platform__slug='manual')
    else:
        qs = base_qs.exclude(problem__platform__slug='manual')

    difficulties = Problem.DIFFICULTY_CHOICES
    difficulty = request.GET.get('difficulty')
    status = request.GET.get('status')
    search = request.GET.get('search')
    topic = request.GET.get('topic')

    if difficulty:
        qs = qs.filter(problem__difficulty=difficulty)
    if status:
        qs = qs.filter(status=status)
    if search:
        qs = qs.filter(problem__title__icontains=search)
    if topic:
        qs = qs.filter(problem__topics__name__iexact=topic)

    min_rating = request.GET.get('min_rating')
    max_rating = request.GET.get('max_rating')
    if min_rating:
        qs = qs.filter(problem__rating__gte=min_rating)
    if max_rating:
        qs = qs.filter(problem__rating__lte=max_rating)

    topics = Topic.objects.filter(
        problems__userproblem__user=request.user
    ).distinct().order_by('name')

    sort = request.GET.get('sort')
    if sort == 'priority':
        qs = qs.filter(review_priority__gt=50).order_by('-review_priority', '-last_practiced')
    else:
        qs = qs.order_by('-last_practiced', '-id')

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    cf_count = base_qs.exclude(problem__platform__slug='manual').count()
    manual_count = base_qs.filter(problem__platform__slug='manual').count()

    return render(request, 'problems/list.html', {
        'problems': page_obj,
        'difficulties': difficulties,
        'active_tab': active_tab,
        'cf_count': cf_count,
        'manual_count': manual_count,
        'sort': sort,
        'topics': topics,
        'selected_topic': topic or '',
        'min_rating': min_rating or '',
        'max_rating': max_rating or '',
    })


@login_required
def edit_problem(request, pk):
    up = get_object_or_404(UserProblem, pk=pk, user=request.user)
    if request.method == 'POST':
        form = UserProblemForm(request.POST, instance=up)
        if form.is_valid():
            form.save()
            messages.success(request, "Problem updated successfully!")
            return redirect('problem_list')
    else:
        form = UserProblemForm(instance=up)

    return render(request, 'problems/edit.html', {'form': form, 'up': up})


@login_required
def delete_problem(request, pk):
    up = get_object_or_404(UserProblem, pk=pk, user=request.user)
    if up.problem.platform.slug != 'manual':
        messages.error(request, "Codeforces problems cannot be deleted — they are managed via sync.")
        return redirect('problem_list')
    up.delete()
    messages.success(request, "Problem deleted successfully!")
    return redirect(reverse('problem_list') + '?tab=manual')