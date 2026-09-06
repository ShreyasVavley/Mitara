import chromadb
from typing import List
import os

class RAGStore:
    def __init__(self, persist_directory: str = "./chroma_db", data_directory: str = "./medical_data"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(name="clinical_guidelines")
        self.data_directory = data_directory
        self._initialize_dummy_data()
        self.ingest_local_documents() # Auto-ingest on startup

    def ingest_local_documents(self):
        """Reads all text/md files in the data directory and vectorizes them into ChromaDB."""
        if not os.path.exists(self.data_directory):
            os.makedirs(self.data_directory)
            return
            
        print(f"Scanning {self.data_directory} for medical documents...")
        for filename in os.listdir(self.data_directory):
            if filename.endswith(".txt") or filename.endswith(".md"):
                file_path = os.path.join(self.data_directory, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Simple chunking by paragraph
                chunks = [chunk.strip() for chunk in content.split('\n\n') if len(chunk.strip()) > 20]
                
                for i, chunk in enumerate(chunks):
                    doc_id = f"{filename}_chunk_{i}"
                    try:
                        self.collection.add(
                            documents=[chunk],
                            metadatas=[{"source": filename}],
                            ids=[doc_id]
                        )
                    except Exception:
                        pass # Document ID already exists in vector DB

    def _initialize_dummy_data(self):
        # Load some mock clinical guidelines for demonstration
        documents = [
            "For chest pain, immediately evaluate for myocardial infarction and administer aspirin.",
            "Type 2 Diabetes management involves metformin as first-line therapy.",
            "Hypertension treatment starts with ACE inhibitors or ARBs."
        ]
        ids = ["g1", "g2", "g3"]
        metadatas = [{"topic": "cardiology"}, {"topic": "endocrinology"}, {"topic": "cardiology"}]
        
        # In a real app, only add if not already present
        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
        except Exception:
            pass # Data might already exist

    def retrieve_guidelines(self, query: str, top_k: int = 3) -> List[str]:
        """
        Performs hybrid retrieval from the vector database.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        if results['documents'] and len(results['documents']) > 0:
            return results['documents'][0]
        return []

    def get_grounded_context(self, query: str) -> str:
        guidelines = self.retrieve_guidelines(query)
        return "\n".join(guidelines)
