from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

from app.domain.model import Document
from app.domain.ports import DocumentParser
from app.infrastructure.config import settings


class DoclingParser(DocumentParser):

    def __init__(self):
        options = PdfPipelineOptions()
        options.do_ocr = settings.pdf_do_ocr
        options.do_table_structure = settings.pdf_do_table_structure

        self.converter = DocumentConverter(
            format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)}
        )
        self.batch_size = settings.pdf_page_batch_size

    def parse(self, document: Document) -> str:
        path = Path(document.path)

        if path.suffix.lower() != ".pdf":
            result = self.converter.convert(str(path))
            return result.document.export_to_markdown()

        return self._parse_pdf_in_batches(path)

    def _parse_pdf_in_batches(self, path: Path) -> str:
        pages_markdown: list[str] = []
        start = 1

        while True:
            end = start + self.batch_size - 1
            result = self.converter.convert(
                str(path),
                raises_on_error=False,
                page_range=(start, end),
            )
            batch_md = result.document.export_to_markdown()
            if not batch_md.strip():
                break
            pages_markdown.append(batch_md)
            # Docling returns fewer pages than requested when EOF is reached
            if result.pages and len(result.pages) < self.batch_size:
                break
            start += self.batch_size

        return "\n\n".join(pages_markdown)
