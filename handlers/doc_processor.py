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
                        """Extract text content from PDF files with detailed debugging"""
                    try:
                            content = ""
                            page_count = 0
                            debug_info = []

                            with open(file_path, 'rb') as file:
                            pdf_reader = PyPDF2.PdfReader(file)
                            page_count = len(pdf_reader.pages)

                            logger.info(f"🔍 PDF Debug for {file_name}:")
                            logger.info(f"   📄 Total pages: {page_count}")

                        # Check if PDF is encrypted
                        if pdf_reader.is_encrypted:
                            logger.warning(f"   🔒 PDF is encrypted")
                            debug_info.append("PDF is encrypted")
                            try:
                                pdf_reader.decrypt("")  # Try empty password
                                logger.info(f"   ✅ Decrypted with empty password")
                            except:
                                logger.error(f"   ❌ Could not decrypt PDF")
                                return {
                                    'name': file_name,
                                    'type': 'pdf',
                                    'content': '',
                                    'metadata': {
                                        'pages': page_count,
                                        'error': 'Encrypted PDF - could not decrypt',
                                        'debug_info': debug_info
                                    }
                                }

                        # Check PDF metadata
                        if pdf_reader.metadata:
                            logger.info(f"   📊 PDF metadata:")
                            for key, value in pdf_reader.metadata.items():
                                logger.info(f"      {key}: {value}")
                                debug_info.append(f"Metadata {key}: {value}")

                        # Process each page with detailed logging
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
                                    logger.info(f"   📄 Page {page_num + 1}: {page_char_count} characters extracted")
                                else:
                                    logger.warning(f"   ⚠️ Page {page_num + 1}: 0 characters (possibly image-only)")
                                    debug_info.append(f"Page {page_num + 1}: No text content")

                                # Check if page has images
                                if '/XObject' in page.get('/Resources', {}):
                                    xobjects = page['/Resources']['/XObject'].get_object()
                                    image_count = sum(1 for obj in xobjects.values()
                                                    if obj.get('/Subtype') == '/Image')
                                    if image_count > 0:
                                        logger.info(f"      🖼️ Page {page_num + 1}: {image_count} images detected")
                                        debug_info.append(f"Page {page_num + 1}: {image_count} images")

                            except Exception as page_error:
                                logger.error(f"   ❌ Page {page_num + 1} processing failed: {page_error}")
                                debug_info.append(f"Page {page_num + 1}: Error - {str(page_error)}")
                                continue

                        # Summary logging
                        logger.info(f"   📊 PDF Summary:")
                        logger.info(f"      Total characters: {total_chars_extracted}")
                        logger.info(f"      Pages with text: {pages_with_content}/{page_count}")
                        logger.info(f"      Success rate: {(pages_with_content/page_count*100):.1f}%")

                        # Determine PDF type
                        if total_chars_extracted == 0:
                            pdf_type = "image-only or encrypted"
                        elif pages_with_content / page_count < 0.3:
                            pdf_type = "mostly visual (likely presentation/deck)"
                        else:
                            pdf_type = "text-heavy document"

                        debug_info.append(f"PDF type assessment: {pdf_type}")
                        logger.info(f"   🏷️ PDF type: {pdf_type}")

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
                            'pdf_type': pdf_type,
                            'debug_info': debug_info
                        }
                    }

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
