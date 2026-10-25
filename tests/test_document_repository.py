import uuid
from unittest.mock import MagicMock
from storage.crud.document_repository import DocumentRepository
from storage.entities.document import Document


def test_create_success():
    mock_session = MagicMock()
    repository = DocumentRepository(session=mock_session)
    document = Document(user_id=uuid.uuid4(), file_name="test.pdf", file_content=b"data")

    result = repository.create(document)

    assert result == document
    mock_session.add.assert_called_once_with(document)
    mock_session.flush.assert_called_once()
    mock_session.refresh.assert_called_once_with(document)


def test_create_failure_triggers_rollback():
    mock_session = MagicMock()
    mock_session.flush.side_effect = Exception("DB Error")
    repository = DocumentRepository(session=mock_session)
    document = Document(user_id=uuid.uuid4(), file_name="test.pdf", file_content=b"data")

    result = repository.create(document)

    assert result is None
    mock_session.rollback.assert_called_once()


def test_get_document():
    mock_session = MagicMock()
    repository = DocumentRepository(session=mock_session)
    id = uuid.uuid4()
    expected_document = Document(user_id=uuid.uuid4(), file_name="test.pdf", file_content=b"data")
    mock_session.get.return_value = expected_document

    result = repository.get(id)

    assert result == expected_document
    mock_session.get.assert_called_once_with(Document, id)

def test_get_not_found():
    mock_session = MagicMock()
    mock_session.get.return_value = None
    repository = DocumentRepository(session=mock_session)

    result = repository.get(uuid.uuid4())

    assert result is None


def test_update_success():
    mock_session = MagicMock()
    repository = DocumentRepository(session=mock_session)
    id = uuid.uuid4()
    
    existing_document = Document(user_id=uuid.uuid4(), file_name="old.pdf", file_content=b"old")
    new_data = Document(user_id=existing_document.user_id, file_name="new.pdf", file_content=b"new")
    
    mock_session.get.return_value = existing_document

    result = repository.update(id, new_data)

    assert result == existing_document
    assert existing_document.file_name == "new.pdf"
    assert existing_document.file_content == b"new"
    mock_session.flush.assert_called_once()
    mock_session.refresh.assert_called_once_with(existing_document)


def test_update_not_found():
    mock_session = MagicMock()
    mock_session.get.return_value = None
    repository = DocumentRepository(session=mock_session)

    result = repository.update(uuid.uuid4(), MagicMock())

    assert result is None


def test_delete_success():
    mock_session = MagicMock()
    repository = DocumentRepository(session=mock_session)
    id = uuid.uuid4()
    existing_document = Document(user_id=uuid.uuid4(), file_name="file.pdf", file_content=b"data")
    mock_session.get.return_value = existing_document

    result = repository.delete(id)

    assert result is True
    mock_session.delete.assert_called_once_with(existing_document)
    mock_session.flush.assert_called_once()


def test_get_by_user_id():
    mock_session = MagicMock()
    repository = DocumentRepository(session=mock_session)
    user_id = uuid.uuid4()
    expected_documents = [Document(user_id=user_id, file_name="1.pdf", file_content=b"1")]

    mock_session.scalars.return_value.all.return_value = expected_documents

    result = repository.get_by_user_id(user_id)

    assert result == expected_documents
    mock_session.scalars.assert_called_once()