import streamlit as st
from agent import OpenClawAgent
import json
from config import DEFAULT_MODEL

st.set_page_config(page_title="OpenClaw Agent", page_icon="🤖",layout="wide")

if "agent" not in st.session_state:
    st.session_state.agent = OpenClawAgent(model_name=DEFAULT_MODEL)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "proactive_triggered" not in st.session_state:
    spark_message = st.session_state.agent.trigger_proactivity()
    if spark_message:
        st.session_state.messages.append({"role": "assistant", "content": spark_message})
    st.session_state.proactive_triggered = True

with st.sidebar:
    st.header("⚙️ Configuration")

    st.subheader("👤 User Profile")
    current_u_name = getattr(st.session_state.agent, "user_name", "")
    current_u_info = getattr(st.session_state.agent, "user_info", "")
    
    new_user_name = st.text_input("Your Name", value=current_u_name, max_chars=50)
    new_user_info = st.text_area("About You (Basic Info)", value=current_u_info, max_chars=200)

    st.divider()

    st.subheader("🤖 Agent Persona")
    new_agent_name = st.text_input("Agent Name", value=st.session_state.agent.agent_name, max_chars=50)
    new_agent_role = st.text_input("Agent Role", value=st.session_state.agent.role, max_chars=100)
    new_instructions = st.text_area("System Instructions", value=st.session_state.agent.system_instructions, max_chars=300)

    if st.button("Apply and Restart"):
        st.session_state.agent = OpenClawAgent(
            model_name=DEFAULT_MODEL,
            agent_name=new_agent_name,
            role=new_agent_role,
            system_instructions=new_instructions,
            user_name=new_user_name,
            user_info=new_user_info
        )
        
        st.session_state.messages = []
        if "proactive_triggered" in st.session_state:
            del st.session_state["proactive_triggered"]
        st.rerun()
tab1, tab2 = st.tabs(["Page A: Agent Interface", "Page B: Under he Hood"])

with tab1:
    col_chat, col_todo = st.columns([7, 3])
    
    with col_chat:
        st.subheader("Chat Window")

        chat_container = st.container()

        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
        
        prompt = st.chat_input("Type your message here...")

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                with st.chat_message("assistant"):
                    with st.spinner("Agent is thinking..."):
                        response = st.session_state.agent.chat(prompt)
                    st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    with col_todo:
        st.subheader("📋 Live To-Do List")
        tasks = st.session_state.agent.todo.list_tasks()
        if "no tasks" in tasks:
            st.info("No active tasks.")
        cleaned_lines = []
        for line in tasks.splitlines():
            line = line.strip()
            if not line:
                continue

            # Remove leading "<id>. " if present
            if ". " in line and line.split(". ", 1)[0].isdigit():
                line = line.split(". ", 1)[1]

            line = line.replace("[[x]]", "✅").replace("[[ ]]", "⬜")
            cleaned_lines.append(line)

        st.markdown("  \n".join(cleaned_lines))

with tab2:
    st.subheader("Under the Hood (Debug and Memory)")

    st.subheader("🕵️ Internal Monologue (Bonus)")
    st.caption("A live log of the agent's thought process.")
    
    monologue_found = False
    for msg in st.session_state.agent.get_memory():
        if msg["role"] == "assistant":
            try:
                data = json.loads(msg["content"])
                if "thought" in data and data["thought"]:
                    st.info(f"**Thinking:** {data['thought']}")
                    monologue_found = True
            except:
                pass
                
    if not monologue_found:
        st.write("*No thoughts yet. Start chatting!*")

    st.divider()

    col_short_mem, col_long_mem = st.columns(2)

    with col_short_mem:
        st.subheader("Short-Term Memory")
        st.caption("Active conversation context sent to the LLM")
        with st.expander("👀 View Raw JSON", expanded=False):
            st.json(st.session_state.agent.get_memory())

    with col_long_mem:
        st.subheader("Long-Term Memory")
        st.caption("Vector DB contents (ChromaDB)")

        if st.button("🗑️ Clear Vector DB"):
            if hasattr(st.session_state.agent.vector_db, 'clear_database'):
                st.session_state.agent.vector_db.clear_database()
                st.success("Long-Term Memory has been wiped!")
                st.rerun()
        with st.expander("👀 View DB Chunks", expanded=False):
            try:
                facts = st.session_state.agent.vector_db.get_all_facts()
                if not facts:
                    st.info("Vector DB is empty.")
                else:
                    for i, fact in enumerate(facts):
                        st.code(f"Chunk {i+1}:\n{fact}")
            except Exception as e:
                st.error(f"Could not load vector DB facts: {e}")
