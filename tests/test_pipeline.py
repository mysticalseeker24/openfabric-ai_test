import unittest
import os
import sys
import tempfile
from datetime import datetime, timedelta

# Add the parent directory to path so we can import our modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from memory import ShortTermMemory, LongTermMemory

class TestPipeline(unittest.TestCase):
    def setUp(self):
        self.stm = ShortTermMemory()
        # Use a temporary file for the test database
        self.test_db = "test_memory.db"
        self.ltm = LongTermMemory(self.test_db)
        self.output_dir = "outputs"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create test files in outputs directory
        test_image_path = os.path.join(self.output_dir, "test_image.png")
        test_model_path = os.path.join(self.output_dir, "test_model.obj")
        with open(test_image_path, "wb") as f:
            f.write(b"test image data")
        with open(test_model_path, "wb") as f:
            f.write(b"test model data")

    def tearDown(self):
        self.stm.clear_context()
        try:
            self.ltm.conn.execute("DROP TABLE IF EXISTS creations")
            self.ltm.conn.commit()
            self.ltm.conn.close()
            if os.path.exists(self.test_db):
                os.remove(self.test_db)
        except Exception as e:
            print(f"Error cleaning up database: {e}")

    def test_short_term_memory(self):
        self.stm.add_context("test_key", "test_value")
        self.assertEqual(self.stm.get_context("test_key"), "test_value")
        self.stm.clear_context()
        self.assertIsNone(self.stm.get_context("test_key"))

    def test_long_term_memory(self):
        # Save a test creation
        self.ltm.save_creation("test_prompt", "enhanced_prompt", 
                              "outputs/test.png", "outputs/test.obj")
        
        # Test retrieval of all creations
        creations = self.ltm.get_all_creations()
        self.assertEqual(len(creations), 1)
        self.assertEqual(creations[0][2], "test_prompt")
        
        # No need to test date-based retrieval here since it depends on the LLM
        # which would require actual API calls to DeepSeek

    def test_ollama_availability(self):
        # This test verifies that the Ollama module is available
        # and properly installed (without actually making API calls)
        import ollama
        # Just importing the module is sufficient to confirm it's available
        # If import fails, the test will fail with an ImportError

    def test_pipeline_structure(self):
        # This test verifies that our main application has the appropriate structure
        # without needing to import the Pipeline class (which depends on Openfabric SDK)
        import os
        import sys
        
        # Check that main.py exists
        self.assertTrue(os.path.exists("main.py"), "main.py should exist")
        
        # Check that it contains the appropriate functions
        with open("main.py", "r") as f:
            content = f.read()
            self.assertIn("def execute_pipeline", content, "main.py should contain execute_pipeline function")
            self.assertIn("class Pipeline", content, "main.py should contain Pipeline class")
            self.assertIn("def enhance_prompt", content, "main.py should contain enhance_prompt method")
            self.assertIn("def execute", content, "main.py should contain execute method")

if __name__ == "__main__":
    unittest.main()
