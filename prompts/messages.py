from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv

load_dotenv()

chat = ChatOpenAI()

messages = [
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content="Who won the FIFA World Cup in 2018?"),
    AIMessage(content="France won the 2018 FIFA World Cup."),
    HumanMessage(content="Who was the captain of that team?")
]

result = chat.invoke(messages)
print(result.content)

