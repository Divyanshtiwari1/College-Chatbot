import os
from pymongo import MongoClient
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URI = 'mongodb+srv://sarveshatawane03:y2flIDD1EmOaU5de@cluster0.sssmr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("iiitn")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client["miniproject"]
collection = db["iiitn"]

# Initialize SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Read data from data.txt
with open('data.txt', 'r') as file:
    data = file.read()

# Function to create chunks with overlap
def create_chunks(text, chunk_size=200, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

# Process and store each chunk and its embedding into MongoDB
chunks = create_chunks(data)
for chunk in chunks:
    text = chunk.strip()
    
    # Generate the embedding for the chunk
    embedding = model.encode(text).tolist()  # Convert the embedding to a list for storage
    
    # Prepare the document to store
    document = {
        "text": text,
        "embedding": embedding
    }
    
    # Insert the document into the MongoDB collection
    collection.insert_one(document)

print("Data and embeddings have been successfully stored in MongoDB.")
