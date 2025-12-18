from datetime import datetime

class Project:
    def __init__(self, name, description, start_date, end_date, id=None, status='active'):
        self.id = id
        self.name = name
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.status = status
        
        valid_statuses = ['active', 'completed', 'on_hold']
        if status not in valid_statuses:
            raise ValueError(f"Статус должен быть одним из: {valid_statuses}")
        
        if start_date and end_date and start_date > end_date:
            raise ValueError("Дата начала не может быть позже даты окончания")

    def update_status(self, new_status):
        valid_statuses = ['active', 'completed', 'on_hold']
        if new_status not in valid_statuses:
            raise ValueError(f"Статус должен быть одним из: {valid_statuses}")
        self.status = new_status

    def get_progress(self):
        if self.status == 'completed':
            return 100.0
        elif self.status == 'on_hold':
            return 0.0
        else:
            return 50.0

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'progress': self.get_progress()
        }