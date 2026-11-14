
import json
from pathlib import Path


class Task:

    def __init__(self, title, subject, deadline, priority, status):
        self.title = title
        self.subject = subject
        self.deadline = deadline
        self.priority = priority
        self.status = status

    def to_dict(self):
        return {
            "title": self.title,
            "subject": self.subject,
            "deadline": self.deadline,
            "priority": self.priority,
            "status": self.status,
        }

    def mark_completed(self):
        if self.status != "Completed":
            self.status = "Completed"
            print(f"Task '{self.title}' marked as completed.")

    def display_task(self):
        print("Title:", self.title)
        print("Subject:", self.subject)
        print("Deadline:", self.deadline)
        print("Priority:", self.priority)
        print("Status:", self.status)

class TaskManager:

    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)
        print(f"Task '{task.title}' added.")

    def display_all_tasks(self):
        for task in self.tasks:
            task.display_task()
            print("--------------------")

    def complete_task(self, title):
        for task in self.tasks:
            if task.title == title:
                task.mark_completed()
                return
        print(f"Task '{title}' not found.")

    def count_tasks_by_status(self):
        completed = sum(1 for task in self.tasks if task.status == "Completed")
        pending = sum(1 for task in self.tasks if task.status == "Pending")

        print(f"Total Tasks: {len(self.tasks)}")
        print(f"Completed Tasks: {completed}")
        print(f"Pending Tasks: {pending}")

    def remove_task(self, title):
        for task in self.tasks:
            if task.title == title:
                self.tasks.remove(task)
                print(f"Task '{title}' removed.")
                return
        print(f"Task '{title}' not found.")

class Goal:

    def __init__(self, title, description, deadline):
        self.title = title
        self.description = description
        self.deadline = deadline
        self.achieved = False

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "deadline": self.deadline,
            "achieved": self.achieved,
        }

    def display_goal(self):
        print("Goal Title:", self.title)
        print("Description:", self.description)
        print("Deadline:", self.deadline)
        print("Status:", "Achieved" if self.achieved else "Pending")

    def mark_achieved(self):
        if not self.achieved:
            self.achieved = True
            print(f"Goal '{self.title}' marked as achieved.")

class GoalManager:

    def __init__(self):
        self.goals = []

    def add_goal(self, goal):
        self.goals.append(goal)
        print(f"Goal '{goal.title}' added.")

    def view_goals(self):
        for goal in self.goals:
            goal.display_goal()
            print("--------------------")

    def complete_goal(self, title):
        for goal in self.goals:
            if goal.title == title:
                goal.mark_achieved()
                return
        print(f"Goal '{title}' not found.")

    def remove_goal(self, title):
        for goal in self.goals:
            if goal.title == title:
                self.goals.remove(goal)
                print(f"Goal '{title}' removed.")
                return
        print(f"Goal '{title}' not found.")

    def count_goals(self):
        achieved = sum(1 for goal in self.goals if goal.achieved)
        pending = sum(1 for goal in self.goals if not goal.achieved)
        print(f"Total Goals: {len(self.goals)}")
        print(f"Achieved Goals: {achieved}")
        print(f"Pending Goals: {pending}")


class Assignment:
    
    def __init__(self, assignment_id, title, subject, deadline, priority, status):
        self.assignment_id = assignment_id
        self.title = title
        self.subject = subject
        self.deadline = deadline
        self.priority = priority
        self.status = status

    def to_dict(self):
        return {
            "assignment_id": self.assignment_id,
            "title": self.title,
            "subject": self.subject,
            "deadline": self.deadline,
            "priority": self.priority,
            "status": self.status,
        }

    def mark_completed(self):
        if self.status != "Completed":
            self.status = "Completed"
            print(f"Assignment '{self.title}' marked as completed.")

    def display_assignment(self):
        print("ID:", self.assignment_id)
        print("Title:", self.title)
        print("Subject:", self.subject)
        print("Deadline:", self.deadline)
        print("Priority:", self.priority)
        print("Status:", self.status)

class AssignmentManager:

    def __init__(self):
        self.assignments = []

    def add_assignment(self, assignment):
        self.assignments.append(assignment)
        print(f"Assignment '{assignment.title}' added.")

    def view_assignments(self):
        for assignment in self.assignments:
            assignment.display_assignment()
            print("--------------------")

    def complete_assignment(self, title):
        for assignment in self.assignments:
            if assignment.title == title:
                assignment.mark_completed()
                return
        print(f"Assignment '{title}' not found.")

    def remove_assignment(self, title):
        for assignment in self.assignments:
            if assignment.title == title:
                self.assignments.remove(assignment)
                print(f"Assignment '{title}' removed.")
                return
        print(f"Assignment '{title}' not found.")

    def count_assignments(self):
        completed = sum(1 for assignment in self.assignments if assignment.status == "Completed")
        pending = sum(1 for assignment in self.assignments if assignment.status == "Pending")
        print(f"Total Assignments: {len(self.assignments)}")
        print(f"Completed Assignments: {completed}")
        print(f"Pending Assignments: {pending}")


class DataManager:

    def __init__(self, task_manager, goal_manager, assignment_manager):
        self.task_manager = task_manager
        self.goal_manager = goal_manager
        self.assignment_manager = assignment_manager
        self.filename = Path(__file__).with_name("catalyst_data.json")

    def save_data(self):
        data = {
            "tasks": [task.to_dict() for task in self.task_manager.tasks],
            "goals": [goal.to_dict() for goal in self.goal_manager.goals],
            "assignments": [
                assignment.to_dict()
                for assignment in self.assignment_manager.assignments
            ],
        }
        with open(self.filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
        print(f"Data saved to: {self.filename}")

    def load_data(self):
        with open(self.filename, "r", encoding="utf-8") as file:
            data = json.load(file)

        tasks = [
            Task(**task_data) for task_data in data["tasks"]
        ]
        goals = []
        for goal_data in data["goals"]:
            goal = Goal(
                goal_data["title"],
                goal_data["description"],
                goal_data["deadline"],
            )
            goal.achieved = goal_data["achieved"]
            goals.append(goal)
        assignments = [
            Assignment(**assignment_data)
            for assignment_data in data["assignments"]
        ]

        self.task_manager.tasks = tasks
        self.goal_manager.goals = goals
        self.assignment_manager.assignments = assignments
        print(f"Data loaded from: {self.filename}")


class ProgressTracker:
    
    def __init__(self, task_manager, goal_manager, assignment_manager):
        self.task_manager = task_manager
        self.goal_manager = goal_manager
        self.assignment_manager = assignment_manager

    def display_progress_summary(self):
        print("Progress Summary:")
        print("--------------------")
        self.task_manager.count_tasks_by_status()
        print("--------------------")
        self.goal_manager.count_goals()
        print("--------------------")
        self.assignment_manager.count_assignments()

    def display_overview(self):
        self.display_progress_summary()
        print("--------------------")
        self.progress()

    def progress(self):
        completed_tasks = sum(
            1 for task in self.task_manager.tasks if task.status == "Completed"
        )
        completed_goals = sum(
            1 for goal in self.goal_manager.goals if goal.achieved
        )
        completed_assignments = sum(
            1
            for assignment in self.assignment_manager.assignments
            if assignment.status == "Completed"
        )
        total_items = (
            len(self.task_manager.tasks)
            + len(self.goal_manager.goals)
            + len(self.assignment_manager.assignments)
        )

        if total_items == 0:
            print("Overall Progress: 0.00%")
            return

        completed_items = (
            completed_tasks + completed_goals + completed_assignments
        )
        percentage = completed_items / total_items * 100
        print(f"Overall Progress: {percentage:.2f}%")

task_manager = TaskManager()
goal_manager = GoalManager()
assignment_manager = AssignmentManager()
data_manager = DataManager(task_manager, goal_manager, assignment_manager)

if data_manager.filename.exists():
    data_manager.load_data()
else:
    task_manager.add_task(
        Task("Complete Python", "Programming", "05-11-2026", "High", "Pending")
    )
    task_manager.add_task(
        Task("Physics Assignment", "Physics", "06-11-2026", "Medium", "Pending")
    )
    task_manager.add_task(
        Task("Networking Lecture", "Cybersecurity", "07-11-2026", "High", "Pending")
    )
    task_manager.complete_task("Complete Python")
    task_manager.complete_task("Networking Lecture")

    goal_manager.add_goal(Goal("Learn Python", "Technical", "15-11-2026"))
    goal_manager.add_goal(Goal("Complete Networking", "Cybersecurity", "20-11-2026"))
    goal_manager.add_goal(Goal("Prepare for Exams", "Academic", "25-11-2026"))
    goal_manager.complete_goal("Learn Python")

    assignment_manager.add_assignment(
        Assignment(1, "Physics Practical", "Physics", "05-11-2026", "High", "Pending")
    )
    assignment_manager.add_assignment(
        Assignment(2, "Python Project", "Programming", "10-11-2026", "Medium", "Pending")
    )
    assignment_manager.add_assignment(
        Assignment(3, "Networking Report", "Cybersecurity", "15-11-2026", "High", "Pending")
    )
    assignment_manager.complete_assignment("Physics Practical")
    data_manager.save_data()


# =================================
# PROGRESS TRACKER
# =================================

tracker = ProgressTracker(
    task_manager,
    goal_manager,
    assignment_manager
)

tracker.display_overview()

def main():
    while True:
        print("\nCatalyst - Task, Goal, and Assignment Manager")
        print("1. Add Task")
        print("2. View Tasks")
        print("3. Complete Task")
        print("4. Remove Task")
        print("5. Add Goal")
        print("6. View Goals")
        print("7. Complete Goal")
        print("8. Remove Goal")
        print("9. Add Assignment")
        print("10. View Assignments")
        print("11. Complete Assignment")
        print("12. Remove Assignment")
        print("13. View Progress Summary")
        print("14. Save Data")
        print("15. Load Data")
        print("16. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            title = input("Enter task title: ")
            subject = input("Enter task subject: ")
            deadline = input("Enter task deadline (DD-MM-YYYY): ")
            priority = input("Enter task priority (High/Medium/Low): ")
            status = "Pending"
            task_manager.add_task(Task(title, subject, deadline, priority, status))
            data_manager.save_data()
        elif choice == "2":
            task_manager.display_all_tasks()
        elif choice == "3":
            title = input("Enter task title to complete: ")
            task_manager.complete_task(title)
            data_manager.save_data()
        elif choice == "4":
            title = input("Enter task title to remove: ")
            task_manager.remove_task(title)
            data_manager.save_data()
        elif choice == "5":
            title = input("Enter goal title: ")
            description = input("Enter goal description: ")
            deadline = input("Enter goal deadline (DD-MM-YYYY): ")
            goal_manager.add_goal(Goal(title, description, deadline))
            data_manager.save_data()
        elif choice == "6":
            goal_manager.view_goals()
        elif choice == "7":
            title = input("Enter goal title to complete: ")
            goal_manager.complete_goal(title)
            data_manager.save_data()
        elif choice == "8":
            title = input("Enter goal title to remove: ")
            goal_manager.remove_goal(title)
            data_manager.save_data()
        elif choice == "9":
            try:
                assignment_id = int(input("Enter assignment ID: "))
            except ValueError:
                print("Assignment ID must be a whole number.")
                continue
            title = input("Enter assignment title: ")
            subject = input("Enter assignment subject: ")
            deadline = input("Enter assignment deadline (DD-MM-YYYY): ")
            priority = input("Enter assignment priority (High/Medium/Low): ")
            status = "Pending"
            assignment_manager.add_assignment(
                Assignment(assignment_id, title, subject, deadline, priority, status)
            )
            data_manager.save_data()
        elif choice == "10":
            assignment_manager.view_assignments()
        elif choice == "11":
            title = input("Enter assignment title to complete: ")
            assignment_manager.complete_assignment(title)
            data_manager.save_data()
        elif choice == "12":
            title = input("Enter assignment title to remove: ")
            assignment_manager.remove_assignment(title)
            data_manager.save_data()
        elif choice == "13":
            tracker.display_overview()
        elif choice == "14":
            data_manager.save_data()
        elif choice == "15":
            data_manager.load_data()
        elif choice == "16":
            data_manager.save_data()
            print("Exiting Catalyst. Goodbye!")
            break
        else:
            print("Invalid choice. Enter a number from 1 to 16.")


if __name__ == "__main__":
    main()