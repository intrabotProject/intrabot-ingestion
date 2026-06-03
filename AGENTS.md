# AGENTS.md — IntraBot Ingestion Service

## Architecture
Ce microservice suit l'architecture hexagonale :
- `app/domain/` : cœur métier pur (aucune dépendance externe)
- `app/adapters/` : implémentations concrètes (Docling, Cohere, ChromaDB)
- `app/application/` : orchestration du pipeline
- `app/infrastructure/` : config, API FastAPI, injection de dépendances

## Règles clean code à respecter
- Toujours implémenter un port de `domain/ports.py`, jamais appeler Cohere/Docling/Chroma directement depuis le domaine
- Une classe = une responsabilité (SRP)
- Les dépendances s'injectent via le constructeur, jamais instanciées à l'intérieur d'une classe métier
- Nommage : classes en PascalCase, méthodes en snake_case, constantes en UPPER_CASE
- Pas de magic strings : toute valeur de config vient de `infrastructure/config.py`

## Pour ajouter un nouveau provider d'embedding (ex: Gemini)
1. Créer `app/adapters/embedder/gemini_embedder.py` qui hérite de `Embedder`
2. Implémenter `embed_documents()` et `embed_query()`
3. Ajouter `elif provider == "gemini"` dans `infrastructure/dependencies.py`
4. Mettre `EMBEDDING_PROVIDER=gemini` dans `.env`
→ Rien d'autre ne change dans le reste du code.

## Pour ajouter le vrai Google Drive
1. Créer `app/adapters/loader/google_drive_loader.py` qui hérite de `DocumentLoader`
2. Implémenter `load()` avec l'API Google Drive
3. Swapper dans `infrastructure/dependencies.py`