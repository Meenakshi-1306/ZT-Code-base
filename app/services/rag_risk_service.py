from app.rag.rag_service import RagService

from app.rag.risk_engine import assess_risk


class RagRiskService:

    def __init__(self):
        self.rag_service = RagService()

    def query(
        self,
        question: str,
        top_k: int = 5,
    ):
        # Step 1: Retrieve relevant compliance evidence
        retrieved_documents = self.rag_service.query(
            question=question,
            top_k=top_k,
        )

        # Step 2: Pass retrieved evidence
        # into the existing risk engine
        risk_result = assess_risk(
            question=question,
            retrieved_documents=retrieved_documents,
        )

        # Step 3: Return both the grounded
        # risk assessment and retrieved evidence
        return {
            "question": question,
            "answer": risk_result["answer"],
            "compliance": risk_result["compliance"],
            "risk_assessment": risk_result["risk_assessment"],
            "recommendation": risk_result["recommendation"],
            "risk_explanation": risk_result["risk_explanation"],
            "results": retrieved_documents,
        }