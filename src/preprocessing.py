"""
Data Preprocessing Module
=========================
Handles loading and splitting documents from various sources
"""

import os
import pandas as pd
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from src.config import DATA_DIR, CHUNK_SIZE, CHUNK_OVERLAP, INCLUDE_CSV_IN_RAG


class DataPreprocessor:
    """
    Handles all data preprocessing operations
    """

    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or DATA_DIR
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def load_documents(self) -> list[Document]:
        """
        Load documents from all sources (PDF, TXT, CSV)

        Returns:
            list[Document]: List of loaded documents
        """
        docs = []

        self._load_pdfs(docs)
        self._load_text_files(docs)

        if INCLUDE_CSV_IN_RAG:
            self._load_csv_data(docs)

        return docs

    def _load_pdfs(self, docs: list) -> int:
        """Load all PDF files from data directory"""
        count = 0
        if not os.path.exists(self.data_dir):
            return count

        for file in os.listdir(self.data_dir):
            if file.endswith(".pdf"):
                try:
                    loader = PyPDFLoader(os.path.join(self.data_dir, file))
                    pdf_docs = loader.load()
                    for doc in pdf_docs:
                        doc.metadata["source_type"] = "PDF"
                        doc.metadata["file_name"] = file
                    docs.extend(pdf_docs)
                    count += 1
                except Exception:
                    pass
        return count

    def _load_text_files(self, docs: list) -> int:
        """Load all TXT files from data directory"""
        count = 0
        if not os.path.exists(self.data_dir):
            return count

        for file in os.listdir(self.data_dir):
            if file.endswith(".txt"):
                try:
                    loader = TextLoader(os.path.join(self.data_dir, file))
                    txt_docs = loader.load()
                    for doc in txt_docs:
                        doc.metadata["source_type"] = "TXT"
                        doc.metadata["file_name"] = file
                    docs.extend(txt_docs)
                    count += 1
                except Exception:
                    pass
        return count

    def _load_csv_data(self, docs: list) -> int:
        """Load patient records from CSV and convert to documents"""
        csv_path = os.path.join(self.data_dir, "healthcare_dataset_cleaned.csv")

        if not os.path.exists(csv_path):
            return 0

        try:
            df = pd.read_csv(csv_path)

            for index, row in df.iterrows():
                patient_text = self._format_patient_record(row)

                doc = Document(
                    page_content=patient_text,
                    metadata={
                        "source": "Patient CSV",
                        "source_type": "CSV",
                        "row": index,
                        "patient_name": row.get("Name", "Unknown"),
                        "medical_condition": row.get("Medical Condition", "Unknown"),
                    },
                )
                docs.append(doc)

            return len(df)
        except Exception:
            return 0

    def _format_patient_record(self, row) -> str:
        """Format a patient record row into readable text"""
        return (
            f"Patient Record:\n"
            f"- Name: {row.get('Name', 'N/A')}\n"
            f"- Age: {row.get('Age', 'N/A')} years old\n"
            f"- Gender: {row.get('Gender', 'N/A')}\n"
            f"- Blood Type: {row.get('Blood Type', 'N/A')}\n"
            f"- Medical Condition: {row.get('Medical Condition', 'N/A')}\n"
            f"- Admission Date: {row.get('Date of Admission', 'N/A')}\n"
            f"- Admission Type: {row.get('Admission Type', 'N/A')}\n"
            f"- Discharge Date: {row.get('Discharge Date', 'N/A')}\n"
            f"- Doctor: Dr. {row.get('Doctor', 'N/A')}\n"
            f"- Hospital: {row.get('Hospital', 'N/A')}\n"
            f"- Insurance: {row.get('Insurance Provider', 'N/A')}\n"
            f"- Medication: {row.get('Medication', 'N/A')}\n"
            f"- Test Results: {row.get('Test Results', 'N/A')}\n"
        )

    def split_documents(self, documents: list[Document]) -> list[Document]:
        """
        Split documents into chunks

        Args:
            documents: List of documents to split

        Returns:
            list[Document]: List of document chunks
        """
        return self.splitter.split_documents(documents)

    def process(self) -> list[Document]:
        """
        Full preprocessing pipeline: load and split

        Returns:
            list[Document]: Processed document chunks
        """
        docs = self.load_documents()
        return self.split_documents(docs)


def preprocess_data() -> list[Document]:
    """Run the full preprocessing pipeline"""
    preprocessor = DataPreprocessor()
    return preprocessor.process()
