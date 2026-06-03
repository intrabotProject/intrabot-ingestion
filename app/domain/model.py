from dataclasses import dataclass, field


@dataclass
class Document:
    name: str        # nom du fichier ex: "rapport_2024.pdf"
    path: str        # chemin local absolu


@dataclass
class Chunk:
    text: str
    metadata: dict = field(default_factory=dict)
    # metadata contient par exemple :
    # { "source": "rapport_2024.pdf", "chunk_index": 3, "headings": "Intro > Contexte" }