import ollama

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

        self.system_prompt = f"You are {self.agent_name}, acting as a {self.role}. {system_instructions}"

        self.memory = [{"role": "system", "content": self.system_prompt}]
    
    def chat(self, user_message):
        self.memory.append({"role": "user", "content": user_message})

        response = ollama.chat(model=self.model_name, messages=self.memory)
        assistant_reply = response['message']['content']

        self.memory.append({"role": "assistant", "content": assistant_reply})

        return assistant_reply