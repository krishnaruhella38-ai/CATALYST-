import calendar
from datetime import date, timedelta
from pathlib import Path
from flask import request, flash
from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database import get_db_connection, init_db

PROJECT_ROOT = Path(__file__).resolve().parent.parent

app = Flask(
    __name__,
    template_folder=str(PROJECT_ROOT / "tempelate"),
    static_folder=str(PROJECT_ROOT / "static"),
)

app.secret_key = "mysecretkey"

init_db()


def _get_workspace_items(user_id):
    connection = get_db_connection()

    try:
        return {
            "tasks": connection.execute(
                "SELECT * FROM tasks WHERE user_id = ? ORDER BY id DESC",
                (user_id,),
            ).fetchall(),
            "goals": connection.execute(
                "SELECT * FROM goals WHERE user_id = ? ORDER BY id DESC",
                (user_id,),
            ).fetchall(),
            "assignments": connection.execute(
                "SELECT * FROM assignments WHERE user_id = ? ORDER BY id DESC",
                (user_id,),
            ).fetchall(),
        }
    finally:
        connection.close()


def _render_workspace_page(template_name):
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template(
        template_name,
        **_get_workspace_items(session["user_id"]),
        today=date.today(),
    )


@app.route("/")
def home():
    return render_template("index.html")



@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    items = _get_workspace_items(session["user_id"])
    today = date.today()
    due_items = []

    for kind, records in (("Task", items["tasks"]), ("Assignment", items["assignments"])):
        for record in records:
            if not record["deadline"] or record["status"] == "Completed":
                continue
            try:
                due_date = date.fromisoformat(record["deadline"])
            except ValueError:
                continue
            due_items.append({
                "kind": kind,
                "title": record["title"],
                "subject": record["subject"],
                "deadline": due_date,
                "priority": record["priority"],
            })

    upcoming = sorted(
        (item for item in due_items if item["deadline"] >= today),
        key=lambda item: item["deadline"],
    )[:5]
    month_days = [
        [
            {
                "date": day,
                "in_month": day.month == today.month,
                "is_today": day == today,
                "has_deadline": any(item["deadline"] == day for item in due_items),
            }
            for day in week
        ]
        for week in calendar.Calendar(firstweekday=6).monthdatescalendar(today.year, today.month)
    ]

    week_start = today - timedelta(days=today.weekday())
    weekly_deadlines = []
    for offset in range(7):
        day = week_start + timedelta(days=offset)
        weekly_deadlines.append({
            "label": day.strftime("%a"),
            "count": sum(item["deadline"] == day for item in due_items),
            "is_today": day == today,
        })

    return render_template(
        "dashboard.html",
        **items,
        today=today,
        month_label=today.strftime("%B %Y"),
        month_days=month_days,
        upcoming=upcoming,
        weekly_deadlines=weekly_deadlines,
    )


@app.route("/tasks")
def tasks_page():
    return _render_workspace_page("tasks.html")


@app.route("/assignments")
def assignments_page():
    return _render_workspace_page("assignments.html")


@app.route("/goals")
def goals_page():
    return _render_workspace_page("goals.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("All fields are required.")
            return redirect(url_for("register"))

        password_hash = generate_password_hash(password)
        connection = get_db_connection()

        try:
            connection.execute(
                """
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
                """,
                (username, email, password_hash),
            )
            connection.commit()
        except Exception:
            flash("That email may already be registered.")
            return redirect(url_for("register"))
        finally:
            connection.close()

        flash("Account created successfully!")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.")
            return redirect(url_for("login"))

        connection = get_db_connection()
        try:
            user = connection.execute(
                "SELECT * FROM users WHERE email = ?",
                (email,),
            ).fetchone()
        finally:
            connection.close()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Login successful!")
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.")
        return redirect(url_for("login"))

    return render_template("login.html")




@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/add_task", methods=["POST"])
def add_task():

    if "user_id" not in session:
        return redirect(url_for("login"))

    title = request.form.get("title", "").strip()
    subject = request.form.get("subject", "").strip()
    deadline = request.form.get("deadline", "").strip()
    priority = request.form.get("priority", "").strip()

    if not title or not subject:
        flash("Title and subject are required.")
        return redirect(url_for("tasks_page"))

    if priority not in ["High", "Medium", "Low"]:
        flash("Invalid priority.")
        return redirect(url_for("tasks_page"))

    connection = get_db_connection()

    try:
        connection.execute(
            """
            INSERT INTO tasks
            (user_id, title, subject, deadline, priority)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                session["user_id"],
                title,
                subject,
                deadline,
                priority
            )
        )

        connection.commit()

    finally:
        connection.close()

    flash("Task added successfully!")
    return redirect(url_for("tasks_page"))

@app.route("/add_goal", methods=["POST"])
def add_goal():
    if "user_id" not in session:
        return redirect(url_for("login"))

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    deadline = request.form.get("deadline", "").strip()

    if not title:
        flash("Title is required.")
        return redirect(url_for("goals_page"))

    connection = get_db_connection()

    try:
        connection.execute(
            """
            INSERT INTO goals
            (user_id, title, description, deadline)
            VALUES (?, ?, ?, ?)
            """,
            (
                session["user_id"],
                title,
                description,
                deadline
            )
        )
        connection.commit()
        flash("Goal added successfully!")

    finally:
        connection.close()

    return redirect(url_for("goals_page"))


@app.route("/complete_task/<int:task_id>", methods=["POST"])
def complete_task(task_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:
        cursor = connection.execute(
            """
            UPDATE tasks
            SET status = ?
            WHERE id = ? AND user_id = ?
            """,
            ("Completed", task_id, session["user_id"])
        )

        connection.commit()

        if cursor.rowcount == 0:
            flash("Task not found!")
        else:
            flash("Task marked as completed!")

    finally:
        connection.close()

    return redirect(url_for("tasks_page"))

@app.route("/complete_goal/<int:goal_id>", methods=["POST"])
def complete_goal(goal_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:
        cursor = connection.execute(
            """
            UPDATE goals
            SET achieved = 1
            WHERE id = ? AND user_id = ?
            """,
            (goal_id, session["user_id"])
        )
        connection.commit()
        flash("Goal marked as achieved!")

    finally:
        connection.close()

    return redirect(url_for("goals_page"))

@app.route("/update_goal/<int:goal_id>", methods=["POST"])
def edit_goal(goal_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    deadline = request.form.get("deadline", "").strip()

    if not title:
        flash("Title is required.")
        return redirect(url_for("goals_page"))

    connection = get_db_connection()

    try:
        cursor = connection.execute(
            """
            UPDATE goals
            SET title = ?, description = ?, deadline = ?
            WHERE id = ? AND user_id = ?
            """,
            (title, description, deadline, goal_id, session["user_id"]),
        )
        connection.commit()

        if cursor.rowcount == 0:
            flash("Goal not found!")
        else:
            flash("Goal updated successfully!")
    finally:
        connection.close()

    return redirect(url_for("goals_page"))

@app.route("/delete_goal/<int:goal_id>", methods=["POST"])
def delete_goal(goal_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:
        cursor = connection.execute(
            """
            DELETE FROM goals
            WHERE id = ? AND user_id = ?
            """,
            (goal_id, session["user_id"])
        )

        connection.commit()

        if cursor.rowcount == 0:
            flash("Goal not found!")
        else:
            flash("Goal deleted successfully!")

    finally:
        connection.close()

    return redirect(url_for("goals_page"))



@app.route("/delete_task/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:
        cursor = connection.execute(
            """
            DELETE FROM tasks
            WHERE id = ? AND user_id = ?
            """,
            (task_id, session["user_id"])
        )

        connection.commit()

        if cursor.rowcount == 0:
            flash("Task not found!")
        else:
            flash("Task deleted successfully!")

    finally:
        connection.close()

    return redirect(url_for("tasks_page"))

@app.route("/update_task/<int:task_id>", methods=["POST"])
def edit_task(task_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    title = request.form.get("title", "").strip()
    subject = request.form.get("subject", "").strip()
    deadline = request.form.get("deadline", "").strip()
    priority = request.form.get("priority", "").strip()

    if not title or not subject:
        flash("Title and subject are required.")
        return redirect(url_for("tasks_page"))
    if priority not in ["High", "Medium", "Low"]:
        flash("Invalid priority.")
        return redirect(url_for("tasks_page"))

    connection = get_db_connection()

    try:
        cursor = connection.execute(
            """
            UPDATE tasks
            SET title = ?, subject = ?, deadline = ?, priority = ?
            WHERE id = ? AND user_id = ?
            """,
            (title, subject, deadline, priority, task_id, session["user_id"])
        )

        connection.commit()

        if cursor.rowcount == 0:
            flash("Task not found!")
        else:
            flash("Task updated successfully!")
    finally:
        connection.close()

    return redirect(url_for("tasks_page"))

@app.route("/add_assignment", methods=["POST"])
def add_assignment():
    if "user_id" not in session:
        return redirect(url_for("login"))

    title = request.form.get("title", "").strip()
    subject = request.form.get("subject", "").strip()
    deadline = request.form.get("deadline", "").strip()
    priority = request.form.get("priority", "").strip()

    if not title or not subject:
        flash("Title and subject are required.")
        return redirect(url_for("assignments_page"))

    if priority not in ["High", "Medium", "Low"]:
        flash("Invalid priority.")
        return redirect(url_for("assignments_page"))

    connection = get_db_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO assignments
            (user_id, title, subject, deadline, priority)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                session["user_id"],
                title,
                subject,
                deadline,
                priority
            )
        )

        connection.commit()

    finally:
        connection.close()

    flash("Assignment added successfully!")
    return redirect(url_for("assignments_page"))

@app.route("/delete_assignment/<int:assignment_id>", methods=["POST"])
def delete_assignment(assignment_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:
        cursor = connection.execute(
            """
            DELETE FROM assignments
            WHERE id = ? AND user_id = ?
            """,
            (assignment_id, session["user_id"])
        )

        connection.commit()

        if cursor.rowcount == 0:
            flash("Assignment not found!")
        else:
            flash("Assignment deleted successfully!")

    finally:
        connection.close()

    return redirect(url_for("assignments_page"))

@app.route("/update_assignment/<int:assignment_id>", methods=["POST"])
def edit_assignment(assignment_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    title = request.form.get("title", "").strip()
    subject = request.form.get("subject", "").strip()
    deadline = request.form.get("deadline", "").strip()
    priority = request.form.get("priority", "").strip()

    if not title or not subject:
        flash("Title and subject are required.")
        return redirect(url_for("assignments_page"))
    if priority not in ["High", "Medium", "Low"]:
        flash("Invalid priority.")
        return redirect(url_for("assignments_page"))

    connection = get_db_connection()

    try:
        cursor = connection.execute(
            """
            UPDATE assignments
            SET title = ?, subject = ?, deadline = ?, priority = ?
            WHERE id = ? AND user_id = ?
            """,
            (title, subject, deadline, priority, assignment_id, session["user_id"])
        )

        connection.commit()

        if cursor.rowcount == 0:
            flash("Assignment not found!")
        else:
            flash("Assignment updated successfully!")
    finally:
        connection.close()

    return redirect(url_for("assignments_page"))

@app.route("/complete_assignment/<int:assignment_id>", methods=["POST"])
def complete_assignment(assignment_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:
        cursor = connection.execute(
            """
            UPDATE assignments
            SET status = ?
            WHERE id = ? AND user_id = ?
            """,
            ("Completed", assignment_id, session["user_id"])
        )

        connection.commit()

        if cursor.rowcount == 0:
            flash("Assignment not found!")
        else:
            flash("Assignment marked as completed!")

    finally:
        connection.close()

    return redirect(url_for("assignments_page"))

@app.route("/display_assignments")
def display_assignments():
    return redirect(url_for("assignments_page"))


@app.route("/submit_feedback", methods=["POST"])
def submit_feedback():

    if "user_id" not in session:
        return redirect(url_for("login"))

    rating = request.form.get("rating", type=int)
    category = request.form.get("category", "").strip()
    message = request.form.get("message", "").strip()

    allowed_categories = [
        "Bug Report",
        "Feature Request",
        "UI/UX",
        "General Feedback"
    ]

    if rating is None or rating not in range(1, 6):
        flash("Please select a valid rating.")
        return redirect(url_for("feedback"))

    if category not in allowed_categories:
        flash("Invalid feedback category.")
        return redirect(url_for("feedback"))

    if not 10 <= len(message) <= 1000:
        flash("Feedback must be between 10 and 1000 characters.")
        return redirect(url_for("feedback"))

    connection = get_db_connection()

    try:
        connection.execute("""
            INSERT INTO feedback
            (user_id, rating, category, message)
            VALUES (?, ?, ?, ?)
        """, (
            session["user_id"],
            rating,
            category,
            message
        ))

        connection.commit()

    finally:
        connection.close()

    flash("Feedback submitted successfully!")

    return redirect(url_for("feedback"))


@app.route("/feedback")
def feedback():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:
        feedback_list = connection.execute("""
            SELECT
                feedback.id,
                feedback.rating,
                feedback.category,
                feedback.message,
                feedback.created_at,
                users.username
            FROM feedback
            JOIN users
            ON feedback.user_id = users.id
            ORDER BY feedback.created_at DESC
        """).fetchall()

    finally:
        connection.close()

    return render_template(
        "feedback.html",
        feedback_list=feedback_list
    )



if __name__ == "__main__":
    app.run(debug=True)