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
        "wrong_attempts": 3,   # WA + TLE + RE count before AC (or total if unsolved)
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

        # Step 1: Collect all submission data per problem
        # problem_key → { meta, solved, solved_at, wrong_attempts }
        problem_map = {}
        latest_id = None

        for sub in data["result"]:
            sub_id = sub.get("id")

            # Track latest submission ID (first in list = most recent)
            if latest_id is None:
                latest_id = sub_id

            # Stop if we've already processed everything after this point
            if since_id and sub_id <= since_id:
                break

            p = sub["problem"]
            contest_id = p.get("contestId")
            index = p.get("index")
            key = (contest_id, index)

            # Initialize problem entry if first time seeing it
            if key not in problem_map:
                problem_code = f"{contest_id}{index}"
                problem_map[key] = {
                    "problem_code": problem_code,
                    "title": p.get("name", ""),
                    "rating": p.get("rating"),       # can be None
                    "tags": p.get("tags", []),
                    "link": f"https://codeforces.com/problemset/problem/{contest_id}/{index}",
                    "solved": False,
                    "solved_at": None,
                    "wrong_attempts": 0,
                }

            verdict = sub.get("verdict")

            if verdict == "OK":
                # Mark as solved — store earliest AC time
                # (submissions are newest-first, so last OK we see = first AC chronologically)
                problem_map[key]["solved"] = True
                problem_map[key]["solved_at"] = sub.get("creationTimeSeconds")

            else:
                # Any non-AC verdict = wrong attempt
                # Common: WRONG_ANSWER, TIME_LIMIT_EXCEEDED, RUNTIME_ERROR, MEMORY_LIMIT_EXCEEDED
                problem_map[key]["wrong_attempts"] += 1

        # Step 2: Convert map to list
        problems = list(problem_map.values())

        return problems, latest_id, None

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