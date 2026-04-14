# FastAPI is the framework. Pydantic is the data validator.
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from uuid import uuid4, UUID

# The app object is your server instance.
app = FastAPI(title="Task API", version="1.0")

# ── Data model ──────────────────────────────────────────────
# Pydantic models define the SHAPE of your data.
# FastAPI uses these to validate requests and generate docs.

class TaskCreate(BaseModel):        # what the client sends in
    title: str
    done: bool = False

class Task(TaskCreate):              # what we store and return
    id: UUID

# ── In-memory store ──────────────────────────────────────────
# A plain dict stands in for a database.
# Key = UUID, Value = Task object.
tasks: dict[UUID, Task] = {}

# ── Endpoints ────────────────────────────────────────────────

@app.get("/tasks", response_model=list[Task])
async def list_tasks():
    # Return every task. response_model tells FastAPI
    # to serialize the return value as a list of Task.
    return list(tasks.values())

@app.post("/tasks", response_model=Task, status_code=201)
async def create_task(body: TaskCreate):
    # FastAPI reads the request JSON and validates it
    # against TaskCreate automatically. Bad data → 422.
    task = Task(id=uuid4(), **body.model_dump())
    tasks[task.id] = task
    return task

@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: UUID):
    # {task_id} in the path becomes a function parameter.
    # UUID type hint means FastAPI validates the format.
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: UUID, body: TaskCreate):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    tasks[task_id] = Task(id=task_id, **body.model_dump())
    return tasks[task_id]

@app.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: UUID):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    del tasks[task_id]
    # 204 No Content — success, but nothing to return