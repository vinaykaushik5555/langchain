# file: structured_output_pydantic.py
from dotenv import load_dotenv
load_dotenv()  # loads OPENAI_API_KEY from .env

from pydantic import BaseModel, Field
from typing import List
from langchain_openai import ChatOpenAI

# 1) Define your schema
class Product(BaseModel):
    name: str = Field(description="Product display name")
    price_inr: float = Field(description="Price in Indian Rupees")
    in_stock: bool
    tags: List[str] = []

# 2) Initialize model (any OpenAI chat model that supports tool/function calling or JSON mode)
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# 3) Bind schema; returns a Runnable that yields a Product instance
structured_llm = llm.with_structured_output(Product)

# 4) Invoke
prompt = (
    "Create a fake e-commerce product for a baby brand with realistic data. "
    "Keep tags short and relevant."
)
result: Product = structured_llm.invoke(prompt)

print(type(result))         # <class '__main__.Product'>
print(result.model_dump())  # dict with validated fields
