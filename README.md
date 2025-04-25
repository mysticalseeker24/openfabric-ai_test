# Openfabric AI Developer Challenge

This project implements an end-to-end creative AI pipeline using Openfabric SDK, DeepSeek LLM, and advanced memory systems. It transforms user prompts into enhanced descriptions, generates images, and converts those images into 3D models while maintaining both short-term and long-term memory of all creations.

## Features

- **Local LLM Integration**: Utilizes DeepSeek LLM (via Ollama) for prompt enhancement and context understanding
- **Text-to-Image Generation**: Connects to Openfabric's Text-to-Image app to create images from enhanced prompts
- **Image-to-3D Conversion**: Transforms generated images into 3D models using Openfabric's Image-to-3D app
- **Multi-level Memory System**:
  - Short-term memory for session context
  - Long-term SQLite database for persistent storage
  - Advanced vector-based memory with ChromaDB for similarity search (optional)
- **User-friendly GUI**: Streamlit interface for easy interaction and creation browsing
- **Optimized File Management**: Unique filenames and automatic cleanup of older files
- **Input Validation**: Robust validation for all data transfers between system components

## Setup

1. Clone the repository: `git clone https://github.com/yourusername/openfabric-ai-assessment.git`
2. Navigate to the project directory: `cd openfabric-ai-assessment`
3. Create and activate a virtual environment: 
   ```
   python -m venv venv
   venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On Linux/Mac
   ```
4. Install dependencies using the custom installation script:
   ```
   python install_dependencies.py
   ```
   This script handles various dependency conflicts that can occur, especially on Windows.
   
   Alternatively, you can use pip: `pip install -r requirements.txt`
5. Install Ollama from https://ollama.com/download and run it
6. Pull DeepSeek LLM: `ollama pull deepseek-r1:14b`
7. Check if all dependencies were successfully installed:
   ```
   python main.py --check
   ```

## Usage

### Command Line Interface

```bash
# Basic usage with default prompt
python main.py

# Custom prompt
python main.py --prompt "A mystical forest with glowing mushrooms"

# Reference a past creation
python main.py --prompt "A new castle design" --reference "recent"
python main.py --prompt "A new castle design" --reference "2025-04-24"

# Start the Streamlit GUI
python main.py --gui
```

### Streamlit GUI

For a more user-friendly experience, you can use the Streamlit interface:

```bash
streamlit run app.py
```

This will launch a web interface where you can:
- Enter prompts and generate new creations
- Browse past creations
- Reference similar creations using vector similarity search
- Download generated 3D models

## System Architecture

- **main.py**: Core pipeline implementation with all integration points
- **memory.py**: Memory systems for context and persistence
- **advanced_memory.py**: Vector-based similarity search using ChromaDB
- **file_manager.py**: Optimized file storage with automatic cleanup
- **validators.py**: Input validation utilities for image processing
- **app.py**: Streamlit GUI for user interaction
- **core/**: Custom implementations of Openfabric SDK components
  - stub.py: Client for communicating with Openfabric apps
  - remote.py: Proxy connection handler
  - helper.py: Utility functions for schema handling
  - loader.py: Schema instantiation tools
- **ontology/**: Data structure definitions

## Testing

A basic test suite is included to verify core functionality:

```bash
python -m unittest tests/test_pipeline.py
```

## Troubleshooting

### Known Issues and Solutions

1. **Gevent Installation Issues on Windows**
   - **Problem**: When installing openfabric-pysdk, gevent fails to compile with Cython errors about missing `long` type in Python 3
   - **Solution**: We've created a custom installation script (`install_dependencies.py`) that bypasses the problematic compilation by installing openfabric-pysdk without dependencies, then manually installing the required dependencies individually.
   - **Alternative**: Modify the METADATA file in the openfabric-pysdk package to remove the upper version constraint for gevent.

2. **Pydantic Version Conflicts**
   - **Problem**: Ollama requires pydantic v2+ (for `pydantic.json_schema`), while openfabric-pysdk requires pydantic v1 (< 2.0.0)
   - **Solution**: Use pydantic v2 and modify any code that depends on pydantic v1 specific APIs. We've made our code compatible with both versions.

3. **Missing ChromaDB or LLM Dependencies**
   - **Problem**: These optional dependencies may fail to install on some systems
   - **Solution**: The pipeline is designed to degrade gracefully, falling back to simpler memory systems or basic prompt handling when advanced features aren't available.

4. **Dependency Check**
   - We've implemented a comprehensive dependency checker (`dependency_check.py`) that runs diagnostically to identify which components are available and what features will work. Run it with `python main.py --check`.

If you encounter issues not listed here, check the logs in the `logs/` directory for more information.

## Requirements

- Python 3.8+
- Windows, Linux, or macOS
- Ollama with DeepSeek LLM model
- Internet connection for Openfabric API access

## Troubleshooting

- If Openfabric SDK connections fail, check your internet connection and Openfabric app IDs
- If Ollama integration fails, ensure the DeepSeek model is properly installed with `ollama list`
- For GUI issues, verify Streamlit is correctly installed with `streamlit hello`

## Contributions

This project was developed as part of the Openfabric AI Developer Challenge. Contributions and improvements are welcome.
