from langchain_google_genai import ChatGoogleGenerativeAI
from ..config import settings

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1, api_key=settings.GOOGLE_API_KEY)