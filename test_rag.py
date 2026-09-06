from rag_store import RAGStore
import os

print("--- Initializing Mitara AI RAG Pipeline ---")

# 1. Create a sample proprietary medical document in the data folder
os.makedirs("medical_data", exist_ok=True)
sample_text = """MITARA CLINICAL PROTOCOL 99-X:

For patients presenting with 'cybernetic overload' or 'glowing red eyes', immediately isolate the patient in a dark room and administer 50mg of Optic-Coolant.

For standard headaches, recommend hydration and standard ibuprofen.
"""

with open("medical_data/custom_protocol.txt", "w", encoding="utf-8") as f:
    f.write(sample_text)

print("[+] Created sample proprietary medical file: 'medical_data/custom_protocol.txt'")

# 2. Initialize RAG store (this automatically vectorizes and ingests the file)
print("[+] Initializing Vector Database & Embedding chunks...")
store = RAGStore(data_directory="medical_data")

# 3. Test Retrieval 1
query1 = "Patient complains of glowing red eyes"
print(f"\n[?] Querying Vector DB: '{query1}'")
results1 = store.retrieve_guidelines(query1, top_k=1)
print(f"    -> RAG Retrieved: {results1}")

# 4. Test Retrieval 2
query2 = "I have a normal headache"
print(f"\n[?] Querying Vector DB: '{query2}'")
results2 = store.retrieve_guidelines(query2, top_k=1)
print(f"    -> RAG Retrieved: {results2}")

print("\n--- RAG Test Complete ---")
