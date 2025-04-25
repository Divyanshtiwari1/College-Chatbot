import os
import numpy as np
from pymongo import MongoClient
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Initialize SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize the LLM
os.environ["GOOGLE_API_KEY"] = "AIzaSyDzpYpw5loxzW4vEMytVw1gXPE-fldWYDw"
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

# Initialize memory for conversation history
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

# Function to find the most similar documents in MongoDB
def find_similar_documents(query_embedding, top_k=5):
    cursor = collection.find()
    similarities = []

    for record in cursor:
        text = record["text"]
        embedding = np.array(record["embedding"])
        
        # Compute cosine similarity between query and stored embedding
        similarity = np.dot(query_embedding, embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(embedding))
        similarities.append((text, similarity))
    
    # Sort by similarity and return top_k most similar texts
    similarities = sorted(similarities, key=lambda x: x[1], reverse=True)
    return similarities[:top_k]

# Function to handle user input and get responses
def chat_with_rag(user_input):
    # Generate embedding for the user query
    query_embedding = model.encode(user_input)
    
    # Find similar documents in MongoDB
    similar_documents = find_similar_documents(query_embedding)

    # Format the retrieved documents for the LLM
    context = " ".join([doc[0] for doc in similar_documents])

    # Prepare the input message for the LLM
    input_message = f"Context: {context}\nQuestion: {user_input}"

    # Use the `invoke` method to generate a response
    response = llm.invoke(input_message)
    
    # Print chat history
    print("\nChat History:")
    for message in memory.chat_memory.messages:
        print(f"{message.type}: {message.content}")
    
    # Return the text of the AIMessage object
    return response.content  # Access the content directly

while True:
    user_question = input("Ask a question (or type 'exit' to quit): ")
    if user_question.lower() == 'exit':
        break
    answer = chat_with_rag(user_question)
    print(f"\nAnswer: {answer}\n")

# Example conversation
print("Response:", chat_with_rag("How many total seats are there?"))
print("\nResponse:", chat_with_rag("In elec branch how many seats are there?"))
print("\nResponse:", chat_with_rag("is there any alumnini association?"))
print("\nResponse:", chat_with_rag("Can you provide some notable alumnini association members and contact?"))