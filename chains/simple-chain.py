from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()


model = ChatOpenAI()

template= PromptTemplate(template='Give me 5 interasting facts about {topic}', input_variables=['topic'])

parser= StrOutputParser()

chain= template | model | parser

result= chain.invoke({'topic':'Cats'})
print(result)
