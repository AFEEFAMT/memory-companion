import chromadb
from chromadb.utils import embedding_functions
import os
import hashlib

# Initialize ChromaDB (Local persistence)
CHROMA_DATA_PATH = os.path.join(os.path.dirname(__file__), 'chroma_db')
client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)

ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

collection = client.get_or_create_collection(name="patient_memories", embedding_function=ef)

def save_vector_memory(note_text, metadata):
    """
    Saves the note text + metadata (date, context) as a vector.
    """
    doc_id = hashlib.sha256(note_text.encode()).hexdigest()
    
    collection.add(
        documents=[note_text],
        metadatas=[metadata],
        ids=[doc_id]
    )

def search_similar_memories(query_text, n_results=2):
    """
    Returns the most relevant notes based on meaning.
    """
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results
    )
    
    if not results['documents'][0]:
        return []
        
    return [{"text": doc, "metadata": meta} 
        for doc, meta in zip(results['documents'][0], results['metadatas'][0])]

def delete_patient_memories(patient_id):
    """
    Deletes all vector embeddings for a specific patient.
    """
    try:
        # Delete entries where metadata matches patient_id
        collection.delete(
            where={"patient_id": patient_id}
        )
        return True
    except Exception as e:
        print(f"Vector delete error: {e}")
        return False