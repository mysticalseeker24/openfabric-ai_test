import ollama
import os
import re
import logging
import base64
from datetime import datetime
from typing import Dict, Optional, List, Any, Union

# Import our memory system
from memory import ShortTermMemory, LongTermMemory

# Import Openfabric SDK components
from core.stub import Stub

class Pipeline:
    def __init__(self):
        # Initialize memory systems
        self.stm = ShortTermMemory()
        self.ltm = LongTermMemory()
        
        # LLM configuration
        self.model = "deepseek-r1:14b"  # Using the model we downloaded
        
        # Setup output directory for images and 3D models
        self.output_dir = "outputs"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Openfabric app IDs from the assessment instructions
        self.text_to_image_app_id = "f0997a01-d6d3-a5fe-53d8-561300318557"
        self.image_to_3d_app_id = "69543f29-4d41-4afc-7f29-3d51591f11eb"
        
        # Initialize the Openfabric Stub with the app IDs
        self.stub = Stub([self.text_to_image_app_id, self.image_to_3d_app_id])
        logging.info("Pipeline initialized with Openfabric apps and DeepSeek LLM")

    def enhance_prompt(self, user_prompt: str) -> str:
        """Enhance user prompt using DeepSeek LLM."""
        instruction = (
            "You are a creative assistant. Enhance the following prompt to be more detailed and vivid for generating a high-quality image, keeping the core idea intact: "
            f"{user_prompt}. Return only the enhanced prompt."
        )
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": instruction}]
            )
            enhanced_prompt = response["message"]["content"]
            print(f"Enhanced prompt: {enhanced_prompt}")
            return enhanced_prompt
        except Exception as e:
            print(f"Error with {self.model}: {e}")
            return user_prompt  # Fall back to original prompt

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

    def execute(self, user_prompt: str) -> Dict[str, str]:
        """
        Execute the full pipeline: enhance prompt, generate image, create 3D model.
        
        Args:
            user_prompt (str): The user's original prompt text
            
        Returns:
            Dict[str, str]: Dictionary containing pipeline results
        """
        try:
            logging.info(f"Processing prompt: '{user_prompt}'")
            
            # Step 1: Check for references to past creations
            referenced_prompt = self.parse_reference(user_prompt)
            if referenced_prompt:
                logging.info(f"Found reference to past creation, using: '{referenced_prompt}'")
                user_prompt = referenced_prompt
                
            # Step 2: Enhance the prompt with DeepSeek LLM
            enhanced_prompt = self.enhance_prompt(user_prompt)
            logging.info(f"Enhanced prompt: {enhanced_prompt}")
            
            # Step 3: Store in short-term memory
            self.stm.add_context("user_prompt", user_prompt)
            self.stm.add_context("enhanced_prompt", enhanced_prompt)

            # Generate timestamp for file naming
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")

            # Step 4: Generate image using Text-to-Image app
            logging.info("Calling Text-to-Image app with Openfabric SDK")
            image_path = os.path.join(self.output_dir, f"image_{timestamp}.png")
            try:
                # Call the Text-to-Image app with the enhanced prompt
                # Note: In the real implementation, the app_id would be mapped to the actual Openfabric service URL
                image_response = self.stub.call(
                    self.text_to_image_app_id, 
                    {"prompt": enhanced_prompt}, 
                    "super-user"  # User ID
                )
                
                # Extract the binary image data from the response
                # The structure follows the Openfabric SDK's response format
                image_data = image_response.get("result")
                if not image_data:
                    raise Exception("No image data received from Text-to-Image app")
                    
                # Save the binary image data to a file
                with open(image_path, "wb") as f:
                    f.write(image_data)
                logging.info(f"Image generated and saved to: {image_path}")
                
            except Exception as e:
                logging.error(f"Error calling Text-to-Image app: {e}")
                return {"error": f"Failed to generate image: {str(e)}"}

            # Step 5: Generate 3D model using Image-to-3D app
            logging.info("Calling Image-to-3D app with Openfabric SDK")
            model_path = os.path.join(self.output_dir, f"model_{timestamp}.obj")
            try:
                # For the Image-to-3D app, we need to read the image file and encode it properly
                with open(image_path, "rb") as img_file:
                    img_data = img_file.read()
                    # Some APIs might require base64 encoding for binary data
                    img_base64 = base64.b64encode(img_data).decode('utf-8')
                
                # Call the Image-to-3D app with the image data
                model_response = self.stub.call(
                    self.image_to_3d_app_id,
                    {"image": img_base64},  # Pass the encoded image data
                    "super-user"  # User ID
                )
                
                # Extract the model data from the response
                model_data = model_response.get("result")
                if not model_data:
                    raise Exception("No model data received from Image-to-3D app")
                    
                # Save the 3D model data to a file
                with open(model_path, "wb") as f:
                    # If the model data is returned as base64 encoded string, we'd need to decode it
                    if isinstance(model_data, str):
                        f.write(base64.b64decode(model_data))
                    else:
                        f.write(model_data)  # Assume binary data
                        
                logging.info(f"3D model generated and saved to: {model_path}")
                
            except Exception as e:
                logging.error(f"Error calling Image-to-3D app: {e}")
                return {
                    "original_prompt": user_prompt,
                    "enhanced_prompt": enhanced_prompt,
                    "image_path": image_path,
                    "error": f"Failed to generate 3D model: {str(e)}"
                }

            # Step 6: Save to long-term memory for future reference
            self.ltm.save_creation(user_prompt, enhanced_prompt, image_path, model_path)
            logging.info("Creation saved to long-term memory")

            # Return the complete pipeline results
            return {
                "original_prompt": user_prompt,
                "enhanced_prompt": enhanced_prompt,
                "image_path": image_path,
                "model_path": model_path
            }

        except Exception as e:
            logging.error(f"Pipeline error: {e}")
            return {"error": str(e)}


def execute_pipeline(user_prompt: str) -> Dict[str, str]:
    """
    Wrapper function to execute the pipeline.
    
    Args:
        user_prompt (str): The user's prompt text
        
    Returns:
        Dict[str, str]: Result of the pipeline execution
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize and execute the pipeline
    pipeline = Pipeline()
    return pipeline.execute(user_prompt)


if __name__ == "__main__":
    # Test the pipeline with a sample prompt
    print("\n========== OPENFABRIC AI DEVELOPER CHALLENGE ==========")
    print("Testing the creative pipeline with DeepSeek LLM...")
    test_prompt = "A futuristic robot with LED lights"
    print(f"User prompt: '{test_prompt}'
")
    
    # Execute the pipeline
    result = execute_pipeline(test_prompt)
    
    # Display the results
    print("
======== PIPELINE RESULTS ========")
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Original prompt: {result['original_prompt']}")
        print(f"Enhanced prompt: {result['enhanced_prompt']}")
        print(f"Generated image: {result['image_path']}")
        print(f"Generated 3D model: {result['model_path']}")
    print("===================================")
