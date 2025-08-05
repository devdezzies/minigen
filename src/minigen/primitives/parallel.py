from typing import List

class Parallel: 
    def __init__(self, name: str, agent_names: List[str]): 
        if not name or not agent_names: 
            raise ValueError("Parallel node requires a name and a list of agent names.")
        self.name = name 
        self.agent_names = agent_names 

    def __repr__(self):
        return f"Parallel(name={self.name}, agent_names={self.agent_names}))"