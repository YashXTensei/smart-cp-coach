import requests
from django.conf import settings


def get_rule_based_suggestion(weak_topics):
    if not weak_topics:
        return None

    top = weak_topics[0]
    topic_name = top[0]
    score = top[1]

    second_line = ""
    if len(weak_topics) >= 2:
        second_line = f" Follow up with {weak_topics[1][0]} as your second priority."

    if score >= 10:
        intensity = "seriously focus on"
    elif score >= 5:
        intensity = "practice"
    else:
        intensity = "revisit"

    return (
        f"Today, {intensity} {topic_name} — your struggle score here is {score}."
        f"{second_line} "
        f"Aim to solve 2-3 problems in the 1300-1600 rating range."
    )


def get_ai_response(weak_topics, user_question=""):
    if not weak_topics:
        topic_context = "No weak topics identified yet."
    else:
        topic_context = "\n".join(
            f"- {name} (struggle score: {score})"
            for name, score in weak_topics[:3]
        )

    if user_question.strip():
        user_part = f"Student's question: {user_question.strip()}"
        focus = "Answer the student's question directly and completely. Use weak topics only as background context, not as the main focus."
    else:
        user_part = "Give a general improvement plan for today."
        focus = "Base your advice on the student's weak topics."

    prompt = f"""You are a competitive programming coach helping a student improve.

{user_part}

Background context — student's weak topics (use only if relevant):
{topic_context}

Instructions: {focus}
Reply in 3-4 sentences. Be specific and actionable.
Plain text only, no markdown, no bullet points."""

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "meta-llama/llama-3.1-8b-instruct",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 250,
                "temperature": 0.7,
            },
            timeout=20,
        )
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()

    except requests.exceptions.Timeout:
        return "AI Coach is taking too long to respond — please try again in a moment."
    except (KeyError, IndexError):
        return "Could not parse the response. Please try again."
    except requests.exceptions.RequestException:
        return "Network error. Please check your connection and try again."