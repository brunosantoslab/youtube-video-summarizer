# YouTube Video Summarizer - Testing Strategy

This document outlines the comprehensive testing strategy for the YouTube Video Summarizer application, ensuring code quality, functionality, and reliability.

## Testing Principles

1. **Test-Driven Development (TDD)**: Write tests before implementing features
2. **Continuous Testing**: Run tests automatically on every code change
3. **Test Pyramid**: Focus on unit tests, followed by integration and E2E tests
4. **Code Coverage**: Aim for high test coverage (target: 80%+)
5. **Meaningful Tests**: Focus on behavior, not implementation details
6. **Fast Feedback**: Optimize test suite for quick execution
7. **Test Independence**: Tests should not depend on each other

## Test Types

### Unit Tests

Focus on testing individual components, functions, and classes in isolation.

#### Domain Layer Testing

- **Entity Tests**: Verify entity behavior and business rules
- **Service Tests**: Test domain service logic with mocked dependencies
- **Value Object Tests**: Ensure correct behavior of value objects

Example domain test:

```python
def test_summary_content_length():
    # Arrange
    summary = Summary(
        id=uuid.uuid4(),
        video_id=uuid.uuid4(),
        content="Test content",
        model_provider="test-provider",
        model_version="1.0",
        processing_metadata=SummaryMetadata(
            processing_time=timedelta(seconds=5),
            token_count=100,
            prompt_version="1.0",
            confidence_score=0.9,
            model_parameters={}
        ),
        date_created=datetime.now(),
        date_modified=datetime.now()
    )
    
    # Act & Assert
    assert len(summary.content) > 0
    assert summary.model_provider == "test-provider"
    assert summary.processing_metadata.confidence_score == 0.9
```

#### Application Layer Testing

- **Service Tests**: Test orchestration logic with mocked repositories and external services
- **DTO Validation**: Verify DTO validation logic
- **Event Handler Tests**: Test event handler behavior

Example application service test:

```python
def test_summary_generation_service():
    # Arrange
    mock_video_repo = Mock(spec=IVideoRepository)
    mock_transcript_repo = Mock(spec=ITranscriptRepository)
    mock_summary_repo = Mock(spec=ISummaryRepository)
    mock_ai_client = Mock(spec=AIProviderClient)
    mock_event_publisher = Mock(spec=EventPublisher)
    
    video_id = uuid.uuid4()
    transcript_id = uuid.uuid4()
    summary_id = uuid.uuid4()
    
    video = Video(id=video_id, youtube_id="test", title="Test Video", ...)
    transcript = Transcript(id=transcript_id, video_id=video_id, content="Test transcript", ...)
    
    mock_video_repo.get_by_id.return_value = video
    mock_transcript_repo.get_by_video.return_value = transcript
    mock_ai_client.generate_summary.return_value = "Generated summary"
    mock_summary_repo.create.return_value = Summary(id=summary_id, video_id=video_id, ...)
    
    service = SummaryGenerationService(
        video_repository=mock_video_repo,
        transcript_repository=mock_transcript_repo,
        summary_repository=mock_summary_repo,
        ai_provider_client=mock_ai_client,
        event_publisher=mock_event_publisher
    )
    
    # Act
    result = service.generate_summary(video_id)
    
    # Assert
    assert result == summary_id
    mock_video_repo.get_by_id.assert_called_once_with(video_id)
    mock_transcript_repo.get_by_video.assert_called_once_with(video_id)
    mock_ai_client.generate_summary.assert_called_once()
    mock_summary_repo.create.assert_called_once()
    mock_event_publisher.publish.assert_called_once()
```

#### Infrastructure Layer Testing

- **Repository Tests**: Test repository implementations with in-memory or test database
- **API Client Tests**: Verify external service clients with mocked HTTP responses
- **Caching Tests**: Test caching behavior

Example repository test:

```python
def test_postgres_video_repository():
    # Arrange
    test_db = TestDatabaseContext()  # In-memory test database
    repo = PostgresVideoRepository(test_db)
    
    video = Video(
        id=uuid.uuid4(),
        youtube_id="test123",
        title="Test Video",
        description="Test description",
        channel_id="channel123",
        channel_title="Test Channel",
        published_at=datetime.now(),
        duration=timedelta(minutes=5),
        thumbnail_url="https://example.com/thumb.jpg",
        status=VideoStatus.NEW,
        date_created=datetime.now(),
        date_modified=datetime.now()
    )
    
    # Act
    created_video = repo.create(video)
    retrieved_video = repo.get_by_id(video.id)
    
    # Assert
    assert retrieved_video is not None
    assert retrieved_video.id == video.id
    assert retrieved_video.youtube_id == "test123"
    assert retrieved_video.title == "Test Video"
```

### Integration Tests

Focus on testing the interaction between components and systems.

#### Repository Integration Tests

- Test repositories against a real test database
- Verify transaction handling and constraints

Example repository integration test:

```python
@pytest.mark.integration
def test_video_repository_integration():
    # Setup test database with migrations
    db_context = create_test_db_context()
    
    # Create repository with real database
    repo = PostgresVideoRepository(db_context)
    
    # Test CRUD operations
    video = Video(...)
    created = repo.create(video)
    retrieved = repo.get_by_id(video.id)
    
    assert retrieved.id == created.id
    
    # Test querying
    videos_by_status = repo.get_by_status(VideoStatus.NEW)
    assert len(videos_by_status) > 0
```

#### API Integration Tests

- Test backend API endpoints with HTTP clients
- Verify request/response handling and error cases

Example API test:

```python
@pytest.mark.integration
def test_summary_api_endpoint():
    # Setup test client
    client = TestClient(app)
    
    # Create test data in database
    video_id = create_test_video()
    
    # Test API endpoint
    response = client.get(f"/api/summaries/video/{video_id}")
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert "content" in data
    assert data["videoId"] == str(video_id)
```

#### External Service Integration Tests

- Test integration with YouTube API, AI providers
- Use recorded responses or test environments

Example external service test:

```python
@pytest.mark.integration
@vcr.use_cassette("tests/fixtures/vcr_cassettes/youtube_api.yaml")
def test_youtube_api_client():
    # Create client with test credentials
    client = YouTubeApiClient(
        api_key=TEST_API_KEY,
        client_id=TEST_CLIENT_ID,
        client_secret=TEST_CLIENT_SECRET,
        redis_cache=MockRedisCache()
    )
    
    # Test API interaction
    video_details = client.get_video_details("dQw4w9WgXcQ")
    
    # Verify response
    assert video_details is not None
    assert "items" in video_details
    assert len(video_details["items"]) > 0
```

### End-to-End Tests

Test complete user flows from frontend to backend.

#### User Flow Tests

- Test key user journeys across the entire application
- Verify system behavior from user perspective

Example E2E test:

```python
@pytest.mark.e2e
def test_video_summary_flow():
    # Setup
    setup_test_database()
    start_test_server()
    driver = webdriver.Chrome()
    
    try:
        # Log in
        driver.get("http://localhost:3000/login")
        # ... authentication steps ...
        
        # Navigate to dashboard
        driver.get("http://localhost:3000/dashboard")
        
        # Add a test video
        add_video_button = driver.find_element_by_id("add-video-button")
        add_video_button.click()
        
        video_url_input = driver.find_element_by_id("video-url-input")
        video_url_input.send_keys("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        
        submit_button = driver.find_element_by_id("submit-video-button")
        submit_button.click()
        
        # Wait for processing
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "summary-content"))
        )
        
        # Verify summary content
        summary_content = driver.find_element_by_id("summary-content")
        assert summary_content.text != ""
        
        # Verify topics are extracted
        topics_section = driver.find_element_by_id("topics-section")
        topics = topics_section.find_elements_by_class_name("topic-tag")
        assert len(topics) > 0
        
    finally:
        driver.quit()
        stop_test_server()
```

#### Performance Tests

- Test system performance under load
- Identify bottlenecks and optimize

Example performance test:

```python
@pytest.mark.performance
def test_summary_generation_performance():
    # Setup
    client = TestClient(app)
    
    # Create test data
    video_ids = create_test_videos(10)
    
    # Measure performance
    start_time = time.time()
    
    for video_id in video_ids:
        response = client.post(f"/api/summaries/generate", json={"videoId": str(video_id)})
        assert response.status_code == 202  # Accepted for processing
    
    # Wait for all tasks to complete
    all_completed = False
    timeout = time.time() + 300  # 5 minute timeout
    
    while not all_completed and time.time() < timeout:
        all_completed = True
        for video_id in video_ids:
            status_response = client.get(f"/api/summaries/status/{video_id}")
            status = status_response.json()["status"]
            if status not in ["COMPLETED", "FAILED"]:
                all_completed = False
                break
        if not all_completed:
            time.sleep(5)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Verify performance meets requirements
    assert total_time < 600  # Total process should take less than 10 minutes
    
    # Check success rate
    success_count = 0
    for video_id in video_ids:
        status_response = client.get(f"/api/summaries/status/{video_id}")
        if status_response.json()["status"] == "COMPLETED":
            success_count += 1
    
    success_rate = success_count / len(video_ids)
    assert success_rate >= 0.8  # At least 80% success rate
```

### Frontend Tests

Focus on testing React components and user interactions.

#### Component Tests

- Test rendering and behavior of UI components
- Verify component props and state management

Example component test:

```typescript
describe('SummaryCard', () => {
  it('renders correctly with data', () => {
    // Arrange
    const mockSummary = {
      id: '123',
      video: {
        id: '456',
        title: 'Test Video',
        channelTitle: 'Test Channel',
        publishedAt: '2023-01-01T00:00:00Z',
        thumbnailUrl: 'https://example.com/thumb.jpg'
      },
      content: 'This is a test summary content',
      topics: [
        { id: 't1', name: 'Topic 1', relevance: 0.9 },
        { id: 't2', name: 'Topic 2', relevance: 0.7 }
      ]
    };
    
    // Mock the custom hook
    jest.mock('../hooks/useSummary', () => ({
      useSummary: () => ({
        summary: mockSummary,
        topics: mockSummary.topics,
        loading: false,
        error: null
      })
    }));
    
    const handleClick = jest.fn();
    
    // Act
    const { getByText, getAllByTestId } = render(
      <SummaryCard summaryId="123" onClick={handleClick} />
    );
    
    // Assert
    expect(getByText('Test Video')).toBeInTheDocument();
    expect(getByText('Test Channel')).toBeInTheDocument();
    expect(getByText(/This is a test summary/)).toBeInTheDocument();
    
    const topicTags = getAllByTestId('topic-tag');
    expect(topicTags).toHaveLength(2);
    
    // Test interaction
    fireEvent.click(getByText('Test Video'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
  
  it('shows skeleton while loading', () => {
    // Mock loading state
    jest.mock('../hooks/useSummary', () => ({
      useSummary: () => ({
        summary: null,
        topics: [],
        loading: true,
        error: null
      })
    }));
    
    // Act
    const { getByTestId } = render(<SummaryCard summaryId="123" />);
    
    // Assert
    expect(getByTestId('summary-card-skeleton')).toBeInTheDocument();
  });
});
```

#### Redux Tests

- Test Redux actions, reducers, and selectors
- Verify state management logic

Example Redux test:

```typescript
describe('summaries reducer', () => {
  it('should handle fetch summary success', () => {
    // Arrange
    const initialState = {
      byId: {},
      loading: true,
      error: null,
      currentSummaryId: null
    };
    
    const summary = {
      id: '123',
      videoId: '456',
      content: 'Test content'
    };
    
    // Act
    const nextState = summariesReducer(
      initialState,
      fetchSummarySuccess(summary)
    );
    
    // Assert
    expect(nextState.loading).toBe(false);
    expect(nextState.byId['123']).toEqual(summary);
    expect(nextState.error).toBeNull();
  });
  
  it('should handle fetch summary failure', () => {
    // Arrange
    const initialState = {
      byId: {},
      loading: true,
      error: null,
      currentSummaryId: null
    };
    
    const error = 'Failed to fetch summary';
    
    // Act
    const nextState = summariesReducer(
      initialState,
      fetchSummaryFailure(error)
    );
    
    // Assert
    expect(nextState.loading).toBe(false);
    expect(nextState.error).toBe(error);
  });
});
```

#### Custom Hook Tests

- Test behavior of custom React hooks
- Verify data fetching and state updates

Example hook test:

```typescript
describe('useSummary hook', () => {
  it('should fetch summary data', async () => {
    // Mock API response
    jest.mock('../services/summaryApi', () => ({
      getSummaryById: jest.fn().mockResolvedValue({
        id: '123',
        videoId: '456',
        content: 'Test content'
      }),
      getTopicsBySummaryId: jest.fn().mockResolvedValue([
        { id: 't1', name: 'Topic 1', relevance: 0.9 }
      ])
    }));
    
    // Setup Redux mock
    const mockDispatch = jest.fn();
    jest.mock('react-redux', () => ({
      useDispatch: () => mockDispatch,
      useSelector: jest.fn(selector => {
        // Mock selector state
        const state = {
          summaries: {
            byId: {},
            loading: false,
            error: null
          },
          topics: {
            byId: {},
            bySummaryId: {}
          }
        };
        return selector(state);
      })
    }));
    
    // Act
    const { result, waitForNextUpdate } = renderHook(() => useSummary('123'));
    
    // Initial state
    expect(result.current.loading).toBe(true);
    expect(result.current.summary).toBeUndefined();
    
    // Wait for data fetching
    await waitForNextUpdate();
    
    // Assert
    expect(mockDispatch).toHaveBeenCalledTimes(2); // For summary and topics
    expect(result.current.loading).toBe(false);
    expect(result.current.summary).toBeDefined();
    expect(result.current.summary.id).toBe('123');
    expect(result.current.topics).toHaveLength(1);
    expect(result.current.topics[0].name).toBe('Topic 1');
  });
});
```

## Test Tools and Frameworks

### Backend Testing

- **pytest**: Main testing framework for Python code
- **pytest-cov**: Code coverage reporting
- **pytest-xdist**: Parallel test execution
- **pytest-mock**: Mocking functionality
- **pytest-asyncio**: Testing async code
- **VCR.py**: Record and replay HTTP interactions

### Frontend Testing

- **Jest**: Main testing framework for JavaScript/TypeScript
- **React Testing Library**: Testing React components
- **MSW (Mock Service Worker)**: Mocking API requests
- **jest-dom**: Custom DOM element matchers

### E2E Testing

- **Playwright**: Cross-browser end-to-end testing
- **Cypress**: Alternative for E2E testing

### Performance Testing

- **Locust**: Load testing tool
- **pytest-benchmark**: Performance benchmarking

## Test Coverage Thresholds

| Component        | Threshold |
|------------------|-----------|
| Domain Layer     | 90%       |
| Application Layer| 85%       |
| Infrastructure   | 80%       |
| API Controllers  | 80%       |
| Frontend Components | 75%    |
| E2E Workflows    | Key user journeys |

## Mocking Strategy

- **External Services**: Always mock for unit/integration tests
- **Repositories**: Mock for unit tests, use test DB for integration tests
- **Domain Services**: Mock for application service tests
- **APIs**: Use mock server for frontend tests

## Continuous Integration

- Run unit tests on every commit
- Run integration tests on pull requests
- Run E2E tests nightly and before releases
- Generate and publish coverage reports

Example GitHub Actions workflow:

```yaml
name: Test Suite

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt
      - name: Run unit tests
        run: |
          pytest tests/unit --cov=src --cov-report=xml
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v1
        
  integration-tests:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: yvs_test
        ports:
          - 5432:5432
      redis:
        image: redis:6
        ports:
          - 6379:6379
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt
      - name: Run integration tests
        run: |
          pytest tests/integration
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/yvs_test
          REDIS_URL: redis://localhost:6379/0
```

## Test Data Management

- Use factories for generating test entities
- Maintain test fixtures for complex scenarios
- Clean up test data after test execution

Example test data factory:

```python
class VideoFactory:
    @staticmethod
    def create(
        id=None,
        youtube_id=None,
        title=None,
        description=None,
        channel_id=None,
        channel_title=None,
        published_at=None,
        duration=None,
        thumbnail_url=None,
        status=None
    ):
        return Video(
            id=id or uuid.uuid4(),
            youtube_id=youtube_id or f"yt-{uuid.uuid4().hex[:11]}",
            title=title or f"Test Video {random.randint(1, 1000)}",
            description=description or "Test video description",
            channel_id=channel_id or f"channel-{uuid.uuid4().hex[:8]}",
            channel_title=channel_title or f"Test Channel {random.randint(1, 100)}",
            published_at=published_at or datetime.now() - timedelta(days=random.randint(1, 30)),
            duration=duration or timedelta(minutes=random.randint(5, 20)),
            thumbnail_url=thumbnail_url or f"https://example.com/thumb-{uuid.uuid4().hex}.jpg",
            status=status or VideoStatus.NEW,
            date_created=datetime.now(),
            date_modified=datetime.now()
        )
```

## Test Documentation

- Document test cases with clear descriptions
- Include test coverage reports in documentation
- Maintain testing guidelines for contributors

## Test Monitoring and Maintenance

- Regular review of failing tests
- Periodic test suite optimization
- Test debt management process

*Author: Bruno Santos*
