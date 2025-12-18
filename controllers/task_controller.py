from datetime import datetime
from typing import List, Optional, Dict, Any
from models.task import Task
from database.database_manager import DatabaseManager

class TaskController:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def add_task(self, title: str, description: str, priority: int, 
                due_date: datetime, project_id: int, assignee_id: int) -> Task:
        if priority not in [1, 2, 3]:
            raise ValueError("Приоритет должен быть 1 (высокий), 2 (средний) или 3 (низкий)")
        
        project = self.db_manager.get_project_by_id(project_id)
        if not project:
            raise ValueError(f"Проект с ID {project_id} не найден")
            
        user = self.db_manager.get_user_by_id(assignee_id)
        if not user:
            raise ValueError(f"Пользователь с ID {assignee_id} не найден")
        
        if due_date < datetime.now():
            raise ValueError("Дата выполнения не может быть в прошлом")
        
        task = Task(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            project_id=project_id,
            assignee_id=assignee_id
        )
        
        task_id = self.db_manager.add_task(task)
        task.id = task_id
        
        return task

    def get_task(self, task_id: int) -> Optional[Task]:
        return self.db_manager.get_task_by_id(task_id)

    def get_all_tasks(self) -> List[Task]:
        return self.db_manager.get_all_tasks()

    def update_task(self, task_id: int, **kwargs) -> bool:
        if not kwargs:
            return False
        
        if 'priority' in kwargs:
            priority = kwargs['priority']
            if priority not in [1, 2, 3]:
                raise ValueError("Приоритет должен быть 1 (высокий), 2 (средний) или 3 (низкий)")
        
        if 'status' in kwargs:
            status = kwargs['status']
            valid_statuses = ['pending', 'in_progress', 'completed']
            if status not in valid_statuses:
                raise ValueError(f"Статус должен быть одним из: {valid_statuses}")
        
        if 'due_date' in kwargs:
            due_date = kwargs['due_date']
            if not isinstance(due_date, datetime):
                raise ValueError("due_date должен быть datetime объектом")
            if due_date < datetime.now():
                print(f"Внимание: Задача {task_id} имеет прошедшую дату выполнения")
        
        if 'project_id' in kwargs:
            project_id = kwargs['project_id']
            project = self.db_manager.get_project_by_id(project_id)
            if not project:
                raise ValueError(f"Проект с ID {project_id} не найден")
        
        if 'assignee_id' in kwargs:
            assignee_id = kwargs['assignee_id']
            user = self.db_manager.get_user_by_id(assignee_id)
            if not user:
                raise ValueError(f"Пользователь с ID {assignee_id} не найден")
        
        return self.db_manager.update_task(task_id, **kwargs)

    def delete_task(self, task_id: int) -> bool:
        return self.db_manager.delete_task(task_id)

    def search_tasks(self, query: str) -> List[Task]:
        if not query or not query.strip():
            return []
        
        return self.db_manager.search_tasks(query)

    def update_task_status(self, task_id: int, new_status: str) -> bool:
        valid_statuses = ['pending', 'in_progress', 'completed']
        if new_status not in valid_statuses:
            raise ValueError(f"Статус должен быть одним из: {valid_statuses}")
        
        return self.db_manager.update_task(task_id, status=new_status)

    def get_overdue_tasks(self) -> List[Task]:

        all_tasks = self.get_all_tasks()
        overdue_tasks = []
        
        current_time = datetime.now()
        
        for task in all_tasks:
            if task.status != 'completed' and task.due_date < current_time:
                overdue_tasks.append(task)
                
        return overdue_tasks

    def get_tasks_by_project(self, project_id: int) -> List[Task]:
        project = self.db_manager.get_project_by_id(project_id)
        if not project:
            raise ValueError(f"Проект с ID {project_id} не найден")
        
        return self.db_manager.get_tasks_by_project(project_id)
    
    def get_tasks_by_user(self, user_id: int) -> List[Task]:
        user = self.db_manager.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"Пользователь с ID {user_id} не найден")
        
        return self.db_manager.get_tasks_by_user(user_id)