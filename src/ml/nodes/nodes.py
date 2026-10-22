""" Langgraph nodes for RAG Workflow"""

from src.ml.state.rag_state import RAGState

class RAGNodes:
    """Contains node function for RAG Workflow"""

    def __init__(self, retriever, llm):
        """
        Initialize RAG nodes

        Args:
            retriever: Document retriever instance
            llm: Language model instance
        """
        self.retriever = retriever
        self.llm = llm

    def retrieve_docs(self, state:RAGState) -> RAGState:
        """
        Retrieve relevant document node

        Args: 
            state: : current RAG State

        Returns:
            Updated RAG State with retrieved documents
        """
        docs = self.retriever.invoke(state.question)

    return RAGState(
        question=state.question,
        retrieved_docs=docs
    )

    def generate_answer(self, state: RAGState) -> RAGState:
        """
        Generate answer node

        Args:
            state: current RAG State

        Returns:
            Updated RAG State with generated answer
        """

        # combine retrieved documents into context
        context = "\n\n".join([doc.page_content for doc in state.retrieved_docs])
        
        #create prompt
        prompt = f""" Answer the question based on the context.
                    Context:
                    {context}
                    Question:
                    {state.question}
        """

        # Generate response

        answer = self.llm.generate(prompt)
        
        return RAGState(
            question=state.question,
            retrieved_docs=state.retrieved_docs,
            answer=answer.content
        )
