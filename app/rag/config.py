from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

RAG_DATA_DIR = BASE_DIR / "data" / "rag"

PDF_DIRECTORY = RAG_DATA_DIR / "pdfs"

VECTOR_DIRECTORY = BASE_DIR / "data" / "vector_store"


PDF_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True,
)

VECTOR_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True,
)