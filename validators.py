import base64
from PIL import Image
import io
from typing import Tuple, Optional

def validate_image(image_data: bytes) -> Tuple[bool, str]:
    """Validate image data is a proper image file"""
    try:
        # Try to open the image data with PIL
        image = Image.open(io.BytesIO(image_data))
        image.verify()
        return True, ""
    except Exception as e:
        return False, str(e)

def validate_base64_image(base64_string: str) -> Tuple[bool, Optional[bytes]]:
    """Validate and decode base64 image data"""
    try:
        # Remove data URL prefix if present
        if "base64," in base64_string:
            base64_string = base64_string.split("base64,")[1]
        
        # Decode base64
        image_data = base64.b64decode(base64_string)
        
        # Validate the decoded data is an image
        valid, error = validate_image(image_data)
        if not valid:
            return False, None
        
        return True, image_data
    except Exception as e:
        return False, None

def prepare_image_for_3d_conversion(image_path: str) -> Optional[str]:
    """
    Prepare image for 3D conversion by ensuring it's in the right format
    Returns base64-encoded image data
    """
    try:
        # Open the image
        with Image.open(image_path) as img:
            # Convert to RGB if needed
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            # Resize if too large
            max_size = 1024
            if max(img.width, img.height) > max_size:
                if img.width > img.height:
                    new_width = max_size
                    new_height = int(img.height * (max_size / img.width))
                else:
                    new_height = max_size
                    new_width = int(img.width * (max_size / img.height))
                
                img = img.resize((new_width, new_height), Image.LANCZOS)
            
            # Save to buffer and convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=95)
            buffer.seek(0)
            
            return base64.b64encode(buffer.read()).decode()
    except Exception as e:
        print(f"Error preparing image: {e}")
        return None
