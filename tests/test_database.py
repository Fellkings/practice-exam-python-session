import tempfile
import os
import pytest
from datetime import datetime, timedelta
from database.database_manager import DatabaseManager
from models.task import Task
from models.project import Project
from models.user import User


class TestDatabaseManager:
    
    def setup_method(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db = DatabaseManager(self.temp_db.name)

    def teardown_method(self):
        self.db.close()
        os.unlink(self.temp_db.name)

    def test_create_tables(self):
        cursor = self.db.connection.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        assert cursor.fetchone() is not None
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='projects'")
        assert cursor.fetchone() is not None
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
        assert cursor.fetchone() is not None

    def test_add_user(self):
        user = User(
            username="testuser",
            email="test@example.com",
            role="developer"
        )
        
        user_id = self.db.add_user(user)
        
        assert user_id is not None
        assert user.id == user_id
        
        cursor = self.db.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        
        assert result is not None
        assert result['username'] == "testuser"
        assert result['email'] == "test@example.com"
        assert result['role'] == "developer"

    def test_add_user_duplicate_username(self):
        user1 = User(
            username="testuser",
            email="test1@example.com",
            role="developer"
        )
        
        self.db.add_user(user1)
        
        user2 = User(
            username="testuser",
            email="test2@example.com",
            role="manager"
        )
        
        with pytest.raises(ValueError):
            self.db.add_user(user2)

    def test_add_user_duplicate_email(self):
        user1 = User(
            username="user1",
            email="test@example.com",
            role="developer"
        )
        
        self.db.add_user(user1)
        
        user2 = User(
            username="user2",
            email="test@example.com",
            role="manager"
        )
        
        with pytest.raises(ValueError):
            self.db.add_user(user2)

    def test_get_user_by_id(self):
        user = User(
            username="testuser",
            email="test@example.com",
            role="developer"
        )
        
        user_id = self.db.add_user(user)
        
        retrieved_user = self.db.get_user_by_id(user_id)
        
        assert retrieved_user is not None
        assert retrieved_user.id == user_id
        assert retrieved_user.username == "testuser"
        assert retrieved_user.email == "test@example.com"
        assert retrieved_user.role == "developer"

    def test_get_user_by_id_nonexistent(self):
        user = self.db.get_user_by_id(99999)
        assert user is None

    def test_get_all_users(self):
        user1 = User(
            username="user1",
            email="user1@example.com",
            role="developer"
        )
        
        user2 = User(
            username="user2",
            email="user2@example.com",
            role="manager"
        )
        
        self.db.add_user(user1)
        self.db.add_user(user2)
        
        users = self.db.get_all_users()
        
        assert isinstance(users, list)
        assert len(users) >= 2
        
        usernames = [user.username for user in users]
        assert "user1" in usernames
        assert "user2" in usernames

    def test_update_user(self):
        user = User(
            username="originaluser",
            email="original@example.com",
            role="developer"
        )
        
        user_id = self.db.add_user(user)
        
        result = self.db.update_user(
            user_id,
            username="updateduser",
            email="updated@example.com",
            role="admin"
        )
        
        assert result == True
        
        updated_user = self.db.get_user_by_id(user_id)
        assert updated_user.username == "updateduser"
        assert updated_user.email == "updated@example.com"
        assert updated_user.role == "admin"

    def test_update_user_nonexistent(self):
        result = self.db.update_user(99999, username="newuser")
        assert result == False

    def test_delete_user(self):
        user = User(
            username="testuser",
            email="test@example.com",
            role="developer"
        )
        
        user_id = self.db.add_user(user)
        
        result = self.db.delete_user(user_id)
        assert result == True
        
        deleted_user = self.db.get_user_by_id(user_id)
        assert deleted_user is None

    def test_delete_user_nonexistent(self):
        result = self.db.delete_user(99999)
        assert result == False

    def test_add_project(self):
        project = Project(
            name="Test Project",
            description="Test Description",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30)
        )
        
        project_id = self.db.add_project(project)
        
        assert project_id is not None
        assert project.id == project_id
        
        cursor = self.db.connection.cursor()
        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        result = cursor.fetchone()
        
        assert result is not None
        assert result['name'] == "Test Project"
        assert result['description'] == "Test Description"
        assert result['status'] == "active"

    def test_get_project_by_id(self):
        project = Project(
            name="Test Project",
            description="Test Description",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30)
        )
        
        project_id = self.db.add_project(project)
        
        retrieved_project = self.db.get_project_by_id(project_id)
        
        assert retrieved_project is not None
        assert retrieved_project.id == project_id
        assert retrieved_project.name == "Test Project"
        assert retrieved_project.description == "Test Description"
        assert retrieved_project.status == "active"

    def test_get_all_projects(self):
        project1 = Project(
            name="Project 1",
            description="Description 1",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30)
        )
        
        project2 = Project(
            name="Project 2",
            description="Description 2",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=60)
        )
        
        self.db.add_project(project1)
        self.db.add_project(project2)
        
        projects = self.db.get_all_projects()
        
        assert isinstance(projects, list)
        assert len(projects) >= 2
        
        project_names = [project.name for project in projects]
        assert "Project 1" in project_names
        assert "Project 2" in project_names

    def test_update_project(self):
        project = Project(
            name="Original Project",
            description="Original Description",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30)
        )
        
        project_id = self.db.add_project(project)
        
        new_end_date = datetime.now() + timedelta(days=45)
        result = self.db.update_project(
            project_id,
            name="Updated Project",
            description="Updated Description",
            end_date=new_end_date,
            status="completed"
        )
        
        assert result == True
        
        updated_project = self.db.get_project_by_id(project_id)
        assert updated_project.name == "Updated Project"
        assert updated_project.description == "Updated Description"
        assert updated_project.end_date.date() == new_end_date.date()
        assert updated_project.status == "completed"

    def test_delete_project(self):
        project = Project(
            name="Test Project",
            description="Test Description",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30)
        )
        
        project_id = self.db.add_project(project)
        
        result = self.db.delete_project(project_id)
        assert result == True
        
        deleted_project = self.db.get_project_by_id(project_id)
        assert deleted_project is None

    def test_add_task(self):
        user = User(
            username="testuser",
            email="test@example.com",
            role="developer"
        )
        user_id = self.db.add_user(user)
        
        project = Project(
            name="Test Project",
            description="Test Description",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30)
        )
        project_id = self.db.add_project(project)
        
        task = Task(
            title="Test Task",
            description="Test Description",
            priority=2,
            due_date=datetime.now() + timedelta(days=7),
            project_id=project_id,
            assignee_id=user_id
        )
        
        task_id = self.db.add_task(task)
        
        assert task_id is not None
        assert task.id == task_id
        
        cursor = self.db.connection.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        result = cursor.fetchone()
        
        assert result is not None
        assert result['title'] == "Test Task"
        assert result['description'] == "Test Description"
        assert result['priority'] == 2
        assert result['status'] == "pending"
        assert result['project_id'] == project_id
        assert result['assignee_id'] == user_id

    def test_add_task_invalid_project(self):
        user = User(
            username="testuser",
            email="test@example.com",
            role="developer"
        )
        user_id = self.db.add_user(user)
        
        task = Task(
            title="Test Task",
            description="Test Description",
            priority=2,
            due_date=datetime.now() + timedelta(days=7),
            project_id=99999,
            assignee_id=user_id
        )
        
        with pytest.raises(ValueError):
            self.db.add_task(task)

    def test_add_task_invalid_user(self):
        project = Project(
            name="Test Project",
            description="Test Description",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30)
        )
        project_id = self.db.add_project(project)
        
        task = Task(
            title="Test Task",
            description="Test Description",
            priority=2,
            due_date=datetime.now() + timedelta(days=7),
            project_id=project_id,
            assignee_id=99999
        )
        
        with pytest.raises(ValueError):
            self.db.add_task(task)

    def test_get_task_by_id(self):
        user = User(
            username="testuser",
            email="test@example.com",
            role="developer"
        )
        user_id = self.db.add_user(user)
        
        project = Project(
            name="Test Project",
            description="Test Description",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30)
        )
        project_id = self.db.add_project(project)
        
        task = Task(
            title="Test Task",
            description="Test Description",
            priority=2,
            due_date=datetime.now() + timedelta(days=7),
            project_id=project_id,
            assignee_id=user_id
        )
        task_id = self.db.add_task(task)
        
        retrieved_task = self.db.get_task_by_id(task_id)
        
        assert retrieved_task is not None
        assert retrieved_task.id == task_id
        assert retrieved_task.title == "Test Task"
        assert retrieved_task.description == "Test Description"
        assert retrieved_task.priority == 2
        assert retrieved_task.status == "pending"
        assert retrieved_task.project_id == project_id
        assert retrieved_task.assignee_id == user_id

    def test_get_all_tasks(self):
        user = User(
            username="testuser",
            email="test@example.com",
            role="developer"
        )
        user_id = self.db.add_user(user)
        
        project = Project(
            name="Test Project",
            description="Test Description",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30)
        )
        project_id = self.db.add_project(project)
        
        task1 = Task(
            title="Task 1",
            description="Description 1",
            priority=1,
            due_date=datetime.now() + timedelta(days=1),
            project_id=project_id,
            assignee_id=user_id
        )
        
        task2 = Task(
            title="Task 2",
            description="Description 2",
            priority=2,
            due_date=datetime.now() + timedelta(days=2),
            project_id=project_id,
            assignee_id=user_id
        )
        
        self.db.add_task(task1)
        self.db.add_task(task2)
        
        tasks = self.db.get_all_tasks()
        
        assert isinstance(tasks, list)
        assert len(tasks) >= 2
        
        task_titles = [task.title for task in tasks]
        assert "Task 1" in task_titles
        assert "Task 2" in task_titles

    def test_update_task(self):
        user = User(
            username="testuser",
            email="test@example.com",
            role="developer"
        )
        user_id = self.db.add_user(user)
        
        project = Project(
            name="Test Project",
            description="Test Description",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30)
        )
        project_id = self.db.add_project(project)
        
        task = Task(
            title="Original Task",
            description="Original Description",
            priority=2,
            due_date=datetime.now() + timedelta(days=7),
            project_id=project_id,
            assignee_id=user_id
        )
        task_id = self.db.add_task(task)
        
        new_due_date = datetime.now() + timedelta(days=14)
        result = self.db.update_task(
            task_id,
            title="Updated Task",
            description="Updated Description",
            priority=1,
            due_date=new_due_date,
            status="in_progress"
        )
        
        assert result == True
        
        updated_task = self.db.get_task_by_id(task_id)
        assert updated_task.title == "Updated Task"
        assert updated_task.description == "Updated Description"
        assert updated_task.priority == 1
        assert updated_task.status == "in_progress"
        assert updated_task.due_date.date() == new_due_date.date()

    def test_delete_task(self):
        user = User(
            username="testuser",
            email="test@example.com",
            role="developer"
        )
        user_id = self.db.add_user(user)
        
        project = Project(
            name="Test Project",
            description="Test Description",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30)
        )
        project_id = self.db.add_project(project)
        
        task = Task(
            title="Test Task",
            description="Test Description",
            priority=2,
            due_date=datetime.now() + timedelta(days=7),
            project_id=project_id,
            assignee_id=user_id
        )
        task_id = self.db.add_task(task)
        
        result = self.db.delete_task(task_id)
        assert result == True
        
        deleted_task = self.db.get_task_by_id(task_id)
        assert deleted_task is None

    def test_search_tasks(self):
        user = User(
            username="testuser",
            email="test@example.com",
            role="developer"
        )
        user_id = self.db.add_user(user)
        
        project = Project(
            name="Test Project",
            description="Test Description",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30)
        )
        project_id = self.db.add_project(project)
        
        task1 = Task(
            title="Important Meeting",
            description="Discuss project requirements",
            priority=1,
            due_date=datetime.now() + timedelta(days=1),
            project_id=project_id,
            assignee_id=user_id
        )
        
        task2 = Task(
            title="Code Review",
            description="Review important changes",
            priority=2,
            due_date=datetime.now() + timedelta(days=2),
            project_id=project_id,
            assignee_id=user_id
        )
        
        self.db.add_task(task1)
        self.db.add_task(task2)
        
        important_tasks = self.db.search_tasks("Important")
        assert len(important_tasks) >= 1
        
        review_tasks = self.db.search_tasks("review")
        assert len(review_tasks) >= 1

    def test_get_tasks_by_project(self):
        user = User(
            username="testuser",
            email="test@example.com",
            role="developer"
        )
        user_id = self.db.add_user(user)
        
        project1 = Project(
            name="Project 1",
            description="Description 1",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30)
        )
        project1_id = self.db.add_project(project1)
        
        project2 = Project(
            name="Project 2",
            description="Description 2",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=60)
        )
        project2_id = self.db.add_project(project2)
        
        task1 = Task(
            title="Task for Project 1",
            description="Task 1",
            priority=1,
            due_date=datetime.now() + timedelta(days=1),
            project_id=project1_id,
            assignee_id=user_id
        )
        
        task2 = Task(
            title="Task for Project 2",
            description="Task 2",
            priority=2,
            due_date=datetime.now() + timedelta(days=2),
            project_id=project2_id,
            assignee_id=user_id
        )
        
        self.db.add_task(task1)
        self.db.add_task(task2)
        
        project1_tasks = self.db.get_tasks_by_project(project1_id)
        assert len(project1_tasks) >= 1
        assert all(task.project_id == project1_id for task in project1_tasks)
        
        project2_tasks = self.db.get_tasks_by_project(project2_id)
        assert len(project2_tasks) >= 1
        assert all(task.project_id == project2_id for task in project2_tasks)

    def test_get_tasks_by_user(self):
        user1 = User(
            username="user1",
            email="user1@example.com",
            role="developer"
        )
        user1_id = self.db.add_user(user1)
        
        user2 = User(
            username="user2",
            email="user2@example.com",
            role="manager"
        )
        user2_id = self.db.add_user(user2)
        
        project = Project(
            name="Test Project",
            description="Test Description",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30)
        )
        project_id = self.db.add_project(project)
        
        task1 = Task(
            title="Task for User 1",
            description="Task 1",
            priority=1,
            due_date=datetime.now() + timedelta(days=1),
            project_id=project_id,
            assignee_id=user1_id
        )
        
        task2 = Task(
            title="Task for User 2",
            description="Task 2",
            priority=2,
            due_date=datetime.now() + timedelta(days=2),
            project_id=project_id,
            assignee_id=user2_id
        )
        
        self.db.add_task(task1)
        self.db.add_task(task2)
        
        user1_tasks = self.db.get_tasks_by_user(user1_id)
        assert len(user1_tasks) >= 1
        assert all(task.assignee_id == user1_id for task in user1_tasks)
        
        user2_tasks = self.db.get_tasks_by_user(user2_id)
        assert len(user2_tasks) >= 1
        assert all(task.assignee_id == user2_id for task in user2_tasks)

    def test_foreign_key_cascade(self):
        user = User(
            username="testuser",
            email="test@example.com",
            role="developer"
        )
        user_id = self.db.add_user(user)
        
        project = Project(
            name="Test Project",
            description="Test Description",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30)
        )
        project_id = self.db.add_project(project)
        
        task = Task(
            title="Test Task",
            description="Test Description",
            priority=2,
            due_date=datetime.now() + timedelta(days=7),
            project_id=project_id,
            assignee_id=user_id
        )
        task_id = self.db.add_task(task)
        
        self.db.delete_project(project_id)
        
        deleted_task = self.db.get_task_by_id(task_id)
        assert deleted_task is None
        
        existing_user = self.db.get_user_by_id(user_id)
        assert existing_user is not None

    def test_foreign_key_cascade_user(self):
        user = User(
            username="testuser",
            email="test@example.com",
            role="developer"
        )
        user_id = self.db.add_user(user)
        
        project = Project(
            name="Test Project",
            description="Test Description",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30)
        )
        project_id = self.db.add_project(project)
        
        task = Task(
            title="Test Task",
            description="Test Description",
            priority=2,
            due_date=datetime.now() + timedelta(days=7),
            project_id=project_id,
            assignee_id=user_id
        )
        task_id = self.db.add_task(task)
        
        self.db.delete_user(user_id)
        
        deleted_task = self.db.get_task_by_id(task_id)
        assert deleted_task is None
        
        existing_project = self.db.get_project_by_id(project_id)
        assert existing_project is not None

    def test_close_and_reopen(self):
        user = User(
            username="testuser",
            email="test@example.com",
            role="developer"
        )
        user_id = self.db.add_user(user)
        
        self.db.close()
        
        new_db = DatabaseManager(self.temp_db.name)
        
        retrieved_user = new_db.get_user_by_id(user_id)
        assert retrieved_user is not None
        assert retrieved_user.username == "testuser"
        
        new_db.close()

    def test_execute_query_error(self):
        with pytest.raises(Exception):
            self.db.execute_query("INVALID SQL QUERY")

    def test_fetch_one(self):
        user = User(
            username="testuser",
            email="test@example.com",
            role="developer"
        )
        user_id = self.db.add_user(user)
        
        result = self.db.fetch_one("SELECT * FROM users WHERE id = ?", (user_id,))
        assert result is not None
        assert result['username'] == "testuser"
        
        result = self.db.fetch_one("SELECT * FROM users WHERE id = ?", (99999,))
        assert result is None

    def test_fetch_all(self):
        user1 = User(
            username="user1",
            email="user1@example.com",
            role="developer"
        )
        
        user2 = User(
            username="user2",
            email="user2@example.com",
            role="manager"
        )
        
        self.db.add_user(user1)
        self.db.add_user(user2)
        
        results = self.db.fetch_all("SELECT * FROM users ORDER BY username")
        assert isinstance(results, list)
        assert len(results) >= 2
        
        usernames = [row['username'] for row in results]
        assert "user1" in usernames
        assert "user2" in usernames