from langchain_core.tools import tool

@tool
def read_error_log(task_id: str) -> str:
    """
    Sử dụng tool này khi bạn cần đọc chi tiết lỗi (stderr) hoặc test case bị fail từ Node 2.
    """
    # Tạm thời hardcode hoặc đọc từ file JSON debug để test
    return "Lỗi thực tế: AssertionError: Expected [2, 3] but got [2, 3, 5]"