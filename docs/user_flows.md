# YouTube Video Summarizer - User Flows

This document describes the key user flows in the YouTube Video Summarizer application. These flows represent the primary user journeys and interactions through the system.

## 1. User Authentication Flow

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant AuthService
    participant YouTube
    
    User->>Frontend: Access Application
    Frontend->>AuthService: Check Auth Status
    alt User Not Authenticated
        Frontend->>User: Show Login Screen
        User->>Frontend: Click "Login with YouTube"
        Frontend->>AuthService: Request Auth URL
        AuthService->>Frontend: Return Auth URL
        Frontend->>YouTube: Redirect to YouTube OAuth
        YouTube->>User: Show Consent Screen
        User->>YouTube: Grant Permission
        YouTube->>Frontend: Redirect with Auth Code
        Frontend->>AuthService: Send Auth Code
        AuthService->>YouTube: Exchange Code for Tokens
        YouTube->>AuthService: Return Access/Refresh Tokens
        AuthService->>Frontend: Return Authentication Success
        Frontend->>User: Show Dashboard
    else User Already Authenticated
        AuthService->>Frontend: Return User Info
        Frontend->>User: Show Dashboard
    end
```

### Steps:

1. User accesses the application
2. System checks authentication status
3. If not authenticated:
   - User is shown login screen
   - User clicks "Login with YouTube" button
   - User is redirected to YouTube OAuth consent screen
   - User grants necessary permissions
   - User is redirected back to application with authorization code
   - System exchanges code for access and refresh tokens
   - System stores tokens securely
4. If already authenticated:
   - System loads user information
   - User is shown dashboard

## 2. Video Discovery and Import Flow

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant VideoService
    participant YouTubeAPI
    participant ProcessingService
    
    User->>Frontend: Access Discovery Tab
    Frontend->>VideoService: Request Subscription Videos
    VideoService->>YouTubeAPI: Fetch User's Subscriptions
    YouTubeAPI->>VideoService: Return Subscribed Channels
    VideoService->>YouTubeAPI: Fetch Recent Videos
    YouTubeAPI->>VideoService: Return Recent Videos
    VideoService->>Frontend: Return Videos List
    Frontend->>User: Display Videos Grid
    
    User->>Frontend: Select Videos to Import
    Frontend->>VideoService: Request Video Import
    VideoService->>ProcessingService: Queue Video Processing
    ProcessingService->>VideoService: Return Processing Status
    VideoService->>Frontend: Return Import Success
    Frontend->>User: Show Import Success Notification
```

### Steps:

1. User navigates to the Discovery tab
2. System fetches videos from user's YouTube subscriptions
3. System displays videos in a grid with key information
4. User selects one or more videos to import
5. User clicks "Import Selected" button
6. System queues selected videos for processing
7. System confirms successful import
8. Processing begins in the background

## 3. Video Processing Flow (Background)

```mermaid
flowchart TD
    A[Video Queued] --> B[Extract Video Metadata]
    B --> C[Extract Transcript]
    
    C -->|Transcript Available| D[Generate Summary]
    C -->|No Transcript| E[Use Fallback Transcription]
    E --> D
    
    D --> F[Extract Topics]
    F --> G[Update Video Status]
    G --> H[Send Notification]
```

### Steps:

1. Video is queued for processing
2. System extracts video metadata from YouTube API
3. System attempts to extract transcript from YouTube captions
4. If captions not available, system uses fallback transcription method
5. System generates summary using AI provider
6. System extracts topics from summary
7. System marks video as processed
8. System sends notification of completion to user

## 4. Dashboard and Summary Viewing Flow

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant SummaryService
    participant VideoService
    participant TopicsService
    
    User->>Frontend: Access Dashboard
    Frontend->>SummaryService: Request Recent Summaries
    SummaryService->>Frontend: Return Recent Summaries
    Frontend->>TopicsService: Request Popular Topics
    TopicsService->>Frontend: Return Popular Topics
    Frontend->>User: Display Dashboard
    
    User->>Frontend: Click on Summary
    Frontend->>SummaryService: Get Full Summary
    SummaryService->>Frontend: Return Full Summary
    Frontend->>VideoService: Get Video Details
    VideoService->>Frontend: Return Video Details
    Frontend->>TopicsService: Get Topics for Summary
    TopicsService->>Frontend: Return Topics
    Frontend->>User: Display Summary Page
    
    User->>Frontend: Click "Save" Button
    Frontend->>SummaryService: Save Summary for User
    SummaryService->>Frontend: Confirm Save
    Frontend->>User: Show Save Confirmation
```

### Steps:

1. User accesses the dashboard
2. System loads recent summaries and popular topics
3. User clicks on a summary card
4. System loads detailed summary information
5. System loads video details
6. System loads topics for the summary
7. System displays the full summary page
8. User can save the summary for later reference
9. User can add notes or tags to saved summaries

## 5. Topic Exploration Flow

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant TopicsService
    participant SummaryService
    
    User->>Frontend: Click on Topic
    Frontend->>TopicsService: Get Topic Details
    TopicsService->>Frontend: Return Topic Details
    Frontend->>TopicsService: Get Related Topics
    TopicsService->>Frontend: Return Related Topics
    Frontend->>SummaryService: Get Summaries by Topic
    SummaryService->>Frontend: Return Matching Summaries
    Frontend->>User: Display Topic Page
    
    User->>Frontend: Click on Related Topic
    Frontend->>TopicsService: Get New Topic Details
    TopicsService->>Frontend: Return New Topic Details
    Frontend->>SummaryService: Get Summaries for New Topic
    SummaryService->>Frontend: Return Matching Summaries
    Frontend->>User: Update Topic Page
```

### Steps:

1. User clicks on a topic tag
2. System loads detailed topic information
3. System loads related topics
4. System loads summaries associated with the topic
5. System displays topic exploration page
6. User can click on related topics to explore further
7. System updates the displayed summaries when topic changes

## 6. Search Flow

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant SearchService
    participant SummaryService
    participant TranscriptService
    
    User->>Frontend: Enter Search Query
    Frontend->>SearchService: Submit Search
    SearchService->>SummaryService: Search in Summaries
    SummaryService->>SearchService: Return Summary Matches
    SearchService->>TranscriptService: Search in Transcripts
    TranscriptService->>SearchService: Return Transcript Matches
    SearchService->>Frontend: Return Combined Results
    Frontend->>User: Display Search Results
    
    User->>Frontend: Apply Filters
    Frontend->>SearchService: Resubmit with Filters
    SearchService->>Frontend: Return Filtered Results
    Frontend->>User: Update Results Display
```

### Steps:

1. User enters a search query
2. System searches across summaries and transcripts
3. System returns combined search results
4. User can apply filters (topics, channels, dates)
5. System updates results based on filters
6. User can click on a result to view the full summary

## 7. User Preferences Flow

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant UserService
    
    User->>Frontend: Access Settings Page
    Frontend->>UserService: Get User Preferences
    UserService->>Frontend: Return Current Preferences
    Frontend->>User: Display Settings Form
    
    User->>Frontend: Update Preferences
    Frontend->>UserService: Save Updated Preferences
    UserService->>Frontend: Confirm Update
    Frontend->>User: Show Confirmation
```

### Steps:

1. User navigates to settings page
2. System loads current user preferences
3. User updates preferences (summary length, language, etc.)
4. User clicks "Save" button
5. System updates user preferences
6. System confirms successful update

## 8. AI Processing Feedback Flow

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant SummaryService
    participant AIService
    
    User->>Frontend: Rate Summary Quality
    Frontend->>SummaryService: Submit Rating
    SummaryService->>AIService: Record Feedback
    AIService->>SummaryService: Confirm Feedback Saved
    SummaryService->>Frontend: Confirm Feedback Recorded
    Frontend->>User: Show Confirmation
    
    alt User Requests Regeneration
        User->>Frontend: Click "Regenerate Summary"
        Frontend->>SummaryService: Request Regeneration
        SummaryService->>AIService: Request New Generation
        AIService->>SummaryService: Return New Summary
        SummaryService->>Frontend: Return Updated Summary
        Frontend->>User: Display New Summary
    end
```

### Steps:

1. User rates summary quality (thumbs up/down)
2. System records feedback for AI improvement
3. If user is unhappy with summary:
   - User can request regeneration
   - System generates new summary with different parameters
   - System displays updated summary
4. System uses feedback to improve future summaries

## 9. Export and Sharing Flow

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant ExportService
    participant SharingService
    
    User->>Frontend: Select Summary to Export
    Frontend->>User: Show Export Options
    
    alt Export to Notebook
        User->>Frontend: Select "Export to Notebook"
        Frontend->>ExportService: Request Notebook Export
        ExportService->>Frontend: Return Notebook Link
        Frontend->>User: Display Export Success with Link
    else Export as PDF
        User->>Frontend: Select "Export as PDF"
        Frontend->>ExportService: Request PDF Export
        ExportService->>Frontend: Return PDF Download
        Frontend->>User: Prompt to Download PDF
    else Share Link
        User->>Frontend: Select "Share Link"
        Frontend->>SharingService: Generate Sharing Link
        SharingService->>Frontend: Return Sharing URL
        Frontend->>User: Display Sharing Link
    end
```

### Steps:

1. User selects a summary to export or share
2. User chooses export format or sharing option
3. For notebook export:
   - System generates embeddable notebook with summary and video
   - System provides link to notebook
4. For PDF export:
   - System generates PDF document with summary
   - System prompts user to download PDF
5. For sharing:
   - System generates shareable link
   - User can copy link to clipboard

## 10. Account Management Flow

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant UserService
    participant AuthService
    
    User->>Frontend: Access Account Settings
    Frontend->>UserService: Get User Profile
    UserService->>Frontend: Return User Information
    Frontend->>User: Display Account Settings
    
    alt Update Profile
        User->>Frontend: Edit Profile Information
        Frontend->>UserService: Update Profile
        UserService->>Frontend: Confirm Update
        Frontend->>User: Show Success Message
    else Delete Account
        User->>Frontend: Request Account Deletion
        Frontend->>User: Request Confirmation
        User->>Frontend: Confirm Deletion
        Frontend->>UserService: Request Account Deletion
        UserService->>AuthService: Revoke YouTube Permissions
        UserService->>Frontend: Confirm Deletion
        Frontend->>User: Show Goodbye Message
    end
```

### Steps:

1. User accesses account settings
2. System displays current account information
3. For profile updates:
   - User edits profile information
   - System updates user profile
4. For account deletion:
   - User requests account deletion
   - System asks for confirmation
   - System revokes YouTube permissions
   - System deletes all user data
   - System confirms successful deletion

---

**Author**: Bruno Santos  
**Created**: April 29, 2025  
**Last Updated**: April 29, 2025
