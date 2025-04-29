# api/tests/unit/services/test_video_processing_service.py
import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from domain.models.video import Video, VideoStatus
from domain.models.processing import ProcessingTask, ProcessingStatus
from application.services.video_processing_service import VideoProcessingService


@pytest.fixture
def mock_video_repository():
    repo = MagicMock()
    video = Video(
        id=uuid.uuid4(),
        youtube_id="test_video_id",
        title="Test Video",
        description="Test description",
        status=VideoStatus.NEW
    )
    repo.get_by_id.return_value = video
    return repo, video


@pytest.fixture
def mock_processing_repository():
    repo = MagicMock()
    
    # Mock create method
    def mock_create(task):
        task.id = uuid.uuid4()
        return task
    
    repo.create.side_effect = mock_create
    
    # Mock update_status
    def mock_update_status(task_id, status, error_message=None, completion_percentage=None):
        task = ProcessingTask(
            id=task_id,
            status=status,
            error_message=error_message,
            completion_percentage=completion_percentage or 0.0,
            results={}
        )
        return task
    
    repo.update_status.side_effect = mock_update_status
    
    # Mock get_by_video_id
    tasks = []
    repo.get_by_video_id.return_value = tasks
    
    return repo


@pytest.fixture
def mock_event_publisher():
    publisher = MagicMock()
    return publisher


@pytest.fixture
def mock_task_queue_service():
    service = MagicMock()
    service.enqueue_task.return_value = "task123"
    return service


def test_queue_video_for_processing(
    mock_video_repository, mock_processing_repository,
    mock_event_publisher, mock_task_queue_service
):
    # Arrange
    video_repo, video = mock_video_repository
    processing_repo = mock_processing_repository
    
    service = VideoProcessingService(
        video_repository=video_repo,
        processing_repository=processing_repo,
        event_publisher=mock_event_publisher,
        task_queue_service=mock_task_queue_service
    )
    
    # Act
    tasks = service.queue_video_for_processing(video.id)
    
    # Assert
    assert len(tasks) == 3  # Three tasks created
    
    # Verify video status was updated
    video_repo.update.assert_called_once()
    assert video.status == VideoStatus.PROCESSING
    
    # Verify task types
    task_types = [task.task_type for task in tasks]
    assert "transcript_extraction" in task_types
    assert "summary_generation" in task_types
    assert "topic_extraction" in task_types
    
    # Verify first task was queued
    mock_task_queue_service.enqueue_task.assert_called_once()
    
    # Using the correct assertion format for keyword arguments
    call_kwargs = mock_task_queue_service.enqueue_task.call_args.kwargs
    call_args = mock_task_queue_service.enqueue_task.call_args.args
    
    # Verify the first parameter is the task name
    assert call_args[0] == "tasks.process_video_step"
    # Verify the first parameter in the args list is the video ID
    assert call_kwargs.get('args')[0] == str(video.id)


def test_handle_step_completion_success(
    mock_video_repository, mock_processing_repository,
    mock_event_publisher, mock_task_queue_service
):
    # Arrange
    video_repo, video = mock_video_repository
    processing_repo = mock_processing_repository
    
    # Create processing tasks
    transcript_task = ProcessingTask(
        id=uuid.uuid4(),
        video_id=video.id,
        task_type="transcript_extraction",
        status=ProcessingStatus.IN_PROGRESS
    )
    summary_task = ProcessingTask(
        id=uuid.uuid4(),
        video_id=video.id,
        task_type="summary_generation",
        status=ProcessingStatus.PENDING
    )
    
    # Update mock repository
    processing_repo.get_by_video_id.return_value = [transcript_task, summary_task]
    
    service = VideoProcessingService(
        video_repository=video_repo,
        processing_repository=processing_repo,
        event_publisher=mock_event_publisher,
        task_queue_service=mock_task_queue_service
    )
    
    # Act
    service.handle_step_completion(
        video_id=video.id,
        task_type="transcript_extraction",
        success=True,
        result_id="transcript123"
    )
    
    # Assert
    # Verify task status was updated
    processing_repo.update_status.assert_called_once()
    
    # Verify task queue was called for next step
    mock_task_queue_service.enqueue_task.assert_called_once()
    call_kwargs = mock_task_queue_service.enqueue_task.call_args.kwargs
    call_args = mock_task_queue_service.enqueue_task.call_args.args
    
    # Verify the first parameter is the task name
    assert call_args[0] == "tasks.process_video_step"
    # Verify the parameters in the args list
    assert len(call_kwargs.get('args')) == 2
    assert call_kwargs.get('args')[1] == "summary_generation"


def test_handle_step_completion_failure(
    mock_video_repository, mock_processing_repository,
    mock_event_publisher, mock_task_queue_service
):
    # Arrange
    video_repo, video = mock_video_repository
    processing_repo = mock_processing_repository
    
    # Create processing task
    transcript_task = ProcessingTask(
        id=uuid.uuid4(),
        video_id=video.id,
        task_type="transcript_extraction",
        status=ProcessingStatus.IN_PROGRESS
    )
    
    # Update mock repository
    processing_repo.get_by_video_id.return_value = [transcript_task]
    
    service = VideoProcessingService(
        video_repository=video_repo,
        processing_repository=processing_repo,
        event_publisher=mock_event_publisher,
        task_queue_service=mock_task_queue_service
    )
    
    # Act
    service.handle_step_completion(
        video_id=video.id,
        task_type="transcript_extraction",
        success=False,
        error="Something went wrong"
    )
    
    # Assert
    # Verify task status was updated to FAILED
    processing_repo.update_status.assert_called_once()
    call_kwargs = processing_repo.update_status.call_args.kwargs
    
    # Verify task_id, status, and error_message parameters
    assert call_kwargs['task_id'] == transcript_task.id
    assert call_kwargs['status'] == ProcessingStatus.FAILED
    assert call_kwargs['error_message'] == "Something went wrong"
    
    # Verify video status was updated to FAILED
    video_repo.update.assert_called_once()
    assert video.status == VideoStatus.FAILED
    
    # Verify no next task was queued
    mock_task_queue_service.enqueue_task.assert_not_called()


def test_handle_step_completion_all_steps_complete(
    mock_video_repository, mock_processing_repository,
    mock_event_publisher, mock_task_queue_service
):
    # Arrange
    video_repo, video = mock_video_repository
    processing_repo = mock_processing_repository
    
    # Create processing tasks
    transcript_task = ProcessingTask(
        id=uuid.uuid4(),
        video_id=video.id,
        task_type="transcript_extraction",
        status=ProcessingStatus.COMPLETED
    )
    summary_task = ProcessingTask(
        id=uuid.uuid4(),
        video_id=video.id,
        task_type="summary_generation",
        status=ProcessingStatus.COMPLETED
    )
    topic_task = ProcessingTask(
        id=uuid.uuid4(),
        video_id=video.id,
        task_type="topic_extraction",
        status=ProcessingStatus.IN_PROGRESS
    )
    
    # Update mock repository
    processing_repo.get_by_video_id.return_value = [transcript_task, summary_task, topic_task]
    
    service = VideoProcessingService(
        video_repository=video_repo,
        processing_repository=processing_repo,
        event_publisher=mock_event_publisher,
        task_queue_service=mock_task_queue_service
    )
    
    # Act
    service.handle_step_completion(
        video_id=video.id,
        task_type="topic_extraction",
        success=True,
        result_id="topics123"
    )
    
    # Assert
    # Verify task status was updated
    processing_repo.update_status.assert_called_once()
    
    # Verify video status was updated to PROCESSED
    video_repo.update.assert_called_once()
    assert video.status == VideoStatus.PROCESSED
    
    # Verify no next task was queued
    mock_task_queue_service.enqueue_task.assert_not_called()


def test_get_processing_status(
    mock_video_repository, mock_processing_repository,
    mock_event_publisher, mock_task_queue_service
):
    # Arrange
    video_repo, video = mock_video_repository
    processing_repo = mock_processing_repository
    
    # Create processing tasks with different statuses
    transcript_task = ProcessingTask(
        id=uuid.uuid4(),
        video_id=video.id,
        task_type="transcript_extraction",
        status=ProcessingStatus.COMPLETED,
        completion_percentage=100.0,
        date_started=datetime.now(),
        date_completed=datetime.now()
    )
    summary_task = ProcessingTask(
        id=uuid.uuid4(),
        video_id=video.id,
        task_type="summary_generation",
        status=ProcessingStatus.IN_PROGRESS,
        completion_percentage=50.0,
        date_started=datetime.now()
    )
    topic_task = ProcessingTask(
        id=uuid.uuid4(),
        video_id=video.id,
        task_type="topic_extraction",
        status=ProcessingStatus.PENDING,
        completion_percentage=0.0
    )
    
    # Update mock repository
    processing_repo.get_by_video_id.return_value = [transcript_task, summary_task, topic_task]
    
    service = VideoProcessingService(
        video_repository=video_repo,
        processing_repository=processing_repo,
        event_publisher=mock_event_publisher,
        task_queue_service=mock_task_queue_service
    )
    
    # Act
    status = service.get_processing_status(video.id)
    
    # Assert
    assert status["video_id"] == str(video.id)
    assert status["status"] == "in_progress"
    assert status["progress"] == 50.0  # (100 + 50 + 0) / 3
    assert "tasks" in status
    assert "transcript_extraction" in status["tasks"]
    assert "summary_generation" in status["tasks"]
    assert "topic_extraction" in status["tasks"]
    assert status["tasks"]["transcript_extraction"]["status"] == "completed"
    assert status["tasks"]["summary_generation"]["status"] == "in_progress"
    assert status["tasks"]["topic_extraction"]["status"] == "pending"