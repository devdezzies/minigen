import inspect 
from pydantic import BaseModel
from typing import get_type_hints

_tool_registry = {}

def tool(description=None, strict=True): 
    def decorator(func): 
        signature = inspect.signature(func)
        type_hints = get_type_hints(func)

        properties = {}
        required = [] 

        _tool_registry[func.__name__] = func

        for name, param in signature.parameters.items():
            param_type = type_hints.get(name, str) 
            if param_type == str: 
                json_type = "string",       
            elif param_type == int: 
                json_type = "integer",
            elif param_type == float: 
                json_type = "number",
            elif param_type == bool: 
                json_type = "boolean",
            else: 
                json_type = "string",

            properties[name] = {
                "type": json_type
            }

            if param.default is inspect.Parameter.empty: 
                required.append(name)
            
        func.tool_spec = {
            "type": "function", 
            "function": {
                "name": func.__name__, 
                "description": description or f"Tool for `{func.__name__}`", 
                "parameters": {
                    "type": "object", 
                    "properties": properties, 
                    "required": required
                },
                "strict": strict
            }, 
        }

        func._is_tool = True 
        return func 
    
    return decorator

def get_tool_func(name: str): 
    return _tool_registry.get(name)
