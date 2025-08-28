from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Initialize the ChatOpenAI model with a temperature setting for response variability
model = ChatOpenAI(temperature=0.1)

# Initialize an empty list to store the chat history
chat_history = []

while True:
    # Prompt the user for input
    user_input = input("You: ")
    
    # Check if the user wants to exit the chat
    if user_input.lower() in ['exit', 'quit']:
        print("Exiting the chat. Goodbye!")
        break
    
    # Append the user's input to the chat history
    chat_history.append(user_input)
    
    # Invoke the model to get a response based on the chat history
    response = model.invoke(chat_history).content
    
    # Append the model's response to the chat history
    chat_history.append(response)
    
    # Display the model's response to the user
    print(f"Bot: {response}")

# Print the entire chat history after exiting the loop
print(chat_history)