from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence

load_dotenv()

model = ChatOpenAI(temperature=0.0)

# Define the first prompt template for a detailed report
template1 = PromptTemplate(
    template='Write a detailed report on {topic}',
    input_variables=['topic']
)

# Define the second prompt template for a summary
template2 = PromptTemplate(
    template='Write a 5 line summary on the following text. \n{text}',
    input_variables=['text']
)

parser = StrOutputParser()

# Create a chain using the templates, model, and parser
chain = template1 | model | parser | template2 | model | parser
# Invoke the chain with a topic and print the result
result = chain.invoke({'topic': 'Kim Kardashian'})
print(result)