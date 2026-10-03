import os
import pickle

import faiss
import numpy as np


class VectorStore:

    def __init__(self, dimension: int):
        self.dimension = dimension

        self.index = faiss.IndexFlatIP(dimension)

        self.documents = []

    def add(self, embeddings, documents):

        embeddings = np.asarray(
            embeddings,
            dtype="float32",
        )

        if len(embeddings) == 0:
            return

        self.index.add(embeddings)

        self.documents.extend(documents)

    def search(
        self,
        query_embedding,
        top_k: int = 10,
        organization_id: str | None = None,
    ):

        if self.index.ntotal == 0:
            return []

        query_embedding = np.asarray(
            [query_embedding],
            dtype="float32",
        )

        # Search more candidates because
        # some results may belong to other organizations.
        search_k = min(
            max(top_k * 10, top_k),
            self.index.ntotal,
        )

        scores, indices = self.index.search(
            query_embedding,
            search_k,
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0],
        ):

            if index == -1:
                continue

            document = self.documents[index]

            metadata = document.get(
                "metadata",
                {},
            )

            # Organization isolation
            if (
                organization_id is not None
                and metadata.get("organization_id")
                != organization_id
            ):
                continue

            results.append({
                "score": float(score),
                "text": document["text"],
                "metadata": metadata,
            })

            if len(results) >= top_k:
                break

        return results

    def save(self, directory: str):

        os.makedirs(
            directory,
            exist_ok=True,
        )

        faiss.write_index(
            self.index,
            os.path.join(
                directory,
                "index.faiss",
            ),
        )

        with open(
            os.path.join(
                directory,
                "documents.pkl",
            ),
            "wb",
        ) as file:

            pickle.dump(
                self.documents,
                file,
            )

    @classmethod
    def load(cls, directory: str):

        index_path = os.path.join(
            directory,
            "index.faiss",
        )

        documents_path = os.path.join(
            directory,
            "documents.pkl",
        )

        if not os.path.exists(index_path):
            return None

        if not os.path.exists(documents_path):
            return None

        index = faiss.read_index(
            index_path,
        )

        with open(
            documents_path,
            "rb",
        ) as file:

            documents = pickle.load(file)

        store = cls(index.d)

        store.index = index

        store.documents = documents

        return store