from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Initialize the ChatOpenAI model with specific parameters
model = ChatOpenAI(model='gpt-4', temperature=1, max_completion_tokens=30)

# CHANGE: Initialize a list to maintain the conversation history
# This list will store the sequence of interactions between the user and the assistant
conversation_history = []

# First query to the model
question1 = "Who is Narendra Modi?"
# Append the user's question to the conversation history
conversation_history.append({"role": "user", "content": question1})
# Invoke the model with the current conversation history
result1 = model.invoke(conversation_history)
# Append the model's response to the conversation history
conversation_history.append({"role": "assistant", "content": result1.content})

# Print the model's response to the first query
print(result1.content)

# Second query to the model
question2 = "what is his age in years?"
# Append the user's question to the conversation history
conversation_history.append({"role": "user", "content": question2})
# Invoke the model with the updated conversation history
result2 = model.invoke(conversation_history)
# Append the model's response to the conversation history
conversation_history.append({"role": "assistant", "content": result2.content})

# Print the model's response to the second query
print(result2.content)