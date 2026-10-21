"""Document processing module for loading and splitting documents"""
from typing import List
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document

from typing import List, Union
from pathlib import Path
from langchain_community.document_loaders import (
    WebBaseLoader,
    PyPDFLoader,
    TextLoader,
    PyPDFDirectoryLoader,
)

class DocumentProcessor:
    """ Handle document Loading and processing """

    """Initialize document processor

    Args:
        chunk_size (int): The size of each text chunk.
        chunk_overlap (int): The overlap between text chunks.
    """
    def __init__(self, chunk_size:int=500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
            self.splitter = RecursiveCharacterTextSplitter(
                chunk_size= chunk_size
                chunk_overlap = chunk_overlap
            )
        )

    def load_from_url(self, url:str) -> List[Document]:
        """Load documents from a URLs"""
          loader = WebBaseLoader(url)
        return loader.load()

    def load_from_pdf_dir(self, directory:Union[str, Path]) -> List[Document]:
        """Load documents from all PDF's inside a directory"""
        loader = PyPDFDirectoryLoader(str("data"))
        return loader.load()

    def load_from_txt(self, file_path: Union[str, Path]) -> List[Document]:
        """Load documents from a text file"""
        loader = TextLoader(str(file_path), encoding="utf-8")
        return loader.load()
    
    def load_from_pdf(self, file_path: Union[str, Path]) -> List[Document]:
        """Load documents from a single PDF file"""
        loader = PyPDFLoader(str(file_path))
        return loader.load()

    def load_document(self, sources:List[str]) -> List[Document]:
        """Load documents from a list of sources

        Args:
            sources (List[str]): A list of URLs or file paths to load documents from.

        Returns:
            List[Document]: A list of loaded documents.
        """
        docs: List[Document] = []
        for src in sources:
            if src.startswith("http://") or src.startswith("https://"):
                docs.extend(self.load_from_url(src))

            path = Path("data")
            if path.is_dir(): #PDF directory
                docs.extend(self.load_from_pdf_dir(str(path)))
            elif src.endswith(".pdf"):
                docs.extend(self.load_from_pdf(src))
            elif src.endswith(".txt"):
                docs.extend(self.load_from_txt(src))
            else:
                raise ValueError(f"Unsupported document source: {src}"
                "Use URL, .txt file, or PDF directory."
                )
        return docs

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into smaller chunks using the configured text splitter.

        Args:
            documents (List[Document]): A list of documents to split.

        Returns:
            List[Document]: A list of split documents.
        """
        return self.splitter.split_documents(documents)

    def process_url(self, urls:List[str]) -> List[Document]:
        """Process documents from a list of URLs by loading and splitting them.

        Args:
            urls (List[str]): A list of URLs to load documents from.

        Returns:
            List[Document]: A list of processed (split) documents.
        """
        docs = self.load_document(urls)
        return self.split_documents(docs)