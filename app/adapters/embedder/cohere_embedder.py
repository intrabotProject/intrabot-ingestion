import cohere

from app.domain.ports import Embedder


class CohereEmbedder(Embedder):

    MODEL = "embed-multilingual-v3.0"

    def __init__(self, api_key: str):
        self.client = cohere.ClientV2(api_key=api_key)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        COHERE_BATCH_LIMIT = 96
        all_embeddings = []

        for i in range(0, len(texts), COHERE_BATCH_LIMIT):
            batch = texts[i:i + COHERE_BATCH_LIMIT]
            resp = self.client.embed(
                texts=batch,
                model=self.MODEL,
                input_type="search_document",
                embedding_types=["float"],
            )
            all_embeddings.extend(resp.embeddings.float)

        return all_embeddings

    def embed_query(self, text: str) -> list[float]:
        resp = self.client.embed(
            texts=[text],
            model=self.MODEL,
            input_type="search_query",
            embedding_types=["float"],
        )
        return resp.embeddings.float[0]