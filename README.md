# Openfabric AI Developer Challenge
This project implements a creative pipeline using Openfabric SDK and DeepSeek LLM (deepseek-r1:8b) for text-to-image and image-to-3D generation with memory functionality.

## Setup
1. Clone the repository: `git clone https://github.com/mysticalseeker24/openfabric-ai_test.git`
2. Navigate to the project directory: `cd openfabric-ai-assessment`
3. Create and activate a virtual environment: `python -m venv venv` and `venv\Scripts\activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Install Ollama from https://ollama.com/download and run it
6. Pull DeepSeek LLM: `ollama pull deepseek-r1:14b`

## Usage
1. Activate the virtual environment: `venv\Scripts\activate`
2. Run the application: `python main.py`
3. Input a prompt like "A futuristic robot with LED lights" or reference past creations like "A new robot like the one I created last Thursday but with wings"
4. Check the `outputs` directory for generated images and 3D models
5. View past creations in memory.db using SQLite tools or `LongTermMemory.get_all_creations()`

## Testing
1. Tested on Windows with Python 3.8+
2. Verified DeepSeek LLM responses using ollama chat
3. Tested pipeline with prompts: "A futuristic robot", "A dragon like last week's but blue"
4. Confirmed memory storage and retrieval using memory.py test cases
