from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Initialize the OpenAIEmbeddings model with specified parameters
# 'model' specifies the model version, and 'dimensions' specifies the size of the output vector
embedding = OpenAIEmbeddings(model='text-embedding-3-large', dimensions=32)

# Generate a 32-dimensional embedding for the input text
result = embedding.embed_query("Delhi is the capital of India")

# Print the resulting embedding vector
print(result)