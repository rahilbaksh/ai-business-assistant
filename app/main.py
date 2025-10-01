import streamlit as st
import os
import tempfile

from document_processor import DocumentProcessor
from multimodal_processor import MultimodalProcessor
from rag_engine import RAGEngine
from visualizer import create_simple_chart
from evaluator import Evaluator

# Minimal CSS for better look
st.markdown("""
<style>
    .card {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton button {
        background-color: #007bff;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        width: 100%;
    }
    .stButton button:hover {
        background-color: #0056b3;
    }
    .answer-box {
        background: #f0f8ff;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="Business AI Assistant",
        layout="wide"
    )
    
    # Header with better spacing
    st.title("📊 Business Intelligence Assistant")
    st.markdown("---")
    st.write("Upload your business documents and get AI-powered insights")
    
    # Initialize components
    if 'doc_processor' not in st.session_state:
        st.session_state.doc_processor = DocumentProcessor()
        st.session_state.multimodal_processor = MultimodalProcessor()
        st.session_state.rag_engine = RAGEngine()
        st.session_state.evaluator = Evaluator()
        st.session_state.all_text = ""
        st.session_state.insights = []
        st.session_state.chat_history = []
    
    # Sidebar
    with st.sidebar:
        st.header("📁 Upload Files")
        
        uploaded_docs = st.file_uploader(
            "Business Documents (PDF, TXT)",
            type=['pdf', 'txt'],
            accept_multiple_files=True
        )
        
        uploaded_image = st.file_uploader(
            "Business Images",
            type=['jpg', 'jpeg', 'png']
        )
        
        if st.button("🚀 Process Files"):
            process_files(uploaded_docs, uploaded_image)
        
        # Show processing status
        if hasattr(st.session_state, 'processed_files'):
            st.sidebar.markdown("---")
            st.sidebar.subheader("📋 Processed Files")
            for file_info in st.session_state.processed_files:
                st.sidebar.write(f"✅ {file_info}")
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 Insights", "🎯 Actions"])
    
    with tab1:
        show_chat()
    with tab2:
        show_insights()
    with tab3:
        show_actions()

def process_files(uploaded_docs, uploaded_image):
    if not uploaded_docs and not uploaded_image:
        st.sidebar.warning("Please upload files first")
        return
    
    all_text = []
    processed_files = []
    
    if uploaded_docs:
        progress_bar = st.sidebar.progress(0)
        for i, doc in enumerate(uploaded_docs):
            with tempfile.NamedTemporaryFile(delete=False, suffix=doc.name) as tmp_file:
                tmp_file.write(doc.getvalue())
                tmp_path = tmp_file.name
            
            # Use the enhanced business document processor
            chunks = st.session_state.doc_processor.process_business_document(tmp_path)
            
            if chunks:
                for chunk in chunks:
                    st.session_state.rag_engine.add_document(chunk, doc.name)
                    all_text.append(chunk)
                processed_files.append(f"{doc.name} ({len(chunks)} chunks)")
                st.sidebar.success(f"✅ {doc.name}")
            else:
                # Fallback to regular processing
                content = st.session_state.doc_processor.process_file(tmp_path)
                if content:
                    st.session_state.rag_engine.add_document(content, doc.name)
                    all_text.append(content)
                    processed_files.append(f"{doc.name} (processed)")
                    st.sidebar.success(f"✅ {doc.name}")
                else:
                    st.sidebar.error(f"❌ Failed to process {doc.name}")
            
            os.unlink(tmp_path)
            progress_bar.progress((i + 1) / len(uploaded_docs))
    
    if uploaded_image:
        with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_image.name) as tmp_file:
            tmp_file.write(uploaded_image.getvalue())
            tmp_path = tmp_file.name
        
        analysis = st.session_state.multimodal_processor.analyze_image(tmp_path)
        st.session_state.image_analysis = analysis
        processed_files.append(f"{uploaded_image.name} (image analysis)")
        st.sidebar.success("✅ Image analyzed")
        
        os.unlink(tmp_path)
    
    if all_text:
        st.session_state.all_text = "\n".join(all_text)
        st.session_state.processed_files = processed_files
        st.sidebar.info(f"📊 Loaded {len(all_text)} text chunks from {len(processed_files)} files")

def show_chat():
    st.markdown('<div class="card"><h3>💬 Ask Questions</h3><p>Get accurate answers about your business documents</p></div>', unsafe_allow_html=True)
    
    # Suggested questions for business documents
    st.subheader("💡 Suggested Questions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Sales Trends"):
            st.session_state.question = "What are the main sales trends in this report?"
        if st.button("Major Risks"):
            st.session_state.question = "What are the major risk factors mentioned?"
    
    with col2:
        if st.button("Legal Issues"):
            st.session_state.question = "What are the major ongoing litigations?"
        if st.button("R&D Investment"):
            st.session_state.question = "How much was invested in research and development?"
    
    with col3:
        if st.button("Business Segments"):
            st.session_state.question = "What are the main business segments?"
        if st.button("Financial Performance"):
            st.session_state.question = "What was the financial performance in 2023?"
    
    # Question input
    question = st.text_input(
        "Enter your question:",
        key="question",
        placeholder="e.g., What are the sales figures for 2023?"
    )
    
    if st.button("🔍 Get Answer", type="primary") and question:
        with st.spinner("🔍 Searching documents..."):
            answer = st.session_state.rag_engine.answer_question(question)
            st.session_state.evaluator.log_query()
            
            # Add to chat history
            st.session_state.chat_history.append({
                "question": question,
                "answer": answer
            })
            
            # Display answer in a nice box
            st.markdown(f'<div class="answer-box"><h4>📋 Answer:</h4><p>{answer}</p></div>', unsafe_allow_html=True)
    
    # Show chat history
    if st.session_state.chat_history:
        st.markdown("---")
        st.subheader("📜 Chat History")
        for i, chat in enumerate(reversed(st.session_state.chat_history[-5:]), 1):
            with st.expander(f"Q: {chat['question'][:50]}..."):
                st.write(f"**Q:** {chat['question']}")
                st.write(f"**A:** {chat['answer']}")

def show_insights():
    st.markdown('<div class="card"><h3>📊 Business Insights</h3><p>Discover patterns and trends in your data</p></div>', unsafe_allow_html=True)
    
    if st.button("🚀 Generate Insights", type="primary"):
        if not st.session_state.all_text:
            st.warning("⚠️ Please upload documents first")
        else:
            with st.spinner("Analyzing documents for insights..."):
                insights = st.session_state.multimodal_processor.generate_ai_insights(st.session_state.all_text)
                st.session_state.insights = insights
                
                if insights:
                    st.success(f"🎉 Found {len(insights)} key insights:")
                    for i, insight in enumerate(insights, 1):
                        st.markdown(f"**{i}.** {insight}")
                    
                    # Try to create visualization
                    try:
                        chart = create_simple_chart(insights, st.session_state.all_text)
                        st.image(chart, use_column_width=True, caption="📈 Insights Visualization")
                    except Exception as e:
                        st.info("📊 Visualization not available for these insights")
                else:
                    st.info("💡 No specific insights generated. Try uploading more detailed business documents.")

def show_actions():
    st.markdown('<div class="card"><h3>🎯 Action Plan</h3><p>Get recommended next steps based on your documents</p></div>', unsafe_allow_html=True)
    
    if st.button("📋 Create Action Plan", type="primary"):
        if not st.session_state.insights:
            st.warning("⚠️ Please generate insights first")
        else:
            with st.spinner("Creating actionable plan..."):
                actions = st.session_state.multimodal_processor.create_action_plan(st.session_state.insights)
                
                if actions:
                    st.success("🎯 Your Action Plan:")
                    for i, action in enumerate(actions, 1):
                        st.markdown(f"**{i}.** {action}")
                    
                    # Add download option
                    action_text = "\n".join([f"{i}. {action}" for i, action in enumerate(actions, 1)])
                    st.download_button(
                        label="📥 Download Action Plan",
                        data=action_text,
                        file_name="business_action_plan.txt",
                        mime="text/plain"
                    )
                else:
                    st.info("💡 No specific actions generated. The system may need more detailed business content.")

if __name__ == "__main__":
    main()