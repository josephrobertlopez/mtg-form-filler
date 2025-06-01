"""
Simple State Reader
Read and view saved workflow states.
"""

import json
import os
import glob
from datetime import datetime
from typing import Optional, List, Dict, Any

def list_state_files(base_dir: str = "workflow_states") -> List[str]:
    """List all saved state files."""
    if not os.path.exists(base_dir):
        return []
    
    pattern = os.path.join(base_dir, "**", "*.json")
    return sorted(glob.glob(pattern, recursive=True))

def load_state(filepath: str) -> Optional[Dict[str, Any]]:
    """Load a state file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def get_latest_state(workflow_name: str = "mtg_workflow") -> Optional[Dict[str, Any]]:
    """Get the most recent state file."""
    files = list_state_files()
    
    # Filter by workflow name
    workflow_files = [f for f in files if workflow_name in f]
    
    if not workflow_files:
        return None
    
    # Get the most recent file
    latest_file = max(workflow_files, key=os.path.getmtime)
    return load_state(latest_file)

def get_latest_page_content(workflow_name: str = "mtg_workflow") -> Optional[Dict[str, Any]]:
    """Get the latest captured page content."""
    files = list_state_files()
    
    # Look for navigate_page or analyze_page states
    content_files = [f for f in files if workflow_name in f and ("navigate_page" in f or "analyze_page" in f)]
    
    if not content_files:
        return None
    
    # Get the most recent file with content
    latest_file = max(content_files, key=os.path.getmtime)
    state_data = load_state(latest_file)
    
    if state_data and state_data.get("state", {}).get("page_content"):
        return state_data["state"]["page_content"]
    
    return None

def print_state_summary(base_dir: str = "workflow_states"):
    """Print a summary of all saved states."""
    files = list_state_files(base_dir)
    
    if not files:
        print("No state files found")
        return
    
    print(f"Found {len(files)} state files:")
    print()
    
    # Group by workflow run
    runs = {}
    for filepath in files:
        try:
            state_data = load_state(filepath)
            if state_data:
                metadata = state_data.get("metadata", {})
                run_id = metadata.get("run_id", "unknown")
                
                if run_id not in runs:
                    runs[run_id] = []
                
                runs[run_id].append({
                    "file": os.path.basename(filepath),
                    "node": metadata.get("node", "unknown"),
                    "order": metadata.get("order", 0),
                    "time": metadata.get("time", "unknown"),
                    "has_error": "_error" in state_data.get("state", {})
                })
        except:
            continue
    
    # Print runs
    for run_id, states in runs.items():
        print(f"Run: {run_id}")
        states.sort(key=lambda x: x["order"])
        
        for state in states:
            status = "❌" if state["has_error"] else "✅"
            print(f"  {status} {state['order']:02d}. {state['node']} - {state['file']}")
        
        print()

def show_latest_content():
    """Show the latest captured page content."""
    content = get_latest_page_content()
    
    if not content:
        print("No page content found")
        return
    
    print("Latest Captured Content:")
    print(f"  URL: {content.get('url', 'N/A')}")
    print(f"  Title: {content.get('title', 'N/A')}")
    print(f"  HTML: {len(content.get('html', ''))} characters")
    print(f"  Text: {len(content.get('text', ''))} characters")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "summary":
            print_state_summary()
        elif command == "content":
            show_latest_content()
        elif command == "latest":
            latest = get_latest_state()
            if latest:
                print("Latest state:")
                metadata = latest.get("metadata", {})
                print(f"  Node: {metadata.get('node')}")
                print(f"  Time: {metadata.get('time')}")
                print(f"  Messages: {len(latest.get('state', {}).get('messages', []))}")
            else:
                print("No states found")
        else:
            print(f"Unknown command: {command}")
    else:
        print("State Reader Commands:")
        print("  summary - Show all workflow runs")
        print("  content - Show latest page content")
        print("  latest  - Show latest state")
        
        choice = input("Enter command: ").strip()
        if choice == "summary":
            print_state_summary()
        elif choice == "content":
            show_latest_content()
        elif choice == "latest":
            latest = get_latest_state()
            if latest:
                print(json.dumps(latest, indent=2))
            else:
                print("No states found")