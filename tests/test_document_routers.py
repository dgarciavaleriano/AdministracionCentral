import uuid
from unittest.mock import MagicMock
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from app import app
from api.controllers.documents import DocumentsController
from storage.entities.document import Document


@pytest.fixture
def mock_controller():
    return MagicMock(spec=DocumentsController)


@pytest.fixture
def client(mock_controller):
    app.dependency_overrides[DocumentsController] = lambda: mock_controller
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_route_create_document_created(client, mock_controller):
    id = uuid.uuid4()
    user_id = uuid.uuid4()
    file_name = "factura.pdf"
    file_content = b"Y29udGVuaWRv"

    
    mock_document = Document(user_id=user_id, file_name=file_name, file_content=file_content)
    mock_document.id = id
    mock_controller.create_document.return_value = mock_document

    payload = {
        "user_id": str(user_id),
        "file_name": file_name,
        "file_content": "Y29udGVuaWRv", 
    }

    response = client.post("/documents/", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["id"] == str(id)
    assert data["file_name"] == file_name

def test_route_create_document_returns_400(client, mock_controller):
    id = uuid.uuid4()
    user_id = uuid.uuid4()
    file_name = "factura.pdf"
    file_content = b"Y29udGVuaWRv"
    
        
    mock_document = Document(user_id=user_id, file_name=file_name, file_content=file_content)
    mock_document.id = id
    mock_controller.create_document.return_value = None
    
    payload = {
        "user_id": str(user_id),
        "file_name": file_name,
        "file_content": "Y29udGVuaWRv", 
    }

    response = client.post("/documents/", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_route_get_document_success(client, mock_controller):
    id = uuid.uuid4()
    user_id = uuid.uuid4()

    mock_document = Document(user_id=user_id, file_name="file.txt", file_content=b"data")
    mock_document.id = id
    mock_controller.get_document.return_value = mock_document

    response = client.get(f"/documents/{id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == str(id)


def test_route_get_document_not_found(client, mock_controller):
    mock_controller.get_document.return_value = None

    response = client.get(f"/documents/{uuid.uuid4()}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Documento no encontrado"


def test_route_update_document_success(client, mock_controller):
    id = uuid.uuid4()
    user_id = uuid.uuid4()
    file_name = "factura.pdf"
    file_content = b"Y29udGVuaWRv"

    mock_document = Document(user_id=user_id, file_name=file_name, file_content=file_content)
    mock_document.id = id
    mock_controller.update_document.return_value = mock_document

    payload = {
        "user_id": str(user_id),
        "file_name": file_name,
        "file_content": "Y29udGVuaWRv",
    }

    response = client.put(f"/documents/{id}", json=payload)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == str(id)

def test_route_update_document_returns_400(client, mock_controller):
    id = uuid.uuid4()
    user_id = uuid.uuid4()
    file_name = "factura.pdf"
    file_content = b"Y29udGVuaWRv"
    
    mock_document = Document(user_id=user_id, file_name=file_name, file_content=file_content)
    mock_document.id = id
    mock_controller.update_document.return_value = None
    
    payload = {
        "user_id": str(user_id),
        "file_name": file_name,
        "file_content": "Y29udGVuaWRv",
    }

    response = client.put(f"/documents/{uuid.uuid4()}", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_route_delete_document_success(client, mock_controller):
    id = uuid.uuid4()
    mock_controller.delete_document.return_value = True

    response = client.delete(f"/documents/{id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_controller.delete_document.assert_called_once_with(id)


def test_route_delete_document_not_found(client, mock_controller):
    id = uuid.uuid4()
    mock_controller.delete_document.return_value = False

    response = client.delete(f"/documents/{id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_route_get_documents_by_user(client, mock_controller):
    user_id = uuid.uuid4()
    id = uuid.uuid4()
    file_name = "factura.pdf"
    file_content = b"Y29udGVuaWRv"

    mock_document = Document(user_id=user_id, file_name=file_name, file_content=file_content)
    mock_document.id = id
    mock_controller.get_documents_by_user_id.return_value = [mock_document]

    response = client.get(f"/documents/user/{user_id}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == str(id)