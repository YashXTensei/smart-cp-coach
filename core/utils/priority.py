from django.utils import timezone

def calculate_review_priority(user_problem):
    """
    Priority score for review queue. Higher = review pehle.

    Factors:
    - wrong_attempts : zyada WA/TLE = zyada struggle = high priority
    - rating         : hard problems = high priority
    - days since last_practiced : purana = high priority
    - status='revision' : user ne khud mark kiya = highest priority
    """
    score = 0
    rating = user_problem.problem.rating or 1200

    # Factor 1: Wrong attempts (most important signal)
    wa = user_problem.wrong_attempts
    if wa >= 5:
        score += 50
    elif wa >= 3:
        score += 35
    elif wa >= 1:
        score += 20

    # Factor 2: Problem rating
    if rating >= 1800:
        score += 30
    elif rating >= 1600:
        score += 20
    elif rating >= 1400:
        score += 10

    # Factor 3: Time since last practiced
    if user_problem.last_practiced:
        days_since = (timezone.now() - user_problem.last_practiced).days
        if days_since > 90:
            score += 25
        elif days_since > 30:
            score += 15
        elif days_since > 14:
            score += 8

    # Factor 4: Manually marked revision — highest weight
    if user_problem.status == 'revision':
        score += 60

    return score