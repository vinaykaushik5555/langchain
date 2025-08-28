
from typing import TypedDict

from langchain_openai import ChatOpenAI

from dotenv import load_dotenv

load_dotenv()

class ReviewResponse(TypedDict):
    summary: str
    sentiment: str
    name: str
    
model = ChatOpenAI()

structured_model = model.with_structured_output(ReviewResponse)

review= """’ve been using the Galaxy S24 Ultra for about three weeks now, and overall, I’m really happy with my purchase. The display is absolutely stunning – super bright and smooth, even outdoors. Watching videos and gaming feels amazing. The camera quality is top-notch, especially the zoom lens, which captures details I didn’t expect. Low-light shots also turned out way better than my old phone.

Performance-wise, it’s super fast and handles multitasking easily. I’ve played some heavy games without any lag. The battery easily lasts me a full day, sometimes even a day and a half with moderate use. Charging is fast, but I wish Samsung included the charger in the box.

On the downside, the phone is a bit bulky and heavy, so using it with one hand is tricky. Also, the price is definitely on the higher side. But considering the features, I think it’s worth it.

Would I recommend it? Yes, if you want a premium flagship with a great camera and long-term software updates. Just be ready for the size and cost. Review by Vinay"""

response = structured_model.invoke(review)
print(response)    