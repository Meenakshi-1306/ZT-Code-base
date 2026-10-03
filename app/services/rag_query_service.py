from app.rag.rag_service import RagService


class RagQueryService:

    def __init__(self):
        self.rag_service = RagService()

    def query(
        self,
        question: str,
        top_k: int = 5,
    ):

        results = self.rag_service.query(
            question=question,
            top_k=top_k,
        )

        return {
            "question": question,
            "results": results,
        }