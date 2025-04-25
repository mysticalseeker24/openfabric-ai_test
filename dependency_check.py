import importlib.util
import sys
import logging
from typing import Dict, List, Tuple, Optional

class DependencyChecker:
    """Utility class to check for required dependencies"""
    
    def __init__(self):
        self.results = {}
        self.logger = logging.getLogger("dependency_checker")
    
    def check_module(self, module_name: str, package_desc: str = "") -> bool:
        """Check if a Python module is available"""
        try:
            spec = importlib.util.find_spec(module_name)
            is_available = spec is not None
            if is_available:
                try:
                    module = importlib.import_module(module_name)
                    version = getattr(module, "__version__", "unknown")
                    self.results[module_name] = {
                        "available": True,
                        "version": version,
                        "description": package_desc
                    }
                except ImportError:
                    self.results[module_name] = {
                        "available": True,
                        "version": "unknown",
                        "description": package_desc,
                        "note": "Module found but couldn't import"
                    }
            else:
                self.results[module_name] = {
                    "available": False,
                    "description": package_desc
                }
            return is_available
        except Exception as e:
            self.results[module_name] = {
                "available": False,
                "description": package_desc,
                "error": str(e)
            }
            return False
    
    def check_all(self, verbose: bool = False) -> Dict[str, Dict]:
        """Check all required and optional dependencies"""
        # Core requirements
        core_deps = [
            ("openfabric_pysdk", "Openfabric Python SDK"),
            ("requests", "HTTP library"),
            ("marshmallow", "Object serialization"),
            ("PIL", "Python Imaging Library"),
            ("pydantic", "Data validation"),
            ("dateutil", "Date utilities")
        ]
        
        # Optional dependencies
        optional_deps = [
            ("ollama", "Local LLM integration"),
            ("streamlit", "GUI frontend"),
            ("chromadb", "Vector database for advanced memory")
        ]
        
        # Check core dependencies
        if verbose:
            print("\nChecking core dependencies...")
        
        for module_name, desc in core_deps:
            available = self.check_module(module_name, desc)
            if verbose:
                status = "✓" if available else "✗"
                print(f"  {status} {module_name}: {desc}")
        
        # Check optional dependencies
        if verbose:
            print("\nChecking optional dependencies...")
        
        for module_name, desc in optional_deps:
            available = self.check_module(module_name, desc)
            if verbose:
                status = "✓" if available else "✗"
                print(f"  {status} {module_name}: {desc}")
        
        # Print summary
        if verbose:
            print("\nFeatures availability:")
            llm_available = self.results.get("ollama", {}).get("available", False)
            print(f"  - LLM Enhancement: {'Available' if llm_available else 'Limited'}")
            
            advanced_memory = self.can_run_advanced_memory()
            print(f"  - Advanced Memory: {'Available' if advanced_memory else 'Basic Only'}")
            
            gui_available = self.results.get("streamlit", {}).get("available", False)
            print(f"  - GUI Interface: {'Available' if gui_available else 'CLI Only'}")
        
        return self.results
    
    def can_run_advanced_memory(self) -> bool:
        """Check if advanced memory system can run"""
        # We need chromadb for the advanced memory system
        return self.check_module("chromadb", "Vector database for advanced memory")


if __name__ == "__main__":
    # Run directly for testing
    checker = DependencyChecker()
    checker.check_all(verbose=True)
