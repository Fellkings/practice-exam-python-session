import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from models.task import Task
from models.project import Project
from models.user import User


class DatabaseManager:
    def __init__(self, db_path: str = "tasks.db") -> None:
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        self._connect()
        self.create_tables()

    def _connect(self) -> None:
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            self.connection.execute("PRAGMA foreign_keys = ON")
        except sqlite3.Error as e:
            raise Exception(f"Ошибка подключения к базе данных: {e}")

    def close(self) -> None:
        if self.connection:
            self.connection.close()
            self.connection = None

    def create_tables(self) -> None:
        try:
            cursor = self.connection.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL UNIQUE,
                    role TEXT NOT NULL CHECK(role IN ('admin', 'manager', 'developer')),
                    registration_date TEXT NOT NULL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('active', 'completed', 'on_hold'))
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    priority INTEGER NOT NULL CHECK(priority IN (1, 2, 3)),
                    status TEXT NOT NULL CHECK(status IN ('pending', 'in_progress', 'completed')),
                    due_date TEXT NOT NULL,
                    project_id INTEGER NOT NULL,
                    assignee_id INTEGER NOT NULL,
                    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
                    FOREIGN KEY (assignee_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')
            
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON tasks(project_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_assignee_id ON tasks(assignee_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority)')
            
            self.connection.commit()
        except sqlite3.Error as e:
            raise Exception(f"Ошибка создания таблиц: {e}")

    def add_task(self, task: Task) -> int:

        try:
            cursor = self.connection.cursor()
            
            cursor.execute("SELECT id FROM projects WHERE id = ?", (task.project_id,))
            if not cursor.fetchone():
                raise ValueError(f"Проект с ID {task.project_id} не найден")
            
            cursor.execute("SELECT id FROM users WHERE id = ?", (task.assignee_id,))
            if not cursor.fetchone():
                raise ValueError(f"Пользователь с ID {task.assignee_id} не найден")
            
            query = '''
                INSERT INTO tasks (title, description, priority, status, due_date, project_id, assignee_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            '''
            params = (
                task.title,
                task.description,
                task.priority,
                task.status,
                task.due_date.isoformat(),
                task.project_id,
                task.assignee_id
            )
            
            cursor.execute(query, params)
            self.connection.commit()
            
            task_id = cursor.lastrowid
            task.id = task_id
            return task_id
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Ошибка целостности данных: {e}")
        except sqlite3.Error as e:
            raise Exception(f"Ошибка базы данных: {e}")

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        try:
            cursor = self.connection.cursor()
            query = "SELECT * FROM tasks WHERE id = ?"
            cursor.execute(query, (task_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_task(dict(row))
            return None
        except sqlite3.Error as e:
            raise Exception(f"Ошибка базы данных: {e}")

    def get_all_tasks(self) -> List[Task]:
        try:
            cursor = self.connection.cursor()
            query = "SELECT * FROM tasks ORDER BY due_date ASC"
            cursor.execute(query)
            rows = cursor.fetchall()
            
            return [self._row_to_task(dict(row)) for row in rows]
        except sqlite3.Error as e:
            raise Exception(f"Ошибка базы данных: {e}")

    def update_task(self, task_id: int, **kwargs) -> bool:
        try:
            if not kwargs:
                return False
                
            cursor = self.connection.cursor()
            
            cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
            if not cursor.fetchone():
                return False
            
            set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
            query = f"UPDATE tasks SET {set_clause} WHERE id = ?"
            
            params = list(kwargs.values())
            params.append(task_id)
            
            for i, value in enumerate(params[:-1]):
                if isinstance(value, datetime):
                    params[i] = value.isoformat()
            
            cursor.execute(query, tuple(params))
            self.connection.commit()
            
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Ошибка базы данных: {e}")

    def delete_task(self, task_id: int) -> bool:
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
            if not cursor.fetchone():
                return False
            
            query = "DELETE FROM tasks WHERE id = ?"
            cursor.execute(query, (task_id,))
            self.connection.commit()
            
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Ошибка базы данных: {e}")

    def search_tasks(self, query_str: str) -> List[Task]:
        try:
            cursor = self.connection.cursor()
            search_pattern = f"%{query_str}%"
            query = """
                SELECT * FROM tasks 
                WHERE title LIKE ? OR description LIKE ?
                ORDER BY due_date ASC
            """
            cursor.execute(query, (search_pattern, search_pattern))
            rows = cursor.fetchall()
            
            return [self._row_to_task(dict(row)) for row in rows]
        except sqlite3.Error as e:
            raise Exception(f"Ошибка базы данных: {e}")

    def get_tasks_by_project(self, project_id: int) -> List[Task]:
        try:
            cursor = self.connection.cursor()
            query = """
                SELECT * FROM tasks 
                WHERE project_id = ? 
                ORDER BY priority ASC, due_date ASC
            """
            cursor.execute(query, (project_id,))
            rows = cursor.fetchall()
            
            return [self._row_to_task(dict(row)) for row in rows]
        except sqlite3.Error as e:
            raise Exception(f"Ошибка базы данных: {e}")

    def get_tasks_by_user(self, user_id: int) -> List[Task]:
        try:
            cursor = self.connection.cursor()
            query = """
                SELECT * FROM tasks 
                WHERE assignee_id = ? 
                ORDER BY due_date ASC, priority ASC
            """
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()
            
            return [self._row_to_task(dict(row)) for row in rows]
        except sqlite3.Error as e:
            raise Exception(f"Ошибка базы данных: {e}")

    def add_project(self, project: Project) -> int:
        try:
            cursor = self.connection.cursor()
            query = '''
                INSERT INTO projects (name, description, start_date, end_date, status)
                VALUES (?, ?, ?, ?, ?)
            '''
            params = (
                project.name,
                project.description,
                project.start_date.isoformat(),
                project.end_date.isoformat(),
                project.status
            )
            
            cursor.execute(query, params)
            self.connection.commit()
            
            project_id = cursor.lastrowid
            project.id = project_id
            return project_id
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Ошибка целостности данных: {e}")
        except sqlite3.Error as e:
            raise Exception(f"Ошибка базы данных: {e}")

    def get_project_by_id(self, project_id: int) -> Optional[Project]:
        try:
            cursor = self.connection.cursor()
            query = "SELECT * FROM projects WHERE id = ?"
            cursor.execute(query, (project_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_project(dict(row))
            return None
        except sqlite3.Error as e:
            raise Exception(f"Ошибка базы данных: {e}")

    def get_all_projects(self) -> List[Project]:
        try:
            cursor = self.connection.cursor()
            query = "SELECT * FROM projects ORDER BY start_date DESC"
            cursor.execute(query)
            rows = cursor.fetchall()
            
            return [self._row_to_project(dict(row)) for row in rows]
        except sqlite3.Error as e:
            raise Exception(f"Ошибка базы данных: {e}")

    def update_project(self, project_id: int, **kwargs) -> bool:
        try:
            if not kwargs:
                return False
                
            cursor = self.connection.cursor()
            
            cursor.execute("SELECT id FROM projects WHERE id = ?", (project_id,))
            if not cursor.fetchone():
                return False
            
            set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
            query = f"UPDATE projects SET {set_clause} WHERE id = ?"
            
            params = list(kwargs.values())
            params.append(project_id)
            
            for i, value in enumerate(params[:-1]):
                if isinstance(value, datetime):
                    params[i] = value.isoformat()
            
            cursor.execute(query, tuple(params))
            self.connection.commit()
            
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Ошибка базы данных: {e}")

    def delete_project(self, project_id: int) -> bool:
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("SELECT id FROM projects WHERE id = ?", (project_id,))
            if not cursor.fetchone():
                return False
            
            query = "DELETE FROM projects WHERE id = ?"
            cursor.execute(query, (project_id,))
            self.connection.commit()
            
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Ошибка базы данных: {e}")

    def add_user(self, user: User) -> int:
        try:
            cursor = self.connection.cursor()
            query = '''
                INSERT INTO users (username, email, role, registration_date)
                VALUES (?, ?, ?, ?)
            '''
            params = (
                user.username,
                user.email,
                user.role,
                user.registration_date.isoformat()
            )
            
            cursor.execute(query, params)
            self.connection.commit()
            
            user_id = cursor.lastrowid
            user.id = user_id
            return user_id
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Ошибка целостности данных: {e}")
        except sqlite3.Error as e:
            raise Exception(f"Ошибка базы данных: {e}")

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        try:
            cursor = self.connection.cursor()
            query = "SELECT * FROM users WHERE id = ?"
            cursor.execute(query, (user_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_user(dict(row))
            return None
        except sqlite3.Error as e:
            raise Exception(f"Ошибка базы данных: {e}")

    def get_all_users(self) -> List[User]:
        try:
            cursor = self.connection.cursor()
            query = "SELECT * FROM users ORDER BY username ASC"
            cursor.execute(query)
            rows = cursor.fetchall()
            
            return [self._row_to_user(dict(row)) for row in rows]
        except sqlite3.Error as e:
            raise Exception(f"Ошибка базы данных: {e}")

    def update_user(self, user_id: int, **kwargs) -> bool:
        try:
            if not kwargs:
                return False
                
            cursor = self.connection.cursor()
            
            cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
            if not cursor.fetchone():
                return False
            
            set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
            query = f"UPDATE users SET {set_clause} WHERE id = ?"
            
            params = list(kwargs.values())
            params.append(user_id)
            
            for i, value in enumerate(params[:-1]):
                if isinstance(value, datetime):
                    params[i] = value.isoformat()
            
            cursor.execute(query, tuple(params))
            self.connection.commit()
            
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Ошибка базы данных: {e}")

    def delete_user(self, user_id: int) -> bool:
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
            if not cursor.fetchone():
                return False
            
            query = "DELETE FROM users WHERE id = ?"
            cursor.execute(query, (user_id,))
            self.connection.commit()
            
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Ошибка базы данных: {e}")