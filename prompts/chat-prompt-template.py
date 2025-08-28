from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv()

chat = ChatOpenAI(model="gpt-4o-mini", temperature=0)

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "Translate the following sentence into {language}: {sentence}")
])

# Fill in variables
messages = chat_prompt.format_messages(
    language="Hindi",
    sentence="I love programming in Python."
)

print(messages)   # List of System + Human messages

response = chat.invoke(messages)
print(response.content)
