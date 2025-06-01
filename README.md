# MTG Workflow with Simple Async State Saving

A clean, minimal implementation of an AI-driven agentic workflow using **LangGraph** and **Playwright**, with automatic **per-node state saving**. Designed for browser automation and debugging through JSON state snapshots.

## ✨ Features

- **Graph-based workflow execution** with [LangGraph](https://github.com/langchain-ai/langgraph)
- **Browser automation** powered by [Playwright](https://playwright.dev/)
- **Auto state saving**: Each node saves its state as a timestamped `.json` file
- **Designed for interactive exploration** in Jupyter Notebooks
- **Lightweight & modular**: Easy to extend or modify

---

## 📂 Project Structure

```
.
├── async_state_saver.py          # Utility to initialize and save state after each node
├── file.ipynb                    # Jupyter notebook for experimentation
├── graph.py                      # Defines LangGraph structure and node logic
├── langgraph.json                # Optional metadata/config for LangGraph
├── requirements.txt              # Python dependencies
├── state_reader.py               # Read and inspect saved state files
└── workflow_states/              # Saved JSON states for each node
    └── mtg_workflow_<timestamp>/
        ├── 001_launch_browser_<timestamp>.json
        ├── 002_navigate_page_<timestamp>.json
        └── 003_analyze_page_<timestamp>.json
```

---

## ⚙️ Setup

1. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   playwright install
   ```

2. **Set required environment variables**:

   Create a `.env` file or export these in your shell:

   ```env
   OPENAI_API_KEY=sk-...
   TAVILY_API_KEY=...
   LANGCHAIN_API_KEY=...
   LANGCHAIN_TRACING_V2=true
   ANTHROPIC_API_KEY=...
   ```

---

## 🚀 Usage

- Run `langgraph dev` to open UI interface for node execution. 
- Each node in the graph executes a browser action (e.g., open page, navigate, analyze).
- After each node, state is saved under `workflow_states/` as:

  ```
  001_launch_browser_<timestamp>.json
  002_navigate_page_<timestamp>.json
  ...
  ```

- Use `state_reader.py` to load and inspect saved states.

---

## 🧪 For Experimentation

This project is built to be used inside Jupyter for:

- Run the `file.ipynb` notebook to trigger the graph for experimentation
- Debugging AI agent behavior
- Capturing intermediate workflow states
- Visualizing form-filling tasks or web scraping logic

---

## 📜 License

MIT License

---

