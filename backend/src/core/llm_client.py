from dataclasses import dataclass, field
import re

from ..config import settings

try:
	from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore[import-not-found]
except ModuleNotFoundError:
	ChatGoogleGenerativeAI = None


from dataclasses import dataclass, field
from typing import List, Any
from langchain_core.messages import AIMessage

@dataclass
class _LLMResponse:
    content: str
    tool_calls: List[Any] = field(default_factory=list)

class _FallbackLLM:
    def invoke(self, prompt, **kwargs):
        # Giả lập trả về một AIMessage chuẩn của LangChain
        content = _generate_fallback_content(str(prompt))
        return AIMessage(content=content, tool_calls=[])
        
    def bind_tools(self, tools, **kwargs):
        """
        Giả lập phương thức bind_tools để Node 1 không bị crash.
        Trong chế độ fallback, chúng ta không thực sự dùng tool, 
        chỉ trả về chính instance để giữ luồng code.
        """
        return self


_CODE_TEMPLATES = [
	(
		r"giai\s*th[uừ]a|factorial",
		"def factorial(n):\n"
		"    if n <= 1:\n"
		"        return 1\n"
		"    return n * factorial(n - 1)\n",
	),
	(
		r"fibonacci|fib",
		"def fib(n):\n"
		"    if n < 2:\n"
		"        return n\n"
		"    return fib(n - 1) + fib(n - 2)\n",
	),
	(
		r"palindrome|đối xứng",
		"def is_palindrome(s):\n"
		"    return s == s[::-1]\n",
	),
	(
		r"nguy[eê]n t[oố]|prime|is_prime",
		"def is_prime(n):\n"
		"    if n < 2:\n"
		"        return False\n"
		"    for i in range(2, int(n ** 0.5) + 1):\n"
		"        if n % i == 0:\n"
		"            return False\n"
		"    return True\n",
	),
	(
		r"chia|divid",
		"def divide(a, b):\n"
		"    return a / b\n",
	),
	(
		r"t[oổ]ng|sum.*list|sum.*array|sum.*m[aả]ng",
		"def sum_list(lst):\n"
		"    return sum(lst)\n",
	),
	(
		r"đảo ngược|reverse.*string|reverse.*str",
		"def reverse_string(s):\n"
		"    return s[::-1]\n",
	),
	(
		r"ucln|gcd|greatest common divisor",
		"def gcd(a, b):\n"
		"    while b:\n"
		"        a, b = b, a % b\n"
		"    return abs(a)\n",
	),
	(
		r"bcnn|lcm|least common multiple",
		"def lcm(a, b):\n"
		"    if a == 0 or b == 0:\n"
		"        return 0\n"
		"    def _gcd(x, y):\n"
		"        while y:\n"
		"            x, y = y, x % y\n"
		"        return abs(x)\n"
		"    return abs(a * b) // _gcd(a, b)\n",
	),
	(
		r"even|lẻ|chẵn|odd|is_even|is_odd",
		"def is_even(n):\n"
		"    return n % 2 == 0\n",
	),
	(
		r"max|min|lớn nhất|nhỏ nhất",
		"def find_max(lst):\n"
		"    return max(lst)\n",
	),
	(
		r"vowel|nguyên âm",
		"def count_vowels(s):\n"
		"    vowels = set('aeiouAEIOU')\n"
		"    return sum(1 for ch in s if ch in vowels)\n",
	),
	(
		r"sort|sắp xếp|sap xep",
		"def sort_list(lst):\n"
		"    return sorted(lst)\n",
	),
	(
		r"abs|absolute|giá trị tuyệt đối",
		"def absolute_value(n):\n"
		"    return abs(n)\n",
	),
]


def _generate_fallback_content(prompt: str) -> str:
	prompt_lower = prompt.lower()

	if "generate 2 to 5 test cases" in prompt_lower or "return only valid json" in prompt_lower:
		return ""

	for pattern, template in _CODE_TEMPLATES:
		if re.search(pattern, prompt_lower):
			return template

	return (
		"def solution(*args, **kwargs):\n"
		"    return None\n"
	)


def _build_llm():
    # 1. Trả về local fallback nếu chưa cài LangChain
    if ChatGoogleGenerativeAI is None:
        return _FallbackLLM()

    # 2. Lấy chuỗi keys từ settings (Hỗ trợ cả GOOGLE_API_KEYS và GOOGLE_API_KEY cũ)
    keys_str = getattr(settings, "GOOGLE_API_KEYS", getattr(settings, "GOOGLE_API_KEY", ""))
    
    # Tách chuỗi thành mảng các key hợp lệ
    api_keys = [k.strip() for k in keys_str.split(",") if k.strip()]

    # Trả về local fallback nếu file .env không có key nào
    if not api_keys:
        return _FallbackLLM()

    try:
        # 3. Tạo ra một "đội quân" LLM, mỗi LLM cầm 1 key khác nhau
        llm_instances = [
            ChatGoogleGenerativeAI(
                model="gemini-2.5-flash", 
                temperature=0.1, 
                api_key=key
            )
            for key in api_keys
        ]

        # 4. Kích hoạt Fallback của LangChain
        # Nếu LLM[0] bị lỗi (ví dụ: 429 Rate Limit), hệ thống tự động gọi LLM[1], LLM[2]...
        if len(llm_instances) > 1:
            return llm_instances[0].with_fallbacks(llm_instances[1:])
        else:
            return llm_instances[0]
            
    except Exception:
        # Nếu có bất kỳ lỗi nào khởi tạo, quay về phao cứu sinh Regex
        return _FallbackLLM()

llm = _build_llm()