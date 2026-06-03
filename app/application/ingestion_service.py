from app.domain.ports import (
    DocumentLoader,
    DocumentParser,
    DocumentChunker,
    Embedder,
    VectorStore,
)


class IngestionService:

    def __init__(
        self,
        loader: DocumentLoader,
        parser: DocumentParser,
        chunker: DocumentChunker,
        embedder: Embedder,
        vector_store: VectorStore,
    ):
        self.loader = loader
        self.parser = parser
        self.chunker = chunker
        self.embedder = embedder
        self.vector_store = vector_store

    def run(self) -> dict:
        documents = self.loader.load()
        total_chunks = 0

        for document in documents:
            text = self.parser.parse(document)
            chunks = self.chunker.chunk(text=text, source=document.name)

            if not chunks:
                continue

            embeddings = self.embedder.embed_documents(
                [c.text for c in chunks]
            )
            self.vector_store.add(chunks=chunks, embeddings=embeddings)
            total_chunks += len(chunks)

        return {
            "files_processed": len(documents),
            "chunks_indexed": total_chunks,
            "total_in_collection": self.vector_store.count(),
        }