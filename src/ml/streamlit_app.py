"""Streamlit UI for Agentic RAG System - Simplified Version"""

import streamlit as st
from pathlib import Path
import sys
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.ml.config.config import Config
from src.ml.document_ingestion.document_processor import DocumentProcessor
from src.ml.Vectorstore.vectorstore import VectorStore
from src.ml.graph_builder.graph_builder import GraphBuilder
from src.ml.Generate.Generatepdf import GeneratePdf
from src.ml.voice.femalevoice import femalevoice
from src.ml.graph_builder.mfgraph_builder import MFGraphBuilder


# Page configuration
st.set_page_config(
    page_title="🤖 Stock Market Search",
    page_icon="🔍",
    layout="centered"
)

# Simple CSS
st.markdown("""
    <style>
    .stButton > button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize session state variables"""
    
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = None
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'mf_rag_system' not in st.session_state:
        st.session_state.mf_rag_system = None
    if 'mf_initialized' not in st.session_state:
        st.session_state.mf_initialized = False
    if 'mf_history' not in st.session_state:
        st.session_state.mf_history = []
    if 'ip_rag_system' not in st.session_state:
        st.session_state.ip_rag_system = None
    if 'ip_initialized' not in st.session_state:
        st.session_state.ip_initialized = False
    if 'ip_history' not in st.session_state:
        st.session_state.ip_history = []

@st.cache_resource
def initialize_rag():
    """Initialize the Stock Market RAG system (cached)"""
    try:
        # Initialize components
        llm = Config.get_llm()
        doc_processor = DocumentProcessor(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )
        vector_store = VectorStore() 
        
        # Use default URLs
        urls = Config.DEFAULT_DOC_URL
        
        
        # Process documents
        documents = doc_processor.process_url(urls)

        
        # Create vector store
        #vector_store.create_vectorstore(documents)
        vector_store.create_retriever(documents)

        
        # Build graph
        graph_builder = GraphBuilder(
            retriever=vector_store.get_retriever(),
            llm=llm
        )
        graph_builder.build()
        
        return graph_builder, len(documents)
    except Exception as e:
        st.error(f"Failed to initialize: {str(e)}")
        return None, 0

@st.cache_resource
def mf_initialize_rag():
    """Initialize the Mutual Fund RAG system (cached)"""
    try:
        # Initialize components
        llm = Config.get_llm()
        doc_processor = DocumentProcessor(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )
        vector_store = VectorStore() 
        
        # Use default URLs
        urls = Config.MutualFund_DOC_URL
        
        
        # Process documents
        documents = doc_processor.process_url(urls)

        
        # Create vector store
        #vector_store.create_vectorstore(documents)
        vector_store.create_retriever(documents)

        
        # Build graph
        mf_graph_builder = MFGraphBuilder(
            retriever=vector_store.get_retriever(),
            llm=llm
        )
        mf_graph_builder.build()
        
        return mf_graph_builder, len(documents)
    except Exception as e:
        st.error(f"Failed to initialize: {str(e)}")
        return None, 0

def generate_question_voice():
    question = "Enter Monthly income in numbers only."
    if question:
        femalevoice.generate_voice(question, "validation.mp3")
        st.session_state["question_voice_ready"] = True

def main():
    """Main application"""
    init_session_state()
     
   
    
    selected_menu = st.radio(
        "Navigation",
        ["Stock Market", "Mutual Fund", "Investment Plan"],
        horizontal=True,
        label_visibility="collapsed",
        key="top_menu",
    )

    descriptions = {
        "Stock Market": "Ask questions about stocks and IPOs.",
        "Mutual Fund": "Ask questions about mutual funds and SIPs.",
        "Investment Plan": "Explore investment planning options.",
    }

     # Title
    selected_menu = st.session_state.get("top_menu", "Stock Market")
    st.title(f"🔍 {selected_menu}")
    st.markdown(descriptions[selected_menu])
    if selected_menu == "Mutual Fund":
        mf_rag_system, num_chunks = mf_initialize_rag()
        if mf_rag_system:
            st.session_state.mf_rag_system = mf_rag_system
            st.session_state.mf_initialized = True
            st.success(f"✅ System ready! ({num_chunks} document chunks loaded)")
            question = "Not required"
            if st.session_state.mf_rag_system:
                with st.spinner("Searching..."):
                    # Get answer
                    result = st.session_state.mf_rag_system.run(question)
                # Display answer
                st.markdown("### 💡 Answer")
                st.success(result['answer'])

    if selected_menu == "Investment Plan":
        
        st.markdown("---")
        st.markdown("### Monthly Income")
        question = st.text_input(
            "Monthly Income",
            placeholder="Enter your Monthly Income",
            on_change=generate_question_voice,
        )
        
        if st.session_state.get("question_voice_ready"):
            st.audio("validation.mp3", format="audio/mp3")
    if selected_menu == "Stock Market":
        print(str(selected_menu))
    # Initialize system
        if not st.session_state.initialized:
            with st.spinner("Loading system..."):
                rag_system, num_chunks = initialize_rag()
                if rag_system:
                    st.session_state.rag_system = rag_system
                    st.session_state.initialized = True
                    st.success(f"✅ System ready! ({num_chunks} document chunks loaded)")
        
        st.markdown("---")

        # Search interface
        with st.form("search_form"):
            question = st.text_input(
                "Enter your question:",
                placeholder="What would you like to know?"
            )
            submit = st.form_submit_button("🔍 Search")        
                    
        # Process search
        if submit and question:
            if st.session_state.rag_system:
                with st.spinner("Searching..."):
                    start_time = time.time()
                        
                    # Get answer
                    result = st.session_state.rag_system.run(question)
                    femalevoice.generate_voice(result['answer'], "output.mp3")
                    
                    elapsed_time = time.time() - start_time
                        
                    # Add to history
                    st.session_state.history.append({
                        'question': question,
                        'answer': result['answer'],
                        'time': elapsed_time
                    })
                        
                # Display answer
                st.markdown("### 💡 Answer")
                st.success(result['answer'])
                st.markdown("### 🔊 Voice Response")
                st.audio("output.mp3")
            
                # Show retrieved docs in expander
                with st.expander("📄 Source Documents"):
                    for i, doc in enumerate(result['retrieved_docs'], 1):
                        st.text_area(
                            f"Document {i}",
                            doc.page_content[:300] + "...",
                            height=100,
                            disabled=True
                        )
                        
                st.caption(f"⏱️ Response time: {elapsed_time:.2f} seconds")
    
    # Show history
    if st.session_state.history:
        st.markdown("---")
        st.markdown("### 📜 Recent Searches")
        
        for item in reversed(st.session_state.history[-6:]):  # Show last 6
            with st.container():
                st.markdown(f"**Q:** {item['question']}")
                st.markdown(f"**A:** {item['answer'][:200]}...")
                st.caption(f"Time: {item['time']:.2f}s")
                st.markdown("")
        
        text = "\n".join(
            f"Q: {item['question']}\nA: {item['answer'][:200]}..." for item in reversed(st.session_state.history[-6:])
        )
        GeneratePdf.OUTPUT_FILE = GeneratePdf.PROJECT_DIR / f"{item['question']}.pdf"
        GeneratePdf.OUTPUT_FILE.write_bytes(GeneratePdf.create_pdf(text))

        st.success(f"📄 PDF generated: {GeneratePdf.OUTPUT_FILE}")
if __name__ == "__main__":
    main()