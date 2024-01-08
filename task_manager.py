import tkinter as tk
from tkinter import simpledialog, messagebox
from plyer import notification
from db_connector import connect_to_database, execute_query, close_connection
import threading

class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager")
        self.tasks_table = "tasks"
        self.notifications_table = "notifications"
        self.users_table = "users"
        self.current_user = None  # To store the current user after login
        self.tasks = self.load_tasks_from_database()
        self.notifications = self.load_notifications_from_database()

        # Set a background color
        self.root.configure(bg="#ADD8E6")

        self.create_widgets()

    def create_widgets(self):
        # Entry Page
        tk.Label(self.root, text="Task Description:", bg="#F0F0F0", font=("Helvetica", 12)).grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)
        tk.Label(self.root, text="Task Deadline:", bg="#F0F0F0", font=("Helvetica", 12)).grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
        tk.Button(self.root, text="Add Task", command=self.add_task, font=("Helvetica", 12), state=tk.DISABLED).grid(row=2, column=0, columnspan=2, pady=10)
        
        self.add_task_button = tk.Button(self.root, text="Add Task", command=self.add_task, font=("Helvetica", 12), state=tk.DISABLED)
        self.add_task_button.grid(row=2, column=0, columnspan=2, pady=10)
        self.description_entry = tk.Entry(self.root, font=("Helvetica", 12))
        self.description_entry.grid(row=0, column=1, padx=5, pady=5)

        self.deadline_entry = tk.Entry(self.root, font=("Helvetica", 12))
        self.deadline_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(self.root, text="Add Task", command=self.add_task, font=("Helvetica", 12), state=tk.DISABLED).grid(row=2, column=0, columnspan=2, pady=10)

        # List of Tasks
        self.task_listbox = tk.Listbox(self.root, font=("Helvetica", 12), selectmode=tk.SINGLE)
        self.task_listbox.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        tk.Button(self.root, text="Set Notification", command=self.set_notification, font=("Helvetica", 12)).grid(row=4, column=0, columnspan=2, pady=5)
        tk.Button(self.root, text="Show Tasks", command=self.show_tasks, font=("Helvetica", 12)).grid(row=5, column=0, pady=5)
        tk.Button(self.root, text="Mark as Complete", command=lambda: self.mark_task(status=True), font=("Helvetica", 12)).grid(row=5, column=1, pady=5)
        tk.Button(self.root, text="Mark as Incomplete", command=lambda: self.mark_task(status=False), font=("Helvetica", 12)).grid(row=6, column=0, columnspan=2, pady=5)
        tk.Button(self.root, text="Register", command=self.show_register_window, font=("Helvetica", 12)).grid(row=7, column=0, columnspan=2, pady=10)
        tk.Button(self.root, text="Login", command=self.show_login_window, font=("Helvetica", 12)).grid(row=8, column=0, columnspan=2, pady=10)
        self.add_task_button = tk.Button(self.root, text="Add Task", command=self.add_task, font=("Helvetica", 12), state=tk.DISABLED)
        self.add_task_button.grid(row=2, column=0, columnspan=2, pady=10)
  
    def load_tasks_from_database(self):
        connection = connect_to_database()
        tasks = []
        if connection:
            try:
                query = f"SELECT * FROM {self.tasks_table}"
                result = execute_query(connection, query)
                tasks = [{'TaskId': row[0], 'description': row[1], 'deadline': row[2], 'status': row[3]} for row in result]
            except Exception as e:
                print(f"Error loading tasks from database: {e}")
            finally:
                close_connection(connection)
        return tasks

    def load_notifications_from_database(self):
        connection = connect_to_database()
        notifications = []
        if connection:
            try:
                query = f"SELECT * FROM {self.notifications_table}"
                result = execute_query(connection, query)
                notifications = [{'NotificationId': row[0], 'title': row[1], 'message': row[2], 'task_id': row[3]} for row in result]
            except Exception as e:
                print(f"Error loading notifications from database: {e}")
            finally:
                close_connection(connection)
        return notifications

    def register_user(self):
        username = self.register_username_entry.get()
        password = self.register_password_entry.get()


        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password.")
            return

        if self.check_username_exists(username):
            messagebox.showerror("Error", "Username already exists. Choose a different username.")
            return

        connection = connect_to_database()
        if connection:
            try:
                query = f"INSERT INTO {self.users_table} (username, password) VALUES (%s, %s)"
                data = (username, password)
                execute_query(connection, query, data)
                connection.commit()
                print("User registered successfully.")
                messagebox.showinfo("Registration", "User registered successfully.")
                self.clear_registration_entries()
            except Exception as e:
                print(f"Error registering user: {e}")
                connection.rollback()
            finally:
                close_connection(connection)

    def login_user(self):
        username = self.login_username_entry.get()
        password = self.login_password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password.")
            return

        if self.check_user_credentials(username, password):
            print("Login successful.")
            messagebox.showinfo("Login", "Login successful.")
            self.current_user = username

        # Enable the "Add Task" button and other functionalities after successful login
            self.add_task_button.config(state=tk.NORMAL)
        # Add similar lines to enable other buttons if needed

        else:
            messagebox.showerror("Error", "Invalid username or password.")


    def check_username_exists(self, username):
        connection = connect_to_database()
        if connection:
            try:
                query = f"SELECT * FROM {self.users_table} WHERE username = %s"
                data = (username,)
                result = execute_query(connection, query, data)
                return bool(result)
            except Exception as e:
                print(f"Error checking username existence: {e}")
            finally:
                close_connection(connection)
        return False

    def check_user_credentials(self, username, password):
        connection = connect_to_database()
        if connection:
            try:
                query = f"SELECT * FROM {self.users_table} WHERE username = %s AND password = %s"
                data = (username, password)
                result = execute_query(connection, query, data)
                return bool(result)
            except Exception as e:
                print(f"Error checking user credentials: {e}")
            finally:
                close_connection(connection)
        return False

    def clear_registration_entries(self):
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

    def add_task(self):
        # Check if a user is logged in before allowing to add a task
        if not self.current_user:
            messagebox.showerror("Error", "Please login before adding a task.")
            return

        description = self.description_entry.get()
        deadline = self.deadline_entry.get() or 'Not set'

        task_id = len(self.tasks) + 1

        task = {'TaskId': task_id, 'description': description, 'deadline': deadline, 'status': False}
        self.tasks.append(task)

        connection = connect_to_database()
        if connection:
            try:
                query = f"INSERT INTO {self.tasks_table} (description, deadline, status, username) VALUES (%s, %s, %s, %s)"
                data = (task['description'], task['deadline'], task['status'], self.current_user)
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
        connection = connect_to_database()
        if connection:
            try:
                query = f"SELECT * FROM {self.tasks_table} WHERE username = %s"
                data = (self.current_user,)
                result = execute_query(connection, query, data)
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

            notification_time = simpledialog.askinteger("Notification Time", "Enter notification time in minutes:")
            if notification_time is not None and notification_time > 0:
                time_difference = notification_time * 60

                threading.Timer(time_difference, self.show_notification, [notification_title, notification_message]).start()

                connection = connect_to_database()
                if connection:
                    try:
                        query = f"INSERT INTO {self.notifications_table} (title, message, task_id) VALUES (%s, %s, %s)"
                        data = (notification_title, notification_message, task['TaskId'])
                        execute_query(connection, query, data)
                        connection.commit()
                    except Exception as e:
                        print(f"Error adding notification to database: {e}")
                        connection.rollback()
                    finally:
                        close_connection(connection)

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

        connection = connect_to_database()
        if connection:
            try:
                query = f"UPDATE {self.tasks_table} SET status = %s WHERE TaskId = %s"
                data = (status, self.tasks[index]['TaskId'])
                execute_query(connection, query, data)
                connection.commit()
            except Exception as e:
                print(f"Error updating task status in database: {e}")
                connection.rollback()
    def show_register_window(self):
        register_window = tk.Toplevel(self.root)
        register_window.title("Register")

        tk.Label(register_window, text="Username:", font=("Helvetica", 12)).grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        tk.Label(register_window, text="Password:", font=("Helvetica", 12)).grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)

        self.register_username_entry = tk.Entry(register_window, font=("Helvetica", 12))
        self.register_username_entry.grid(row=0, column=1, padx=5, pady=5)

        self.register_password_entry = tk.Entry(register_window, show="*", font=("Helvetica", 12))
        self.register_password_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(register_window, text="Register", command=self.register_user, font=("Helvetica", 12)).grid(row=2, column=0, columnspan=2, pady=10)

    def show_login_window(self):
        login_window = tk.Toplevel(self.root)
        login_window.title("Login")

        tk.Label(login_window, text="Username:", font=("Helvetica", 12)).grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        tk.Label(login_window, text="Password:", font=("Helvetica", 12)).grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)

        self.login_username_entry = tk.Entry(login_window, font=("Helvetica", 12))
        self.login_username_entry.grid(row=0, column=1, padx=5, pady=5)

        self.login_password_entry = tk.Entry(login_window, show="*", font=("Helvetica", 12))
        self.login_password_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(login_window, text="Login", command=self.login_user, font=("Helvetica", 12)).grid(row=2, column=0, columnspan=2, pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()
