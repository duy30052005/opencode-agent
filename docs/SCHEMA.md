## 📋 Unified JSON Schema for All Nodes

Tài liệu này định nghĩa **contract duy nhất** cho tất cả các nodes. Mỗi node phải tuân thủ format này để tương tác được với nhau.

---

## 🎯 Core State Structure

```json
{
  "metadata": {
    "task_id": "string (UUID v4)",
    "timestamp": "string (ISO-8601)",
    "version": "string (1.0)",
    "llm_model": "string (gpt-4 | claude-3-opus)"
  },
  "state": {
    "requirement": "string - Đề bài/Yêu cầu từ người dùng",
    "code": "string - Mã nguồn hiện tại (Python)",
    "execution_result": {
      "status": "string (pending | success | error | timeout)",
      "stdout": "string - Output của chương trình",
      "stderr": "string - Error log",
      "exit_code": "integer (0 = success, non-zero = error)",
      "execution_time_ms": "integer",
      "test_cases": [
        {
          "input": "string | dict",
          "expected_output": "string | dict",
          "actual_output": "string | dict",
          "passed": "boolean"
        }
      ]
    },
    "is_success": "boolean - Có vượt qua tất cả test cases?",
    "retry_count": "integer - Số lần đã sửa (0, 1, 2, ...)",
    "max_retries": "integer - Giới hạn (default: 3)",
    "history": [
      {
        "attempt": "integer (1, 2, 3, ...)",
        "node": "string (code_generator | code_executor | critic_router)",
        "input": "object - Input nhận được",
        "output": "object - Output trả ra",
        "timestamp": "string (ISO-8601)",
        "duration_ms": "integer"
      }
    ]
  },
  "action": {
    "next_node": "string (code_generator | code_executor | critic_router | END_SUCCESS | END_FAILURE)",
    "message": "string - Thông báo cho giao diện hiển thị",
    "reasoning": "string - Lý do chọn next_node (để học sinh hiểu)"
  }
}
```

---

## 🔄 Node Input/Output Specifications

### **Node 1: Code Generator** (xCrepe)

**INPUT:**
```json
{
  "metadata": {...},
  "state": {
    "requirement": "Viết hàm tính giai thừa của n",
    "code": null,  // Lần đầu là null
    "execution_result": {
      "status": "pending",
      "stderr": null  // Hoặc error log nếu là lần retry
    },
    "retry_count": 0,
    "max_retries": 3,
    "history": []
  }
}
```

**OUTPUT:**
```json
{
  "metadata": {...},
  "state": {
    "requirement": "...",
    "code": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)",
    "execution_result": {
      "status": "pending"
    },
    "retry_count": 0,
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
    "next_node": "code_executor",
    "message": "✅ Đã sinh code. Bây giờ chạy thử...",
    "reasoning": "Code hoàn chỉnh, sẵn sàng để execute"
  }
}
```

**Lưu ý:**
- LLM được gọi tại đây (OpenAI/Anthropic)
- Nếu `retry_count > 0`, hãy đặt context lỗi vào prompt
- Output phải là valid Python code

---

### **Node 2: Code Executor** (TBD)

**INPUT:**
```json
{
  "metadata": {...},
  "state": {
    "requirement": "...",
    "code": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)",
    "execution_result": {
      "status": "pending"
    },
    "retry_count": 0,
    "max_retries": 3,
    "history": [...]
  }
}
```

**OUTPUT (Success Case):**
```json
{
  "metadata": {...},
  "state": {
    "requirement": "...",
    "code": "...",
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
        },
        {
          "input": {"n": 0},
          "expected_output": "1",
          "actual_output": "1",
          "passed": true
        }
      ]
    },
    "is_success": true,
    "retry_count": 0,
    "history": [...]
  },
  "action": {
    "next_node": "critic_router",
    "message": "✅ Code chạy thành công!",
    "reasoning": "Không có lỗi, tất cả test case pass"
  }
}
```

**OUTPUT (Error Case):**
```json
{
  "metadata": {...},
  "state": {
    "requirement": "...",
    "code": "...",
    "execution_result": {
      "status": "error",
      "stdout": "",
      "stderr": "ZeroDivisionError: division by zero at line 5",
      "exit_code": 1,
      "execution_time_ms": 120,
      "test_cases": [
        {
          "input": {"a": 10, "b": 2},
          "expected_output": "5",
          "actual_output": "5",
          "passed": true
        },
        {
          "input": {"a": 10, "b": 0},
          "expected_output": "Error",
          "actual_output": "ZeroDivisionError",
          "passed": false
        }
      ]
    },
    "is_success": false,
    "retry_count": 0,
    "history": [...]
  },
  "action": {
    "next_node": "critic_router",
    "message": "❌ Code bị lỗi!",
    "reasoning": "ZeroDivisionError khi b=0"
  }
}
```

**Lưu ý:**
- PHẢI chạy trong sandbox (không thực thi trực tiếp)
- Timeout limit: 5 giây
- Test cases nên được định sẵn hoặc trích từ requirement
- stderr phải chi tiết (traceback)

---

### **Node 3: Critic/Router** (oooreiP)

**INPUT:**
```json
{
  "metadata": {...},
  "state": {
    "requirement": "...",
    "code": "...",
    "execution_result": {
      "status": "error",
      "stderr": "ZeroDivisionError: division by zero"
    },
    "is_success": false,
    "retry_count": 0,
    "max_retries": 3,
    "history": [...]
  }
}
```

**OUTPUT (Pass Case - End Success):**
```json
{
  "metadata": {...},
  "state": {
    "requirement": "...",
    "code": "...",
    "execution_result": {...},
    "is_success": true,
    "retry_count": 0,
    "history": [...]
  },
  "action": {
    "next_node": "END_SUCCESS",
    "message": "🎉 Bài toán hoàn thành! Code đã vượt qua tất cả test cases.",
    "reasoning": "is_success=true, tất cả test case passed"
  }
}
```

**OUTPUT (Retry Case):**
```json
{
  "metadata": {...},
  "state": {
    "requirement": "...",
    "code": "...",
    "execution_result": {
      "status": "error",
      "stderr": "ZeroDivisionError: division by zero"
    },
    "is_success": false,
    "retry_count": 1,
    "max_retries": 3,
    "history": [...]
  },
  "action": {
    "next_node": "code_generator",
    "message": "🔧 Phát hiện lỗi! Agent sẽ sửa lỗi...",
    "reasoning": "is_success=false, retry_count (1) < max_retries (3). Gửi lỗi cho Node 1 để sửa."
  }
}
```

**OUTPUT (Max Retries Exceeded):**
```json
{
  "metadata": {...},
  "state": {
    "requirement": "...",
    "code": "...",
    "execution_result": {...},
    "is_success": false,
    "retry_count": 3,
    "max_retries": 3,
    "history": [...]
  },
  "action": {
    "next_node": "END_FAILURE",
    "message": "⚠️ Agent chưa tìm được giải pháp sau 3 lượt thử. Đây là code cuối cùng và lỗi để bạn cùng nghiên cứu.",
    "reasoning": "retry_count (3) >= max_retries (3). Dừng luồng để tránh lặp vô hạn."
  }
}
```

**Lưu ý:**
- Đây có thể là Logic thuần (không cần LLM) hoặc hybrid với LLM
- Logic quyết định:
  - Nếu `is_success = true` → END_SUCCESS
  - Nếu `is_success = false` và `retry_count < max_retries` → code_generator (retry)
  - Nếu `retry_count >= max_retries` → END_FAILURE

---

## 📊 Complete Flow Example

### Scenario: Division with Error Handling

**Step 1: User Input**
```json
{
  "requirement": "Viết hàm chia hai số a và b, xử lý trường hợp b=0"
}
```

**Step 2: Node 1 Output (Code Generator)**
```json
{
  "code": "def divide(a, b):\n    return a / b",  # Lỗi: quên xử lý b=0
  "action": {"next_node": "code_executor"}
}
```

**Step 3: Node 2 Output (Code Executor)**
```json
{
  "execution_result": {
    "status": "error",
    "stderr": "ZeroDivisionError: division by zero",
    "test_cases": [
      {"input": {"a": 10, "b": 2}, "passed": true},
      {"input": {"a": 10, "b": 0}, "passed": false}  # ❌ Fail
    ]
  },
  "is_success": false,
  "action": {"next_node": "critic_router"}
}
```

**Step 4: Node 3 Output (Critic/Router)**
```json
{
  "retry_count": 1,
  "action": {
    "next_node": "code_generator",
    "message": "Phát hiện ZeroDivisionError. Sửa lỗi...",
    "reasoning": "retry_count=1 < max_retries=3"
  }
}
```

**Step 5: Node 1 Output (Code Generator - Lần 2)**
```json
{
  "code": "def divide(a, b):\n    if b == 0:\n        raise ValueError('Cannot divide by zero')\n    return a / b",
  "retry_count": 1,
  "action": {"next_node": "code_executor"}
}
```

**Step 6: Node 2 Output (Code Executor - Lần 2)**
```json
{
  "execution_result": {
    "status": "success",
    "test_cases": [
      {"input": {"a": 10, "b": 2}, "passed": true},
      {"input": {"a": 10, "b": 0}, "passed": true}  # ✅ Pass
    ]
  },
  "is_success": true,
  "action": {"next_node": "critic_router"}
}
```

**Step 7: Node 3 Output (Critic/Router - Lần 2)**
```json
{
  "action": {
    "next_node": "END_SUCCESS",
    "message": "🎉 Thành công! Code đã sửa lỗi."
  }
}
```

---

## ✅ Validation Rules

Mỗi node PHẢI đảm bảo output của nó tuân thủ:

- ✅ `metadata` không thay đổi
- ✅ `state` được append lịch sử
- ✅ `action.next_node` là một trong các giá trị hợp lệ
- ✅ Tất cả field strings có giá trị (không null)
- ✅ `retry_count` tăng đúng quy luật

---

## 🔗 Integration Points

- **Node 1 → Node 2**: `state.code` phải là valid Python
- **Node 2 → Node 3**: `state.execution_result` phải có `status` và `stderr`/`stdout`
- **Node 3 → Node 1**: Nếu retry, phải attach `execution_result.stderr` vào prompt
- **Node 3 → END**: Quyết định cuối cùng dựa trên `is_success` và `retry_count`

