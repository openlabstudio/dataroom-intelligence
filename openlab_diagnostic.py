#!/usr/bin/env python3
"""
OPENLAB Shared Drive Specific Diagnostic
Diagnose exact permission issues for OPENLAB setup
"""

import os
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def check_service_account_details():
    """Check service account configuration"""
    print("🔐 SERVICE ACCOUNT ANALYSIS")
    print("=" * 40)

    # Try environment variable first (Railway)
    creds_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if creds_json:
        try:
            creds_data = json.loads(creds_json)
            print("✅ Credentials source: Environment variable (Railway)")
        except json.JSONDecodeError:
            print("❌ Invalid JSON in environment variable")
            return None
    else:
        # Try local file
        try:
            with open('config/openlab_creds.json', 'r') as f:
                creds_data = json.load(f)
            print("✅ Credentials source: Local file (config/openlab_creds.json)")
        except FileNotFoundError:
            print("❌ No credentials found!")
            print("💡 Set GOOGLE_SERVICE_ACCOUNT_JSON or place openlab_creds.json")
            return None

    # Analyze service account
    email = creds_data.get('client_email', 'Unknown')
    project_id = creds_data.get('project_id', 'Unknown')
    account_type = creds_data.get('type', 'Unknown')

    print(f"📧 Service Account: {email}")
    print(f"🆔 Project ID: {project_id}")
    print(f"🔒 Type: {account_type}")

    # Check if it's external to OPENLAB
    if 'openlab' not in email.lower() and 'openlab' not in project_id.lower():
        print("⚠️  EXTERNAL SERVICE ACCOUNT DETECTED")
        print("💡 This service account is NOT from OPENLAB's Google Cloud")
        print("💡 OPENLAB admin may need to allow external access")
    else:
        print("✅ Internal OPENLAB service account")

    return creds_data

def test_drive_access_detailed():
    """Detailed Google Drive access test"""
    print("\n🔍 GOOGLE DRIVE ACCESS TEST")
    print("=" * 40)

    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError

        # Get credentials
        creds_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        if creds_json:
            creds_data = json.loads(creds_json)
        else:
            with open('config/openlab_creds.json', 'r') as f:
                creds_data = json.load(f)

        # Create credentials with all necessary scopes
        credentials = Credentials.from_service_account_info(
            creds_data,
            scopes=[
                'https://www.googleapis.com/auth/drive.readonly',
                'https://www.googleapis.com/auth/drive',
                'https://www.googleapis.com/auth/drive.file'
            ]
        )

        service = build('drive', 'v3', credentials=credentials)

        # Test 1: Basic access
        print("🔍 Testing basic API access...")
        try:
            about = service.about().get(fields="user,storageQuota").execute()
            user_email = about.get('user', {}).get('emailAddress', 'Unknown')
            print(f"✅ API access successful as: {user_email}")
        except Exception as e:
            print(f"❌ Basic API access failed: {e}")
            return False

        # Test 2: List Shared Drives
        print("\n🔍 Testing Shared Drive access...")
        try:
            drives_result = service.drives().list().execute()
            shared_drives = drives_result.get('drives', [])

            print(f"📁 Found {len(shared_drives)} Shared Drive(s):")

            openlab_drive = None
            for drive in shared_drives:
                name = drive['name']
                drive_id = drive['id']
                print(f"   📁 {name} (ID: {drive_id})")

                if 'openlab' in name.lower():
                    openlab_drive = drive
                    print(f"   🎯 OPENLAB Shared Drive found!")

            if not shared_drives:
                print("❌ NO SHARED DRIVES ACCESSIBLE")
                print("💡 Service account is NOT added to any Shared Drive")
                print("💡 ACTION REQUIRED: Add service account to OPENLAB Shared Drive")
                return False

            if not openlab_drive:
                print("❌ OPENLAB Shared Drive NOT FOUND")
                print("💡 Service account has access to Shared Drives, but not OPENLAB")
                print("💡 ACTION REQUIRED: Add service account to OPENLAB Shared Drive specifically")
                return False

            print(f"✅ OPENLAB Shared Drive accessible: {openlab_drive['name']}")
            return openlab_drive

        except HttpError as e:
            print(f"❌ Shared Drive access failed: {e}")
            if e.resp.status == 403:
                print("💡 Permission denied - likely workspace policy issue")
                print("💡 OPENLAB admin may need to allow external service accounts")
            return False

    except Exception as e:
        print(f"❌ Drive access test failed: {e}")
        return False

def test_specific_folder(folder_url):
    """Test access to specific OPENLAB folder"""
    print(f"\n🔍 TESTING SPECIFIC FOLDER")
    print("=" * 40)
    print(f"📁 URL: {folder_url}")

    try:
        # Import here to avoid issues if not available
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        import re

        # Get credentials
        creds_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        if creds_json:
            creds_data = json.loads(creds_json)
        else:
            with open('config/openlab_creds.json', 'r') as f:
                creds_data = json.load(f)

        credentials = Credentials.from_service_account_info(
            creds_data,
            scopes=[
                'https://www.googleapis.com/auth/drive.readonly',
                'https://www.googleapis.com/auth/drive',
                'https://www.googleapis.com/auth/drive.file'
            ]
        )

        service = build('drive', 'v3', credentials=credentials)

        # Extract folder ID
        patterns = [
            r'/folders/([a-zA-Z0-9-_]+)',
            r'id=([a-zA-Z0-9-_]+)',
            r'/drive/folders/([a-zA-Z0-9-_]+)',
            r'/drive/u/\d+/folders/([a-zA-Z0-9-_]+)'
        ]

        folder_id = None
        for pattern in patterns:
            match = re.search(pattern, folder_url)
            if match:
                folder_id = match.group(1)
                break

        if not folder_id:
            print("❌ Could not extract folder ID from URL")
            return False

        print(f"📋 Folder ID: {folder_id}")

        # Test folder metadata access
        print("\n🔍 Testing folder metadata access...")
        try:
            folder_metadata = service.files().get(
                fileId=folder_id,
                fields="id,name,parents,driveId,capabilities,permissions",
                supportsAllDrives=True
            ).execute()

            folder_name = folder_metadata.get('name', 'Unknown')
            print(f"✅ Folder accessible: {folder_name}")

            # Check if in Shared Drive
            if 'driveId' in folder_metadata:
                drive_id = folder_metadata['driveId']
                print(f"🏢 Located in Shared Drive ID: {drive_id}")

                # Get Shared Drive name
                try:
                    drive_info = service.drives().get(driveId=drive_id).execute()
                    drive_name = drive_info.get('name', 'Unknown')
                    print(f"📁 Shared Drive name: {drive_name}")

                    if 'openlab' in drive_name.lower():
                        print("🎯 Confirmed: This is in OPENLAB Shared Drive")
                    else:
                        print("⚠️  This folder is NOT in OPENLAB Shared Drive")
                except Exception as e:
                    print(f"⚠️  Could not get Shared Drive info: {e}")
            else:
                print("👤 This folder is in personal Google Drive (not Shared Drive)")

        except HttpError as e:
            print(f"❌ Folder metadata access failed: {e}")
            if e.resp.status == 404:
                print("💡 Folder not found - check URL")
            elif e.resp.status == 403:
                print("💡 Permission denied to folder")
                print("💡 Even if you have folder permissions, you need Shared Drive access")
            return False

        # Test folder contents
        print("\n🔍 Testing folder contents access...")
        try:
            query = f"'{folder_id}' in parents and trashed=false"

            results = service.files().list(
                q=query,
                fields="files(id,name,mimeType,size)",
                includeItemsFromAllDrives=True,  # CRITICAL for Shared Drives
                supportsAllDrives=True,          # CRITICAL for Shared Drives
                pageSize=10
            ).execute()

            files = results.get('files', [])
            print(f"📄 Found {len(files)} file(s) in folder")

            if not files:
                print("❌ No files accessible")
                print("💡 Possible causes:")
                print("   - Folder is empty")
                print("   - Missing Shared Drive permissions")
                print("   - Wrong API parameters")
                return False

            # Show first few files
            supported_types = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
            supported_count = 0

            for i, file in enumerate(files[:5]):
                mime_type = file.get('mimeType', 'unknown')
                size = file.get('size', 'unknown')
                is_supported = any(st in mime_type for st in supported_types)

                if is_supported:
                    supported_count += 1

                status = "✅" if is_supported else "⚠️"
                print(f"   {status} {file['name']} ({mime_type})")

            if len(files) > 5:
                print(f"   ... and {len(files) - 5} more files")

            print(f"\n📊 {supported_count}/{len(files)} files are supported for analysis")

            if supported_count > 0:
                print("🎉 SUCCESS: Folder access working!")
                return True
            else:
                print("⚠️  No supported files found (PDF, Word, Excel)")
                return False

        except HttpError as e:
            print(f"❌ Folder contents access failed: {e}")
            if e.resp.status == 403:
                print("💡 This usually means missing Shared Drive permissions")
                print("💡 Add service account to OPENLAB Shared Drive (not just folder)")
            return False

    except Exception as e:
        print(f"❌ Folder test failed: {e}")
        return False

def main():
    """Main diagnostic function"""
    print("🚀 OPENLAB SHARED DRIVE DIAGNOSTIC")
    print("=" * 50)
    print("🎯 Goal: Fix access to OPENLAB dataroom folder")
    print()

    # Step 1: Check service account
    creds_data = check_service_account_details()
    if not creds_data:
        print("\n❌ CANNOT PROCEED: No valid credentials found")
        return

    # Step 2: Test Drive access
    openlab_drive = test_drive_access_detailed()

    # Step 3: Test specific folder if provided
    if len(sys.argv) > 1:
        folder_url = sys.argv[1]
        success = test_specific_folder(folder_url)

        print("\n" + "=" * 50)
        if success:
            print("🎉 ✅ FOLDER ACCESS WORKING!")
            print("🚀 You can now use /analyze command in Slack")
        else:
            print("❌ FOLDER ACCESS FAILED")
            print_recommendations(creds_data, openlab_drive)
    else:
        print("\n💡 To test your specific folder, run:")
        print("   python openlab_diagnostic.py 'https://drive.google.com/drive/folders/YOUR_FOLDER_ID'")

        if not openlab_drive:
            print_recommendations(creds_data, False)

def print_recommendations(creds_data, has_openlab_access):
    """Print specific recommendations based on test results"""
    print("\n🛠 RECOMMENDED ACTIONS")
    print("=" * 30)

    service_account_email = creds_data.get('client_email', 'Unknown')

    if not has_openlab_access:
        print("🎯 PRIMARY ISSUE: Service account not added to OPENLAB Shared Drive")
        print("\n📋 STEPS TO FIX:")
        print("1. Open Google Drive → 'Shared drives' → 'OPENLAB'")
        print("2. Right-click OPENLAB → 'Manage members'")
        print("3. Click 'Add members'")
        print(f"4. Enter: {service_account_email}")
        print("5. Role: 'Content Manager' or 'Contributor'")
        print("6. Click 'Send'")

        print("\n⚠️  IMPORTANT: Add to SHARED DRIVE, not just folder!")

        # Check if external service account
        if 'openlab' not in service_account_email.lower():
            print("\n🔒 WORKSPACE POLICY CHECK:")
            print("If adding service account fails, OPENLAB admin needs to:")
            print("• Google Admin Console → Security → API controls")
            print("• Allow external service account access")
            print("• Or create internal service account in OPENLAB's Google Cloud")
    else:
        print("✅ Shared Drive access working")
        print("💡 Issue might be with specific folder permissions")
        print("💡 Try /analyze command with folder URL")

if __name__ == "__main__":
    main()
