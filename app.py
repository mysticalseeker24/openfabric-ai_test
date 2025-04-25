import streamlit as st
import base64
from pathlib import Path
import os
import time
import random
from datetime import datetime
from PIL import Image, ImageOps
import io

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

# Custom CSS for Midjourney-like styling
st.markdown("""
<style>
    /* Global styling */
    .stApp {
        background-color: #0c0e16;
        color: #e0e0e0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1d2d;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3b4179;
    }
    /* Form styling */
    .stTextArea textarea, .stTextInput input, .stSelectbox, .stMultiselect {
        background-color: #1a1d2d;
        color: #ffffff;
        border: 1px solid #3b4179;
        border-radius: 8px;
    }
    /* Button styling */
    .stButton>button {
        background-color: #5865f2;
        color: white;
        border: none;
        padding: 8px 20px;
        font-weight: 500;
        border-radius: 6px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #4752c4;
        box-shadow: 0 0 15px rgba(88, 101, 242, 0.5);
    }
    /* Card layout for creations */
    .creation-card {
        background-color: #1a1d2d;
        border-radius: 10px;
        padding: 10px;
        border: 1px solid #2c2f3e;
        margin-bottom: 20px;
    }
    /* Image styling */
    .stImage img {
        border-radius: 8px;
    }
    /* Heading styles */
    h1, h2, h3 {
        color: #ffffff;
    }
    /* Custom title with glow effect */
    .title-container {
        display: flex;
        justify-content: center;
        margin-bottom: 2rem;
    }
    .glow-text {
        color: #ffffff;
        text-shadow: 0 0 10px #5865f2, 0 0 20px #5865f2, 0 0 30px #5865f2;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# Enhanced image handling functions
def load_image(image_path):
    """Load image from path and return base64 encoding"""
    if not os.path.exists(image_path):
        return None
    
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except Exception as e:
        st.error(f"Error loading image: {e}")
        return None

def process_image_for_display(image_path):
    """Process image to add a subtle border and enhance for display"""
    try:
        img = Image.open(image_path)
        # Add a subtle border (Midjourney style)
        img_with_border = ImageOps.expand(img, border=4, fill='#3b4179')
        return img_with_border
    except Exception as e:
        st.error(f"Error processing image: {e}")
        return None
        
def display_image_with_download(image_path, caption=""):
    """Display image with download button in Midjourney style"""
    try:
        img = process_image_for_display(image_path)
        if img:
            st.image(img, caption=caption, use_column_width=True)
            
            # Add download button for the image
            with open(image_path, "rb") as file:
                btn = st.download_button(
                    label="⬇️ Download Image",
                    data=file,
                    file_name=os.path.basename(image_path),
                    mime="image/png"
                )
        else:
            st.warning(f"Cannot display image at {image_path}")
    except Exception as e:
        st.error(f"Error displaying image: {e}")

def create_model_card(model_path):
    """Create a download card for 3D model in Midjourney style"""
    if not os.path.exists(model_path):
        return st.warning("3D model file not found")
        
    st.markdown("""
    <div style='background-color: #1a1d2d; padding: 15px; border-radius: 10px; margin-top: 10px; border: 1px solid #3b4179;'>
        <h4 style='color: #ffffff; margin-top: 0;'>3D Model</h4>
        <p style='color: #a0a0a0;'>Your 3D model is ready for download</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Add download button
    with open(model_path, "rb") as f:
        model_data = f.read()
        st.download_button(
            label="⬇️ Download 3D Model",
            data=model_data,
            file_name=os.path.basename(model_path),
            mime="model/gltf-binary"
        )

# Main application function
def main():
    # Custom stylish title with glow effect
    st.markdown(
        """
        <div class="title-container">
            <h1 class="glow-text">🎨 CreatiFabric AI Studio</h1>
        </div>
        """, unsafe_allow_html=True
    )
    
    # Modern description with highlight
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 30px;">
            <p style="font-size: 18px; color: #e0e0e0;">
                Transform your imagination into digital art and 3D models with our<br/>
                <span style="color: #5865f2; font-weight: bold;">end-to-end AI creative pipeline</span>
            </p>
        </div>
        """, unsafe_allow_html=True
    )
    
    # Add feature highlights in a grid
    with st.container():
        cols = st.columns(4)
        
        with cols[0]:
            st.markdown("""
            <div style="background-color: #1a1d2d; padding: 15px; border-radius: 10px; height: 100px; text-align: center;">
                <h3 style="font-size: 18px;">💡 Smart Prompts</h3>
                <p style="color: #a0a0a0; font-size: 14px;">DeepSeek LLM Enhancement</p>
            </div>
            """, unsafe_allow_html=True)
            
        with cols[1]:
            st.markdown("""
            <div style="background-color: #1a1d2d; padding: 15px; border-radius: 10px; height: 100px; text-align: center;">
                <h3 style="font-size: 18px;">🎨 Image Generation</h3>
                <p style="color: #a0a0a0; font-size: 14px;">Openfabric Text-to-Image</p>
            </div>
            """, unsafe_allow_html=True)
            
        with cols[2]:
            st.markdown("""
            <div style="background-color: #1a1d2d; padding: 15px; border-radius: 10px; height: 100px; text-align: center;">
                <h3 style="font-size: 18px;">🗑️ 3D Models</h3>
                <p style="color: #a0a0a0; font-size: 14px;">Image-to-3D Conversion</p>
            </div>
            """, unsafe_allow_html=True)
            
        with cols[3]:
            st.markdown("""
            <div style="background-color: #1a1d2d; padding: 15px; border-radius: 10px; height: 100px; text-align: center;">
                <h3 style="font-size: 18px;">📂 Memory System</h3>
                <p style="color: #a0a0a0; font-size: 14px;">Store & Find Similar Ideas</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Add some spacing
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # Initialize components
    ltm = LongTermMemory()
    try:
        adv_mem = AdvancedMemory()
        use_advanced = True
    except Exception as e:
        st.warning(f"Advanced memory system not available: {e}. Using standard memory.")
        use_advanced = False
    
    pipeline = Pipeline()
    
    # Create tabs for different sections with custom styling
    tab1, tab2, tab3 = st.tabs(["✨ Create", "🖼️ Gallery", "ℹ️ About"])
    
    # Tab 1: Create New
    with tab1:
        # Create a modern card-like container for the creation form
        st.markdown("""
        <div style="background-color: #1a1d2d; padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 1px solid #3b4179;">
            <h2 style="color: #5865f2; margin-top: 0;">Create Your Masterpiece</h2>
            <p style="color: #a0a0a0;">Enter a detailed prompt to generate unique art and 3D models</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("creation_form", clear_on_submit=False):
            # Midjourney-style prompt input with examples
            prompt_placeholder = random.choice([
                "A cyberpunk city with neon lights and flying cars...",
                "An enchanted forest with magical creatures and glowing plants...",
                "A futuristic space station orbiting a distant planet...",
                "An underwater civilization with bioluminescent architecture..."
            ])
            
            prompt = st.text_area(
                "💬 Your Creative Prompt", 
                placeholder=prompt_placeholder,
                height=100,
                help="Be detailed and descriptive for best results. Include style, mood, lighting, and composition details."
            )
            
            # Add style guides like in Midjourney
            st.markdown("<p style='color:#a0a0a0; font-size:14px;'>Enhance your prompt with style options:</p>", unsafe_allow_html=True)
            
            style_cols = st.columns(4)
            with style_cols[0]:
                artistic_style = st.selectbox("Artistic Style", [
                    "None", "Photorealistic", "Digital Art", "Oil Painting", "Watercolor", "Sketch", "3D Render", "Anime"
                ])
            
            with style_cols[1]:
                lighting = st.selectbox("Lighting", [
                    "None", "Soft", "Dramatic", "Cinematic", "Neon", "Backlit", "Golden Hour"
                ])
            
            with style_cols[2]:
                mood = st.selectbox("Mood", [
                    "None", "Peaceful", "Mysterious", "Energetic", "Melancholic", "Ethereal", "Dystopian"
                ])
            
            with style_cols[3]:
                detail_level = st.selectbox("Detail Level", [
                    "Standard", "Highly Detailed", "Minimalist", "Abstract"
                ])
            
            # Add separator
            st.markdown("<hr style='border-color: #3b4179; margin: 15px 0;'/>", unsafe_allow_html=True)
            
            # Reference options with better UI
            st.markdown("<p style='color:#a0a0a0; font-size:14px;'>Reference past creations to influence the new one:</p>", unsafe_allow_html=True)
            
            reference_options = st.radio(
                "",  # Empty label for cleaner UI
                options=["No reference", "Most recent creation", "Creation by date", "Similar creation"],
                horizontal=True
            )
            
            reference_date = None
            reference_id = None
            
            # Show appropriate reference selector based on choice
            ref_container = st.container()
            with ref_container:
                if reference_options == "Creation by date":
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.markdown("<p style='color:#5865f2; padding-top: 5px;'>Select date:</p>", unsafe_allow_html=True)
                    with col2:
                        reference_date = st.date_input("", value=datetime.now())
                elif reference_options == "Similar creation" and use_advanced:
                    # Only show this option if advanced memory is available and prompt is entered
                    if prompt:
                        try:
                            similar_creations = adv_mem.find_similar_creations(prompt)
                            if similar_creations:
                                reference_id = st.selectbox(
                                    "Select a similar creation to reference",
                                    options=[(c["id"], c["metadata"]["original_prompt"][:50] + "...") for c in similar_creations],
                                    format_func=lambda x: x[1]
                                )
                                reference_id = reference_id[0] if reference_id else None
                            else:
                                st.info("Enter a prompt to find similar creations")
                        except Exception as e:
                            st.error(f"Error finding similar creations: {e}")
                    else:
                        st.info("Enter a prompt above to see similar creations")
            
            # Submit button with eye-catching style
            submitted = st.form_submit_button("🚀 Generate Creation")
            
            # Process form submission
            if submitted and prompt:
                # Enhance prompt with style selections if specified
                full_prompt = prompt
                style_elements = []
                
                if artistic_style != "None":
                    style_elements.append(artistic_style)
                if lighting != "None":
                    style_elements.append(f"{lighting} lighting")
                if mood != "None":
                    style_elements.append(f"{mood} mood")
                if detail_level != "Standard":
                    style_elements.append(detail_level)
                
                if style_elements:
                    full_prompt = f"{prompt}, {', '.join(style_elements)}"
                
                # Set up the reference parameter based on selection
                reference = None
                if reference_options == "Most recent creation":
                    reference = "recent"
                elif reference_options == "Creation by date" and reference_date:
                    reference = reference_date.strftime("%Y-%m-%d")
                elif reference_options == "Similar creation" and reference_id:
                    # For the similar creation, we'll use the ID directly
                    reference = reference_id
                
                # Create a progress container
                progress_container = st.empty()
                with progress_container.container():
                    # Display an animated loading message
                    st.markdown("""
                    <div style="background-color: #1a1d2d; padding: 20px; border-radius: 12px; text-align: center;">
                        <h3 style="color: #5865f2;">Creating Your Masterpiece</h3>
                        <p style="color: #a0a0a0;">This might take a minute. We're enhancing your prompt, generating art, and building a 3D model...</p>
                        <div style="display: flex; justify-content: center; margin-top: 20px;">
                            <div class="stSpinner"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    try:
                        # Execute the pipeline with the enhanced prompt
                        result = pipeline.execute(full_prompt, reference)
                        
                        # Clear the progress container once done
                        progress_container.empty()
                        
                        if "error" in result:
                            st.error(result["error"])
                            # Show partial results if available
                            if "partial_completion" in result and result["partial_completion"]:
                                st.warning("We encountered an issue during processing, but we still have some results for you.")
                        else:
                            # Create a success notification
                            st.success("✅ Creation successful!")
                            
                        # Display results in a beautiful card layout (regardless of error if we have partial results)
                        if "original_prompt" in result:
                            st.markdown("""
                            <div style="background-color: #1a1d2d; padding: 20px; border-radius: 12px; margin: 20px 0; border: 1px solid #3b4179;">
                                <h2 style="color: #ffffff; text-align: center;">Your Creation</h2>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Split the display into columns
                            col1, col2 = st.columns([1, 1])
                            
                            with col1:
                                # Prompt information
                                st.markdown("""
                                <div style="background-color: #1a1d2d; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                                    <h4 style="color: #5865f2; margin-top: 0;">Original Prompt</h4>
                                </div>
                                """, unsafe_allow_html=True)
                                st.write(result["original_prompt"])
                                
                                st.markdown("""
                                <div style="background-color: #1a1d2d; padding: 15px; border-radius: 10px; margin-top: 20px;">
                                    <h4 style="color: #5865f2; margin-top: 0;">Enhanced by DeepSeek LLM</h4>
                                </div>
                                """, unsafe_allow_html=True)
                                st.write(result["enhanced_prompt"])
                            
                            with col2:
                                # Display image with our custom function for better styling
                                if "image_path" in result and os.path.exists(result["image_path"]):
                                    st.markdown("""
                                    <div style="background-color: #1a1d2d; padding: 15px; border-radius: 10px; margin-bottom: 10px;">
                                        <h4 style="color: #5865f2; margin-top: 0;">Generated Image</h4>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    display_image_with_download(result["image_path"])
                                
                                # Display 3D model download if available
                                if "model_path" in result and Path(result["model_path"]).exists():
                                    create_model_card(result["model_path"])
                    except Exception as e:
                        progress_container.empty()  # Clear the progress indicator
                        st.error(f"Error in pipeline execution: {str(e)}")
    
    # Tab 2: Gallery of Past Creations
    with tab2:
        # Create a stylish gallery header
        st.markdown("""
        <div style="background-color: #1a1d2d; padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 1px solid #3b4179;">
            <h2 style="color: #5865f2; margin-top: 0;">Your Creation Gallery</h2>
            <p style="color: #a0a0a0;">Browse and interact with your past creations</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Get all creations from memory
        creations = ltm.get_all_creations()
        
        if not creations:
            # Empty gallery state
            st.markdown("""
            <div style="background-color: #1a1d2d; padding: 40px; border-radius: 12px; text-align: center; margin-top: 50px;">
                <h3 style="color: #ffffff;">Your Gallery is Empty</h3>
                <p style="color: #a0a0a0;">Head over to the Create tab to make your first masterpiece!</p>
                <div style="font-size: 48px; margin: 20px;">✨</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Add filter and sort options
            filter_col1, filter_col2 = st.columns([1, 2])
            
            with filter_col1:
                view_mode = st.radio("View Mode", ["Grid View", "Detailed View"], horizontal=True)
                
            with filter_col2:
                sort_by = st.selectbox("Sort By", ["Newest First", "Oldest First", "Alphabetical"])
                
            # Sort creations based on user selection
            if sort_by == "Oldest First":
                creations = creations[::-1]  # Reverse the order (original is newest first)
            elif sort_by == "Alphabetical":
                creations = sorted(creations, key=lambda x: x[1].lower())
                
            # Grid View Mode - Midjourney style gallery
            if view_mode == "Grid View":
                st.markdown("<hr style='border-color: #3b4179; margin: 15px 0;'/>", unsafe_allow_html=True)
                
                # Create a grid of image thumbnails - 3 per row
                for i in range(0, len(creations), 3):
                    cols = st.columns(3)
                    for j in range(3):
                        if i+j < len(creations):
                            creation = creations[i+j]
                            with cols[j]:
                                # Image card with prompt as caption
                                try:
                                    if os.path.exists(creation[4]):
                                        img = process_image_for_display(creation[4])
                                        if img:
                                            # Click to select functionality
                                            st.image(img, caption=creation[1][:40] + "...")
                                            if st.button(f"View Details {i+j+1}", key=f"grid_{i+j}"):
                                                st.session_state['selected_creation'] = i+j
                                except Exception as e:
                                    st.error(f"Error displaying thumbnail: {e}")
                
                # If a creation is selected from grid, show detail view
                if 'selected_creation' in st.session_state:
                    st.markdown("""
                    <div style="background-color: #1a1d2d; padding: 15px; border-radius: 10px; margin-top: 20px; border: 1px solid #3b4179;">
                        <h3 style="color: #5865f2;">Creation Details</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    selected_creation = creations[st.session_state['selected_creation']]
                    detail_col1, detail_col2 = st.columns(2)
                    
                    with detail_col1:
                        st.markdown("""
                        <div style="background-color: #1a1d2d; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                            <h4 style="color: #5865f2; margin-top: 0;">Original Prompt</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        st.write(selected_creation[1])
                        
                        st.markdown("""
                        <div style="background-color: #1a1d2d; padding: 15px; border-radius: 10px; margin-top: 15px;">
                            <h4 style="color: #5865f2; margin-top: 0;">Enhanced Prompt</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        st.write(selected_creation[2])
                        
                        st.markdown(f"""
                        <div style="background-color: #1a1d2d; padding: 15px; border-radius: 10px; margin-top: 15px;">
                            <h4 style="color: #5865f2; margin-top: 0;">Created On</h4>
                            <p style="color: #e0e0e0;">{selected_creation[3]}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with detail_col2:
                        display_image_with_download(selected_creation[4])
                        
                        # Display 3D model download if available
                        if Path(selected_creation[5]).exists():
                            create_model_card(selected_creation[5])
            
            # Detailed View Mode - List with details
            else:
                # Create a selection for past creations
                selected_idx = st.selectbox(
                    "Select a creation to view",
                    options=range(len(creations)),
                    format_func=lambda i: f"{creations[i][1][:40]}... ({creations[i][3]})" 
                )
                
                if selected_idx is not None:
                    creation = creations[selected_idx]
                    
                    # Create a beautiful detailed view
                    st.markdown("""
                    <div style="background-color: #1a1d2d; padding: 20px; border-radius: 12px; margin: 20px 0; border: 1px solid #3b4179;">
                        <h2 style="color: #ffffff; text-align: center;">Creation Details</h2>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("""
                        <div style="background-color: #1a1d2d; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                            <h4 style="color: #5865f2; margin-top: 0;">Original Prompt</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        st.write(creation[1])
                        
                        st.markdown("""
                        <div style="background-color: #1a1d2d; padding: 15px; border-radius: 10px; margin-top: 15px;">
                            <h4 style="color: #5865f2; margin-top: 0;">Enhanced Prompt</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        st.write(creation[2])
                        
                        st.markdown(f"""
                        <div style="background-color: #1a1d2d; padding: 15px; border-radius: 10px; margin-top: 15px;">
                            <h4 style="color: #5865f2; margin-top: 0;">Created On</h4>
                            <p style="color: #e0e0e0;">{creation[3]}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("""
                        <div style="background-color: #1a1d2d; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                            <h4 style="color: #5865f2; margin-top: 0;">Generated Image</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        display_image_with_download(creation[4])
                        
                        # Display 3D model download if available
                        if Path(creation[5]).exists():
                            create_model_card(creation[5])
    
    # Tab 3: About
    with tab3:
        # Create a stylish about header
        st.markdown("""
        <div style="background-color: #1a1d2d; padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 1px solid #3b4179;">
            <h2 style="color: #5865f2; margin-top: 0;">About CreatiFabric AI Studio</h2>
            <p style="color: #a0a0a0;">End-to-end AI creative pipeline built for the Openfabric AI Developer Challenge</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create two columns for about content
        about_col1, about_col2 = st.columns([3, 2])
        
        with about_col1:
            # Pipeline flow diagram - visual representation
            st.markdown("""
            <div style="background-color: #1a1d2d; padding: 20px; border-radius: 12px; margin-bottom: 20px;">
                <h3 style="color: #ffffff; text-align: center;">AI Creative Pipeline Architecture</h3>
                
                <div style="display: flex; flex-direction: column; align-items: center; margin-top: 20px;">
                    <!-- Step 1 -->
                    <div style="background-color: #3b4179; padding: 15px; border-radius: 8px; width: 80%; margin-bottom: 10px; text-align: center;">
                        <h4 style="color: #ffffff; margin: 0;">1. User Prompt</h4>
                        <p style="color: #d0d0d0; margin: 5px 0 0 0;">Your creative input</p>
                    </div>
                    
                    <div style="color: #5865f2; margin: 5px 0; font-size: 20px;">↓</div>
                    
                    <!-- Step 2 -->
                    <div style="background-color: #3b4179; padding: 15px; border-radius: 8px; width: 80%; margin-bottom: 10px; text-align: center;">
                        <h4 style="color: #ffffff; margin: 0;">2. DeepSeek LLM</h4>
                        <p style="color: #d0d0d0; margin: 5px 0 0 0;">Enhances your prompts with creative details</p>
                    </div>
                    
                    <div style="color: #5865f2; margin: 5px 0; font-size: 20px;">↓</div>
                    
                    <!-- Step 3 -->
                    <div style="background-color: #3b4179; padding: 15px; border-radius: 8px; width: 80%; margin-bottom: 10px; text-align: center;">
                        <h4 style="color: #ffffff; margin: 0;">3. Openfabric Text-to-Image</h4>
                        <p style="color: #d0d0d0; margin: 5px 0 0 0;">Generates stunning artwork from the enhanced prompt</p>
                    </div>
                    
                    <div style="color: #5865f2; margin: 5px 0; font-size: 20px;">↓</div>
                    
                    <!-- Step 4 -->
                    <div style="background-color: #3b4179; padding: 15px; border-radius: 8px; width: 80%; margin-bottom: 10px; text-align: center;">
                        <h4 style="color: #ffffff; margin: 0;">4. Openfabric Image-to-3D</h4>
                        <p style="color: #d0d0d0; margin: 5px 0 0 0;">Transforms the image into a 3D model</p>
                    </div>
                    
                    <div style="color: #5865f2; margin: 5px 0; font-size: 20px;">↓</div>
                    
                    <!-- Step 5 -->
                    <div style="background-color: #3b4179; padding: 15px; border-radius: 8px; width: 80%; margin-bottom: 10px; text-align: center;">
                        <h4 style="color: #ffffff; margin: 0;">5. Multi-layer Memory System</h4>
                        <p style="color: #d0d0d0; margin: 5px 0 0 0;">Stores creations for future reference</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with about_col2:
            # Technology stack cards
            st.markdown("""
            <div style="background-color: #1a1d2d; padding: 20px; border-radius: 12px; margin-bottom: 20px;">
                <h3 style="color: #ffffff; text-align: center;">Technology Stack</h3>
                
                <div style="margin-top: 15px;">
                    <div style="background-color: #2c2f3e; padding: 10px; border-radius: 8px; margin-bottom: 8px;">
                        <p style="color: #5865f2; margin: 0; font-weight: 500;">AI & Machine Learning:</p>
                        <p style="color: #d0d0d0; margin: 5px 0 0 0;">• DeepSeek LLM via Ollama</p>
                        <p style="color: #d0d0d0; margin: 5px 0 0 0;">• Openfabric Text-to-Image</p>
                        <p style="color: #d0d0d0; margin: 5px 0 0 0;">• Openfabric Image-to-3D</p>
                    </div>
                    
                    <div style="background-color: #2c2f3e; padding: 10px; border-radius: 8px; margin-bottom: 8px;">
                        <p style="color: #5865f2; margin: 0; font-weight: 500;">Memory Systems:</p>
                        <p style="color: #d0d0d0; margin: 5px 0 0 0;">• Short-term Session Memory</p>
                        <p style="color: #d0d0d0; margin: 5px 0 0 0;">• SQLite Long-term Storage</p>
                        <p style="color: #d0d0d0; margin: 5px 0 0 0;">• ChromaDB Vector Database</p>
                    </div>
                    
                    <div style="background-color: #2c2f3e; padding: 10px; border-radius: 8px; margin-bottom: 8px;">
                        <p style="color: #5865f2; margin: 0; font-weight: 500;">Backend:</p>
                        <p style="color: #d0d0d0; margin: 5px 0 0 0;">• Python 3.8+</p>
                        <p style="color: #d0d0d0; margin: 5px 0 0 0;">• Openfabric SDK</p>
                        <p style="color: #d0d0d0; margin: 5px 0 0 0;">• Pillow for Image Processing</p>
                    </div>
                    
                    <div style="background-color: #2c2f3e; padding: 10px; border-radius: 8px;">
                        <p style="color: #5865f2; margin: 0; font-weight: 500;">Frontend:</p>
                        <p style="color: #d0d0d0; margin: 5px 0 0 0;">• Streamlit</p>
                        <p style="color: #d0d0d0; margin: 5px 0 0 0;">• HTML/CSS</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # App IDs reference
            st.markdown("""
            <div style="background-color: #1a1d2d; padding: 20px; border-radius: 12px;">
                <h3 style="color: #ffffff; text-align: center;">Openfabric App IDs</h3>
                
                <div style="margin-top: 15px;">
                    <div style="background-color: #2c2f3e; padding: 10px; border-radius: 8px; margin-bottom: 8px;">
                        <p style="color: #5865f2; margin: 0; font-weight: 500;">Text-to-Image:</p>
                        <p style="color: #d0d0d0; margin: 5px 0 0 0; font-family: monospace; word-break: break-all;">f0997a01-d6d3-a5fe-53d8-561300318557</p>
                    </div>
                    
                    <div style="background-color: #2c2f3e; padding: 10px; border-radius: 8px;">
                        <p style="color: #5865f2; margin: 0; font-weight: 500;">Image-to-3D:</p>
                        <p style="color: #d0d0d0; margin: 5px 0 0 0; font-family: monospace; word-break: break-all;">69543f29-4d41-4afc-7f29-3d51591f11eb</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# Run the application
if __name__ == "__main__":
    main()
