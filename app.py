import streamlit as st
from datetime import datetime
from config import Config
from utils.document_processor import DocumentProcessor, validate_text_input
from utils.openai_helper import OpenAIHelper
from utils.embeddings import EmbeddingStore


# Page configuration
st.set_page_config(
    page_title="InsightGPT",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .stat-box {
        padding: 1rem;
        background-color: #f0f2f6;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
    .insight-item {
        padding: 0.5rem;
        margin: 0.3rem 0;
        background-color: #f8f9fa;
        border-radius: 5px;
        border-left: 3px solid #764ba2;
    }
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196F3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'document_text' not in st.session_state:
        st.session_state.document_text = None
    if 'document_stats' not in st.session_state:
        st.session_state.document_stats = None
    if 'summary' not in st.session_state:
        st.session_state.summary = None
    if 'insights' not in st.session_state:
        st.session_state.insights = None
    if 'keywords' not in st.session_state:
        st.session_state.keywords = None
    if 'embedding_store' not in st.session_state:
        st.session_state.embedding_store = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'processed' not in st.session_state:
        st.session_state.processed = False
    if 'api_key' not in st.session_state:
        st.session_state.api_key = Config.OPENAI_API_KEY


def render_sidebar():
    """Render sidebar with file upload and configuration"""
    with st.sidebar:
        st.markdown("### 🧠 InsightGPT")
        st.markdown("---")
        
        # API Key configuration
        st.markdown("#### 🔑 API Configuration")
        
        api_key_input = st.text_input(
            "OpenAI API Key",
            value=st.session_state.api_key if st.session_state.api_key else "",
            type="password",
            help="Enter your OpenAI API key. Get one at https://platform.openai.com/api-keys"
        )
        
        if api_key_input:
            st.session_state.api_key = api_key_input
        
        # Validate API key
        api_key_valid = Config.validate_api_key(st.session_state.api_key)
        
        if not api_key_valid:
            st.warning("⚠️ Please enter a valid OpenAI API key to continue")
            st.info("💡 Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)")
        else:
            st.success("✅ API key configured")
        
        st.markdown("---")
        
        # Model selection
        st.markdown("#### ⚙️ Model Settings")
        model_option = st.selectbox(
            "Select Model",
            options=["gpt-4", "gpt-3.5-turbo"],
            index=0,
            help="GPT-4 is more accurate but slower and more expensive"
        )
        
        st.session_state.selected_model = model_option
        
        st.markdown("---")
        
        # Document input
        st.markdown("#### 📄 Document Input")
        
        input_method = st.radio(
            "Choose input method:",
            options=["Upload File", "Paste Text"],
            help="Upload a document or paste text directly"
        )
        
        document_text = None
        
        if input_method == "Upload File":
            uploaded_file = st.file_uploader(
                "Upload Document",
                type=['pdf', 'docx', 'txt'],
                help="Supported formats: PDF, DOCX, TXT (max 10MB)"
            )
            
            if uploaded_file and api_key_valid:
                if st.button("📊 Process Document", type="primary"):
                    with st.spinner("Processing document..."):
                        processor = DocumentProcessor()
                        text, success = processor.process_uploaded_file(uploaded_file)
                        
                        if success:
                            document_text = text
                            st.success("✅ Document processed successfully!")
        
        else:  # Paste Text
            pasted_text = st.text_area(
                "Paste your text here:",
                height=200,
                placeholder="Enter or paste your document text here..."
            )
            
            if pasted_text and api_key_valid:
                if st.button("📊 Process Text", type="primary"):
                    is_valid, error_msg = validate_text_input(pasted_text)
                    if is_valid:
                        document_text = pasted_text
                        st.success("✅ Text ready for processing!")
                    else:
                        st.error(f"❌ {error_msg}")
        
        # Process the document if we have text
        if document_text:
            process_document(document_text)
        
        st.markdown("---")
        
        # Clear/Reset button
        if st.session_state.processed:
            if st.button("🔄 Clear All", help="Reset and start with a new document"):
                for key in list(st.session_state.keys()):
                    if key != 'api_key':
                        del st.session_state[key]
                initialize_session_state()
                st.rerun()
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <small>
        **InsightGPT** v1.0<br>
        Powered by OpenAI GPT-4<br>
        Built with Streamlit
        </small>
        """, unsafe_allow_html=True)


def process_document(text: str):
    """Process document: generate summary, insights, and embeddings"""
    try:
        # Store document text
        st.session_state.document_text = text
        
        # Get document statistics
        processor = DocumentProcessor()
        st.session_state.document_stats = processor.get_text_stats(text)
        
        # Initialize OpenAI helper
        openai_helper = OpenAIHelper(
            api_key=st.session_state.api_key,
            model=st.session_state.selected_model
        )
        
        # Generate summary
        with st.spinner("Generating summary..."):
            st.session_state.summary = openai_helper.generate_summary(text)
        
        # Extract insights
        with st.spinner("Extracting insights..."):
            st.session_state.insights = openai_helper.extract_insights(text)
        
        # Generate keywords
        with st.spinner("Generating keywords..."):
            st.session_state.keywords = openai_helper.generate_keywords(text)
        
        # Create embeddings for Q&A
        with st.spinner("Creating embeddings for Q&A..."):
            chunks = processor.chunk_text(text)
            embedding_store = EmbeddingStore(api_key=st.session_state.api_key)
            
            if embedding_store.create_embeddings(chunks):
                st.session_state.embedding_store = embedding_store
        
        # Mark as processed
        st.session_state.processed = True
        st.session_state.chat_history = []  # Reset chat history
        
    except Exception as e:
        st.error(f"Error processing document: {str(e)}")
        st.session_state.processed = False


def render_summary_tab():
    """Render the summary tab"""
    if not st.session_state.processed:
        st.info("👈 Upload a document or paste text to get started")
        return
    
    st.markdown("### 📝 Document Summary")
    
    # Document statistics
    col1, col2, col3, col4 = st.columns(4)
    stats = st.session_state.document_stats
    
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <h4>{stats['words']:,}</h4>
            <p>Words</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-box">
            <h4>{stats['sentences']:,}</h4>
            <p>Sentences</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-box">
            <h4>{stats['paragraphs']:,}</h4>
            <p>Paragraphs</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-box">
            <h4>{stats['characters']:,}</h4>
            <p>Characters</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Summary
    if st.session_state.summary:
        st.markdown("#### 📄 Summary")
        st.markdown(st.session_state.summary)
    else:
        st.warning("Summary generation failed. Please try again.")


def render_insights_tab():
    """Render the insights tab"""
    if not st.session_state.processed:
        st.info("👈 Upload a document or paste text to get started")
        return
    
    st.markdown("### 🔍 Extracted Insights")
    
    # Keywords
    if st.session_state.keywords:
        with st.expander("🏷️ **Key Keywords & Phrases**", expanded=True):
            keyword_html = " ".join([
                f'<span style="background-color: #e3f2fd; padding: 0.3rem 0.6rem; margin: 0.2rem; border-radius: 15px; display: inline-block;">{kw}</span>'
                for kw in st.session_state.keywords
            ])
            st.markdown(keyword_html, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Insights
    if st.session_state.insights:
        col1, col2 = st.columns(2)
        
        with col1:
            # Key Entities
            with st.expander("👥 **Key Entities**", expanded=True):
                entities = st.session_state.insights.get('entities', [])
                if entities:
                    for entity in entities:
                        st.markdown(f'<div class="insight-item">• {entity}</div>', unsafe_allow_html=True)
                else:
                    st.info("No entities identified")
            
            # Main Themes
            with st.expander("💡 **Main Themes**", expanded=True):
                themes = st.session_state.insights.get('themes', [])
                if themes:
                    for theme in themes:
                        st.markdown(f'<div class="insight-item">• {theme}</div>', unsafe_allow_html=True)
                else:
                    st.info("No themes identified")
        
        with col2:
            # Action Items
            with st.expander("✅ **Action Items**", expanded=True):
                actions = st.session_state.insights.get('action_items', [])
                if actions:
                    for i, action in enumerate(actions, 1):
                        st.markdown(f'<div class="insight-item">{i}. {action}</div>', unsafe_allow_html=True)
                else:
                    st.info("No action items identified")


def render_qa_tab():
    """Render the Q&A tab"""
    if not st.session_state.processed:
        st.info("👈 Upload a document or paste text to get started")
        return
    
    st.markdown("### 💬 Ask Questions About Your Document")
    
    # Check if embeddings are ready
    if not st.session_state.embedding_store or not st.session_state.embedding_store.is_ready():
        st.error("Embedding store not ready. Please reprocess the document.")
        return
    
    # Display chat history
    st.markdown("#### Chat History")
    
    chat_container = st.container()
    
    with chat_container:
        if st.session_state.chat_history:
            for msg in st.session_state.chat_history:
                if msg['role'] == 'user':
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>You:</strong><br>{msg['content']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <strong>Assistant:</strong><br>{msg['content']}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("💡 Ask any question about your document. The AI will search through the content to find relevant information.")
    
    st.markdown("---")
    
    # Question input
    col1, col2 = st.columns([4, 1])
    
    with col1:
        question = st.text_input(
            "Your question:",
            placeholder="e.g., What are the main conclusions? Who are the key people mentioned?",
            key="question_input"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        ask_button = st.button("🚀 Ask", type="primary", use_container_width=True)
    
    if ask_button and question:
        with st.spinner("Searching document and generating answer..."):
            # Search for relevant chunks
            search_results = st.session_state.embedding_store.search(question, top_k=3)
            
            if search_results:
                # Extract just the text chunks
                relevant_chunks = [chunk for chunk, _ in search_results]
                
                # Get answer
                openai_helper = OpenAIHelper(
                    api_key=st.session_state.api_key,
                    model=st.session_state.selected_model
                )
                
                answer = openai_helper.answer_question(
                    question=question,
                    context_chunks=relevant_chunks,
                    chat_history=st.session_state.chat_history
                )
                
                if answer:
                    # Add to chat history
                    st.session_state.chat_history.append({
                        'role': 'user',
                        'content': question
                    })
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': answer
                    })
                    
                    # Rerun to update display
                    st.rerun()
            else:
                st.error("Could not find relevant information in the document.")
    
    # Clear chat button
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()


def render_download_tab():
    """Render the download tab"""
    if not st.session_state.processed:
        st.info("👈 Upload a document or paste text to get started")
        return
    
    st.markdown("### 📥 Download Report")
    
    st.info("Generate a comprehensive report with all insights and summaries.")
    
    # Generate report
    report = generate_report()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Download as TXT
        st.download_button(
            label="📄 Download as TXT",
            data=report,
            file_name=f"insight_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col2:
        # Preview button
        if st.button("👁️ Preview Report", use_container_width=True):
            with st.expander("Report Preview", expanded=True):
                st.text(report)


def generate_report() -> str:
    """Generate a downloadable report"""
    report_lines = []
    
    # Header
    report_lines.append("=" * 80)
    report_lines.append("INSIGHTGPT - DOCUMENT ANALYSIS REPORT")
    report_lines.append("=" * 80)
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    
    # Document Statistics
    report_lines.append("-" * 80)
    report_lines.append("DOCUMENT STATISTICS")
    report_lines.append("-" * 80)
    stats = st.session_state.document_stats
    report_lines.append(f"Words: {stats['words']:,}")
    report_lines.append(f"Sentences: {stats['sentences']:,}")
    report_lines.append(f"Paragraphs: {stats['paragraphs']:,}")
    report_lines.append(f"Characters: {stats['characters']:,}")
    report_lines.append("")
    
    # Summary
    if st.session_state.summary:
        report_lines.append("-" * 80)
        report_lines.append("SUMMARY")
        report_lines.append("-" * 80)
        report_lines.append(st.session_state.summary)
        report_lines.append("")
    
    # Keywords
    if st.session_state.keywords:
        report_lines.append("-" * 80)
        report_lines.append("KEY KEYWORDS & PHRASES")
        report_lines.append("-" * 80)
        report_lines.append(", ".join(st.session_state.keywords))
        report_lines.append("")
    
    # Insights
    if st.session_state.insights:
        insights = st.session_state.insights
        
        # Entities
        report_lines.append("-" * 80)
        report_lines.append("KEY ENTITIES")
        report_lines.append("-" * 80)
        entities = insights.get('entities', [])
        if entities:
            for entity in entities:
                report_lines.append(f"• {entity}")
        else:
            report_lines.append("None identified")
        report_lines.append("")
        
        # Themes
        report_lines.append("-" * 80)
        report_lines.append("MAIN THEMES")
        report_lines.append("-" * 80)
        themes = insights.get('themes', [])
        if themes:
            for theme in themes:
                report_lines.append(f"• {theme}")
        else:
            report_lines.append("None identified")
        report_lines.append("")
        
        # Action Items
        report_lines.append("-" * 80)
        report_lines.append("ACTION ITEMS")
        report_lines.append("-" * 80)
        actions = insights.get('action_items', [])
        if actions:
            for i, action in enumerate(actions, 1):
                report_lines.append(f"{i}. {action}")
        else:
            report_lines.append("None identified")
        report_lines.append("")
    
    # Q&A History
    if st.session_state.chat_history:
        report_lines.append("-" * 80)
        report_lines.append("Q&A HISTORY")
        report_lines.append("-" * 80)
        for msg in st.session_state.chat_history:
            if msg['role'] == 'user':
                report_lines.append(f"\nQ: {msg['content']}")
            else:
                report_lines.append(f"A: {msg['content']}\n")
        report_lines.append("")
    
    # Footer
    report_lines.append("=" * 80)
    report_lines.append("End of Report")
    report_lines.append("=" * 80)
    
    return "\n".join(report_lines)


def main():
    """Main application"""
    # Initialize session state
    initialize_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>🧠 InsightGPT</h1>
        <p>Intelligent Knowledge Explorer</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main content area with tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 Summary",
        "🔍 Insights",
        "💬 Q&A",
        "📥 Download"
    ])
    
    with tab1:
        render_summary_tab()
    
    with tab2:
        render_insights_tab()
    
    with tab3:
        render_qa_tab()
    
    with tab4:
        render_download_tab()


if __name__ == "__main__":
    main()
