"""
MTG Workflow with Simple Async State Saving
Clean, minimal implementation that saves state after each node automatically.
"""

from typing import TypedDict, Optional, Any
from langgraph.graph import StateGraph, START, END
from playwright.sync_api import sync_playwright
from async_state_saver import init_state_saver, save_state

# Global browser objects
_BROWSER = None
_PAGE = None

class State(TypedDict):
    messages: list
    browser_ready: bool
    page_ready: bool
    page_content: Optional[dict]
    error_message: Optional[str]

def debug_print(node: str, msg: str):
    """Simple debug print."""
    print(f"[{node}] {msg}")

@save_state("launch_browser")
def launch_browser_node(state: State) -> State:
    """Launch Playwright browser."""
    global _BROWSER
    
    # Initialize state if needed
    if not state:
        state = {"messages": [], "browser_ready": False, "page_ready": False, "page_content": None, "error_message": None}
    
    debug_print("launch_browser", "Starting browser...")
    
    try:
        playwright = sync_playwright().start()
        _BROWSER = playwright.chromium.launch(headless=False)
        
        debug_print("launch_browser", "Browser launched!")
        
        return {
            **state,
            "browser_ready": True,
            "messages": state.get("messages", []) + ["Browser launched"]
        }
        
    except Exception as e:
        debug_print("launch_browser", f"Failed: {e}")
        return {
            **state,
            "error_message": f"Browser failed: {e}",
            "messages": state.get("messages", []) + [f"Browser error: {e}"]
        }

@save_state("navigate_page")
def navigate_to_page_node(state: State) -> State:
    """Navigate to MTG site and capture content."""
    global _BROWSER, _PAGE
    
    if not state.get("browser_ready") or not _BROWSER:
        return {
            **state,
            "error_message": "No browser available",
            "messages": state.get("messages", []) + ["No browser for navigation"]
        }
    
    debug_print("navigate_page", "Navigating to MTG Card Smith...")
    
    try:
        _PAGE = _BROWSER.new_page()
        
        # Navigate with retry
        for attempt in range(2):
            try:
                _PAGE.goto(
                    "https://mtgcardsmith.com/mtg-card-maker/edit",
                    wait_until="domcontentloaded",
                    timeout=60000
                )
                break
            except Exception as nav_error:
                if attempt == 0:
                    debug_print("navigate_page", f"Attempt {attempt + 1} failed, retrying...")
                else:
                    raise nav_error
        
        debug_print("navigate_page", "Capturing page content...")
        
        # Capture content
        html_content = _PAGE.content()
        page_title = _PAGE.title()
        current_url = _PAGE.url
        
        try:
            text_content = _PAGE.evaluate("() => document.body.innerText")
        except:
            text_content = "Text extraction failed"
        
        page_data = {
            "html": html_content,
            "text": text_content,
            "title": page_title,
            "url": current_url
        }
        
        debug_print("navigate_page", f"Captured {len(html_content)} chars HTML")
        
        return {
            **state,
            "page_ready": True,
            "page_content": page_data,
            "messages": state.get("messages", []) + [f"Captured page: {len(html_content)} chars"]
        }
        
    except Exception as e:
        error_msg = f"Navigation failed: {e}"
        if "Timeout" in str(e):
            error_msg += " (site may be slow)"
        
        debug_print("navigate_page", error_msg)
        return {
            **state,
            "error_message": error_msg,
            "messages": state.get("messages", []) + [error_msg]
        }

@save_state("analyze_page")
def analyze_page_node(state: State) -> State:
    """Analyze captured page content."""
    
    if not state.get("page_content"):
        return {
            **state,
            "error_message": "No page content to analyze",
            "messages": state.get("messages", []) + ["No content available"]
        }
    
    debug_print("analyze_page", "Analyzing page content...")
    
    try:
        page_data = state["page_content"]
        html_size = len(page_data.get("html", ""))
        text_size = len(page_data.get("text", ""))
        
        debug_print("analyze_page", f"HTML: {html_size} chars, Text: {text_size} chars")
        breakpoint()
        return {
            **state,
            "messages": state.get("messages", []) + [f"Analysis complete: {html_size} HTML, {text_size} text chars"]
        }
        
    except Exception as e:
        debug_print("analyze_page", f"Analysis failed: {e}")
        return {
            **state,
            "error_message": f"Analysis failed: {e}",
            "messages": state.get("messages", []) + [f"Analysis error: {e}"]
        }

# Initialize state saver
init_state_saver("mtg_workflow", "workflow_states")

# Build graph
builder = StateGraph(State)
builder.add_node("launch_browser", launch_browser_node)
builder.add_node("navigate_page", navigate_to_page_node)
builder.add_node("analyze_page", analyze_page_node)

builder.add_edge(START, "launch_browser")
builder.add_edge("launch_browser", "navigate_page")
builder.add_edge("navigate_page", "analyze_page")
builder.add_edge("analyze_page", END)

# Export for LangGraph
graph = builder.compile()