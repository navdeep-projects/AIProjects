"""Graph builder for Langgraph workflow"""

from langgraph.graph import StateGraph, END
from src.ml.state.rag_state import RAGState
from src.ml.nodes.nodes import RAGNodes

class GraphBuilder:
    """Builds and manages the langgraph workflow """
    def __init__(self, retriever, llm):
        """
        Intialize graph builder

        Args : 
            retriever: Document retriever instance
            llm: Language model instance
        """

        self.nodes = None
        self.graph = None
        self.retriever = retriever
        self.llm = llm

    def build(self):
        """
        Build the RAG workflow graph

        Returns :
        Compiled graph instance
        """
        builder = StateGraph(RAGState)

        #Add nodes
        builder.add_node("retriever", self.nodes.retrieve_docs)
        builder.add_node("responder", self.nodes.generate_answer)

        #Set entry point
        builder.set_entry("retriever")

        # Add edges
        builder.add_edge("retriever", "responder")
        builder.add_edge("responder", END)

        # compile graph
        self.graph = builder.compile()
        return self.graph


    def run(self, question: str) -> dict:
        """
        Run the workflow

        Args: 
            question: User question

        Returns :
            Final state with answer
        """

        if self.graph is None:
            self.build()

        initial_state = RAGState(question=question)
        return self.graph.invoke(initial_state)
    