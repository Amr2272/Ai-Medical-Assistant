import os
import torch
from dotenv import load_dotenv

# Load variables from a local .env file (GROQ_API_KEY, etc.) if present
load_dotenv()

# =========================
# Paths
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
FAISS_INDEX_DIR = os.path.join(BASE_DIR, "faiss_index")

# =========================
# Patient Analytics (Text-to-Pandas)
# =========================
PATIENT_CSV_PATH = os.path.join(DATA_DIR, "healthcare_dataset_cleaned.csv")
INCLUDE_CSV_IN_RAG = False

# =========================
# Device Configuration
# =========================
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# =========================
# LLM Configuration (Groq API)
# =========================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
LLM_MAX_TOKENS = 512
LLM_TEMPERATURE = 0.5

# =========================
# Embedding Configuration
# =========================
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# =========================
# Retrieval Configuration
# =========================
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_RESULTS = 8
SEARCH_TYPE = "similarity"