import base64
import uuid
import pytest


def create_test_blob(content: bytes = b"Hello Rekaz") -> tuple[str, dict]:
    blob_id = f"test-{uuid.uuid4()}"
    payload = {"id": blob_id, "data": base64.b64encode(content).decode("utf-8")}
    return blob_id, payload


def get_auth_headers(client) -> dict:
    return {"Authorization": f"Bearer {client.app.state.settings.auth_bearer_token}"}


@pytest.mark.parametrize("client_for_backend", ["fs", "s3", "ftp", "db"], indirect=True)
def test_upload_retrieve(client_for_backend):
    client = client_for_backend
    file_content = b"Hello Rekaz"

    blob_id, payload = create_test_blob(file_content)
    auth_headers = get_auth_headers(client)

    upload_response = client.post("/v1/blobs", json=payload, headers=auth_headers)
    assert upload_response.status_code == 201, upload_response.text
    response_blob_id = upload_response.json()["id"]

    retrieve_response = client.get(
        f"/v1/blobs/{response_blob_id}", headers=auth_headers
    )
    assert retrieve_response.status_code == 200, retrieve_response.text

    response_data = retrieve_response.json()
    retrieved_content = base64.b64decode(response_data["data"])
    assert retrieved_content == file_content


@pytest.mark.parametrize("client_for_backend", ["fs", "s3", "db"], indirect=True)
def test_upload_large_file(client_for_backend):
    client = client_for_backend
    large_content = b"Large file content " * 1000  # ~19KB

    blob_id, payload = create_test_blob(large_content)
    auth_headers = get_auth_headers(client)

    upload_response = client.post("/v1/blobs", json=payload, headers=auth_headers)
    assert upload_response.status_code == 201, upload_response.text

    retrieve_response = client.get(f"/v1/blobs/{blob_id}", headers=auth_headers)
    assert retrieve_response.status_code == 200

    retrieved_content = base64.b64decode(retrieve_response.json()["data"])
    assert retrieved_content == large_content
