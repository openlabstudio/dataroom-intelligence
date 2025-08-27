"""
Expert-Level Slack Output Formatter
FASE 2D - SPRINT 3: Format output with URLs, sources, and expert insights

Formats the market intelligence output to provide actionable value to VC analysts,
with clickable URLs, verifiable sources, and clear insights.
"""

from typing import Dict, List, Any
from utils.logger import get_logger

logger = get_logger(__name__)

def format_expert_competitive_landscape(comp_analysis: Dict[str, Any]) -> str:
    """Format competitive landscape with URLs and specific insights"""
    response = ""
    
    # Get independent analysis data
    independent = comp_analysis.get('independent_analysis', comp_analysis)
    
    # Check if we meet requirements
    meets_reqs = independent.get('meets_requirements', {})
    sources_count = independent.get('sources_count', 0)
    
    # Header with requirements status
    threat_level = independent.get('threat_level', 'Unknown')
    threat_display = threat_level.capitalize()
    
    if meets_reqs.get('competitors', {}).get('met'):
        header = f"🏢 **COMPETITIVE LANDSCAPE** ({threat_display} risk - ✅ {sources_count} sources)\n"
    else:
        header = f"🏢 **COMPETITIVE LANDSCAPE** ({threat_display} risk - ⚠️ {sources_count} sources)\n"
    response += header
    
    # Show solution-level competitors with URLs (most specific)
    solution_competitors = independent.get('solution_competitors', [])
    if solution_competitors:
        comp = solution_competitors[0]
        if isinstance(comp, dict):
            name = comp.get('name', 'Unknown')
            desc = comp.get('description', '')[:50]
            url = comp.get('url', '')
            if url:
                response += f"• **Direct competitor:** [{name}]({url}) - {desc}\n"
            else:
                response += f"• **Direct competitor:** {name} - {desc}\n"
    
    # Show market leader with URL
    market_leaders = independent.get('market_leaders', [])
    if not market_leaders:
        # Fall back to subvertical competitors
        market_leaders = independent.get('subvertical_competitors', [])
    
    if market_leaders:
        leader = market_leaders[0]
        if isinstance(leader, dict):
            name = leader.get('name', 'Unknown')
            funding = leader.get('funding', '')
            url = leader.get('url', '')
            if url:
                response += f"• **Market leader:** [{name}]({url}) ({funding})\n"
            else:
                response += f"• **Market leader:** {name} ({funding})\n"
    
    # Show key competitive risk with source
    risks = independent.get('competitive_risks', [])
    if risks:
        risk = risks[0]
        if isinstance(risk, dict):
            text = risk.get('text', str(risk))[:80]
            url = risk.get('url', '')
            if url:
                response += f"• **Key risk:** {text} [source]({url})\n"
            else:
                response += f"• **Key risk:** {text}\n"
        else:
            response += f"• **Key risk:** {str(risk)[:80]}\n"
    
    # Add regulatory insight if available
    regulatory = independent.get('regulatory_insights', [])
    if regulatory:
        reg = regulatory[0]
        if isinstance(reg, dict):
            text = reg.get('regulation', reg.get('text', ''))[:80]
            jurisdiction = reg.get('jurisdiction', '')
            url = reg.get('url', '')
            if url:
                response += f"• **Regulatory:** [{jurisdiction}]({url}) {text}\n"
            else:
                response += f"• **Regulatory:** [{jurisdiction}] {text}\n"
    
    response += "\n"
    return response

def format_expert_market_validation(validation: Dict[str, Any]) -> str:
    """Format market validation with expert opinions and precedents"""
    response = ""
    
    # Get independent analysis data
    independent = validation.get('independent_analysis', validation)
    
    # Header with confidence
    confidence_level = independent.get('confidence_level', 'Unknown')
    sources_count = len(independent.get('sources', []))
    validation_score = independent.get('validation_score', 0)
    
    if sources_count >= 10:
        header = f"📈 **MARKET VALIDATION** ({confidence_level} - ✅ {sources_count} sources)\n"
    else:
        header = f"📈 **MARKET VALIDATION** ({confidence_level} - {sources_count} sources)\n"
    response += header
    
    # Show expert consensus with source
    expert_consensus = independent.get('expert_consensus', [])
    if expert_consensus:
        expert = str(expert_consensus[0])[:100]
        # Check if we have URLs stored separately
        expert_urls = getattr(independent, 'expert_urls', [])
        if expert_urls and len(expert_urls) > 0:
            response += f"• **Expert:** {expert} [→]({expert_urls[0]})\n"
        else:
            response += f"• **Expert:** {expert}\n"
    
    # Show precedent with URL
    precedents = independent.get('precedent_analysis', [])
    if precedents:
        precedent = precedents[0]
        if isinstance(precedent, dict):
            company = precedent.get('company', 'Unknown')
            outcome = precedent.get('outcome', '')
            url = precedent.get('url', '')
            if url:
                response += f"• **Precedent:** [{company}]({url}) - {outcome}\n"
            else:
                response += f"• **Precedent:** {company} - {outcome}\n"
    
    # Show regulatory requirement
    regulatory = independent.get('regulatory_assessment', [])
    if regulatory:
        reg = str(regulatory[0])[:100]
        response += f"• **Regulatory:** {reg}\n"
    
    # Show feasibility assessment
    feasibility = independent.get('feasibility_assessment', '')
    if feasibility:
        response += f"• **Assessment:** {feasibility[:80]}\n"
    
    response += "\n"
    return response

def format_expert_funding_benchmarks(benchmarks: Dict[str, Any]) -> str:
    """Format funding benchmarks with specific deals and patterns"""
    response = ""
    
    # Get independent analysis data
    independent = benchmarks.get('independent_analysis', benchmarks)
    
    # Header
    confidence_level = independent.get('confidence_level', 'Unknown')
    sources_count = len(independent.get('sources', []))
    
    if sources_count >= 5:
        header = f"💰 **FUNDING BENCHMARKS** ({confidence_level} - ✅ {sources_count} sources)\n"
    else:
        header = f"💰 **FUNDING BENCHMARKS** ({confidence_level} - {sources_count} sources)\n"
    response += header
    
    # Show market funding pattern
    patterns = independent.get('market_funding_patterns', [])
    if patterns:
        pattern = str(patterns[0])[:100]
        response += f"• **Market:** {pattern}\n"
    
    # Show similar deal with URL
    similar_deals = independent.get('similar_deals', [])
    if similar_deals:
        deal = similar_deals[0]
        if isinstance(deal, dict):
            company = deal.get('company', 'Unknown')
            details = deal.get('details', '')[:50]
            url = deal.get('url', '')
            if url:
                response += f"• **Recent:** [{company}]({url}) - {details}\n"
            else:
                response += f"• **Recent:** {company} - {details}\n"
    
    # Show funding climate
    climate = independent.get('funding_climate', '')
    if climate:
        response += f"• **Climate:** {climate}\n"
    
    # Show investor sentiment if available
    sentiment = independent.get('investor_sentiment', [])
    if sentiment:
        sent = str(sentiment[0])[:80]
        response += f"• **Sentiment:** {sent}\n"
    
    response += "\n"
    return response

def format_opportunities_and_risks(market_intelligence_result) -> str:
    """Format separated opportunities and risks sections"""
    response = ""
    
    # Collect all opportunities
    opportunities = []
    risks = []
    
    # From competitive analysis
    if hasattr(market_intelligence_result, 'competitive_analysis'):
        comp = market_intelligence_result.competitive_analysis
        if isinstance(comp, dict):
            indep = comp.get('independent_analysis', comp)
            opportunities.extend(indep.get('market_opportunities', [])[:2])
            risks.extend(indep.get('competitive_risks', [])[:2])
    
    # From market validation
    if hasattr(market_intelligence_result, 'market_validation'):
        val = market_intelligence_result.market_validation
        if isinstance(val, dict):
            indep = val.get('independent_analysis', val)
            opportunities.extend(indep.get('market_opportunities', [])[:2])
            risks.extend(indep.get('market_risks', [])[:2])
    
    # Format opportunities
    if opportunities:
        response += "✅ **OPPORTUNITIES**\n"
        for i, opp in enumerate(opportunities[:3], 1):
            if isinstance(opp, dict):
                text = opp.get('text', str(opp))[:100]
                url = opp.get('url', '')
                if url:
                    response += f"{i}. {text} [→]({url})\n"
                else:
                    response += f"{i}. {text}\n"
            else:
                response += f"{i}. {str(opp)[:100]}\n"
        response += "\n"
    
    # Format risks
    if risks:
        response += "⚠️ **RISKS**\n"
        for i, risk in enumerate(risks[:3], 1):
            if isinstance(risk, dict):
                text = risk.get('text', str(risk))[:100]
                url = risk.get('url', '')
                if url:
                    response += f"{i}. {text} [→]({url})\n"
                else:
                    response += f"{i}. {text}\n"
            else:
                response += f"{i}. {str(risk)[:100]}\n"
        response += "\n"
    
    return response

def format_sources_section(market_intelligence_result) -> str:
    """Format clickable sources section"""
    response = ""
    
    # Collect all unique sources
    all_sources = []
    seen_urls = set()
    
    # From competitive analysis
    if hasattr(market_intelligence_result, 'competitive_analysis'):
        comp = market_intelligence_result.competitive_analysis
        if isinstance(comp, dict):
            sources = comp.get('all_sources', [])
            for source in sources:
                url = source.get('url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_sources.append(source)
    
    # From market validation
    if hasattr(market_intelligence_result, 'market_validation'):
        val = market_intelligence_result.market_validation
        if isinstance(val, dict):
            indep = val.get('independent_analysis', val)
            sources = indep.get('sources', [])
            for source in sources:
                if isinstance(source, dict):
                    url = source.get('url', '')
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        all_sources.append(source)
    
    # Show top sources
    if len(all_sources) >= 10:
        response += f"📚 **SOURCES** (✅ {len(all_sources)} verified)\n"
    else:
        response += f"📚 **SOURCES** ({len(all_sources)} found)\n"
    
    # Group by type
    academic = [s for s in all_sources if s.get('type') == 'academic']
    industry = [s for s in all_sources if s.get('type') == 'industry_report']
    regulatory = [s for s in all_sources if s.get('type') == 'regulatory']
    financial = [s for s in all_sources if s.get('type') == 'financial']
    
    # Show by category (limited for Slack)
    if academic:
        response += f"• Academic: {len(academic)} papers\n"
    if industry:
        response += f"• Industry: {len(industry)} reports\n"
    if regulatory:
        response += f"• Regulatory: {len(regulatory)} documents\n"
    if financial:
        response += f"• Financial: {len(financial)} sources\n"
    
    # Show top 3 most relevant sources with clickable links
    response += "\nTop sources:\n"
    for source in all_sources[:3]:
        title = source.get('title', '')[:50]
        url = source.get('url', '')
        domain = source.get('domain', '')
        if url:
            response += f"• [{title}...]({url})\n"
    
    response += "\n"
    return response

def format_expert_market_research(market_intelligence_result) -> str:
    """Main formatter for expert-level market research output"""
    
    response = "✅ **MARKET RESEARCH ANALYSIS COMPLETED**\n\n"
    
    # Check if we have any valid data
    has_data = (
        (hasattr(market_intelligence_result, 'market_profile') and market_intelligence_result.market_profile) or
        (hasattr(market_intelligence_result, 'competitive_analysis') and market_intelligence_result.competitive_analysis) or
        (hasattr(market_intelligence_result, 'market_validation') and market_intelligence_result.market_validation) or
        (hasattr(market_intelligence_result, 'funding_benchmarks') and market_intelligence_result.funding_benchmarks)
    )
    
    if not has_data:
        response += "⚠️ **ANALYSIS INCOMPLETE** - Please try again\n"
        return response
    
    # Market Taxonomy (keep existing)
    if hasattr(market_intelligence_result, 'market_profile') and market_intelligence_result.market_profile:
        profile = market_intelligence_result.market_profile
        solution = getattr(profile, 'solution', 'Not identified')
        sub_vertical = getattr(profile, 'sub_vertical', 'Not identified')
        vertical = getattr(profile, 'vertical', 'Not identified')
        confidence = getattr(profile, 'confidence_score', 0)
        overall_score = confidence * 10
        
        response += f"📊 **MARKET TAXONOMY** ({overall_score:.1f}/10)\n"
        response += f"• **Solution:** {solution}\n"
        response += f"• **Sub-vertical:** {sub_vertical}\n"
        response += f"• **Vertical:** {vertical}\n\n"
    
    # Competitive Landscape with URLs
    if hasattr(market_intelligence_result, 'competitive_analysis') and market_intelligence_result.competitive_analysis:
        response += format_expert_competitive_landscape(market_intelligence_result.competitive_analysis)
    
    # Market Validation with expert opinions
    if hasattr(market_intelligence_result, 'market_validation') and market_intelligence_result.market_validation:
        response += format_expert_market_validation(market_intelligence_result.market_validation)
    
    # Funding Benchmarks with specific deals
    if hasattr(market_intelligence_result, 'funding_benchmarks') and market_intelligence_result.funding_benchmarks:
        response += format_expert_funding_benchmarks(market_intelligence_result.funding_benchmarks)
    
    # Opportunities and Risks (separated)
    response += format_opportunities_and_risks(market_intelligence_result)
    
    # Sources section
    response += format_sources_section(market_intelligence_result)
    
    # Critical assessment (keep brief)
    if hasattr(market_intelligence_result, 'critical_assessment') and market_intelligence_result.critical_assessment:
        assessment = market_intelligence_result.critical_assessment
        response += "🧠 **KEY INSIGHT:**\n"
        
        if isinstance(assessment, dict):
            # Find the first meaningful point
            for key, value in assessment.items():
                if isinstance(value, str) and len(value) > 50:
                    clean_text = value.replace('"', '').replace("'", "").strip()[:200]
                    response += f"⚠️ {clean_text}\n\n"
                    break
        else:
            assessment_text = str(assessment)[:200]
            response += f"⚠️ {assessment_text}\n\n"
    
    # Commands
    response += "📋 `/ask` `/scoring` `/memo` `/gaps` `/reset`"
    
    return response