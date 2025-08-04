from minigen import Agent
from ..utils.logging import logger
from pydantic import BaseModel 
from typing import Optional, Type, List, Dict, Any  

class Chain: 
    def __init__(self, agent: Agent, verbose: bool = False): 
        self.agent = agent  
        self.steps: List[Dict[str, Any]] = [] 
        self.verbose = verbose 

    def add_step(self, prompt_template: str, response_model: Optional[Type[BaseModel]] = None): 
        step = {"prompt_template": prompt_template, "response_model": response_model} 
        self.steps.append(step) 
        return self 
    
    def run(self, initial_input: str): 
        logger.info(f"Starting prompt chaining with input: {initial_input}")
        current_input = initial_input 

        for i, step in enumerate(self.steps): 
            prompt = step["prompt_template"].format(input=current_input)

            if self.verbose: 
                logger.info(f"--- Step {i+1} ---")
                logger.info(f"Prompt: {prompt}")
            
            output = self.agent.chat(prompt, response_model=step["response_model"]) 

            if isinstance(output, BaseModel): 
                current_input = output.model_dump_json() 
            else: 
                current_input = output
            
            if self.verbose: 
                logger.info(f"Output: {current_input}")
            
        logger.info("Chain finished")
        return current_input