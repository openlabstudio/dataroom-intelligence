"""
Document processing handler for DataRoom Intelligence Bot
Extracts content from PDFs, Excel, Word, and other document types
"""

import os
# import pandas as pd  # COMENTAR TEMPORALMENTE
from typing import Dict, List, Optional, Any
from pathlib import Path
import PyPDF2
import docx
from utils.logger import get_logger

logger = get_logger(__name__)

class DocumentProcessor:
    """Processes various document types and extracts structured content"""

    def __init__(self):
        self.supported_extensions = {
            '.pdf': self._process_pdf,
            # '.xlsx': self._process_excel,    # COMENTAR TEMPORALMENTE
            # '.xls': self._process_excel,     # COMENTAR TEMPORALMENTE
            '.docx': self._process_word,
            '.doc': self._process_word,
            '.txt': self._process_text,
            # '.csv': self._process_csv        # COMENTAR TEMPORALMENTE
        }

    def process_document(self, file_path: str, file_name: str, mime_type: str) -> Dict[str, Any]:
        """Process a document and extract its content"""
        try:
            logger.info(f"📄 Processing document: {file_name}")

            # Get file extension
            file_ext = Path(file_name).suffix.lower()

            if file_ext not in self.supported_extensions:
                logger.warning(f"⚠️ Unsupported file extension: {file_ext}")
                return {
                    'name': file_name,
                    'type': 'unsupported',
                    'content': '',
                    'metadata': {'error': f'Unsupported file type: {file_ext}'}
                }

            # Process based on file type
            processor_func = self.supported_extensions[file_ext]
            content_data = processor_func(file_path, file_name)

            logger.info(f"✅ Successfully processed: {file_name}")
            return content_data

        except Exception as e:
            logger.error(f"❌ Failed to process {file_name}: {e}")
            return {
                'name': file_name,
                'type': 'error',
                'content': '',
                'metadata': {'error': str(e)}
            }

    def _process_pdf(self, file_path: str, file_name: str) -> Dict[str, Any]:
        """Extract text content from PDF files with multiple extraction methods"""
        try:
            # FIRST: Try PyPDF2 (fast, works with most PDFs)
            result = self._try_pypdf2_extraction(file_path, file_name)

            # If PyPDF2 fails or extracts very little, try pdfplumber
            if result['metadata']['total_chars_extracted'] < 100:
                logger.info(f"   🔄 PyPDF2 extracted only {result['metadata']['total_chars_extracted']} chars, trying pdfplumber...")
                plumber_result = self._try_pdfplumber_extraction(file_path, file_name)

                # Use the better result
                if plumber_result['metadata']['total_chars_extracted'] > result['metadata']['total_chars_extracted']:
                    logger.info(f"   ✅ pdfplumber performed better: {plumber_result['metadata']['total_chars_extracted']} chars")
                    plumber_result['metadata']['extraction_method'] = 'pdfplumber'
                    plumber_result['metadata']['pypdf2_result'] = result['metadata']
                    return plumber_result
                else:
                    result['metadata']['extraction_method'] = 'pypdf2'
                    result['metadata']['pdfplumber_attempted'] = True
                    return result
            else:
                result['metadata']['extraction_method'] = 'pypdf2'
                return result

        except Exception as e:
            logger.error(f"❌ PDF processing failed for {file_name}: {e}")
            return {
                'name': file_name,
                'type': 'pdf',
                'content': '',
                'metadata': {
                    'error': str(e),
                    'debug_info': [f"Fatal error: {str(e)}"]
                }
            }

    def _try_pypdf2_extraction(self, file_path: str, file_name: str) -> Dict[str, Any]:
        """Try extraction with PyPDF2 (original method)"""
        content = ""
        page_count = 0
        debug_info = []

        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            page_count = len(pdf_reader.pages)

            logger.info(f"🔍 PDF PyPDF2 extraction for {file_name}:")
            logger.info(f"   📄 Total pages: {page_count}")
            logger.info(f"   📏 File size: {os.path.getsize(file_path)} bytes")

            # Check metadata
            creator_info = "Unknown"
            if pdf_reader.metadata:
                creator = str(pdf_reader.metadata.get('/Creator', '')).lower()
                producer = str(pdf_reader.metadata.get('/Producer', '')).lower()
                creator_info = f"Creator: {creator}, Producer: {producer}"

                if 'powerpoint' in creator:
                    debug_info.append("PDF Type: PowerPoint export")
                elif 'preview' in creator or 'quartz' in producer:
                    debug_info.append("PDF Type: macOS Preview (potentially problematic)")
                elif 'scanner' in creator or 'scan' in producer:
                    debug_info.append("PDF Type: Scanned document")

            # Extract text page by page
            total_chars_extracted = 0
            pages_with_content = 0

            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    page_char_count = len(page_text.strip())
                    total_chars_extracted += page_char_count

                    if page_char_count > 0:
                        pages_with_content += 1
                        content += f"\n--- Page {page_num + 1} ---\n"
                        content += page_text

                        if page_num < 3:  # Only log first 3 pages
                            sample_text = page_text.strip()[:100].replace('\n', ' ')
                            logger.info(f"   📄 Page {page_num + 1}: {page_char_count} chars - \"{sample_text}...\"")

                except Exception as page_error:
                    logger.debug(f"   ❌ Page {page_num + 1} failed: {page_error}")
                    continue

            # Determine quality
            text_percentage = (pages_with_content / page_count) if page_count > 0 else 0

            if total_chars_extracted == 0:
                pdf_type = "image-only or encrypted"
                pdf_quality = "poor"
            elif text_percentage < 0.3:
                pdf_type = "mostly visual (likely presentation/deck)"
                pdf_quality = "low"
            elif text_percentage > 0.8:
                pdf_type = "text-heavy document"
                pdf_quality = "excellent"
            else:
                pdf_type = "mixed content"
                pdf_quality = "good"

            logger.info(f"   📊 PyPDF2 Summary: {pages_with_content}/{page_count} pages, {total_chars_extracted} chars")

            return {
                'name': file_name,
                'type': 'pdf',
                'content': content.strip(),
                'metadata': {
                    'pages': page_count,
                    'content_length': len(content),
                    'has_content': bool(content.strip()),
                    'pages_with_text': pages_with_content,
                    'total_chars_extracted': total_chars_extracted,
                    'text_extraction_rate': f"{(text_percentage*100):.1f}%",
                    'pdf_type': pdf_type,
                    'pdf_quality': pdf_quality,
                    'file_size_bytes': os.path.getsize(file_path),
                    'creator_info': creator_info,
                    'debug_info': debug_info
                }
            }

    def _try_pdfplumber_extraction(self, file_path: str, file_name: str) -> Dict[str, Any]:
        """Try extraction with pdfplumber (better for complex layouts)"""
        try:
            import pdfplumber
        except ImportError:
            logger.warning("   ⚠️ pdfplumber not installed, cannot try alternative extraction")
            return {
                'name': file_name,
                'type': 'pdf',
                'content': '',
                'metadata': {
                    'error': 'pdfplumber not available',
                    'total_chars_extracted': 0
                }
            }

        content = ""
        debug_info = []

        logger.info(f"🔧 PDF pdfplumber extraction for {file_name}:")

        with pdfplumber.open(file_path) as pdf:
            page_count = len(pdf.pages)
            total_chars_extracted = 0
            pages_with_content = 0
            pages_with_tables = 0

            for page_num, page in enumerate(pdf.pages):
                try:
                    # Extract text
                    page_text = page.extract_text()

                    if page_text and page_text.strip():
                        page_char_count = len(page_text.strip())
                        total_chars_extracted += page_char_count
                        pages_with_content += 1

                        content += f"\n--- Page {page_num + 1} ---\n"
                        content += page_text

                        if page_num < 3:  # Log first 3 pages
                            sample_text = page_text.strip()[:100].replace('\n', ' ')
                            logger.info(f"   📄 Page {page_num + 1}: {page_char_count} chars - \"{sample_text}...\"")

                    # Try to extract tables (pdfplumber's strength)
                    tables = page.extract_tables()
                    if tables:
                        pages_with_tables += 1
                        for table_num, table in enumerate(tables):
                            content += f"\n--- Page {page_num + 1} Table {table_num + 1} ---\n"
                            for row in table:
                                if row and any(cell for cell in row if cell):  # Skip empty rows
                                    row_text = " | ".join(str(cell) if cell else "" for cell in row)
                                    content += row_text + "\n"
                                    total_chars_extracted += len(row_text)

                        if page_num < 3:  # Log table info for first pages
                            logger.info(f"      📊 Page {page_num + 1}: {len(tables)} tables extracted")

                except Exception as page_error:
                    logger.debug(f"   ❌ pdfplumber Page {page_num + 1} failed: {page_error}")
                    continue

            # Calculate quality
            text_percentage = (pages_with_content / page_count) if page_count > 0 else 0

            if total_chars_extracted == 0:
                pdf_type = "unreadable with pdfplumber"
                pdf_quality = "poor"
            elif text_percentage > 0.8:
                pdf_type = "text-heavy document"
                pdf_quality = "excellent"
            elif pages_with_tables > 0:
                pdf_type = "table/data-heavy document"
                pdf_quality = "good"
            else:
                pdf_type = "mixed content (text + graphics)"
                pdf_quality = "good"

            logger.info(f"   📊 pdfplumber Summary: {pages_with_content}/{page_count} pages, {pages_with_tables} with tables, {total_chars_extracted} chars")

            debug_info.extend([
                f"pdfplumber extraction: {total_chars_extracted} characters",
                f"Pages with tables: {pages_with_tables}",
                f"Text percentage: {text_percentage:.1%}"
            ])

            return {
                'name': file_name,
                'type': 'pdf',
                'content': content.strip(),
                'metadata': {
                    'pages': page_count,
                    'content_length': len(content),
                    'has_content': bool(content.strip()),
                    'pages_with_text': pages_with_content,
                    'pages_with_tables': pages_with_tables,
                    'total_chars_extracted': total_chars_extracted,
                    'text_extraction_rate': f"{(text_percentage*100):.1f}%",
                    'pdf_type': pdf_type,
                    'pdf_quality': pdf_quality,
                    'file_size_bytes': os.path.getsize(file_path),
                    'debug_info': debug_info
                }
            }

    def _process_word(self, file_path: str, file_name: str) -> Dict[str, Any]:
        """Extract text content from Word documents"""
        try:
            doc = docx.Document(file_path)

            content = f"Word Document: {file_name}\n"
            content += "=" * 50 + "\n\n"

            paragraph_count = 0
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    content += paragraph.text + "\n\n"
                    paragraph_count += 1

            # Extract tables if any
            table_count = len(doc.tables)
            if table_count > 0:
                content += "\n--- TABLES ---\n\n"
                for i, table in enumerate(doc.tables):
                    content += f"Table {i + 1}:\n"
                    for row in table.rows:
                        row_text = " | ".join(cell.text.strip() for cell in row.cells)
                        content += row_text + "\n"
                    content += "\n"

            return {
                'name': file_name,
                'type': 'word',
                'content': content.strip(),
                'metadata': {
                    'paragraphs': paragraph_count,
                    'tables': table_count,
                    'content_length': len(content),
                    'has_content': bool(content.strip())
                }
            }

        except Exception as e:
            logger.error(f"❌ Word processing failed: {e}")
            raise

    def _process_text(self, file_path: str, file_name: str) -> Dict[str, Any]:
        """Process plain text files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            return {
                'name': file_name,
                'type': 'text',
                'content': content,
                'metadata': {
                    'content_length': len(content),
                    'line_count': len(content.split('\n')),
                    'has_content': bool(content.strip())
                }
            }

        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as file:
                content = file.read()

            return {
                'name': file_name,
                'type': 'text',
                'content': content,
                'metadata': {
                    'content_length': len(content),
                    'line_count': len(content.split('\n')),
                    'has_content': bool(content.strip()),
                    'encoding': 'latin-1'
                }
            }

    def process_dataroom_documents(self, downloaded_files: List[Dict]) -> List[Dict[str, Any]]:
        """Process all documents in a data room"""
        processed_documents = []

        logger.info(f"🔄 Processing {len(downloaded_files)} documents...")

        for file_info in downloaded_files:
            try:
                processed_doc = self.process_document(
                    file_info['path'],
                    file_info['name'],
                    file_info['mime_type']
                )
                processed_documents.append(processed_doc)

            except Exception as e:
                logger.error(f"❌ Failed to process {file_info['name']}: {e}")
                # Add error document to maintain document list
                processed_documents.append({
                    'name': file_info['name'],
                    'type': 'error',
                    'content': '',
                    'metadata': {'error': str(e)}
                })

        logger.info(f"✅ Processed {len(processed_documents)} documents")
        return processed_documents

    def get_content_summary(self, processed_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a summary of all processed documents"""
        summary = {
            'total_documents': len(processed_documents),
            'document_types': {},
            'total_content_length': 0,
            'successful_processing': 0,
            'failed_processing': 0,
            'document_list': []
        }

        for doc in processed_documents:
            doc_type = doc.get('type', 'unknown')

            # Count by type
            if doc_type not in summary['document_types']:
                summary['document_types'][doc_type] = 0
            summary['document_types'][doc_type] += 1

            # Track processing success
            if doc_type == 'error':
                summary['failed_processing'] += 1
            else:
                summary['successful_processing'] += 1
                summary['total_content_length'] += len(doc.get('content', ''))

            # Document list for reference
            summary['document_list'].append({
                'name': doc['name'],
                'type': doc_type,
                'has_content': bool(doc.get('content', '').strip()),
                'content_length': len(doc.get('content', ''))
            })

        return summary
