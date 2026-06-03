from pathlib import Path

from app.domain.model import Document
from app.domain.ports import DocumentLoader


class LocalLoader(DocumentLoader):

    SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".pptx", ".html", ".md", ".txt"}

    def __init__(self, local_dir: str):
        self.local_dir = Path(local_dir)

    def load(self) -> list[Document]:
        if not self.local_dir.exists():
            raise FileNotFoundError(f"Dossier introuvable : {self.local_dir}")

        return [
            Document(name=f.name, path=str(f))
            for f in self.local_dir.rglob("*")
            if f.is_file() and f.suffix.lower() in self.SUPPORTED_EXTENSIONS
        ]