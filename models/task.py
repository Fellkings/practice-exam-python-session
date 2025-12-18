from datetime import datetime

class Task:
    def __init__(self, title, description, priority, due_date, project_id, assignee_id, 
                 id=None, status='pending'):
        self.id = id
        self.title = title
        self.description = description
        self.priority = priority
        self.status = status
        self.due_date = due_date
        self.project_id = project_id
        self.assignee_id = assignee_id
        
        if priority not in [1, 2, 3]:
            raise ValueError("Приоритет должен быть 1 (высокий), 2 (средний) или 3 (низкий)")
        
        valid_statuses = ['pending', 'in_progress', 'completed']
        if status not in valid_statuses:
            raise ValueError(f"Статус должен быть одним из: {valid_statuses}")

    def update_status(self, new_status):
        valid_statuses = ['pending', 'in_progress', 'completed']
        if new_status not in valid_statuses:
            raise ValueError(f"Статус должен быть одним из: {valid_statuses}")
        self.status = new_status

    def is_overdue(self):
        if self.status == 'completed':
            return False
        return datetime.now() > self.due_date

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'project_id': self.project_id,
            'assignee_id': self.assignee_id
        }