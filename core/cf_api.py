import requests

CF_API_BASE = "https://codeforces.com/api"


def validate_cf_handle(handle):
    """Returns True if handle exists on Codeforces, False otherwise."""
    try:
        resp = requests.get(f"{CF_API_BASE}/user.info", params={"handles": handle}, timeout=10)
        data = resp.json()
        return data.get("status") == "OK"
    except Exception:
        return False


def fetch_cf_user_info(handle):
    """
    Returns (rating, rank) for a CF handle, or (None, None) on failure.
    """
    try:
        resp = requests.get(f"{CF_API_BASE}/user.info", params={"handles": handle}, timeout=10)
        data = resp.json()
        if data.get("status") == "OK":
            info = data["result"][0]
            return info.get("rating"), info.get("rank", "")
        return None, None
    except Exception:
        return None, None


def fetch_cf_submissions(handle, since_id=None):
    """
    Returns list of attempted problems for a CF handle.
    Tracks both AC submissions AND wrong attempts (WA/TLE/RE etc.)

    Each item:
    {
        "problem_code": "1234A",
        "title": "Problem Name",
        "rating": 1400,
        "tags": ["dp", "greedy"],
        "link": "https://...",
        "solved": True/False,
        "solved_at": timestamp or None,
        "wrong_attempts": 3,
    }
    """
    try:
        count = 10000 if since_id is None else 200
        resp = requests.get(
            f"{CF_API_BASE}/user.status",
            params={"handle": handle, "from": 1, "count": count},
            timeout=15
        )
        data = resp.json()
        if data.get("status") != "OK":
            return None, None, "CF API error"

        problem_map = {}
        latest_id = None

        for sub in data["result"]:
            sub_id = sub.get("id")

            if latest_id is None:
                latest_id = sub_id

            if since_id and sub_id <= since_id:
                break

            p = sub["problem"]
            contest_id = p.get("contestId")
            index = p.get("index")
            key = (contest_id, index)

            if key not in problem_map:
                problem_code = f"{contest_id}{index}"
                problem_map[key] = {
                    "problem_code": problem_code,
                    "title": p.get("name", ""),
                    "rating": p.get("rating"),
                    "tags": p.get("tags", []),
                    "link": f"https://codeforces.com/problemset/problem/{contest_id}/{index}",
                    "solved": False,
                    "solved_at": None,
                    "wrong_attempts": 0,
                }

            verdict = sub.get("verdict")
            if verdict == "OK":
                # Newest-first — last overwrite = chronologically first AC
                problem_map[key]["solved"] = True
                problem_map[key]["solved_at"] = sub.get("creationTimeSeconds")
            else:
                problem_map[key]["wrong_attempts"] += 1

        return list(problem_map.values()), latest_id, None

    except Exception as e:
        return None, None, str(e)


def rating_to_difficulty(rating):
    if rating is None:
        return "medium"
    if rating < 1200:
        return "easy"
    elif rating <= 1900:
        return "medium"
    else:
        return "hard"


def get_cf_color(rank):
    """Returns Bootstrap-compatible color for CF rank."""
    if not rank:
        return "#000000"
    rank = rank.lower()
    if "legendary" in rank:
        return "#FF0000"
    elif "international" in rank and "grandmaster" in rank:
        return "#FF0000"
    elif "grandmaster" in rank:
        return "#FF0000"
    elif "international" in rank and "master" in rank:
        return "#FF8C00"
    elif "master" in rank:
        return "#FF8C00"
    elif "candidate" in rank:
        return "#AA00AA"
    elif "expert" in rank:
        return "#0000FF"
    elif "specialist" in rank:
        return "#03A89E"
    elif "pupil" in rank:
        return "#008000"
    else:
        return "#808080"  # newbie