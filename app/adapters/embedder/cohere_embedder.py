import cohere

from app.domain.ports import Embedder


class CohereEmbedder(Embedder):

    MODEL = "embed-multilingual-v3.0"

    def __init__(self, api_key: str):
        self.client = cohere.ClientV2(api_key=api_key)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        resp = self.client.embed(
            texts=texts,
            model=self.MODEL,
            input_type="search_document",
            embedding_types=["float"],
        )
        return resp.embeddings.float

    def embed_query(self, text: str) -> list[float]:
        resp = self.client.embed(
            texts=[text],
            model=self.MODEL,
            input_type="search_query",
            embedding_types=["float"],
        )
        return resp.embeddings.float[0]