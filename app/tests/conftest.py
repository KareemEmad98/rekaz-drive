import os
import shutil
import sys
import pytest
from fastapi.testclient import TestClient
from dotenv import load_dotenv


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_files():
    yield  # This runs all tests first

    cleanup_paths = ["./storage", "./metadata.db", ".pytest_cache"]

    for path in cleanup_paths:
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
                print(f"Cleaned up directory: {path}")
            elif os.path.isfile(path):
                os.remove(path)
                print(f"Cleaned up file: {path}")
        except (OSError, PermissionError) as e:
            print(f"Could not clean up {path}: {e}")


@pytest.fixture(scope="session", autouse=True)
def load_test_env():
    load_dotenv(".env.test", override=True)


@pytest.fixture(scope="function")
def client_for_backend(request):
    backend = request.param

    os.environ["STORAGE"] = backend

    modules_to_remove = [name for name in sys.modules.keys() if name.startswith("app.")]
    for module_name in modules_to_remove:
        del sys.modules[module_name]

    from app.infra.settings import Settings
    from fastapi import FastAPI
    from app.api.routes import blobs

    settings = Settings()

    print(f"\n=== Testing with backend: {backend} ===")
    print(f"Environment STORAGE: {os.environ.get('STORAGE')}")
    print(f"Settings storage: {settings.storage}")
    assert settings.storage == backend, f"Expected {backend}, got {settings.storage}"

    app = FastAPI(title="Rekaz Drive", version="1.0.0")
    app.include_router(blobs.router)
    app.state.settings = settings

    with TestClient(app) as client:
        yield client
