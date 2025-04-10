import pdfplumber
import docx
import io
from typing import Dict, List, Union
import json
import os

class DocumentProcessor:
    def __init__(self):
        self.supported_types = {
            'application/pdf': self._process_pdf,
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': self._process_docx
        }

    def process_document(self, content: bytes, mime_type: str) -> Dict:
        """Process a document and extract its content."""
        if mime_type not in self.supported_types:
            raise ValueError(f"Unsupported file type: {mime_type}")

        processor = self.supported_types[mime_type]
        return processor(content)

    def _process_pdf(self, content: bytes) -> Dict:
        """Extract text from a PDF document."""
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            sections = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    sections.append({
                        'content': text,
                        'page': page.page_number
                    })
            return {
                'type': 'pdf',
                'sections': sections
            }

    def _process_docx(self, content: bytes) -> Dict:
        """Extract text from a Word document."""
        doc = docx.Document(io.BytesIO(content))
        sections = []
        current_section = {'content': '', 'heading': ''}

        for paragraph in doc.paragraphs:
            if paragraph.style.name.startswith('Heading'):
                if current_section['content']:
                    sections.append(current_section)
                current_section = {
                    'content': paragraph.text,
                    'heading': paragraph.text
                }
            else:
                current_section['content'] += '\n' + paragraph.text

        if current_section['content']:
            sections.append(current_section)

        return {
            'type': 'docx',
            'sections': sections
        }

    def save_processed_document(self, processed_content: Dict, filename: str, output_dir: str = 'processed_docs'):
        """Save processed document content to a JSON file."""
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{filename}.json")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(processed_content, f, ensure_ascii=False, indent=2)

    def load_processed_document(self, filename: str, input_dir: str = 'processed_docs') -> Dict:
        """Load processed document content from a JSON file."""
        input_path = os.path.join(input_dir, f"{filename}.json")
        
        with open(input_path, 'r', encoding='utf-8') as f:
            return json.load(f) 