# intrabot-ingestion

Microservice d'ingestion du projet IntraBot.

Pipeline : **Google Drive → Docling (parse) → HybridChunker → Cohere (embed) → ChromaDB**

---

## Démarrage rapide

**1. Cloner le repo**
```bash
git clone https://github.com/VOTRE-ORGA/intrabot-ingestion.git
cd intrabot-ingestion
```

**2. Créer et activer le venv**
```bash
python -m venv .venv
```

| OS | Commande |
|---|---|
| Windows cmd | `.venv\Scripts\activate.bat` |
| Windows PowerShell | `.venv\Scripts\Activate.ps1` |
| Linux / macOS | `source .venv/bin/activate` |

> **PowerShell bloque ?** Exécutez d'abord :
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```

**3. Installer les dépendances**
```bash
pip install -r requirements.txt
```

**4. Configurer le `.env`**
```bash
cp .env.example .env
```
Ouvrir `.env` et renseigner `COHERE_API_KEY` avec votre clé gratuite depuis https://dashboard.cohere.com/api-keys

**5. Ajouter des documents à ingérer**
```bash
mkdir -p data/docs
# Copier vos PDF / DOCX / HTML dans data/docs/
```

**6. Lancer le serveur**
```bash
python -m uvicorn app.infrastructure.api:app --port 8001 --reload
```

**7. Tester via Swagger**

Ouvrir http://127.0.0.1:8001/docs

| Endpoint | Méthode | Description |
|---|---|---|
| `/ingest` | `POST` | Ingère les documents du dossier `data/docs/` |
| `/embed` | `POST` | Envoie une question, reçoit son vecteur |
| `/health` | `GET` | Vérifie que le service tourne |

---

## Architecture hexagonale

```
app/
├── domain/              # cœur métier — zéro dépendance externe
│   ├── model.py         # entités : Document, Chunk
│   └── ports.py         # interfaces : Loader, Parser, Chunker, Embedder, VectorStore
├── adapters/            # implémentations concrètes
│   ├── loader/          # LocalLoader (→ GoogleDriveLoader prévu)
│   ├── parser/          # DoclingParser
│   ├── chunker/         # DoclingChunker
│   ├── embedder/        # CohereEmbedder (→ GeminiEmbedder possible)
│   └── vectorstore/     # ChromaStore
├── application/         # IngestionService — orchestre le pipeline
└── infrastructure/      # config, API FastAPI, injection de dépendances
```

---

## Prérequis

- Python 3.10+
- Une clé API Cohere gratuite : https://dashboard.cohere.com/api-keys

---

## Installation

> Voir la section [Démarrage rapide](#démarrage-rapide) pour les étapes détaillées.

```bash
git clone https://github.com/VOTRE-ORGA/intrabot-ingestion.git
cd intrabot-ingestion
python -m venv .venv
# Activer le venv selon votre OS (voir Démarrage rapide)
pip install -r requirements.txt
cp .env.example .env   # puis renseigner COHERE_API_KEY
```

---

## Lancer le service

```bash
# Créer le dossier de documents et y déposer des fichiers PDF/DOCX/HTML
mkdir -p data/docs

# Démarrer le serveur
python -m uvicorn app.infrastructure.api:app --port 8001 --reload
```

---

## Utiliser l'API

| Action | Méthode | URL |
|---|---|---|
| Vérifier que le service tourne | `GET` | `http://localhost:8001/health` |
| Lancer l'ingestion | `POST` | `http://localhost:8001/ingest` |
| Envoyer une question (vecteur) | `POST` | `http://localhost:8001/embed` |
| Interface Swagger | — | `http://localhost:8001/docs` |

---

## Changer de provider d'embedding

Modifiez la variable `EMBEDDING_PROVIDER` dans `.env` :

```env
# Provider par défaut
EMBEDDING_PROVIDER=cohere

# Pour utiliser Gemini (voir AGENTS.md pour les étapes d'ajout)
EMBEDDING_PROVIDER=gemini
```

---

## Variables d'environnement

| Variable | Description | Défaut |
|---|---|---|
| `EMBEDDING_PROVIDER` | Provider d'embedding (`cohere`, `gemini`, …) | `cohere` |
| `COHERE_API_KEY` | Clé API Cohere | — |
| `SOURCE_DIR` | Dossier des documents à ingérer | `./data/docs` |
| `CHROMA_PATH` | Chemin de la base ChromaDB | `./data/chroma` |
| `COLLECTION_NAME` | Nom de la collection Chroma | `intrabot` |
| `MAX_TOKENS` | Taille maximale d'un chunk (en tokens) | `512` |
| `PDF_DO_OCR` | Active l'OCR sur les PDF (coûteux en mémoire, inutile pour les PDF natifs) | `false` |
| `PDF_DO_TABLE_STRUCTURE` | Active la reconstruction des tableaux | `false` |
| `PDF_PAGE_BATCH_SIZE` | Nombre de pages traitées par lot (évite les `bad_alloc` sur les gros PDF) | `50` |

Exemple de fichier `.env` :

```env
EMBEDDING_PROVIDER=cohere
COHERE_API_KEY=your_cohere_api_key_here
SOURCE_DIR=./data/docs
CHROMA_PATH=./data/chroma
COLLECTION_NAME=intrabot
MAX_TOKENS=512
```
