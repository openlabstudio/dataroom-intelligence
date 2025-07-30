# deploy_check.py - Pre-deployment verification script
"""
Pre-deployment verification for DataRoom Intelligence Bot
Validates all configurations before Railway deployment
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_environment_variables():
    """Check all required environment variables"""
    print("🔧 Checking Environment Variables...")

    required_vars = {
        "SLACK_BOT_TOKEN": "Slack bot token",
        "SLACK_SIGNING_SECRET": "Slack signing secret",
        "SLACK_APP_TOKEN": "Slack app token",
        "OPENAI_API_KEY": "OpenAI API key",
        "GOOGLE_SERVICE_ACCOUNT_JSON": "Google service account JSON"
    }

    missing = []
    present = []

    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            present.append(f"✅ {var}: {'*' * min(10, len(value))}...")
        else:
            missing.append(f"❌ {var}: {description}")

    for item in present:
        print(f"  {item}")

    if missing:
        print("\n❌ Missing environment variables:")
        for item in missing:
            print(f"  {item}")
        return False

    print("✅ All environment variables present")
    return True

def check_google_credentials():
    """Validate Google service account JSON"""
    print("\n🔐 Checking Google Credentials...")

    creds_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not creds_json:
        print("❌ GOOGLE_SERVICE_ACCOUNT_JSON not found")
        return False

    try:
        creds_data = json.loads(creds_json)
        required_fields = ["type", "project_id", "private_key", "client_email"]

        for field in required_fields:
            if field not in creds_data:
                print(f"❌ Missing field in credentials: {field}")
                return False

        print(f"✅ Valid service account for: {creds_data.get('client_email')}")
        print(f"✅ Project ID: {creds_data.get('project_id')}")
        return True

    except json.JSONDecodeError:
        print("❌ Invalid JSON in GOOGLE_SERVICE_ACCOUNT_JSON")
        return False

def check_file_structure():
    """Check required files are present"""
    print("\n📁 Checking File Structure...")

    required_files = [
        "app.py",
        "requirements.txt",
        "config/settings.py",
        "handlers/drive_handler.py",
        "handlers/doc_processor.py",
        "handlers/ai_analyzer.py",
        "utils/logger.py",
        "utils/slack_formatter.py",
        "prompts/analysis_prompts.py",
        "prompts/qa_prompts.py"
    ]

    missing = []
    present = []

    for file_path in required_files:
        if os.path.exists(file_path):
            present.append(f"✅ {file_path}")
        else:
            missing.append(f"❌ {file_path}")

    for item in present:
        print(f"  {item}")

    if missing:
        print("\n❌ Missing files:")
        for item in missing:
            print(f"  {item}")
        return False

    print("✅ All required files present")
    return True

def check_dependencies():
    """Check Python dependencies"""
    print("\n📦 Checking Dependencies...")

    try:
        import slack_bolt
        import openai
        import google.oauth2.service_account
        import PyPDF2
        import docx
        print("✅ Core dependencies available")

        # Optional but recommended
        try:
            import pdfplumber
            print("✅ pdfplumber available (enhanced PDF processing)")
        except ImportError:
            print("⚠️ pdfplumber not installed (PDF processing may be limited)")

        return True

    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def test_configuration_loading():
    """Test loading the cloud-ready configuration"""
    print("\n⚙️ Testing Configuration Loading...")

    try:
        # Add the current directory to Python path for imports
        sys.path.insert(0, os.getcwd())

        from config.settings import config

        print(f"✅ Config loaded successfully")
        print(f"✅ Environment: {config.ENVIRONMENT}")
        print(f"✅ Cloud deployment: {config.is_cloud_deployment}")
        print(f"✅ Temp storage: {config.temp_storage_path}")

        # Test validation
        status = config.validate_configuration()
        print(f"✅ Configuration validation: {status}")

        return True

    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False

def create_deployment_files():
    """Create deployment files if they don't exist"""
    print("\n📝 Creating Deployment Files...")

    # railway.toml
    railway_config = """[build]
builder = "NIXPACKS"

[deploy]
startCommand = "python app.py"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
"""

    # Procfile
    procfile_content = "web: python app.py"

    # .railwayignore
    railwayignore_content = """.env
.env.local
.env.*.local
temp/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
.DS_Store
.vscode/
.idea/
*.log
config/*_creds.json
!config/openlab_creds.json
"""

    files_created = []

    if not os.path.exists("railway.toml"):
        with open("railway.toml", "w") as f:
            f.write(railway_config)
        files_created.append("railway.toml")

    if not os.path.exists("Procfile"):
        with open("Procfile", "w") as f:
            f.write(procfile_content)
        files_created.append("Procfile")

    if not os.path.exists(".railwayignore"):
        with open(".railwayignore", "w") as f:
            f.write(railwayignore_content)
        files_created.append(".railwayignore")

    if files_created:
        print(f"✅ Created deployment files: {', '.join(files_created)}")
    else:
        print("✅ All deployment files already exist")

    return True

def main():
    """Main verification function"""
    print("🚀 DataRoom Intelligence Bot - Pre-Deployment Check")
    print("=" * 60)

    checks = [
        check_environment_variables,
        check_google_credentials,
        check_file_structure,
        check_dependencies,
        test_configuration_loading,
        create_deployment_files
    ]

    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"❌ Check failed with error: {e}")
            results.append(False)

    print("\n📊 DEPLOYMENT READINESS SUMMARY")
    print("=" * 60)

    if all(results):
        print("🎉 ✅ ALL CHECKS PASSED - READY FOR DEPLOYMENT!")
        print("\nNext steps:")
        print("1. railway login")
        print("2. railway init")
        print("3. Set environment variables in Railway dashboard")
        print("4. railway up")
    else:
        failed_count = sum(1 for r in results if not r)
        print(f"❌ {failed_count} checks failed - Fix issues before deployment")

        print("\n🔧 Quick fixes:")
        print("- Set missing environment variables")
        print("- Install missing dependencies: pip install -r requirements.txt")
        print("- Verify Google service account JSON format")

    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
