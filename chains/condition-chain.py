from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.runnable import RunnableParallel, RunnableBranch, RunnableLambda
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Literal

# Load environment variables from a .env file
load_dotenv()

# Initialize the ChatOpenAI model
model = ChatOpenAI()

# Initialize a string output parser
parser = StrOutputParser()

# Define a Pydantic model for feedback sentiment
class Feedback(BaseModel):
    sentiment: Literal['positive', 'negative'] = Field(description='Give the sentiment of the feedback')

# Initialize a Pydantic output parser with the Feedback model
parser2 = PydanticOutputParser(pydantic_object=Feedback)

# Define a prompt template for classifying sentiment
prompt1 = PromptTemplate(
    template='Classify the sentiment of the following feedback text into postive or negative \n {feedback} \n {format_instruction}',
    input_variables=['feedback'],
    partial_variables={'format_instruction':parser2.get_format_instructions()}
)

# Create a chain for sentiment classification
classifier_chain = prompt1 | model | parser2

# Define a prompt template for responding to positive feedback
prompt2 = PromptTemplate(
    template='Write an appropriate response to this positive feedback \n {feedback}',
    input_variables=['feedback']
)

# Define a prompt template for responding to negative feedback
prompt3 = PromptTemplate(
    template='Write an appropriate response to this negative feedback \n {feedback}',
    input_variables=['feedback']
)

# Create a branching chain to handle positive and negative feedback differently
branch_chain = RunnableBranch(
    (lambda x:x.sentiment == 'positive', prompt2 | model | parser),
    (lambda x:x.sentiment == 'negative', prompt3 | model | parser),
    RunnableLambda(lambda x: "could not find sentiment")  # Fallback if sentiment is not found
)

# Combine the classifier chain and branch chain into a single chain
chain = classifier_chain | branch_chain

# Invoke the chain with a sample feedback and print the result
print(chain.invoke({'feedback': 'This is a beautiful phone'}))

# Print the chain graph in ASCII format
chain.get_graph().print_ascii()