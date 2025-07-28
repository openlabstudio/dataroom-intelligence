"""
Google Drive API handler for DataRoom Intelligence Bot
Handles downloading and managing documents from Google Drive folders
"""

import os
import io
import re
from typing import List, Dict, Optional, Tuple
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.service_account import Credentials
from config.settings import config
from utils.logger import get_logger

logger = get_logger(__name__)

class GoogleDriveHandler:
    """Handles Google Drive API operations for document downloading"""

    def __init__(self):
        self.service = self._authenticate()
        self.temp_dir = config.TEMP_STORAGE_PATH

    def _authenticate(self):
        """Authenticate with Google Drive API using service account"""
        try:
            credentials = Credentials.from_service_account_file(
                config.GOOGLE_SERVICE_ACCOUNT_PATH,
                scopes=['https://www.googleapis.com/auth/drive.readonly']
            )
            service = build('drive', 'v3', credentials=credentials)
            logger.info("✅ Google Drive API authenticated successfully")
            return service
        except Exception as e:
            logger.error(f"❌ Google Drive authentication failed: {e}")
            raise

    def extract_folder_id(self, drive_link: str) -> str:
        """Extract folder ID from Google Drive URL"""
        patterns = [
            r'/folders/([a-zA-Z0-9-_]+)',
            r'id=([a-zA-Z0-9-_]+)',
            r'/drive/folders/([a-zA-Z0-9-_]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, drive_link)
            if match:
                folder_id = match.group(1)
                logger.info(f"📁 Extracted folder ID: {folder_id}")
                return folder_id

        raise ValueError(f"❌ Could not extract folder ID from link: {drive_link}")

    def list_folder_contents(self, folder_id: str) -> List[Dict]:
        """List all files in a Google Drive folder"""
        try:
            query = f"'{folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                fields="files(id, name, mimeType, size)"
            ).execute()

            files = results.get('files', [])
            logger.info(f"📋 Found {len(files)} files in folder")

            # Filter supported file types
            supported_files = []
            supported_types = [
                'application/pdf',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # .xlsx
                'application/vnd.ms-excel',  # .xls
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # .docx
                'application/msword',  # .doc
                'text/plain',  # .txt
                'text/csv'  # .csv
            ]

            for file in files:
                if file['mimeType'] in supported_types:
                    supported_files.append(file)
                    logger.info(f"✅ Supported file: {file['name']} ({file['mimeType']})")
                else:
                    logger.warning(f"⚠️ Unsupported file type: {file['name']} ({file['mimeType']})")

            return supported_files

        except Exception as e:
            logger.error(f"❌ Failed to list folder contents: {e}")
            raise

    def download_file(self, file_id: str, file_name: str, mime_type: str) -> str:
        """Download a file from Google Drive to temp storage"""
        try:
            # Create temp directory if it doesn't exist
            os.makedirs(self.temp_dir, exist_ok=True)

            # Clean filename for local storage
            safe_filename = re.sub(r'[<>:"/\\|?*]', '', file_name)

            local_path = os.path.join(self.temp_dir, safe_filename)

            # Download file
            request = self.service.files().get_media(fileId=file_id)
            file_io = io.BytesIO()

            downloader = MediaIoBaseDownload(file_io, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                if status:
                    logger.info(f"📥 Download progress: {int(status.progress() * 100)}%")

            # Write to local file
            with open(local_path, 'wb') as f:
                f.write(file_io.getvalue())

            logger.info(f"✅ Downloaded: {file_name} -> {local_path}")
            return local_path

        except Exception as e:
            logger.error(f"❌ Failed to download {file_name}: {e}")
            raise

    def download_dataroom(self, drive_link: str) -> List[Dict]:
        """Download all supported files from a data room folder"""
        try:
            logger.info(f"🚀 Starting data room download from: {drive_link}")

            # Extract folder ID
            folder_id = self.extract_folder_id(drive_link)

            # List folder contents
            files = self.list_folder_contents(folder_id)

            if not files:
                logger.warning("⚠️ No supported files found in data room")
                return []

            # Check file limit
            if len(files) > config.MAX_FILES_PER_DATAROOM:
                logger.warning(f"⚠️ Too many files ({len(files)}), limiting to {config.MAX_FILES_PER_DATAROOM}")
                files = files[:config.MAX_FILES_PER_DATAROOM]

            # Download all files
            downloaded_files = []
            for file_info in files:
                try:
                    local_path = self.download_file(
                        file_info['id'],
                        file_info['name'],
                        file_info['mimeType']
                    )

                    downloaded_files.append({
                        'name': file_info['name'],
                        'path': local_path,
                        'mime_type': file_info['mimeType'],
                        'size': file_info.get('size', 0)
                    })

                except Exception as e:
                    logger.error(f"❌ Failed to download {file_info['name']}: {e}")
                    continue

            logger.info(f"✅ Successfully downloaded {len(downloaded_files)} files")
            return downloaded_files

        except Exception as e:
            logger.error(f"❌ Data room download failed: {e}")
            raise

    def cleanup_temp_files(self):
        """Clean up temporary downloaded files"""
        try:
            if os.path.exists(self.temp_dir):
                for filename in os.listdir(self.temp_dir):
                    file_path = os.path.join(self.temp_dir, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        logger.info(f"🗑️ Cleaned up: {filename}")
                logger.info("✅ Temporary files cleaned up")
        except Exception as e:
            logger.error(f"❌ Failed to cleanup temp files: {e}")
