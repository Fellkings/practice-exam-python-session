import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
from datetime import datetime, timedelta
from models.project import Project


class ProjectView(ttk.Frame):
    def __init__(self, parent, project_controller) -> None:
        super().__init__(parent)
        self.project_controller = project_controller
        
        self.projects = []
        self.selected_project_id = None
        
        self.create_widgets()
        
        self.refresh_projects()

    def create_widgets(self) -> None:
        control_frame = ttk.LabelFrame(self, text="Управление проектами")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Добавить проект", 
                  command=self.add_project).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Удалить выбранный", 
                  command=self.delete_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Обновить", 
                  command=self.refresh_projects).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Обновить статус", 
                  command=self.update_project_status).pack(side=tk.LEFT, padx=2)
        
        search_frame = ttk.Frame(control_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Поиск по названию:").pack(side=tk.LEFT, padx=2)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=2)
        search_entry.bind("<KeyRelease>", self.filter_projects)
        
        filter_frame = ttk.Frame(control_frame)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Статус:").pack(side=tk.LEFT, padx=2)
        self.status_filter_var = tk.StringVar(value="Все")
        status_combo = ttk.Combobox(filter_frame, textvariable=self.status_filter_var,
                                   values=["Все", "active", "completed", "on_hold"],
                                   state="readonly", width=15)
        status_combo.pack(side=tk.LEFT, padx=2)
        status_combo.bind("<<ComboboxSelected>>", self.filter_by_status)
        
        table_frame = ttk.LabelFrame(self, text="Список проектов")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("ID", "Название", "Описание", "Дата начала", "Дата окончания", "Статус")
        
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        column_widths = {
            "ID": 50,
            "Название": 150,
            "Описание": 200,
            "Дата начала": 100,
            "Дата окончания": 100,
            "Статус": 80
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100))
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_project_select)
        
        self.tree.bind("<Double-1>", self.edit_project)

    def refresh_projects(self) -> None:
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            self.projects = self.project_controller.get_all_projects()
            
            for project in self.projects:
                self.tree.insert("", tk.END, values=(
                    project.id,
                    project.name,
                    project.description[:50] + "..." if len(project.description) > 50 else project.description,
                    project.start_date.strftime("%d.%m.%Y"),
                    project.end_date.strftime("%d.%m.%Y"),
                    project.status
                ))
            
            self.search_var.set("")
            self.status_filter_var.set("Все")
            
            self.selected_project_id = None
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить проекты: {e}")

    def add_project(self) -> None:
        dialog = ProjectFormDialog(self, self.project_controller)
        if dialog.result:
            self.refresh_projects()

    def delete_selected(self) -> None:
        if not self.selected_project_id:
            messagebox.showwarning("Удаление", "Выберите проект для удаления")
            return
        
        project_name = ""
        for project in self.projects:
            if project.id == self.selected_project_id:
                project_name = project.name
                break
        
        if not project_name:
            messagebox.showerror("Ошибка", "Проект не найден")
            return
        
        if not messagebox.askyesno("Удаление", f"Вы уверены, что хотите удалить проект '{project_name}'?"):
            return
        
        try:
            if self.project_controller.delete_project(self.selected_project_id):
                messagebox.showinfo("Успех", "Проект успешно удален")
                self.refresh_projects()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить проект")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка удаления: {e}")

    def on_project_select(self, event) -> None:
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            self.selected_project_id = item['values'][0]

    def edit_project(self, event) -> None:
        if not self.selected_project_id:
            return
        
        try:
            project = self.project_controller.get_project(self.selected_project_id)
            if not project:
                messagebox.showerror("Ошибка", "Проект не найден")
                return
            
            dialog = ProjectFormDialog(self, self.project_controller, project=project)
            if dialog.result:
                self.refresh_projects()
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить проект: {e}")

    def update_project_status(self) -> None:
        if not self.selected_project_id:
            messagebox.showwarning("Обновление", "Выберите проект для обновления статуса")
            return
        
        try:
            project = self.project_controller.get_project(self.selected_project_id)
            if not project:
                messagebox.showerror("Ошибка", "Проект не найден")
                return
            
            new_status = simpledialog.askstring(
                "Обновление статуса",
                "Введите новый статус (active, completed, on_hold):",
                initialvalue=project.status,
                parent=self
            )
            
            if new_status:
                if new_status not in ["active", "completed", "on_hold"]:
                    messagebox.showerror("Ошибка", "Недопустимый статус")
                    return
                
                if self.project_controller.update_project_status(self.selected_project_id, new_status):
                    messagebox.showinfo("Успех", "Статус проекта обновлен")
                    self.refresh_projects()
                else:
                    messagebox.showerror("Ошибка", "Не удалось обновить статус")
                    
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка обновления статуса: {e}")

    def filter_projects(self, event) -> None:
        search_text = self.search_var.get().lower()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        filtered_projects = []
        for project in self.projects:
            if (search_text in project.name.lower() or 
                search_text in project.description.lower()):
                filtered_projects.append(project)
        
        status = self.status_filter_var.get()
        if status != "Все":
            filtered_projects = [p for p in filtered_projects if p.status == status]
        
        for project in filtered_projects:
            self.tree.insert("", tk.END, values=(
                project.id,
                project.name,
                project.description[:50] + "..." if len(project.description) > 50 else project.description,
                project.start_date.strftime("%d.%m.%Y"),
                project.end_date.strftime("%d.%m.%Y"),
                project.status
            ))

    def filter_by_status(self, event=None) -> None:
        self.filter_projects(None)


class ProjectFormDialog:
    def __init__(self, parent, project_controller, project=None):
        self.project_controller = project_controller
        self.project = project
        self.result = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Новый проект" if not project else "Редактирование проекта")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.minsize(450, 350)
        
        self._create_widgets()
        
        if project:
            self._populate_form()
        
        self.dialog.wait_window()

    def _create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=0)
        
        ttk.Label(main_frame, text="Название проекта*:").grid(
            row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(main_frame, textvariable=self.name_var)
        name_entry.grid(row=0, column=1, sticky=tk.EW, pady=5)
        name_entry.focus_set()
        
        ttk.Label(main_frame, text="Описание:").grid(
            row=1, column=0, sticky=tk.NW, pady=5)
        self.description_text = scrolledtext.ScrolledText(
            main_frame, height=4, wrap=tk.WORD)
        self.description_text.grid(row=1, column=1, sticky=tk.NSEW, pady=5)
        
        ttk.Label(main_frame, text="Дата начала* (ГГГГ-ММ-ДД):").grid(
            row=2, column=0, sticky=tk.W, pady=5)
        self.start_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(main_frame, textvariable=self.start_date_var).grid(
            row=2, column=1, sticky=tk.EW, pady=5)
        
        ttk.Label(main_frame, text="Дата окончания* (ГГГГ-ММ-ДД):").grid(
            row=3, column=0, sticky=tk.W, pady=5)
        default_end_date = datetime.now() + timedelta(days=30)
        self.end_date_var = tk.StringVar(value=default_end_date.strftime("%Y-%m-%d"))
        ttk.Entry(main_frame, textvariable=self.end_date_var).grid(
            row=3, column=1, sticky=tk.EW, pady=5)
            
        ttk.Label(main_frame, text="Статус:").grid(
            row=4, column=0, sticky=tk.W, pady=5)
        self.status_var = tk.StringVar(value="active")
        status_combo = ttk.Combobox(
            main_frame, 
            textvariable=self.status_var,
            values=["active", "completed", "on_hold"],
            state="readonly"
        )
        status_combo.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=(20, 10))
        
        save_btn = ttk.Button(
            button_frame, 
            text="Сохранить", 
            command=self._save_project,
            width=15
        )
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_btn = ttk.Button(
            button_frame, 
            text="Отмена", 
            command=self.dialog.destroy,
            width=15
        )
        cancel_btn.pack(side=tk.LEFT)
        
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)

    def _populate_form(self):
        if not self.project:
            return
        
        self.name_var.set(self.project.name)
        self.description_text.delete(1.0, tk.END)
        self.description_text.insert(1.0, self.project.description or "")
        self.status_var.set(self.project.status)
        
        if isinstance(self.project.start_date, datetime):
            self.start_date_var.set(self.project.start_date.strftime("%Y-%m-%d"))
        elif isinstance(self.project.start_date, str):
            try:
                date_obj = datetime.fromisoformat(self.project.start_date.replace('Z', '+00:00'))
                self.start_date_var.set(date_obj.strftime("%Y-%m-%d"))
            except:
                self.start_date_var.set(datetime.now().strftime("%Y-%m-%d"))
        else:
            try:
                self.start_date_var.set(self.project.start_date.strftime("%Y-%m-%d"))
            except:
                self.start_date_var.set(datetime.now().strftime("%Y-%m-%d"))

        if isinstance(self.project.end_date, datetime):
            self.end_date_var.set(self.project.end_date.strftime("%Y-%m-%d"))
        elif isinstance(self.project.end_date, str):
            try:
                date_obj = datetime.fromisoformat(self.project.end_date.replace('Z', '+00:00'))
                self.end_date_var.set(date_obj.strftime("%Y-%m-%d"))
            except:
                default_end_date = datetime.now() + timedelta(days=30)
                self.end_date_var.set(default_end_date.strftime("%Y-%m-%d"))
        else:
            try:
                self.end_date_var.set(self.project.end_date.strftime("%Y-%m-%d"))
            except:
                default_end_date = datetime.now() + timedelta(days=30)
                self.end_date_var.set(default_end_date.strftime("%Y-%m-%d"))

    def _save_project(self):
        try:
            if not self.name_var.get().strip():
                messagebox.showerror("Ошибка", "Введите название проекта")
                return
            
            name = self.name_var.get().strip()
            description = self.description_text.get(1.0, tk.END).strip()
            status = self.status_var.get()
            
            start_date_str = self.start_date_var.get().strip()
            end_date_str = self.end_date_var.get().strip()
            
            if not start_date_str:
                messagebox.showerror("Ошибка", "Введите дату начала")
                return
            
            if not end_date_str:
                messagebox.showerror("Ошибка", "Введите дату окончания")
                return
            
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Ошибка", 
                    "Некорректный формат даты начала. Используйте ГГГГ-ММ-ДД (например: 2025-12-19)")
                return
            
            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Ошибка", 
                    "Некорректный формат даты окончания. Используйте ГГГГ-ММ-ДД (например: 2025-12-19)")
                return
            
            if start_date >= end_date:
                messagebox.showerror("Ошибка", "Дата начала должна быть раньше даты окончания")
                return
            
            print(f"Сохранение проекта: {name}")
            print(f"Дата начала: {start_date} (тип: {type(start_date)})")
            print(f"Дата окончания: {end_date} (тип: {type(end_date)})")
            
            if self.project:
                success = self.project_controller.update_project(
                    self.project.id,
                    name=name,
                    description=description,
                    start_date=start_date,
                    end_date=end_date,
                    status=status
                )
                if not success:
                    messagebox.showerror("Ошибка", "Не удалось обновить проект")
                    return
            else:
                try:
                    new_project = self.project_controller.add_project(
                        name=name,
                        description=description,
                        start_date=start_date,
                        end_date=end_date
                    )
                    print(f"Проект создан с ID: {new_project.id}")
                except ValueError as e:
                    messagebox.showerror("Ошибка валидации", str(e))
                    return
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось создать проект: {e}")
                    import traceback
                    traceback.print_exc()
                    return
            
            self.result = True
            self.dialog.destroy()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить проект: {e}")
            import traceback
            traceback.print_exc()