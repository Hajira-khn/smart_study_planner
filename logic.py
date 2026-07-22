"""
logic.py — Pure business logic extracted from the Smart Study Planner.
No Tkinter dependency here, making it fully unit-testable.
"""
from datetime import date

# ── Constants ────────────────────────────────────────────────
VALID_PRIORITIES  = ["High", "Medium", "Low"]
VALID_DURATIONS   = ["30 min", "1 hour", "1.5 hours", "2 hours", "3 hours", "4 hours"]
SUBJECTS_LIST     = [
    "Programming", "Artificial Intelligence",
    "Human Computer Interaction", "English", "Mathematics"
]

DEFAULT_SUBJECTS = [
    {"name": "Programming",               "hours": 10, "progress": 78},
    {"name": "Artificial Intelligence",   "hours": 8,  "progress": 62},
    {"name": "Human Computer Interaction","hours": 6,  "progress": 45},
    {"name": "English",                   "hours": 4,  "progress": 90},
    {"name": "Mathematics",               "hours": 9,  "progress": 55},
]


# ── Authentication ────────────────────────────────────────────
def validate_login(username: str, password: str) -> tuple[bool, str]:
    """Return (success, message). No real auth — only non-empty check."""
    username = username.strip()
    password = password.strip()
    if not username and not password:
        return False, "Username and password are required."
    if not username:
        return False, "Username is required."
    if not password:
        return False, "Password is required."
    return True, "Login successful."


# ── Subject management ────────────────────────────────────────
def add_subject(subjects: list, name: str, hours: int = 4) -> tuple[bool, str]:
    name = name.strip()
    if not name:
        return False, "Subject name cannot be empty."
    if any(s["name"].lower() == name.lower() for s in subjects):
        return False, f"Subject '{name}' already exists."
    if hours < 1 or hours > 40:
        return False, "Weekly hours must be between 1 and 40."
    subjects.append({"name": name, "hours": hours, "progress": 0})
    return True, f"Subject '{name}' added."


def delete_subject(subjects: list, name: str) -> tuple[bool, str]:
    for i, s in enumerate(subjects):
        if s["name"] == name:
            subjects.pop(i)
            return True, f"Subject '{name}' deleted."
    return False, f"Subject '{name}' not found."


def search_subjects(subjects: list, query: str) -> list:
    query = query.strip().lower()
    if not query:
        return subjects
    return [s for s in subjects if query in s["name"].lower()]


def update_progress(subjects: list, name: str, progress: int) -> tuple[bool, str]:
    if not (0 <= progress <= 100):
        return False, "Progress must be between 0 and 100."
    for s in subjects:
        if s["name"] == name:
            s["progress"] = progress
            return True, "Progress updated."
    return False, f"Subject '{name}' not found."


# ── Study plan management ─────────────────────────────────────
def add_plan(plans: list, date_str: str, subject: str,
             duration: str, priority: str, notes: str = "") -> tuple[bool, str]:
    if not date_str.strip():
        return False, "Date is required."
    if subject not in SUBJECTS_LIST:
        return False, f"Invalid subject: {subject}"
    if duration not in VALID_DURATIONS:
        return False, f"Invalid duration: {duration}"
    if priority not in VALID_PRIORITIES:
        return False, f"Invalid priority: {priority}"
    # Basic date format check
    try:
        parts = date_str.strip().split("-")
        assert len(parts) == 3
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
        date(year, month, day)   # raises ValueError if invalid
    except (ValueError, AssertionError):
        return False, "Date must be in YYYY-MM-DD format."
    plans.append((date_str.strip(), subject, duration, priority, notes or "—"))
    return True, "Plan added."


def delete_plan(plans: list, index: int) -> tuple[bool, str]:
    if index < 0 or index >= len(plans):
        return False, "Index out of range."
    plans.pop(index)
    return True, "Plan deleted."


def filter_plans_by_priority(plans: list, priority: str) -> list:
    if priority not in VALID_PRIORITIES:
        return []
    return [p for p in plans if p[3] == priority]


# ── Progress / statistics ─────────────────────────────────────
def calculate_overall_progress(subjects: list) -> float:
    if not subjects:
        return 0.0
    return round(sum(s["progress"] for s in subjects) / len(subjects), 2)


def total_weekly_hours(subjects: list) -> int:
    return sum(s["hours"] for s in subjects)
