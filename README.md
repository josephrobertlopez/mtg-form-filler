# MTG Workflow with Simple Async State Saving

A clean, minimal implementation of an AI-driven agentic workflow using **LangGraph** and **Playwright**, with automatic **per-node state saving**. Designed for browser automation and debugging through JSON state snapshots.

## ✨ Features

- **Graph-based workflow execution** with [LangGraph](https://github.com/langchain-ai/langgraph)
- **Browser automation** powered by [Playwright](https://playwright.dev/)
- **Auto state saving**: Each node saves its state as a timestamped `.json` file
- **Designed for interactive exploration** in Jupyter Notebooks
- **Lightweight & modular**: Easy to extend or modify
- **Python 3.11** via Pipenv and Dockerized setup

---

## 📂 Project Structure

```
.
├── async_state_saver.py          # Utility to initialize and save state after each node
├── file.ipynb                    # Jupyter notebook for experimentation
├── graph.py                      # Defines LangGraph structure and node logic
├── langgraph.json                # Optional metadata/config for LangGraph
├── Pipfile                       # Pipenv environment config (Python 3.11)
├── Pipfile.lock                  # Locked dependency versions
├── Dockerfile                    # Dockerized setup for consistent builds
├── state_reader.py               # Utility for loading state snapshots
└── workflow_states/              # Saved JSON states for each node
    └── mtg_workflow_<timestamp>/
        ├── 001_launch_browser_<timestamp>.json
        ├── 002_navigate_page_<timestamp>.json
        └── 003_analyze_page_<timestamp>.json
```

---

## ⚙️ Setup

### 🐍 Local (Pipenv + Python 3.11)

1. Install dependencies:

   ```bash
   pip install pipenv
   pipenv install
   pipenv run playwright install
   ```

2. Set required environment variables:

   Create a `.env` file or export them:

   ```
   OPENAI_API_KEY=...
   TAVILY_API_KEY=...
   LANGCHAIN_API_KEY=...
   LANGCHAIN_TRACING_V2=true
   ANTHROPIC_API_KEY=...
   ```

3. Run:

   ```bash
   pipenv run python file.ipynb  # or run `langgraph dev` if using LangGraph CLI
   ```

---

### 🐳 Docker

1. Build the container:

   ```bash
   docker build -t mtg-form-filler .
   ```

2. Run the container:

   ```bash
   docker run --rm -it \
     --env-file .env \
     -v $(pwd):/app \
     mtg-form-filler
   ```

Browsers are pre-installed via `playwright install --with-deps`.

---

## 🚀 Usage

- Each graph node performs a web automation step.
- After each step, a timestamped JSON file is saved to `workflow_states/`.
- Use `state_reader.py` to load and inspect intermediate state.
- Run experiments and workflows in `file.ipynb` or using the LangGraph CLI.

---

## 🧪 Experiment Freely

Built for rapid prototyping in Jupyter:

- Debug browser-based agent workflows
- Capture state after every action
- Visualize AI decision-making in web tasks

---

## 📜 License

MIT License

