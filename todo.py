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
    
    