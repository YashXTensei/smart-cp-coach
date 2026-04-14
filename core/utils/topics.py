from collections import defaultdict

def get_weak_topics(user_problems):
    """
    Weak topic = jisme problems pe zyada struggle hua.

    Score = sum of wrong_attempts for all problems in that topic.
    Minimum 2 problems required (single-problem noise avoid karo).
    Returns top 5 as [(topic_name, score), ...]
    """
    topic_wrong_attempts = defaultdict(int)
    topic_problem_count = defaultdict(int)

    for up in user_problems.filter(status__in=['solved', 'revision']):
        for topic in up.problem.topics.all():
            topic_problem_count[topic.name] += 1
            topic_wrong_attempts[topic.name] += up.wrong_attempts

    weak = {
        topic: score
        for topic, score in topic_wrong_attempts.items()
        if topic_problem_count[topic] >= 2 and score > 0
    }

    return sorted(weak.items(), key=lambda x: x[1], reverse=True)[:5]