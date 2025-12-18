import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from models.task import Task


class TaskView(ttk.Frame):
    def __init__(self, parent, task_controller, project_controller, user_controller) -> None:
        super().__init__(parent)
        self.task_controller = task_controller
        self.project_controller = project_controller
        self.user_controller = user_controller
        
        self.tasks = []
        self.projects = []
        self.users = []
        self.selected_task_id = None
        
        self.create_widgets()
        
        self.refresh_tasks()
        self._load_projects()
        self._load_users()

    def create_widgets(self) -> None:
        control_frame = ttk.LabelFrame(self, text="Управление задачами")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Добавить задачу", 
                  command=self.add_task).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Удалить выбранную", 
                  command=self.delete_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Обновить", 
                  command=self.refresh_tasks).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Обновить статус", 
                  command=self.update_task_status).pack(side=tk.LEFT, padx=2)
        
        search_frame = ttk.Frame(control_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT, padx=2)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=2)
        search_entry.bind("<KeyRelease>", self.filter_tasks)
        
        filter_frame = ttk.Frame(control_frame)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Статус:").pack(side=tk.LEFT, padx=2)
        self.status_filter_var = tk.StringVar(value="Все")
        status_combo = ttk.Combobox(filter_frame, textvariable=self.status_filter_var,
                                   values=["Все", "pending", "in_progress", "completed"],
                                   state="readonly", width=15)
        status_combo.pack(side=tk.LEFT, padx=2)
        status_combo.bind("<<ComboboxSelected>>", self.filter_by_status)
        
        ttk.Label(filter_frame, text="Приоритет:").pack(side=tk.LEFT, padx=2)
        self.priority_filter_var = tk.StringVar(value="Все")
        priority_combo = ttk.Combobox(filter_frame, textvariable=self.priority_filter_var,
                                     values=["Все", "1 - Высокий", "2 - Средний", "3 - Низкий"],
                                     state="readonly", width=15)
        priority_combo.pack(side=tk.LEFT, padx=2)
        priority_combo.bind("<<ComboboxSelected>>", self.filter_by_priority)
        
        ttk.Button(filter_frame, text="Просроченные", 
                  command=self.filter_overdue).pack(side=tk.LEFT, padx=2)
        
        table_frame = ttk.LabelFrame(self, text="Список задач")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("ID", "Название", "Описание", "Приоритет", "Статус", 
                  "Срок", "Проект", "Исполнитель")
        
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        column_widths = {
            "ID": 50,
            "Название": 150,
            "Описание": 200,
            "Приоритет": 80,
            "Статус": 100,
            "Срок": 100,
            "Проект": 120,
            "Исполнитель": 100
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100))
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_task_select)
        
        self.tree.bind("<Double-1>", self.edit_task)

    def refresh_tasks(self) -> None:
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            self.tasks = self.task_controller.get_all_tasks()
            
            for task in self.tasks:
                project_name = self._get_project_name(task.project_id)
                user_name = self._get_user_name(task.assignee_id)
                
                self.tree.insert("", tk.END, values=(
                    task.id,
                    task.title,
                    task.description[:50] + "..." if len(task.description) > 50 else task.description,
                    task.priority,
                    task.status,
                    task.due_date.strftime("%d.%m.%Y"),
                    project_name,
                    user_name
                ))
            
            self.search_var.set("")
            self.status_filter_var.set("Все")
            self.priority_filter_var.set("Все")
            
            self.selected_task_id = None
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить задачи: {e}")

    def add_task(self) -> None:
        dialog = TaskFormDialog(self, self.task_controller, 
                               self.project_controller, self.user_controller)
        if dialog.result:
            self.refresh_tasks()

    def delete_selected(self) -> None:
        if not self.selected_task_id:
            messagebox.showwarning("Удаление", "Выберите задачу для удаления")
            return
        
        task_title = ""
        for task in self.tasks:
            if task.id == self.selected_task_id:
                task_title = task.title
                break
        
        if not task_title:
            messagebox.showerror("Ошибка", "Задача не найдена")
            return
        
        if not messagebox.askyesno("Удаление", f"Вы уверены, что хотите удалить задачу '{task_title}'?"):
            return
        
        try:
            if self.task_controller.delete_task(self.selected_task_id):
                messagebox.showinfo("Успех", "Задача успешно удалена")
                self.refresh_tasks()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить задачу")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка удаления: {e}")

    def on_task_select(self, event) -> None:
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            self.selected_task_id = item['values'][0]

    def edit_task(self, event) -> None:
        if not self.selected_task_id:
            return
        
        try:
            task = self.task_controller.get_task(self.selected_task_id)
            if not task:
                messagebox.showerror("Ошибка", "Задача не найден")
                return
            
            dialog = TaskFormDialog(self, self.task_controller,
                                  self.project_controller, self.user_controller,
                                  task=task)
            if dialog.result:
                self.refresh_tasks()
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить задачу: {e}")

    def update_task_status(self) -> None:
        if not self.selected_task_id:
            messagebox.showwarning("Обновление", "Выберите задачу для обновления статуса")
            return
        
        try:
            task = self.task_controller.get_task(self.selected_task_id)
            if not task:
                messagebox.showerror("Ошибка", "Задача не найдена")
                return
            
            new_status = simpledialog.askstring(
                "Обновление статуса",
                "Введите новый статус (pending, in_progress, completed):",
                initialvalue=task.status,
                parent=self
            )
            
            if new_status:
                if new_status not in ["pending", "in_progress", "completed"]:
                    messagebox.showerror("Ошибка", "Недопустимый статус")
                    return
                
                if self.task_controller.update_task_status(self.selected_task_id, new_status):
                    messagebox.showinfo("Успех", "Статус задачи обновлен")
                    self.refresh_tasks()
                else:
                    messagebox.showerror("Ошибка", "Не удалось обновить статус")
                    
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка обновления статуса: {e}")

    def _load_projects(self):
        try:
            self.projects = self.project_controller.get_all_projects()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить проекты: {e}")
            self.projects = []

    def _load_users(self):
        try:
            self.users = self.user_controller.get_all_users()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить пользователей: {e}")
            self.users = []

    def _get_project_name(self, project_id):
        for project in self.projects:
            if project.id == project_id:
                return project.name
        return f"ID: {project_id}"

    def _get_user_name(self, user_id):
        for user in self.users:
            if user.id == user_id:
                return user.username
        return f"ID: {user_id}"

    def filter_tasks(self, event) -> None:
        search_text = self.search_var.get().lower()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        filtered_tasks = []
        for task in self.tasks:
            if (search_text in task.title.lower() or 
                search_text in task.description.lower() or
                search_text in str(task.priority) or
                search_text in task.status.lower()):
                filtered_tasks.append(task)
        
        filtered_tasks = self._apply_status_filter(filtered_tasks)
        filtered_tasks = self._apply_priority_filter(filtered_tasks)
        
        for task in filtered_tasks:
            project_name = self._get_project_name(task.project_id)
            user_name = self._get_user_name(task.assignee_id)
            
            self.tree.insert("", tk.END, values=(
                task.id,
                task.title,
                task.description[:50] + "..." if len(task.description) > 50 else task.description,
                task.priority,
                task.status,
                task.due_date.strftime("%d.%m.%Y"),
                project_name,
                user_name
            ))

    def filter_by_status(self, event=None) -> None:
        self.filter_tasks(None)

    def filter_by_priority(self, event=None) -> None:
        self.filter_tasks(None)

    def filter_overdue(self) -> None:
        try:
            overdue_tasks = self.task_controller.get_overdue_tasks()
            
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            for task in overdue_tasks:
                project_name = self._get_project_name(task.project_id)
                user_name = self._get_user_name(task.assignee_id)
                
                self.tree.insert("", tk.END, values=(
                    task.id,
                    task.title,
                    task.description[:50] + "..." if len(task.description) > 50 else task.description,
                    task.priority,
                    task.status,
                    task.due_date.strftime("%d.%m.%Y"),
                    project_name,
                    user_name
                ))
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить просроченные задачи: {e}")

    def _apply_status_filter(self, tasks):
        status = self.status_filter_var.get()
        if status == "Все":
            return tasks
        return [task for task in tasks if task.status == status]

    def _apply_priority_filter(self, tasks):
        priority_str = self.priority_filter_var.get()
        if priority_str == "Все":
            return tasks
        
        try:
            priority = int(priority_str[0])
            return [task for task in tasks if task.priority == priority]
        except (ValueError, IndexError):
            return tasks


class TaskFormDialog:
    
    def __init__(self, parent, task_controller, project_controller, 
                 user_controller, task=None):
        self.task_controller = task_controller
        self.project_controller = project_controller
        self.user_controller = user_controller
        self.task = task
        self.result = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Новая задача" if not task else "Редактирование задачи")
        self.dialog.geometry("500x350")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._create_widgets()
        
        if task:
            self._populate_form()
        
        self.dialog.wait_window()

    def _create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Название задачи*:").grid(row=0, column=0, 
                                                            sticky=tk.W, pady=5)
        self.title_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.title_var, width=30).grid(
            row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(main_frame, text="Описание:").grid(row=1, column=0, 
                                                    sticky=tk.W, pady=5)
        self.description_text = tk.Text(main_frame, width=30, height=4)
        self.description_text.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(main_frame, text="Приоритет*:").grid(row=2, column=0, 
                                                      sticky=tk.W, pady=5)
        self.priority_var = tk.IntVar(value=2)
        priority_frame = ttk.Frame(main_frame)
        priority_frame.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        ttk.Radiobutton(priority_frame, text="Высокий (1)", 
                       variable=self.priority_var, value=1).pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(priority_frame, text="Средний (2)", 
                       variable=self.priority_var, value=2).pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(priority_frame, text="Низкий (3)", 
                       variable=self.priority_var, value=3).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(main_frame, text="Статус:").grid(row=3, column=0, 
                                                  sticky=tk.W, pady=5)
        self.status_var = tk.StringVar(value="pending")
        status_combo = ttk.Combobox(main_frame, textvariable=self.status_var,
                                   values=["pending", "in_progress", "completed"],
                                   state="readonly", width=15)
        status_combo.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(main_frame, text="Срок выполнения* (ГГГГ-ММ-ДД):").grid(row=4, column=0, 
                                                                       sticky=tk.W, pady=5)
        default_date = datetime.now().replace(day=datetime.now().day + 7)
        self.due_date_var = tk.StringVar(value=default_date.strftime("%Y-%m-%d"))
        ttk.Entry(main_frame, textvariable=self.due_date_var, width=30).grid(
            row=4, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(main_frame, text="Проект*:").grid(row=5, column=0, 
                                                   sticky=tk.W, pady=5)
        self.project_var = tk.StringVar()
        self.project_combo = ttk.Combobox(main_frame, textvariable=self.project_var,
                                         state="readonly", width=30)
        self.project_combo.grid(row=5, column=1, sticky=tk.W, pady=5)
        self._load_projects()
        
        ttk.Label(main_frame, text="Исполнитель*:").grid(row=6, column=0, 
                                                        sticky=tk.W, pady=5)
        self.user_var = tk.StringVar()
        self.user_combo = ttk.Combobox(main_frame, textvariable=self.user_var,
                                      state="readonly", width=30)
        self.user_combo.grid(row=6, column=1, sticky=tk.W, pady=5)
        self._load_users()
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Сохранить", 
                  command=self._save_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена", 
                  command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

    def _load_projects(self):
        try:
            projects = self.project_controller.get_all_projects()
            project_list = [f"{project.id}: {project.name}" for project in projects]
            self.project_combo['values'] = project_list
            self.project_map = {item: project.id for item, project in zip(project_list, projects)}
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить проекты: {e}")

    def _load_users(self):
        try:
            users = self.user_controller.get_all_users()
            user_list = [f"{user.id}: {user.username}" for user in users]
            self.user_combo['values'] = user_list
            self.user_map = {item: user.id for item, user in zip(user_list, users)}
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить пользователей: {e}")

    def _populate_form(self):
        if not self.task:
            return
        
        self.title_var.set(self.task.title)
        self.description_text.delete(1.0, tk.END)
        self.description_text.insert(1.0, self.task.description)
        self.priority_var.set(self.task.priority)
        self.status_var.set(self.task.status)
        self.due_date_var.set(self.task.due_date.strftime("%Y-%m-%d"))
        
        for key, value in self.project_map.items():
            if value == self.task.project_id:
                self.project_var.set(key)
                break
        
        for key, value in self.user_map.items():
            if value == self.task.assignee_id:
                self.user_var.set(key)
                break

    def _get_project_id(self):
        selected = self.project_var.get()
        return self.project_map.get(selected)

    def _get_user_id(self):
        selected = self.user_var.get()
        return self.user_map.get(selected)

    def _save_task(self):
        try:
            if not self.title_var.get().strip():
                messagebox.showerror("Ошибка", "Введите название задачи")
                return
            
            if not self.due_date_var.get():
                messagebox.showerror("Ошибка", "Введите срок выполнения")
                return
            
            if not self._get_project_id():
                messagebox.showerror("Ошибка", "Выберите проект")
                return
            
            if not self._get_user_id():
                messagebox.showerror("Ошибка", "Выберите исполнителя")
                return
            
            title = self.title_var.get().strip()
            description = self.description_text.get(1.0, tk.END).strip()
            priority = self.priority_var.get()
            status = self.status_var.get()
            
            due_date = datetime.strptime(self.due_date_var.get(), "%Y-%m-%d")
            
            project_id = self._get_project_id()
            assignee_id = self._get_user_id()
            
            if self.task:
                success = self.task_controller.update_task(
                    self.task.id,
                    title=title,
                    description=description,
                    priority=priority,
                    status=status,
                    due_date=due_date,
                    project_id=project_id,
                    assignee_id=assignee_id
                )
                if not success:
                    messagebox.showerror("Ошибка", "Не удалось обновить задачу")
                    return
            else:
                self.task_controller.add_task(
                    title=title,
                    description=description,
                    priority=priority,
                    due_date=due_date,
                    project_id=project_id,
                    assignee_id=assignee_id
                )
            
            self.result = True
            self.dialog.destroy()
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректный формат даты. Используйте ГГГГ-ММ-ДД")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить задачу: {e}")