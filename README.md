# 🧠 InsightGPT – Intelligent Knowledge Explorer

A powerful Streamlit web application that uses OpenAI's GPT-4 to analyze documents, generate summaries, extract insights, and provide an interactive question-answering interface.

## Why This Project
InsightGPT demonstrates my ability to build end-to-end AI systems — combining modern LLM APIs, retrieval-based search, and human-centered UX. The app was designed to show practical use of agentic reasoning and contextual retrieval pipelines for real-world data exploration.


![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

### 📝 **Intelligent Summarization**
- Generates comprehensive, well-structured summaries of your documents
- Captures main ideas, key points, and important details
- Maintains the core message and context of the original

### 🔍 **Deep Insight Extraction**
- **Key Entities**: Identifies important people, organizations, places, and concepts
- **Main Themes**: Extracts core topics and ideas discussed in the document
- **Action Items**: Highlights tasks, recommendations, and next steps
- **Keywords**: Generates relevant keywords and key phrases

### 💬 **Interactive Q&A (RAG-Style)**
- Ask any question about your document
- Uses FAISS vector search to find relevant content
- Maintains chat history for contextual follow-up questions
- Provides accurate answers based on document content

### 📊 **Document Statistics**
- Word, sentence, and paragraph counts
- Character count and reading metrics
- Visual representation of document structure

### 📥 **Downloadable Reports**
- Generate comprehensive reports with all insights
- Export as TXT format
- Includes summary, insights, keywords, and Q&A history

### 🎨 **Polished UI**
- Clean, responsive Streamlit interface
- Tab-based navigation
- Custom styling with gradient headers
- Expandable sections and accordions
- Color-coded chat messages

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/InsightGPT.git
   cd InsightGPT
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

### Running the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📖 Usage Guide

### 1. **Configure API Key**
   - Enter your OpenAI API key in the sidebar
   - Or set it in the `.env` file before running the app

### 2. **Select Model**
   - Choose between GPT-4 (more accurate) or GPT-3.5-turbo (faster)
   - GPT-4 recommended for best results

### 3. **Upload or Paste Document**
   - **Upload File**: Supports PDF, DOCX, and TXT files (max 10MB)
   - **Paste Text**: Directly paste text content (minimum 50 characters)

### 4. **Process Document**
   - Click "Process Document" or "Process Text"
   - Wait for analysis to complete (may take 30-60 seconds)

### 5. **Explore Results**
   - **Summary Tab**: View document statistics and AI-generated summary
   - **Insights Tab**: Explore extracted entities, themes, and action items
   - **Q&A Tab**: Ask questions about your document
   - **Download Tab**: Generate and download comprehensive report

## 🏗️ Project Structure

```
InsightGPT/
├── app.py                      # Main Streamlit application
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
└── utils/
    ├── __init__.py
    ├── document_processor.py  # Document parsing and chunking
    ├── openai_helper.py       # OpenAI API integration
    └── embeddings.py          # FAISS vector store and search
```

## 🔧 Configuration

Edit `config.py` to customize:

- **MAX_FILE_SIZE_MB**: Maximum upload file size (default: 10MB)
- **CHUNK_SIZE**: Text chunk size for embeddings (default: 1000 characters)
- **CHUNK_OVERLAP**: Overlap between chunks (default: 200 characters)
- **TOP_K_RESULTS**: Number of relevant chunks to retrieve (default: 3)
- **Temperature settings**: Control creativity of AI responses

## 🛠️ Technical Details

### Technologies Used

- **Streamlit**: Web application framework
- **OpenAI API**: GPT-4/3.5 for text generation
- **FAISS**: Facebook's vector similarity search
- **PyPDF2**: PDF text extraction
- **python-docx**: DOCX file processing
- **tiktoken**: Token counting for OpenAI models

### Key Components

1. **Document Processing**
   - Extracts text from PDF, DOCX, and TXT files
   - Splits text into overlapping chunks for embedding
   - Handles various encodings and file formats

2. **OpenAI Integration**
   - Summarization with controlled temperature
   - Structured insight extraction
   - Context-aware question answering
   - Token counting and management

3. **Vector Search**
   - Creates embeddings using OpenAI's text-embedding-ada-002
   - Builds FAISS index for fast similarity search
   - Retrieves relevant context for Q&A

## 📸 Screenshots

### Main Interface
*(Screenshot placeholder - The app features a purple gradient header with tab-based navigation)*

### Summary View
*(Screenshot placeholder - Shows document statistics and AI-generated summary)*

### Insights Extraction
*(Screenshot placeholder - Displays keywords, entities, themes, and action items)*

### Interactive Q&A
*(Screenshot placeholder - Chat interface with color-coded messages)*

## 🚨 Error Handling

The app includes comprehensive error handling for:

- Invalid or missing API keys
- Unsupported file formats
- File size limits
- Empty or invalid text input
- API call failures
- Encoding errors
- Network issues

## 💡 Tips for Best Results

1. **Use GPT-4** for more accurate and detailed analysis
2. **Upload clear, well-formatted documents** for better text extraction
3. **Ask specific questions** in the Q&A interface
4. **For long documents**, processing may take longer due to embedding generation
5. **Check token limits**: Very large documents may be truncated

## 🔐 Security Notes

- API keys are stored in environment variables
- Never commit `.env` file to version control
- API keys are masked in the UI with password input
- Consider implementing rate limiting for production use

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🐛 Known Issues

- Very large PDF files (>50 pages) may take significant time to process
- Some PDF files with complex formatting may not extract text correctly
- Embedding generation can be slow for documents >10,000 words

## 🔮 Future Enhancements

- [ ] Support for more file formats (PPT, CSV, Excel)
- [ ] Multi-language support
- [ ] Custom prompt templates
- [ ] Export reports as PDF or Markdown
- [ ] Batch processing of multiple documents
- [ ] Comparison between multiple documents
- [ ] Integration with other LLM providers
- [ ] Persistent storage of processed documents

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Email: support@insightgpt.example.com

## 👏 Acknowledgments

- OpenAI for providing the GPT-4 API
- Streamlit for the amazing web framework
- Facebook Research for FAISS

---

**Built with ❤️ using Streamlit and OpenAI GPT-4**