from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Load environment variables from the .env file
load_dotenv()

# Initialize the OpenAIEmbeddings model with specified parameters
embedding = OpenAIEmbeddings(model='text-embedding-3-large', dimensions=300)

# List of documents to be embedded
documents = [
    "Virat Kohli is an Indian cricketer known for his aggressive batting and leadership.",
    "MS Dhoni is a former Indian captain famous for his calm demeanor and finishing skills.",
    "Sachin Tendulkar, also known as the 'God of Cricket', holds many batting records.",
    "Rohit Sharma is known for his elegant batting and record-breaking double centuries.",
    "Jasprit Bumrah is an Indian fast bowler known for his unorthodox action and yorkers."
]

# Query to compare against the documents
query = 'tell me about bumrah'

# Generate embeddings for the documents
doc_embeddings = embedding.embed_documents(documents)

# Generate an embedding for the query
query_embedding = embedding.embed_query(query)

# Calculate cosine similarity between the query embedding and each document embedding
# Cosine similarity measures the cosine of the angle between two vectors, providing a value between -1 and 1.
# A value of 1 indicates identical vectors, 0 indicates orthogonality (no similarity), and -1 indicates completely opposite vectors.
scores = cosine_similarity([query_embedding], doc_embeddings)[0]

# Find the index of the document with the highest similarity score
index, score = sorted(list(enumerate(scores)), key=lambda x: x[1])[-1]

# Print the query, most similar document, and similarity score
print(query)
print(documents[index])
print("similarity score is:", score)