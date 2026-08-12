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
│   "metadata": {...},  ← GIỮ NGUYÊN                  │
│   "state": {...},     ← PHẢI CÓ LỊCH SỬ             │
│   "action": {...}     ← ROUTE ĐẾN NODE TIẾP THEO   │
│ }                                                   │
└─────────────────────────────────────────────────────┘
```

---

## 👥 Team Members & Trách Nhiệm

### 🔧 **Duy** (Infra & Orchestration)

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

### 📝 **Vinh** (Node 1: Code Generator)

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
    "code": null,
    "execution_result": {
      "stderr": null
    },
    "retry_count": 0
  }
}
```

**Đầu ra trả về:**
```json
{
  "metadata": {...},
  "state": {
    "code": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)",
    "history": [...]
  },
  "action": {
    "next_node": "code_executor",
    "message": "✅ Đã sinh code",
    "reasoning": "Code hợp lệ, sẵn sàng chạy"
  }
}
```

**Các file sẽ tạo:**
```
src/nodes/
├── base_node.py          ← Template (được cung cấp)
└── node_1_generator.py   ← Vinh code ở đây
```

**Quy tắc tuân thủ:**
- ✅ Trích code từ LLM response (thường là ```python code ```)
- ✅ Validate syntax code (try compile nó)
- ✅ Nếu error: Đọc `state.execution_result.stderr` từ Node 2, đặt vào prompt
- ✅ Luôn set `action.next_node = "code_executor"`
- ✅ Thêm entry vào `history` array

---

### ⚡ **Bằng** (Node 2: Code Executor)

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
  "metadata": {...},
  "state": {
    "execution_result": {
      "status": "success",
      "stdout": "factorial(5) = 120",
      "stderr": "",
      "exit_code": 0,
      "execution_time_ms": 45,
      "test_cases": [...]
    },
    "is_success": true,
    "history": [...]
  },
  "action": {
    "next_node": "critic_router",
    "message": "✅ Code chạy thành công!",
    "reasoning": "Tất cả test case pass"
  }
}
```

**Các file sẽ tạo:**
```
src/nodes/
└── node_2_executor.py   ← Bằng code ở đây
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

### 🔍 **Mẫn** (Node 3: Critic/Router)

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
  "metadata": {...},
  "state": {...},
  "action": {
    "next_node": "END_SUCCESS",
    "message": "🎉 Bài toán hoàn thành!",
    "reasoning": "is_success=true"
  }
}
```

**Các file sẽ tạo:**
```
src/nodes/
└── node_3_router.py   ← Mẫn code ở đây
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
│   │   ├── base_node.py              ← Template chung (tạo bởi Duy)
│   │   ├── node_1_generator.py       ← Của Vinh
│   │   ├── node_2_executor.py        ← Của Bằng
│   │   └── node_3_router.py          ← Của Mẫn
│   │
│   ├── core/
│   │   ├── workflow.py               ← Của Duy (LangGraph)
│   │   ├── llm_client.py             ← Của Duy
│   │   └── sandbox.py                ← Của Duy
│   │
│   └── schemas/
│       └── node_schema.py            ← Của Duy (Pydantic models)
│
├── tests/
│   ├── test_node_1.py                ← Của Vinh
│   ├── test_node_2.py                ← Của Bằng
│   ├── test_node_3.py                ← Của Mẫn
│   └── test_integration.py           ← Của Duy
│
├── docs/
│   ├── SCHEMA.md                     ← Của Duy (JSON format)
│   ├── DEVELOPMENT.md                ← **BẠN ĐANG ĐỌC FILE NÀY**
│   └── EXAMPLES.md                   ← Của Duy (Ví dụ)
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
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-06-05T10:00:00Z",
  "version": "1.0",
  "llm_model": "gpt-4"
}
```

**Quy tắc:** Mỗi node **PHẢI copy-paste** metadata từ input sang output (không sửa)

---

### **2. State - PHẢI APPEND HISTORY, KHÔNG XÓA**

```json
"state": {
  "requirement": "...",
  "code": "...",
  "execution_result": {...},
  "is_success": false,
  "retry_count": 0,
  "max_retries": 3,
  "history": [...]
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
  "next_node": "code_executor",
  "message": "✅ Đã sinh code",
  "reasoning": "Code hợp lệ..."
}
```

**Quy tắc:**
- Node 1 luôn set: `next_node = "code_executor"`
- Node 2 luôn set: `next_node = "critic_router"`
- Node 3 set 1 trong 3: `code_generator` (retry), `END_SUCCESS`, `END_FAILURE`

---

## 🚀 Các Bước Bắt Đầu Cho Mỗi Developer

### **Bước 1: Tạo Branch Riêng**

```bash
# Vinh (Node 1)
git checkout -b feature/node-1-generator

# Bằng (Node 2)
git checkout -b feature/node-2-executor

# Mẫn (Node 3)
git checkout -b feature/node-3-router

# Duy (Infrastructure)
git checkout -b infra/langgraph-setup
```

### **Bước 2: Đọc Tài Liệu**

1. **docs/SCHEMA.md** - Hiểu JSON format
2. **docs/DEVELOPMENT.md** - Tài liệu này
3. **docs/CONTRACT.md** (nếu có) - Interface chi tiết

---

## ⚠️ Common Mistakes (Tránh Những Lỗi Này)

### ❌ **Lỗi 1: Sửa Metadata**
```python
# SAI ❌
output["metadata"]["timestamp"] = new_time

# ĐÚNG ✓
output["metadata"] = input_data["metadata"]
```

### ❌ **Lỗi 2: Xóa History Entries**
```python
# SAI ❌
state["history"] = []

# ĐÚNG ✓
state["history"] = state.get("history", []) + [new_entry]
```

### ❌ **Lỗi 3: Set next_node Sai**
```python
# SAI ❌ (Node 1 set sang Node 3)
output["action"]["next_node"] = "critic_router"

# ĐÚNG ✓ (Node 1 → Node 2)
output["action"]["next_node"] = "code_executor"
```

### ❌ **Lỗi 5: Quên Tăng retry_count Ở Node 3 (Mẫn)**
```python
# SAI ❌
if should_retry:
    output["state"]["retry_count"] = retry_count

# ĐÚNG ✓
if should_retry:
    output["state"]["retry_count"] = retry_count + 1
```

---

## ✅ Checklist Trước Khi PR

- [ ] Đã đọc docs/SCHEMA.md
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

✅ Node 1 (Vinh) → Node 2 (Bằng) → Node 3 (Mẫn) → END

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

**Happy Coding! 🚀**

*Mọi thắc mắc → Tạo GitHub Issue hoặc tag Duy*
