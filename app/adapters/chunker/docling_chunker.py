from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter

from app.domain.model import Chunk
from app.domain.ports import DocumentChunker


class DoclingChunker(DocumentChunker):

    def __init__(self, max_tokens: int = 512):
        self.chunker = HybridChunker(max_tokens=max_tokens)
        self.converter = DocumentConverter()

    def chunk(self, text: str, source: str) -> list[Chunk]:
        doc = self.converter.convert_text(text).document
        chunks = []

        for i, chunk in enumerate(self.chunker.chunk(dl_doc=doc)):
            contextualized = self.chunker.contextualize(chunk=chunk)
            headings = getattr(chunk.meta, "headings", None) or []

            chunks.append(Chunk(
                text=contextualized,
                metadata={
                    "source": source,
                    "chunk_index": i,
                    "headings": " > ".join(headings) if headings else "",
                }
            ))

        return chunks