from enum import Enum 
from pydantic import BaseModel, Field
from minigen import Agent 
from ..utils.logging import logger
from typing import Dict, Callable
from minigen.state import NetworkState

def create_llm_router(agents: Dict[str, Agent]) -> Callable[[NetworkState], str]:
    agent_names = list(agents.keys())
    RouteOptions = Enum("RouteOptions", {name: name for name in agent_names} | {"FINISH": "FINISH"})

    class NextAgent(BaseModel): 
        next_agent_name: RouteOptions = Field(..., description="The name of the next agent to run, or FINISH if the task is complete.")
    
    agent_descriptions = "\n".join(
        f"- {name}: {agent.session.messages[0]['content'].split('.')[0]}" for name, agent in agents.items()
    )

    routing_system_prompt = (
        "You are the master router and project manager of a team of AI agents. "
        "Your goal is to solve the user's request by intelligently routing tasks to the correct agent. "
        "Based on the original user request and the conversation history, you must decide which agent should run next. "
        "Do not try to answer the user's request yourself.\n\n"
        "Here are your available agents:\n"
        f"{agent_descriptions}\n\n"
        "Review the full conversation history. If the last message fully satisfies the original request, choose FINISH. "
        "Otherwise, choose the best agent for the very next step. Your response MUST be a JSON object matching the required format."
    )

    router_agent = Agent(name="Router", model="gemini-2.5-pro", system_prompt=routing_system_prompt, api_key="AIzaSyBv9pjgGcE6Dl8r3Fa4ZEi_YPOQamqT6vs", 
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",)

    def llm_router_function(state: NetworkState) -> str: 
        logger.info("LLM Router is making a decision...")

        router_agent.session.messages.extend(state.messages)

        decision = router_agent.chat(
            prompt="Based on the history, who should go next", 
            response_model=NextAgent
        )
        
        chosen_route = decision.choices[0].message.parsed.next_agent_name.value

        if chosen_route == "FINISH":
            return None
    
        return chosen_route
    
    return llm_router_function

