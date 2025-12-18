from datetime import datetime
from typing import List, Optional, Dict, Any
from models.user import User
from database.database_manager import DatabaseManager

class UserController:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def add_user(self, username: str, email: str, role: str) -> User:
        if not username or not username.strip():
            raise ValueError("Имя пользователя не может быть пустым")
        
        user = User(username, email, role)
        if not user._is_valid_email(email):
            raise ValueError("Некорректный email адрес")
        
        valid_roles = ['admin', 'manager', 'developer']
        if role not in valid_roles:
            raise ValueError(f"Роль должна быть одной из: {valid_roles}")
        
        all_users = self.get_all_users()
        for existing_user in all_users:
            if existing_user.username == username:
                raise ValueError(f"Пользователь с именем '{username}' уже существует")
            
            if existing_user.email == email:
                raise ValueError(f"Пользователь с email '{email}' уже существует")
        
        user = User(
            username=username,
            email=email,
            role=role
        )
        
        user_id = self.db_manager.add_user(user)
        user.id = user_id
        
        return user


    def get_user(self, user_id: int) -> Optional[User]:
        return self.db_manager.get_user_by_id(user_id)

    def get_all_users(self) -> List[User]:
        return self.db_manager.get_all_users()

    def update_user(self, user_id: int, **kwargs) -> bool:

        if not kwargs:
            return False
        
        if 'role' in kwargs:
            role = kwargs['role']
            valid_roles = ['admin', 'manager', 'developer']
            if role not in valid_roles:
                raise ValueError(f"Роль должна быть одной из: {valid_roles}")
        
        if 'email' in kwargs:
            email = kwargs['email']
            user = User("temp", email, "developer")
            if not user._is_valid_email(email):
                raise ValueError("Некорректный email адрес")
            
            all_users = self.get_all_users()
            for existing_user in all_users:
                if existing_user.id != user_id and existing_user.email == email:
                    raise ValueError(f"Пользователь с email '{email}' уже существует")
        
        if 'username' in kwargs:
            username = kwargs['username']
            if not username or not username.strip():
                raise ValueError("Имя пользователя не может быть пустым")
            
            all_users = self.get_all_users()
            for existing_user in all_users:
                if existing_user.id != user_id and existing_user.username == username:
                    raise ValueError(f"Пользователь с именем '{username}' уже существует")
        
        return self.db_manager.update_user(user_id, **kwargs)


    def delete_user(self, user_id: int) -> bool:
        return self.db_manager.delete_user(user_id)

    def get_user_tasks(self, user_id: int) -> List[Dict[str, Any]]:
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"Пользователь с ID {user_id} не найден")
        
        from controllers.task_controller import TaskController
        task_controller = TaskController(self.db_manager)
        tasks = task_controller.get_tasks_by_user(user_id)
        
        result = []
        for task in tasks:
            project = self.db_manager.get_project_by_id(task.project_id)
            project_name = project.name if project else "Неизвестный проект"
            
            task_info = task.to_dict()
            task_info['project_name'] = project_name
            task_info['is_overdue'] = task.is_overdue()
            
            result.append(task_info)
        
        return result