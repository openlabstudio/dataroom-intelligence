# handlers/drive_handler.py - Updated for cloud deployment
"""
Google Drive API handler for DataRoom Intelligence Bot
Cloud-ready with support for environment variable credentials
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
        self.temp_dir = config.temp_storage_path

    def _authenticate(self):
        """Authenticate with Google Drive API using service account - Cloud ready"""
        try:
            # Get credentials from config (supports both env var and file)
            creds_data = config.google_credentials_json

            if not creds_data:
                raise ValueError("No Google Drive credentials found. Set GOOGLE_SERVICE_ACCOUNT_JSON environment variable or place credentials file.")

            # Create credentials from JSON data
            credentials = Credentials.from_service_account_info(
                creds_data,
                scopes=['https://www.googleapis.com/auth/drive.readonly']
            )

            service = build('drive', 'v3', credentials=credentials)

            # Test the connection
            about = service.about().get(fields="user").execute()
            user_email = about.get('user', {}).get('emailAddress', 'Unknown')

            logger.info(f"✅ Google Drive API authenticated successfully")
            logger.info(f"🔐 Service account: {user_email}")
            logger.info(f"🌍 Deployment: {'Cloud' if config.is_cloud_deployment else 'Local'}")

            return service

        except Exception as e:
            logger.error(f"❌ Google Drive authentication failed: {e}")
            logger.error(f"💡 Ensure GOOGLE_SERVICE_ACCOUNT_JSON is set or credentials file exists")
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
        """Download a file from Google Drive to temp storage - Cloud ready"""
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
                    progress = int(status.progress() * 100)
                    if progress % 25 == 0:  # Log every 25%
                        logger.info(f"📥 Download progress: {progress}%")

            # Write to local file
            with open(local_path, 'wb') as f:
                f.write(file_io.getvalue())

            file_size = os.path.getsize(local_path)
            logger.info(f"✅ Downloaded: {file_name} -> {local_path} ({file_size} bytes)")
            return local_path

        except Exception as e:
            logger.error(f"❌ Failed to download {file_name}: {e}")
            raise

    def download_dataroom(self, drive_link: str) -> List[Dict]:
        """Download all supported files from a data room folder"""
        try:
            logger.info(f"🚀 Starting data room download from: {drive_link}")
            logger.info(f"📁 Using temp directory: {self.temp_dir}")

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
            for i, file_info in enumerate(files, 1):
                try:
                    logger.info(f"📥 Downloading {i}/{len(files)}: {file_info['name']}")

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

            logger.info(f"✅ Successfully downloaded {len(downloaded_files)}/{len(files)} files")
            logger.info(f"📂 Files stored in: {self.temp_dir}")

            return downloaded_files

        except Exception as e:
            logger.error(f"❌ Data room download failed: {e}")
            raise

    def cleanup_temp_files(self):
        """Clean up temporary downloaded files - Cloud ready"""
        try:
            if os.path.exists(self.temp_dir):
                file_count = 0
                total_size = 0

                for filename in os.listdir(self.temp_dir):
                    file_path = os.path.join(self.temp_dir, filename)
                    if os.path.isfile(file_path):
                        file_size = os.path.getsize(file_path)
                        total_size += file_size
                        os.remove(file_path)
                        file_count += 1

                if file_count > 0:
                    size_mb = total_size / (1024 * 1024)
                    logger.info(f"🗑️ Cleaned up {file_count} files ({size_mb:.1f} MB)")
                    logger.info(f"💾 Freed temp storage: {self.temp_dir}")
                else:
                    logger.info("✅ Temp directory already clean")

        except Exception as e:
            logger.error(f"❌ Failed to cleanup temp files: {e}")

    def get_storage_info(self) -> dict:
        """Get information about temp storage - useful for cloud debugging"""
        try:
            info = {
                "temp_dir": self.temp_dir,
                "exists": os.path.exists(self.temp_dir),
                "writable": os.access(self.temp_dir, os.W_OK) if os.path.exists(self.temp_dir) else False,
                "files_count": 0,
                "total_size_mb": 0
            }

            if os.path.exists(self.temp_dir):
                files = [f for f in os.listdir(self.temp_dir) if os.path.isfile(os.path.join(self.temp_dir, f))]
                info["files_count"] = len(files)

                total_size = sum(os.path.getsize(os.path.join(self.temp_dir, f)) for f in files)
                info["total_size_mb"] = total_size / (1024 * 1024)

            return info

        except Exception as e:
            return {"error": str(e)}
