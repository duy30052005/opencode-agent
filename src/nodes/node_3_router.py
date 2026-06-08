from .base_node import BaseNode
from ..schemas.node_3_schema import Node3Input, Node3Output
import time

class CriticRouter(BaseNode):
  NODE_NAME = 'critic_router'

  def __call__(self, state: Node3Input) -> Node3Output:
    start_time = time.perf_counter()
    #take data from input
    s = state['state']
    is_success = s.get('is_success', False)
    retry_count = s.get('retry_count', 0)
    max_retries = s.get('max_retries', 3)
    #decide base on the data above
    #copy state->never break the input
    new_state = s.copy()
    #if code true
    if is_success:
      action = {
        'next_node': 'END_SUCCESS',
        'message': 'Hoàn thành! Code đã vượt qua tất cả các test case.',
        'reasoning': 'is_success = true, tất cả test case passed',
      }
      #if it's wrong and not hit the max retries
    elif retry_count < max_retries:
      new_state['retry_count'] = retry_count + 1
      action = {
        'next_node': 'code_generator',
        'message': 'Phát hiện lỗi, Agent sẽ sửa lỗi...',
        'reasoning': f'is_success=false, retry_count ({retry_count}) < max_retries ({max_retries}).',
      }
      #wrong and hit the limit retries
    else:
      action = {
        'next_node': 'END_FAILURE',
        'message': 'Agent chưa tìm được giải pháp sau '
                    f'{max_retries} lượt thử. Đây là code và lỗi cuối cùng.',
        'reasoning': f'retry_count ({retry_count}) >= max_retries ({max_retries}). Dừng để tránh lãng phí tài nguyên.',
      }
      # build output
    output = Node3Output(state=new_state, action= action)
    # record this step in history and return
    end_time = time.perf_counter()
    duration_ms = int((end_time - start_time) * 1000)
    self.write_history(output, state, output, duration_ms= duration_ms)
    return output
