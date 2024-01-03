# task_manager.py
import tkinter as tk
from tkinter import simpledialog, messagebox
from plyer import notification
from db_connector import connect_to_database, execute_query, close_connection
import threading
import datetime

class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager")
        self.tasks = self.load_tasks_from_database()  # Load tasks from the database on initialization

        # Set a background color
        self.root.configure(bg="#ADD8E6")

        self.create_widgets()

    def load_tasks_from_database(self):
        # Load tasks from the database
        connection = connect_to_database()
        tasks = []
        if connection:
            try:
                query = "SELECT * FROM tasks"
                result = execute_query(connection, query)
                tasks = [{'TaskId': row[0], 'description': row[1], 'deadline': row[2], 'status': row[3]} for row in result]
            except Exception as e:
                print(f"Error loading tasks from database: {e}")
            finally:
                close_connection(connection)
        return tasks

    def create_widgets(self):
        # Entry Page
        tk.Label(self.root, text="Task Description:", bg="#F0F0F0", font=("Helvetica", 12)).grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)
        tk.Label(self.root, text="Task Deadline:", bg="#F0F0F0", font=("Helvetica", 12)).grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)

        self.description_entry = tk.Entry(self.root, font=("Helvetica", 12))
        self.description_entry.grid(row=0, column=1, padx=5, pady=5)

        self.deadline_entry = tk.Entry(self.root, font=("Helvetica", 12))
        self.deadline_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(self.root, text="Add Task", command=self.add_task, font=("Helvetica", 12)).grid(row=2, column=0, columnspan=2, pady=10)

        # List of Tasks
        self.task_listbox = tk.Listbox(self.root, font=("Helvetica", 12), selectmode=tk.SINGLE)
        self.task_listbox.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        tk.Button(self.root, text="Set Notification", command=self.set_notification, font=("Helvetica", 12)).grid(row=4, column=0, columnspan=2, pady=5)
        tk.Button(self.root, text="Show Tasks", command=self.show_tasks, font=("Helvetica", 12)).grid(row=5, column=0, pady=5)
        tk.Button(self.root, text="Mark as Complete", command=lambda: self.mark_task(status=True), font=("Helvetica", 12)).grid(row=5, column=1, pady=5)
        tk.Button(self.root, text="Mark as Incomplete", command=lambda: self.mark_task(status=False), font=("Helvetica", 12)).grid(row=6, column=0, columnspan=2, pady=5)

    def add_task(self):
        description = self.description_entry.get()
        deadline = self.deadline_entry.get() or 'Not set'

        # Assign a unique id to each task
        task_id = len(self.tasks) + 1

        task = {'TaskId': task_id, 'description': description, 'deadline': deadline, 'status': False}
        self.tasks.append(task)

        # Save tasks to the database
        connection = connect_to_database()
        if connection:
            try:
                query = "INSERT INTO tasks (TaskId, description, deadline, status) VALUES (%s, %s, %s, %s)"
                data = (task['TaskId'], task['description'], task['deadline'], task['status'])
                execute_query(connection, query, data)
                connection.commit()
            except Exception as e:
                print(f"Error adding task to database: {e}")
                connection.rollback()
            finally:
                close_connection(connection)

        messagebox.showinfo("Task Added", f"Task '{description}' added with{'out' if not deadline else ''} deadline.")
        self.clear_entries()
        self.update_task_list()

    def show_tasks(self):
        # Load tasks from the database
        connection = connect_to_database()
        if connection:
            try:
                query = "SELECT * FROM tasks"
                result = execute_query(connection, query)
                self.tasks = [{'TaskId': row[0], 'description': row[1], 'deadline': row[2], 'status': row[3]} for row in result]
            except Exception as e:
                print(f"Error loading tasks from database: {e}")
            finally:
                close_connection(connection)

        self.update_task_list()
        if not self.tasks:
            messagebox.showinfo("Task Manager", "No tasks available.")
        else:
            messagebox.showinfo("Task Manager", "\n".join([f"{task['description']} - Deadline: {task['deadline']} - Status: {'Complete' if task.get('status', False) else 'Incomplete'}" for task in self.tasks]))

    def update_task_list(self):
        self.task_listbox.delete(0, tk.END)
        for task in self.tasks:
            self.task_listbox.insert(tk.END, task['description'])

    def clear_entries(self):
        self.description_entry.delete(0, tk.END)
        self.deadline_entry.delete(0, tk.END)

    def set_notification(self):
        selected_index = self.task_listbox.curselection()
        if not selected_index:
            messagebox.showerror("Error", "Please select a task.")
            return

        index = selected_index[0]
        task = self.tasks[index]

        if task['deadline'] != 'Not set':
            notification_title = "Task Reminder"
            notification_message = f"Don't forget: {task['description']}\nDeadline: {task['deadline']}"

            # Prompt user for notification time in minutes
            notification_time = simpledialog.askinteger("Notification Time", "Enter notification time in minutes:")
            if notification_time is not None and notification_time > 0:
                # Convert minutes to seconds
                time_difference = notification_time * 60

                # Schedule notification using a separate thread
                threading.Timer(time_difference, self.show_notification, [notification_title, notification_message]).start()

                messagebox.showinfo("Notification Set", f"Notification will be shown after {notification_time} minutes.")
            else:
                messagebox.showinfo("Notification", "Invalid notification time. Please enter a positive number.")
        else:
            messagebox.showinfo("Notification", "Task has no deadline. Set a deadline before adding a notification.")

    def show_notification(self, title, message):
        notification.notify(
            title=title,
            message=message,
            timeout=10,
            toast=True,
            app_icon=None,
        )

    def mark_task(self, status):
        selected_index = self.task_listbox.curselection()
        if not selected_index:
            messagebox.showerror("Error", "Please select a task.")
            return

        index = selected_index[0]
        self.tasks[index]['status'] = status

        # Save tasks to the database
        connection = connect_to_database()
        if connection:
            try:
                query = "UPDATE tasks SET status = %s WHERE TaskId = %s"
                data = (status, self.tasks[index]['TaskId'])
                execute_query(connection, query, data)
                connection.commit()
            except Exception as e:
                print(f"Error updating task status in database: {e}")
                connection.rollback()
            finally:
                close_connection(connection)

        messagebox.showinfo("Task Updated", f"Task marked as {'Complete' if status else 'Incomplete'}.")
        self.update_task_list()

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()
