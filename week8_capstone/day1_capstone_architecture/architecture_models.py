from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class CapstoneConfig:
    """
    Central configuration for the unified Capstone application.
    """
    enable_memory: bool = True
    enable_rag: bool = True
    enable_sandbox: bool = True
    enable_human_in_loop: bool = True
    
    # Model configs
    tutor_llm_model: str = "llama3-70b-8192"
    evaluation_llm_model: str = "llama3-8b-8192"
    
    # DB paths
    chroma_db_path: str = "./data/chroma_db"
    learner_profile_path: str = "./data/learner_profiles.json"
