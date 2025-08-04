from enum import Enum 
from pydantic import BaseModel
from minigen import Agent 
from ..utils.logging import logger
from typing import Dict, Callable, Type

class Router: 
    def __init__(self, agent: Agent, route_model: Type[BaseModel], routing_prompt_template: str): 
        self.agent = agent 
        self.route_model = route_model 
        self.routing_prompt_template = routing_prompt_template 
        self.routes: Dict[Enum, Callable] = {}

    def add_route(self, choice: Enum, target_chain: Callable): 
        self.routes[choice] = target_chain
        return self 
    
    def run(self, initial_input: str): 
        logger.info(f"Starting routing with input: {initial_input}")
        
        prompt = self.routing_prompt_template.format(input=initial_input)
        
        decision = self.agent.chat(prompt, response_model=self.route_model) 

        chosen_route = decision.choices[0].message.parsed.route
        logger.info(f"Chosen route: {chosen_route}") 

        if chosen_route in self.routes: 
            target_chain = self.routes[chosen_route] 
            return target_chain.run(initial_input) 
        else: 
            raise ValueError(f"Unknown route: {chosen_route}")