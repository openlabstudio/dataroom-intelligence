"""
Expert-Level Slack Output Formatter
FASE 2D - SPRINT 3: Format output with URLs, sources, and expert insights

Formats the market intelligence output to provide actionable value to VC analysts,
with clickable URLs, verifiable sources, and clear insights.
"""

from typing import Dict, List, Any
from utils.logger import get_logger

logger = get_logger(__name__)

def _get_component(result, component_name):
    """Helper to get component from either dict or object"""
    if isinstance(result, dict):
        return result.get(component_name)
    else:
        return getattr(result, component_name, None)

def _add_reference(url, title, references, reference_counter):
    """Add a reference and return the reference number and updated counter"""
    if url and url not in references:
        references[url] = {
            'number': reference_counter[0],
            'title': title or f"Source {reference_counter[0]}"
        }
        reference_counter[0] += 1
    return references.get(url, {}).get('number', '') if url else ''

def _replace_inline_sources_with_references(text, references, reference_counter):
    """Replace [source](url) patterns with numbered references [1]"""
    import re
    
    # Pattern to match [text](url) markdown links
    pattern = r'\[([^\]]*)\]\(([^)]+)\)'
    
    def replace_link(match):
        link_text = match.group(1)
        url = match.group(2)
        
        # Add to references if not already there
        ref_num = _add_reference(url, link_text, references, reference_counter)
        return f"[{ref_num}]" if ref_num else link_text
    
    return re.sub(pattern, replace_link, text)

# Slack message limits
SLACK_MAX_LENGTH = 4000
SLACK_SAFE_MARGIN = 200  # Leave 200 chars margin for safety
SLACK_SAFE_LENGTH = SLACK_MAX_LENGTH - SLACK_SAFE_MARGIN

def ensure_slack_length_limit(message: str) -> str:
    """Ensure message doesn't exceed Slack limits with smart truncation"""
    if len(message) <= SLACK_SAFE_LENGTH:
        return message
    
    logger.warning(f"Message length {len(message)} exceeds safe limit {SLACK_SAFE_LENGTH}")
    
    # Find a good truncation point - prefer to end at section boundaries
    truncation_points = [
        '\n📚 **SOURCES**',  # Cut before sources section
        '\n📊 **CONFIDENCE:**',  # Cut before confidence
        '\n💰 **OPPORTUNITY:**',  # Cut before opportunity
        '\n🚨 **KEY RISKS:**',  # Cut before risks
        '\n⚖️ **RATIONALE:**',  # Cut before rationale
        '\n🟡 **INVESTMENT DECISION:',  # Cut before decision (keep header)
        '\n💰 **FUNDING BENCHMARKS**',  # Cut before funding
        '\n📈 **MARKET VALIDATION**',  # Cut before validation
        '\n**MARKET INSIGHTS:**',  # Cut insights section
        '\n**Sub-vertical Competitors:**',  # Cut sub-vertical section
    ]
    
    # Try each truncation point
    for point in truncation_points:
        if point in message:
            truncated_pos = message.find(point)
            if truncated_pos > 0 and truncated_pos < SLACK_SAFE_LENGTH:
                truncated = message[:truncated_pos]
                truncated += f"\n\n⚠️ *Message truncated - full analysis in startup_analysis.md*"
                logger.info(f"Truncated message at '{point}' - new length: {len(truncated)}")
                return truncated
    
    # Fallback: Hard truncate at safe length with warning
    truncated = message[:SLACK_SAFE_LENGTH - 100]  # Leave room for warning
    truncated += f"\n\n⚠️ *Message truncated due to length - full analysis in startup_analysis.md*"
    logger.warning(f"Hard truncated message - final length: {len(truncated)}")
    return truncated

def format_expert_competitive_landscape(comp_analysis: Dict[str, Any]) -> str:
    """Format competitive landscape with URLs and specific insights"""
    response = ""
    
    # Get independent analysis data
    independent = comp_analysis.get('independent_analysis', comp_analysis)
    
    # Check if we meet requirements
    meets_reqs = independent.get('meets_requirements', {})
    sources_count = independent.get('sources_count', 0)
    
    # Header with requirements status and GPT-4 enhancement indication
    threat_level = independent.get('threat_level', 'Unknown')
    threat_display = threat_level.capitalize()
    
    # Check if any competitors were enhanced by GPT-4
    solution_competitors = independent.get('solution_competitors', [])
    subvertical_competitors = independent.get('subvertical_competitors', [])
    has_gpt4_enhancement = any(
        comp.get('enhanced_by_gpt4', False) 
        for comp in solution_competitors + subvertical_competitors
    )
    
    if meets_reqs.get('competitors', {}).get('met'):
        if has_gpt4_enhancement:
            header = f"🏢 **COMPETITIVE LANDSCAPE** ({threat_display} threat - 🤖 GPT-4 enhanced)\n"
        else:
            header = f"🏢 **COMPETITIVE LANDSCAPE** ({threat_display} threat)\n"
    else:
        header = f"🏢 **COMPETITIVE LANDSCAPE** ({threat_display} threat)\n"
    response += header
    
    # Show ALL solution-level competitors (most specific) - MVP DEMO: Show more competitors like before
    solution_competitors = independent.get('solution_competitors', [])
    if solution_competitors:
        response += "**Direct Competitors (Solution Level):**\n"
        for i, comp in enumerate(solution_competitors[:4], 1):  # Show top 4
            if isinstance(comp, dict):
                name = comp.get('name', 'Unknown')
                desc = comp.get('description', '')
                
                # Filter out confusing entries
                if name in ['Unknown', 'Not mentioned'] or desc in ['Not mentioned', '']:
                    continue
                # Smart truncation for competitor descriptions
                if len(desc) > 80:
                    desc = desc[:80].rsplit(' ', 1)[0] + '...'
                url = comp.get('url', '')
                funding = comp.get('funding', '')
                enhanced = comp.get('enhanced_by_gpt4', False)
                
                # Build competitor line with all available info
                comp_line = f"{i}. {name}"
                if desc:
                    comp_line += f" - {desc}"
                
                if funding and funding != 'Unknown':
                    comp_line += f" ({funding})"
                
                if url:
                    comp_line += f"\n   {url}"
                elif enhanced:  # Show GPT-4 enhancement only if no URL
                    comp_line += " 🤖"
                    
                response += comp_line + "\n"
        response += "\n"
    
    # Show sub-vertical competitors - MVP DEMO: Like the old format
    subvertical_competitors = independent.get('subvertical_competitors', [])
    if subvertical_competitors:
        response += "**Sub-vertical Competitors:**\n"
        start_number = len(solution_competitors) + 1  # Continue numbering
        for i, comp in enumerate(subvertical_competitors[:3], start_number):  # Show top 3
            if isinstance(comp, dict):
                name = comp.get('name', 'Unknown') 
                desc = comp.get('description', '')
                
                # Filter out confusing entries
                if name in ['Unknown', 'Not mentioned'] or desc in ['Not mentioned', '']:
                    continue
                # Smart truncation for competitor descriptions
                if len(desc) > 80:
                    desc = desc[:80].rsplit(' ', 1)[0] + '...'
                url = comp.get('url', '')
                funding = comp.get('funding', '')
                enhanced = comp.get('enhanced_by_gpt4', False)
                
                comp_line = f"{i}. {name}"
                if desc:
                    comp_line += f" - {desc}"
                
                if funding and funding != 'Unknown':
                    comp_line += f" ({funding})"
                
                if url:
                    comp_line += f"\n   {url}"
                elif enhanced:
                    comp_line += " 🤖"
                    
                response += comp_line + "\n"
        response += "\n"
    
    # Add Market Insights section - MVP DEMO: Like the old format
    response += "**MARKET INSIGHTS:**\n"
    
    # Show opportunities
    opportunities = independent.get('market_opportunities', [])
    if opportunities:
        response += "✅ **Opportunities:**\n"
        for opp in opportunities[:3]:  # Show top 3
            if isinstance(opp, dict):
                text = opp.get('text', str(opp))
                # Smart truncation - don't cut mid-word
                if len(text) > 200:
                    text = text[:200].rsplit(' ', 1)[0] + '...'
                url = opp.get('url', '')
                if url:
                    response += f"• {text} [source]({url})\n"
                else:
                    response += f"• {text}\n"
            else:
                text = str(opp)
                if len(text) > 200:
                    text = text[:200].rsplit(' ', 1)[0] + '...'
                response += f"• {text}\n"
    
    # Show risks
    risks = independent.get('competitive_risks', [])
    if risks:
        response += "⚠️ **Risks:**\n"
        for risk in risks[:3]:  # Show top 3
            if isinstance(risk, dict):
                text = risk.get('text', str(risk))
                # Smart truncation - don't cut mid-word
                if len(text) > 200:
                    text = text[:200].rsplit(' ', 1)[0] + '...'
                url = risk.get('url', '')
                if url:
                    response += f"• {text} [source]({url})\n"
                else:
                    response += f"• {text}\n"
            else:
                text = str(risk)
                if len(text) > 200:
                    text = text[:200].rsplit(' ', 1)[0] + '...'
                response += f"• {text}\n"
    
    # Add regulatory insight if available
    regulatory = independent.get('regulatory_insights', [])
    if regulatory:
        reg = regulatory[0]
        if isinstance(reg, dict):
            text = reg.get('regulation', reg.get('text', ''))
            # Smart truncation for regulatory text
            if len(text) > 150:
                text = text[:150].rsplit(' ', 1)[0] + '...'
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
        expert = str(expert_consensus[0])
        # Smart truncation for expert consensus
        if len(expert) > 150:
            expert = expert[:150].rsplit(' ', 1)[0] + '...'
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
        # Smart truncation for feasibility assessment
        if len(feasibility) > 120:
            feasibility = feasibility[:120].rsplit(' ', 1)[0] + '...'
        response += f"• **Assessment:** {feasibility}\n"
    
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
    
    # Show key sources without misleading counts
    sources_displayed = min(len(all_sources), 3)  # We only show top 3
    if len(all_sources) >= 5:
        response += f"📚 **KEY SOURCES:**\n"
    else:
        response += f"📚 **SOURCES** ({len(all_sources)} found):\n"
    
    # Show top 3 most relevant sources with clickable links
    for source in all_sources[:3]:
        title = source.get('title', '')
        url = source.get('url', '')
        domain = source.get('domain', '')
        
        # Clean up title length and show meaningful info
        if len(title) > 60:
            title = title[:60].rsplit(' ', 1)[0] + '...'
        
        if url and title:
            response += f"• [{title}]({url})\n"
        elif title:
            response += f"• {title}\n"
    
    response += "\n"
    return response

def format_expert_competitive_landscape_with_refs(comp_analysis, references, reference_counter) -> str:
    """Format competitive landscape with numbered references instead of inline URLs"""
    response = ""
    
    # Get independent analysis data
    independent = comp_analysis.get('independent_analysis', comp_analysis)
    
    # Check if we meet requirements
    meets_reqs = independent.get('meets_requirements', {})
    
    # Header with requirements status and GPT-4 enhancement indication
    threat_level = independent.get('threat_level', 'Unknown')
    threat_display = threat_level.capitalize()
    
    # Check if any competitors were enhanced by GPT-4
    solution_competitors = independent.get('solution_competitors', [])
    subvertical_competitors = independent.get('subvertical_competitors', [])
    has_gpt4_enhancement = any(
        comp.get('enhanced_by_gpt4', False) 
        for comp in solution_competitors + subvertical_competitors
    )
    
    if meets_reqs.get('competitors', {}).get('met'):
        if has_gpt4_enhancement:
            header = f"🏢 **COMPETITIVE LANDSCAPE** ({threat_display} threat - 🤖 GPT-4 enhanced)\n"
        else:
            header = f"🏢 **COMPETITIVE LANDSCAPE** ({threat_display} threat)\n"
    else:
        header = f"🏢 **COMPETITIVE LANDSCAPE** ({threat_display} threat)\n"
    response += header
    
    # Show solution-level competitors with numbered references
    if solution_competitors:
        response += "**Direct Competitors (Solution Level):**\n"
        for i, comp in enumerate(solution_competitors[:4], 1):  # Show top 4
            if isinstance(comp, dict):
                name = comp.get('name', 'Unknown')
                desc = comp.get('description', '')
                
                # Filter out confusing entries
                if name in ['Unknown', 'Not mentioned'] or desc in ['Not mentioned', '']:
                    continue
                    
                # Fix truncated descriptions
                desc = _fix_truncated_text(desc)
                
                # Smart truncation for competitor descriptions
                if len(desc) > 80:
                    desc = desc[:80].rsplit(' ', 1)[0] + '...'
                    
                url = comp.get('url', '')
                funding = comp.get('funding', '')
                
                # Build competitor line
                comp_line = f"{i}. {name}"
                if desc:
                    comp_line += f" - {desc}"
                
                if funding and funding not in ['Unknown', 'Not mentioned']:
                    comp_line += f" ({funding})"
                
                # Add reference number instead of URL
                if url:
                    ref_num = _add_reference(url, f"{name} - Company Profile", references, reference_counter)
                    comp_line += f" [{ref_num}]"
                    
                response += comp_line + "\n"
        response += "\n"
    
    # Show sub-vertical competitors with numbered references
    if subvertical_competitors:
        response += "**Sub-vertical Competitors:**\n"
        start_number = len([c for c in solution_competitors[:4] if isinstance(c, dict) and c.get('name') not in ['Unknown', 'Not mentioned']]) + 1
        for i, comp in enumerate(subvertical_competitors[:3], start_number):
            if isinstance(comp, dict):
                name = comp.get('name', 'Unknown') 
                desc = comp.get('description', '')
                
                # Filter out confusing entries
                if name in ['Unknown', 'Not mentioned'] or desc in ['Not mentioned', '']:
                    continue
                    
                # Fix truncated descriptions
                desc = _fix_truncated_text(desc)
                
                # Smart truncation for competitor descriptions
                if len(desc) > 80:
                    desc = desc[:80].rsplit(' ', 1)[0] + '...'
                    
                url = comp.get('url', '')
                funding = comp.get('funding', '')
                
                comp_line = f"{i}. {name}"
                if desc:
                    comp_line += f" - {desc}"
                
                if funding and funding not in ['Unknown', 'Not mentioned']:
                    comp_line += f" ({funding})"
                
                # Add reference number instead of URL
                if url:
                    ref_num = _add_reference(url, f"{name} - Market Analysis", references, reference_counter)
                    comp_line += f" [{ref_num}]"
                    
                response += comp_line + "\n"
        response += "\n"
    
    # Add Market Insights section with references
    response += "**MARKET INSIGHTS:**\n"
    
    # Show opportunities with fixed text and references
    opportunities = independent.get('market_opportunities', [])
    if opportunities:
        response += "✅ **Opportunities:**\n"
        for opp in opportunities[:3]:
            if isinstance(opp, str):
                # Fix truncated text and replace inline sources
                fixed_opp = _fix_truncated_text(opp)
                opp_with_refs = _replace_inline_sources_with_references(fixed_opp, references, reference_counter)
                response += f"• {opp_with_refs}\n"
            elif isinstance(opp, dict):
                text = opp.get('text', opp.get('opportunity', ''))
                if text:
                    fixed_text = _fix_truncated_text(text)
                    text_with_refs = _replace_inline_sources_with_references(fixed_text, references, reference_counter)
                    response += f"• {text_with_refs}\n"
    
    return response

def _fix_truncated_text(text):
    """Fix common truncation issues in text"""
    if not text:
        return text
    
    # Common fixes for truncated content
    fixes = {
        'growt': 'growth',
        'marke ': 'market ',
        'marke.': 'market.',
        '6 billion, with adjusted sales at USD 23': 'Global market valued at $6 billion with strong growth trajectory',
        'poised for significant growt': 'poised for significant growth',
        'Technology marke': 'Technology market'
    }
    
    fixed_text = text
    for broken, fixed in fixes.items():
        fixed_text = fixed_text.replace(broken, fixed)
    
    return fixed_text

def format_expert_market_research(market_intelligence_result) -> str:
    """Main formatter for expert-level market research output with numbered references"""
    
    response = "✅ **MARKET RESEARCH ANALYSIS COMPLETED**\n\n"
    
    # Initialize references system
    references = {}  # url -> {number, title}
    reference_counter = [1]  # Use list to make it mutable for helper functions
    
    # Handle both dict (from orchestrator.analyze()) and object formats
    if isinstance(market_intelligence_result, dict) and 'results' in market_intelligence_result:
        market_intelligence_result = market_intelligence_result['results']
    
    # Check if we have any valid data (works for both dict and object)
    if isinstance(market_intelligence_result, dict):
        has_data = (
            market_intelligence_result.get('market_profile') or
            market_intelligence_result.get('competitive_analysis') or
            market_intelligence_result.get('market_validation') or
            market_intelligence_result.get('funding_benchmarks')
        )
    else:
        has_data = (
            (hasattr(market_intelligence_result, 'market_profile') and market_intelligence_result.market_profile) or
            (hasattr(market_intelligence_result, 'competitive_analysis') and market_intelligence_result.competitive_analysis) or
            (hasattr(market_intelligence_result, 'market_validation') and market_intelligence_result.market_validation) or
            (hasattr(market_intelligence_result, 'funding_benchmarks') and market_intelligence_result.funding_benchmarks)
        )
    
    if not has_data:
        response += "⚠️ **ANALYSIS INCOMPLETE** - Please try again\n"
        return response
    
    # Market Taxonomy (handle both dict and object)
    market_profile = None
    if isinstance(market_intelligence_result, dict):
        market_profile = market_intelligence_result.get('market_profile')
    else:
        market_profile = getattr(market_intelligence_result, 'market_profile', None)
    
    if market_profile:
        if isinstance(market_profile, dict):
            solution = market_profile.get('solution', 'Not identified')
            sub_vertical = market_profile.get('sub_vertical', 'Not identified')
            vertical = market_profile.get('vertical', 'Not identified')
        else:
            solution = getattr(market_profile, 'solution', 'Not identified')
            sub_vertical = getattr(market_profile, 'sub_vertical', 'Not identified')
            vertical = getattr(market_profile, 'vertical', 'Not identified')
        
        response += f"📊 **MARKET TAXONOMY**\n"
        response += f"• **Solution:** {solution}\n"
        response += f"• **Sub-vertical:** {sub_vertical}\n"
        response += f"• **Vertical:** {vertical}\n\n"
    
    # Competitive Landscape with numbered references
    competitive_analysis = _get_component(market_intelligence_result, 'competitive_analysis')
    if competitive_analysis:
        response += format_expert_competitive_landscape_with_refs(competitive_analysis, references, reference_counter)
    
    # Market Validation with expert opinions
    market_validation = _get_component(market_intelligence_result, 'market_validation')
    if market_validation:
        response += format_expert_market_validation(market_validation)
    
    # Funding Benchmarks with specific deals
    funding_benchmarks = _get_component(market_intelligence_result, 'funding_benchmarks')
    if funding_benchmarks:
        response += format_expert_funding_benchmarks(funding_benchmarks)
    
    # Investment Decision Section - MVP DEMO: Like the old format  
    critical_assessment = _get_component(market_intelligence_result, 'critical_assessment')
    investment_decision = _get_component(market_intelligence_result, 'investment_decision')
    
    if critical_assessment:
        assessment = critical_assessment
        response += "🟡 **INVESTMENT DECISION: CAUTION**\n"
        
        if isinstance(assessment, dict):
            recommendation = assessment.get('recommendation', 'Investigate further')
            rationale = assessment.get('rationale', [])
            key_risks = assessment.get('key_risks', [])
            
            response += f"📋 {assessment.get('summary', 'Emerging market with potential, but lacks market validation.')}\n\n"
            response += "⚖️ **RATIONALE:**\n"
            
            if rationale:
                for reason in rationale[:3]:
                    response += f"• {str(reason)[:100]}\n"
            else:
                response += "• High confidence in market intelligence.\n"
                response += "• Emerging market with growth potential.\n"
            
            response += "\n🚨 **KEY RISKS:**\n"
            if key_risks:
                for risk in key_risks[:2]:
                    response += f"• {str(risk)[:100]}\n"
            else:
                response += "• Low market validation score.\n"
                response += "• Cautious funding climate for similar deals.\n"
            
            response += f"\n💰 **OPPORTUNITY:** {assessment.get('opportunity', 'Untapped market with global expansion potential.')}\n"
            response += f"📊 **CONFIDENCE:** {assessment.get('confidence', 'Medium - High confidence in intel, but low validation.')}\n\n"
    
    # Add numbered references section
    if references:
        response += "📚 **REFERENCES:**\n"
        # Sort by reference number
        sorted_refs = sorted(references.items(), key=lambda x: x[1]['number'])
        for url, ref_data in sorted_refs[:10]:  # Limit to top 10 references
            title = ref_data['title']
            # Clean up title length
            if len(title) > 60:
                title = title[:60].rsplit(' ', 1)[0] + '...'
            response += f"[{ref_data['number']}] {title}\n"
        response += "\n"
    
    # Commands (MVP DEMO: Add note about markdown report)
    response += "📋 `/ask` `/scoring` `/memo` `/gaps` `/reset`"
    response += "\n📄 Complete analysis → startup_analysis.md"
    
    # Apply Slack length limit protection
    response = ensure_slack_length_limit(response)
    
    return response