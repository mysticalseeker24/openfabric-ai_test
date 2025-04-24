import os
import uuid
import time
from pathlib import Path
from typing import Tuple, List
import base64
import shutil

class FileManager:
    def __init__(self, base_dir: str = "outputs", max_files: int = 100):
        """Initialize file manager with base directory and limits"""
        self.base_dir = Path(base_dir)
        self.image_dir = self.base_dir / "images"
        self.model_dir = self.base_dir / "models"
        self.max_files = max_files
        
        # Create directories if they don't exist
        self.image_dir.mkdir(parents=True, exist_ok=True)
        self.model_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_unique_filename(self, extension: str) -> str:
        """Generate a unique filename using UUID"""
        return f"{uuid.uuid4()}.{extension.lstrip('.')}"
    
    def save_image(self, image_data: bytes) -> str:
        """Save image data to file system with unique name"""
        filename = self.generate_unique_filename("jpg")
        file_path = self.image_dir / filename
        
        with open(file_path, "wb") as f:
            f.write(image_data)
        
        # Check if cleanup is needed
        self._cleanup_if_needed(self.image_dir)
        
        return str(file_path)
    
    def save_model(self, model_data: bytes) -> str:
        """Save 3D model data to file system with unique name"""
        filename = self.generate_unique_filename("glb")  # Using glTF binary format
        file_path = self.model_dir / filename
        
        with open(file_path, "wb") as f:
            f.write(model_data)
        
        # Check if cleanup is needed
        self._cleanup_if_needed(self.model_dir)
        
        return str(file_path)
    
    def _cleanup_if_needed(self, directory: Path) -> None:
        """Clean up oldest files if directory exceeds max file count"""
        files = list(directory.glob("*"))
        
        if len(files) > self.max_files:
            # Sort files by modification time (oldest first)
            files.sort(key=lambda x: x.stat().st_mtime)
            
            # Remove oldest files until we're under the limit
            for file in files[:len(files) - self.max_files]:
                try:
                    file.unlink()
                except Exception as e:
                    print(f"Error removing file {file}: {e}")
    
    def get_file_info(self, file_path: str) -> dict:
        """Get file information including size and creation time"""
        path = Path(file_path)
        
        if not path.exists():
            return {"exists": False}
        
        stat = path.stat()
        return {
            "exists": True,
            "size_bytes": stat.st_size,
            "created": time.ctime(stat.st_ctime),
            "modified": time.ctime(stat.st_mtime)
        }
