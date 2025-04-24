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
4. Install dependencies: `pip install -r requirements.txt`
5. Install Ollama from https://ollama.com/download and run it
6. Pull DeepSeek LLM: `ollama pull deepseek-r1:14b`

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

1. Basic pipeline test: `python main.py`
2. GUI test: `streamlit run app.py`
3. Unit tests: `python -m unittest tests/test_pipeline.py`

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
