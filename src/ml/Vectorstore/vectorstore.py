"""Vector store for document embedding and retrieval"""

from typing import List
from langchain_community.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document

class VectorStore:
    """Manages Vector store application"""
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = None
        self.retriever = None

    def create_retriever(self, documents: List[Document]):
        """Create a vector store from a list of documents

        Args:
            documents (List[Document]): A list of documents to add to the vector store.
        Returns:
            The retriever instance for querying the vector store.
        """
        self.vectorstore = FAISS.from_documents(documents, self.embeddings)
        self.retriever = self.vectorstore.as_retriever()

    def get_retriever(self):
        """Get the retriever Instance
        
        Returns:
            The retriever instance for querying the vector store.
        """
        if not self.retriever:
            raise ValueError("Vector store has not been created yet.")
        return self.retriever


    def retrieve_documents(self, query: str, k: int = 4) -> List[Document]:
        """Retrieve documents from the vector store based on a query"""
        if not self.retriever:
            raise ValueError("Vector store has not been created yet.")
        return self.retriever.get_relevant_documents(query)[:k]