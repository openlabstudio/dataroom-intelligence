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
        logger.info("🎯 FORMATTING STARTING - Analyst market research formatter called")
        logger.info(f"🎯 INPUT TYPE: {type(market_intelligence_result)}")
        logger.info(f"🎯 INPUT ATTRIBUTES: {dir(market_intelligence_result)}")
        
        response = "✅ **MARKET RESEARCH COMPLETED**\n\n"
        
        # 1. MARKET TAXONOMY (Simple, no score)
        response += _format_market_taxonomy(market_intelligence_result)
        
        # 2. COMPETITIVE LANDSCAPE (Clear hierarchy)
        response += _format_competitive_landscape(market_intelligence_result)
        
        # 3. MARKET INSIGHTS (Opportunities & Risks)
        response += _format_market_insights(market_intelligence_result)
        
        # 4. INVESTMENT DECISION (Critical Synthesizer output)
        response += _format_investment_decision(market_intelligence_result)
        
        # 5. KEY SOURCES (Only the most relevant)
        response += _format_key_sources(market_intelligence_result)
        
        # 6. COMMANDS (Keep user engagement)
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
            # comp_data is already a dict - extract independent_analysis
            independent = comp_data.get('independent_analysis', {})
        
        section = "🏢 **COMPETITIVE LANDSCAPE**\n\n"
        
        # Solution-level competitors (most important)
        solution_competitors = independent.get('solution_competitors', [])
        if solution_competitors:
            section += "**Direct Competitors (Solution Level):**\n"
            for i, comp in enumerate(solution_competitors[:3], 1):  # Max 3 for Slack limit
                name = comp.get('name', 'Unknown')
                description = comp.get('description', comp.get('mention_context', ''))[:40]  # Shorter desc
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
            for i, comp in enumerate(unique_subvertical[:2], len(solution_competitors) + 1):  # Max 2 sub-vertical
                name = comp.get('name', 'Unknown')
                description = comp.get('description', comp.get('mention_context', ''))[:40]  # Shorter desc
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

def _format_investment_decision(result) -> str:
    """Format investment decision from Critical Synthesizer Agent"""
    try:
        # Check if investment decision is available
        if not hasattr(result, 'investment_decision') or not result.investment_decision:
            return ""  # No investment decision available
        
        decision_data = result.investment_decision
        decision = decision_data.get('decision', 'CAUTION')
        
        # Decision icon mapping
        decision_icons = {
            'GO': '🟢',
            'CAUTION': '🟡', 
            'NO-GO': '🔴'
        }
        
        section = f"\n{decision_icons.get(decision, '🟡')} **INVESTMENT DECISION: {decision}**\n\n"
        
        # Executive Summary
        executive_summary = decision_data.get('executive_summary', '')
        if executive_summary:
            section += f"📋 {executive_summary}\n\n"
        
        # Rationale  
        rationale = decision_data.get('key_rationale', [])
        if rationale:
            section += "⚖️ **RATIONALE:**\n"
            for reason in rationale:
                section += f"• {reason}\n"
            section += "\n"
        
        # Key Risks
        risks = decision_data.get('key_risks', [])
        if risks:
            section += "🚨 **KEY RISKS:**\n"
            for risk in risks:
                section += f"• {risk}\n"
            section += "\n"
        
        # Market Opportunity
        opportunity = decision_data.get('market_opportunity', '')
        if opportunity:
            section += f"💰 **OPPORTUNITY:** {opportunity}\n\n"
        
        # Confidence Level
        confidence = decision_data.get('confidence_level', 'Medium')
        confidence_reason = decision_data.get('confidence_reason', '')
        section += f"📊 **CONFIDENCE:** {confidence}"
        if confidence_reason:
            section += f" - {confidence_reason}"
        section += "\n"
        
        # Red Flags (if any)
        red_flags = decision_data.get('red_flags', [])
        if red_flags:
            section += "\n🔍 **RED FLAGS:**\n"
            for flag in red_flags:
                severity_icon = "🚨" if flag.get('severity') == 'high' else "⚠️"
                section += f"• {severity_icon} {flag.get('reason', 'Unknown risk')}\n"
        
        section += "\n"
        return section
        
    except Exception as e:
        logger.error(f"❌ Investment decision formatting failed: {e}")
        return "\n🟡 **INVESTMENT DECISION: CAUTION**\n📋 Decision analysis unavailable - manual review required\n\n"

def _format_key_sources(result) -> str:
    """Format only the most relevant and credible sources"""
    try:
        section = "📚 **Key Sources:**\n"
        
        sources = []
        
        # AGGRESSIVE DEBUG: Log everything
        logger.info(f"🚨 SOURCES DEBUG START")
        logger.info(f"🚨 Result type: {type(result)}")
        logger.info(f"🚨 Result has competitive_analysis: {hasattr(result, 'competitive_analysis')}")
        
# Removed fake sources - testing complete
        
        # Handle both object and dict formats for competitive_analysis
        if hasattr(result, 'competitive_analysis'):
            comp_data = result.competitive_analysis
            logger.info(f"🚨 Competitive analysis exists, type: {type(comp_data)}")
            
            # Case 1: Object with to_dict method (CompetitiveProfile)
            if hasattr(comp_data, 'to_dict'):
                comp_dict = comp_data.to_dict()
                comp_sources = comp_dict.get('all_sources', [])
                logger.info(f"🚨 Object format: Found {len(comp_sources)} sources via to_dict()")
            # Case 2: Already a dict (from orchestrator)
            elif isinstance(comp_data, dict):
                comp_sources = comp_data.get('all_sources', [])
                logger.info(f"🚨 Dict format: Found {len(comp_sources)} sources directly")
            else:
                comp_sources = []
                logger.warning(f"🚨 Unknown competitive_analysis format: {type(comp_data)}")
            
            if comp_sources:
                logger.info(f"🚨 First real source: {comp_sources[0]}")
                sources.extend(comp_sources[:5])  # Top 5 from competitive
            else:
                logger.warning(f"🚨 No sources found in competitive_analysis")
        else:
            logger.error(f"🚨 NO competitive_analysis found in result!")
        
        # Filter and rank sources by credibility
        credible_sources = []
        for source in sources:
            domain = source.get('domain', '')
            source_type = source.get('type', 'general')
            title = source.get('title', 'Unknown')
            url = source.get('url', '')
            
            # Prioritize credible sources - EXPANDED to include market research sources
            if any(term in domain.lower() for term in [
                # Premium financial/startup sources
                'crunchbase', 'techcrunch', 'reuters', 'bloomberg', 
                'pitchbook', 'cbinsights', 'ft.com', 'wsj.com',
                # Consulting & Industry Reports
                'mckinsey', 'bcg.com', 'deloitte', 'pwc.com', 'kpmg',
                # Academic/Research
                'nature.com', 'sciencedirect', 'springer', '.edu'
            ]):
                credibility_score = 3
            elif any(term in domain.lower() for term in [
                # Market Research firms
                'tracxn', 'stratview', 'grandview', 'precedence', 'market.us',
                'startus-insights', 'mordorintelligence', 'researchandmarkets',
                # Industry databases
                'statista', 'ibisworld', 'euromonitor', 'frost.com'
            ]) or source_type in ['industry_report', 'financial']:
                credibility_score = 2
            else:
                credibility_score = 1
            
            credible_sources.append({
                'title': title[:40],  # Shorter titles for Slack limit
                'url': url,
                'credibility': credibility_score,
                'domain': domain
            })
        
        # Sort by credibility and take top 4 (increased for more coverage)
        credible_sources.sort(key=lambda x: x['credibility'], reverse=True)
        
        # Limit sources for Slack message length
        top_sources = credible_sources[:3]  # Reduced from 4 to 3
        
        if top_sources:
            # Group by credibility for better display
            high_cred = [s for s in top_sources if s['credibility'] >= 2]
            other_sources = [s for s in top_sources if s['credibility'] == 1]
            
            # Show high credibility sources first
            for i, source in enumerate(high_cred, 1):
                section += f"{i}. {source['title']}... ({source['domain']})\n"
                section += f"   {source['url']}\n"
            
            # Show other sources if we have space and need more
            remaining_slots = 3 - len(high_cred)  # Match total of 3 sources
            for i, source in enumerate(other_sources[:remaining_slots], len(high_cred) + 1):
                section += f"{i}. {source['title']}... ({source['domain']})\n"
                section += f"   {source['url']}\n"
                
        else:
            section += "⚠️ **No sources available**\n"
            section += "• Web search may have failed\n"
            section += "• Try running analysis again\n"
        
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