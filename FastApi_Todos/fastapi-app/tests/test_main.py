import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from main import app, save_todos, load_todos, TodoItem

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown():
    # 테스트 전 초기화
    save_todos([])
    yield
    # 테스트 후 정리
    save_todos([])

def test_read_root_success():
    # NOTE: 이 테스트는 'templates/index.html' 파일이 테스트 환경 경로에 존재함을 전제로 합니다.
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<html>" in response.text  # HTML 내용이 포함되어 있는지 확인

# ==============================================================================
# 2. load_todos() (JSONDecodeError) 커버리지 추가
# ==============================================================================
def test_load_todos_json_decode_error():
    # todo.json 파일을 만들고, 깨진 JSON 내용을 작성합니다.
    with open(TODO_FILE, "w", encoding="utf-8") as file:
        file.write("{invalid: json}")
        
    todos = load_todos()
    # load_todos 함수가 JSONDecodeError를 잡고 빈 리스트를 반환하는지 확인
    assert todos == []
    
def test_get_todos_empty():
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == []

def test_get_todos_with_items():
    todo = TodoItem(id=1, title="Test", description="Test description", completed=False)
    save_todos([todo.model_dump()])
    response = client.get("/todos")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Test"

def test_create_todo():
    todo = {"id": 1, "title": "Test", "description": "Test description", "completed": False}
    response = client.post("/todos", json=todo)
    assert response.status_code == 200
    assert response.json()["title"] == "Test"

def test_create_todo_invalid():
    todo = {"id": 1, "title": "Test"}
    response = client.post("/todos", json=todo)
    assert response.status_code == 422

def test_update_todo():
    todo = TodoItem(id=1, title="Test", description="Test description", completed=False)
    save_todos([todo.model_dump()])
    updated_todo = {"id": 1, "title": "Updated", "description": "Updated description", "completed": True}
    response = client.put("/todos/1", json=updated_todo)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated"

def test_update_todo_not_found():
    updated_todo = {"id": 1, "title": "Updated", "description": "Updated description", "completed": True}
    response = client.put("/todos/1", json=updated_todo)
    assert response.status_code == 404

def test_delete_todo():
    todo = TodoItem(id=1, title="Test", description="Test description", completed=False)
    save_todos([todo.model_dump()])
    response = client.delete("/todos/1")
    assert response.status_code == 200
    assert response.json()["message"] == "To-Do item deleted"
    
def test_delete_todo_not_found():
    response = client.delete("/todos/1")
    assert response.status_code == 200
    assert response.json()["message"] == "To-Do item deleted"

def test_toggle_todo_completion():
    todo = TodoItem(id=1, title="Test", description="Test description", completed=False)
    save_todos([todo.model_dump()])
    response = client.patch("/todos/1/toggle")
    assert response.status_code == 200
    assert response.json()["message"] == "Todo 1 completion status toggled to True"
    
    # 한 번 더 토글하여 False로 변경
    response = client.patch("/todos/1/toggle")
    assert response.status_code == 200
    assert response.json()["message"] == "Todo 1 completion status toggled to False"

def test_toggle_todo_not_found():
    response = client.patch("/todos/999/toggle")
    assert response.status_code == 404
    assert response.json()["detail"] == "To-Do item not found"