import uuid
from unittest.mock import MagicMock
from api.controllers.documents import DocumentsController
from storage.entities.document import Document


def test_controller_create_document():
    mock_repo = MagicMock()
    controller = DocumentsController(db=MagicMock())
    controller.document_repository = mock_repo

    user_id = uuid.uuid4()
    file_name = "a.txt"
    file_content = b"content"

    expected_document = Document(user_id=user_id, file_name=file_name, file_content=file_content)
    mock_repo.create.return_value = expected_document

    result = controller.create_document(user_id, file_name, file_content)

    assert result == expected_document
    mock_repo.create.assert_called_once()


def test_controller_get_document():
    mock_repo = MagicMock()
    controller = DocumentsController(db=MagicMock())
    controller.document_repository = mock_repo

    id = uuid.uuid4()
    user_id = uuid.uuid4()
    file_name = "a.txt"
    file_content = b"content"

    expected_document = Document(user_id=user_id, file_name=file_name, file_content=file_content)
    mock_repo.get.return_value = expected_document

    result = controller.get_document(id)

    assert result == expected_document
    mock_repo.get.assert_called_once_with(id)


def test_controller_update_document():
    mock_repo = MagicMock()
    controller = DocumentsController(db=MagicMock())
    controller.document_repository = mock_repo

    id = uuid.uuid4()
    user_id = uuid.uuid4()
    file_name = "a.txt"
    file_content = b"content"

    expected_document = Document(user_id=user_id, file_name=file_name, file_content=file_content)
    mock_repo.update.return_value = expected_document

    result = controller.update_document(id, user_id, file_name, file_content)

    assert result == expected_document
    mock_repo.update.assert_called_once()


def test_controller_delete_document():
    mock_repo = MagicMock()
    controller = DocumentsController(db=MagicMock())
    controller.document_repository = mock_repo

    id = uuid.uuid4()
    mock_repo.delete.return_value = True

    result = controller.delete_document(id)

    assert result is True
    mock_repo.delete.assert_called_once_with(id)


def test_controller_get_documents_by_user_id():
    mock_repo = MagicMock()
    controller = DocumentsController(db=MagicMock())
    controller.document_repository = mock_repo

    user_id = uuid.uuid4()
    mock_repo.get_by_user_id.return_value = []

    result = controller.get_documents_by_user_id(user_id)

    assert result == []
    mock_repo.get_by_user_id.assert_called_once_with(user_id)