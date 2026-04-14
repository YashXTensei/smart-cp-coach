import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from ..models import UserProblem
from ..utils.topics import get_weak_topics
from ..cf_api import get_cf_color
from ..utils.ai_coach import get_rule_based_suggestion, get_ai_response
from django.views.decorators.http import require_POST
from django.http import JsonResponse

@login_required
def dashboard(request):
    user_problems = UserProblem.objects.filter(user=request.user)\
        .select_related('problem', 'problem__platform')\
        .prefetch_related('problem__topics')

    total = user_problems.count()
    solved = user_problems.filter(status='solved').count()
    revision = user_problems.filter(status='revision').count()
    unsolved = user_problems.filter(status='unsolved').count()

    easy = user_problems.filter(problem__difficulty='easy').count()
    medium = user_problems.filter(problem__difficulty='medium').count()
    hard = user_problems.filter(problem__difficulty='hard').count()

    weak_topics = get_weak_topics(user_problems)
    today_focus = get_rule_based_suggestion(weak_topics)  # rule-based, free

    recent = user_problems.order_by('-last_practiced')[:10]

    bell_count = user_problems.filter(review_priority__gt=50).count()

    profile = request.user.profile
    has_cf_handle = bool(profile.cf_handle)

    # Active tab — default CF agar handle hai, warna manual
    default_tab = 'cf' if has_cf_handle else 'manual'
    active_tab = request.GET.get('tab', default_tab)

    # CF problems — last 10 for dashboard preview
    cf_problems = user_problems\
        .exclude(problem__platform__slug='manual')\
        .order_by('-last_practiced')[:10]

    # Manual problems — sab (generally kam honge)
    manual_problems = user_problems\
        .filter(problem__platform__slug='manual')\
        .order_by('-last_practiced')

    cf_count = user_problems.exclude(problem__platform__slug='manual').count()
    manual_count = user_problems.filter(problem__platform__slug='manual').count()

    # CF rating color
    cf_color = get_cf_color(profile.cf_rank) if profile.cf_rank else None

    return render(request, 'core/dashboard.html', {
        'total': total,
        'solved': solved,
        'revision': revision,
        'unsolved': unsolved,
        'easy': easy,
        'medium': medium,
        'hard': hard,
        'weak_topics': weak_topics,
        'recent': recent,
        'bell_count': bell_count,
        'has_cf_handle': has_cf_handle,
        'profile': profile,
        'active_tab': active_tab,
        'cf_problems': cf_problems,
        'manual_problems': manual_problems,
        'cf_count': cf_count,
        'manual_count': manual_count,
        'cf_color': cf_color,
        'today_focus': today_focus,
    })

@login_required
@require_POST
def ask_coach(request):
    try:
        body = json.loads(request.body)
        user_question = body.get('question', '').strip()
    except json.JSONDecodeError:
        user_question = ''

    # Weak topics fresh nikalo
    user_problems = UserProblem.objects.filter(user=request.user)\
        .select_related('problem')\
        .prefetch_related('problem__topics')

    weak_topics = get_weak_topics(user_problems)
    response_text = get_ai_response(weak_topics, user_question)

    return JsonResponse({'response': response_text})