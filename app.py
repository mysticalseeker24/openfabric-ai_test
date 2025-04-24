import streamlit as st
import base64
from pathlib import Path
import os
from datetime import datetime
import time

# Import our application components
from main import Pipeline
from memory import LongTermMemory
from advanced_memory import AdvancedMemory

# Setup page configuration
st.set_page_config(
    page_title="Openfabric AI Creative Pipeline",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Function to load and display images
def load_image(image_path):
    if not os.path.exists(image_path):
        return None
    
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except Exception as e:
        st.error(f"Error loading image: {e}")
        return None

# Main application function
def main():
    # Title and description
    st.title("🎨 Openfabric AI Creative Pipeline")
    st.markdown(
        """
        This application uses DeepSeek LLM, Openfabric's Text-to-Image and Image-to-3D services 
        to create a complete AI creative pipeline. Enter a prompt below to generate art and 3D models.
        """
    )
    
    # Initialize components
    ltm = LongTermMemory()
    try:
        adv_mem = AdvancedMemory()
        use_advanced = True
    except Exception as e:
        st.warning(f"Advanced memory system not available: {e}. Using standard memory.")
        use_advanced = False
    
    pipeline = Pipeline()
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Create New", "View Past Creations", "About"])
    
    # Tab 1: Create New
    with tab1:
        st.subheader("Generate New Creation")
        
        with st.form("creation_form"):
            # Input form
            prompt = st.text_area("Enter your creative prompt:", 
                                 help="Describe what you want to create. Be as detailed as possible.")
            
            reference_options = st.radio(
                "Use past creations as reference?",
                options=["No reference", "Most recent", "Specific date", "Similar creation"]
            )
            
            reference_date = None
            reference_id = None
            
            if reference_options == "Specific date":
                reference_date = st.date_input("Select date", value=datetime.now())
            elif reference_options == "Similar creation" and use_advanced:
                # Only show this option if advanced memory is available
                if prompt:
                    try:
                        similar_creations = adv_mem.find_similar_creations(prompt)
                        if similar_creations:
                            reference_id = st.selectbox(
                                "Select similar creation",
                                options=[(c["id"], c["metadata"]["original_prompt"][:40] + "...") for c in similar_creations],
                                format_func=lambda x: x[1]
                            )
                            reference_id = reference_id[0] if reference_id else None
                        else:
                            st.info("No similar creations found yet. Enter a prompt first.")
                    except Exception as e:
                        st.error(f"Error finding similar creations: {e}")
            
            submitted = st.form_submit_button("Generate")
            
            if submitted and prompt:
                # Set up the reference parameter based on selection
                reference = None
                if reference_options == "Most recent":
                    reference = "recent"
                elif reference_options == "Specific date" and reference_date:
                    reference = reference_date.strftime("%Y-%m-%d")
                elif reference_options == "Similar creation" and reference_id:
                    # For the similar creation, we'll use the ID directly
                    reference = reference_id
                
                with st.spinner("Working on your creation..."):
                    try:
                        # Execute the pipeline
                        result = pipeline.execute(prompt, reference)
                        
                        if "error" in result:
                            st.error(result["error"])
                        else:
                            st.success("Creation successful!")
                            
                            # Display results
                            st.subheader("Results")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.text("Original Prompt")
                                st.write(result["original_prompt"])
                                
                                st.text("Enhanced Prompt")
                                st.write(result["enhanced_prompt"])
                            
                            with col2:
                                st.text("Generated Image")
                                try:
                                    st.image(result["image_path"])
                                except Exception as e:
                                    st.error(f"Error displaying image: {e}")
                                    st.write(f"Image path: {result['image_path']}")
                                
                                st.text("3D Model")
                                if Path(result["model_path"]).exists():
                                    st.write(f"3D Model saved at: {result['model_path']}")
                                    if st.button("Download 3D Model"):
                                        with open(result["model_path"], "rb") as f:
                                            model_data = f.read()
                                            st.download_button(
                                                label="Download Model",
                                                data=model_data,
                                                file_name=os.path.basename(result["model_path"]),
                                                mime="model/gltf-binary"
                                            )
                    except Exception as e:
                        st.error(f"Error in pipeline execution: {str(e)}")
    
    # Tab 2: View Past Creations
    with tab2:
        st.subheader("Your Past Creations")
        
        # Get all creations from memory
        creations = ltm.get_all_creations()
        
        if not creations:
            st.info("No creations found yet. Create something new first!")
        else:
            # Create a selection for past creations
            selected_idx = st.selectbox(
                "Select a creation to view",
                options=range(len(creations)),
                format_func=lambda i: f"{creations[i][1][:40]}... ({creations[i][3]})" 
            )
            
            if selected_idx is not None:
                creation = creations[selected_idx]
                
                # Display the selected creation
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Prompt Information")
                    st.text("Original Prompt")
                    st.write(creation[1])
                    st.text("Enhanced Prompt")
                    st.write(creation[2])
                    st.text("Creation Date")
                    st.write(creation[3])
                
                with col2:
                    st.markdown("### Generated Media")
                    st.text("Generated Image")
                    try:
                        st.image(creation[4])
                    except Exception as e:
                        st.error(f"Error displaying image: {e}")
                        st.write(f"Image path: {creation[4]}")
                    
                    st.text("3D Model")
                    if Path(creation[5]).exists():
                        st.write(f"3D Model saved at: {creation[5]}")
                        if st.button("Download 3D Model"):
                            with open(creation[5], "rb") as f:
                                model_data = f.read()
                                st.download_button(
                                    label="Download Model",
                                    data=model_data,
                                    file_name=os.path.basename(creation[5]),
                                    mime="model/gltf-binary"
                                )
    
    # Tab 3: About
    with tab3:
        st.markdown("### About This Application")
        st.write("""
        ## Openfabric AI Developer Challenge
        
        This application demonstrates an end-to-end AI creative pipeline built for the Openfabric AI Developer Challenge.
        
        ### Features:
        
        1. **Local LLM Integration**: Uses DeepSeek LLM via Ollama for prompt enhancement
        2. **Text-to-Image Generation**: Uses Openfabric's Text-to-Image app to create images from prompts
        3. **Image-to-3D Conversion**: Transforms generated images into 3D models
        4. **Memory Systems**: 
           - Short-term memory for session context
           - Long-term SQLite memory for persistent storage
           - Advanced vector memory with ChromaDB for similarity search
        5. **File Optimization**: Efficient file storage with automatic cleanup
        
        ### Technology Stack:
        
        - Python 3.8+
        - Streamlit for the user interface
        - Ollama/DeepSeek for LLM capabilities
        - Openfabric SDK for AI services
        - SQLite and ChromaDB for memory systems
        - Pillow for image processing
        """)

# Run the application
if __name__ == "__main__":
    main()
