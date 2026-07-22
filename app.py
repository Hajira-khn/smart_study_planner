import os
from copy import deepcopy
from flask import Flask, render_template, request, redirect, url_for, session

from logic import (
    validate_login,
    add_subject, delete_subject, search_subjects, update_progress,
    add_plan, delete_plan, filter_plans_by_priority,
    calculate_overall_progress, total_weekly_hours,
    DEFAULT_SUBJECTS, SUBJECTS_LIST, VALID_PRIORITIES, VALID_DURATIONS,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

NAV_ITEMS = [
    ("⊞", "Dashboard", "dashboard", "dashboard"),
    ("◉", "Subjects", "subjects", "subjects_page"),
    ("📅", "Study Planner", "planner", "planner_page"),
    ("📊", "Progress", "progress", "progress_page"),
    ("⚙", "Settings", "settings", "settings_page"),
    ("ℹ", "About", "about", "about_page"),
]


def ensure_state():
    """Make sure session has subjects/plans initialized."""
    if "subjects" not in session:
        session["subjects"] = deepcopy(DEFAULT_SUBJECTS)
    if "plans" not in session:
        session["plans"] = []


def login_required(view):
    def wrapped(*args, **kwargs):
        if not session.get("username"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    wrapped.__name__ = view.__name__
    return wrapped


@app.route("/", methods=["GET"])
def index():
    return redirect(url_for("dashboard") if session.get("username") else url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        ok, msg = validate_login(username, password)
        if ok:
            session["username"] = username.strip()
            ensure_state()
            return redirect(url_for("dashboard"))
        error = msg
    return render_template("login.html", error=error, nav=NAV_ITEMS, active="login")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    ensure_state()
    subjects = session["subjects"]
    plans = session["plans"]
    overall = calculate_overall_progress(subjects)
    hours = total_weekly_hours(subjects)
    recent_plans = list(reversed(plans))[:5]
    return render_template(
        "dashboard.html", nav=NAV_ITEMS, active="dashboard",
        username=session["username"], subjects=subjects, overall=overall,
        hours=hours, plan_count=len(plans), recent_plans=recent_plans,
    )


@app.route("/subjects", methods=["GET", "POST"])
@login_required
def subjects_page():
    ensure_state()
    subjects = session["subjects"]
    message = None
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            name = request.form.get("name", "")
            try:
                hours = int(request.form.get("hours", 4))
            except ValueError:
                hours = 0
            ok, msg = add_subject(subjects, name, hours)
            message = msg
        elif action == "delete":
            name = request.form.get("name", "")
            ok, msg = delete_subject(subjects, name)
            message = msg
        elif action == "progress":
            name = request.form.get("name", "")
            try:
                progress = int(request.form.get("progress", 0))
            except ValueError:
                progress = 0
            ok, msg = update_progress(subjects, name, progress)
            message = msg
        session["subjects"] = subjects

    query = request.args.get("q", "")
    shown = search_subjects(subjects, query) if query else subjects
    return render_template(
        "subjects.html", nav=NAV_ITEMS, active="subjects",
        subjects=shown, message=message, query=query,
    )


@app.route("/planner", methods=["GET", "POST"])
@login_required
def planner_page():
    ensure_state()
    plans = session["plans"]
    message = None
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            ok, msg = add_plan(
                plans,
                request.form.get("date", ""),
                request.form.get("subject", ""),
                request.form.get("duration", ""),
                request.form.get("priority", ""),
                request.form.get("notes", ""),
            )
            message = msg
        elif action == "delete":
            try:
                idx = int(request.form.get("index", -1))
            except ValueError:
                idx = -1
            ok, msg = delete_plan(plans, idx)
            message = msg
        session["plans"] = plans

    priority_filter = request.args.get("priority", "")
    if priority_filter:
        matches = filter_plans_by_priority(plans, priority_filter)
        # keep original indices so delete-by-index still works after filtering
        shown_plans = [(i, p) for i, p in enumerate(plans) if p in matches]
    else:
        shown_plans = list(enumerate(plans))
    return render_template(
        "planner.html", nav=NAV_ITEMS, active="planner",
        shown_plans=shown_plans,
        message=message, priority_filter=priority_filter,
        subjects_list=SUBJECTS_LIST, durations=VALID_DURATIONS, priorities=VALID_PRIORITIES,
    )


@app.route("/progress")
@login_required
def progress_page():
    ensure_state()
    subjects = session["subjects"]
    overall = calculate_overall_progress(subjects)
    hours = total_weekly_hours(subjects)
    return render_template(
        "progress.html", nav=NAV_ITEMS, active="progress",
        subjects=subjects, overall=overall, hours=hours,
    )


@app.route("/settings")
@login_required
def settings_page():
    return render_template(
        "settings.html", nav=NAV_ITEMS, active="settings", username=session.get("username"),
    )


@app.route("/about")
@login_required
def about_page():
    return render_template("about.html", nav=NAV_ITEMS, active="about")


if __name__ == "__main__":
    app.run(debug=True)
