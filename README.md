# AI Medical Assistant

## Overview

This project is an AI-powered Medical Assistant designed to provide information based on a knowledge base of medical documents. It leverages Retrieval-Augmented Generation (RAG) to answer user queries and includes robust session management with user-specific chat histories. The system is built using FastAPI for the backend and a simple HTML/JavaScript frontend.

## Features

### Core AI Functionality

*   **Retrieval-Augmented Generation (RAG)**: Answers medical questions by searching and synthesizing information from a provided knowledge base (PDF, TXT, CSV files).
*   **Conversational History**: Maintains chat history for each session, allowing for follow-up questions and context-aware responses.
*   **Statistical Analysis**: Can answer structured-data questions (e.g., "how many patients have diabetes?") by routing them to an analytics layer.

### User and Session Management

*   **User ID Privacy**: Each user has a unique ID, ensuring that conversations and sessions are isolated and private. Users can only access their own chat histories.
*   **Login/Logout System**: A simple login screen allows users to enter their User ID. This ID is stored locally in the browser's `localStorage`.
*   **Session Creation**: Users can create new chat sessions.
*   **Session Switching**: Users can switch between existing chat sessions, loading previous conversations.
*   **Session Deletion**: Individual chat sessions can be deleted, and the system also supports clearing all sessions.
*   **Persistent History**: Chat histories are stored in `data/chat_history.json` and loaded on application startup.

### Technical Stack

*   **Backend**: FastAPI (Python)
*   **Frontend**: HTML, CSS, JavaScript
*   **RAG Framework**: LangChain Ecosystem (langchain, langchain-core, langchain-community, langchain-classic)
*   **LLM Integration**: Groq API (via `langchain-groq`)
*   **Embeddings & Vector Store**: Sentence Transformers, FAISS
*   **Document Processing**: PyPDF, Pandas

## Project Structure

```
AI-Medical-Assistant-Enhanced-Analytics-Improved/
├── .env.example
├── app.py                      # Main FastAPI application
├── data/                       # Medical documents (PDF, TXT, CSV) and chat_history.json
│   ├── chat_history.json       # Persistent chat history storage
│   └── ... (other data files)
├── faiss_index/                # FAISS vector store index files
│   ├── index.faiss
│   └── index.pkl
├── README.md                   # Project README (this file)
├── requirements.txt            # Python dependencies
├── run.py                      # Script to run the FastAPI application
├── SESSION_MANAGEMENT.md       # Documentation for session management features
├── src/                        # Source code for RAG components
│   ├── analytics.py            # Patient analytics for structured queries
│   ├── config.py               # Configuration settings
│   ├── llm.py                  # LLM manager
│   ├── preprocessing.py        # Data preprocessing for RAG
│   ├── prompts.py              # LLM prompts
│   ├── rag.py                  # RAG orchestrator
│   └── retriever.py            # Document retriever
├── static/                     # Main CSS file (should be moved to static/)                     
│   └── style.css               # (CSS, JS, images) - currently contains style.css
├── templates/                  # HTML templates
│   ├── index.html              # Main UI template
│   └── index_old.html          # Old UI template (pre-user ID feature)
└── USER_ID_FEATURE.md          # Documentation for User ID privacy feature
```

## Setup and Installation

### 1. Clone the Repository

```bash
git clone <repository_url>
cd AI-Medical-Assistant-Enhanced-Analytics-Improved
```

### 2. Create a Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Key

Create a `.env` file in the project root based on `.env.example` and add your Groq API key:

```
GROQ_API_KEY="your_groq_api_key_here"
GROQ_MODEL="openai/gpt-oss-120b" # Or your preferred Groq model
```

### 5. Prepare Data

Place your medical documents (PDF, TXT, CSV) in the `data/` directory. The RAG system will process these files to build its knowledge base.

## Usage

### 1. Run the Application

```bash
python run.py
```

The application will start, typically accessible at `http://127.0.0.1:8000`.

### 2. Login

Upon first access, you will be prompted to enter a User ID. This ID will be stored in your browser's `localStorage`.

### 3. Interact with the Assistant

*   Type your medical questions into the chat input.
*   Create new sessions, switch between them, or delete them using the sidebar controls.

## API Endpoints

The backend exposes the following API endpoints:

| Endpoint                       | Method | Description                                     | Authentication (User ID) |
| :----------------------------- | :----- | :---------------------------------------------- | :----------------------- |
| `/`                            | GET    | Serves the main HTML application                | Optional                 |
| `/api/session`                 | POST   | Creates a new chat session                      | Required                 |
| `/api/session/{session_id}/switch` | POST   | Switches to an existing session                 | Required                 |
| `/api/session/{session_id}`    | GET    | Retrieves information about a specific session  | Required                 |
| `/api/sessions`                | GET    | Lists all sessions for the current user         | Required                 |
| `/api/history`                 | GET    | Retrieves chat history for the current user     | Required                 |
| `/api/history/{session_id}`    | GET    | Retrieves a specific chat session's messages    | Required                 |
| `/api/history`                 | PUT    | Renames a chat session                          | Required                 |
| `/api/history/{session_id}`    | DELETE | Deletes a specific chat session                 | Required                 |
| `/api/history`                 | DELETE | Clears all chat sessions for the current user   | Required                 |
| `/api/chat`                    | POST   | Sends a message to the AI assistant             | Required                 |
| `/api/upload`                  | POST   | Uploads new medical documents                   | N/A                      |
| `/api/rebuild`                 | POST   | Rebuilds the RAG knowledge base                 | N/A                      |
| `/api/export`                  | GET    | Exports the entire chat history                 | N/A                      |
| `/api/status`                  | GET    | Provides application status and metrics         | N/A                      |
| `/health`                      | GET    | Health check endpoint                           | N/A                      |

## Security Considerations

*   **User ID System**: Provides data isolation for chat histories per user. However, it is a simple ID-based system without strong authentication (e.g., passwords).
*   **Production Use**: For production environments, it is highly recommended to implement a robust authentication system (e.g., OAuth, JWT) and ensure HTTPS is used for all communications.

## Future Enhancements

*   Implement a more robust authentication system (e.g., JWT).
*   Migrate session storage from JSON files to a proper database.
*   Add an admin panel for user and session management.
*   Encrypt stored chat data.
*   Implement automatic backups for chat history.
*   Add features for session renaming, export/import, sharing, and archiving.

## Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests.

## License

This project is open-source and available under the MIT License.


---
