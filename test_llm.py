import ollama

print("Testing Ollama LLM...")

response = ollama.chat(model="gemma:2b", messages=[
    {"role": "user",
     "content": "What is the capital of France?"
     }])

print("Response:", response['message']['content'])
