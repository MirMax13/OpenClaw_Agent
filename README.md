# 🤖 OpenClaw Agent

An autonomous, local AI personal assistant built with Python, Streamlit, and Ollama. This agent uses a ReAct-style reasoning loop to manage a to-do list, search the internet, and proactively remember user preferences using a Vector Database (RAG).

## 🌟 Key Features
- **Local & Private:** Runs entirely locally using Ollama (optimized for `llama3` 8B).
- **Tool Use (ReAct):** The agent autonomously decides when to use tools: `add_task`, `list_tasks`, `mark_completed`, `search_internet`, and `save_memory`.
- **Proactive Memory (RAG):** Uses ChromaDB to automatically save personal facts and preferences shared by the user without explicit commands.
- **Dynamic Context Injection:** Prevents LLM context hijacking by dynamically updating the system prompt with active tasks and relevant long-term memories before every request.
- **Proactivity Trigger:** The agent initiates conversations if there are unfinished tasks on the To-Do list upon startup or state changes.

## 🏗️ Architecture & Clean Code
The project strictly separates UI, Logic, and Data:
- `app.py`: Streamlit frontend and session state management.
- `agent.py`: The core Reasoning Loop and JSON parsing logic.
- `config.py`: Prompts and model configurations.
- `todo.py`, `search.py`, `memory.py`: Isolated tool modules.

## 🧠 Handling Smaller Local Models (2B vs 8B)
During development, significant testing was done on smaller models like `gemma:2b`. 
**Observed Limitations:**
1. **Context Hijacking:** 2B models struggle with complex ReAct loops and often fall into repetition loops, ignoring new user input.
2. **JSON Formatting:** High failure rate in maintaining strict JSON structures when the system prompt is too long.
3. **Persona Amnesia:** Forgetting system instructions under heavy cognitive load.

**The Solution:** The architecture includes dynamic prompt switching. If a `gemma` model is detected, the system falls back to a minimal `GEMMA_SYSTEM_PROMPT_TEMPLATE` (stripping out complex RAG rules and user background info) to preserve basic JSON formatting and tool execution stability. However, for the full autonomous experience, **Llama 3 (8B)** is highly recommended.

## 🚀 How to Run

### Prerequisites
1. Install [Ollama](https://ollama.com/) and pull the models:
   ```bash
   ollama pull llama3
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running Locally
```bash
streamlit run app.py
```

### Running with Docker
First, build the image:

```bash
docker build -t openclaw-agent .
```

Then run the container. Since the agent needs to communicate with the Ollama instance on your host machine, use the appropriate command for your OS:

**Windows / Mac (Docker Desktop):**

```bash
docker run -p 8501:8501 -e OLLAMA_HOST=http://host.docker.internal:11434 openclaw-agent
```

**Linux:**

```bash
docker run --network host -e OLLAMA_HOST=http://localhost:11434 openclaw-agent
```