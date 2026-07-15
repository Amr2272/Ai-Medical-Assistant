# AI Medical Assistant

<<<<<<< HEAD
## Overview

This project is an AI-powered Medical Assistant designed to provide information based on a knowledge base of medical documents. It leverages Retrieval-Augmented Generation (RAG) to answer user queries and includes robust session management with user-specific chat histories. The system is built using FastAPI for the backend and a simple HTML/JavaScript frontend.
=======
**A production-style Retrieval-Augmented Generation (RAG) system for medical question-answering**, built with LangChain, Groq LLMs, FAISS, and Streamlit — combining semantic document search with a safe text-to-pandas analytics layer for exact, grounded answers.

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/LangChain-RAG-1C3C3C?logo=langchain&logoColor=white" alt="LangChain">
  <img src="https://img.shields.io/badge/Groq-LLM%20Inference-F55036" alt="Groq">
  <img src="https://img.shields.io/badge/FAISS-Vector%20Search-00A0D2" alt="FAISS">
  <img src="https://img.shields.io/badge/Streamlit-UI-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/License-Educational-lightgrey" alt="License">
</p>
>>>>>>> bd1c4fb27d994cc1782005ee6802e51e51158d0c

## Features

<<<<<<< HEAD
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
=======
## 📌 Overview

The assistant answers two distinct kinds of medical questions accurately:

- **Open-ended / semantic questions** — *"What are the symptoms of COVID-19?"* — answered via retrieval-augmented generation grounded strictly in your source documents.
- **Structured / statistical questions** — *"How many patients have diabetes?"* — routed to a sandboxed pandas-execution layer so numbers are always exact, never hallucinated.

A query router automatically decides which path to take, so users can move fluidly between the two without changing how they ask questions.

---

## 📖 Table of Contents

- [Features](#-features)
- [Architecture](#️-architecture)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [Configuration](#️-configuration)
- [How It Works](#-how-it-works)
- [Safety & Limitations](#-safety--limitations)
- [Example Questions](#-example-questions)
- [Troubleshooting](#️-troubleshooting)
- [Tech Stack](#-tech-stack)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgements](#-acknowledgements)

---

## ✨ Features

| Capability | Description |
|---|---|
| 🔍 **Hybrid Retrieval** | Semantic search over PDFs/TXT/CSV using FAISS + HuggingFace embeddings |
| 🧠 **History-Aware RAG** | Follow-up questions are automatically contextualized using chat history |
| 📊 **Text-to-Pandas Analytics** | Statistical/structured questions are routed to a safe pandas-execution layer for exact answers |
| 🛡️ **Safe Expression Sandbox** | Generated pandas code is validated via AST against an allow-list before execution |
| 💾 **Persistent Chat History** | Conversations are saved to JSON and restored on restart |
| 👥 **Multi-Session Support** | Switch between separate user contexts, each with its own chats |
| 🎨 **Light & Dark Themes** | Seamless theme detection and styling for both modes |
| ⚡ **FAISS Index Caching** | Embeddings are cached on disk — fast startup on subsequent runs |
| 🌐 **Bilingual Keywords** | Statistical query detection supports both English and Arabic keywords |
| ⚠️ **Medical Disclaimer** | Built-in disclaimer banner reminding users this is not professional medical advice |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     Streamlit UI (app.py)                 │
│   Chat interface · Sidebar · Session management · Theme   │
└────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────┐
│                  RAGOrchestrator (rag.py)                 │
│                                                             │
│   ┌─────────────────┐     ┌──────────────────────────┐    │
│   │  Query Router    │────▶│  PatientAnalytics        │    │
│   │ (is_statistical) │     │  (text-to-pandas, safe)   │    │
│   └────────┬─────────┘     └──────────────────────────┘    │
│            │ no match / can't answer                       │
│            ▼                                                │
│   ┌─────────────────────────────────────────────────┐      │
│   │  History-Aware Retriever  →  Stuff Documents QA  │      │
│   │  (contextualize prompt)     (QA prompt + LLM)    │      │
│   └─────────────────────────────────────────────────┘      │
└────────────────────────────┬─────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐   ┌──────────────────┐   ┌──────────────────┐
│  LLMManager   │   │ RetrieverManager │   │ DataPreprocessor │
│  (Groq API)   │   │ (FAISS + HF Emb) │   │ (PDF/TXT/CSV)    │
└──────────────┘   └──────────────────┘   └──────────────────┘
```

---

## 📁 Project Structure

```
.
├── app.py                  # Streamlit UI + persistent chat history
├── run.py                  # Entry point — launches the Streamlit server
├── data/                   # Place your PDF / TXT / CSV files here
│   └── healthcare_dataset_cleaned.csv   # (optional) patient records for analytics
├── faiss_index/            # Auto-generated FAISS cache (created on first run)
├── src/
│   ├── __init__.py         # Package exports
│   ├── config.py           # All configuration constants
│   ├── llm.py              # LLMManager — Groq ChatGroq singleton
│   ├── retriever.py        # RetrieverManager — FAISS + embeddings (with caching)
│   ├── preprocessing.py    # DataPreprocessor — loads & chunks PDFs/TXT/CSV
│   ├── prompts.py          # Contextualization & QA prompt templates
│   ├── analytics.py        # PatientAnalytics — text-to-pandas with safety checks
│   └── rag.py              # RAGOrchestrator — ties everything together
└── .env                     # API keys (GROQ_API_KEY, GROQ_MODEL)
```

---

## 🚀 Quick Start

### 1. Prerequisites

- **Python 3.10+**
- A free **Groq API key** → get one at [console.groq.com/keys](https://console.groq.com/keys)

### 2. Clone & Install

```bash
git clone <your-repo-url>
cd ai-medical-assistant
>>>>>>> bd1c4fb27d994cc1782005ee6802e51e51158d0c

### 2. Create a Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

<<<<<<< HEAD
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
=======
> If you don't have a `requirements.txt`, the main dependencies are:
> ```text
> streamlit
> langchain
> langchain-groq
> langchain-huggingface
> langchain-community
> faiss-cpu
> sentence-transformers
> torch
> pypdf
> pandas
> tabulate
> python-dotenv
> ```

### 3. Configure Environment

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_key_here
GROQ_MODEL=openai/gpt-oss-120b
```

### 4. Add Your Data

Place your documents in the `data/` directory:

```
data/
├── medical_guide.pdf
├── covid_notes.txt
└── healthcare_dataset_cleaned.csv   # optional — enables analytics layer
```

Supported formats:
- **PDF** — loaded via `PyPDFLoader`
- **TXT** — loaded via `TextLoader`
- **CSV** — patient records (only ingested into RAG if `INCLUDE_CSV_IN_RAG=True` in `config.py`; otherwise handled exclusively by the analytics layer)

### 5. Run
>>>>>>> bd1c4fb27d994cc1782005ee6802e51e51158d0c

```bash
python run.py
```

<<<<<<< HEAD
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
=======
Or directly with Streamlit:

```bash
streamlit run app.py --server.port 8501
```

The app will open at [http://localhost:8501](http://localhost:8501).
>>>>>>> bd1c4fb27d994cc1782005ee6802e51e51158d0c

## Future Enhancements

<<<<<<< HEAD
*   Implement a more robust authentication system (e.g., JWT).
*   Migrate session storage from JSON files to a proper database.
*   Add an admin panel for user and session management.
*   Encrypt stored chat data.
*   Implement automatic backups for chat history.
*   Add features for session renaming, export/import, sharing, and archiving.

## Contributing
=======
## ⚙️ Configuration

All settings live in [`src/config.py`](src/config.py):

| Setting | Default | Description |
|---|---|---|
| `DATA_DIR` | `./data` | Directory containing source documents |
| `FAISS_INDEX_DIR` | `./faiss_index` | Where the cached FAISS index is stored |
| `PATIENT_CSV_PATH` | `./data/healthcare_dataset_cleaned.csv` | CSV used by the analytics layer |
| `INCLUDE_CSV_IN_RAG` | `False` | If `True`, patient records are also ingested into the vector store |
| `DEVICE` | auto (`cuda` if available, else `cpu`) | Compute device for embeddings |
| `LLM_MODEL` | `openai/gpt-oss-120b` | Groq model name (override via `GROQ_MODEL` env var) |
| `LLM_MAX_TOKENS` | `512` | Max generation tokens |
| `LLM_TEMPERATURE` | `0.5` | Sampling temperature |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | HuggingFace embedding model |
| `CHUNK_SIZE` | `1000` | Document chunk size (characters) |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks |
| `TOP_K_RESULTS` | `5` | Number of chunks retrieved per query |
| `SEARCH_TYPE` | `mmr` | FAISS search type (`similarity`, `mmr`, etc.) |
>>>>>>> bd1c4fb27d994cc1782005ee6802e51e51158d0c

Contributions are welcome! Please feel free to open issues or submit pull requests.

<<<<<<< HEAD
## License

This project is open-source and available under the MIT License.
=======
## 💬 How It Works

### 1. Document Ingestion
On first launch, `DataPreprocessor` loads all PDFs and TXT files from `data/`, splits them into chunks using `RecursiveCharacterTextSplitter`, and embeds them into a FAISS index. The index is cached to `faiss_index/` so subsequent startups skip re-embedding.

### 2. Query Routing
When you ask a question, `RAGOrchestrator.run()` first checks `PatientAnalytics.is_statistical_query()` — a heuristic that looks for keywords like *"how many"*, *"average"*, *"percentage"*, *"كام"*, *"عدد"*, etc.

- **Statistical query** → The LLM generates a single pandas expression, which is validated by an AST-based allow-list (no imports, no file I/O, no method calls on a blocklist like `to_csv`, `eval`, `query`). If safe, it's executed against the CSV and the result is formatted directly — keeping numbers exact.
- **Semantic query** → Falls through to the standard RAG chain: the question is contextualized using chat history, relevant chunks are retrieved from FAISS, and the LLM generates an answer grounded **only** in the retrieved context.

### 3. Conversation Memory
Each session maintains an `InMemoryChatMessageHistory`. When you reload a saved chat, `restore_rag_memory()` replays the message pairs into the LLM's memory so follow-up questions work correctly.

### 4. Persistent Chat History
All chats are serialized to `data/chat_history.json` (with `datetime` ISO encoding). The sidebar lets you:
- ➕ Start a new chat
- 🗑️ Delete a chat
- 🔑 Switch user sessions
- ♻️ Rebuild the knowledge base (clears FAISS cache)

---

## 🔒 Safety & Limitations

- **Medical Disclaimer**: This assistant is **not a substitute for professional medical advice**. Always consult a licensed physician.
- **Grounded Answers**: The QA prompt explicitly forbids the LLM from using external knowledge or hallucinating. If the answer isn't in the retrieved context, the assistant says so.
- **Sandboxed Analytics**: Generated pandas expressions are parsed with `ast` and rejected if they contain imports, assignments, function definitions, file/network operations, or calls to dangerous methods.
- **No External Data**: The system only answers based on documents you place in `data/`.

---

## 🧪 Example Questions

**Semantic (RAG):**
- *"What are the symptoms of COVID-19?"*
- *"What medications are used for hypertension?"*
- *"What is the treatment for severe COVID-19?"*
- *"What are the risk factors for heart disease?"*

**Structured (Analytics):**
- *"How many patients have diabetes?"*
- *"What is the average age of patients with cancer?"*
- *"Which doctor treats the most patients?"*
- *"Show me patients with cancer admitted urgently"*

---

## 🛠️ Troubleshooting

| Issue | Fix |
|---|---|
| `GROQ_API_KEY is not set` | Create a `.env` file with your key (see [Configure Environment](#3-configure-environment)) |
| Slow first startup | Expected — embeddings are being computed. Subsequent runs use the FAISS cache. |
| `No cached FAISS index found and no documents were provided` | Add at least one PDF or TXT file to `data/` |
| Analytics layer disabled | Ensure `data/healthcare_dataset_cleaned.csv` exists with the expected columns |
| Want to rebuild the index | Click **♻️ Rebuild Knowledge Base** in the sidebar, or delete the `faiss_index/` folder |
>>>>>>> bd1c4fb27d994cc1782005ee6802e51e51158d0c

## Contact

<<<<<<< HEAD
For any questions or feedback, please contact [Your Name/Email/GitHub Profile].

---
=======
## 📦 Tech Stack

- **[Streamlit](https://streamlit.io/)** — Web UI
- **[LangChain](https://www.langchain.com/)** — RAG orchestration
- **[Groq](https://groq.com/)** — Fast LLM inference
- **[FAISS](https://github.com/facebookresearch/faiss)** — Vector search
- **[HuggingFace Transformers](https://huggingface.co/)** — Embeddings
- **[PyTorch](https://pytorch.org/)** — Backend for embeddings
- **[Pandas](https://pandas.pydata.org/)** — Structured data analytics

---

## 🗺️ Roadmap

- [ ] Add automated evaluation suite for retrieval quality
- [ ] Support additional document formats (DOCX, HTML)
- [ ] Add citation highlighting in the UI for retrieved sources
- [ ] Dockerize the app for one-command deployment

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request