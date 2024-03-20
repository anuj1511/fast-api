from bson import ObjectId
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from typing import List

app = FastAPI()

# Mongo Connection
mongo_url = "mongodb+srv://Anuj:Anuj@database.34bt3.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(mongo_url)
db = client["todo_db"]
todos_collection = db["todos"]

class Todo(BaseModel):
    id: str
    title: str
    description: str
    is_completed: bool

class TodoNoId(BaseModel):
    title: str
    description: str
    is_completed: bool

class TodoResponse(BaseModel):
    todo: Todo
    message: str

def is_valid_object_id(object_id_str):
    try:
        object_id = ObjectId(object_id_str)
        return True
    except Exception as e:
        return False

# CRUD operations

@app.get("/")
def read_root():
    print("bla bla")
    return {"Hello": "World"}

@app.post("/todos/", response_model=TodoResponse)
def create_todo(todo: TodoNoId):
    print(todo, type(todo))
    todo_dict = todo.__dict__
    result = todos_collection.insert_one(todo_dict)
    todo_dict["id"] = str(result.inserted_id)
    return TodoResponse(todo=todo_dict, message="Todo created successfully")

@app.get("/todos/", response_model=List[Todo])
def read_todos():
    print("here")
    todos = list(todos_collection.find())
    for todo in todos:
        todo["id"] = str(todo["_id"])
    return todos

@app.get("/todos/{todo_id}", response_model=Todo)
def read_todo(todo_id: str):

    if is_valid_object_id(todo_id) == False:
        raise HTTPException(status_code=404, detail="Invalid ObjectId")
    
    todo = todos_collection.find_one({"_id": ObjectId(todo_id)})
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo["id"] = str(todo["_id"])
    return todo

@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: str, todo: TodoNoId):

    if is_valid_object_id(todo_id) == False:
        raise HTTPException(status_code=404, detail="Invalid ObjectId")

    todo_dict = todo.__dict__
    if todos_collection.find_one({"_id": ObjectId(todo_id)}) is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    todos_collection.update_one({"_id": ObjectId(todo_id)}, {"$set": todo_dict})

    updated_todo = todos_collection.find_one({"_id": ObjectId(todo_id)})
    updated_todo["id"] = str(updated_todo["_id"])

    return TodoResponse(todo=updated_todo, message="Todo updated successfully!")

@app.delete("/todos/{todo_id}", response_model=TodoResponse)
def delete_todo(todo_id: str):
    todo = todos_collection.find_one({"_id": ObjectId(todo_id)})
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    result = todos_collection.delete_one({"_id": ObjectId(todo_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo["id"] = str(todo["_id"])
    return TodoResponse(todo=todo, message="Todo deleted successfully!")

