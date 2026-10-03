import os

from app.rag.config import VECTOR_DIRECTORY

from app.rag.ingest import process_pdf

from app.rag.embedding_service import (
    EmbeddingService,
)

from app.rag.vector_store import (
    VectorStore,
)


class RagService:

    def __init__(self):

        self.embedding_service = (
            EmbeddingService()
        )

    # ============================================================
    # INDEX DOCUMENT
    # ============================================================

    def index_document(
        self,
        file_path: str,
        organization_id: str,
        document_id: str,
    ):

        result = process_pdf(
            pdf_path=file_path,
            organization_id=organization_id,
            document_id=document_id,
        )

        documents = result[
            "documents"
        ]

        if not documents:

            raise ValueError(
                "No readable text found in PDF."
            )

        texts = [
            document["text"]
            for document in documents
        ]

        embeddings = (
            self.embedding_service
            .embed_documents(
                texts
            )
        )

        vector_store = (
            VectorStore.load(
                str(VECTOR_DIRECTORY)
            )
        )

        if vector_store is None:

            vector_store = VectorStore(
                self.embedding_service.dimension
            )

        vector_store.add(
            embeddings,
            documents,
        )

        vector_store.save(
            str(VECTOR_DIRECTORY)
        )

        return {
            "filename":
                os.path.basename(
                    file_path
                ),

            "standard":
                result["standard"],

            "version":
                result["version"],

            "pages":
                result["pages"],

            "chunks":
                result["chunks"],
        }

    # ============================================================
    # QUERY
    # ============================================================

    def query(
        self,
        question: str,
        organization_id: str,
        top_k: int = 5,
    ):

        vector_store = (
            VectorStore.load(
                str(VECTOR_DIRECTORY)
            )
        )

        if vector_store is None:

            raise ValueError(
                "RAG vector store is not initialized."
            )

        query_embedding = (
            self.embedding_service
            .embed_query(
                question
            )
        )

        return vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            organization_id=organization_id,
        )