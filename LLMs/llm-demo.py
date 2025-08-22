from langchain_openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

llm = OpenAI(model='gpt-3.5-turbo-instruct', temperature=0.1)

result = llm.invoke("Who is Narendra Modi?")

print(result)

## since llm dont have memory it wont remember the previous question
result = llm.invoke("how old is he?")

print(result)