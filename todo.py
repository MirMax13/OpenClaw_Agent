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
        task_lower = task.lower().strip()

        # Simple check to prevent adding duplicate tasks
        for existing_task in data["tasks"]:
            if existing_task["task"].lower().strip() == task_lower and not existing_task["completed"]:
                return f"Task '{existing_task['task']}' already exists and is not completed yet."
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
    
    def mark_completed(self, task_name):
        data = self.load()
        task_name_lower = task_name.lower().strip()
        
        # First search in uncompleted
        for task in data["tasks"]:
            if task["task"].lower().strip() == task_name_lower and not task["completed"]:
                task["completed"] = True
                self.save(data)
                return f"Task marked as completed: {task['task']}"
        # If exact match not found, try partial match
        for task in data["tasks"]:
            if task_name_lower in task["task"].lower() and not task["completed"]:
                task["completed"] = True
                self.save(data)
                return f"Task marked as completed: {task['task']}"
        
        # Finally, search if it's already in completed
        for task in data["tasks"]:
            if task["task"].lower().strip() == task_name_lower and task["completed"]:
                return f"Task '{task['task']}' is already marked as completed."
        return f"Task '{task_name}' not found."
    
if __name__ == "__main__":
    manager = ToDoManager()

    print(manager.add_task("Buy groceries"))
    print(manager.add_task("Finish coding project"))
    print(manager.list_tasks())
    print(manager.mark_completed("Buy groceries"))
    print(manager.list_tasks())