from .agent import Agent 
from .state import NetworkState 
from .utils.logging import logger 
from typing import Dict, Callable, Optional, Any
from .primitives import Parallel
from concurrent.futures import ThreadPoolExecutor
import json

RouterFunction = Callable[[NetworkState], Optional[str]]

class AgentNetwork: 
    def __init__(self):
        self.nodes: Dict[str, Any] = {}
        self.router: Optional[RouterFunction] = None 
        self.state = NetworkState() 

    def add_node(self, node: Any):
        if not hasattr(node, 'name'): 
            raise TypeError("Nodes added to the network must have a name")
        self.nodes[node.name] = node 
        logger.info(f"Node: {node.name} ({type(node).__name__}) added to the network")

    def set_router(self, router_func: RouterFunction): 
        self.router = router_func 
        logger.info("Router has been set.")
    
    def set_entry_point(self, node_name: str):
        if node_name not in self.nodes: 
            raise ValueError(f"Entry point node: {node_name} not found in the network.")
        self.state.next_agent_name = node_name
        logger.info(f"Network entry point set to {node_name}")
    
    def run(self, initial_input: str, max_rounds: int = 10): 
        if not self.router: 
            raise ConnectionError("Router must be set before running the network")
        if not self.state.next_agent_name: 
            raise ConnectionError("Entry point must be set before running the network")

        self.state.messages.append({"role": "user", "content": initial_input})

        round_count = 0
        current_node_name = self.state.next_agent_name

        while current_node_name and round_count < max_rounds: 
            current_node = self.nodes.get(current_node_name)

            if not current_node: 
                raise ValueError(f"Router directed to an unknown node: {current_node_name}")
            
            logger.info(f"-------- Round {round_count + 1} | Running Node: {current_node_name} ({type(current_node).__name__}) --------")

            last_message = self.state.messages[-1]['content']

            if isinstance(current_node, Agent): 
                current_node.clear_session()
                response = current_node.chat(last_message)
                self.state.messages.append({"role": "assistant", "name": current_node_name, "content": response})
            
            elif isinstance(current_node, Parallel): 
                results = self._run_parallel_node(current_node, last_message)
                aggregated_content = json.dumps(results, indent=2)
                self.state.messages.append({"role": "assistant", "name": current_node_name, "content": aggregated_content})

            current_node_name = self.router(self.state)
            logger.info(f"Router decision: next node is {current_node_name}")
            round_count += 1

        if round_count >= max_rounds:
            logger.warning(f"--- Network Finished: Reached maximum number of rounds ({max_rounds})")
            self.state.result = "Network stopped due to reaching max rounds."
        else:
            logger.info("--- Network Finished ---")
            self.state.result = self.state.messages[-1]['content']
            
        return self.state

    def _run_parallel_node(self, parallel_node: Parallel, prompt: str) -> list: 
        results = []

        def run_single_agent(agent_name: str): 
            agent = self.nodes.get(agent_name)
            if not isinstance(agent, Agent): 
                return {"agent": agent_name, "error": "Node is not a valid Agent"}
            
            logger.info(f" -> Starting parallel task for agent: {agent_name}")
            agent.clear_session() 
            response = agent.chat(prompt)
            logger.info(f" <- Finished parallel task for agent: {agent_name}")
            return {"agent": agent_name, "response": response}
    
        with ThreadPoolExecutor() as executor: 
            future_results = executor.map(run_single_agent, parallel_node.agent_names)
            results.extend(future_results)
        
        return results
