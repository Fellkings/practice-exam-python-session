from datetime import datetime
from typing import List, Optional, Dict, Any
from models.project import Project
from database.database_manager import DatabaseManager

class ProjectController:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def add_project(self, name: str, description: str, 
                   start_date: datetime, end_date: datetime) -> Project:
        if not name or not name.strip():
            raise ValueError("Название проекта не может быть пустым")
        
        if start_date >= end_date:
            raise ValueError("Дата начала должна быть раньше даты окончания")
        
        if start_date < datetime.now().date():
            raise ValueError("Дата начала не может быть в прошлом")
        
        project = Project(
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date
        )
        
        project_id = self.db_manager.add_project(project)
        project.id = project_id
        
        return project

    def get_project(self, project_id: int) -> Optional[Project]:
        return self.db_manager.get_project_by_id(project_id)

    def get_all_projects(self) -> List[Project]:
        return self.db_manager.get_all_projects()

    def update_project(self, project_id: int, **kwargs) -> bool:
        if not kwargs:
            return False
        
        if 'status' in kwargs:
            status = kwargs['status']
            valid_statuses = ['active', 'completed', 'on_hold']
            if status not in valid_statuses:
                raise ValueError(f"Статус должен быть одним из: {valid_statuses}")
        
        if 'start_date' in kwargs or 'end_date' in kwargs:
            project = self.get_project(project_id)
            if project:
                start_date = kwargs.get('start_date', project.start_date)
                end_date = kwargs.get('end_date', project.end_date)
                
                if start_date >= end_date:
                    raise ValueError("Дата начала должна быть раньше даты окончания")

        if 'name' in kwargs:
            name = kwargs['name']
            if not name or not name.strip():
                raise ValueError("Название проекта не может быть пустым")
        
        return self.db_manager.update_project(project_id, **kwargs)

    def delete_project(self, project_id: int) -> bool:
        return self.db_manager.delete_project(project_id)

    def update_project_status(self, project_id: int, new_status: str) -> bool:
        valid_statuses = ['active', 'completed', 'on_hold']
        if new_status not in valid_statuses:
            raise ValueError(f"Статус должен быть одним из: {valid_statuses}")
        
        return self.db_manager.update_project(project_id, status=new_status)

    def get_project_progress(self, project_id: int) -> float:
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Проект с ID {project_id} не найден")
        
        return project.get_progress()