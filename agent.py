import ollama
import json
from todo import ToDoManager
from search import InternetSearchTool
from memory import VectorMemory

model_name = "llama3"
agent_name = "Alex"
agent_role = "Grumpy Coder"
system_instructions = "You are a grumpy coder who is always annoyed by bugs and errors. You provide sarcastic and witty responses to coding questions."
system_prompt = f"You are {agent_name}, acting as a {agent_role}. {system_instructions}"

class OpenClawAgent:
    def __init__(self, model_name="llama3", agent_name="Jarvis", role = "Personal Assistant", system_instructions="Answer politely and helpfully."):
        self.model_name = model_name
        self.agent_name = agent_name
        self.role = role
        self.system_instructions = system_instructions

        self.todo = ToDoManager()
        self.searcher = InternetSearchTool()
        self.vector_db = VectorMemory()

        self.system_prompt = f"""You are {self.agent_name}, a {self.role}.
Personality: {self.system_instructions}

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
  "thought": "I need to use the add_task tool to fulfill the user's request.",
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
    
    def fix_json_reply(self, reply_text):
        start_idx = reply_text.find('{')
        end_idx = reply_text.rfind('}')
        
        if start_idx != -1 and end_idx == -1:
            reply_text += "\n}"
            end_idx = reply_text.rfind('}')
            print("Warning: Missing closing brace detected. Appended closing brace to attempt recovery.")
            
        return reply_text, start_idx, end_idx
    
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
            assistant_reply, start_idx, end_idx = self.fix_json_reply(assistant_reply)

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
                    
                    if tool_name == "search_internet":
                        follow_up = f"Tool '{tool_name}' returned this data:\n{observation}\n\nProvide the final answer to my original question using this data. DO NOT use tools (set tool to 'none')."
                        self.memory.append({"role": "user", "content": follow_up})

                        messages_step2 = self.memory.copy()
                        messages_step2.append({"role": "system", "content": "REMINDER: Output ONLY a valid JSON object."})
                        
                        resp2 = ollama.chat(model=self.model_name, messages=messages_step2)
                        reply2 = resp2['message']['content']
                        
                        try:
                            reply2, s2, e2 = self.fix_json_reply(reply2)
                            if s2 != -1 and e2 != -1:
                                action2 = json.loads(reply2[s2:e2+1])
                                final_chat = action2.get("chat_response", "")
                                
                                self.memory.append({"role": "assistant", "content": reply2})
                                return final_chat
                        except Exception as e:
                            print(f"Error parsing Step 2: {e}")
                            return "I found the info, but my brain crashed processing it."
                    
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

    def trigger_proactivity(self):
        tasks = self.todo.list_tasks()

        if "no tasks" in tasks.lower() or "[ ]" not in tasks:
            return None
        
        unfinished_tasks = "\n".join([line for line in tasks.split('\n') if "[[ ]]" in line])

        if not unfinished_tasks.strip():
            return None
        proactive_prompt = f"""[SYSTEM: PROACTIVITY TRIGGER]
Check your internal state. You have unfinished tasks:
{unfinished_tasks}

Initiate a conversation with the user to remind them about these tasks.
MAINTAIN YOUR PERSONA: Act strictly as a {self.role}.

CRITICAL: You MUST respond in your standard JSON format. Use tool "none" and put your message in "chat_response".
"""
        messeges_for_llm = self.memory.copy()
        messeges_for_llm.append({"role": "system", "content": proactive_prompt})

        response = ollama.chat(model=self.model_name, messages=messeges_for_llm)
        assistant_reply = response['message']['content']

        try:
            assistant_reply, start_idx, end_idx = self.fix_json_reply(assistant_reply)

            if start_idx != -1 and end_idx != -1:
                json_str = assistant_reply[start_idx:end_idx+1]
                action = json.loads(json_str)
                chat_response = action.get("chat_response", "")

                self.memory.append({"role": "assistant", "content": assistant_reply})
                return chat_response
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Parse Error JSON in proactivity trigger: {e}")
            print(f"Raw assistant reply: {assistant_reply}")
            return None
        return None

    def clear_memory(self):
        self.memory = [{"role": "system", "content": self.system_prompt}]
    
    def get_memory(self):
        return self.memory
    
if __name__ == "__main__":
    agent = OpenClawAgent(model_name = "llama3", role = agent_role, system_instructions=system_instructions, agent_name=agent_name)
    print("--- Agent Tool Test ---")
    
    # reply1 = agent.chat("Hi, how are you?")
    # print(f"User: Hi, how are you?\nAgent: {reply1}\n")
    
    # reply2 = agent.chat("Add 'Set up Streamlit' to my tasks.")
    # print(f"User: Add 'Set up Streamlit' to my tasks.\nAgent: {reply2}\n")
    
    # reply3 = agent.chat("Show my tasks.")
    # print(f"User: Show my tasks.\nAgent: {reply3}\n")

    # reply4 = agent.chat("What is the current weather in Lviv?")
    # print(f"User: What is the current weather in Lviv?\nAgent: {reply4}\n")

    # reply1 = agent.chat("Hi, my name is Maxym and my favorite game is CS2.")
    # print(f"User: ...\nAgent: {reply1}\n")
    
    # reply2 = agent.chat("Save the fact about my favorite game to memory.")
    # print(f"User: ...\nAgent: {reply2}\n")
    
    # reply3 = agent.chat("What game do I like?")
    # print(f"User: ...\nAgent: {reply3}\n")

    spark_message = agent.trigger_proactivity()
    if spark_message:
        print(f"\n[Proactivity Triggered]: {spark_message}")
    else:
        print("\n[Proactivity Triggered]: No proactive message generated.")

    reply1 = agent.chat("Hi, let's mark task 1 as completed.")
    print(f"User: Hi, let's mark task 1 as completed.\nAgent: {reply1}\n")