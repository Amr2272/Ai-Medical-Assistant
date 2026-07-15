# Session Management Features

## Overview

The AI Medical Assistant now includes comprehensive session management capabilities, allowing users to create, switch between, and delete conversation sessions. Each session maintains its own chat history and context.

## Features

### 1. Create Session
- **Endpoint**: `POST /api/session`
- **Description**: Creates a new conversation session
- **Response**: 
  ```json
  {
    "success": true,
    "session_id": "abc123def456...",
    "message": "New session created successfully"
  }
  ```

### 2. Switch Session
- **Endpoint**: `POST /api/session/{session_id}/switch`
- **Description**: Switches to an existing session
- **Response**:
  ```json
  {
    "success": true,
    "session_id": "abc123def456...",
    "title": "Chat Title",
    "message_count": 5
  }
  ```

### 3. Get Session Info
- **Endpoint**: `GET /api/session/{session_id}`
- **Description**: Retrieves information about a specific session
- **Response**:
  ```json
  {
    "success": true,
    "session_id": "abc123def456...",
    "title": "Chat Title",
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:45:00",
    "message_count": 5
  }
  ```

### 4. List All Sessions
- **Endpoint**: `GET /api/sessions`
- **Description**: Lists all available sessions with metadata
- **Response**:
  ```json
  {
    "success": true,
    "total": 3,
    "sessions": [
      {
        "session_id": "abc123def456...",
        "title": "Medical Question 1",
        "created_at": "2024-01-15T10:30:00",
        "updated_at": "2024-01-15T10:45:00",
        "message_count": 5
      },
      ...
    ]
  }
  ```

### 5. Delete Session
- **Endpoint**: `DELETE /api/history/{session_id}`
- **Description**: Deletes a specific session and its history
- **Response**:
  ```json
  {
    "success": true,
    "message": "Session 'Chat Title' deleted successfully"
  }
  ```

### 6. Delete All Sessions
- **Endpoint**: `DELETE /api/history`
- **Description**: Deletes all sessions
- **Response**:
  ```json
  {
    "success": true,
    "message": "Deleted 3 session(s) successfully"
  }
  ```

## Frontend UI Components

### Session Badge
- Displays the current active session ID (first 8 characters)
- Located at the top of the sidebar
- Updates dynamically when switching sessions

### Session Management Panel
- **Location**: Sidebar under "Session Management" expandable section
- **Features**:
  - Create new session button
  - Active session counter
  - List of all sessions with:
    - Session title
    - Session ID (shortened)
    - Message count
    - Delete button for each session
  - Click on any session to switch to it

### Session List in Management Panel
- Shows all active sessions
- Highlights the currently active session
- Each session item shows:
  - Title (auto-generated from first user message)
  - Short session ID
  - Message count
  - Delete button (appears on hover)

## Frontend Functions

### `createSession()`
Creates a new session on the backend and returns the session ID.

### `createNewSession()`
Creates a new session and immediately switches to it, clearing the chat view and showing the welcome screen.

### `switchSession(sessionId)`
Switches to an existing session on the backend.

### `updateSessionBadge()`
Updates the session badge display with the current session ID.

### `loadSessionsList()`
Fetches all sessions from the backend and renders them in the session management panel.

### `deleteSessionFromList(sessionId)`
Deletes a session and updates the UI. If the deleted session was active, creates a new session.

## Session Lifecycle

1. **Creation**: When a user clicks "Create Session" or starts a new chat, a new session is created
2. **Active**: The session becomes active and displays in the session badge
3. **Persistence**: All messages are saved to the session history
4. **Switching**: User can switch between sessions, loading the previous chat history
5. **Deletion**: Sessions can be individually deleted or all cleared at once

## Session Metadata

Each session stores:
- **session_id**: Unique identifier (UUID hex)
- **title**: Auto-generated from the first user message (first 45 characters)
- **created_at**: ISO format timestamp
- **updated_at**: ISO format timestamp (updated on each message)
- **messages**: Array of message objects with role, content, and timestamp

## Backend Implementation

### Session Storage
- Sessions are stored in memory in the `history` dictionary
- Persisted to `data/chat_history.json` on disk
- Loaded from disk on application startup

### RAG Integration
- Each session maintains its own conversation history in the RAG system
- When a session is deleted, its history is cleared from both the file system and RAG system
- Session context is passed to the RAG chain for better question understanding

## Error Handling

- **Session Not Found**: Returns 404 error if trying to access non-existent session
- **Deletion Confirmation**: Frontend shows confirmation for bulk delete operations
- **Fallback**: If session deletion fails, user is notified via console

## Best Practices

1. **Session Naming**: Sessions are automatically named from the first user message
2. **Session Switching**: Switching sessions preserves the chat history
3. **Cleanup**: Regularly delete old sessions to manage storage
4. **Backup**: Session history is automatically saved to disk

## Future Enhancements

Potential improvements:
- Session renaming functionality
- Session export/import
- Session sharing
- Session search/filtering
- Session archiving
- Automatic session cleanup based on age
- Session tagging/categorization
