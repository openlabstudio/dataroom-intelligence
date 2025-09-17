"""
Slack message formatting utilities for DataRoom Intelligence Bot
Formats analysis results and responses for optimal Slack display
"""

from typing import Dict, List, Any, Union
from config.settings import config
from utils.logger import get_logger

logger = get_logger(__name__)

def format_analysis_response(analysis_result: Union[str, Dict[str, Any]],
                           document_summary: Dict[str, Any] = None,
                           market_profile=None) -> str:
    """
    Format the main analysis response for Slack

    Compatibilidad:
      - Si recibe `str`, lo devuelve tal cual (nuevo flujo 'Slack-Ready')
      - Si recibe `dict`, usa el formateo legacy

    TODO (deprecación): eliminar cuando toda la app use salida 'Slack-Ready'
    """

    # Debug logging to trace the issue
    logger.info(f"🔍 format_analysis_response received: type={type(analysis_result)}, len={len(str(analysis_result))}")
    
    # NEW: Handle string response directly (analyst-friendly implementation)
    if isinstance(analysis_result, str):
        if document_summary or market_profile:
            logger.warning("format_analysis_response received string but also received "
                          "document_summary/market_profile parameters - these will be ignored. "
                          "Consider using analysis_result directly.")
        logger.info("🚀 Using direct Slack-ready string content!")
        return analysis_result

    # Handle dictionary response (legacy path)
    if isinstance(analysis_result, dict):
        if 'error' in analysis_result:
            return format_error_response("analysis", analysis_result['error'])

        # NEW: Use Slack-ready content directly if available
        if 'slack_ready_content' in analysis_result:
            logger.info("🚀 Using direct Slack-ready content!")
            return analysis_result['slack_ready_content']

    # FALLBACK: Old format (in case we need to rollback)
    response = f"🎯 **DATA ROOM ANALYSIS COMPLETE**\n\n"
    
    # Documents first
    response += f"📄 **Documents Analyzed: {document_summary.get('successful_processing', 0)}**\n\n"
    
    
    # Market Taxonomy (if available)
    if market_profile:
        response += "📊 **MARKET TAXONOMY**\n"
        if hasattr(market_profile, 'solution') and market_profile.solution:
            response += f"• **Solution:** {market_profile.solution}\n"
        if hasattr(market_profile, 'sub_vertical') and market_profile.sub_vertical:
            response += f"• **Sub-vertical:** {market_profile.sub_vertical}\n"
        if hasattr(market_profile, 'vertical') and market_profile.vertical:
            response += f"• **Vertical:** {market_profile.vertical}\n"
        if hasattr(market_profile, 'industry') and market_profile.industry:
            response += f"• **Industry:** {market_profile.industry}\n"
        if hasattr(market_profile, 'target_market') and market_profile.target_market:
            response += f"• **Target:** {market_profile.target_market}\n"
        response += "\n"

    # Executive Summary
    executive_summary = analysis_result.get('executive_summary', [])
    if executive_summary:
        response += "📈 **EXECUTIVE SUMMARY:**\n"
        for point in executive_summary[:4]:  # Limit to 4 points
            response += f"• {point}\n"
        response += "\n"

    # Value Proposition
    value_proposition = analysis_result.get('value_proposition', [])
    if value_proposition:
        response += "💡 **VALUE PROPOSITION:**\n"
        for point in value_proposition:
            response += f"• {point}\n"
        response += "\n"

    # Market Analysis
    market_analysis = analysis_result.get('market_analysis', [])
    if market_analysis:
        response += "📊 **MARKET ANALYSIS:**\n"
        for point in market_analysis:
            response += f"• {point}\n"
        response += "\n"

    # Competitors
    competitors = analysis_result.get('competitors', [])
    if competitors:
        response += "⚔️ **COMPETITORS:**\n"
        for point in competitors:
            response += f"• {point}\n"
        response += "\n"

    # Product Roadmap
    product_roadmap = analysis_result.get('product_roadmap', [])
    if product_roadmap:
        response += "🛣️ **PRODUCT ROADMAP:**\n"
        for point in product_roadmap:
            response += f"• {point}\n"
        response += "\n"

    # Go-to-Market Strategy
    go_to_market_strategy = analysis_result.get('go_to_market_strategy', [])
    if go_to_market_strategy:
        response += "🚀 **GO-TO-MARKET STRATEGY:**\n"
        for point in go_to_market_strategy:
            response += f"• {point}\n"
        response += "\n"

    # Financial Highlights
    financial_highlights = analysis_result.get('financial_highlights', [])
    if financial_highlights:
        response += "💰 **FINANCIAL HIGHLIGHTS:**\n"
        for highlight in financial_highlights:
            response += f"• {highlight}\n"
        response += "\n"


    # Action buttons/commands
    response += "**Next Steps:**\n"
    response += "💬 Ask questions: `/ask [your question]`\n"
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

    elif command == "gaps":
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
