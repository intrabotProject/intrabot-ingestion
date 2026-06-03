from docling.document_converter import DocumentConverter

from app.domain.model import Document
from app.domain.ports import DocumentParser


class DoclingParser(DocumentParser):

    def __init__(self):
        self.converter = DocumentConverter()

    def parse(self, document: Document) -> str:
        result = self.converter.convert(document.path)
        return result.document.export_to_markdown()