import os
import unittest
from pathlib import Path
from markitup import MarkItUp, Config


class TestMarkItUp(unittest.TestCase):
    def setUp(self):
        # Get the absolute path to the test_files directory
        self.test_files_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "test_files"
        )

    def test_plain_text_conversion(self):
        """Test converting a plain text file to markdown."""
        filepath = os.path.join(self.test_files_dir, "test.txt")
        
        with open(filepath, "rb") as f:
            markitup = MarkItUp()
            result, info = markitup.convert(f)
            
        self.assertIsNotNone(result)
        self.assertEqual(info.category, "text")
        self.assertTrue(result.markdown, "Content should not be empty")

    def test_docx_conversion(self):
        """Test converting a DOCX file to markdown."""
        filepath = os.path.join(self.test_files_dir, "test.docx")
        
        with open(filepath, "rb") as f:
            markitup = MarkItUp()
            result, info = markitup.convert(f)
            
        self.assertIsNotNone(result)
        self.assertEqual(info.category, "docx")
        self.assertTrue(result.markdown, "Content should not be empty")
        
    def test_docx_with_comments_conversion(self):
        """Test converting a DOCX file with comments to markdown."""
        filepath = os.path.join(self.test_files_dir, "test_with_comment.docx")
        
        with open(filepath, "rb") as f:
            markitup = MarkItUp()
            result, info = markitup.convert(f)
            
        self.assertIsNotNone(result)
        self.assertEqual(info.category, "docx")
        self.assertTrue(result.markdown, "Content should not be empty")
        
    def test_pdf_conversion(self):
        """Test converting a PDF file to markdown."""
        filepath = os.path.join(self.test_files_dir, "test.pdf")
        
        with open(filepath, "rb") as f:
            markitup = MarkItUp()
            result, info = markitup.convert(f)
            
        self.assertIsNotNone(result)
        self.assertEqual(info.category, "pdf")
        self.assertTrue(result.markdown, "Content should not be empty")

    def test_html_conversion(self):
        """Test converting HTML files to markdown."""
        html_files = ["test_blog.html", "test_wikipedia.html", "test_serp.html"]
        
        for html_file in html_files:
            filepath = os.path.join(self.test_files_dir, html_file)
            with self.subTest(file=html_file):
                with open(filepath, "rb") as f:
                    markitup = MarkItUp()
                    result, info = markitup.convert(f)
                    
                self.assertIsNotNone(result)
                self.assertEqual(info.category, "text")
                self.assertTrue(result.markdown, "Content should not be empty")

    def test_xlsx_conversion(self):
        """Test converting an XLSX file to markdown."""
        filepath = os.path.join(self.test_files_dir, "test.xlsx")
        
        with open(filepath, "rb") as f:
            markitup = MarkItUp()
            result, info = markitup.convert(f)
            
        self.assertIsNotNone(result)
        self.assertEqual(info.category, "xlsx")
        self.assertTrue(result.markdown, "Content should not be empty")
        
    def test_xls_conversion(self):
        """Test converting an XLS file to markdown."""
        filepath = os.path.join(self.test_files_dir, "test.xls")
        
        with open(filepath, "rb") as f:
            markitup = MarkItUp()
            result, info = markitup.convert(f)
            
        self.assertIsNotNone(result)
        self.assertEqual(info.category, "xls")
        self.assertTrue(result.markdown, "Content should not be empty")

    def test_csv_conversion(self):
        """Test converting CSV files to markdown."""
        csv_files = ["test.csv", "test_mskanji.csv"]
        
        for csv_file in csv_files:
            filepath = os.path.join(self.test_files_dir, csv_file)
            with self.subTest(file=csv_file):
                with open(filepath, "rb") as f:
                    markitup = MarkItUp()
                    result, info = markitup.convert(f)
                    
                self.assertIsNotNone(result)
                self.assertEqual(info.category, "csv")
                self.assertTrue(result.markdown, "Content should not be empty")
                
    def test_pptx_conversion(self):
        """Test converting a PPTX file to markdown."""
        filepath = os.path.join(self.test_files_dir, "test.pptx")
        
        with open(filepath, "rb") as f:
            markitup = MarkItUp()
            result, info = markitup.convert(f)
            
        self.assertIsNotNone(result)
        self.assertEqual(info.category, "pptx")
        self.assertTrue(result.markdown, "Content should not be empty")
        
    def test_audio_conversion(self):
        """Test converting audio files to markdown."""
        audio_files = ["test.mp3", "test.m4a"]
        
        for audio_file in audio_files:
            filepath = os.path.join(self.test_files_dir, audio_file)
            with self.subTest(file=audio_file):
                with open(filepath, "rb") as f:
                    markitup = MarkItUp()
                    result, info = markitup.convert(f)
                    
                self.assertIsNotNone(result)
                self.assertEqual(info.category, "audio")
                self.assertTrue(result.markdown, "Content should not be empty")

    def test_image_in_config(self):
        """Test with only image in modalities config."""
        filepath = os.path.join(self.test_files_dir, "test.pdf")
        
        with open(filepath, "rb") as f:
            # Configure with only image modality
            config = Config(modalities=["image"])
            markitup = MarkItUp(config=config)
            result, info = markitup.convert(f)
            
        self.assertIsNotNone(result)
        self.assertEqual(info.category, "pdf")
        # PDF might still include image references if there are images in the PDF
        
    def test_audio_in_config(self):
        """Test with only audio in modalities config."""
        filepath = os.path.join(self.test_files_dir, "test.docx")
        
        with open(filepath, "rb") as f:
            # Configure with only audio modality
            config = Config(modalities=["audio"])
            markitup = MarkItUp(config=config)
            result, info = markitup.convert(f)
            
        self.assertIsNotNone(result)
        self.assertEqual(info.category, "docx")
        # Should not have image tags in the result
        
    def test_no_modalities_config(self):
        """Test with empty modalities config."""
        filepath = os.path.join(self.test_files_dir, "test_with_comment.docx")
        
        with open(filepath, "rb") as f:
            # Configure with no modalities
            config = Config(modalities=[])
            markitup = MarkItUp(config=config)
            result, info = markitup.convert(f)
            
        self.assertIsNotNone(result)
        self.assertEqual(info.category, "docx")
        # Should have text without image or audio references
        
    def test_unsupported_format(self):
        """Test handling of an unsupported file format."""
        filepath = os.path.join(self.test_files_dir, "random.bin")
        
        with open(filepath, "rb") as f:
            markitup = MarkItUp()
            with self.assertRaises(Exception):
                # Should raise an exception for unsupported format
                markitup.convert(f)
                
    def test_multiple_files_same_config(self):
        """Test converting multiple files with the same configuration."""
        test_files = {
            "test.txt": "text",
            "test.docx": "docx",
            "test.pdf": "pdf",
            "test.xlsx": "xlsx"
        }
        
        # Create a single configuration to use for all conversions
        config = Config(modalities=["image", "audio"])
        markitup = MarkItUp(config=config)
        
        for filename, expected_category in test_files.items():
            filepath = os.path.join(self.test_files_dir, filename)
            with self.subTest(file=filename):
                with open(filepath, "rb") as f:
                    result, info = markitup.convert(f)
                    
                self.assertIsNotNone(result)
                self.assertEqual(info.category, expected_category)
                self.assertTrue(result.markdown, "Content should not be empty")
                
    def test_to_llm_method(self):
        """Test the to_llm method of the conversion result."""
        filepath = os.path.join(self.test_files_dir, "test.docx")
        
        with open(filepath, "rb") as f:
            markitup = MarkItUp()
            result, info = markitup.convert(f)
            
        # Call the to_llm method and check the result
        llm_format = result.to_llm()
        self.assertIsNotNone(llm_format)
        self.assertIsInstance(llm_format, list)
        
        # Check if there's at least one content element
        if llm_format:
            self.assertIn("type", llm_format[0])


if __name__ == "__main__":
    unittest.main()