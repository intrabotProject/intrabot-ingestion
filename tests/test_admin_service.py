from unittest.mock import MagicMock, patch

from app.application.admin_service import AdminService
from app.domain.model import Document, DocumentNotFoundError


def _build_service():
    loader = MagicMock()
    vector_store = MagicMock()
    document_repository = MagicMock()
    metadata_repository = MagicMock()
    ingestion_service = MagicMock()
    metadata_repository.get_category.return_value = "public"
    metadata_repository.list_all.return_value = {}
    return AdminService(
        loader=loader,
        vector_store=vector_store,
        collection_name="intrabot",
        document_repository=document_repository,
        metadata_repository=metadata_repository,
        ingestion_service=ingestion_service,
    ), loader, vector_store, document_repository, metadata_repository, ingestion_service


def test_list_documents_merges_disk_and_indexed_sources():
    service, loader, vector_store, _, metadata_repository, _ = _build_service()
    loader.load.return_value = [
        Document(name="a.pdf", path="/data/docs/a.pdf"),
        Document(name="b.pdf", path="/data/docs/b.pdf"),
    ]
    vector_store.list_sources.return_value = {"a.pdf": 3}
    vector_store.get_indexed_categories.return_value = {"a.pdf": "engineering"}
    metadata_repository.list_all.return_value = {"a.pdf": "engineering"}

    documents = service.list_documents()

    assert len(documents) == 2
    by_source = {doc.source: doc for doc in documents}

    assert by_source["a.pdf"].status == "indexed"
    assert by_source["a.pdf"].chunk_count == 3
    assert by_source["a.pdf"].category == "engineering"
    assert by_source["b.pdf"].status == "pending"
    assert by_source["b.pdf"].chunk_count == 0


def test_get_collection_stats():
    service, loader, vector_store, _, _, _ = _build_service()
    loader.load.return_value = [
        Document(name="a.pdf", path="/data/docs/a.pdf"),
    ]
    vector_store.list_sources.return_value = {"a.pdf": 2}
    vector_store.get_indexed_categories.return_value = {"a.pdf": "public"}
    vector_store.count.return_value = 2

    stats = service.get_collection_stats()

    assert stats.collection_name == "intrabot"
    assert stats.document_count == 1
    assert stats.chunk_count == 2
    assert stats.indexed_document_count == 1
    assert stats.pending_document_count == 0


def test_upload_document_ingests_immediately():
    service, _, vector_store, document_repository, metadata_repository, ingestion_service = _build_service()
    document = Document(name="new.pdf", path="/data/docs/new.pdf")
    document_repository.save.return_value = "new.pdf"
    document_repository.get_document.return_value = document
    metadata_repository.set_category.return_value = "rh"
    ingestion_service.ingest_document.return_value = {"chunks_indexed": 8}

    with patch.object(service, "_file_size_bytes", return_value=100):
        summary = service.upload_document("new.pdf", b"content", category="rh")

    metadata_repository.set_category.assert_called_once_with("new.pdf", "rh")
    vector_store.delete_by_source.assert_called_once_with("new.pdf")
    ingestion_service.ingest_document.assert_called_once_with(document, category="rh")
    assert summary.source == "new.pdf"
    assert summary.status == "indexed"
    assert summary.chunk_count == 8
    assert summary.category == "rh"


def test_delete_document_removes_file_and_chunks():
    service, _, vector_store, document_repository, metadata_repository, _ = _build_service()
    vector_store.delete_by_source.return_value = 4
    document_repository.delete.return_value = True

    result = service.delete_document("a.pdf")

    metadata_repository.delete.assert_called_once_with("a.pdf")
    assert result.source == "a.pdf"
    assert result.file_deleted is True
    assert result.chunks_deleted == 4


def test_delete_document_raises_when_missing():
    service, _, vector_store, document_repository, _, _ = _build_service()
    vector_store.delete_by_source.return_value = 0
    document_repository.delete.return_value = False

    try:
        service.delete_document("missing.pdf")
        assert False, "Expected DocumentNotFoundError"
    except DocumentNotFoundError:
        pass


def test_reindex_document_replaces_chunks():
    service, _, vector_store, document_repository, metadata_repository, ingestion_service = _build_service()
    document = Document(name="a.pdf", path="/data/docs/a.pdf")
    document_repository.get_document.return_value = document
    metadata_repository.get_category.return_value = "finance"
    ingestion_service.ingest_document.return_value = {"chunks_indexed": 5}
    vector_store.count.return_value = 12

    result = service.reindex_document("a.pdf")

    vector_store.delete_by_source.assert_called_once_with("a.pdf")
    ingestion_service.ingest_document.assert_called_once_with(document, category="finance")
    assert result.chunks_indexed == 5
    assert result.total_in_collection == 12
