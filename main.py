import ollama
import os
import re
import logging
import base64
from datetime import datetime
import uuid
import json
from pathlib import Path
from typing import Dict, Optional, List, Any, Union

# Import our memory systems
from memory import ShortTermMemory, LongTermMemory
from advanced_memory import AdvancedMemory

# Import utility components
from file_manager import FileManager
from validators import validate_base64_image, prepare_image_for_3d_conversion

# Import Openfabric SDK components
from core.stub import Stub

class Pipeline:
    """Main AI pipeline for the Openfabric Developer Challenge"""
    
    def __init__(self):
        """Initialize the AI pipeline with necessary components"""
        # Initialize memory systems
        self.stm = ShortTermMemory()
        self.ltm = LongTermMemory()
        
        # Initialize advanced memory if available
        try:
            self.advanced_mem = AdvancedMemory()
            self.use_advanced_memory = True
        except Exception as e:
            logging.warning(f"Advanced memory unavailable: {e}. Using standard memory only.")
            self.use_advanced_memory = False
        
        # Initialize file manager for optimized storage
        self.file_manager = FileManager()
        
        # LLM configuration
        self.model = "deepseek-r1:14b"
        
        # Check if Ollama is available
        try:
            import ollama
            self.ollama_available = True
        except ImportError:
            logging.error("Ollama not available. Pipeline will function with limited capabilities.")
            self.ollama_available = False
        
        # Openfabric app IDs from the assessment instructions
        self.text_to_image_app_id = "f0997a01-d6d3-a5fe-53d8-561300318557"
        self.image_to_3d_app_id = "69543f29-4d41-4afc-7f29-3d51591f11eb"
        
        # Initialize the Stub with app IDs
        try:
            self.stub = Stub([self.text_to_image_app_id, self.image_to_3d_app_id])
            logging.info("Stub successfully initialized with app IDs")
        except Exception as e:
            logging.error(f"Error initializing Stub: {e}")
            raise
        
        logging.info("Pipeline initialized with Openfabric apps and DeepSeek LLM")

    def enhance_prompt(self, user_prompt: str, reference_date: str = "") -> str:
        """
        Enhance the user prompt using Ollama/DeepSeek LLM
        
        Args:
            user_prompt (str): Original user prompt
            reference_date (str): Optional date or ID for referencing previous creations
            
        Returns:
            str: Enhanced prompt with additional details
        """
        if not self.ollama_available:
            logging.warning("Ollama not available. Using original prompt.")
            return user_prompt
        
        # Check if we need to reference past creations
        reference_text = ""
        
        if reference_date:
            try:
                # Check if it's a simple date string
                if reference_date.lower() == "recent":
                    # Get most recent creation
                    creations = self.ltm.get_all_creations()
                    if creations:
                        creation = creations[0]  # Most recent first
                        reference_text = f"""
Reference: Previously I created '{creation[1]}' which was enhanced to '{creation[2]}'. """
                elif self.use_advanced_memory and len(reference_date) > 30:  # Looks like a UUID
                    # Try to get by ID from advanced memory
                    creation = self.advanced_mem.get_creation_by_id(reference_date)
                    if creation:
                        reference_text = f"""
Reference: Previously I created '{creation['metadata']['original_prompt']}' which was enhanced to '{creation['metadata']['enhanced_prompt']}'. """
                else:
                    # Try as a date string
                    creations = self.ltm.get_creation_by_date(reference_date)
                    if creations:
                        creation = creations[0]  # Take the first one
                        reference_text = f"""
Reference: Previously I created '{creation[1]}' which was enhanced to '{creation[2]}'. """
            except Exception as e:
                logging.error(f"Error fetching reference creation: {e}")
        
        # Prepare system prompt
        system_prompt = """
        You are a creative AI assistant. Enhance the user's prompt to create a more detailed
        and visually descriptive version for image generation. Include details about style, 
        lighting, mood, and composition. Keep the enhanced prompt under 200 words.
        """
        
        # Add reference if available
        full_prompt = user_prompt + reference_text
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_prompt}
                ]
            )
            
            enhanced_prompt = response['message']['content'].strip()
            logging.info(f"Enhanced prompt: {enhanced_prompt}")
            return enhanced_prompt
        except Exception as e:
            logging.error(f"Error enhancing prompt with Ollama: {e}")
            return user_prompt  # Fallback to original prompt

    def parse_reference(self, user_prompt: str) -> Optional[str]:
        """Parse user prompt for references to past creations using DeepSeek."""
        instruction = (
            "Extract any date references (e.g., 'last Thursday', 'yesterday') or descriptions from the following prompt: "
            f"{user_prompt}. Return the date reference or description if found, otherwise return None."
        )
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": instruction}]
            )
            ref = response["message"]["content"]
            print(f"Reference extracted: {ref}")
            
            if ref.lower() != "none":
                creations = self.ltm.get_creation_by_date(ref)
                if creations:
                    original_prompt = creations[0][2]  # original_prompt from DB
                    # Modify the original prompt with new details
                    date_pattern = r"(last \w+|yesterday|today|\d+\s*(days|weeks|months)\s*ago)"
                    new_details = re.sub(date_pattern, "", user_prompt, flags=re.IGNORECASE).strip()
                    return f"{original_prompt}, {new_details}"
            return None
        except Exception as e:
            print(f"Error parsing reference with {self.model}: {e}")
            return None

    def execute(self, user_prompt: str, reference_date: str = "") -> Dict[str, Any]:
        """
        Execute the full AI pipeline
        
        Args:
            user_prompt (str): Original user prompt
            reference_date (str): Optional date reference for previous creations
            
        Returns:
            Dictionary with results or error message
        """
        try:
            # Track which steps are completed successfully
            steps_completed = {
                "enhance": False,
                "image": False,
                "model": False,
                "memory": False
            }
            
            # Step 1: Enhance the prompt using DeepSeek LLM or fallback
            logging.info(f"Enhancing prompt: '{user_prompt}'")
            enhanced_prompt = self.enhance_prompt(user_prompt, reference_date)
            self.stm.add_context("enhanced_prompt", enhanced_prompt)
            steps_completed["enhance"] = True
            
            # Check if Openfabric SDK is available
            if self.stub is None:
                logging.error("Openfabric SDK not available. Cannot generate image or 3D model.")
                return {
                    "error": "Openfabric SDK not available. Pipeline requires SDK connection.",
                    "original_prompt": user_prompt,
                    "enhanced_prompt": enhanced_prompt
                }
            
            # Step 2: Generate image using Text-to-Image app
            logging.info(f"Calling Text-to-Image app with prompt: {enhanced_prompt}")
            try:
                image_response = self.stub.call(
                    self.text_to_image_app_id, 
                    {"prompt": enhanced_prompt}, 
                    "super-user"
                )
                
                if not image_response or "image" not in image_response:
                    logging.error("Failed to generate image")
                    return {"error": "Failed to generate image from the prompt"}
                
                # Process the image response (typically base64 encoded)
                img_base64 = image_response["image"]
                valid, img_data = validate_base64_image(img_base64)
                
                if not valid or not img_data:
                    logging.error("Invalid image data received")
                    return {
                        "error": "Invalid image data received",
                        "original_prompt": user_prompt,
                        "enhanced_prompt": enhanced_prompt
                    }
                
                # Save the image using our file manager
                image_path = self.file_manager.save_image(img_data)
                self.stm.add_context("image_path", image_path)
                logging.info(f"Image saved to: {image_path}")
                steps_completed["image"] = True
                
            except Exception as e:
                logging.error(f"Error calling Text-to-Image app: {e}")
                return {"error": f"Failed to generate image: {str(e)}"}
            
            # Step 3: Convert image to 3D model using Image-to-3D app
            logging.info("Converting image to 3D model using Image-to-3D app")
            try:
                # Prepare image for 3D conversion
                prepared_img_base64 = prepare_image_for_3d_conversion(image_path)
                if not prepared_img_base64:
                    logging.error("Failed to prepare image for 3D conversion")
                    return {
                        "error": "Failed to prepare image for 3D conversion",
                        "original_prompt": user_prompt,
                        "enhanced_prompt": enhanced_prompt,
                        "image_path": image_path
                    }
                
                # Call the Image-to-3D app with the image
                model_response = self.stub.call(
                    self.image_to_3d_app_id,
                    {"image": prepared_img_base64},
                    "super-user"
                )
                
                if not model_response or "model" not in model_response:
                    logging.error("Failed to generate 3D model")
                    return {
                        "error": "Failed to generate 3D model from the image",
                        "original_prompt": user_prompt,
                        "enhanced_prompt": enhanced_prompt,
                        "image_path": image_path
                    }
                
                # Process the 3D model response (typically base64 encoded)
                model_base64 = model_response["model"]
                model_data = base64.b64decode(model_base64)
                
                # Save the 3D model using our file manager
                model_path = self.file_manager.save_model(model_data)
                self.stm.add_context("model_path", model_path)
                logging.info(f"3D model saved to: {model_path}")
                steps_completed["model"] = True
            
            except Exception as e:
                logging.error(f"Error calling Image-to-3D app: {e}")
                # Return partial results if we at least have an image
                if steps_completed["image"]:
                    return {
                        "error": f"Failed to generate 3D model: {str(e)}",
                        "original_prompt": user_prompt,
                        "enhanced_prompt": enhanced_prompt,
                        "image_path": image_path,
                        "partial_completion": True
                    }
                else:
                    return {"error": f"Failed to generate 3D model: {str(e)}"}
            # Step 4: Save creation to memory systems
            try:
                # Save to long-term memory
                self.ltm.save_creation(user_prompt, enhanced_prompt, image_path, model_path)
                steps_completed["memory"] = True
                
                # Save to advanced memory if available
                if self.use_advanced_memory:
                    try:
                        self.advanced_mem.save_creation(user_prompt, enhanced_prompt, image_path, model_path)
                        logging.info("Creation saved to advanced memory system")
                    except Exception as adv_err:
                        logging.warning(f"Error saving to advanced memory: {adv_err}")
                    
                logging.info("Creation saved to memory systems")
            except Exception as e:
                logging.error(f"Error saving to memory: {e}")
                # Continue even if memory saving fails - we still have the files
            
            # Return the results
            success = all([steps_completed["enhance"], steps_completed["image"], steps_completed["model"]])
            
            return {
                "original_prompt": user_prompt,
                "enhanced_prompt": enhanced_prompt,
                "image_path": image_path,
                "model_path": model_path,
                "success": success,
                "steps_completed": steps_completed
            }

        except Exception as e:
            logging.error(f"Pipeline execution error: {str(e)}")
            return {"error": f"Pipeline execution failed: {str(e)}", "steps_completed": steps_completed}

def execute_pipeline(user_prompt: str, reference_date: str = "") -> Dict[str, Any]:
    """
    Wrapper function to execute the pipeline
    
    Args:
        user_prompt (str): User's original prompt
        reference_date (str): Optional date reference
        
    Returns:
        Dict[str, Any]: Dictionary with results or error message
    """
    # Set up logging if not already configured
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("logs/pipeline.log"),
                logging.StreamHandler()
            ]
        )
    
    # Ensure output directories exist
    os.makedirs("outputs/images", exist_ok=True)
    os.makedirs("outputs/models", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Initialize and execute the pipeline
    pipeline = Pipeline()
    return pipeline.execute(user_prompt, reference_date)


if __name__ == "__main__":
    import argparse
    import sys
    
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Openfabric AI Developer Challenge")
    parser.add_argument("--gui", action="store_true", help="Launch the Streamlit GUI")
    parser.add_argument("--prompt", type=str, default="A majestic underwater city with bioluminescent buildings", help="Prompt for pipeline execution")
    parser.add_argument("--reference", type=str, default="", help="Reference date, 'recent', or ID for past creation")
    parser.add_argument("--check", action="store_true", help="Run dependency check only")
    
    args = parser.parse_args()
    
    # Ensure directories exist
    os.makedirs("outputs/images", exist_ok=True)
    os.makedirs("outputs/models", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/pipeline.log"),
            logging.StreamHandler()
        ]
    )
    
    # Run dependency check if requested
    if args.check:
        print("""
========== CHECKING DEPENDENCIES ==========""")
        from dependency_check import DependencyChecker
        checker = DependencyChecker()
        results = checker.check_all(verbose=True)
        print("""
=========================================""")
        sys.exit(0)
    
    if args.gui:
        # Check if Streamlit is available
        try:
            import streamlit
            print("""
========== LAUNCHING STREAMLIT GUI ==========""")
            import subprocess
            subprocess.run(["streamlit", "run", "app.py"])
        except ImportError:
            print("Streamlit is not installed. Please install it with: pip install streamlit")
            print("Then run the GUI with: streamlit run app.py")
        except Exception as e:
            print(f"Error launching Streamlit: {e}")
    else:
        # Run the pipeline with the given prompt
        test_prompt = args.prompt
        reference = args.reference
        
        print(f"Running pipeline with prompt: '{test_prompt}'...")
        if reference:
            print(f"Using reference: '{reference}'...")
            
        result = execute_pipeline(test_prompt, reference)
        
        print("""
======== PIPELINE RESULTS ========""")
        if "error" in result:
            print(f"Error: {result['error']}")
            # Show partial results if available
            if "original_prompt" in result:
                print(f"Original prompt: {result['original_prompt']}")
            if "enhanced_prompt" in result:
                print(f"Enhanced prompt: {result['enhanced_prompt']}")
            if "image_path" in result:
                print(f"Generated image: {result['image_path']}")
            if "partial_completion" in result and result['partial_completion']:
                print("""
Note: The pipeline completed partially. Some steps succeeded.""")
        else:
            print(f"Original prompt: {result['original_prompt']}")
            print(f"Enhanced prompt: {result['enhanced_prompt']}")
            print(f"Generated image: {result['image_path']}")
            print(f"Generated 3D model: {result['model_path']}")
            
            # Show which steps were completed successfully
            if "steps_completed" in result:
                print("\nSteps completed:")
                for step, completed in result["steps_completed"].items():
                    print(f"  - {step}: {'✓' if completed else '✗'}")
        print("==================================")
