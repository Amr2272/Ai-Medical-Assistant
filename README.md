# 🩺 AI Medical Assistant

**A production-style Retrieval-Augmented Generation (RAG) system for medical question-answering**, built with LangChain, Groq LLMs, FAISS, and Streamlit — combining semantic document search with a safe text-to-pandas analytics layer for exact, grounded answers.

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/LangChain-RAG-1C3C3C?logo=langchain&logoColor=white" alt="LangChain">
  <img src="https://img.shields.io/badge/Groq-LLM%20Inference-F55036" alt="Groq">
  <img src="https://img.shields.io/badge/FAISS-Vector%20Search-00A0D2" alt="FAISS">
  <img src="https://img.shields.io/badge/Streamlit-UI-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/License-Educational-lightgrey" alt="License">
</p>

---

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

pip install -r requirements.txt
```

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

```bash
python run.py
```

Or directly with Streamlit:

```bash
streamlit run app.py --server.port 8501
```

The app will open at [http://localhost:8501](http://localhost:8501).

---

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

---

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

---

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

---

## 📄 License

This project is provided for educational and research purposes. Ensure you comply with all applicable regulations when handling medical data.

---

## 🙏 Acknowledgements

Built with RAG, LangChain & Groq.

> **AI Medical Assistant v1.1** — *Not a substitute for professional medical advice.*
