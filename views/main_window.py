import tkinter as tk
from tkinter import ttk, Menu
from database.database_manager import DatabaseManager
from controllers.task_controller import TaskController
from controllers.project_controller import ProjectController
from controllers.user_controller import UserController
from views.task_view import TaskView
from views.project_view import ProjectView
from views.user_view import UserView


class MainWindow:
    def __init__(self, db_path="tasks.db"):
        self.root = tk.Tk()
        self.root.title("Система управления задачами")
        self.root.geometry("1200x700")
        
        self.db_manager = DatabaseManager(db_path)
        self.task_controller = TaskController(self.db_manager)
        self.project_controller = ProjectController(self.db_manager)
        self.user_controller = UserController(self.db_manager)
        
        self._create_menu()
        
        self._create_notebook()
        
        self._create_status_bar()
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _create_menu(self):
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Обновить все", command=self.refresh_all)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self._on_closing)
        
        task_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Задачи", menu=task_menu)
        task_menu.add_command(label="Новая задача", command=self._add_new_task)
        task_menu.add_separator()
        task_menu.add_command(label="Обновить список", command=self.refresh_tasks)
        
        project_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Проекты", menu=project_menu)
        project_menu.add_command(label="Новый проект", command=self._add_new_project)
        project_menu.add_separator()
        project_menu.add_command(label="Обновить список", command=self.refresh_projects)
        
        user_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Пользователи", menu=user_menu)
        user_menu.add_command(label="Новый пользователь", command=self._add_new_user)
        user_menu.add_separator()
        user_menu.add_command(label="Обновить список", command=self.refresh_users)
        
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self._show_about)

    def _create_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.task_view = TaskView(self.notebook, self.task_controller, 
                                 self.project_controller, self.user_controller)
        self.project_view = ProjectView(self.notebook, self.project_controller)
        self.user_view = UserView(self.notebook, self.user_controller)
        
        self.notebook.add(self.task_view, text="Задачи")
        self.notebook.add(self.project_view, text="Проекты")
        self.notebook.add(self.user_view, text="Пользователи")

    def _create_status_bar(self):
        self.status_bar = tk.Label(self.root, text="Готово", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self._update_statistics()

    def _update_statistics(self):
        try:
            all_tasks = self.task_controller.get_all_tasks()
            overdue_tasks = self.task_controller.get_overdue_tasks()
            all_projects = self.project_controller.get_all_projects()
            all_users = self.user_controller.get_all_users()
            
            stats_text = f"Задачи: {len(all_tasks)} | Просрочено: {len(overdue_tasks)} | "
            stats_text += f"Проекты: {len(all_projects)} | Пользователи: {len(all_users)}"
            
            self.status_bar.config(text=stats_text)
            
        except Exception as e:
            print(f"Ошибка обновления статистики: {e}")

    def _add_new_task(self):
        self.notebook.select(0)
        self.task_view.add_task()

    def _add_new_project(self):
        self.notebook.select(1)
        self.project_view.add_project()

    def _add_new_user(self):
        self.notebook.select(2)
        self.user_view.add_user()

    def _show_about(self):
        import tkinter.messagebox as messagebox
        messagebox.showinfo("О программе", 
                          "Система управления задачами\nВерсия 1.0")

    def refresh_all(self):
        self.refresh_tasks()
        self.refresh_projects()
        self.refresh_users()
        self._update_statistics()

    def refresh_tasks(self):
        self.task_view.refresh_tasks()

    def refresh_projects(self):
        self.project_view.refresh_projects()

    def refresh_users(self):
        self.user_view.refresh_users()

    def _on_closing(self):
        import tkinter.messagebox as messagebox
        if messagebox.askokcancel("Выход", "Вы уверены, что хотите выйти?"):
            self.db_manager.close()
            self.root.destroy()

    def run(self):
        self.root.mainloop()