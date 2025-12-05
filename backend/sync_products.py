import requests

print("Syncing all products to HuggingFace ChromaDB...")
response = requests.post("http://127.0.0.1:8000/sync-to-rag")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
