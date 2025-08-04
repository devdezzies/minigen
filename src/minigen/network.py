from .agent import Agent 
from .state import NetworkState 
from .utils.logging import logger 
from typing import Dict, Callable, Optional 

RouterFunction = Callable[[NetworkState], Optional[str]]

class AgentNetwork: 
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.router: Optional[RouterFunction] = None 
        self.state = NetworkState() 

    def add_agent(self, agent: Agent):
        if not agent.name: 
            raise ValueError("Agent in a network must have a name.")
        self.agents[agent.name] = agent 
        logger.info(f"Agent: {agent.name} added to the network")

    def set_router(self, router_func: RouterFunction): 
        self.router = router_func 
        logger.info("Rouyer has been set.")
    
    def set_entry_point(self, agent_name: str):
        if agent_name not in self.agents: 
            raise ValueError(f"Entry point agent: {agent_name} not found in the network.")
        self.state.next_agent_name = agent_name
        logger.info(f"Network entry point set to {agent_name}")
    
    def run(self, initial_input: str, max_rounds: int = 10): 
        if not self.router: 
            raise ConnectionError("Router must be set before running the network")
        if not self.state.next_agent_name: 
            raise ConnectionError("Entry point must be set before running the network")

        self.state.messages.append({"role": "user", "content": initial_input})

        round_count = 0
        while self.state.next_agent_name and round_count < max_rounds: 
            current_agent_name = self.state.next_agent_name 
            current_agent = self.agents.get(current_agent_name)

            if not current_agent: 
                raise ValueError(f"Router directed to an unknown agent: {current_agent_name}")
            
            logger.info(f"-------- Running Agent: {current_agent_name} --------")

            context_for_agent = []

            system_prompt = next((msg for msg in current_agent.session.messages if msg["role"] == "system"), None)
            if system_prompt: 
                context_for_agent.append(system_prompt)
            
            original_request = self.state.messages[0]
            context_for_agent.append(original_request)

            if len(self.state.messages) > 1: 
                last_message = self.state.messages[-1]
                context_for_agent.append(last_message)
            
            current_agent.session.messages = context_for_agent 
            response = current_agent.session.run(model=current_agent.model)

            self.state.messages.append({"role": "assistant", "name": current_agent_name, "content": response})

            next_step = self.router(self.state) 
            self.state.next_agent_name = next_step 

            logger.info(f"Router decision: next agent is {next_step}")

        if round_count >= max_rounds:
            logger.warning(f"--- Network Finished: Reached maximum number of rounds ({max_rounds})")
            self.state.result = "Network stopped due to reaching max rounds."
        else:
            logger.info("--- Network Finished ---")
            self.state.result = self.state.messages[-1]['content']
            
        return self.state
