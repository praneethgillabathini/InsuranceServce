import os
from src.core.pdf_processor import PDFProcessor


def test_conversion():
    input_dir = "C:\\PROGRAMS\\hackathon\\InsuranceService\\data\\input"
    output_dir = "data/output"
    pdf_filename = "Aditya Birla(G)_03.pdf"
    input_path = os.path.join(input_dir, pdf_filename)
    output_path = os.path.join(output_dir, pdf_filename.replace(".pdf", ".md"))

    if not os.path.exists(input_path):
        print(f"⚠️  TEST SKIPPED: Please place a file named '{pdf_filename}' inside '{input_dir}'")
        return

    print("--- Initializing Processor ---")
    processor = PDFProcessor()

    print(f"--- Converting {pdf_filename} ---")
    markdown_content = processor.convert_to_markdown(input_path)

    processor.save_markdown(markdown_content, output_path)
    print("✅ Test Successful!")


if __name__ == "__main__":
    test_conversion()