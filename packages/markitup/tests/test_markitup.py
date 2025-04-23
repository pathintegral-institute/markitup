import os
import unittest
from pathlib import Path
from markitup import MarkItUp, Config
from markitup.converter_utils.utils import read_files_to_bytestreams

fs = read_files_to_bytestreams('packages/markitup/tests/test_files')


class TestMarkItUp(unittest.TestCase):
    def setUp(self):
        print("Setting up test environment")
        print(fs)

    def test_plain_text_conversion(self):
        """Test converting a plain text file to markdown."""
        markitup = MarkItUp()
        # fs['test.txt'].seek(0)
        result, info = markitup.convert(fs['test.txt'], 'test.txt')
        self.assertIsNotNone(result)
        self.assertEqual(info.category, "text")
        self.assertTrue(result.to_llm(), "Content should not be empty")

    def test_docx_conversion(self):
        """Test converting a DOCX file to markdown."""
        markitup = MarkItUp()
        result, info = markitup.convert(fs['test.docx'], 'test.docx')
            
        self.assertIsNotNone(result)
        self.assertEqual(info.category, "docx")
        self.assertTrue(result.to_llm(), "Content should not be empty")
        
    def test_docx_with_comments_conversion(self):
        """Test converting a DOCX file with comments to markdown."""
        markitup = MarkItUp()
        result, info = markitup.convert(fs['test_with_comment.docx'], 'test_with_comment.docx')
            
        self.assertIsNotNone(result)
        self.assertEqual(info.category, "docx")
        self.assertTrue(result.to_llm(), "Content should not be empty")
        
    def test_pdf_conversion(self):
        """Test converting a PDF file to markdown."""
        markitup = MarkItUp()
        result, info = markitup.convert(fs['test.pdf'], 'test.pdf')
            
        self.assertIsNotNone(result)
        self.assertEqual(info.category, "pdf")
        self.assertTrue(result.to_llm(), "Content should not be empty")

    def test_html_conversion(self):
        """Test converting HTML files to markdown."""
        html_files = ["test_blog.html", "test_wikipedia.html", "test_serp.html"]
        
        for html_file in html_files:
            with self.subTest(file=html_file):
                markitup = MarkItUp()
                result, info = markitup.convert(fs[html_file], html_file)
                    
                self.assertIsNotNone(result)
                self.assertEqual(info.category, "html")
                self.assertTrue(result.to_llm(), "Content should not be empty")

    def test_xlsx_conversion(self):
        """Test converting an XLSX file to markdown."""
        markitup = MarkItUp()
        result, info = markitup.convert(fs['test.xlsx'], 'test.xlsx')
            
        self.assertIsNotNone(result)
        self.assertEqual(info.category, "xlsx")
        self.assertTrue(result.to_llm(), "Content should not be empty")
        
    def test_xls_conversion(self):
        """Test converting an XLS file to markdown."""
        markitup = MarkItUp()
        result, info = markitup.convert(fs['test.xls'], 'test.xls')
            
        self.assertIsNotNone(result)
        self.assertEqual(info.category, "xls")
        self.assertTrue(result.to_llm(), "Content should not be empty")

    def test_csv_conversion(self):
        """Test converting CSV files to markdown."""
        csv_files = ["test.csv", "test_mskanji.csv"]
        
        for csv_file in csv_files:
            with self.subTest(file=csv_file):
                markitup = MarkItUp()
                result, info = markitup.convert(fs[csv_file], csv_file)
                    
                self.assertIsNotNone(result)
                self.assertEqual(info.category, "csv")
                self.assertTrue(result.to_llm(), "Content should not be empty")
                
    def test_pptx_conversion(self):
        """Test converting a PPTX file to markdown."""
        markitup = MarkItUp()
        result, info = markitup.convert(fs['test.pptx'], 'test.pptx')
            
        self.assertIsNotNone(result)
        self.assertEqual(info.category, "pptx")
        self.assertTrue(result.to_llm(), "Content should not be empty")
        
    def test_audio_conversion(self):
        """Test converting audio files to markdown."""
        audio_files = ["test.mp3"]
        
        for audio_file in audio_files:
            with self.subTest(file=audio_file):
                markitup = MarkItUp(config=Config(modalities=["audio"]))
                result, info = markitup.convert(fs[audio_file], audio_file)
                    
                self.assertIsNotNone(result)
                self.assertEqual(info.category, "audio")
                self.assertTrue(result.to_llm(), "Content should not be empty")

    def test_image_in_config(self):
        """Test with only image in modalities config."""
        # Configure with only image modality
        config = Config(modalities=["image"])
        markitup = MarkItUp(config=config)
        result, info = markitup.convert(fs['test.pdf'], 'test.pdf')
            
        self.assertIsNotNone(result)
        self.assertEqual(info.category, "pdf")
        # PDF might still include image references if there are images in the PDF
        
    def test_audio_in_config(self):
        """Test with only audio in modalities config."""
        # Configure with only audio modality
        config = Config(modalities=["audio"])
        markitup = MarkItUp(config=config)
        result, info = markitup.convert(fs['test.docx'], 'test.docx')
            
        self.assertIsNotNone(result)
        self.assertEqual(info.category, "docx")
        # Should not have image tags in the result
        
    def test_no_modalities_config(self):
        """Test with empty modalities config."""
        # Configure with no modalities
        config = Config(modalities=[])
        markitup = MarkItUp(config=config)
        result, info = markitup.convert(fs['test_with_comment.docx'], 'test_with_comment.docx')
            
        self.assertIsNotNone(result)
        self.assertEqual(info.category, "docx")
        # Should have text without image or audio references
        
    def test_unsupported_format(self):
        """Test handling of an unsupported file format."""
        markitup = MarkItUp()
        with self.assertRaises(Exception):
            # Should raise an exception for unsupported format
            markitup.convert(fs['random.bin'], 'random.bin')
                
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
            with self.subTest(file=filename):
                result, info = markitup.convert(fs[filename], filename)
                    
                self.assertIsNotNone(result)
                self.assertEqual(info.category, expected_category)
                self.assertTrue(result.to_llm(), "Content should not be empty")
                
    def test_to_llm_method(self):
        """Test the to_llm method of the conversion result."""
        markitup = MarkItUp()
        result, info = markitup.convert(fs['test.docx'], 'test.docx')
            
        # Call the to_llm method and check the result
        llm_format = result.to_llm()
        self.assertIsNotNone(llm_format)
        self.assertIsInstance(llm_format, list)
        
        # Check if there's at least one content element
        if llm_format:
            self.assertIn("type", llm_format[0])


if __name__ == "__main__":
    unittest.main()