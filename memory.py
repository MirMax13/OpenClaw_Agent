import chromadb

class VectorMemory:
    def __init__(self, db_path="./chromadb", collection_name="agent_memory"):

        self.client =chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def save_fact(self, fact_text):
        document_id = str(len(self.collection.get()['ids']) + 1)
        self.collection.add(
            documents=[fact_text],
            metadatas=[{"source": "agent_decision"}],
            ids=[document_id]
        )
        return "Fact saved successfully"

    def search_facts(self, query, n_results=2):
        if self.collection.count() == 0:
            return "No facts in memory."
        
        results = self.collection.query(
            query_texts=[query],
            n_results=min(n_results, self.collection.count())
        )

        if not results['documents'] or not results['documents'][0]:
            return "No relevant memories found."
        formatted_results = "Relevant memories:\n"
        for doc, distance in zip(results['documents'][0], results['distances'][0]):
            formatted_results += f"- [Distance: {distance:.4f}] {doc}\n"
        return formatted_results
    
    def get_all_facts(self):
        if self.collection.count() == 0:
            return []
        results = self.collection.get()
        return results['documents']
    def clear_database(self):
        try:
            all_ids = self.collection.get()['ids']
            if all_ids:
                self.collection.delete(ids=all_ids)
                
            return "Memory cleared successfully."
        except Exception as e:
            return f"Error: {e}"

if __name__ == "__main__":
    memory = VectorMemory()

    print("Testing VectorMemory...")

    memory.save_fact("I prefer dark theme in my IDE.")
    memory.save_fact("I enjoy working on AI projects.")

    print("\nAll facts in memory:")
    print(memory.get_all_facts())

    query = "What do I prefer in my IDE?"
    print(f"\nSearching for: '{query}'")
    print(memory.search_facts(query))