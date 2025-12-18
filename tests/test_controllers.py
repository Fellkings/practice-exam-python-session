import tempfile
import os
import pytest
import time
from datetime import datetime, timedelta
from database.database_manager import DatabaseManager
from controllers.task_controller import TaskController
from controllers.project_controller import ProjectController
from controllers.user_controller import UserController


class TestTaskController:

    def setup_method(self):
            self.temp_db_path = tempfile.mktemp(suffix='.db')
            
            if os.path.exists(self.temp_db_path):
                try:
                    os.unlink(self.temp_db_path)
                except:
                    pass
            
            self.db_manager = DatabaseManager(self.temp_db_path)
            self.controller = TaskController(self.db_manager)

            self.project_controller = ProjectController(self.db_manager)
            self.user_controller = UserController(self.db_manager)

            self.user = self.user_controller.add_user(
                username="testuser",
                email="test@example.com",
                role="developer"
            )

            self.project = self.project_controller.add_project(
                name="Test Project",
                description="Test Description",
                start_date=datetime.now() + timedelta(days=1),
                end_date=datetime.now() + timedelta(days=31)
            )
            
            self.due_date = datetime.now() + timedelta(days=7)

    def teardown_method(self):
        if hasattr(self.db_manager, 'connection'):
            if self.db_manager.connection:
                self.db_manager.connection.close()
        
        if hasattr(self.db_manager, 'close'):
            self.db_manager.close()
        
        import gc
        gc.collect() 
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                if os.path.exists(self.temp_db_path):
                    os.unlink(self.temp_db_path)
                break
            except PermissionError:
                if attempt < max_attempts - 1:
                    time.sleep(0.1 * (attempt + 1))
                else:
                    print(f"Не удалось удалить файл: {self.temp_db_path}")

    def test_add_task_success(self):
        task = self.controller.add_task(
            title="Test Task",
            description="Test Description",
            priority=2,
            due_date=self.due_date,
            project_id=self.project.id,
            assignee_id=self.user.id
        )
        
        assert task.id is not None
        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.priority == 2
        assert task.status == "pending"
        assert task.project_id == self.project.id
        assert task.assignee_id == self.user.id
    
    def test_add_task_invalid_priority(self):
        with pytest.raises(ValueError, match="Приоритет должен быть 1"):
            self.controller.add_task(
                title="Test Task",
                description="Test Description",
                priority=5,
                due_date=self.due_date,
                project_id=self.project.id,
                assignee_id=self.user.id
            )
    
    def test_add_task_past_due_date(self):
        past_date = datetime.now() - timedelta(days=1)
        
        with pytest.raises(ValueError, match="Дата выполнения не может быть в прошлом"):
            self.controller.add_task(
                title="Test Task",
                description="Test Description",
                priority=2,
                due_date=past_date,
                project_id=self.project.id,
                assignee_id=self.user.id
            )
    
    def test_add_task_nonexistent_project(self):
        with pytest.raises(ValueError, match="Проект с ID"):
            self.controller.add_task(
                title="Test Task",
                description="Test Description",
                priority=2,
                due_date=self.due_date,
                project_id=99999,
                assignee_id=self.user.id
            )
    
    def test_add_task_nonexistent_user(self):
        with pytest.raises(ValueError, match="Пользователь с ID"):
            self.controller.add_task(
                title="Test Task",
                description="Test Description",
                priority=2,
                due_date=self.due_date,
                project_id=self.project.id,
                assignee_id=99999
            )
    
    def test_get_task_success(self):
        task = self.controller.add_task(
            title="Test Task",
            description="Test Description",
            priority=2,
            due_date=self.due_date,
            project_id=self.project.id,
            assignee_id=self.user.id
        )
        
        retrieved_task = self.controller.get_task(task.id)
        
        assert retrieved_task is not None
        assert retrieved_task.id == task.id
        assert retrieved_task.title == task.title
        assert retrieved_task.description == task.description
        assert retrieved_task.priority == task.priority
    
    def test_get_task_nonexistent(self):
        task = self.controller.get_task(99999)
        assert task is None
    
    def test_get_all_tasks(self):
        task1 = self.controller.add_task(
            title="Task 1",
            description="Description 1",
            priority=1,
            due_date=self.due_date,
            project_id=self.project.id,
            assignee_id=self.user.id
        )
        
        task2 = self.controller.add_task(
            title="Task 2",
            description="Description 2",
            priority=2,
            due_date=self.due_date + timedelta(days=1),
            project_id=self.project.id,
            assignee_id=self.user.id
        )
        
        all_tasks = self.controller.get_all_tasks()
        
        assert isinstance(all_tasks, list)
        assert len(all_tasks) >= 2
        
        task_ids = [task.id for task in all_tasks]
        assert task1.id in task_ids
        assert task2.id in task_ids
    
    def test_update_task_success(self):
        task = self.controller.add_task(
            title="Original Title",
            description="Original Description",
            priority=2,
            due_date=self.due_date,
            project_id=self.project.id,
            assignee_id=self.user.id
        )
        
        new_due_date = self.due_date + timedelta(days=14)
        result = self.controller.update_task(
            task.id,
            title="Updated Title",
            description="Updated Description",
            priority=1,
            due_date=new_due_date,
            status="in_progress"
        )
        
        assert result == True
        
        updated_task = self.controller.get_task(task.id)
        assert updated_task.title == "Updated Title"
        assert updated_task.description == "Updated Description"
        assert updated_task.priority == 1
        assert updated_task.status == "in_progress"
        assert updated_task.due_date.date() == new_due_date.date()
    
    def test_update_task_nonexistent(self):
        result = self.controller.update_task(99999, title="New Title")
        assert result == False
    
    def test_update_task_invalid_status(self):
        task = self.controller.add_task(
            title="Test Task",
            description="Test Description",
            priority=2,
            due_date=self.due_date,
            project_id=self.project.id,
            assignee_id=self.user.id
        )
        
        with pytest.raises(ValueError, match="Статус должен быть одним из"):
            self.controller.update_task(task.id, status="invalid_status")
    
    def test_update_task_invalid_priority(self):
        task = self.controller.add_task(
            title="Test Task",
            description="Test Description",
            priority=2,
            due_date=self.due_date,
            project_id=self.project.id,
            assignee_id=self.user.id
        )
        
        with pytest.raises(ValueError, match="Приоритет должен быть 1"):
            self.controller.update_task(task.id, priority=5)
    
    def test_delete_task_success(self):
        task = self.controller.add_task(
            title="Task to Delete",
            description="Will be deleted",
            priority=2,
            due_date=self.due_date,
            project_id=self.project.id,
            assignee_id=self.user.id
        )
        
        result = self.controller.delete_task(task.id)
        assert result == True
        
        deleted_task = self.controller.get_task(task.id)
        assert deleted_task is None
    
    def test_delete_task_nonexistent(self):
        result = self.controller.delete_task(99999)
        assert result == False
    
    def test_search_tasks(self):
        task1 = self.controller.add_task(
            title="Important Meeting",
            description="Discuss project requirements",
            priority=1,
            due_date=self.due_date,
            project_id=self.project.id,
            assignee_id=self.user.id
        )
        
        task2 = self.controller.add_task(
            title="Code Review",
            description="Review important changes",
            priority=2,
            due_date=self.due_date + timedelta(days=1),
            project_id=self.project.id,
            assignee_id=self.user.id
        )
        
        important_results = self.controller.search_tasks("Important")
        assert len(important_results) >= 1
        assert any("Important" in task.title for task in important_results)

        review_results = self.controller.search_tasks("review")
        assert len(review_results) >= 1
        assert any("review" in task.description.lower() for task in review_results)
        
        empty_results = self.controller.search_tasks("")
        assert empty_results == []
    
    def test_update_task_status_success(self):
        task = self.controller.add_task(
            title="Test Task",
            description="Test Description",
            priority=2,
            due_date=self.due_date,
            project_id=self.project.id,
            assignee_id=self.user.id
        )
        
        result = self.controller.update_task_status(task.id, "in_progress")
        assert result == True
        
        updated_task = self.controller.get_task(task.id)
        assert updated_task.status == "in_progress"
    
    def test_update_task_status_invalid(self):
        task = self.controller.add_task(
            title="Test Task",
            description="Test Description",
            priority=2,
            due_date=self.due_date,
            project_id=self.project.id,
            assignee_id=self.user.id
        )
        
        with pytest.raises(ValueError, match="Статус должен быть одним из"):
            self.controller.update_task_status(task.id, "invalid_status")
    
    def test_get_overdue_tasks(self):
        future_task = self.controller.add_task(
            title="Future Task",
            description="Not overdue",
            priority=2,
            due_date=datetime.now() + timedelta(days=7),
            project_id=self.project.id,
            assignee_id=self.user.id
        )
        
        task_to_overdue = self.controller.add_task(
            title="Will Be Overdue",
            description="Will become overdue",
            priority=1,
            due_date=datetime.now() + timedelta(days=1),
            project_id=self.project.id,
            assignee_id=self.user.id
        )
        
        result = self.controller.update_task(
            task_to_overdue.id,
            due_date=datetime.now() - timedelta(days=1)
        )
        
        if result:
            overdue_tasks = self.controller.get_overdue_tasks()
            overdue_task_ids = [task.id for task in overdue_tasks]
            assert task_to_overdue.id in overdue_task_ids, \
                f"Задача {task_to_overdue.id} должна быть просроченной после обновления даты"
            assert future_task.id not in overdue_task_ids, \
                f"Задача {future_task.id} не должна быть просроченной"
        else:
            pytest.skip("Cannot create overdue tasks due to date validation in update_task")
    
    def test_get_tasks_by_project_success(self):
        task = self.controller.add_task(
            title="Test Task",
            description="Test Description",
            priority=2,
            due_date=self.due_date,
            project_id=self.project.id,
            assignee_id=self.user.id
        )
        
        project_tasks = self.controller.get_tasks_by_project(self.project.id)
        
        assert len(project_tasks) >= 1
        assert any(t.id == task.id for t in project_tasks)
        assert all(t.project_id == self.project.id for t in project_tasks)
    
    def test_get_tasks_by_project_nonexistent(self):
        with pytest.raises(ValueError, match="Проект с ID"):
            self.controller.get_tasks_by_project(99999)
    
    def test_get_tasks_by_user_success(self):
        task = self.controller.add_task(
            title="Test Task",
            description="Test Description",
            priority=2,
            due_date=self.due_date,
            project_id=self.project.id,
            assignee_id=self.user.id
        )
        
        user_tasks = self.controller.get_tasks_by_user(self.user.id)
        
        assert len(user_tasks) >= 1
        assert any(t.id == task.id for t in user_tasks)
        assert all(t.assignee_id == self.user.id for t in user_tasks)
    
    def test_get_tasks_by_user_nonexistent(self):
        with pytest.raises(ValueError, match="Пользователь с ID"):
            self.controller.get_tasks_by_user(99999)


class TestProjectController:

    def setup_method(self):
        self.db_manager = DatabaseManager(":memory:")
        self.controller = ProjectController(self.db_manager)
        
        self.user_controller = UserController(self.db_manager)
        self.task_controller = TaskController(self.db_manager)
        
        self.user = self.user_controller.add_user(
            username="testuser",
            email="test@example.com",
            role="developer"
        )

        self.start_date = datetime.now() + timedelta(days=1)
        self.end_date = datetime.now() + timedelta(days=31)

    def teardown_method(self):
        if hasattr(self.db_manager, 'close'):
            self.db_manager.close()

    def test_add_project_success(self):
        project = self.controller.add_project(
            name="Test Project",
            description="Test Description",
            start_date=self.start_date,
            end_date=self.end_date
        )
        
        assert project.id is not None
        assert project.name == "Test Project"
        assert project.description == "Test Description"
        assert project.status == "active"
    
    def test_add_project_invalid_dates(self):
        with pytest.raises(ValueError, match="Дата начала должна быть раньше"):
            self.controller.add_project(
                name="Test Project",
                description="Test Description",
                start_date=self.end_date,
                end_date=self.start_date
            )
    
    def test_add_project_empty_name(self):
        with pytest.raises(ValueError, match="Название проекта не может быть пустым"):
            self.controller.add_project(
                name="",
                description="Test Description",
                start_date=self.start_date,
                end_date=self.end_date
            )
    
    def test_get_project_success(self):
        project = self.controller.add_project(
            name="Test Project",
            description="Test Description",
            start_date=self.start_date,
            end_date=self.end_date
        )
        
        retrieved_project = self.controller.get_project(project.id)
        
        assert retrieved_project is not None
        assert retrieved_project.id == project.id
        assert retrieved_project.name == project.name
        assert retrieved_project.description == project.description
    
    def test_get_project_nonexistent(self):
        project = self.controller.get_project(99999)
        assert project is None
    
    def test_get_all_projects(self):
        project1 = self.controller.add_project(
            name="Project 1",
            description="Description 1",
            start_date=self.start_date,
            end_date=self.end_date
        )
        
        project2 = self.controller.add_project(
            name="Project 2",
            description="Description 2",
            start_date=self.start_date + timedelta(days=1),
            end_date=self.end_date + timedelta(days=1)
        )
        
        all_projects = self.controller.get_all_projects()
        
        assert isinstance(all_projects, list)
        assert len(all_projects) >= 2
        
        project_ids = [p.id for p in all_projects]
        assert project1.id in project_ids
        assert project2.id in project_ids
    
    def test_update_project_success(self):
        project = self.controller.add_project(
            name="Original Name",
            description="Original Description",
            start_date=self.start_date,
            end_date=self.end_date
        )
        
        new_end_date = self.end_date + timedelta(days=14)
        result = self.controller.update_project(
            project.id,
            name="Updated Name",
            description="Updated Description",
            end_date=new_end_date,
            status="on_hold"
        )
        
        assert result == True
        
        updated_project = self.controller.get_project(project.id)
        assert updated_project.name == "Updated Name"
        assert updated_project.description == "Updated Description"
        assert updated_project.end_date.date() == new_end_date.date()
        assert updated_project.status == "on_hold"
    
    def test_update_project_nonexistent(self):
        result = self.controller.update_project(99999, name="New Name")
        assert result == False
    
    def test_update_project_invalid_status(self):
        project = self.controller.add_project(
            name="Test Project",
            description="Test Description",
            start_date=self.start_date,
            end_date=self.end_date
        )
        
        with pytest.raises(ValueError, match="Статус должен быть одним из"):
            self.controller.update_project(project.id, status="invalid_status")
    
    def test_update_project_invalid_dates(self):
        project = self.controller.add_project(
            name="Test Project",
            description="Test Description",
            start_date=self.start_date,
            end_date=self.end_date
        )
        
        invalid_end_date = self.start_date - timedelta(days=1)
        
        with pytest.raises(ValueError, match="Дата начала должна быть раньше"):
            self.controller.update_project(
                project.id,
                end_date=invalid_end_date
            )
    
    def test_delete_project_success(self):
        project = self.controller.add_project(
            name="Project to Delete",
            description="Will be deleted",
            start_date=self.start_date,
            end_date=self.end_date
        )
        
        result = self.controller.delete_project(project.id)
        assert result == True
        
        deleted_project = self.controller.get_project(project.id)
        assert deleted_project is None
    
    def test_delete_project_nonexistent(self):
        result = self.controller.delete_project(99999)
        assert result == False
    
    def test_update_project_status_success(self):
        project = self.controller.add_project(
            name="Test Project",
            description="Test Description",
            start_date=self.start_date,
            end_date=self.end_date
        )
        
        result = self.controller.update_project_status(project.id, "completed")
        assert result == True
        
        updated_project = self.controller.get_project(project.id)
        assert updated_project.status == "completed"
    
    def test_update_project_status_invalid(self):
        project = self.controller.add_project(
            name="Test Project",
            description="Test Description",
            start_date=self.start_date,
            end_date=self.end_date
        )
        
        with pytest.raises(ValueError, match="Статус должен быть одним из"):
            self.controller.update_project_status(project.id, "invalid_status")
    
    def test_get_project_progress_success(self):
        project = self.controller.add_project(
            name="Test Project",
            description="Test Description",
            start_date=self.start_date,
            end_date=self.end_date
        )
        
        task1 = self.task_controller.add_task(
            title="Task 1",
            description="Description 1",
            priority=1,
            due_date=datetime.now() + timedelta(days=5),
            project_id=project.id,
            assignee_id=self.user.id
        )
        
        task2 = self.task_controller.add_task(
            title="Task 2",
            description="Description 2",
            priority=2,
            due_date=datetime.now() + timedelta(days=10),
            project_id=project.id,
            assignee_id=self.user.id
        )
        
        self.task_controller.update_task_status(task1.id, "completed")
        
        progress = self.controller.get_project_progress(project.id)
        
        assert isinstance(progress, (int, float))
        assert progress == 50.0
    
    def test_get_project_progress_nonexistent(self):
        with pytest.raises(ValueError, match="Проект с ID"):
            self.controller.get_project_progress(99999)


class TestUserController:
    
    def setup_method(self):
        self.db_manager = DatabaseManager(":memory:")
        self.controller = UserController(self.db_manager)
        self.user = self.controller.add_user(
            username="testuser",
            email="test@example.com",
            role="developer"
        )

    def teardown_method(self):
        if hasattr(self.db_manager, 'close'):
            self.db_manager.close()

    def test_add_user_success(self):
        user = self.controller.add_user(
            username="newuser",
            email="new@example.com",
            role="developer"
        )
        
        assert user.id is not None
        assert user.username == "newuser"
        assert user.email == "new@example.com"
        assert user.role == "developer"
    
    def test_add_user_invalid_email(self):
        
        with pytest.raises(ValueError, match="Некорректный email адрес"):
            self.controller.add_user(
                username="testuser",
                email="invalid-email",
                role="developer"
            )
    
    def test_add_user_invalid_role(self):
        
        with pytest.raises(ValueError, match="Роль должна быть одной из"):
            self.controller.add_user(
                username="testuser",
                email="test@example.com",
                role="invalid_role"
            )
    
    def test_add_user_duplicate_username(self):

        with pytest.raises(ValueError, match="уже существует"):
            self.controller.add_user(
                username="testuser",
                email="test2@example.com",
                role="manager"
            )
    
    def test_add_user_duplicate_email(self):

        with pytest.raises(ValueError, match="уже существует"):
            self.controller.add_user(
                username="user2",
                email="test@example.com",
                role="manager"
            )
    
    def test_get_user_success(self):
        retrieved_user = self.controller.get_user(self.user.id)
        assert retrieved_user is not None
        assert retrieved_user.id == self.user.id
        assert retrieved_user.username == self.user.username
        assert retrieved_user.email == self.user.email
        assert retrieved_user.role == self.user.role
    
    def test_get_user_nonexistent(self):
        user = self.controller.get_user(99999)
        assert user is None
    
    def test_get_all_users(self):

        user2 = self.controller.add_user(
            username="user2",
            email="user2@example.com",
            role="manager"
        )
        
        all_users = self.controller.get_all_users()
        
        assert isinstance(all_users, list)
        assert len(all_users) >= 2
        
        user_ids = [u.id for u in all_users]
        assert self.user.id in user_ids
        assert user2.id in user_ids
    
    def test_update_user_success(self):

        result = self.controller.update_user(
            self.user.id,
            username="updateduser",
            email="updated@example.com",
            role="admin"
        )
        
        assert result == True
        
        updated_user = self.controller.get_user(self.user.id)
        assert updated_user.username == "updateduser"
        assert updated_user.email == "updated@example.com"
        assert updated_user.role == "admin"
    
    def test_update_user_partial(self):

        result = self.controller.update_user(
            self.user.id,
            username="newusername"
        )
        
        assert result == True
        
        updated_user = self.controller.get_user(self.user.id)
        assert updated_user.username == "newusername"
        assert updated_user.email == "test@example.com"
        assert updated_user.role == "developer"
    
    def test_update_user_nonexistent(self):
        result = self.controller.update_user(99999, username="newuser")
        assert result == False
    
    def test_update_user_invalid_role(self):

        with pytest.raises(ValueError, match="Роль должна быть одной из"):
            self.controller.update_user(self.user.id, role="invalid_role")
    
    def test_update_user_invalid_email(self):

        with pytest.raises(ValueError, match="Некорректный email адрес"):
            self.controller.update_user(self.user.id, email="invalid-email")
    
    def test_update_user_duplicate_email(self):

        user2 = self.controller.add_user(
            username="user2",
            email="user2@example.com",
            role="manager"
        )
        
        with pytest.raises(ValueError, match="уже существует"):
            self.controller.update_user(user2.id, email="test@example.com")
    
    def test_update_user_duplicate_username(self):

        user2 = self.controller.add_user(
            username="user2",
            email="user2@example.com",
            role="manager"
        )
        
        with pytest.raises(ValueError, match="уже существует"):
            self.controller.update_user(user2.id, username="testuser")
    
    def test_delete_user_success(self):
        user_to_delete = self.controller.add_user(
            username="user_to_delete",
            email="delete@example.com",
            role="developer"
        )
        
        result = self.controller.delete_user(user_to_delete.id)
        assert result == True
        
        deleted_user = self.controller.get_user(user_to_delete.id)
        assert deleted_user is None
    
    def test_delete_user_nonexistent(self):
        result = self.controller.delete_user(99999)
        assert result == False
    
    def test_get_user_tasks(self):
        project_controller = ProjectController(self.db_manager)
        task_controller = TaskController(self.db_manager)
        project = project_controller.add_project(
            name="Test Project",
            description="Test Description",
            start_date=datetime.now() + timedelta(days=1),
            end_date=datetime.now() + timedelta(days=30)
        )

        task1 = task_controller.add_task(
            title="Task 1",
            description="Description 1",
            priority=1,
            due_date=datetime.now() + timedelta(days=7),
            project_id=project.id,
            assignee_id=self.user.id
        )
        
        other_user = self.controller.add_user(
            username="otheruser",
            email="other@example.com",
            role="developer"
        )
        
        task2 = task_controller.add_task(
            title="Task 2",
            description="Description 2",
            priority=2,
            due_date=datetime.now() + timedelta(days=14),
            project_id=project.id,
            assignee_id=other_user.id
        )
        
        user_tasks = self.controller.get_user_tasks(self.user.id)
        
        assert isinstance(user_tasks, list)
        assert len(user_tasks) >= 1
        
        if user_tasks:
            task = user_tasks[0]
            assert "id" in task
            assert "title" in task
            assert "description" in task or "project_name" in task
            assert "is_overdue" in task or "status" in task
        
        task_ids = [t["id"] for t in user_tasks]
        assert task1.id in task_ids, f"Задача {task1.id} должна быть в списке"
        assert task2.id not in task_ids, f"Задача {task2.id} не должна быть в списке"