from ..config import settings

try:
	from langchain_google_genai import ChatGoogleGenerativeAI
except ModuleNotFoundError:
	ChatGoogleGenerativeAI = None


class _MissingLLM:
	def invoke(self, prompt):
		raise RuntimeError("langchain_google_genai is not installed")


if ChatGoogleGenerativeAI is None:
	llm = _MissingLLM()
else:
	llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1, api_key=settings.GOOGLE_API_KEY)