import re
from datetime import datetime

class User:
    def __init__(self, username, email, role, id=None, registration_date=None):
        self.id = id
        self.username = username
        self.email = email
        self.role = role
        self.registration_date = registration_date or datetime.now()
        
        if not self._is_valid_email(email):
            raise ValueError("Некорректный email адрес")
        
        valid_roles = ['admin', 'manager', 'developer']
        if role not in valid_roles:
            raise ValueError(f"Роль должна быть одной из: {valid_roles}")

    def _is_valid_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def update_info(self, username=None, email=None, role=None):
        if username is not None:
            self.username = username
            
        if email is not None:
            if not self._is_valid_email(email):
                raise ValueError("Некорректный email адрес")
            self.email = email
            
        if role is not None:
            valid_roles = ['admin', 'manager', 'developer']
            if role not in valid_roles:
                raise ValueError(f"Роль должна быть одной из: {valid_roles}")
            self.role = role

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'registration_date': self.registration_date.isoformat() if self.registration_date else None
        }