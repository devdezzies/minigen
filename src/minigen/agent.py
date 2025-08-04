from .utils.logging import logger
from openai import OpenAI
from .context import AgentSession
from pydantic import BaseModel, ValidationError
from typing import Optional, Type

class Agent: 
    def __init__(self, model="gpt-4", base_url=None, api_key=None, tools: Optional[list]=None, name: Optional[str] = "MiniGen Agent", system_prompt: Optional[str] = None): 
        self.model = model 
        self.name = name
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.session = AgentSession(client=self.client, tools=tools, system_prompt=system_prompt)

    def chat(self, prompt: str, response_model: Optional[Type[BaseModel]] = None): 
        logger.info(f"Prompt: {prompt}")
        self.session.user(prompt) 

        if response_model: 
            logger.info(f"Response requested in format: {response_model.__name__}") 
            try: 
                parsed = self.session.parse_run(model=self.model, response_model=response_model) 
                logger.info(f"Parsed response: {parsed}")
                return parsed 
            except (ValidationError, Exception) as e: 
                logger.error("[Response Parsing Failed]", e)
                raise e 
        else: 
            response = self.session.run(model=self.model) 
            logger.info(f"Response: {response}")
            return response
    
    def clear_session(self): 
        self.session.messages = [msg for msg in self.session.messages if msg["role"] == "system"]