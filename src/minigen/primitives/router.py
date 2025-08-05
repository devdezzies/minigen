from enum import Enum 
from pydantic import BaseModel, Field
from minigen import Agent 
from ..utils.logging import logger
from typing import Dict, Callable, Any
from minigen.state import NetworkState
from .parallel import Parallel


def create_llm_router(nodes: Dict[str, Any]) -> Callable[[NetworkState], str]:
    
    routable_names = list(nodes.keys())
    RouteOptions = Enum("RouteOptions", {name: name for name in routable_names} | {"FINISH": "FINISH"})

    class NextNode(BaseModel): 
        next_node_name: RouteOptions = Field(..., description="The name of the next node to run, or FINISH if the task is complete.")
    
    agent_descriptions = []
    parallel_descriptions = []
    for name, node in nodes.items(): 
        if isinstance(node, Agent): 
            if node.session.messages and node.session.messages[0]['role'] == 'system': 
                description = node.session.messages[0]['content'].split('\n')[0] 
                agent_descriptions.append(f"- **{name}**: {description}")
            
        elif isinstance(node, Parallel): 
            description = f"Runs the following agents in parallel: {', '.join(node.agent_names)}"
            parallel_descriptions.append(f"- **{name}**: {description}")

    routing_system_prompt = (
        "You are the master router and project manager of a team of AI agents and parallel workflows. "
        "Your goal is to solve the user's request by intelligently routing tasks.\n\n"
        "Here are your available nodes:\n\n"
        "--- Sequential Agents (for single tasks) ---\n"
        f"{'\n'.join(agent_descriptions)}\n\n"
        "--- Parallel Workflows (for concurrent tasks) ---\n"
        f"{'\n'.join(parallel_descriptions)}\n\n"
        "--- Your Instructions ---\n"
        "1.  **Analyze the Goal**: Review the original user request and the full conversation history.\n"
        "2.  **Choose the Right Tool**: \n"
        "    - If the next part of the task can be broken down into independent sub-problems (e.g., researching two different topics), choose a **Parallel** node.\n"
        "    - If a parallel task just finished (the last message is a JSON array of results), you MUST choose an agent designed to **synthesize** or **aggregate** those results.\n"
        "    - Otherwise, choose the best **Sequential Agent** for the next single step.\n"
        "3.  **Check for Completion**: If the last message fully satisfies the original request, you MUST choose **FINISH**.\n"
        "4.  **Output Format**: Your response must be ONLY the required JSON object."
    )

    router_agent = Agent(
        name="Router", 
        system_prompt=routing_system_prompt
    )

    def llm_router_function(state: NetworkState) -> str: 
        logger.info("LLM router is making a decision..")

        router_agent.clear_session()
        context_messages = list(state.messages) 
        router_agent.session.messages.extend(context_messages)

        decision = router_agent.chat(
            prompt="Given the history, what is the next node to run?", 
            response_model=NextNode
        )

        chosen_route = decision.choices[0].message.parsed.next_node_name.value 

        if chosen_route == "FINISH": 
            return None 
        
        return chosen_route 
    
    return llm_router_function