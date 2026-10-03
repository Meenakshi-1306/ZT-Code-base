from app.services.rag_query_service import (
    RagQueryService,
)


class RagQueryController:

    def __init__(self):
        self.service = RagQueryService()

    def query(
        self,
        question: str,
        top_k: int = 5,
    ):

        return self.service.query(
            question=question,
            top_k=top_k,
        )