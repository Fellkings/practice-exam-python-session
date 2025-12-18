import pytest
from datetime import datetime, timedelta
from models.task import Task
from models.project import Project
from models.user import User


class TestTaskModel:
    
    def test_task_creation(self):
        due_date = datetime.now() + timedelta(days=7)
        task = Task(
            title="Test Task",
            description="Test Description",
            priority=2,
            due_date=due_date,
            project_id=1,
            assignee_id=1
        )
        
        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.priority == 2
        assert task.status == "pending"
        assert task.due_date == due_date
        assert task.project_id == 1
        assert task.assignee_id == 1
        assert task.id is None
    
    def test_task_creation_with_custom_status(self):
        due_date = datetime.now() + timedelta(days=7)
        task = Task(
            title="Test Task",
            description="Test Description",
            priority=2,
            due_date=due_date,
            project_id=1,
            assignee_id=1,
            status="in_progress"
        )
        
        assert task.status == "in_progress"
    
    def test_task_creation_with_id(self):
        due_date = datetime.now() + timedelta(days=7)
        task = Task(
            title="Test Task",
            description="Test Description",
            priority=2,
            due_date=due_date,
            project_id=1,
            assignee_id=1,
            id=10
        )
        
        assert task.id == 10
    
    def test_task_invalid_priority(self):
        due_date = datetime.now() + timedelta(days=7)
        
        with pytest.raises(ValueError, match="Приоритет должен быть 1"):
            Task(
                title="Test Task",
                description="Test Description",
                priority=5,
                due_date=due_date,
                project_id=1,
                assignee_id=1
            )
    
    def test_task_invalid_status(self):
        due_date = datetime.now() + timedelta(days=7)
        
        with pytest.raises(ValueError, match="Статус должен быть одним из"):
            Task(
                title="Test Task",
                description="Test Description",
                priority=2,
                due_date=due_date,
                project_id=1,
                assignee_id=1,
                status="invalid_status"
            )
    
    def test_update_status_valid(self):
        task = Task(
            title="Test Task",
            description="Test Description",
            priority=2,
            due_date=datetime.now() + timedelta(days=7),
            project_id=1,
            assignee_id=1
        )
        
        task.update_status("in_progress")
        assert task.status == "in_progress"
        
        task.update_status("completed")
        assert task.status == "completed"
    
    def test_update_status_invalid(self):
        task = Task(
            title="Test Task",
            description="Test Description",
            priority=2,
            due_date=datetime.now() + timedelta(days=7),
            project_id=1,
            assignee_id=1
        )
        
        with pytest.raises(ValueError, match="Статус должен быть одним из"):
            task.update_status("invalid_status")
    
    def test_is_overdue_not_overdue(self):
        future_date = datetime.now() + timedelta(days=1)
        task = Task(
            title="Test Task",
            description="Test Description",
            priority=2,
            due_date=future_date,
            project_id=1,
            assignee_id=1
        )
        
        assert task.is_overdue() == False
    
    def test_is_overdue_overdue(self):
        past_date = datetime.now() - timedelta(days=1)
        task = Task(
            title="Test Task",
            description="Test Description",
            priority=2,
            due_date=past_date,
            project_id=1,
            assignee_id=1
        )
        
        assert task.is_overdue() == True
    
    def test_is_overdue_completed(self):
        past_date = datetime.now() - timedelta(days=1)
        task = Task(
            title="Test Task",
            description="Test Description",
            priority=2,
            due_date=past_date,
            project_id=1,
            assignee_id=1,
            status="completed"
        )
        
        assert task.is_overdue() == False
    
    def test_to_dict(self):
        due_date = datetime.now() + timedelta(days=7)
        task = Task(
            title="Test Task",
            description="Test Description",
            priority=2,
            due_date=due_date,
            project_id=1,
            assignee_id=1,
            id=5,
            status="in_progress"
        )
        
        task_dict = task.to_dict()
        
        assert task_dict["id"] == 5
        assert task_dict["title"] == "Test Task"
        assert task_dict["description"] == "Test Description"
        assert task_dict["priority"] == 2
        assert task_dict["status"] == "in_progress"
        assert task_dict["due_date"] == due_date.isoformat()
        assert task_dict["project_id"] == 1
        assert task_dict["assignee_id"] == 1


class TestProjectModel:
    
    def test_project_creation(self):
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)
        project = Project(
            name="Test Project",
            description="Test Description",
            start_date=start_date,
            end_date=end_date
        )
        
        assert project.name == "Test Project"
        assert project.description == "Test Description"
        assert project.start_date == start_date
        assert project.end_date == end_date
        assert project.status == "active"
        assert project.id is None
    
    def test_project_creation_with_custom_status(self):
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)
        project = Project(
            name="Test Project",
            description="Test Description",
            start_date=start_date,
            end_date=end_date,
            status="completed"
        )
        
        assert project.status == "completed"
    
    def test_project_creation_with_id(self):
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)
        project = Project(
            name="Test Project",
            description="Test Description",
            start_date=start_date,
            end_date=end_date,
            id=15
        )
        
        assert project.id == 15
    
    def test_project_invalid_dates(self):
        start_date = datetime.now()
        end_date = start_date - timedelta(days=1)
        
        with pytest.raises(ValueError, match="Дата начала не может быть позже даты окончания"):
            Project(
                name="Test Project",
                description="Test Description",
                start_date=start_date,
                end_date=end_date
            )
    
    def test_project_invalid_status(self):
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)
        
        with pytest.raises(ValueError, match="Статус должен быть одним из"):
            Project(
                name="Test Project",
                description="Test Description",
                start_date=start_date,
                end_date=end_date,
                status="invalid_status"
            )
    
    def test_update_status_valid(self):
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)
        project = Project(
            name="Test Project",
            description="Test Description",
            start_date=start_date,
            end_date=end_date
        )
        
        project.update_status("on_hold")
        assert project.status == "on_hold"
        
        project.update_status("completed")
        assert project.status == "completed"
    
    def test_update_status_invalid(self):
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)
        project = Project(
            name="Test Project",
            description="Test Description",
            start_date=start_date,
            end_date=end_date
        )
        
        with pytest.raises(ValueError, match="Статус должен быть одним из"):
            project.update_status("invalid_status")
    
    def test_get_progress_active(self):
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)
        project = Project(
            name="Test Project",
            description="Test Description",
            start_date=start_date,
            end_date=end_date,
            status="active"
        )
        
        progress = project.get_progress()
        assert isinstance(progress, float)
        assert 0 <= progress <= 100
    
    def test_get_progress_completed(self):
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)
        project = Project(
            name="Test Project",
            description="Test Description",
            start_date=start_date,
            end_date=end_date,
            status="completed"
        )
        
        progress = project.get_progress()
        assert progress == 100.0
    
    def test_get_progress_on_hold(self):
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)
        project = Project(
            name="Test Project",
            description="Test Description",
            start_date=start_date,
            end_date=end_date,
            status="on_hold"
        )
        
        progress = project.get_progress()
        assert progress == 0.0
    
    def test_to_dict(self):
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)
        project = Project(
            name="Test Project",
            description="Test Description",
            start_date=start_date,
            end_date=end_date,
            id=8,
            status="active"
        )
        
        project_dict = project.to_dict()
        
        assert project_dict["id"] == 8
        assert project_dict["name"] == "Test Project"
        assert project_dict["description"] == "Test Description"
        assert project_dict["start_date"] == start_date.isoformat()
        assert project_dict["end_date"] == end_date.isoformat()
        assert project_dict["status"] == "active"
        assert "progress" in project_dict
        assert isinstance(project_dict["progress"], float)


class TestUserModel:
    
    def test_user_creation(self):
        user = User(
            username="testuser",
            email="test@example.com",
            role="developer"
        )
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == "developer"
        assert user.id is None
        assert user.registration_date is not None
        assert isinstance(user.registration_date, datetime)
    
    def test_user_creation_with_custom_registration_date(self):
        reg_date = datetime.now() - timedelta(days=30)
        user = User(
            username="testuser",
            email="test@example.com",
            role="developer",
            registration_date=reg_date
        )
        
        assert user.registration_date == reg_date
    
    def test_user_creation_with_id(self):
        user = User(
            username="testuser",
            email="test@example.com",
            role="developer",
            id=20
        )
        
        assert user.id == 20
    
    def test_user_invalid_email(self):
        with pytest.raises(ValueError, match="Некорректный email адрес"):
            User(
                username="testuser",
                email="invalid-email",
                role="developer"
            )
    
    def test_user_invalid_role(self):
        with pytest.raises(ValueError, match="Роль должна быть одной из"):
            User(
                username="testuser",
                email="test@example.com",
                role="invalid_role"
            )
    
    def test_is_valid_email_valid(self):
        user = User("test", "test@example.com", "developer")
        
        assert user._is_valid_email("user@example.com") == True
        assert user._is_valid_email("user.name@example.co.uk") == True
        assert user._is_valid_email("user+tag@example.org") == True
    
    def test_is_valid_email_invalid(self):
        user = User("test", "test@example.com", "developer")
        
        assert user._is_valid_email("invalid-email") == False
        assert user._is_valid_email("user@") == False
        assert user._is_valid_email("@example.com") == False
        assert user._is_valid_email("user@example") == False
    
    def test_update_info_valid(self):
        user = User(
            username="testuser",
            email="test@example.com",
            role="developer"
        )
        
        user.update_info(username="newuser", email="new@example.com", role="manager")
        
        assert user.username == "newuser"
        assert user.email == "new@example.com"
        assert user.role == "manager"
    
    def test_update_info_partial(self):
        user = User(
            username="testuser",
            email="test@example.com",
            role="developer"
        )
        
        user.update_info(username="newuser")
        assert user.username == "newuser"
        assert user.email == "test@example.com"
        assert user.role == "developer"
    
    def test_update_info_invalid_email(self):
        user = User(
            username="testuser",
            email="test@example.com",
            role="developer"
        )
        
        with pytest.raises(ValueError, match="Некорректный email адрес"):
            user.update_info(email="invalid-email")
    
    def test_update_info_invalid_role(self):
        user = User(
            username="testuser",
            email="test@example.com",
            role="developer"
        )
        
        with pytest.raises(ValueError, match="Роль должна быть одной из"):
            user.update_info(role="invalid_role")
    
    def test_to_dict(self):
        reg_date = datetime.now()
        user = User(
            username="testuser",
            email="test@example.com",
            role="developer",
            id=12,
            registration_date=reg_date
        )
        
        user_dict = user.to_dict()
        
        assert user_dict["id"] == 12
        assert user_dict["username"] == "testuser"
        assert user_dict["email"] == "test@example.com"
        assert user_dict["role"] == "developer"
        assert user_dict["registration_date"] == reg_date.isoformat()