"""
LangChain conversation chain for VTA.
Handles conversational memory and context management.
"""
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Try to import LangChain
try:
    from langchain.memory import ConversationBufferMemory
    from langchain.chains import ConversationChain
    from langchain.prompts import PromptTemplate
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger.warning("LangChain not available")
    
    # Stubs
    class ConversationBufferMemory:
        def __init__(self, *args, **kwargs):
            self.chat_history = []
        
        def save_context(self, inputs, outputs):
            pass
        
        def load_memory_variables(self, inputs):
            return {"history": ""}
    
    class ConversationChain:
        def __init__(self, *args, **kwargs):
            pass
        
        def predict(self, input: str) -> str:
            return "Chain not available"
    
    class PromptTemplate:
        def __init__(self, *args, **kwargs):
            pass


# VTA-specific prompt template
VTA_PROMPT_TEMPLATE = """You are the Virtual Testing Assistant (VTA) AI, an expert in automotive test optimization for Nissan NTCE.

You help with:
- Test recommendations for vehicle configurations
- ROI analysis and cost-benefit calculations
- Test suite metrics and optimization
- Simulation export to CARLA or SUMO
- Governance and project reporting

When answering:
- Be concise and professional
- Use specific numbers when available
- Recommend using tools for detailed analysis
- Focus on actionable insights

Conversation history:
{history}

User: {input}
VTA: """


class VTAConversationMemory:
    """
    Manages conversation history and context for VTA.
    """
    
    def __init__(self, max_turns: int = 10):
        """
        Initialize conversation memory.
        
        Args:
            max_turns: Maximum number of conversation turns to remember
        """
        self.max_turns = max_turns
        self.history: List[Dict[str, str]] = []
    
    def add_turn(self, user_input: str, assistant_output: str):
        """Add a conversation turn."""
        self.history.append({
            "user": user_input,
            "assistant": assistant_output
        })
        
        # Keep only last N turns
        if len(self.history) > self.max_turns:
            self.history = self.history[-self.max_turns:]
    
    def get_history_string(self) -> str:
        """Get history as formatted string."""
        if not self.history:
            return "No previous conversation."
        
        lines = []
        for turn in self.history:
            lines.append(f"User: {turn['user']}")
            lines.append(f"VTA: {turn['assistant']}")
        
        return "\n".join(lines)
    
    def clear(self):
        """Clear conversation history."""
        self.history = []
    
    def get_recent_context(self, num_turns: int = 3) -> str:
        """Get recent conversation context."""
        recent = self.history[-num_turns:] if self.history else []
        
        if not recent:
            return "No recent conversation."
        
        lines = []
        for turn in recent:
            lines.append(f"User: {turn['user']}")
            lines.append(f"VTA: {turn['assistant']}")
        
        return "\n".join(lines)


class VTAConversationChain:
    """
    Conversation chain for VTA with context management.
    """
    
    def __init__(self, llm, memory: Optional[VTAConversationMemory] = None):
        """
        Initialize conversation chain.
        
        Args:
            llm: Language model instance
            memory: Optional conversation memory
        """
        self.llm = llm
        self.memory = memory or VTAConversationMemory()
        self.prompt_template = VTA_PROMPT_TEMPLATE
    
    def predict(self, user_input: str) -> str:
        """
        Generate response to user input.
        
        Args:
            user_input: User's message
            
        Returns:
            Assistant's response
        """
        try:
            # Format prompt with history
            history = self.memory.get_history_string()
            prompt = self.prompt_template.format(
                history=history,
                input=user_input
            )
            
            # Get response from LLM
            response = self.llm._call(prompt)
            
            # Save to memory
            self.memory.add_turn(user_input, response)
            
            return response
        
        except Exception as e:
            logger.error(f"Error in conversation chain: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def reset(self):
        """Reset conversation memory."""
        self.memory.clear()
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get summary of conversation context."""
        return {
            "num_turns": len(self.memory.history),
            "recent_context": self.memory.get_recent_context(3)
        }


def create_conversation_chain(llm, max_turns: int = 10) -> VTAConversationChain:
    """
    Create a VTA conversation chain.
    
    Args:
        llm: Language model instance
        max_turns: Maximum conversation history to keep
        
    Returns:
        VTAConversationChain instance
    """
    memory = VTAConversationMemory(max_turns=max_turns)
    return VTAConversationChain(llm=llm, memory=memory)


if __name__ == "__main__":
    from src.orchestrators.llm_setup import create_llm_manager
    
    print("\n" + "=" * 70)
    print("CONVERSATION CHAIN TEST")
    print("=" * 70)
    
    # Create LLM
    print("\n[1/4] Creating LLM...")
    llm_manager = create_llm_manager(use_mock=True)
    llm = llm_manager.initialize_llm()
    print("[OK] LLM initialized")
    
    # Create conversation chain
    print("\n[2/4] Creating conversation chain...")
    chain = create_conversation_chain(llm, max_turns=5)
    print("[OK] Chain created")
    
    # Test conversation
    print("\n[3/4] Testing conversation...")
    
    user_inputs = [
        "Hello, can you help me?",
        "I need test recommendations for Ariya EV",
        "What about the ROI for test optimization?"
    ]
    
    for i, user_input in enumerate(user_inputs, 1):
        print(f"\n--- Turn {i} ---")
        print(f"User: {user_input}")
        response = chain.predict(user_input)
        print(f"VTA: {response[:200]}...")
    
    # Get context summary
    print("\n[4/4] Getting context summary...")
    summary = chain.get_context_summary()
    print(f"[OK] Conversation turns: {summary['num_turns']}")
    print(f"[OK] Recent context:\n{summary['recent_context'][:200]}...")
    
    print("\n[OK] Conversation chain test complete")

