import os
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
from marker.config.parser import ConfigParser


class PDFProcessor:

    def __init__(self):
        print("Loading Marker models... (this may take a while on first run)")
        self.model_dict = create_model_dict()
        config = ConfigParser({"workers": 1, "pdftext_workers": 1})
        self.converter = PdfConverter(
            artifact_dict=self.model_dict,
            config=config.generate_config_dict()
        )
        print("Marker models loaded successfully.")

    def convert_to_markdown(self, pdf_path: str) -> str:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found at: {pdf_path}")

        print(f"Converting: {pdf_path}")
        rendered = self.converter(pdf_path)
        full_text, _, _ = text_from_rendered(rendered)
        return full_text

    @staticmethod
    def save_markdown(markdown_text: str, output_path: str):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_text)
        print(f"Markdown saved to: {output_path}")


if __name__ == "__main__":

    input_path = "C:\\PROGRAMS\\hackathon\\InsuranceService\\data\\input\\Bajaj(G)_03.pdf"
    output_path = "C:\\PROGRAMS\\hackathon\\InsuranceService\\data\\output\\Bajaj(G)_03.md"

    processor = PDFProcessor()
    markdown = processor.convert_to_markdown(input_path)
    processor.save_markdown(markdown, output_path)