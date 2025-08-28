"""
Analyst-Focused Market Research Formatter
Simple, clear, actionable format for VC analysts

Focus: Clarity over complexity, actionable insights over generic data
"""

from typing import Dict, Any, List
from utils.logger import get_logger

logger = get_logger(__name__)

def format_analyst_market_research(market_intelligence_result) -> str:
    """
    Format market research for VC analyst consumption
    
    Design principles:
    - Simple structure, no confusing sections
    - Clear competitor hierarchy (Solution > Sub-vertical > Vertical)
    - Actionable insights with proper context
    - Clean URLs and source attribution
    - Under 3500 chars for Slack
    
    Args:
        market_intelligence_result: Result from orchestrator
        
    Returns:
        Clean, analyst-friendly formatted string
    """
    try:
        logger.info("🎯 Formatting market research for analyst consumption")
        
        response = "✅ **MARKET RESEARCH COMPLETED**\n\n"
        
        # 1. MARKET TAXONOMY (Simple, no score)
        response += _format_market_taxonomy(market_intelligence_result)
        
        # 2. COMPETITIVE LANDSCAPE (Clear hierarchy)
        response += _format_competitive_landscape(market_intelligence_result)
        
        # 3. MARKET INSIGHTS (Opportunities & Risks)
        response += _format_market_insights(market_intelligence_result)
        
        # 4. KEY SOURCES (Only the most relevant)
        response += _format_key_sources(market_intelligence_result)
        
        # 5. COMMANDS (Keep user engagement)
        response += "\n📋 `/ask` `/scoring` `/memo` `/gaps` `/reset`"
        
        logger.info(f"✅ Analyst format completed. Length: {len(response)} chars")
        return response
        
    except Exception as e:
        logger.error(f"❌ Analyst formatting failed: {e}", exc_info=True)
        return _get_fallback_response(str(e))

def _format_market_taxonomy(result) -> str:
    """Format market taxonomy - simple and clean"""
    try:
        if not hasattr(result, 'market_profile') or not result.market_profile:
            return "📊 **MARKET TAXONOMY**\n⚠️ Market classification not available\n\n"
        
        profile = result.market_profile
        
        section = "📊 **MARKET TAXONOMY**\n"
        section += f"• **Solution:** {getattr(profile, 'solution', 'Not identified')}\n"
        section += f"• **Sub-vertical:** {getattr(profile, 'sub_vertical', 'Not identified')}\n"
        section += f"• **Vertical:** {getattr(profile, 'vertical', 'Not identified')}\n"
        section += f"• **Target:** {getattr(profile, 'target_market', 'Not identified')}\n\n"
        
        return section
        
    except Exception as e:
        logger.error(f"❌ Market taxonomy formatting failed: {e}")
        return "📊 **MARKET TAXONOMY**\n⚠️ Classification data unavailable\n\n"

def _format_competitive_landscape(result) -> str:
    """Format competitive landscape with clear hierarchy"""
    try:
        if not hasattr(result, 'competitive_analysis') or not result.competitive_analysis:
            return "🏢 **COMPETITIVE LANDSCAPE**\n⚠️ Competitive data not available\n\n"
        
        # Get competitive data
        comp_data = result.competitive_analysis
        if hasattr(comp_data, 'to_dict'):
            comp_dict = comp_data.to_dict()
            independent = comp_dict.get('independent_analysis', {})
        else:
            independent = comp_data
        
        section = "🏢 **COMPETITIVE LANDSCAPE**\n\n"
        
        # Solution-level competitors (most important)
        solution_competitors = independent.get('solution_competitors', [])
        if solution_competitors:
            section += "**Direct Competitors (Solution Level):**\n"
            for i, comp in enumerate(solution_competitors[:4], 1):  # Max 4 to save space
                name = comp.get('name', 'Unknown')
                description = comp.get('description', comp.get('mention_context', ''))[:60]
                url = comp.get('url', '')
                
                section += f"{i}. {name}"
                if description and description != name:
                    section += f" - {description}..."
                section += f"\n   {url}\n"
            section += "\n"
        
        # Sub-vertical competitors (if different from solution)
        subvertical_competitors = independent.get('subvertical_competitors', [])
        unique_subvertical = [
            comp for comp in subvertical_competitors 
            if comp.get('name') not in [s.get('name') for s in solution_competitors]
        ]
        
        if unique_subvertical:
            section += "**Sub-vertical Competitors:**\n"
            for i, comp in enumerate(unique_subvertical[:3], len(solution_competitors) + 1):
                name = comp.get('name', 'Unknown')
                description = comp.get('description', comp.get('mention_context', ''))[:60]
                url = comp.get('url', '')
                
                section += f"{i}. {name}"
                if description and description != name:
                    section += f" - {description}..."
                section += f"\n   {url}\n"
            section += "\n"
        
        # If no competitors found
        if not solution_competitors and not unique_subvertical:
            section += "⚠️ **Specific competitors not identified in current search**\n"
            section += "• Recommendation: Manual competitive analysis required\n"
            section += "• Consider broader industry research or specialized databases\n\n"
        
        return section
        
    except Exception as e:
        logger.error(f"❌ Competitive landscape formatting failed: {e}")
        return "🏢 **COMPETITIVE LANDSCAPE**\n⚠️ Competitive analysis unavailable\n\n"

def _format_market_insights(result) -> str:
    """Format intelligent market insights - opportunities and risks"""
    try:
        from utils.insight_generator import generate_market_insights
        
        # Extract competitive data and market profile
        competitive_data = {}
        market_profile = {}
        
        if hasattr(result, 'competitive_analysis'):
            comp_data = result.competitive_analysis
            if hasattr(comp_data, 'to_dict'):
                comp_dict = comp_data.to_dict()
                competitive_data = comp_dict.get('independent_analysis', {})
        
        if hasattr(result, 'market_profile'):
            profile = result.market_profile
            if hasattr(profile, 'to_dict'):
                market_profile = profile.to_dict()
            else:
                market_profile = {
                    'solution': getattr(profile, 'solution', 'Unknown'),
                    'sub_vertical': getattr(profile, 'sub_vertical', 'Unknown'),
                    'vertical': getattr(profile, 'vertical', 'Unknown'),
                    'target_market': getattr(profile, 'target_market', 'Unknown')
                }
        
        # Generate intelligent insights
        insights = generate_market_insights(competitive_data, market_profile)
        
        section = "**Market Insights:**\n"
        
        # Format opportunities
        opportunities = insights.get('opportunities', [])
        if opportunities:
            section += "✅ **Opportunities:**\n"
            for opp in opportunities[:3]:  # Max 3 for space
                section += f"• {opp}\n"
        
        # Format risks
        risks = insights.get('risks', [])
        if risks:
            section += "⚠️ **Risks:**\n"
            for risk in risks[:3]:  # Max 3 for space
                section += f"• {risk}\n"
        
        if not opportunities and not risks:
            section += "⚠️ **Market insights generation failed**\n"
            section += "• Manual competitive analysis recommended\n"
        
        section += "\n"
        return section
        
    except ImportError:
        logger.warning("Insight generator not available")
        return "**Market Insights:**\n⚠️ Advanced insight analysis unavailable\n\n"
    except Exception as e:
        logger.error(f"❌ Market insights formatting failed: {e}")
        return "**Market Insights:**\n⚠️ Insights analysis error\n\n"

def _format_key_sources(result) -> str:
    """Format only the most relevant and credible sources"""
    try:
        section = "📚 **Key Sources:**\n"
        
        sources = []
        
        # Collect sources from all analysis components
        if hasattr(result, 'competitive_analysis'):
            comp_data = result.competitive_analysis
            if hasattr(comp_data, 'to_dict'):
                comp_dict = comp_data.to_dict()
                comp_sources = comp_dict.get('all_sources', [])
                sources.extend(comp_sources[:5])  # Top 5 from competitive
        
        # Filter and rank sources by credibility
        credible_sources = []
        for source in sources:
            domain = source.get('domain', '')
            source_type = source.get('type', 'general')
            title = source.get('title', 'Unknown')
            url = source.get('url', '')
            
            # Prioritize credible sources
            if any(term in domain.lower() for term in [
                'crunchbase', 'techcrunch', 'reuters', 'bloomberg', 
                'nature.com', 'mckinsey', 'bcg.com', 'deloitte',
                'pitchbook', 'cbinsights'
            ]):
                credibility_score = 3
            elif source_type in ['industry_report', 'financial']:
                credibility_score = 2
            else:
                credibility_score = 1
            
            credible_sources.append({
                'title': title[:50],  # Truncate long titles
                'url': url,
                'credibility': credibility_score,
                'domain': domain
            })
        
        # Sort by credibility and take top 3
        credible_sources.sort(key=lambda x: x['credibility'], reverse=True)
        top_sources = credible_sources[:3]
        
        if top_sources:
            for i, source in enumerate(top_sources, 1):
                section += f"{i}. {source['title']}... ({source['domain']})\n"
                section += f"   {source['url']}\n"
        else:
            section += "⚠️ **No credible sources identified**\n"
            section += "• Sources may require manual verification\n"
            section += "• Consider industry databases or expert contacts\n"
        
        section += "\n"
        return section
        
    except Exception as e:
        logger.error(f"❌ Key sources formatting failed: {e}")
        return "📚 **Key Sources:**\n⚠️ Source attribution unavailable\n\n"

def _get_fallback_response(error_msg: str) -> str:
    """Fallback response when formatting fails"""
    return f"""❌ **MARKET RESEARCH ERROR**

The market research analysis encountered an error during formatting.

**Error:** {error_msg}

**Next Steps:**
• Try running `/market-research` again
• Check that documents contain market information
• Contact administrator if issue persists

📋 `/analyze` `/ask` `/reset`"""