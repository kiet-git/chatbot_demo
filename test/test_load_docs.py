import unittest
from chain import load_documents  # Import the function you want to test
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from docx import Document


# Define the directory path for your test documents
TEST_DIR = "./tests/test_documents/"

class TestLoadDocuments(unittest.TestCase):

    def setUp(self):
        # Ensure the directory for test documents exists
        os.makedirs(TEST_DIR, exist_ok=True)

        # Create a test PDF document
        pdf_path = os.path.join(TEST_DIR, 'test_document.pdf')
        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.drawString(100, 750, "Test PDF content")
        c.save()

        # Create a test DOCX document
        docx_path = os.path.join(TEST_DIR, 'test_document.docx')
        doc = Document()
        doc.add_paragraph("Test DOCX content")
        doc.save(docx_path)

        # Create a test TXT document
        txt_path = os.path.join(TEST_DIR, 'test_document.txt')
        with open(txt_path, 'w') as txt_file:
            txt_file.write("Test text content")


    def tearDown(self):
        # Remove the test files and directories inside TEST_DIR
        for item in os.listdir(TEST_DIR):
            item_path = os.path.join(TEST_DIR, item)

            if os.path.isdir(item_path):
                # Remove directories and their contents
                shutil.rmtree(item_path)
            else:
                # Remove files
                os.remove(item_path)

    def test_load_documents(self):
        documents = load_documents(TEST_DIR)
        # Define the expected text content for each document type
        expected_content = {
            'pdf': "Test PDF content",
            'docx': "Test DOCX content",
            'txt': "Test text content"
        }

        self.assertEqual(len(documents), 3)

        for doc in documents:
            self.assertTrue(doc.page_content is not None)
            self.assertTrue(doc.metadata is not None)

             # Get the file extension from the metadata 'source' attribute
            source = doc.metadata.get('source', '')
            file_extension = source.split('.')[-1]

            # Check if the expected content exists in the document
            self.assertTrue(expected_content.get(file_extension) in doc.page_content)

    def test_load_invalid_document(self):
        invalid_path = os.path.join(TEST_DIR, 'invalid_document.html')
        with open(invalid_path, 'w') as invalid_file:
            invalid_file.write("Invalid document content")
        documents = load_documents(TEST_DIR)
        self.assertEqual(len(documents), 3)  # Expect 3 valid documents

    def test_load_empty_directory(self):
        empty_dir = TEST_DIR + 'empty_directory/'
        os.makedirs(empty_dir, exist_ok=True)
        documents = load_documents(empty_dir)
        self.assertEqual(len(documents), 0)

    def test_load_nonexistent_directory(self):
        nonexistent_dir = TEST_DIR + 'nonexistent_directory/'
        self.assertFalse(os.path.exists(nonexistent_dir))
        documents = load_documents(nonexistent_dir)
        self.assertEqual(len(documents), 0)

    def test_load_directory_with_subdirectory(self):
        # Create a subdirectory inside the test directory
        sub_dir = os.path.join(TEST_DIR, 'subdirectory/')
        os.makedirs(sub_dir, exist_ok=True)

        # Create a test TXT document inside the subdirectory
        subdocument_path = os.path.join(sub_dir, 'subdocument.txt')
        with open(subdocument_path, 'w') as subdocument_file:
            subdocument_file.write("Test subdocument content")

        # Load documents from the test directory
        documents = load_documents(TEST_DIR)

        self.assertEqual(len(documents), 4)  # Expect 4 documents, including the one in the subdirectory

        # Check if the content of the subdocument is present in the loaded documents
        subdocument_content = "Test subdocument content"
        self.assertTrue(any(subdocument_content in doc.page_content for doc in documents))


if __name__ == '__main__':
    unittest.main()
