import os
import json

class ToDoManager:
    def __init__(self, filepath="todo.json"):
        self.filepath = filepath
        self.ensure_file_exists()
    
    def ensure_file_exists(self):
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump({"tasks": []}, f)
    
    def load(self):
        with open(self.filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    
    def save(self, data):
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        
    def add_task(self, task):
        data = self.load()

        task_id = len(data["tasks"]) + 1
        data["tasks"].append({"id": task_id, "task": task, "completed": False})
        self.save(data)
        message = f"Task added: {task} (ID: {task_id})"
        return message
    
    def list_tasks(self):
        data = self.load()
        if not data["tasks"]:
            return "No tasks found."
        result = "To-Do List:\n"
        for task in data["tasks"]:
            status = "[x]" if task["completed"] else "[ ]"
            result += f"{task['id']}. [{status}] {task['task']}\n"
        return result
    
    def mark_completed(self, task_id):
        data = self.load()
        for task in data["tasks"]:
            if task["id"] == task_id:
                task["completed"] = True
                self.save(data)
                return f"Task marked as completed: {task['task']} (ID: {task_id})"
        return f"Task with ID {task_id} not found."
    
