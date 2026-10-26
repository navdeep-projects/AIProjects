"""LangGraph nodes for RAG workflow + ReAct Agent inside generate_content"""

from typing import List, Optional
from src.ml.state.rag_state import RAGState

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from langchain_core.tools import Tool
from pathlib import Path
import truststore

# Wikipedia tool
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun


class MFRAGNodes:
    """Contains Mutual Fund node functions for RAG workflow"""

    def __init__(self, retriever, llm):
        self.retriever = retriever
        self.llm = llm
        self._agent = None  # lazy-init agent
        self.retriever_tool = None
        

    def retrieve_docs(self, state: RAGState) -> RAGState:
        """Classic retriever node"""
        docs = self.retriever.invoke(state.question)
        return RAGState(
            question=state.question,
            retrieved_docs=docs
        )

    def _build_tools(self) -> List[Tool]:
        """Build retriever + wikipedia tools"""

        def retriever_tool_fn(query: str) -> str:
            docs: List[Document] = self.retriever.invoke(query)
            if not docs:
                return "No documents found."
            merged = []
            for i, d in enumerate(docs[:8], start=1):
                meta = d.metadata if hasattr(d, "metadata") else {}
                title = meta.get("title") or meta.get("source") or f"doc_{i}"
                merged.append(f"[{i}] {title}\n{d.page_content}")
            return "\n\n".join(merged)

        self.retriever_tool = Tool(
            name="retriever",
            description="Fetch passages from indexed corpus.",
            func=retriever_tool_fn,
        )

        def wiki_tool_fn(query: str) -> str:
            wiki = WikipediaQueryRun(
                api_wrapper=WikipediaAPIWrapper(top_k_results=10, lang="en")
            )
            return wiki.run(query)

        self.wikipedia_tool = Tool(
            name="wikipedia",
            description="Search Wikipedia for general knowledge.",
            func=wiki_tool_fn,
        )

        return [self.retriever_tool, self.wikipedia_tool]

    from langchain.chat_models import init_chat_model
    truststore.inject_into_ssl()
    
    def _build_agent(self):
        """ReAct agent with tools"""
        print("Building agent...")
        self._build_tools()
        print(f"Tools built: {[t.name for t in self._build_tools()]}")
        tools = [self.retriever_tool, self.wikipedia_tool]
        print(f"Tools Assigned")
        system_prompt = (
            "You are a helpful RAG agent. "
            "Prefer 'retriever' for user-provided docs. "
            "Return only the final useful answer."
        )
        print(f"System prompt: {system_prompt}")
        
        self._agent = create_react_agent(self.llm, tools=tools, prompt=system_prompt)

    def generate_answer(self, state: RAGState) -> RAGState:
        """
        Generate answer using ReAct agent with retriever for Mutual Fund documents.
        """
        print("Generating answer...")
        if self._agent is None:
            self._build_agent()
        print("Agents created")
        prompt_file = (
            Path(__file__).resolve().parents[3]
            / "data"
            / "MutualFundprompt.txt"
        )
        state.question = prompt_file.read_text(encoding="utf-8")

        result = self._agent.invoke({"messages": [HumanMessage(content=state.question)]})
        messages = result.get("messages", [])
        print("Messages retrieved")
        answer: Optional[str] = None
        if messages:
            answer_msg = messages[-1]
            answer = getattr(answer_msg, "content", None)
        print(f"Answer: {answer}")
        return RAGState(
            question=state.question,
            retrieved_docs=state.retrieved_docs,
            answer= answer 
        )
