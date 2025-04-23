# YouTube Video Summarizer - Frontend Architecture

This document outlines the frontend architecture for the YouTube Video Summarizer, built with React, TypeScript, and Tailwind CSS.

## Tech Stack

- **Framework**: React 18+ with TypeScript
- **State Management**: Redux Toolkit
- **Styling**: Tailwind CSS
- **Routing**: React Router
- **API Integration**: Axios
- **Testing**: Jest + React Testing Library
- **Build Tool**: Vite

## Architecture Overview

The frontend follows a component-based architecture with a focus on reusability, maintainability, and performance. It is organized into the following layers:

1. **Presentation Components**: UI components that focus solely on rendering
2. **Container Components**: Smart components that manage data and state
3. **Hooks**: Custom hooks for shared logic and API integration
4. **State Management**: Global application state using Redux
5. **API Client**: Communication layer with the backend API
6. **Utilities**: Helper functions and utilities

## Project Structure

```
src/
├── assets/             # Static assets
├── components/         # Reusable UI components
│   ├── common/         # General-purpose components
│   ├── layout/         # Layout components
│   ├── summaries/      # Summary-related components
│   ├── videos/         # Video-related components
│   └── topics/         # Topic-related components
├── containers/         # Container components
├── context/            # React context providers
├── hooks/              # Custom hooks
├── pages/              # Page components
├── services/           # API services
├── store/              # Redux store and slices
├── types/              # TypeScript type definitions
├── utils/              # Utility functions
├── App.tsx             # Main application component
└── main.tsx            # Application entry point
```

## Component Hierarchy

### Page Components

Top-level components that represent different pages in the application.

1. **DashboardPage**
   - Main dashboard displaying video summaries
   - Contains filtering and sorting options

2. **AuthPage**
   - Handles YouTube authentication flow
   - Includes login and callback handling

3. **VideoSummaryPage**
   - Detailed view of a single video summary
   - Shows topics, summary content, and links to original video

4. **SettingsPage**
   - User preference management
   - Authentication management

5. **SavedSummariesPage**
   - Collection of user-saved summaries
   - Organization options

### Core Components

#### Layout Components

1. **AppLayout**
   - Main application layout with header, footer, and sidebar
   - Handles responsive layout adjustments

2. **Sidebar**
   - Navigation menu
   - Quick access to saved summaries and filters

3. **Header**
   - User profile and authentication status
   - Global search
   - Notification indicators

#### Summary Components

1. **SummaryCard**
   - Compact view of a video summary for dashboard display
   - Shows key information and primary topics

2. **SummaryDetail**
   - Expanded view with full summary content
   - Organized topic presentation

3. **TopicList**
   - Displays topics extracted from a video
   - Includes relevance indicators and filtering

4. **TopicDetail**
   - Expanded information about a specific topic
   - Includes relevant timestamps and context

#### Video Components

1. **VideoPlayer**
   - Embedded YouTube video player
   - Custom controls for timestamp navigation

2. **VideoMetadata**
   - Displays video information (title, channel, etc.)
   - Publication date and other metadata

3. **VideoGrid**
   - Grid layout for multiple video cards
   - Pagination and infinite scroll support

#### Notebook Integration

1. **NotebookLink**
   - Generates and displays links for notebook viewing
   - Copy functionality and preview

2. **EmbedCodeGenerator**
   - Creates embed code for including videos in notebooks
   - Preview and configuration options

## Redux Store Structure

The application uses Redux Toolkit for state management, organized into slices:

```typescript
interface RootState {
  auth: {
    isAuthenticated: boolean;
    user: User | null;
    loading: boolean;
    error: string | null;
  };
  videos: {
    items: Video[];
    loading: boolean;
    error: string | null;
    pagination: {
      page: number;
      totalPages: number;
      totalItems: number;
    };
    filters: {
      search: string;
      channel: string | null;
      dateRange: { start: string | null; end: string | null };
      topics: string[];
    };
  };
  summaries: {
    byId: Record<string, Summary>;
    loading: boolean;
    error: string | null;
    currentSummaryId: string | null;
  };
  topics: {
    byId: Record<string, Topic>;
    bySummaryId: Record<string, string[]>;
    loading: boolean;
    error: string | null;
  };
  settings: {
    preferences: UserPreferences;
    loading: boolean;
    error: string | null;
  };
  ui: {
    sidebarOpen: boolean;
    currentTheme: 'light' | 'dark' | 'system';
    notifications: Notification[];
  };
}
```

## API Client

The API client handles communication with the backend:

```typescript
// Example API client for summaries
export const summaryApi = {
  getSummaries: (params: SummaryListParams): Promise<SummaryListResponse> => {
    return axiosInstance.get('/api/summaries', { params });
  },
  
  getSummaryById: (id: string): Promise<Summary> => {
    return axiosInstance.get(`/api/summaries/${id}`);
  },
  
  saveSummary: (summaryId: string): Promise<SavedSummary> => {
    return axiosInstance.post(`/api/summaries/${summaryId}/save`);
  },
  
  getSavedSummaries: (): Promise<SavedSummary[]> => {
    return axiosInstance.get('/api/summaries/saved');
  }
};
```

## Custom Hooks

Custom hooks encapsulate common functionality:

```typescript
// Example hook for working with summaries
export function useSummary(summaryId: string) {
  const dispatch = useAppDispatch();
  const summary = useAppSelector(state => state.summaries.byId[summaryId]);
  const topics = useAppSelector(state => {
    const topicIds = state.topics.bySummaryId[summaryId] || [];
    return topicIds.map(id => state.topics.byId[id]);
  });
  const loading = useAppSelector(state => state.summaries.loading);
  const error = useAppSelector(state => state.summaries.error);
  
  useEffect(() => {
    if (!summary && !loading && !error) {
      dispatch(fetchSummary(summaryId));
    }
  }, [summaryId, summary, loading, error, dispatch]);
  
  const saveSummary = useCallback(() => {
    dispatch(saveSummaryAction(summaryId));
  }, [summaryId, dispatch]);
  
  return {
    summary,
    topics,
    loading,
    error,
    saveSummary
  };
}
```

## Component Examples

### SummaryCard Component

```tsx
interface SummaryCardProps {
  summaryId: string;
  onClick?: () => void;
  compact?: boolean;
}

export const SummaryCard: React.FC<SummaryCardProps> = ({ 
  summaryId, 
  onClick,
  compact = false
}) => {
  const { summary, topics, loading } = useSummary(summaryId);
  
  if (loading) {
    return <SummaryCardSkeleton />;
  }
  
  if (!summary) {
    return null;
  }
  
  const mainTopics = topics
    .sort((a, b) => b.relevance - a.relevance)
    .slice(0, compact ? 2 : 3);
  
  return (
    <div 
      className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow"
      onClick={onClick}
    >
      <div className="flex items-start gap-4">
        <img 
          src={summary.video.thumbnailUrl} 
          alt={summary.video.title}
          className="w-24 h-16 rounded object-cover"
        />
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white truncate">
            {summary.video.title}
          </h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {summary.video.channelTitle} • {formatDistance(new Date(summary.video.publishedAt), new Date())}
          </p>
          
          {!compact && (
            <p className="mt-2 text-sm text-gray-700 dark:text-gray-300 line-clamp-2">
              {summary.content.substring(0, 120)}...
            </p>
          )}
          
          <div className="mt-2 flex flex-wrap gap-1">
            {mainTopics.map(topic => (
              <TopicTag 
                key={topic.id} 
                name={topic.name} 
                relevance={topic.relevance} 
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Topic Tag Component
interface TopicTagProps {
  name: string;
  relevance: number;
}

const TopicTag: React.FC<TopicTagProps> = ({ name, relevance }) => {
  // Color based on relevance
  const getColor = () => {
    if (relevance > 0.8) return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
    if (relevance > 0.5) return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
    return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
  };
  
  return (
    <span className={`text-xs px-2 py-1 rounded-full ${getColor()}`}>
      {name}
    </span>
  );
};
```

### Dashboard Component

```tsx
export const DashboardPage: React.FC = () => {
  const dispatch = useAppDispatch();
  const videos = useAppSelector(state => state.videos.items);
  const loading = useAppSelector(state => state.videos.loading);
  const filters = useAppSelector(state => state.videos.filters);
  const pagination = useAppSelector(state => state.videos.pagination);
  
  const [searchInput, setSearchInput] = useState(filters.search);
  
  useEffect(() => {
    dispatch(fetchVideos({ page: 1 }));
  }, [dispatch]);
  
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    dispatch(updateFilters({ search: searchInput }));
    dispatch(fetchVideos({ page: 1 }));
  };
  
  const handleLoadMore = () => {
    dispatch(fetchVideos({ page: pagination.page + 1 }));
  };
  
  const handleVideoClick = (videoId: string) => {
    // Navigate to video summary
    navigate(`/summaries/${videoId}`);
  };
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
        Your YouTube Feed Summaries
      </h1>
      
      {/* Search and filters */}
      <div className="mb-6">
        <form onSubmit={handleSearch} className="flex gap-2">
          <input
            type="text"
            value={searchInput}
            onChange={e => setSearchInput(e.target.value)}
            placeholder="Search summaries..."
            className="flex-1 px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
          />
          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Search
          </button>
        </form>
        
        <div className="mt-4 flex flex-wrap gap-2">
          <FilterDropdown
            label="Channel"
            options={[...]}
            value={filters.channel}
            onChange={channel => {
              dispatch(updateFilters({ channel }));
              dispatch(fetchVideos({ page: 1 }));
            }}
          />
          
          <DateRangePicker
            startDate={filters.dateRange.start}
            endDate={filters.dateRange.end}
            onChange={dateRange => {
              dispatch(updateFilters({ dateRange }));
              dispatch(fetchVideos({ page: 1 }));
            }}
          />
          
          <TopicFilter
            selectedTopics={filters.topics}
            onChange={topics => {
              dispatch(updateFilters({ topics }));
              dispatch(fetchVideos({ page: 1 }));
            }}
          />
        </div>
      </div>
      
      {/* Video grid */}
      {loading && videos.length === 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <SummaryCardSkeleton key={i} />
          ))}
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {videos.map(video => (
              <SummaryCard
                key={video.id}
                summaryId={video.summaryId}
                onClick={() => handleVideoClick(video.id)}
              />
            ))}
          </div>
          
          {pagination.page < pagination.totalPages && (
            <div className="mt-8 text-center">
              <button
                onClick={handleLoadMore}
                disabled={loading}
                className="px-6 py-2 bg-gray-200 dark:bg-gray-700 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 dark:text-white"
              >
                {loading ? 'Loading...' : 'Load More'}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};
```

### Video Summary Detail Page

```tsx
export const VideoSummaryPage: React.FC = () => {
  const { summaryId } = useParams<{ summaryId: string }>();
  const { summary, topics, loading, error } = useSummary(summaryId || '');
  const [activeTab, setActiveTab] = useState<'summary' | 'topics'>('summary');
  
  if (loading) {
    return <SummaryDetailSkeleton />;
  }
  
  if (error || !summary) {
    return (
      <div className="text-center py-12">
        <h3 className="text-xl font-semibold text-red-600 dark:text-red-400">
          {error || 'Summary not found'}
        </h3>
        <button
          onClick={() => navigate(-1)}
          className="mt-4 px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded-lg"
        >
          Go Back
        </button>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto px-4 py-8 max-w-5xl">
      <div className="mb-6">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400"
        >
          <ArrowLeftIcon className="w-4 h-4 mr-1" />
          Back to Dashboard
        </button>
      </div>
      
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
        {/* Video player */}
        <div className="aspect-w-16 aspect-h-9">
          <iframe
            src={`https://www.youtube.com/embed/${summary.video.youtubeId}`}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
            className="w-full h-full"
          ></iframe>
        </div>
        
        <div className="p-6">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            {summary.video.title}
          </h1>
          
          <div className="flex items-center text-gray-600 dark:text-gray-400 mb-6">
            <span className="mr-4">{summary.video.channelTitle}</span>
            <span>{format(new Date(summary.video.publishedAt), 'MMM d, yyyy')}</span>
          </div>
          
          {/* Tab navigation */}
          <div className="border-b border-gray-200 dark:border-gray-700 mb-6">
            <nav className="flex space-x-8">
              <button
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'summary'
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400'
                }`}
                onClick={() => setActiveTab('summary')}
              >
                Summary
              </button>
              <button
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'topics'
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400'
                }`}
                onClick={() => setActiveTab('topics')}
              >
                Topics ({topics.length})
              </button>
            </nav>
          </div>
          
          {/* Tab content */}
          {activeTab === 'summary' ? (
            <div className="prose dark:prose-invert max-w-none">
              {summary.content.split('\n\n').map((paragraph, index) => (
                <p key={index}>{paragraph}</p>
              ))}
            </div>
          ) : (
            <div className="space-y-6">
              {topics
                .sort((a, b) => b.relevance - a.relevance)
                .map(topic => (
                  <TopicCard
                    key={topic.id}
                    topic={topic}
                    onTimestampClick={(time) => {
                      // Logic to seek video player to timestamp
                    }}
                  />
                ))}
            </div>
          )}
          
          {/* Actions */}
          <div className="mt-8 flex flex-wrap gap-4">
            <button className="flex items-center px-4 py-2 bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-800">
              <BookmarkIcon className="w-4 h-4 mr-2" />
              Save Summary
            </button>
            
            <button className="flex items-center px-4 py-2 bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200 rounded-lg hover:bg-purple-200 dark:hover:bg-purple-800">
              <NotebookIcon className="w-4 h-4 mr-2" />
              Open in Notebook
            </button>
            
            <button className="flex items-center px-4 py-2 bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600">
              <ShareIcon className="w-4 h-4 mr-2" />
              Share
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
```

## Authentication Flow

The frontend implements the YouTube OAuth authentication flow:

```typescript
export const AuthService = {
  // Start the authentication process
  initiateAuth: async (): Promise<void> => {
    // Redirect to backend auth endpoint
    window.location.href = `${API_BASE_URL}/auth/youtube/login`;
  },
  
  // Handle the callback from YouTube OAuth
  handleAuthCallback: async (code: string): Promise<User> => {
    const response = await axiosInstance.post('/auth/youtube/callback', { code });
    
    // Store token
    localStorage.setItem('authToken', response.data.token);
    
    // Set default Authorization header for future requests
    axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${response.data.token}`;
    
    return response.data.user;
  },
  
  // Check if user is authenticated
  checkAuth: async (): Promise<User | null> => {
    const token = localStorage.getItem('authToken');
    
    if (!token) {
      return null;
    }
    
    try {
      axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      const response = await axiosInstance.get('/auth/me');
      return response.data;
    } catch (error) {
      // Clear invalid token
      localStorage.removeItem('authToken');
      return null;
    }
  },
  
  // Log out user
  logout: async (): Promise<void> => {
    localStorage.removeItem('authToken');
    axiosInstance.defaults.headers.common['Authorization'] = '';
  }
};
```

## Responsive Design

The application uses Tailwind CSS for responsive design, implementing:

1. **Mobile-first approach**: Base styles designed for mobile devices
2. **Responsive breakpoints**: Specific adjustments for different screen sizes
3. **Flexible layouts**: Using Flexbox and Grid for adaptable components
4. **Component adaptations**: Components that change their display mode based on screen size

Example responsive component:

```tsx
export const SummaryLayout: React.FC<SummaryLayoutProps> = ({ 
  children, 
  sidebar 
}) => {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex flex-col lg:flex-row gap-8">
        <div className="w-full lg:w-2/3">
          {children}
        </div>
        
        <div className="w-full lg:w-1/3">
          <div className="sticky top-8">
            {sidebar}
          </div>
        </div>
      </div>
    </div>
  );
};
```

## Theme Support

The application supports light and dark modes:

```typescript
export const ThemeContext = createContext<{
  theme: 'light' | 'dark' | 'system';
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
}>({
  theme: 'system',
  setTheme: () => {},
});

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setThemeState] = useState<'light' | 'dark' | 'system'>(
    () => (localStorage.getItem('theme') as any) || 'system'
  );
  
  const setTheme = useCallback((newTheme: 'light' | 'dark' | 'system') => {
    setThemeState(newTheme);
    localStorage.setItem('theme', newTheme);
    
    if (newTheme === 'system') {
      if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    } else if (newTheme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, []);
  
  useEffect(() => {
    setTheme(theme);
    
    if (theme === 'system') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const handleChange = (e: MediaQueryListEvent) => {
        if (e.matches) {
          document.documentElement.classList.add('dark');
        } else {
          document.documentElement.classList.remove('dark');
        }
      };
      
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    }
  }, [theme, setTheme]);
  
  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};
```

*Author: Bruno Santos*