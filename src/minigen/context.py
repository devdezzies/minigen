from .utils.logging import logger

class AgentSession: 
    def __init__(self): 
        self.memory = []
    
    def __enter__(self): 
        logger.info("Starting agent session...")
        return self

    def __exit__(self, exc_type, exc_value, traceback): 
        logger.info("Ending agent session...")
        if exc_type: 
            logger.error("Error occurred", exc_info=True) 
        return False
    
    def add_message(self, role: str, content: str): 
        logger.debug(f"Adding message: {role} - {content}")
        if role not in {"system", "user", "assistant", "tool"}: 
            raise ValueError(f"Invalid role: {role}")
        self.memory.append({"role": role, "content": content})

    def get_messages(self): 
        return list(self.memory) 
    
    def clear(self): 
        logger.info("Clearing agent session memory...")
        self.memory.clear()