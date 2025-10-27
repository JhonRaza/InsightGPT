# InsightGPT Development Documentation

## Project Overview

InsightGPT is a production-ready Streamlit application that leverages OpenAI's GPT-4 for intelligent document analysis. The application provides summarization, insight extraction, and RAG-style question answering capabilities.

## Architecture

### Core Components

1. **app.py** - Main Streamlit application
   - Session state management
   - UI rendering and layout
   - User interaction handling
   - Tab-based navigation

2. **config.py** - Configuration management
   - Environment variable loading
   - API settings
   - Model parameters
   - Application constants

3. **utils/document_processor.py** - Document handling
   - Multi-format file parsing (PDF, DOCX, TXT)
   - Text extraction and validation
   - Text chunking with overlap
   - Document statistics calculation

4. **utils/openai_helper.py** - OpenAI integration
   - API client management
   - Summarization with temperature control
   - Structured insight extraction
   - Context-aware Q&A
   - Token counting and management

5. **utils/embeddings.py** - Vector search
   - OpenAI embedding generation
   - FAISS index creation and management
   - Similarity search
   - Result formatting

## Data Flow

```
User Input (File/Text)
    ↓
DocumentProcessor
    ├── Extract text
    ├── Validate input
    └── Generate chunks
    ↓
OpenAIHelper
    ├── Generate summary
    ├── Extract insights
    └── Create keywords
    ↓
EmbeddingStore
    ├── Create embeddings
    └── Build FAISS index
    ↓
User Interface
    ├── Display results
    └── Handle Q&A
```

## Key Design Decisions

### 1. Session State Management
- All processed data stored in `st.session_state`
- Persists across reruns
- Enables chat history and state preservation

### 2. Chunking Strategy
- Default chunk size: 1000 characters
- Overlap: 200 characters
- Breaks at sentence boundaries when possible
- Maintains context across chunks

### 3. Temperature Settings
- Summary: 0.3 (more factual)
- Extraction: 0.2 (very precise)
- Q&A: 0.7 (more conversational)

### 4. Vector Search
- Uses OpenAI's text-embedding-ada-002
- FAISS IndexFlatIP for cosine similarity
- Returns top 3 most relevant chunks
- Normalizes embeddings for consistent scoring

### 5. Error Handling
- Graceful degradation
- User-friendly error messages
- Validation at every input point
- API failure recovery

## API Usage Optimization

### Token Management
- Token counting before API calls
- Automatic text truncation for large documents
- Batch processing for embeddings
- Efficient prompt construction

### Cost Optimization
- Configurable model selection (GPT-4 vs 3.5)
- Chunk-based processing
- Selective API calls
- Caching in session state

## Security Considerations

### API Key Handling
- Environment variable storage
- Password-masked input fields
- No hardcoded keys
- Validation before use

### Data Privacy
- No persistent storage of documents
- Session-based processing
- No external data transmission (except OpenAI)
- User controls all data

## Performance Considerations

### Optimization Strategies
1. **Batch Embedding Generation**
   - Process 10 chunks at a time
   - Progress bar for user feedback
   - Error recovery per batch

2. **Progressive Loading**
   - Show stats immediately
   - Load heavy operations in sequence
   - Clear user feedback at each step

3. **Efficient Chunking**
   - Smart sentence boundary detection
   - Overlap minimizes context loss
   - Configurable chunk sizes

### Bottlenecks
- Embedding generation (1-2s per batch)
- Large PDF parsing (memory intensive)
- Multiple API calls for processing

## Testing Strategy

### Manual Testing Checklist
- [ ] Upload PDF, DOCX, TXT files
- [ ] Test with large documents (>10,000 words)
- [ ] Test with small documents (<100 words)
- [ ] Invalid API key handling
- [ ] Empty file handling
- [ ] Corrupted file handling
- [ ] Q&A with various question types
- [ ] Chat history persistence
- [ ] Report generation and download
- [ ] Model switching (GPT-4 ↔ GPT-3.5)

### Edge Cases
- Empty documents
- Files with no extractable text
- Very long documents (token limits)
- Special characters and encodings
- Rapid consecutive uploads
- Network interruptions

## Deployment Considerations

### Local Deployment
```bash
streamlit run app.py
```

### Cloud Deployment Options
1. **Streamlit Cloud**
   - Free tier available
   - Automatic HTTPS
   - GitHub integration

2. **Heroku**
   - Requires Procfile
   - Set environment variables
   - Use buildpack

3. **Docker**
   - Create Dockerfile
   - Multi-stage build
   - Environment variable injection

### Environment Variables
Required:
- `OPENAI_API_KEY`

Optional:
- `STREAMLIT_SERVER_PORT`
- `STREAMLIT_SERVER_ADDRESS`

## Monitoring and Logging

### Current Logging
- Streamlit's built-in logging
- User-visible error messages
- Progress indicators

### Production Recommendations
- Add structured logging (JSON)
- Track API call volumes
- Monitor response times
- Log error rates
- User analytics (privacy-aware)

## Maintenance

### Regular Updates
- Update dependencies quarterly
- Monitor OpenAI API changes
- Test with new Python versions
- Review security advisories

### Dependency Management
```bash
# Update all packages
pip list --outdated
pip install --upgrade package_name

# Regenerate requirements
pip freeze > requirements.txt
```

## Future Enhancements

### Planned Features
1. **Multi-Document Support**
   - Compare multiple documents
   - Cross-document search
   - Batch processing

2. **Advanced Analytics**
   - Sentiment analysis
   - Topic modeling
   - Named entity recognition

3. **Export Options**
   - PDF reports with formatting
   - Markdown export
   - JSON structured data

4. **Collaboration Features**
   - Shareable sessions
   - Team workspaces
   - Comment threads

### Technical Debt
- Add comprehensive unit tests
- Implement proper logging framework
- Add database for persistent storage
- Implement rate limiting
- Add user authentication

## Contributing Guidelines

### Code Style
- Follow PEP 8
- Use type hints
- Document functions with docstrings
- Keep functions focused and small

### Pull Request Process
1. Fork the repository
2. Create feature branch
3. Add tests if applicable
4. Update documentation
5. Submit PR with clear description

### Commit Message Format
```
type(scope): brief description

Detailed explanation if needed

Fixes #issue_number
```

Types: feat, fix, docs, style, refactor, test, chore

## Resources

### Documentation
- [Streamlit Docs](https://docs.streamlit.io)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [FAISS Documentation](https://faiss.ai)

### Related Projects
- LangChain - LLM application framework
- LlamaIndex - Data framework for LLMs
- ChromaDB - Alternative vector database

## Contact

For questions or contributions:
- GitHub Issues: [Repository URL]
- Email: dev@insightgpt.example.com

---

Last Updated: October 27, 2025
