"""Configuration module for Agentic RAG system"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

import truststore


load_dotenv()

class Config:

    #API Keys
    
    os.environ.setdefault("USER_AGENT", "AgenticRAG/1.0") 
    
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

    #Model Configuration
    LLM_Model = "openai:gpt-4o"

    #document Processing
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 50

    # Default URLs
    DEFAULT_DOC_URL = [
        "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=3&ssid=15&smid=11",
        "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=3&ssid=17&smid=39"
    ]

    @classmethod
    def get_llm(cls):
        """Intialize and return the LLM Model"""
        truststore.inject_into_ssl()
        return init_chat_model(cls.LLM_Model)


