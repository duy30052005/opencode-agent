from .base_node import BaseNode
from ..schemas.node_1_schema import Node1Input, Node1Output
from ..core.llm_client import llm
import time

class CodeGenerator(BaseNode):
    NODE_NAME = "code_generator"

    def __call__(self, state: Node1Input) -> Node1Output:
        start_time = time.perf_counter()

        requirement = state["state"]["requirement"]

        prompt = f"""You are a helpful assistant that generates Python code based on the given requirement.
        Requirement: {requirement}

        Please provide the generated code without any explanations or comments. The response should be purely the code that fulfills the requirement."""

        # response = llm.invoke(prompt)
        response = "```python\ndef sum_list(numbers):\n    return sum(numbers)\n```"
        # generated_code = response.content
        generated_code = response

        new_state = state["state"].copy()
        new_state["code"] = generated_code.split("```python")[1].split("```")[0].strip() if "```python" in generated_code else generated_code.strip()

        action = {
            "next_node": "code_executor",
            "message": "Code generation completed. Proceeding to execution.",
            "reasoning": "The code has been generated based on the requirement, and we can now execute it to see if it meets the requirement."
        }

        output = Node1Output(state=new_state, action=action)

        end_time = time.perf_counter()
        duration_ms = int((end_time - start_time) * 1000)

        self.write_history(output, state, output, duration_ms=duration_ms)

        return output
