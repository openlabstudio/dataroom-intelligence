# handlers/drive_handler.py - FIXED for Shared Drive support
"""
Google Drive API handler for DataRoom Intelligence Bot
FIXED VERSION with complete Shared Drive support for OPENLAB/Datarooms
"""

import os
import io
import re
from typing import List, Dict, Optional, Tuple
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
from google.oauth2.service_account import Credentials
from config.settings import config
from utils.logger import get_logger

logger = get_logger(__name__)

class GoogleDriveHandler:
    """Handles Google Drive API operations with FULL Shared Drive support"""

    def __init__(self):
        self.service = self._authenticate()
        self.temp_dir = config.temp_storage_path

    def _authenticate(self):
        """Authenticate with Google Drive API - Enhanced for Shared Drives"""
        try:
            # Get credentials from config
            creds_data = config.google_credentials_json

            if not creds_data:
                raise ValueError("No Google Drive credentials found. Set GOOGLE_SERVICE_ACCOUNT_JSON environment variable or place credentials file.")

            # Create credentials with ENHANCED SCOPES for Shared Drives
            credentials = Credentials.from_service_account_info(
                creds_data,
                scopes=[
                    'https://www.googleapis.com/auth/drive.readonly',
                    'https://www.googleapis.com/auth/drive',  # Enhanced scope for Shared Drives
                    'https://www.googleapis.com/auth/drive.file'
                ]
            )

            service = build('drive', 'v3', credentials=credentials)

            # Test the connection AND Shared Drive access
            about = service.about().get(fields="user").execute()
            user_email = about.get('user', {}).get('emailAddress', 'Unknown')

            # Test Shared Drive access
            try:
                drives = service.drives().list().execute()
                shared_drives = drives.get('drives', [])

                logger.info(f"✅ Google Drive API authenticated successfully")
                logger.info(f"🔐 Service account: {user_email}")
                logger.info(f"📁 Shared Drives accessible: {len(shared_drives)}")

                # Log accessible Shared Drives (any client)
                for drive in shared_drives:
                    drive_name = drive['name']
                    logger.info(f"📁 Shared Drive accessible: {drive_name} (ID: {drive['id']})")

                if not shared_drives:
                    logger.warning("⚠️ No Shared Drives accessible - service account may need to be added to Shared Drives")

            except HttpError as e:
                logger.warning(f"⚠️ Shared Drive test failed: {e} - Personal Drive access only")

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
            r'/drive/folders/([a-zA-Z0-9-_]+)',
            r'/drive/u/\d+/folders/([a-zA-Z0-9-_]+)'  # Handle user-specific URLs
        ]

        for pattern in patterns:
            match = re.search(pattern, drive_link)
            if match:
                folder_id = match.group(1)
                logger.info(f"📁 Extracted folder ID: {folder_id}")
                return folder_id

        raise ValueError(f"❌ Could not extract folder ID from link: {drive_link}")

    def list_folder_contents(self, folder_id: str) -> List[Dict]:
        """List all files in a Google Drive folder - FIXED for Shared Drives"""
        try:
            # First, check if folder exists and get its metadata
            try:
                folder_metadata = self.service.files().get(
                    fileId=folder_id,
                    fields="id,name,parents,driveId,capabilities",
                    supportsAllDrives=True  # CRITICAL for Shared Drive folders
                ).execute()

                folder_name = folder_metadata.get('name', 'Unknown')
                logger.info(f"📁 Accessing folder: {folder_name}")

                # Check if it's in a Shared Drive
                if 'driveId' in folder_metadata:
                    drive_id = folder_metadata['driveId']
                    logger.info(f"🏢 Folder is in Shared Drive: {drive_id}")

                    # Get Shared Drive name (auto-detect any client)
                    try:
                        drive_info = self.service.drives().get(driveId=drive_id).execute()
                        drive_name = drive_info.get('name', 'Unknown')
                        logger.info(f"📁 Shared Drive name: {drive_name}")

                        # ✅ AUTO-DETECT: Works for any client's Shared Drive
                        logger.info(f"🎯 Client Shared Drive confirmed: {drive_name}")
                        logger.info(f"📊 Using Shared Drive for analysis: {drive_name}")
                    except Exception as e:
                        logger.warning(f"⚠️ Could not get Shared Drive info: {e}")
                else:
                    logger.info("👤 Folder is in personal Google Drive")

            except HttpError as e:
                if e.resp.status == 404:
                    raise ValueError(f"❌ Folder not found or not accessible: {folder_id}")
                elif e.resp.status == 403:
                    raise ValueError(f"❌ Permission denied to folder: {folder_id}. Service account needs access.")
                else:
                    raise

            # List folder contents with ENHANCED parameters for Shared Drives
            query = f"'{folder_id}' in parents and trashed=false"

            logger.info(f"🔍 Listing folder contents with Shared Drive support...")

            results = self.service.files().list(
                q=query,
                fields="files(id,name,mimeType,size,parents,driveId)",
                includeItemsFromAllDrives=True,  # CRITICAL: Include Shared Drive items
                supportsAllDrives=True,          # CRITICAL: Support Shared Drive operations
                pageSize=100  # Increase page size for better performance
            ).execute()

            files = results.get('files', [])
            logger.info(f"📋 Found {len(files)} files in folder")

            if not files:
                logger.warning("⚠️ No files found - folder may be empty or inaccessible")
                logger.info("💡 If folder should contain files, check:")
                logger.info("   - Service account has access to the Shared Drive")
                logger.info("   - Folder permissions are correctly set")
                return []

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
                file_type = file['mimeType']
                file_name = file['name']
                file_size = file.get('size', 0)

                if file_type in supported_types:
                    supported_files.append(file)
                    logger.info(f"✅ Supported: {file_name} ({file_type}) - {file_size} bytes")

                    # Special logging for PDFs
                    if file_type == 'application/pdf':
                        logger.info(f"   📕 PDF detected: {file_name}")
                else:
                    logger.warning(f"⚠️ Unsupported: {file_name} ({file_type})")

            logger.info(f"📊 Result: {len(supported_files)}/{len(files)} files are supported")
            return supported_files

        except Exception as e:
            logger.error(f"❌ Failed to list folder contents: {e}")

            # Enhanced error reporting
            if "includeItemsFromAllDrives" in str(e).lower():
                logger.error("💡 This looks like a Shared Drive access issue")
                logger.error("💡 Ensure service account is added to the Shared Drive")

            raise

    def download_file(self, file_id: str, file_name: str, mime_type: str) -> str:
        """Download a file from Google Drive - Enhanced for Shared Drives"""
        try:
            # Create temp directory if it doesn't exist
            os.makedirs(self.temp_dir, exist_ok=True)

            # Clean filename for local storage
            safe_filename = re.sub(r'[<>:"/\\|?*]', '', file_name)
            local_path = os.path.join(self.temp_dir, safe_filename)

            logger.info(f"📥 Downloading: {file_name} -> {local_path}")

            # Download file with Shared Drive support
            request = self.service.files().get_media(
                fileId=file_id,
                supportsAllDrives=True  # CRITICAL for Shared Drive files
            )

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

        except HttpError as e:
            if e.resp.status == 403:
                logger.error(f"❌ Permission denied downloading {file_name}")
                logger.error("💡 Service account may need access to this specific file")
            elif e.resp.status == 404:
                logger.error(f"❌ File not found: {file_name}")
            else:
                logger.error(f"❌ HTTP error downloading {file_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to download {file_name}: {e}")
            raise

    def download_dataroom(self, drive_link: str) -> List[Dict]:
        """Download all supported files from a data room folder - FIXED"""
        try:
            logger.info(f"🚀 Starting data room download from: {drive_link}")
            logger.info(f"📁 Using temp directory: {self.temp_dir}")

            # Extract folder ID
            folder_id = self.extract_folder_id(drive_link)

            # List folder contents with enhanced Shared Drive support
            files = self.list_folder_contents(folder_id)

            if not files:
                logger.warning("⚠️ No supported files found in data room")
                logger.info("💡 Troubleshooting steps:")
                logger.info("   1. Verify the folder contains PDF, Word, Excel, or CSV files")
                logger.info("   2. Check service account has access to the Shared Drive")
                logger.info("   3. Ensure folder permissions are correctly set")
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
                        'size': file_info.get('size', 0),
                        'drive_id': file_info.get('driveId')  # Track if from Shared Drive
                    })

                except Exception as e:
                    logger.error(f"❌ Failed to download {file_info['name']}: {e}")
                    continue

            logger.info(f"✅ Successfully downloaded {len(downloaded_files)}/{len(files)} files")
            logger.info(f"📂 Files stored in: {self.temp_dir}")

            # Log Shared Drive vs Personal Drive stats
            shared_drive_files = sum(1 for f in downloaded_files if f.get('drive_id'))
            personal_files = len(downloaded_files) - shared_drive_files

            if shared_drive_files > 0:
                logger.info(f"🏢 Shared Drive files: {shared_drive_files}")
            if personal_files > 0:
                logger.info(f"👤 Personal Drive files: {personal_files}")

            return downloaded_files

        except Exception as e:
            logger.error(f"❌ Data room download failed: {e}")

            # Enhanced error guidance
            if "not found" in str(e).lower():
                logger.error("💡 Folder not found - check the Google Drive link")
            elif "permission" in str(e).lower():
                logger.error("💡 Permission issue - ensure service account has access")
                logger.error("💡 For Shared Drives: Add service account as Content Manager")
            elif "shared drive" in str(e).lower():
                logger.error("💡 Shared Drive issue - verify includeItemsFromAllDrives=True")

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
        """Get information about temp storage and Shared Drive access"""
        try:
            info = {
                "temp_dir": self.temp_dir,
                "exists": os.path.exists(self.temp_dir),
                "writable": os.access(self.temp_dir, os.W_OK) if os.path.exists(self.temp_dir) else False,
                "files_count": 0,
                "total_size_mb": 0,
                "shared_drives": []
            }

            if os.path.exists(self.temp_dir):
                files = [f for f in os.listdir(self.temp_dir) if os.path.isfile(os.path.join(self.temp_dir, f))]
                info["files_count"] = len(files)

                total_size = sum(os.path.getsize(os.path.join(self.temp_dir, f)) for f in files)
                info["total_size_mb"] = total_size / (1024 * 1024)

            # Get Shared Drive info
            try:
                drives = self.service.drives().list().execute()
                shared_drives = drives.get('drives', [])
                info["shared_drives"] = [
                    {"name": drive["name"], "id": drive["id"]}
                    for drive in shared_drives
                ]
            except Exception as e:
                info["shared_drives_error"] = str(e)

            return info

        except Exception as e:
            return {"error": str(e)}

    def test_shared_drive_access(self, folder_url: str = None) -> dict:
        """Test Shared Drive access - for debugging"""
        try:
            result = {
                "basic_access": False,
                "shared_drives": [],
                "folder_access": None,
                "files_found": 0
            }

            # Test basic access
            about = self.service.about().get(fields="user").execute()
            result["basic_access"] = True

            # List Shared Drives
            drives = self.service.drives().list().execute()
            result["shared_drives"] = drives.get('drives', [])

            # Test specific folder if provided
            if folder_url:
                folder_id = self.extract_folder_id(folder_url)
                files = self.list_folder_contents(folder_id)
                result["folder_access"] = True
                result["files_found"] = len(files)

            return result

        except Exception as e:
            return {"error": str(e)}
