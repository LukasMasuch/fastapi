import os

from starlette.testclient import TestClient

from request_files.tutorial002 import app

client = TestClient(app)

openapi_schema = {
    "openapi": "3.0.2",
    "info": {"title": "Fast API", "version": "0.1.0"},
    "paths": {
        "/files/": {
            "post": {
                "responses": {
                    "200": {
                        "description": "Successful Response",
                        "content": {"application/json": {"schema": {}}},
                    },
                    "422": {
                        "description": "Validation Error",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/HTTPValidationError"
                                }
                            }
                        },
                    },
                },
                "summary": "Create Files",
                "operationId": "create_files_files__post",
                "requestBody": {
                    "content": {
                        "multipart/form-data": {
                            "schema": {"$ref": "#/components/schemas/Body_create_files"}
                        }
                    },
                    "required": True,
                },
            }
        },
        "/uploadfiles/": {
            "post": {
                "responses": {
                    "200": {
                        "description": "Successful Response",
                        "content": {"application/json": {"schema": {}}},
                    },
                    "422": {
                        "description": "Validation Error",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/HTTPValidationError"
                                }
                            }
                        },
                    },
                },
                "summary": "Create Upload Files",
                "operationId": "create_upload_files_uploadfiles__post",
                "requestBody": {
                    "content": {
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/Body_create_upload_files"
                            }
                        }
                    },
                    "required": True,
                },
            }
        },
        "/": {
            "get": {
                "responses": {
                    "200": {
                        "description": "Successful Response",
                        "content": {"application/json": {"schema": {}}},
                    }
                },
                "summary": "Main",
                "operationId": "main__get",
            }
        },
    },
    "components": {
        "schemas": {
            "Body_create_files": {
                "title": "Body_create_files",
                "required": ["files"],
                "type": "object",
                "properties": {
                    "files": {
                        "title": "Files",
                        "type": "array",
                        "items": {"type": "string", "format": "binary"},
                    }
                },
            },
            "Body_create_upload_files": {
                "title": "Body_create_upload_files",
                "required": ["files"],
                "type": "object",
                "properties": {
                    "files": {
                        "title": "Files",
                        "type": "array",
                        "items": {"type": "string", "format": "binary"},
                    }
                },
            },
            "ValidationError": {
                "title": "ValidationError",
                "required": ["loc", "msg", "type"],
                "type": "object",
                "properties": {
                    "loc": {
                        "title": "Location",
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "msg": {"title": "Message", "type": "string"},
                    "type": {"title": "Error Type", "type": "string"},
                },
            },
            "HTTPValidationError": {
                "title": "HTTPValidationError",
                "type": "object",
                "properties": {
                    "detail": {
                        "title": "Detail",
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/ValidationError"},
                    }
                },
            },
        }
    },
}


def test_openapi_schema():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert response.json() == openapi_schema


file_required = {
    "detail": [
        {
            "loc": ["body", "files"],
            "msg": "field required",
            "type": "value_error.missing",
        }
    ]
}


def test_post_form_no_body():
    response = client.post("/files/")
    assert response.status_code == 422
    assert response.json() == file_required


def test_post_body_json():
    response = client.post("/files/", json={"file": "Foo"})
    assert response.status_code == 422
    assert response.json() == file_required


def test_post_files(tmpdir):
    path = os.path.join(tmpdir, "test.txt")
    with open(path, "wb") as file:
        file.write(b"<file content>")
    path2 = os.path.join(tmpdir, "test2.txt")
    with open(path2, "wb") as file:
        file.write(b"<file content2>")

    client = TestClient(app)
    response = client.post(
        "/files/",
        files=(
            ("files", ("test.txt", open(path, "rb"))),
            ("files", ("test2.txt", open(path2, "rb"))),
        ),
    )
    assert response.status_code == 200
    assert response.json() == {"file_sizes": [14, 15]}


def test_post_upload_file(tmpdir):
    path = os.path.join(tmpdir, "test.txt")
    with open(path, "wb") as file:
        file.write(b"<file content>")
    path2 = os.path.join(tmpdir, "test2.txt")
    with open(path2, "wb") as file:
        file.write(b"<file content2>")

    client = TestClient(app)
    response = client.post(
        "/uploadfiles/",
        files=(
            ("files", ("test.txt", open(path, "rb"))),
            ("files", ("test2.txt", open(path2, "rb"))),
        ),
    )
    assert response.status_code == 200
    assert response.json() == {"filenames": ["test.txt", "test2.txt"]}


def test_get_root():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert b"<form" in response.content
