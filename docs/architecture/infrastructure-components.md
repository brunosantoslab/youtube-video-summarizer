# YouTube Video Summarizer - Infrastructure Components

This document outlines the infrastructure components that will implement the interfaces defined in the domain and application layers.

## Persistence Infrastructure

### Database Context

The primary database context for the application using PostgreSQL.

```python
# Example implementation using SQLAlchemy
class YVSDatabaseContext:
    def __init__(self, connection_string):
        self.engine = create_engine(connection_string)
        self.session_factory = sessionmaker(bind=self.engine)
        self.metadata = MetaData()
        
    def create_session(self):
        return self.session_factory()
    
    def create_tables(self):
        Base.metadata.create_all(self.engine)
```

### Repository Implementations

#### PostgresUserRepository

Implementation of the `IUserRepository` interface.

```python
class PostgresUserRepository(IUserRepository):
    def __init__(self, db_context):
        self.db_context = db_context
        
    def get_by_id(self, id):
        with self.db_context.create_session() as session:
            return session.query(UserEntity).filter(UserEntity.id == id).first()
    
    def get_by_youtube_id(self, youtube_id):
        with self.db_context.create_session() as session:
            return session.query(UserEntity).filter(UserEntity.youtube_id == youtube_id).first()
    
    def create(self, user):
        with self.db_context.create_session() as session:
            user_entity = UserEntity.from_domain(user)
            session.add(user_entity)
            session.commit()
            return user_entity.to_domain()
    
    def update(self, user):
        with self.db_context.create_session() as session:
            user_entity = session.query(UserEntity).filter(UserEntity.id == user.id).first()
            user_entity.update_from_domain(user)
            session.commit()
            return user_entity.to_domain()
    
    def delete(self, id):
        with self.db_context.create_session() as session:
            user_entity = session.query(UserEntity).filter(UserEntity.id == id).first()
            if user_entity:
                session.delete(user_entity)
                session.commit()
                return True
            return False
```

Similar implementations would exist for all repository interfaces.

### Entity Mappings

Database entity mappings separate from domain entities.

```python
# Example using SQLAlchemy ORM
class UserEntity(Base):
    __tablename__ = 'users'
    
    id = Column(UUID, primary_key=True)
    email = Column(String, unique=True)
    youtube_user_id = Column(String, unique=True)
    display_name = Column(String)
    preferences_json = Column(JSON)
    date_created = Column(DateTime)
    date_modified = Column(DateTime)
    
    @staticmethod
    def from_domain(user_domain):
        return UserEntity(
            id=user_domain.id,
            email=user_domain.email,
            youtube_user_id=user_domain.youtube_user_id,
            display_name=user_domain.display_name,
            preferences_json=json.dumps(user_domain.preference_settings.to_dict()),
            date_created=user_domain.date_created,
            date_modified=user_domain.date_modified
        )
    
    def to_domain(self):
        from domain.models import User, UserPreferences
        return User(
            id=self.id,
            email=self.email,
            youtube_user_id=self.youtube_user_id,
            display_name=self.display_name,
            preference_settings=UserPreferences.from_dict(json.loads(self.preferences_json)),
            date_created=self.date_created,
            date_modified=self.date_modified
        )
    
    def update_from_domain(self, user_domain):
        self.email = user_domain.email
        self.youtube_user_id = user_domain.youtube_user_id
        self.display_name = user_domain.display_name
        self.preferences_json = json.dumps(user_domain.preference_settings.to_dict())
        self.date_modified = datetime.now()
```

Similar entity mappings would exist for all domain entities.

## External Service Integrations

### YouTubeApiClient

Handles integration with the YouTube Data API.

```python
class YouTubeApiClient:
    def __init__(self, api_key, client_id, client_secret, redis_cache):
        self.api_key = api_key
        self.client_id = client_id
        self.client_secret = client_secret
        self.redis_cache = redis_cache
        
    def get_subscriptions(self, access_token, page_token=None):
        cache_key = f"yt_subs_{hash(access_token)}_{page_token}"
        cached_result = self.redis_cache.get(cache_key)
        
        if cached_result:
            return json.loads(cached_result)
        
        # Make API call to YouTube
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {
            "part": "snippet",
            "mine": "true",
            "maxResults": 50,
            "pageToken": page_token
        }
        
        response = requests.get(
            "https://www.googleapis.com/youtube/v3/subscriptions",
            headers=headers,
            params=params
        )
        
        result = response.json()
        self.redis_cache.set(cache_key, json.dumps(result), ex=3600)  # Cache for 1 hour
        return result
    
    def get_video_details(self, video_id, part="snippet,contentDetails"):
        cache_key = f"yt_video_{video_id}_{part}"
        cached_result = self.redis_cache.get(cache_key)
        
        if cached_result:
            return json.loads(cached_result)
        
        params = {
            "part": part,
            "id": video_id,
            "key": self.api_key
        }
        
        response = requests.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params=params
        )
        
        result = response.json()
        self.redis_cache.set(cache_key, json.dumps(result), ex=86400)  # Cache for 24 hours
        return result
    
    def get_video_transcript(self, video_id, language_code=None):
        # Implementation of YouTube caption retrieval
        # ...
```

### AIProviderClient

Manages interactions with AI services for summarization and topic extraction.

```python
class AIProviderClient:
    def __init__(self, config, redis_cache):
        self.config = config
        self.redis_cache = redis_cache
        self.openai_client = OpenAIClient(config.openai_api_key)
        self.google_client = GoogleAIClient(config.google_api_key)
        
    def generate_summary(self, transcript, model=None, max_tokens=None):
        # Select appropriate AI provider based on config or parameter
        provider = model or self.config.default_ai_provider
        
        if provider == "openai":
            return self.openai_client.generate_summary(transcript, max_tokens)
        elif provider == "google":
            return self.google_client.generate_summary(transcript, max_tokens)
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")
    
    def extract_topics(self, text, max_topics=5, min_relevance=0.3):
        # Similar provider selection logic
        # ...
```

### LangChainService

Implements LangChain workflows for advanced NLP tasks.

```python
class LangChainService:
    def __init__(self, ai_provider_client):
        self.ai_provider_client = ai_provider_client
        
    def extract_topics_from_transcript(self, transcript, max_topics=5):
        # Implement LangChain workflow for topic extraction
        # ...
        
    def generate_structured_summary(self, transcript, summary_format):
        # Implement LangChain workflow for structured summary generation
        # ...
        
    def detect_topic_timestamps(self, transcript, topics):
        # Implement LangChain workflow to find when topics appear in transcript
        # ...
```

## Caching Infrastructure

### RedisCache

Implements caching for expensive operations.

```python
class RedisCache:
    def __init__(self, redis_url):
        self.redis_client = redis.from_url(redis_url)
        
    def get(self, key):
        return self.redis_client.get(key)
        
    def set(self, key, value, ex=None):
        return self.redis_client.set(key, value, ex=ex)
        
    def delete(self, key):
        return self.redis_client.delete(key)
        
    def exists(self, key):
        return self.redis_client.exists(key)
```

## Background Processing

### CeleryTaskQueue

Manages asynchronous processing tasks.

```python
class CeleryTaskQueue:
    def __init__(self, broker_url, backend_url):
        self.app = Celery('yvs', broker=broker_url, backend=backend_url)
        
    def initialize(self):
        self.app.conf.update(
            task_serializer='json',
            accept_content=['json'],
            result_serializer='json',
            timezone='UTC',
            enable_utc=True,
        )
        
    def register_tasks(self, tasks_module):
        self.app.autodiscover_tasks([tasks_module])
        
    def enqueue_task(self, task_name, args=None, kwargs=None, countdown=None):
        args = args or []
        kwargs = kwargs or {}
        return self.app.send_task(task_name, args=args, kwargs=kwargs, countdown=countdown)
```

## Authentication Infrastructure

### YouTubeAuthService

Manages YouTube OAuth authentication.

```python
class YouTubeAuthService:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        
    def get_authorization_url(self, state=None):
        oauth = OAuth2Session(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri,
            scope=["https://www.googleapis.com/auth/youtube.readonly"]
        )
        authorization_url, state = oauth.authorization_url(
            "https://accounts.google.com/o/oauth2/auth",
            access_type="offline",
            prompt="consent"
        )
        return authorization_url, state
        
    def get_token(self, code):
        oauth = OAuth2Session(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri
        )
        token = oauth.fetch_token(
            "https://oauth2.googleapis.com/token",
            code=code,
            client_secret=self.client_secret
        )
        return token
        
    def refresh_token(self, refresh_token):
        # Implementation of token refresh
        # ...
```

## Configuration Management

### ConfigurationProvider

Manages application configuration.

```python
class ConfigurationProvider:
    def __init__(self, config_file_path=None, env_prefix="YVS_"):
        self.config_file_path = config_file_path
        self.env_prefix = env_prefix
        self.config = {}
        self._load_config()
        
    def _load_config(self):
        # Load from file if specified
        if self.config_file_path and os.path.exists(self.config_file_path):
            with open(self.config_file_path, 'r') as f:
                self.config.update(json.load(f))
                
        # Override with environment variables
        for key, value in os.environ.items():
            if key.startswith(self.env_prefix):
                config_key = key[len(self.env_prefix):].lower()
                self.config[config_key] = value
        
    def get(self, key, default=None):
        return self.config.get(key, default)
        
    def get_connection_string(self):
        # Construct database connection string from config values
        # ...
```

## Logging and Monitoring

### StructuredLogger

Provides structured logging throughout the application.

```python
class StructuredLogger:
    def __init__(self, app_name, log_level=logging.INFO):
        self.logger = logging.getLogger(app_name)
        self.logger.setLevel(log_level)
        
        # Configure handlers and formatters
        handler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
    def info(self, message, **kwargs):
        self.logger.info(message, extra=kwargs)
        
    def error(self, message, **kwargs):
        self.logger.error(message, extra=kwargs)
        
    def warning(self, message, **kwargs):
        self.logger.warning(message, extra=kwargs)
        
    def debug(self, message, **kwargs):
        self.logger.debug(message, extra=kwargs)
```

### MetricsCollector

Collects application metrics for monitoring.

```python
class MetricsCollector:
    def __init__(self, app_name):
        self.app_name = app_name
        # Setup metrics collection (e.g., Prometheus, StatsD)
        # ...
        
    def increment_counter(self, name, value=1, tags=None):
        # Implementation of counter metric
        # ...
        
    def record_timing(self, name, value, tags=None):
        # Implementation of timing metric
        # ...
        
    def gauge(self, name, value, tags=None):
        # Implementation of gauge metric
        # ...
```

## Event Infrastructure

### EventPublisher

Manages domain event publication.

```python
class EventPublisher:
    def __init__(self, redis_client):
        self.redis_client = redis_client
        
    def publish(self, event_type, payload):
        event = {
            "id": str(uuid.uuid4()),
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            "payload": payload
        }
        
        # Publish to Redis pub/sub channel
        self.redis_client.publish(
            f"events:{event_type}",
            json.dumps(event)
        )
        return event["id"]
```

### EventSubscriber

Manages event subscription and handling.

```python
class EventSubscriber:
    def __init__(self, redis_client, logger):
        self.redis_client = redis_client
        self.logger = logger
        self.handlers = {}
        
    def register_handler(self, event_type, handler):
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
        
    def start_listening(self):
        pubsub = self.redis_client.pubsub()
        channels = [f"events:{event_type}" for event_type in self.handlers.keys()]
        pubsub.subscribe(*channels)
        
        for message in pubsub.listen():
            if message["type"] == "message":
                channel = message["channel"].decode("utf-8")
                event_type = channel.split(":", 1)[1]
                
                if event_type in self.handlers:
                    event_data = json.loads(message["data"])
                    for handler in self.handlers[event_type]:
                        try:
                            handler(event_data)
                        except Exception as e:
                            self.logger.error(
                                f"Error handling event {event_type}",
                                event_id=event_data["id"],
                                error=str(e)
                            )
```

*Author: Bruno Santos*
