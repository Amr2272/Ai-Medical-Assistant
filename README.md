# 🩺 AI Medical Assistant

A Retrieval-Augmented Generation (RAG) chatbot for medical Q&A, combining:
- **Document search** over medical PDFs/TXT files (COVID-19 info, CDC reports, etc.)
- **Structured analytics** over a patient records CSV — statistical questions
  (e.g. "how many patients have diabetes?") are answered by direct computation
  on the data, not by semantic search, so the numbers are always exact.

> ⚠️ **This is not a substitute for professional medical advice.** See the
> disclaimer shown in the app itself.

---

## 1. Requirements

- **Python 3.10+**
- **A HuggingFace account** (the LLM,llama-3.3-70b-versatile, is a *gated* model)
- **Hardware:**
  - **GPU strongly recommended** — the app will run on CPU but will be **very
    slow** (answers can take minutes).
  - If you don't have a suitable GPU, consider

---

## 2. Setup

### 2.1 Install dependencies

```bash
python -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate

pip install -r requirements.txt
```

If you have an NVIDIA GPU, make sure you have a CUDA-compatible build of
PyTorch installed (the default `pip install torch` from requirements.txt
usually picks the right one automatically, but if `torch.cuda.is_available()`
returns `False` on a machine with a GPU, reinstall PyTorch following the
instructions at https://pytorch.org/get-started/locally/).

### 2.2 Authenticate with HuggingFace

Mistral-7B-Instruct requires accepting its license and logging in:

1. Create a free account at https://huggingface.co
2. Request access to the model: https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3
3. Create an access token: https://huggingface.co/settings/tokens
4. Log in from the terminal:

```bash
huggingface-cli login
# paste your token when prompted
```

### 2.3 Add your data (already included)

The `data/` folder should contain:
- `healthcare_dataset_cleaned.csv` — patient records (used by the analytics layer)
- Any `.pdf` or `.txt` files you want the RAG system to search over

This project ships with sample data already in place. To add more sources,
just drop more `.pdf` or `.txt` files into `data/` and rebuild the index (see
below).

---

## 3. Running the app

```bash
python run.py
```

This starts a Streamlit server and opens the app at `http://localhost:8501`.

**First run:** the app will download the embedding model and the LLM
(several GB), then build a FAISS search index from the documents in `data/`.
This can take a while, especially on CPU.

**Subsequent runs** are much faster — the FAISS index is cached to disk
(`faiss_index/`) and loaded directly instead of being rebuilt.

If you add/change files in `data/`, click **"♻️ Rebuild Knowledge Base"** in
the app sidebar to refresh the index.

---

## 4. Project structure

```
.
├── app.py                  # Streamlit UI
├── run.py                  # Entry point (checks data/, launches Streamlit)
├── requirements.txt
├── data/                   # Your source documents + patient CSV
├── faiss_index/            # Auto-generated vector index cache (after first run)
└── src/
    ├── config.py           # Paths, model names, chunking/retrieval settings
    ├── llm.py               # Loads & quantizes the local LLM
    ├── retriever.py         # Embeddings + FAISS index (build/save/load)
    ├── preprocessing.py     # Loads & splits PDF/TXT documents
    ├── prompts.py            # System prompts for the RAG chain
    ├── analytics.py          # Text-to-pandas layer for statistical questions
    └── rag.py                 # Orchestrator: routes questions, runs the chains
```

---

## 5. How questions are answered

1. **Statistical questions** about the patient dataset ("كام مريض عنده سكر؟",
   "average age of cancer patients") → routed to `src/analytics.py`, which
   asks the LLM to generate a single pandas expression, validates it is safe,
   and executes it directly against the CSV. The number in the answer is
   always the real computed value, never guessed by the model.
2. **Everything else** (symptoms, definitions, document content) → goes
   through the standard RAG pipeline: retrieve relevant chunks from the
   FAISS index, then generate an answer grounded in that context.
3. If the analytics layer can't confidently answer, it automatically falls
   back to the RAG pipeline.

---

## 6. Known limitations

- **Chat history is in-memory only** — it's lost if the app restarts. For
  persistent history, swap `InMemoryChatMessageHistory` in `src/rag.py` for
  a database-backed store (e.g. SQLite).
- **The statistical-question router is keyword-based** — it may occasionally
  miss an unusual phrasing and send a statistical question through the RAG
  path instead. If you notice this happening, the keyword list is in
  `src/analytics.py` (`_STAT_KEYWORDS`).
- **Not yet containerized** — see the project owner if you need a Dockerfile
  for deployment.
- **Not a medical device** — outputs are for informational purposes only.

---

## 7. Troubleshooting

| Problem | Likely cause / fix |
|---|---|
| `401 Unauthorized` downloading the model | You haven't run `huggingface-cli login`, or haven't been granted access to the gated Mistral model yet. |
| App is extremely slow to answer | You're running on CPU. Either use a GPU machine or switch to an API-based LLM. |
| `CUDA out of memory` | Lower `LLM_MAX_NEW_TOKENS` in `src/config.py`, or make sure 4-bit quantization (`USE_4BIT_QUANTIZATION = True`) is enabled. |
| Answers don't reflect new files added to `data/` | Click "♻️ Rebuild Knowledge Base" in the sidebar, or delete the `faiss_index/` folder and restart. |
| CSV-related questions go to the wrong pipeline | Add the phrasing you used to `_STAT_KEYWORDS` in `src/analytics.py`. |

---

## Notes

This project currently runs Mistral-7B **locally**, which requires a capable
GPU. If most users running this app won't have one, an easy upgrade is to
swap `src/llm.py` for a call to a hosted LLM API instead — this removes the
GPU requirement entirely and runs identically on any machine. Ask if you'd
like this change made.
