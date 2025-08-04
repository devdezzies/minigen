# MiniGen 
![](/assets/terraria.png)
MiniGen is a framework for building agents using OpenAI compatibility APIs. 
You can use Gemini, Groq, Claude, Ollama, or other LLM providers with OpenAI compatibility APIs. This framework provides essential wrappers for building an agent directly with the OpenAI API. This framework provides you with simplicity and transparency by explicitly showing the agent's planning steps.

## Tool Calling 
In tool calling, you no longer have to write the boilerplate JSON code to define your tools. Just define the function and add a decorator that will translate everything for you. 

```python 
from minigen import tool 

@tool(description="Convert lbs to kg")
def lbs_to_kg(lbs): 
    return lbs * 0.45359237
```

This decorator will extend your function by adding an additional method for JSON creation. 

```json
{
    'type': 'function',
    'function': {'name': 'lbs_to_kg',
    'description': 'Convert lbs to kg',
    'parameters': {'type': 'object',
        'properties': {'lbs': {'type': ('string',)}},
        'required': ['lbs']},
    'strict': True
    }
}
```

# AgentSession 
Another important part is session context. This contains information that the model has to know, including user query, assistant output, and tool calls. Let's try to combine the tool calling with a session. 

```python
from openai import OpenAI 
from minigen import tool, AgentSession

@tool(description="Convert lbs to kg")
def lbs_to_kg(lbs): 
    return lbs * 0.45359237

with AgentSession(client=client, tools=[add]) as session: 
    session.user("How much is 20 lbs in kg?")
    result = session.run() 
    print("Answer:", result)
```

You can also add system prompt to the session. Just add `session.assistant("You are a helpful assistant")`
