"""RAG state definition for langgraph"""

from typing import List
from pydantic import BaseModel
from langchain_core.documents import Document

class RAGState(BaseModel):
    """State Object for RAG Workflow"""
    question: str
    retrieved_docs: List[Document] = []
    answer: str = ""