from sentence_transformers import SentenceTransformer


class EmbeddingService:

    def __init__(
        self,
        model_name: str = "BAAI/bge-small-en-v1.5",
    ):

        self.model = SentenceTransformer(
            model_name,
        )

    def embed_documents(
        self,
        documents: list[str],
    ):

        if not documents:
            return []

        embeddings = self.model.encode(
            documents,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        return embeddings

    def embed_query(
        self,
        query: str,
    ):

        embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        return embedding[0]

    @property
    def dimension(self):

        return self.model.get_sentence_embedding_dimension()