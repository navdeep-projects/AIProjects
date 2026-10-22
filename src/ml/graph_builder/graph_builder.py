"""Graph builder for Langgraph workflow"""

from langgraph.graph import StateGraph, END
from src.ml.state.rag_state import RAGState
from src.ml.nodes.reactnode import RAGNodes


class GraphBuilder:
    """Builds and manages the langgraph workflow """
    def __init__(self, retriever, llm):
        """
        Intialize graph builder

        Args : 
            retriever: Document retriever instance
            llm: Language model instance
        """
        self.nodes = RAGNodes(retriever=retriever, llm=llm)
        self.graph = None
        

    def build(self):
        """
        Build the RAG workflow graph

        Returns :
        Compiled graph instance
        """
        builder = StateGraph(RAGState)

        #Add nodes
        builder.add_node("retrieve_docs", self.nodes.retrieve_docs)
        builder.add_node("generate_answer", self.nodes.generate_answer)

        #Set entry point
        builder.set_entry_point("retrieve_docs")

        # Add edges
        builder.add_edge("retrieve_docs", "generate_answer")
        builder.add_edge("generate_answer", END)

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
        print("Run started")
        if self.graph is None:
            print("Building graph...")
            self.build()
            print("Graph built successfully.")

        initial_state = RAGState(question=question)
        print(f"Initial state: {initial_state}")
        result = self.graph.invoke(initial_state)
        print(f"Final state: {result}")
        return result
    