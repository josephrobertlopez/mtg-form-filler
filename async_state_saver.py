"""
Simple Async State Saver for LangGraph
Automatically saves state after each node execution without blocking the event loop.
"""

import json
import os
import asyncio
import aiofiles
import functools
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Dict, Optional, TypeVar, Union, Callable
import uuid

StateType = TypeVar('StateType')
NodeFunction = Callable[[StateType], StateType]

class SimpleStateSaver:
    """Simple async state saver with thread safety."""
    
    def __init__(self, workflow_name: str = "workflow", base_dir: str = "states"):
        self.workflow_name = workflow_name
        self.base_dir = base_dir
        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + str(uuid.uuid4())[:8]
        self.counter = 0
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="StateSaver")
        
        # Create directories
        os.makedirs(base_dir, exist_ok=True)
        self.run_dir = os.path.join(base_dir, f"{workflow_name}_{self.run_id}")
        os.makedirs(self.run_dir, exist_ok=True)
        
        print(f"[StateSaver] Saving states to: {self.run_dir}")
    
    def save_sync(self, state: Dict[str, Any], node_name: str) -> str:
        """Save state synchronously (runs in thread)."""
        with self._lock:
            self.counter += 1
            timestamp = datetime.now().strftime("%H%M%S")
            filename = f"{self.counter:03d}_{node_name}_{timestamp}.json"
            filepath = os.path.join(self.run_dir, filename)
            
            try:
                # Make state JSON serializable
                clean_state = self._clean_for_json(state)
                
                data = {
                    "metadata": {
                        "node": node_name,
                        "order": self.counter,
                        "time": datetime.now().isoformat(),
                        "workflow": self.workflow_name,
                        "run_id": self.run_id
                    },
                    "state": clean_state
                }
                
                # Write synchronously (will run in background thread)
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
                
                print(f"[StateSaver] Saved: {filename}")
                return filepath
                
            except Exception as e:
                print(f"[StateSaver] Error saving {node_name}: {e}")
                return ""
    
    def save_background(self, state: Dict[str, Any], node_name: str):
        """Save state in background thread."""
        self._executor.submit(self.save_sync, state, node_name)
    
    def _clean_for_json(self, obj: Any) -> Any:
        """Make object JSON serializable."""
        if obj is None or isinstance(obj, (str, int, float, bool)):
            return obj
        elif isinstance(obj, (list, tuple)):
            return [self._clean_for_json(item) for item in obj]
        elif isinstance(obj, dict):
            return {str(k): self._clean_for_json(v) for k, v in obj.items()}
        else:
            return str(obj)  # Convert non-serializable to string

# Global saver instance
_saver: Optional[SimpleStateSaver] = None

def init_state_saver(workflow_name: str = "workflow", base_dir: str = "states"):
    """Initialize the global state saver."""
    global _saver
    _saver = SimpleStateSaver(workflow_name, base_dir)
    return _saver

def save_state(node_name: str = None):
    """Decorator to auto-save state after node execution."""
    def decorator(func: NodeFunction) -> NodeFunction:
        @functools.wraps(func)
        def wrapper(state: StateType) -> StateType:
            actual_node_name = node_name or func.__name__
            
            try:
                # Run the original node
                result = func(state)
                
                # Save state in background thread (non-blocking)
                if _saver:
                    _saver.save_background(result, actual_node_name)
                
                return result
                
            except Exception as e:
                # Save error state
                if _saver:
                    error_state = dict(state) if isinstance(state, dict) else {"original_state": state}
                    error_state["_error"] = str(e)
                    _saver.save_background(error_state, f"{actual_node_name}_ERROR")
                raise
        
        return wrapper
    
    return decorator