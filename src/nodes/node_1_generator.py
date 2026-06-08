from .base_node import BaseNode
from ..schemas.node_1_schema import Node1Input, Node1Output
from ..core.llm_client import llm

class CodeGenerator(BaseNode):
    NODE_NAME = "code_generator"
    
    def __call__(self, state: Node1Input) -> Node1Output:
        requirement = state["state"]["requirement"]
        
        prompt = f"""You are a helpful assistant that generates Python code based on the given requirement. 
        Requirement: {requirement}
        
        Please provide the generated code without any explanations or comments. The response should be purely the code that fulfills the requirement."""
        
        response = llm(prompt)
        generated_code = response.content.strip()
        
        new_state = state["state"].copy()
        new_state["code"] = generated_code
        
        action = {
            "next_node": "code_executor",
            "message": "Code generation completed. Proceeding to execution.",
            "reasoning": "The code has been generated based on the requirement, and we can now execute it to see if it meets the requirement."
        }
        
        return Node1Output(state=new_state, action=action)