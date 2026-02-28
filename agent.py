import ollama
import json
from todo import ToDoManager
from search import InternetSearchTool
from memory import VectorMemory

model_name = "gemma:2b"
agent_name = "Alex"
agent_role = "Grumpy Coder"
system_instructions = "You are a grumpy coder who is always annoyed by bugs and errors. You provide sarcastic and witty responses to coding questions."
system_prompt = f"You are {agent_name}, acting as a {agent_role}. {system_instructions}"

class OpenClawAgent:
    def __init__(self, model_name="gemma:2b", agent_name="Jarvis", role = "Personal Assistant", system_instructions="Answer politely and helpfully."):
        self.model_name = model_name
        self.agent_name = agent_name
        self.role = role

        self.todo = ToDoManager()
        self.searcher = InternetSearchTool()
self.vector_db = VectorMemory()

        self.system_prompt = f"""You are {self.agent_name}, a {self.role}.
Personality: {system_instructions}

CRITICAL INSTRUCTION: You MUST ALWAYS respond with a single, valid JSON object. NEVER write raw text outside the JSON.

Your JSON must have EXACTLY these 4 keys:
1. "thought": Your internal reasoning.
2. "tool": The tool you need to use ("add_task", "list_tasks", "search_internet", "save_memory", or "none").
3. "tool_input": The input for the tool (task text, or ID, or "none").
4. "chat_response": Your response to the user, spoken in your character's personality.

Available tools:
- "add_task": input is task text.
- "list_tasks": input is "none".
- "mark_completed": input is task ID.
- "search_internet": use when you need to find up-to-date facts, news, or answer questions you don't know. Input is the search query.
- "save_memory": use to save important facts, user preferences, or completed tasks to long-term memory. Input is the text to save.

JSON EXAMPLE 1 (Using a tool):
{{
  "thought": "User wants to add a task. I hate tasks.",
  "tool": "add_task",
  "tool_input": "Set up Streamlit",
  "chat_response": "[Generate your response here based on your assigned personality]"
}}

JSON EXAMPLE 2 (Just chatting):
{{
  "thought": "User is just saying hi.",
  "tool": "none",
  "tool_input": "none",
  "chat_response": "[Generate your greeting here based on your assigned personality]"
}}
"""
        self.memory = [{"role": "system", "content": self.system_prompt}]
    
    def chat(self, user_message):
context = self.vector_db.search_facts(user_message)

        self.memory.append({"role": "user", "content": user_message})

        messages_for_llm = self.memory.copy()

        if "Relevant memories:" in context:
            messages_for_llm.append({"role": "system", "content": f"Long-Term Memory Context:\n{context}"})

        messages_for_llm.append({"role": "system", "content": "REMINDER: Output ONLY a valid JSON object. No other text."})

        response = ollama.chat(model=self.model_name, messages=messages_for_llm)
        assistant_reply = response['message']['content']

        try:
            start_idx = assistant_reply.find('{')
            end_idx = assistant_reply.rfind('}')
            
            # Attempt to recover from missing closing brace
            if start_idx != -1 and end_idx == -1:
                assistant_reply += "\n}"
                end_idx = assistant_reply.rfind('}')
                print("Warning: Missing closing brace detected. Appended closing brace to attempt recovery.")

            if start_idx != -1 and end_idx != -1:
                json_str = assistant_reply[start_idx:end_idx+1]
                action = json.loads(json_str)
                
                tool_name = action.get("tool", "none")
                tool_input = action.get("tool_input", "none")
                chat_response = action.get("chat_response", "")
                thought = action.get("thought", "")
                
                print(f"\nThought: {thought}")
                
                observation = ""
                if tool_name != "none":
                    print(f"Tool: {tool_name} | Input: {tool_input}")
                    if tool_name == "add_task":
                        observation = self.todo.add_task(tool_input)
                    elif tool_name == "list_tasks":
                        observation = self.todo.list_tasks()
                    elif tool_name == "mark_completed":
                        observation = self.todo.mark_completed(int(tool_input))
                    elif tool_name == "search_internet":
                        observation = self.searcher.search(tool_input)
elif tool_name == "save_memory":
                        observation = self.vector_db.save_fact(tool_input)
                    
                    self.memory.append({"role": "assistant", "content": assistant_reply})
                    self.memory.append({"role": "system", "content": f"System Tool Result: {observation}"})

                    return f"{chat_response}\n\n[System]: {observation}"
                
                self.memory.append({"role": "assistant", "content": assistant_reply})
                return chat_response
                
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Parse Error JSON: {e}")
            print(f"Raw assistant reply: {assistant_reply}")
            return "Ugh, my brain crashed. Could you repeat that?"

        self.memory.append({"role": "assistant", "content": assistant_reply})

        return assistant_reply

    def clear_memory(self):
        self.memory = [{"role": "system", "content": self.system_prompt}]
    
    def get_memory(self):
        return self.memory
    
if __name__ == "__main__":
    agent = OpenClawAgent(model_name = "llama3", role = agent_role, system_instructions=system_instructions, agent_name=agent_name)
    print("--- Agent Tool Test ---")
    
    reply1 = agent.chat("Hi, how are you?")
    print(f"User: Hi, how are you?\nAgent: {reply1}\n")
    
    reply2 = agent.chat("Add 'Set up Streamlit' to my tasks.")
    print(f"User: Add 'Set up Streamlit' to my tasks.\nAgent: {reply2}\n")
    
    reply3 = agent.chat("Show my tasks.")
    print(f"User: Show my tasks.\nAgent: {reply3}\n")

    reply4 = agent.chat("What is the current weather in Lviv?")
    print(f"User: What is the current weather in Lviv?\nAgent: {reply4}\n")