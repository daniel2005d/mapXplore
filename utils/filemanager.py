import zipfile
import io
from base64 import b64decode
import xml.etree.ElementTree as ET
import PyPDF2


class FileManager:
    def __init__(self) -> None:
        self._magic_numbers = {                                                                                                                                                                                                                      
            b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A": "png",
            b"\xFF\xD8\xFF": "jpeg",
            b"\x47\x49\x46\x38\x37\x61": "GIF", 
            b"\x50\x4B\x03\x04":"zip",
            b"%PDF-":"pdf"

        }    
    
    def _get_format(self, content:bytearray)->str:
        for magic_file, file_type in self._magic_numbers.items():
                    if content.startswith(magic_file):
                        return file_type
        return None
    
    def _read_office(self, zip_file, document_name)->str:
        text=""
        with zip_file.open(document_name) as xml:
            
            tree = ET.parse(xml)
            root = tree.getroot()
            for elem in root.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t") or elem in root.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"):
                if elem.text:                                                                                                                                                                                                              
                    text += elem.text
        return text
          

    def get_file_type(self, content:str):
        content_bytes = b64decode(content)
        return self.get_zip_format(content_bytes)
    
        
    def get_zip_format(self, content:bytearray):
        file_type = self._get_format(content)
        if file_type is not None:
            if file_type == 'zip':
                    with zipfile.ZipFile(io.BytesIO(content), 'r') as zip_file:
                        if 'word/document.xml' in zip_file.namelist():
                                return self._read_office(zip_file, 'word/document.xml'), 'docx'
                        elif 'xl/workbook.xml' in zip_file.namelist():
                                return self._read_office(zip_file, 'xl/workbook.xml'), 'xlsx'
                        elif 'ppt/presentation.xml' in zip_file.namelist():
                                return 'pptx'
        
        return None, file_type
    
    def read_pdf(self, content:bytearray, max_pages=2)->str:
        text = ""
        pdf = io.BytesIO(content)
        reader = PyPDF2.PdfFileReader(pdf)
        pages = min(reader.numPages, max_pages)
        for page in range(pages):
            page_content = reader.getPage(page)
            text+=page_content.extract_text()
        if reader.numPages > max_pages:
             text+=f" [green][{max_pages}/{reader.numPages}] pages[reset]"
             

        return text

         
        

