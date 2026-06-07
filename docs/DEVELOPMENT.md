## 🛠️ Hướng Dẫn Phát Triển & Quy Tắc Chung

**Tài liệu này định nghĩa cách các team members làm việc song song mà vẫn đảm bảo LangGraph workflow chạy mượt.**

---

## 📌 Quy Tắc Vàng

Hãy ghi nhớ: **Mỗi node hoạt động độc lập nhưng phải tuân thủ cùng 1 Input/Output Format**

```
┌─────────────────────────────────────────────────────┐
│           INPUT JSON (từ node trước)                │
├─────────────────────────────────────────────────────┤
│ {                                                   │
│   "metadata": {...},                                │
│   "state": {...}                                    │
│ }                                                   │
└────────────────┬────────────────────────────────────┘
                 │
        ┌────────▼────────┐
        │   YOUR NODE     │  ← Bạn code ở đây
        │   (Xử lý logic) │
        └────────┬────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│           OUTPUT JSON (cho node sau)                │
├─────────────────────────────────────────────────────┤
│ {                                                   │
│   "metadata": {...},  ← CỔI COP NGUYÊN              │
│   "state": {...},     ← PHẢI CÓ LỊCH SỬ             │
│   "action": {...}     ← ROUTE ĐẾN NODE TIẾP THEO   │
│ }                                                   │
└─────────────────────────────────────────────────────┘
```

---

## 👥 Team Members & Trách Nhiệm

### ���� **duy30052005** (Infra & Orchestration)

**Trách nhiệm:**
- Tạo LangGraph workflow kết nối 3 nodes
- Tạo API/Interface để gọi workflow
- Setup CI/CD pipeline
- Quản lý dependencies & .env files

**Không cần code logic xử lý của từng node**

**Các file sẽ tạo:**
```
src/
├── core/
│   ├── workflow.py          ← LangGraph setup
│   ├── llm_client.py        ← OpenAI/Anthropic client
│   └── sandbox.py           ← Safe execution container
└── utils/
    ├── logger.py
    └── helpers.py
```

---

### 📝 **xCrepe** (Node 1: Code Generator)

**Trách nhiệm:**
- Nhận `requirement` (đề bài)
- Gọi LLM để sinh code
- Nếu lỗi (retry), đọc error log rồi sửa
- Trả về Python code hợp lệ

**Đầu vào nhận:**
```json
{
  "metadata": {...},
  "state": {
    "requirement": "Viết hàm tính giai thừa của n",
    "code": null,  // null lần đầu, hoặc lỗi code trong retry
    "execution_result": {
      "stderr": null  // null lần đầu, hoặc error log khi retry
    },
    "retry_count": 0  // 0, 1, 2, ...
  }
}
```

**Đầu ra trả về:**
```json
{
  "metadata": {...},  // GIỮ NGUYÊN
  "state": {
    "code": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)",
    "history": [
      {
        "attempt": 1,
        "node": "code_generator",
        "input": {...},
        "output": {...},
        "timestamp": "...",
        "duration_ms": 1250
      }
    ]
  },
  "action": {
    "next_node": "code_executor",  // LUÔN LÀ code_executor
    "message": "✅ Đã sinh code",
    "reasoning": "Code hợp lệ, sẵn sàng chạy"
  }
}
```

**Các file sẽ tạo:**
```
src/nodes/
├── base_node.py          ← Template (được cung cấp)
└── node_1_generator.py   ← XCrepe code ở đây
```

**Quy tắc tuân thủ:**
- ✅ Trích code từ LLM response (thường là ```python code ```)
- ✅ Validate syntax code (try compile nó)
- ✅ Nếu error: Đọc `state.execution_result.stderr` từ Node 2, đặt vào prompt
- ✅ Luôn set `action.next_node = "code_executor"`
- ✅ Thêm entry vào `history` array

---

### ⚡ **TBD** (Node 2: Code Executor)

**Trách nhiệm:**
- Nhận code Python từ Node 1
- Chạy code **an toàn** (trong sandbox - không virus hệ thống)
- Capture output & error logs
- Chạy test cases để kiểm tra code đúng hay sai
- Trả về kết quả chạy

**Đầu vào nhận:**
```json
{
  "metadata": {...},
  "state": {
    "code": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)",
    "requirement": "Viết hàm tính giai thừa của n",
    "retry_count": 0
  }
}
```

**Đầu ra trả về (case thành công):**
```json
{
  "metadata": {...},  // GIỮ NGUYÊN
  "state": {
    "execution_result": {
      "status": "success",
      "stdout": "factorial(5) = 120",
      "stderr": "",
      "exit_code": 0,
      "execution_time_ms": 45,
      "test_cases": [
        {
          "input": {"n": 5},
          "expected_output": "120",
          "actual_output": "120",
          "passed": true
        }
      ]
    },
    "is_success": true,
    "history": [...]
  },
  "action": {
    "next_node": "critic_router",  // LUÔN LÀ critic_router
    "message": "✅ Code chạy thành công!",
    "reasoning": "Tất cả test case pass"
  }
}
```

**Đầu ra trả về (case lỗi):**
```json
{
  "metadata": {...},
  "state": {
    "execution_result": {
      "status": "error",
      "stdout": "",
      "stderr": "ZeroDivisionError: division by zero",
      "exit_code": 1,
      "execution_time_ms": 120,
      "test_cases": [
        {
          "input": {"b": 0},
          "expected_output": "Error",
          "actual_output": "ZeroDivisionError",
          "passed": false
        }
      ]
    },
    "is_success": false,
    "history": [...]
  },
  "action": {
    "next_node": "critic_router",  // LUÔN LÀ critic_router
    "message": "❌ Code bị lỗi",
    "reasoning": "ZeroDivisionError khi test case b=0"
  }
}
```

**Các file sẽ tạo:**
```
src/nodes/
└── node_2_executor.py   ← TBD code ở đây
```

**Quy tắc tuân thủ:**
- ✅ Chạy code trong **sandbox** (RestrictedPython hoặc Docker)
- ✅ Timeout tối đa: **5 giây**
- ✅ Capture đầy đủ stderr/stdout
- ✅ Tạo test cases từ requirement (2-5 test cases)
- ✅ Set `is_success = True` CHỈ khi tất cả test cases pass
- ✅ Luôn set `action.next_node = "critic_router"`
- ✅ Capture full traceback nếu error

---

### 🔍 **oooreiP** (Node 3: Critic/Router)

**Trách nhiệm:**
- Kiểm tra kết quả từ Node 2
- **Logic quyết định** (không cần LLM):
  - Nếu `is_success = true` → Kết thúc (SUCCESS)
  - Nếu `is_success = false` + `retry_count < 3` → Quay lại Node 1 (sửa lỗi)
  - Nếu `retry_count >= 3` → Kết thúc (FAILURE)
- Tăng `retry_count` nếu quyết định retry
- Trả về thông báo cho giao diện

**Đầu vào nhận:**
```json
{
  "metadata": {...},
  "state": {
    "is_success": false,
    "execution_result": {
      "status": "error",
      "stderr": "ZeroDivisionError: division by zero"
    },
    "retry_count": 0,
    "max_retries": 3
  }
}
```

**Đầu ra trả về (case thành công):**
```json
{
  "metadata": {...},  // GIỮ NGUYÊN
  "state": {...},
  "action": {
    "next_node": "END_SUCCESS",  // KẾT THÚC
    "message": "🎉 Bài toán hoàn thành!",
    "reasoning": "is_success=true"
  }
}
```

**Đầu ra trả về (case retry):**
```json
{
  "metadata": {...},
  "state": {
    "retry_count": 1,  // TĂNG từ 0 lên 1
    "history": [...]
  },
  "action": {
    "next_node": "code_generator",  // QUAY LẠI NODE 1
    "message": "🔧 Phát hiện lỗi! Agent sẽ sửa...",
    "reasoning": "retry_count=1, chưa quá max_retries=3"
  }
}
```

**Đầu ra trả về (case hết cơ hội):**
```json
{
  "metadata": {...},
  "state": {
    "retry_count": 3,
    "history": [...]
  },
  "action": {
    "next_node": "END_FAILURE",  // KẾT THÚC THẤT BẠI
    "message": "⚠️ Agent chưa tìm giải pháp sau 3 lượt thử",
    "reasoning": "retry_count=3 >= max_retries=3"
  }
}
```

**Các file sẽ tạo:**
```
src/nodes/
└── node_3_router.py   ← oooreiP code ở đây
```

**Quy tắc tuân thủ:**
- ✅ Logic quyết định đơn giản (không phức tạp)
- ✅ Luôn tăng `retry_count` khi routing về Node 1
- ✅ Giữ nguyên tất cả history
- ✅ 3 giá trị `next_node`: `code_generator`, `END_SUCCESS`, `END_FAILURE`
- ✅ Message phải giáo dục (giúp học sinh hiểu)

---

## 📂 Cấu Trúc Thư Mục & Quy Tắc Đặt Tên

```
opencode-agent/
│
├── src/
│   ├── nodes/
│   │   ├── base_node.py              ← Template chung (tạo bởi duy30052005)
│   │   ├── node_1_generator.py       ← Của xCrepe
│   │   ├── node_2_executor.py        ← Của TBD
│   │   └── node_3_router.py          ← Của oooreiP
│   │
│   ├── core/
│   │   ├── workflow.py               ← Của duy30052005 (LangGraph)
│   │   ├── llm_client.py             ← Của duy30052005
│   │   └── sandbox.py                ← Của duy30052005
│   │
│   └── schemas/
│       └── node_schema.py            ← Của duy30052005 (Pydantic models)
│
├── tests/
│   ├── test_node_1.py                ← Của xCrepe
│   ├── test_node_2.py                ← Của TBD
│   ├── test_node_3.py                ← Của oooreiP
│   └── test_integration.py           ← Của duy30052005
│
├── docs/
│   ├── SCHEMA.md                     ← Của duy30052005 (JSON format)
│   ├── DEVELOPMENT.md                ← **BẠN ĐANG ĐỌC FILE NÀY**
│   └── EXAMPLES.md                   ← Của duy30052005 (Ví dụ)
│
├── .env.example                      ← Template env
├── requirements.txt                  ← Dependencies
└── README.md                         ← Overview dự án
```

---

## 🎯 Quy Tắc JSON Mà Ai Cũng Phải Tuân Thủ

### **1. Metadata - PHẢI GIỮ NGUYÊN NGUYÊN BẢN**

```json
"metadata": {
  "task_id": "550e8400-e29b-41d4-a716-446655440000",  // UUID
  "timestamp": "2026-06-05T10:00:00Z",                // ISO-8601
  "version": "1.0",                                   // Phiên bản schema
  "llm_model": "gpt-4"                                // LLM được sử dụng
}
```

**Quy tắc:** Mỗi node **PHẢI copy-paste** metadata từ input sang output (không sửa)

---

### **2. State - PHẢI APPEND HISTORY, KHÔNG XÓA**

```json
"state": {
  "requirement": "...",           // CỐ ĐỊNH từ đầu
  "code": "...",                  // CẬP NHẬT bởi Node 1
  "execution_result": {...},      // CẬP NHẬT bởi Node 2
  "is_success": false,            // CẬP NHẬT bởi Node 2
  "retry_count": 0,               // CẬP NHẬT bởi Node 3 nếu retry
  "max_retries": 3,               // CỐ ĐỊNH
  "history": [
    {
      "attempt": 1,               // Lần chạy (1, 2, 3...)
      "node": "code_generator",   // Node nào tạo entry này
      "input": {...},             // Input node nhận
      "output": {...},            // Output node trả ra
      "timestamp": "...",         // ISO-8601
      "duration_ms": 1250         // Thời gian xử lý (ms)
    },
    {
      "attempt": 2,
      "node": "code_executor",
      "input": {...},
      "output": {...},
      "timestamp": "...",
      "duration_ms": 450
    }
  ]
}
```

**Quy tắc:** 
- Mỗi node **PHẢI thêm 1 entry** vào `history`
- Không xóa entry cũ
- `attempt` tự động tăng (1, 2, 3...)

---

### **3. Action - QUYẾT ĐỊNH ROUTE TIẾP THEO**

```json
"action": {
  "next_node": "code_executor",   // Giá trị: code_generator | code_executor | critic_router | END_SUCCESS | END_FAILURE
  "message": "✅ Đã sinh code",   // Thông báo cho giao diện (người dùng nhìn thấy)
  "reasoning": "Code hợp lệ..."   // Giải thích logic (không bắt buộc nhưng tốt)
}
```

**Quy tắc:**
- Node 1 luôn set: `next_node = "code_executor"`
- Node 2 luôn set: `next_node = "critic_router"`
- Node 3 set 1 trong 3: `code_generator` (retry), `END_SUCCESS`, `END_FAILURE`

---

## 📋 Luồng Dữ Liệu Chi Tiết

### **Scenario 1: Thành công ngay lần đầu**

```
User: "Viết hàm tính giai thừa"
         │
         ▼
[Node 1] Sinh code: def factorial(n): ...
         │
         ├─ Metadata: giữ nguyên ✓
         ├─ State.code: "def factorial..."
         ├─ State.history.append(attempt=1, node=code_generator, ...)
         ├─ Action.next_node = "code_executor"
         │
         ▼
[Node 2] Chạy code + test cases
         │
         ├─ Metadata: giữ nguyên ✓
         ├─ State.execution_result: {status: success, stdout: ..., test_cases: [...]}
         ├─ State.is_success = true ✓
         ├─ State.history.append(attempt=1, node=code_executor, ...)
         ├─ Action.next_node = "critic_router"
         │
         ▼
[Node 3] Kiểm tra: is_success=true
         │
         ├─ Metadata: giữ nguyên ✓
         ├─ State: giữ nguyên, chỉ append history
         ├─ State.history.append(attempt=1, node=critic_router, ...)
         ├─ Action.next_node = "END_SUCCESS" 🎉
         │
         ▼
    THÀNH CÔNG!
```

---

### **Scenario 2: Lỗi lần đầu, sửa thành công lần 2**

```
User: "Viết hàm chia a/b"
         │
         ▼
[Node 1 - Attempt 1] Sinh code: def divide(a, b): return a/b
         │
         ├─ State.code: "def divide..."
         ├─ State.history.append(attempt=1, ...)
         ├─ Action.next_node = "code_executor"
         │
         ▼
[Node 2 - Attempt 1] Chạy code: ZeroDivisionError
         │
         ├─ State.execution_result: {status: error, stderr: "ZeroDivisionError..."}
         ├─ State.is_success = false ✗
         ├─ State.history.append(attempt=1, ...)
         ├─ Action.next_node = "critic_router"
         │
         ▼
[Node 3 - Attempt 1] Kiểm tra: is_success=false && retry_count (0) < max_retries (3)
         │
         ├─ State.retry_count = 1 (TĂNG)
         ├─ State.history.append(attempt=1, ...)
         ├─ Action.next_node = "code_generator" (RETRY) ↻
         │
         ▼
[Node 1 - Attempt 2] Đọc error: "ZeroDivisionError", sinh code mới
         │
         ├─ Input nhận có: state.execution_result.stderr = "ZeroDivisionError..."
         ├─ Sinh code sửa: def divide(a, b): 
         │                   if b == 0: return None
         │                   return a/b
         ├─ State.code: "def divide... (sửa)"
         ├─ State.history.append(attempt=2, ...)
         ├─ Action.next_node = "code_executor"
         │
         ▼
[Node 2 - Attempt 2] Chạy code: Thành công!
         │
         ├─ State.execution_result: {status: success, test_cases: all passed}
         ├─ State.is_success = true ✓
         ├─ State.history.append(attempt=2, ...)
         ├─ Action.next_node = "critic_router"
         │
         ▼
[Node 3 - Attempt 2] Kiểm tra: is_success=true
         │
         ├─ State.history.append(attempt=2, ...)
         ├─ Action.next_node = "END_SUCCESS" 🎉
         │
         ▼
    THÀNH CÔNG SAU 2 LẦN!
```

---

## 🚀 Các Bước Bắt Đầu Cho Mỗi Developer

### **Bước 1: Tạo Branch Riêng**

```bash
# xCrepe
git checkout -b feature/node-1-generator

# TBD
git checkout -b feature/node-2-executor

# oooreiP
git checkout -b feature/node-3-router

# duy30052005
git checkout -b infra/langgraph-setup
```

---

### **Bước 2: Đọc Tài Liệu**

1. **docs/SCHEMA.md** - Hiểu JSON format
2. **docs/DEVELOPMENT.md** - Tài liệu này
3. **docs/CONTRACT.md** (nếu có) - Interface chi tiết

---

### **Bước 3: Copy Template Base Node**

```bash
# Mỗi node sẽ có file:
src/nodes/base_node.py          # Template (được cung cấp)
src/nodes/node_X_yourname.py    # Của bạn
```

**base_node.py chứa:**
```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseNode(ABC):
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input và return output theo schema"""
        pass
```

---

### **Bước 4: Implement Node Của Bạn**

**Ví dụ Node 1 (xCrepe):**

```python
# src/nodes/node_1_generator.py

from .base_node import BaseNode
from typing import Dict, Any
import json

class CodeGenerator(BaseNode):
    def __init__(self, llm_config):
        super().__init__("code_generator")
        self.llm_config = llm_config
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # 1. Lấy metadata & state từ input
        metadata = input_data["metadata"]
        state = input_data["state"]
        
        requirement = state["requirement"]
        error_log = state.get("execution_result", {}).get("stderr")
        retry_count = state.get("retry_count", 0)
        
        # 2. Build prompt (nếu retry, thêm error log vào)
        if error_log:
            prompt = f"""
            Original requirement: {requirement}
            Previous code had error: {error_log}
            Please fix the code...
            """
        else:
            prompt = f"Write Python code for: {requirement}"
        
        # 3. Gọi LLM (OpenAI hoặc Anthropic)
        code = await self.call_llm(prompt)
        
        # 4. Validate code (compile check)
        self.validate_code(code)
        
        # 5. Tạo output theo schema
        output = {
            "metadata": metadata,  # GIỮ NGUYÊN
            "state": {
                **state,  # Copy state cũ
                "code": code,
                "retry_count": retry_count,
                "history": state.get("history", []) + [
                    {
                        "attempt": retry_count + 1,
                        "node": "code_generator",
                        "input": input_data,
                        "output": {"code": code},
                        "timestamp": self.get_iso_timestamp(),
                        "duration_ms": 1250
                    }
                ]
            },
            "action": {
                "next_node": "code_executor",
                "message": "✅ Đã sinh code",
                "reasoning": "Code hợp lệ, sẵn sàng chạy"
            }
        }
        
        return output
    
    async def call_llm(self, prompt: str) -> str:
        # Call OpenAI/Anthropic here
        pass
    
    def validate_code(self, code: str) -> bool:
        try:
            compile(code, '<string>', 'exec')
            return True
        except SyntaxError as e:
            raise ValueError(f"Invalid code: {e}")
```

---

### **Bước 5: Viết Unit Tests**

```python
# tests/test_node_1.py

import pytest
from src.nodes.node_1_generator import CodeGenerator

@pytest.mark.asyncio
async def test_generate_factorial_code():
    generator = CodeGenerator(llm_config={})
    
    input_data = {
        "metadata": {
            "task_id": "test-1",
            "timestamp": "2026-06-05T10:00:00Z",
            "version": "1.0",
            "llm_model": "gpt-4"
        },
        "state": {
            "requirement": "Write factorial function",
            "code": None,
            "execution_result": {"status": "pending"},
            "retry_count": 0,
            "history": []
        }
    }
    
    result = await generator.process(input_data)
    
    # Kiểm tra output
    assert "def factorial" in result["state"]["code"]
    assert result["action"]["next_node"] == "code_executor"
    assert len(result["state"]["history"]) == 1
    assert result["metadata"] == input_data["metadata"]

@pytest.mark.asyncio
async def test_generator_with_error_retry():
    generator = CodeGenerator(llm_config={})
    
    input_data = {
        "metadata": {...},
        "state": {
            "requirement": "...",
            "code": "def divide(a, b): return a/b",
            "execution_result": {
                "stderr": "ZeroDivisionError: division by zero"
            },
            "retry_count": 1,
            "history": [...]
        }
    }
    
    result = await generator.process(input_data)
    
    # Kiểm tra code đã được sửa
    assert "if b == 0" in result["state"]["code"]
```

---

### **Bước 6: Submit PR**

```bash
git add .
git commit -m "feat: implement Node 1 (Code Generator) with LLM integration"
git push origin feature/node-1-generator
```

**PR description phải bao gồm:**
- ✅ Mô tả logic của node
- ✅ Cách node xử lý input/output
- ✅ Test coverage
- ✅ Link đến SCHEMA.md & DEVELOPMENT.md

---

## ⚠️ Common Mistakes (Tránh Những Lỗi Này)

### ❌ **Lỗi 1: Sửa Metadata**
```python
# SAI ❌
output["metadata"]["timestamp"] = new_time  # Đừng sửa!

# ĐÚNG ✓
output["metadata"] = input_data["metadata"]  # Copy nguyên bản
```

---

### ❌ **Lỗi 2: Xóa History Entries**
```python
# SAI ❌
state["history"] = []  # Xóa hết lịch sử!

# ĐÚNG ✓
state["history"] = state.get("history", []) + [new_entry]  # Append
```

---

### ❌ **Lỗi 3: Set next_node Sai**
```python
# SAI ❌ (Node 1 set sang Node 3 luôn)
output["action"]["next_node"] = "critic_router"

# ĐÚNG ✓ (Node 1 phải send sang Node 2 trước)
output["action"]["next_node"] = "code_executor"
```

---

### ❌ **Lỗi 4: Không Validate Input/Output**
```python
# SAI ❌
async def process(self, input_data):
    # Không check input format
    code = input_data["state"]["code"]  # Crash nếu key không tồn tại

# ĐÚNG ✓
async def process(self, input_data):
    self.validate_input(input_data)  # Check schema
    state = input_data.get("state", {})
    code = state.get("code")  # Safe get
```

---

### ❌ **Lỗi 5: Quên Tăng retry_count Ở Node 3**
```python
# SAI ❌ (Node 3 quên tăng retry_count)
if should_retry:
    output["state"]["retry_count"] = retry_count  # Không thay đổi

# ĐÚNG ✓
if should_retry:
    output["state"]["retry_count"] = retry_count + 1  # Tăng 1
```

---

## 🧪 Testing Strategy

### **Test Pyramid:**

```
           /\\
          /  \\  Integration Tests
         /────\\  (workflow end-to-end)
        /      \\
       /────────\\
      /          \\  Unit Tests per Node
     /            \\  (input/output contract)
    /──────────────\\
   /                \\
```

---

### **Integration Test (duy30052005)**

```python
# tests/test_integration.py

async def test_full_workflow_success():
    workflow = AgentWorkflow()
    
    result = await workflow.run(
        requirement="Write factorial function"
    )
    
    assert result["is_success"] == True
    assert result["action"]["next_node"] == "END_SUCCESS"
    assert len(result["history"]) == 3  # 3 nodes
```

---

### **Contract Test (Mỗi developer)**

```python
# tests/test_node_X.py

async def test_input_output_contract():
    """Verify node follows JSON schema"""
    node = YourNode()
    
    input_data = load_valid_input()
    output = await node.process(input_data)
    
    # Validate output schema
    validate_output_schema(output)
    
    assert "metadata" in output
    assert "state" in output
    assert "action" in output
```

---

## 📞 Communication Rules

### **Khi cần hỗ trợ:**

1. **Nếu chưa hiểu** → Hỏi duy30052005 về LangGraph setup
2. **Nếu lỗi schema** → Check docs/SCHEMA.md trước
3. **Nếu lỗi dependency** → Update requirements.txt + notify duy30052005

### **Commit Messages (Format)**

```
feat: implement Node X (XYZ)
docs: add documentation for SCHEMA
fix: correct retry logic in Node 3
test: add unit tests for Node 1
```

---

## ✅ Checklist Trước Khi PR

- [ ] Tôi đã đọc docs/SCHEMA.md
- [ ] Code tuân thủ JSON contract
- [ ] Output schema khớp với requirement
- [ ] Metadata được giữ nguyên
- [ ] History được append (không xóa)
- [ ] next_node set đúng
- [ ] Unit tests coverage >= 80%
- [ ] Không có hardcoded config (dùng .env)
- [ ] Docstring đầy đủ
- [ ] Error handling xử lý

---

## 🎯 Success Criteria

Workflow sẽ chạy **thành công** khi:

✅ Node 1 → Node 2 → Node 3 → END (trong 1 vòng lặp hoặc nhiều lần retry)

✅ Mỗi node:
- Nhận input đúng schema
- Xử lý logic riêng
- Trả output đúng schema
- Không modify metadata
- Append history

✅ Toàn bộ flow:
- Hỗ trợ auto-retry đến 3 lần
- Dừng tự động khi hết cơ hội
- Hiển thị thông báo cho người dùng

---

## 📚 Tài Liệu Tham Khảo

- **docs/SCHEMA.md** - JSON format chi tiết
- **docs/CONTRACT.md** - Interface definitions
- **README.md** - Project overview
- **examples/** - Ví dụ chạy thử

---

**Happy Coding! 🚀**

*Mọi thắc mắc → Tạo GitHub Issue hoặc tag duy30052005*
