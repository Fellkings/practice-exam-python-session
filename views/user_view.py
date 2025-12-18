import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from models.user import User


class UserView(ttk.Frame):
    def __init__(self, parent, user_controller) -> None:
        super().__init__(parent)
        self.user_controller = user_controller
        
        self.users = []
        self.selected_user_id = None
        
        self.create_widgets()
        
        self.refresh_users()

    def create_widgets(self) -> None:
        control_frame = ttk.LabelFrame(self, text="Управление пользователями")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Добавить пользователя", 
                  command=self.add_user).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Удалить выбранного", 
                  command=self.delete_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Обновить", 
                  command=self.refresh_users).pack(side=tk.LEFT, padx=2)
        
        search_frame = ttk.Frame(control_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Поиск по имени:").pack(side=tk.LEFT, padx=2)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=2)
        search_entry.bind("<KeyRelease>", self.filter_users)
        
        filter_frame = ttk.Frame(control_frame)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Роль:").pack(side=tk.LEFT, padx=2)
        self.role_filter_var = tk.StringVar(value="Все")
        role_combo = ttk.Combobox(filter_frame, textvariable=self.role_filter_var,
                                 values=["Все", "admin", "manager", "developer"],
                                 state="readonly", width=15)
        role_combo.pack(side=tk.LEFT, padx=2)
        role_combo.bind("<<ComboboxSelected>>", self.filter_by_role)
        
        table_frame = ttk.LabelFrame(self, text="Список пользователей")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("ID", "Имя пользователя", "Email", "Роль", "Дата регистрации")
        
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        column_widths = {
            "ID": 50,
            "Имя пользователя": 150,
            "Email": 200,
            "Роль": 100,
            "Дата регистрации": 120
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100))
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_user_select)
        
        self.tree.bind("<Double-1>", self.edit_user)

    def refresh_users(self) -> None:
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            self.users = self.user_controller.get_all_users()
            
            for user in self.users:
                self.tree.insert("", tk.END, values=(
                    user.id,
                    user.username,
                    user.email,
                    user.role,
                    user.registration_date.strftime("%d.%m.%Y")
                ))
            
            self.search_var.set("")
            self.role_filter_var.set("Все")
            
            self.selected_user_id = None
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить пользователей: {e}")

    def add_user(self) -> None:
        dialog = UserFormDialog(self, self.user_controller)
        if dialog.result:
            self.refresh_users()

    def delete_selected(self) -> None:
        if not self.selected_user_id:
            messagebox.showwarning("Удаление", "Выберите пользователя для удаления")
            return
        
        username = ""
        for user in self.users:
            if user.id == self.selected_user_id:
                username = user.username
                break
        
        if not username:
            messagebox.showerror("Ошибка", "Пользователь не найден")
            return
        
        if not messagebox.askyesno("Удаление", f"Вы уверены, что хотите удалить пользователя '{username}'?"):
            return
        
        try:
            if self.user_controller.delete_user(self.selected_user_id):
                messagebox.showinfo("Успех", "Пользователь успешно удален")
                self.refresh_users()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить пользователя")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка удаления: {e}")

    def on_user_select(self, event) -> None:
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            self.selected_user_id = item['values'][0]

    def edit_user(self, event) -> None:
        if not self.selected_user_id:
            return
        
        try:
            user = self.user_controller.get_user(self.selected_user_id)
            if not user:
                messagebox.showerror("Ошибка", "Пользователь не найден")
                return
            
            dialog = UserFormDialog(self, self.user_controller, user=user)
            if dialog.result:
                self.refresh_users()
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить пользователя: {e}")

    def filter_users(self, event) -> None:
        search_text = self.search_var.get().lower()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        filtered_users = []
        for user in self.users:
            if (search_text in user.username.lower() or 
                search_text in user.email.lower() or
                search_text in user.role.lower()):
                filtered_users.append(user)
        
        role = self.role_filter_var.get()
        if role != "Все":
            filtered_users = [u for u in filtered_users if u.role == role]
        
        for user in filtered_users:
            self.tree.insert("", tk.END, values=(
                user.id,
                user.username,
                user.email,
                user.role,
                user.registration_date.strftime("%d.%m.%Y")
            ))

    def filter_by_role(self, event=None) -> None:
        self.filter_users(None)


class UserFormDialog:
    def __init__(self, parent, user_controller, user=None):
        self.user_controller = user_controller
        self.user = user
        self.result = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Новый пользователь" if not user else "Редактирование пользователя")
        self.dialog.geometry("400x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._create_widgets()
        
        if user:
            self._populate_form()
        
        self.dialog.wait_window()

    def _create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Имя пользователя*:").grid(row=0, column=0, 
                                                             sticky=tk.W, pady=5)
        self.username_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.username_var, width=30).grid(
            row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(main_frame, text="Email*:").grid(row=1, column=0, 
                                                  sticky=tk.W, pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.email_var, width=30).grid(
            row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(main_frame, text="Роль*:").grid(row=2, column=0, 
                                                 sticky=tk.W, pady=5)
        self.role_var = tk.StringVar(value="developer")
        role_combo = ttk.Combobox(main_frame, textvariable=self.role_var,
                                 values=["admin", "manager", "developer"],
                                 state="readonly", width=15)
        role_combo.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Сохранить", 
                  command=self._save_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена", 
                  command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

    def _populate_form(self):
        if not self.user:
            return
        
        self.username_var.set(self.user.username)
        self.email_var.set(self.user.email)
        self.role_var.set(self.user.role)

    def _save_user(self):
        try:
            if not self.username_var.get().strip():
                messagebox.showerror("Ошибка", "Введите имя пользователя")
                return
            
            if not self.email_var.get().strip():
                messagebox.showerror("Ошибка", "Введите email")
                return
            
            if not self.role_var.get():
                messagebox.showerror("Ошибка", "Выберите роль")
                return
            
            username = self.username_var.get().strip()
            email = self.email_var.get().strip()
            role = self.role_var.get()
            
            temp_user = User(username, email, role)
            
            if self.user:
                success = self.user_controller.update_user(
                    self.user.id,
                    username=username,
                    email=email,
                    role=role
                )
                if not success:
                    messagebox.showerror("Ошибка", "Не удалось обновить пользователя")
                    return
            else:
                self.user_controller.add_user(
                    username=username,
                    email=email,
                    role=role
                )
            
            self.result = True
            self.dialog.destroy()
            
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить пользователя: {e}")