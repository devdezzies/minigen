from .utils.logging import logger
from .tool import get_tool_func
from openai import OpenAI
import json
from typing import Type, Optional
from pydantic import BaseModel

class AgentSession: 
    def __init__(self, client: OpenAI, tools=None, system_prompt: Optional[str] = None): 
        self.client = client
        self.messages = []
        self.tools = [tool.tool_spec for tool in tools] if tools else []

        if system_prompt: 
            self.messages.append({"role": "system", "content": system_prompt})
            logger.info(f"System prompt set: {system_prompt}")
    
    def __enter__(self): 
        logger.info("Starting agent session...")
        return self

    def __exit__(self, exc_type, exc_value, traceback): 
        logger.info("Ending agent session...")
        if exc_type: 
            logger.error("Error occurred", exc_info=True) 
        return False
    
    def user(self, content: str): 
        self.messages.append({"role": "user", "content": content})
        logger.info(f"User: {content}")

    def assistant(self, content: str): 
        self.messages.append({"role": "assistant", "content": content})
        logger.info(f"Assistant: {content}")
    
    def tool_response(self, tool_call_id: str, name: str, result: str): 
        self.messages.append({
            "role": "tool", 
            "tool_call_id": tool_call_id, 
            "name": name, 
            "content": result
        })
        logger.info(f"Tool '{name}': {result}")
    
    def parse_run(self, response_model: Type[BaseModel], model="gpt-4", **kwargs):
        logger.info(f"Running session with parsing for model {response_model.__name__}")
        try: 
            parsed_response = self.client.chat.completions.parse( 
                model=model, 
                messages=self.messages, 
                response_format=response_model, 
                **kwargs
            )

            self.assistant(parsed_response.model_dump_json())

            return parsed_response
        except Exception as e: 
            logger.error(f"Error during parsing run: {e}", exc_info=True)
            raise e
         
        
    def run(self, model="gpt-4", **kwargs): 
        response = self.client.chat.completions.create( 
            model=model, 
            messages=self.messages, 
            tools=[tool for tool in self.tools], 
            tool_choice="auto", 
            **kwargs
        )

        message = response.choices[0].message  
        
        tool_calls = message.tool_calls or [] 
        self.messages.append({
            "role": "assistant", 
            "content": message.content, 
            "tool_calls": [tc.model_dump() for tc in tool_calls] if tool_calls else None
        })
        logger.info(f"Assistant: {message.content}")

        if tool_calls: 
            for tool_call in tool_calls: 
                func_name = tool_call.function.name 
                args = json.loads(tool_call.function.arguments)

                if func_name not in [tool.get("function").get("name") for tool in self.tools]: 
                    raise ValueError(f"Unknown tool: {func_name}")

                func = get_tool_func(func_name)
                logger.info(f"Calling tool: {func_name} with args: {args}")
                result = func(**args)

                self.tool_response( 
                    tool_call_id=tool_call.id, 
                    name=func_name, 
                    result=json.dumps(result)
                )
            return self.run(model=model, **kwargs)
        return message.content

    def get_messages(self): 
        return list(self.memory) 
    
    def clear(self): 
        logger.info("Clearing agent session memory...")
        self.memory.clear()