# Customized Web Chatbot

**Turn any website into an interactive Q&A chatbot — with source citations, multi-turn conversations, and smart retrieval.**

## Overview

ASL Web Chatbot is a Retrieval-Augmented Generation (RAG) application that indexes any website and provides accurate, grounded answers using only that site's content. Point it at a URL, wait for one-time indexing, and start asking questions — every answer is cited with source links back to the original pages.

The project offers **two modes**:

- **Chatbot Mode** — Standard RAG pipeline with single-prompt retrieval and streaming responses
- **Agent Mode** — LangGraph-powered agent that decides which queries to run, resolves follow-up references to past topics, and retrieves across multiple conversation turns for better multi-turn accuracy

## Features

- **One-click website indexing** — Paste a URL, the app auto-discovers all pages via sitemap
- **RAG-powered answers** — Grounded strictly in the indexed site's content, no hallucinations
- **Source citations** — Every answer includes clickable links to the original pages
- **Multi-turn conversations** — Chat history awareness for follow-up questions
- **Agent mode** — Smart retrieval that resolves references like "tell me more about the first one" by querying multiple past topics
- **Streaming responses** — Token-by-token output for a real-time feel
- **Conversation management** — Create, rename, switch, and delete chat sessions
- **Dark-themed UI** — Polished Streamlit interface with sidebar navigation
- **Persistent vector store** — Indexed sites are cached and reused across sessions
- **Cross-platform scraping** — Handles Windows' event loop quirks for reliable crawling

## Tech Stack

| Category        | Technology                           |
| --------------  | ------------------------------------ |
| **Language**    | Python 3.12+                         |
| **UI**          | Streamlit                            |
| **RAG**         | LangChain, LangChain Chroma          |
| **Agent**       | LangGraph, LangChain Agents          |
| **LLM**         | Mistral AI                           |
| **Agent Model** | Mistral AI                           |
| **Embeddings**  | Mistral Embed (mistral-embed)        |
| **Vector DB**   | ChromaDB (persistent)                |
| **Web Scraping**| Crawl4AI (async, headless Chromium)  |
| **Sitemap**     | ultimate-sitemap-parser              |
| **Env Config**  | python-dotenv                        |

## Requirements

- **Python 3.12+**
- **uv** package manager (or pip)
- **Mistral API key** — get one free at [console.mistral.ai](https://console.mistral.ai/)
- **Playwright browsers** — installed automatically (see setup)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/swayam279/Customized_Web_Chatbot.git
cd ASL-Web-Chatbot
```

### 2. Set up environment variables

Create a `.env` file in the project root:

```env
MISTRAL_API_KEY=your_mistral_api_key_here
```

### 3. Install dependencies

Using [uv](https://docs.astral.sh/uv/) (recommended):

```bash
uv sync
```

Or with pip:

```bash
pip install -e .
```

### 4. Install Playwright browsers

```bash
uv run playwright install
uv run playwright install-deps
```

## Usage

### Standard Chatbot Mode

```bash
uv run streamlit run src/app.py
```

1. Paste a website URL in the sidebar (e.g. `https://docs.langchain.com/`)
2. Click **Start** — the app indexeses the entire site (one-time per URL)
3. Ask questions — answers appear with source citations

### Agent Mode

```bash
uv run streamlit run src/AgentApp.py
```

Same interface as above, but with smarter multi-turn retrieval. The agent decides which past queries to re-run when resolving follow-ups, making it ideal for deep exploration of documentation sites.

### CLI Pipeline (for scripting)

```bash
uv run python src/run.py
```

Prompts for a URL and runs the full indexing pipeline directly in the terminal.

### Quick Start — No Indexing

```bash
uv run python src/test.py
```

Run the included test/demo module to verify everything is wired up correctly.

## Project Structure

```
ASL-Web-Chatbot/
├── src/
│   ├── AgentApp.py            # Streamlit UI — Agent mode
│   ├── app.py                 # Streamlit UI — Standard chatbot mode
│   ├── Agent.py               # LangGraph agent with multi-query retrieval tool
│   ├── chatbot.py             # Standard RAG chat functions (non-streaming + streaming)
│   ├── run.py                 # CLI entry point — full indexing pipeline
│   ├── vector_store.py        # ChromaDB setup, embeddings, retriever (MMR)
│   ├── crawler.py             # Async web scraper via Crawl4AI
│   ├── sitemap.py             # Sitemap discovery via ultimate-sitemap-parser
│   ├── url_validator.py       # URL accessibility checker
│   ├── document_generator.py  # Convert scraped data to LangChain Documents
│   ├── text_splitter.py       # Chunk documents with overlap filtering
│   ├── markdown_cleaner.py    # Clean up markdown from web scraper,
│   └── test.py                # Test/demo module
├── Notebooks/
│   └── workflow.ipynb         # Interactive development notebook
├── chroma_web_chatbot/        # Persistent vector store (auto-created)
├── pyproject.toml             # Project config + dependencies
└── .env                       # Environment variables (create this)
```

## How It Works

### Indexing Pipeline

```
URL → Sitemap Discovery → URL Validation → Async Scraping → Markdown Cleaning →
Document Building → Text Splitting (chunks) → ChromaDB Embedding & Storage
```

1. **Sitemap Discovery** — Fetches `sitemap.xml` and extracts all page URLs
2. **URL Validation** — Confirms each URL is accessible before scraping
3. **Async Scraping** — Crawl4AI renders pages headlessly, extracts clean markdown with content filtering/removes noise (nav, footer, sidebar)
4. **Document Building** — Wrapped into LangChain `Document` objects with metadata
5. **Text Splitting** — Documents split into 2,000-char chunks with 200-char overlap
6. **Vector Storage** — Chunks embedded via Mistral Embed and stored in ChromaDB

### Chat Flow

```
User Question → Chat History Window (last 3 turns) →
Retriever Query → MMR Retrieval (k=5, fetch_k=15) →
Mistral LLM + System Prompt → Streaming Answer + Sources
```

### Agent Flow (Agent Mode)

```
User Question → Agent decides which past queries are relevant →
multi_query_retriever tool (parallel execution) →
Merged, deduplicated context → Mistral LLM → Answer + Sources
```

The agent mode uses a LangGraph loop to decide which queries to run, making it particularly effective at resolving follow-ups like "tell me more about X" by searching for both the original question and the current one simultaneously.

## Configuration

### Environment Variables

| Variable          | Description                | Required |
| ----------------- | -------------------------- | -------- |
| `MISTRAL_API_KEY` | API key for Mistral AI API | Yes      |

### Retrieval Parameters

The retriever uses **MMR (Maximal Marginal Relevance)** for diverse results:

- `k=5` — returns 5 documents per query
- `fetch_k=15` — fetches 15 candidates
- `lambda_mult=0.5` — balances relevance vs diversity

### Chunking Parameters

- `chunk_size=2000` characters per chunk
- `chunk_overlap=200` characters between consecutive chunks
- Minimum chunk length: 100 characters (filtered out)

## Testing

A `test.py` module is included in the `src/` directory for verifying the setup.

For the vector store:
```bash
uv run python src/vector_store.py
```

For the text splitter:
```bash
uv run python src/text_splitter.py
```

For the sitemap module:
```bash
uv run python src/sitemap.py
```

## Development

### Code Style

[Tool: ruff](https://docs.astral.sh/ruff/) is configured in `pyproject.toml`:

```bash
uv run ruff check src/
uv run ruff format src/
```

## Acknowledgments

- [LangChain](https://github.com/langchain-ai/langchain) for the RAG framework
- [ChromaDB](https://github.com/chroma-core/chroma) for vector storage
- [Crawl4AI](https://github.com/unclecode/crawl4ai) for web scraping
- [Mistral AI](https://mistral.ai/) for LLM + embeddings
- [Streamlit](https://streamlit.io/) for the UI framework
- [LangGraph](https://github.com/langchain-ai/langgraph) for agent orchestration
