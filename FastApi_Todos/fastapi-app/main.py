from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json
import os

app = FastAPI()

#To-Do 항목 모델
class TodoItem(BaseModel):
    id: int
    title: str
    description : str
    completed : bool


#JSON 파일 경로
TODO_FILE="todo.json"

#JSON 파일에서 TO-DO 항목 로드
def load_todos():
    if os.path.exists(TODO_FILE):
        try:
            with open(TODO_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return []  # 파일이 비어있거나 잘못된 경우 빈 리스트 반환
    return []

#JSOn 파일에 TO-DO 항목 저장
def save_todos(todos):
    with open(TODO_FILE, "w") as file:
        json.dump(todos, file, indent=4)

# To-Do  목록 조회
@app.get("/todos", response_model=list[TodoItem])
def get_todos():
    return load_todos()

# 신규 To-Do 항목 추가
@app.post("/todos", response_model=TodoItem)
def create_todo(todo: TodoItem):
    todos = load_todos()
    todos.append(todo.model_dump())
    save_todos(todos)
    return todo

# To-Do 항목 수정
@app.put("/todos/{todo_id}", response_model=TodoItem)
def update_todo(todo_id: int, updated_todo: TodoItem):
    todos = load_todos()
    for todo in todos:
        if todo["id"] == todo_id:
            todo.update(updated_todo.model_dump())
            save_todos(todos)
            return updated_todo
    raise HTTPException(status_code=404, detail="To-Do item not found")

# To-Do 항목 삭제
@app.delete("/todos/{todo_id}", response_model=dict)
def delete_todo(todo_id: int):
    todos = load_todos()
    todos = [todo for todo in todos if todo["id"] != todo_id]
    save_todos(todos)
    return {"message": "To-Do item deleted"}
    
# To-Do 완료 상태 토글 (1단계 개선)
@app.patch("/todos/{todo_id}/toggle", response_model=dict)
def toggle_todo_completion(todo_id: int):
    todos = load_todos()
    for todo in todos:
        if todo["id"] == todo_id:
            todo["completed"] = not todo["completed"]
            save_todos(todos)
            return {"message": f"Todo {todo_id} completion status toggled to {todo['completed']}"}
    raise HTTPException(status_code=404, detail="To-Do item not found")

# HTML 파일 서빙
@app.get("/", response_class=HTMLResponse)
def read_root():
    base_dir = os.path.dirname(__file__)
    html_file_path = os.path.join(base_dir, "templates", "index.html")
    
    with open(html_file_path, "r", encoding="utf-8") as file:
        content = file.read()
    return HTMLResponse(content=content)