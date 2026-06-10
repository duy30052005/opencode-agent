# 🤖 Lightweight OpenCode Agent

**Hệ thống Agent tự viết code → chạy thử → đọc lỗi → sửa code**

Một nền tảng để học sinh hiểu rõ chu trình lập trình: **Write → Test → Debug → Fix**

---

## 📋 Mục Tiêu

Tạo một Agent thông minh giúp học sinh thấy được chi tiết từng bước:
1. 📝 **Code Generator** - Viết code từ đề bài
2. ▶️ **Code Executor** - Chạy thử code an toàn (Sandbox)
3. 🔍 **Critic/Router** - Kiểm tra kết quả, định hướng sửa lỗi

---

## 🏗️ Kiến Trúc

```
[User Input] 
    ↓
[Node 1: Code Generator (xCrepe)]
    ↓
[Node 2: Code Executor (TBD)]
    ↓
[Node 3: Critic/Router (oooreiP)]
    ↓
[Success/Failure]
```

---

## 👥 Team Assignment

| Node | Developer | Status | Branch |
|------|-----------|--------|--------|
| 🔧 Infra & Orchestration | `duy30052005` | 🟢 Active | `infra/langgraph-setup` |
| 📝 Code Generator (Node 1) | `xCrepe` | 🟢 Active | `feature/node-1-generator` |
| ▶️ Code Executor (Node 2) | `TBD` | 🟡 Waiting | `feature/node-2-executor` |
| 🔍 Critic/Router (Node 3) | `oooreiP` | 🟢 Active | `feature/node-3-router` |

---

## 📂 Project Structure

```
opencode-agent/
├── README.md
├── SCHEMA.md                    # 📋 JSON Schema documentation
├── requirements.txt
├── .env.example
├── .gitignore
│
├── docs/
│   ├── SCHEMA.md                # ✅ Unified JSON Schema
│   ├── CONTRACT.md              # ✅ Node Input/Output Contract
│   ├── INTEGRATION_GUIDE.md     # 🔗 How to integrate nodes
│   └── DEVELOPMENT_GUIDE.md     # 📖 Development guidelines
│
├── src/
│   ├── __init__.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── node_schema.py       # Unified JSON schema classes
│   │   └── validators.py        # Validation logic
│   │
│   ├── nodes/
│   │   ├── __init__.py
│   │   ├── base_node.py         # Base class for all nodes
│   │   ├── node_1_generator.py  # Code Generator (xCrepe)
│   │   ├── node_2_executor.py   # Code Executor (TBD)
│   │   └── node_3_router.py     # Critic/Router (oooreiP)
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── workflow.py          # LangGraph workflow
│   │   ├── sandbox.py           # Safe execution environment
│   │   └── llm_client.py        # LLM provider (OpenAI/Anthropic)
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py
│       └── helpers.py
│
├── tests/
│   ├── test_schemas.py
│   ├── test_nodes.py
│   └── test_integration.py
│
├── examples/
│   ├── factorial_demo.py
│   ├── division_demo.py
│   └── run_all_scenarios.py
│
└── .github/
    └── DEVELOPMENT.md
```

---

## 🎯 Key Features

- ✅ **Unified JSON Contract** - Mỗi node nhận/gửi cùng một format
- ✅ **Parallel Development** - Team có thể code độc lập
- ✅ **Safe Sandbox** - Chạy code không ảnh hưởng hệ thống
- ✅ **LLM Agnostic** - Support OpenAI & Anthropic
- ✅ **Streaming Feedback** - Hiển thị tiến trình real-time
- ✅ **Max Retries** - Giới hạn 3-5 lần sửa lỗi

---

## 📖 Getting Started

### 1. Clone & Setup

```bash
git clone https://github.com/duy30052005/opencode-agent.git
cd opencode-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API keys
```

### 2. Read Documentation

- 📋 **[SCHEMA.md](docs/SCHEMA.md)** - JSON format chi tiết
- 🔗 **[CONTRACT.md](docs/CONTRACT.md)** - Node Input/Output
- 📖 **[DEVELOPMENT_GUIDE.md](docs/DEVELOPMENT_GUIDE.md)** - Hướng dẫn code

### 3. Start Development

Mỗi developer sẽ:
1. Checkout branch riêng: `git checkout -b feature/node-{N}-{name}`
2. Implement theo interface đã định
3. Viết unit tests
4. Submit PR

---

## 🚀 Example Usage

```python
from src.core.workflow import AgentWorkflow

workflow = AgentWorkflow()
result = workflow.run(requirement="Viết hàm tính giai thừa của n")

print(result)
# {
#   "is_success": True,
#   "code": "def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)",
#   "execution_result": {...},
#   "history": [...]
# }
```

---

## 📝 License

MIT

---

## 🤝 Contributing

Xem [DEVELOPMENT_GUIDE.md](docs/DEVELOPMENT_GUIDE.md)
