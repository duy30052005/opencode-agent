from .base_node import BaseNode
from src.schemas.node_1_schema import Node1Input, Node1Output
from src.core import llm_client
import time

class CodeGenerator(BaseNode):
    NODE_NAME = "code_generator"

    def __call__(self, state: Node1Input) -> Node1Output:
        start_time = time.perf_counter()
        
        requirement = state["state"]["requirement"]
        if state["state"].get("retry_count", 0) < 1:
            code = self._new_code(requirement)
            new_state = self._new_state(state, code)
            action = {
                "next_node": "code_executor",
                "message": "Code generation completed. Proceeding to execution.",
                "reasoning": "The code has been generated based on the requirement, and we can now execute it to see if it meets the requirement."
            }
        else:
            code = state["state"].get("code", None)
            stderr = state["state"]["execution_result"].get("stderr", None)
            code = self._fix_code(requirement, code, stderr)
            new_state = self._new_state(state, code)
            action = {
                "next_node": "code_executor",
                "message": "Code has been revised based on the previous execution results. Proceeding to execution.",
                "reasoning": "The code has been revised to address the errors encountered in the previous execution attempt. We will execute the revised code to check if it now meets the requirement."
            }

        output = Node1Output(state=new_state, action=action)

        end_time = time.perf_counter()
        duration_ms = int((end_time - start_time) * 1000)

        self.write_history(output, state, output, duration_ms=duration_ms)

        return output

    def _new_state(self, state: Node1Input, code: str) -> Node1Input:
        new_state = state["state"].copy()
        new_state["code"] = code.split("```python")[1].split("```")[0].strip() if "```python" in code else code.strip()

        return new_state

    def _new_code(self, requirement: str) -> str:

        prompt = f"""You are a helpful assistant that generates Python code based on the given requirement.
        Requirement: {requirement}

        Please provide the generated code without any explanations or comments. The response should be purely the code that fulfills the requirement.
        CRITICAL RULES FOR AUTO-TESTING:
        1. You MUST write a function that takes arguments and uses 'return' to output the result.
        2. DO NOT use the `input()` function anywhere in your code.
        3. DO NOT use `print()` for the final output (use 'return' instead).
        4. DO NOT include test blocks like `if __name__ == '__main__':`.
        5. Only output the raw python code for the function(s)."""

        response = llm_client.llm.invoke(prompt)
        # response = llm_client.groq.invoke(prompt)
        return response.content

    def _fix_code(self, requirement: str, code: str | None, stderr: str | None) -> dict:
        if stderr and code:            
            prompt = f"""The previously generated code did not pass the test. Please revise the code based on the following previous code, requirement and error message.
            Requirement: {requirement}
            Previous Code: ```python
            {code}
            ```
            Error Message: {stderr}

            Please provide the revised code without any explanations or comments. The response should be purely the code that fulfills the requirement and resolves the errors.
            CRITICAL RULES FOR AUTO-TESTING:
            1. You MUST write a function that takes arguments and uses 'return' to output the result.
            2. DO NOT use the `input()` function anywhere in your code.
            3. DO NOT use `print()` for the final output (use 'return' instead).
            4. DO NOT include test blocks like `if __name__ == '__main__':`.
            5. Only output the raw python code for the function(s)."""

            response = llm_client.llm.invoke(prompt)
            # response = llm_client.groq.invoke(prompt)
            revised_code = response.content
            return revised_code
        else:
            return code