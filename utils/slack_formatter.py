"""
Slack message formatting utilities for DataRoom Intelligence Bot
Formats analysis results and responses for optimal Slack display
"""

from typing import Dict, List, Any
from config.settings import config

def format_analysis_response(analysis_result: Dict[str, Any], document_summary: Dict[str, Any]) -> str:
    """Format the main analysis response for Slack"""

    if 'error' in analysis_result:
        return format_error_response("analysis", analysis_result['error'])

    response = f"🎯 **DATA ROOM ANALYSIS COMPLETE**\n\n"
    
    # Documents first
    response += f"📄 **Documents Analyzed: {document_summary.get('successful_processing', 0)}**\n\n"
    
    # Overall score with individual aspects breakdown
    overall_score = analysis_result.get('overall_score', 0)
    scoring = analysis_result.get('scoring', {})
    
    # Calculate component scores from existing scoring data
    if scoring:
        scores = [data.get('score', 0) for data in scoring.values()]
        calculated_overall = sum(scores) / len(scores) if scores else overall_score
    else:
        calculated_overall = overall_score
    
    response += f"📊 **Overall Score: {calculated_overall:.1f}/10**\n"
    response += f"*For detailed breakdown, see 'Complete Scoring' section below*\n\n"

    # Executive Summary
    executive_summary = analysis_result.get('executive_summary', [])
    if executive_summary:
        response += "📈 **EXECUTIVE SUMMARY:**\n"
        for point in executive_summary[:4]:  # Limit to 4 points
            response += f"• {point}\n"
        response += "\n"

    # Complete Scoring Overview (all categories with justifications)
    if scoring:
        response += "📊 **COMPLETE SCORING:**\n"
        for category, data in scoring.items():
            category_name = category.replace('_', ' ').title()
            score = data.get('score', 0)
            justification = data.get('justification', 'Information not available')
            # Replace "not analyzed" with "information not available"
            justification = justification.replace('not analyzed', 'information not available')
            justification = justification.replace('Not analyzed', 'Information not available')
            response += f"• **{category_name}:** {score}/10 - {justification}\n"
        response += "\n"

    # Red Flags
    red_flags = analysis_result.get('red_flags', [])
    if red_flags:
        response += "⚠️ **KEY RED FLAGS:**\n"
        for flag in red_flags[:3]:  # Limit to 3 flags
            response += f"• {flag}\n"
        if len(red_flags) > 3:
            response += f"• *...and {len(red_flags) - 3} more*\n"
        response += "\n"

    # Complete Missing Information (same as /gaps command)
    missing_info = analysis_result.get('missing_info', [])
    if missing_info:
        response += "❓ **INFORMATION GAPS ANALYSIS:**\n"
        for gap in missing_info:  # Show all gaps, not just first 3
            response += f"• {gap}\n"
        response += "\n"

    # Recommendation
    recommendation = analysis_result.get('recommendation', 'INVESTIGATE_FURTHER')
    response += f"🎯 **RECOMMENDATION:** {recommendation}\n\n"

    # Action buttons/commands
    response += "**Next Steps:**\n"
    response += "💬 Ask questions: `/ask [your question]`\n"
    response += "📊 Full scoring: `/scoring`\n"
    response += "📄 Investment memo: `/memo`\n"
    response += "🔍 Gap analysis: `/gaps`\n"
    response += "🔄 New analysis: `/reset`"

    return response

def format_health_response() -> str:
    """Format health check response"""

    response = "🏥 **Health Check Status**\n\n"

    # Check each component
    components = [
        ("Slack", config.slack_configured, "✅" if config.slack_configured else "❌"),
        ("OpenAI", config.openai_configured, "✅" if config.openai_configured else "❌"),
        ("Google Drive", config.google_drive_configured, "✅" if config.google_drive_configured else "❌"),
        ("Temp Storage", True, "✅"),  # Always available
    ]

    for name, status, emoji in components:
        response += f"{emoji} **{name}:** {'OK' if status else 'NOT CONFIGURED'}\n"

    # Overall status
    all_configured = all(status for _, status, _ in components[:-1])  # Exclude temp storage from requirement
    response += f"\n{('✅' if all_configured else '❌')} **All Configured:** {'YES' if all_configured else 'NO'}\n\n"

    # Environment info
    response += f"🌍 **Environment:** {config.ENVIRONMENT}\n"
    response += f"🐛 **Debug Mode:** {config.DEBUG}\n"

    if hasattr(config, 'TEMP_STORAGE_PATH'):
        response += f"📁 **Temp Directory:** {config.TEMP_STORAGE_PATH}\n"

    if not all_configured:
        response += "\n⚠️ **Missing Configuration:**\n"
        for name, status, _ in components:
            if not status and name != "Temp Storage":
                if name == "Slack":
                    response += "  - Slack tokens (SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET)\n"
                elif name == "OpenAI":
                    response += "  - OpenAI API key (OPENAI_API_KEY)\n"
                elif name == "Google Drive":
                    response += "  - Google Drive credentials (config/kfund_creds.json)\n"

    return response

def format_error_response(command: str, error_message: str) -> str:
    """Format error responses consistently"""

    response = f"❌ **{command.upper()} ERROR**\n\n"
    response += f"**Error:** {error_message}\n\n"

    # Command-specific help
    if command == "analyze":
        response += "**Usage:** `/analyze [google-drive-link]`\n"
        response += "**Example:** `/analyze https://drive.google.com/drive/folders/1234567890`\n\n"
        response += "**Troubleshooting:**\n"
        response += "• Ensure the Google Drive folder is shared (view access)\n"
        response += "• Check that the folder contains supported files (PDF, Excel, Word)\n"
        response += "• Verify the link is a folder link, not a file link\n"

    elif command == "ask":
        response += "**Usage:** `/ask [your question]`\n"
        response += "**Example:** `/ask What is the company's current runway?`\n\n"
        response += "**Note:** You must run `/analyze` first before asking questions.\n"

    elif command in ["scoring", "memo", "gaps"]:
        response += f"**Note:** You must run `/analyze` first before using `/{command}`.\n"

    response += "\n💡 **Need help?** Use `/health` to check system status."

    return response

def format_document_summary(document_summary: Dict[str, Any]) -> str:
    """Format document processing summary"""

    total = document_summary.get('total_documents', 0)
    successful = document_summary.get('successful_processing', 0)
    failed = document_summary.get('failed_processing', 0)

    response = f"📄 **DOCUMENT PROCESSING SUMMARY**\n\n"
    response += f"📊 **Total Documents:** {total}\n"
    response += f"✅ **Successfully Processed:** {successful}\n"

    if failed > 0:
        response += f"❌ **Failed Processing:** {failed}\n"

    # Document types breakdown
    doc_types = document_summary.get('document_types', {})
    if doc_types:
        response += f"\n**Document Types:**\n"
        for doc_type, count in doc_types.items():
            if doc_type != 'error':
                type_emoji = get_document_type_emoji(doc_type)
                response += f"{type_emoji} {doc_type.title()}: {count}\n"

    # Content stats
    total_content = document_summary.get('total_content_length', 0)
    if total_content > 0:
        response += f"\n📏 **Total Content:** {format_content_size(total_content)}\n"

    return response

def get_document_type_emoji(doc_type: str) -> str:
    """Get emoji for document type"""
    emoji_map = {
        'pdf': '📕',
        'excel': '📊',
        'word': '📝',
        'text': '📄',
        'csv': '📈',
        'error': '❌',
        'unsupported': '⚠️'
    }
    return emoji_map.get(doc_type.lower(), '📄')

def format_content_size(size: int) -> str:
    """Format content size in human readable format"""
    if size < 1000:
        return f"{size} characters"
    elif size < 1000000:
        return f"{size//1000}K characters"
    else:
        return f"{size//1000000}M characters"

def format_scoring_breakdown(scoring_data: Dict[str, Any]) -> str:
    """Format detailed scoring breakdown"""

    response = "📊 **DETAILED SCORING BREAKDOWN**\n\n"

    overall_score = scoring_data.get('overall_score', 0)
    response += f"🎯 **Overall Score: {overall_score}/10**\n\n"

    # Category scores
    categories = scoring_data.get('category_scores', {})
    for category, data in categories.items():
        category_name = category.replace('_', ' ').title()
        score = data.get('score', 0)
        justification = data.get('justification', 'No justification available')

        # Score emoji
        if score >= 8:
            emoji = "🟢"
        elif score >= 6:
            emoji = "🟡"
        elif score >= 4:
            emoji = "🟠"
        else:
            emoji = "🔴"

        response += f"{emoji} **{category_name}:** {score}/10\n"
        response += f"   _{justification}_\n\n"

    # Recommendation
    recommendation = scoring_data.get('recommendation', 'UNKNOWN')
    response += f"🎯 **Recommendation:** {recommendation}\n"

    return response

def truncate_text(text: str, max_length: int = 3000) -> str:
    """Truncate text to fit Slack message limits"""
    if len(text) <= max_length:
        return text

    truncated = text[:max_length - 100]  # Leave room for truncation message
    truncated += "\n\n...\n\n*[Response truncated due to length. Use specific commands for full details.]*"

    return truncated
