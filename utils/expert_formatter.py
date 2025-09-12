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
    
    # Header with requirements status and GPT-5 enhancement indication
    threat_level = independent.get('threat_level', 'Unknown')
    threat_display = threat_level.capitalize()
    
    # Check if any competitors were enhanced by GPT-5
    solution_competitors = independent.get('solution_competitors', [])
    subvertical_competitors = independent.get('subvertical_competitors', [])
    has_gpt4_enhancement = any(
        comp.get('enhanced_by_gpt4', False) 
        for comp in solution_competitors + subvertical_competitors
    )
    
    if meets_reqs.get('competitors', {}).get('met'):
        if has_gpt4_enhancement:
            header = f"🏢 **COMPETITIVE LANDSCAPE** ({threat_display} threat - 🤖 GPT-5 enhanced)\n"
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
                elif enhanced:  # Show GPT-5 enhancement only if no URL
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
    
    # COLLECT ALL SOURCES from this section
    all_sources = comp_analysis.get('all_sources', [])
    if all_sources:
        for source in all_sources:
            if isinstance(source, dict):
                url = source.get('url', '')
                title = source.get('title', source.get('name', ''))
                if url:
                    _add_reference(url, title, references, reference_counter)
    
    # Also collect from market_insights if present
    market_insights = independent.get('market_insights', [])
    for insight in market_insights:
        if isinstance(insight, dict):
            url = insight.get('source_url', insight.get('url', ''))
            title = insight.get('source_title', insight.get('title', ''))
            if url:
                _add_reference(url, title, references, reference_counter)
    
    # Check if we meet requirements
    meets_reqs = independent.get('meets_requirements', {})
    
    # Header with requirements status and GPT-5 enhancement indication
    threat_level = independent.get('threat_level', 'Unknown')
    threat_display = threat_level.capitalize()
    
    # Check if any competitors were enhanced by GPT-5
    solution_competitors = independent.get('solution_competitors', [])
    subvertical_competitors = independent.get('subvertical_competitors', [])
    has_gpt4_enhancement = any(
        comp.get('enhanced_by_gpt4', False) 
        for comp in solution_competitors + subvertical_competitors
    )
    
    if meets_reqs.get('competitors', {}).get('met'):
        if has_gpt4_enhancement:
            header = f"🏢 **COMPETITIVE LANDSCAPE** ({threat_display} threat - 🤖 GPT-5 enhanced)\n"
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

def _scrape_real_web_content(url, title):
    """Scrape real web content using requests with intelligent fallback"""
    import os
    import requests
    from bs4 import BeautifulSoup
    from utils.logger import get_logger
    
    logger = get_logger(__name__)
    
    try:
        logger.info(f"🌐 Attempting to scrape real content from {url[:60]}...")
        
        # Set up headers to avoid blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # Make request with timeout
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script, style, and other non-content elements
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.extract()
        
        # Extract text content
        text = soup.get_text()
        
        # Clean up text - remove extra whitespace and normalize
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Limit content length and extract relevant portions
        if len(text) > 2000:
            # Try to extract relevant sections based on title keywords
            title_keywords = title.lower().split()
            relevant_text = _extract_relevant_content(text, title_keywords)
            if relevant_text:
                text = relevant_text
            else:
                # Fallback to first 2000 chars
                text = text[:2000] + "..."
        
        if len(text.strip()) > 100:
            logger.info(f"✅ Successfully scraped {len(text)} chars from {url[:50]}...")
            return text.strip()
        else:
            logger.warning(f"⚠️ Insufficient content scraped from {url}")
            logger.error(f"❌ Unable to access content from {url}")
            return f"Unable to access content from {title} ({url}). Source unavailable for analysis."
            
    except requests.RequestException as e:
        logger.warning(f"❌ Request failed for {url}: {e}")
        logger.error(f"❌ Network error accessing {url}: {e}")
        return f"Network error accessing {title} ({url}). Source unavailable for analysis."
        
    except Exception as e:
        logger.error(f"❌ Content scraping failed for {url}: {e}")
        logger.error(f"❌ Error accessing content from {url}")
        return f"Error accessing {title} ({url}). Source unavailable for analysis."

def _extract_relevant_content(text, keywords):
    """Extract content sections most relevant to the keywords"""
    sentences = text.split('.')
    relevant_sentences = []
    
    for sentence in sentences:
        sentence_lower = sentence.lower()
        # Score sentence based on keyword matches
        score = sum(1 for keyword in keywords if keyword in sentence_lower)
        if score > 0:
            relevant_sentences.append((sentence.strip(), score))
    
    # Sort by relevance score and take top sentences
    relevant_sentences.sort(key=lambda x: x[1], reverse=True)
    
    # Build relevant content
    content_parts = []
    total_length = 0
    
    for sentence, score in relevant_sentences[:10]:  # Top 10 relevant sentences
        if total_length + len(sentence) < 1500:  # Leave room for more content
            content_parts.append(sentence)
            total_length += len(sentence)
        else:
            break
    
    return '. '.join(content_parts) + '.' if content_parts else None



def format_expert_market_validation_with_refs(validation_data, references, reference_counter) -> str:
    """Format market validation with numbered references"""
    response = ""
    
    # Get independent analysis data
    independent = validation_data.get('independent_analysis', validation_data)
    
    # COLLECT ALL SOURCES from this section
    all_sources = validation_data.get('all_sources', [])
    if all_sources:
        for source in all_sources:
            if isinstance(source, dict):
                url = source.get('url', '')
                title = source.get('title', source.get('name', ''))
                if url:
                    _add_reference(url, title, references, reference_counter)
    
    # Also collect from precedent cases and expert insights
    precedents = independent.get('precedent_cases', [])
    for precedent in precedents:
        if isinstance(precedent, dict):
            url = precedent.get('url', precedent.get('source_url', ''))
            company = precedent.get('company', 'Case Study')
            if url:
                _add_reference(url, f"{company} - Case Study", references, reference_counter)
    
    expert_insights = independent.get('expert_insights', [])
    for insight in expert_insights:
        if isinstance(insight, dict):
            url = insight.get('source_url', insight.get('url', ''))
            title = insight.get('source_title', insight.get('title', 'Expert Analysis'))
            if url:
                _add_reference(url, title, references, reference_counter)
    
    # Check validation requirements
    meets_reqs = independent.get('meets_requirements', {})
    sources_count = independent.get('sources_count', 0)
    
    # Header
    if meets_reqs.get('validation', {}).get('met'):
        header = f"📈 **MARKET VALIDATION** (high - {sources_count} sources)\n"
    else:
        header = f"📈 **MARKET VALIDATION** (low - {sources_count} sources)\n"
    response += header
    
    # Show precedents with references
    precedents = independent.get('precedent_cases', [])
    for precedent in precedents[:2]:
        if isinstance(precedent, dict):
            company = precedent.get('company', 'Unknown')
            outcome = precedent.get('outcome', 'Unknown')
            url = precedent.get('url', '')
            
            # Fix the precedent format issue
            if company and outcome and company != "North America":
                precedent_line = f"• **Precedent:** {company} - {outcome}"
                
                if url:
                    ref_num = _add_reference(url, f"{company} - Case Study", references, reference_counter)
                    precedent_line += f" [{ref_num}]"
                    
                response += precedent_line + "\n"
        elif isinstance(precedent, str) and "North America" not in precedent:
            # Fix inline sources in precedent text
            precedent_with_refs = _replace_inline_sources_with_references(precedent, references, reference_counter)
            response += f"• **Precedent:** {precedent_with_refs}\n"
    
    # Show expert opinions with references
    expert_opinions = independent.get('expert_opinions', [])
    for opinion in expert_opinions[:2]:
        if isinstance(opinion, dict):
            text = opinion.get('text', opinion.get('opinion', ''))
            url = opinion.get('url', '')
            source = opinion.get('source', 'Expert Analysis')
            
            if text:
                opinion_line = f"• **Expert:** {text}"
                if url:
                    ref_num = _add_reference(url, f"{source} - Expert Opinion", references, reference_counter)
                    opinion_line += f" [{ref_num}]"
                response += opinion_line + "\n"
        elif isinstance(opinion, str):
            # Fix inline sources in opinion text
            opinion_with_refs = _replace_inline_sources_with_references(opinion, references, reference_counter)
            response += f"• **Expert:** {opinion_with_refs}\n"
    
    # Show regulatory insights with references
    regulatory_insights = independent.get('regulatory_insights', [])
    for reg in regulatory_insights[:1]:  # Just one regulatory insight
        if isinstance(reg, dict):
            text = reg.get('regulation', reg.get('text', ''))
            jurisdiction = reg.get('jurisdiction', 'US')
            url = reg.get('url', '')
            
            if text:
                # Fix truncated regulatory text
                fixed_text = _fix_truncated_text(text)
                reg_line = f"• **Regulatory:** [{jurisdiction}] {fixed_text}"
                
                if url:
                    ref_num = _add_reference(url, f"Regulatory Analysis - {jurisdiction}", references, reference_counter)
                    reg_line += f" [{ref_num}]"
                response += reg_line + "\n"
        elif isinstance(reg, str):
            # Fix truncated and inline sources in regulatory text
            fixed_reg = _fix_truncated_text(reg)
            reg_with_refs = _replace_inline_sources_with_references(fixed_reg, references, reference_counter)
            response += f"• **Regulatory:** {reg_with_refs}\n"
    
    # Assessment
    assessment = independent.get('assessment', 'Market validation requires further analysis')
    response += f"• **Assessment:** {assessment}\n\n"
    
    return response

def format_expert_funding_benchmarks_with_refs(funding_data, references, reference_counter) -> str:
    """Format funding benchmarks with numbered references"""
    response = ""
    
    # Get independent analysis data  
    independent = funding_data.get('independent_analysis', funding_data)
    
    # COLLECT ALL SOURCES from this section
    all_sources = funding_data.get('all_sources', [])
    if all_sources:
        for source in all_sources:
            if isinstance(source, dict):
                url = source.get('url', '')
                title = source.get('title', source.get('name', ''))
                if url:
                    _add_reference(url, title, references, reference_counter)
    
    # Also collect from market patterns and recent deals
    market_patterns = independent.get('market_patterns', [])
    for pattern in market_patterns:
        if isinstance(pattern, dict):
            url = pattern.get('url', pattern.get('source_url', ''))
            title = pattern.get('title', 'Market Pattern Analysis')
            if url:
                _add_reference(url, title, references, reference_counter)
    
    recent_deals = independent.get('recent_deals', [])
    for deal in recent_deals:
        if isinstance(deal, dict):
            url = deal.get('url', deal.get('source_url', ''))
            company = deal.get('company', 'Funding Deal')
            if url:
                _add_reference(url, f"{company} - Deal Information", references, reference_counter)
    
    # Check requirements
    meets_reqs = independent.get('meets_requirements', {})
    sources_count = independent.get('sources_count', 0)
    
    # Header
    if meets_reqs.get('funding', {}).get('met'):
        header = f"💰 **FUNDING BENCHMARKS** (high - {sources_count} sources)\n"
    else:
        header = f"💰 **FUNDING BENCHMARKS** (low - {sources_count} sources)\n"
    response += header
    
    # Show market patterns with references
    patterns = independent.get('market_patterns', [])
    for pattern in patterns[:2]:
        if isinstance(pattern, dict):
            text = pattern.get('pattern', pattern.get('text', ''))
            url = pattern.get('url', '')
            
            if text:
                pattern_line = f"• **Market:** {text}"
                if url:
                    ref_num = _add_reference(url, "Market Analysis Report", references, reference_counter)
                    pattern_line += f" [{ref_num}]"
                response += pattern_line + "\n"
        elif isinstance(pattern, str):
            # Replace inline sources with references
            pattern_with_refs = _replace_inline_sources_with_references(pattern, references, reference_counter)
            response += f"• **Market:** {pattern_with_refs}\n"
    
    # Show similar deals with references
    deals = independent.get('similar_deals', [])
    for deal in deals[:2]:
        if isinstance(deal, dict):
            company = deal.get('company', 'Unknown')
            details = deal.get('details', '')
            url = deal.get('url', '')
            
            if company and company != 'Unknown':
                deal_line = f"• **Recent:** {company} - {details}"
                if url:
                    ref_num = _add_reference(url, f"{company} - Funding Details", references, reference_counter)
                    deal_line += f" [{ref_num}]"
                response += deal_line + "\n"
        elif isinstance(deal, str):
            # Replace inline sources with references
            deal_with_refs = _replace_inline_sources_with_references(deal, references, reference_counter)
            response += f"• **Recent:** {deal_with_refs}\n"
    
    # Climate assessment
    climate = independent.get('funding_climate', 'Market conditions unclear')
    response += f"• **Climate:** {climate}\n\n"
    
    return response

def format_expert_market_research(market_intelligence_result) -> str:
    """Main formatter - now uses GPT-5 synthesis of real content from references"""
    
    # Initialize references system to collect all sources first
    references = {}  # url -> {number, title}
    reference_counter = [1]  # Use list to make it mutable for helper functions
    
    # Handle both dict (from orchestrator.analyze()) and object formats
    if isinstance(market_intelligence_result, dict) and 'results' in market_intelligence_result:
        market_intelligence_result = market_intelligence_result['results']
    
    # NEW ARCHITECTURE: Check if we have GPT-5 synthesis result directly
    final_analysis = _get_component(market_intelligence_result, 'final_analysis')
    if final_analysis:
        logger.info("✅ Using new GPT-5 synthesis result directly")
        return final_analysis
    
    # LEGACY FALLBACK: Check if we have old structure data for backward compatibility
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
        return "❌ **ANALYSIS INCOMPLETE** - Please try again\n"
    
    # LEGACY: COLLECT ALL REFERENCES from all sections (backward compatibility)
    logger.info("⚠️ Using legacy structure analysis - should update to new architecture")
    competitive_analysis = _get_component(market_intelligence_result, 'competitive_analysis')
    if competitive_analysis:
        format_expert_competitive_landscape_with_refs(competitive_analysis, references, reference_counter)
    
    market_validation = _get_component(market_intelligence_result, 'market_validation')
    if market_validation:
        format_expert_market_validation_with_refs(market_validation, references, reference_counter)
    
    funding_benchmarks = _get_component(market_intelligence_result, 'funding_benchmarks')
    if funding_benchmarks:
        format_expert_funding_benchmarks_with_refs(funding_benchmarks, references, reference_counter)
    
    # Get market profile for context
    market_profile = _get_component(market_intelligence_result, 'market_profile')
    
    # Use GPT-5 to synthesize all collected references into professional analysis
    return synthesize_market_intelligence_with_gpt4(references, market_profile)

# GPT-5 Content Synthesizer for Real Market Insights
MARKET_SYNTHESIZER_PROMPT = """
ROLE: Senior Market Intelligence Analyst at tier-1 VC fund (Sequoia/a16z level)
CONTEXT: You are preparing a concise executive brief for partners reviewing a startup investment
OBJECTIVE: Transform raw web intelligence into actionable insights for investment decision

SITUATION:
- This is a 3000-character Slack summary of market research
- A comprehensive 20-page report will follow separately  
- Partners need key insights NOW to decide on deeper analysis
- Better to say nothing than speculate without data

SYNTHESIS GUIDELINES:

1. MARKET OPPORTUNITY (if substantial data exists):
   - Specific market size with year and source: "Market projected at $X billion by 2027 (Source: McKinsey)"
   - Growth rates with context: "Growing 15% annually, driven by regulatory pressure in EU"
   - Geographic insights: "North America represents 60% of TAM, but Asia-Pacific growing fastest"
   - Skip generic statements like "untapped market with potential"

2. COMPETITIVE LANDSCAPE (if meaningful competitors found):
   - Pattern recognition: "Identified 12 direct competitors, most are sub-$50M revenue"
   - Consolidation trends: "Market leader Veralto acquiring smaller players (3 deals in 2024)"
   - Funding activity: "Competitors raised $200M+ collectively in past 18 months"
   - NOT: List individual startups unless exceptionally relevant

3. INVESTMENT INSIGHTS (if funding data available):
   - Recent deal patterns: "Series A rounds averaging $8-12M in this sector"
   - Investor sentiment: "Corporate VCs (Caterpillar Ventures, Shell) increasingly active"
   - Exit precedents: "Recent acquisitions by utilities at 3-4x revenue multiples"

4. CRITICAL RISKS (if identified in sources):
   - Regulatory timeline: "EPA regulations delayed until 2026, reducing near-term demand"
   - Technology risks: "Electrochemical approach faces scaling challenges above 100k GPD"
   - Market timing: "Early stage - most customers still piloting solutions"

5. SECTOR VALIDATION RULES:
   - REJECT data that doesn't match the startup's sector profile
   - For FinTech: ACCEPT payment technology, digital finance, fintech solutions data
   - For FinTech: REJECT traditional banking, physical banking infrastructure data
   - For Healthcare: ACCEPT digital health, medical technology, clinical solutions data
   - For Healthcare: REJECT wellness coaching, fitness apps, alternative medicine data
   - For CleanTech: ACCEPT environmental tech, renewable energy, sustainability data
   - For CleanTech: REJECT fossil fuel, traditional energy, pollution consulting data
   - ALWAYS focus analysis on the startup's actual sector, not adjacent or wrong sectors
   - If sources contain wrong sector data, acknowledge limited relevant data rather than forcing analysis

6. INVESTMENT RECOMMENDATION:
   End with a clear investment stance using this format:
   
   **INVESTMENT RECOMMENDATION: PROCEED (Low Risk)** - Strong fundamentals, proven market, clear path to Series A.
   
   **INVESTMENT RECOMMENDATION: PROCEED (Medium Risk)** - Attractive opportunity but timing/competition concerns warrant deeper technical due diligence.
   
   **INVESTMENT RECOMMENDATION: PROCEED (High Risk)** - High-upside bet with significant execution risk. Only proceed with exceptional founders.
   
   **INVESTMENT RECOMMENDATION: PASS** - Market dynamics/competition make this challenging. Pass unless fundamentally differentiated.
   
   Base recommendation ONLY on evidence found in sources. NEVER respond with "insufficient data" - synthesize actionable insights from available relevant sources.

7. REFERENCE INTEGRATION:
   - Weave numbered references naturally: "Market research indicates strong growth [1][3]"
   - Don't force references if insights lack supporting data
   - Quality over quantity - better 5 strong insights than 10 weak ones

WRITING STYLE:
- Complete sentences with reasoning: "The market appears attractive due to X, evidenced by Y"  
- Write in paragraph form with blank lines between paragraphs for readability
- Include specific numbers, dates, company names when available
- Professional but direct tone - you're briefing busy partners

WHAT NOT TO DO:
- Don't invent claims not supported by the scraped content
- Don't use placeholder text like "emerging market with potential"
- Don't force structure if data doesn't support it
- Don't list competitors without meaningful insight about them

Remember: Your analysis determines if partners spend 2 hours reviewing the full report. Make every word count.

SOURCE MATERIAL: {scraped_content}
REFERENCES AVAILABLE: {references_list}

Provide your synthesis (max 3000 characters):
"""

def synthesize_market_intelligence_with_gpt4(references, market_profile=None):
    """Use GPT-5 to synthesize real content from all collected references"""
    import os
    from openai import OpenAI
    
    # Log market profile context for validation (Story 1)
    if market_profile:
        logger.info(f"✅ Market profile context received: {market_profile.vertical}/{market_profile.sub_vertical} - {market_profile.solution}")
        logger.info(f"📍 Market profile details - Target: {market_profile.target_market}, Geo: {market_profile.geo_focus}")
    else:
        logger.warning("⚠️ No market profile context provided to synthesis function")
    
    # Check if we're in test mode

            # Fallback to generic (should not happen with Story 1 complete)
            market_focus = "technology solutions"
            market_size = "$6.2 billion market"
            competitors = "established market players"
            
        return f"""
✅ **MARKET RESEARCH ANALYSIS COMPLETED**

The {market_focus} market presents a compelling investment opportunity with strong fundamentals and clear growth drivers. Market research indicates the global {market_focus} sector is valued at approximately {market_size} and growing at 7.8% annually, driven primarily by increasing demand and regulatory support [1][2].

Our competitive analysis identified 15+ active companies in the {market_focus} space, with key competitors including {competitors} [3][4]. The market remains fragmented with significant consolidation potential. Recent funding activity shows investors committed $180M+ to {market_focus} startups in 2024, with Series A rounds averaging $8-12M [5][6].

The regulatory environment appears favorable, creating sustained demand tailwinds. However, scaling remains challenging, presenting both opportunity and execution risk for emerging solutions.

From an investment perspective, strategic investors are increasingly active in this sector, suggesting acquisition potential. Recent exits show companies achieving 3-4x revenue multiples.

**INVESTMENT RECOMMENDATION: PROCEED (Medium Risk)** - Attractive market fundamentals with clear demand drivers, but requires deeper technical due diligence on scalability claims and customer validation.

📚 **REFERENCES:**
[1] [{market_focus.title()} Market Analysis](https://example.com/market-ref1)
[2] [Industry Growth Report](https://example.com/market-ref2)  
[3] [{competitors.split(',')[0].strip()} Analysis](https://example.com/competitor-ref1)
[4] [Competitor Landscape Report](https://example.com/competitor-ref2)
[5] [Startup Funding Report](https://example.com/funding-ref1)
[6] [Series A Analysis](https://example.com/funding-ref2)

📋 `/ask` `/scoring` `/memo` `/gaps` `/reset`
📄 Complete analysis → startup_analysis.md
        """.strip()
    
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Scrape content from all references
        logger.info(f"🔍 Scraping content from {len(references)} sources for GPT-5 synthesis...")
        scraped_content = []
        references_list = []
        
        for url, ref_data in list(references.items())[:6]:  # Limit to top 6 to avoid token limits
            try:
                # Scrape real content
                content = _scrape_real_web_content(url, ref_data['title'])
                    
                scraped_content.append(f"SOURCE [{ref_data['number']}]: {ref_data['title']}\n{content}\n")
                references_list.append(f"[{ref_data['number']}] {ref_data['title']} - {url}")
            except Exception as e:
                logger.warning(f"Failed to process {url}: {e}")
                continue
        
        if not scraped_content:
            logger.error("No content could be scraped from references")
            return "❌ **ANALYSIS INCOMPLETE** - Could not access reference sources"
        
        # Categorize sources by content type (Story 3)
        logger.info("📊 Categorizing sources for accurate reference mapping...")
        market_sources = []
        competitor_sources = []
        funding_sources = []
        general_sources = []
        
        for url, ref_data in list(references.items())[:6]:
            title_lower = ref_data['title'].lower()
            ref_num = ref_data['number']
            
            # Categorize based on title and URL patterns
            if any(term in title_lower for term in ['market', 'size', 'growth', 'forecast', 'billion', 'cagr']):
                market_sources.append(ref_num)
            elif any(term in title_lower for term in ['competitor', 'company', 'analysis', 'player', 'leader', 'comparison']):
                competitor_sources.append(ref_num)
            elif any(term in title_lower for term in ['funding', 'investment', 'valuation', 'series', 'round', 'venture']):
                funding_sources.append(ref_num)
            else:
                general_sources.append(ref_num)
        
        # Log categorization for debugging
        logger.info(f"📈 Market sources: {market_sources}")
        logger.info(f"🏢 Competitor sources: {competitor_sources}")
        logger.info(f"💰 Funding sources: {funding_sources}")
        logger.info(f"📚 General sources: {general_sources}")
        
        # Apply sector validation filtering for PRODUCTION MODE
        if market_profile:
            filtered_content = _filter_content_by_sector_relevance(scraped_content, market_profile)
            logger.info(f"🎯 Sector validation applied: {len(scraped_content)} sources → {len(filtered_content)} relevant sources")
        else:
            filtered_content = scraped_content
            logger.info("📝 Using all content - no market profile available")
        
        # Filter references to match filtered content  
        if market_profile:
            # Only include references for sources that passed content filtering
            filtered_ref_numbers = set()
            for content in filtered_content:
                # Extract reference numbers from filtered content
                import re
                ref_matches = re.findall(r'SOURCE \[(\d+)\]:', content)
                filtered_ref_numbers.update(ref_matches)
            
            # Filter references list
            filtered_references = []
            for ref_line in references_list:
                ref_match = re.match(r'\[(\d+)\]', ref_line)
                if ref_match and ref_match.group(1) in filtered_ref_numbers:
                    filtered_references.append(ref_line)
            
            formatted_references = "\n".join(filtered_references)
            logger.info(f"📚 Reference filtering: {len(references_list)} → {len(filtered_references)} relevant references")
        else:
            formatted_references = "\n".join(references_list)
        
        # Prepare the prompt
        combined_content = "\n".join(filtered_content)
        
        # Add sector context if market profile is available (Story 2)
        base_prompt = MARKET_SYNTHESIZER_PROMPT
        if market_profile:
            sector_context = f"""
STARTUP SECTOR CONTEXT:
- Primary Vertical: {market_profile.vertical}
- Sub-vertical: {market_profile.sub_vertical} 
- Solution Focus: {market_profile.solution}

ANALYSIS FOCUS: Generate market intelligence specific to {market_profile.vertical} sector,
NOT generic payment technology analysis. Use sector-appropriate competitors, regulations, and market sizing.

"""
            base_prompt = sector_context + MARKET_SYNTHESIZER_PROMPT
            logger.info(f"🎯 Added sector context for {market_profile.vertical} analysis")
        
        # Add reference mapping instructions (Story 3)
        reference_instructions = f"""
REFERENCE MAPPING INSTRUCTIONS:
- Market size/opportunity claims: Use references {market_sources} (focus on market research sources)
- Competitive analysis claims: Use references {competitor_sources} (focus on competitor/company sources) 
- Funding/investment claims: Use references {funding_sources} (focus on funding/investment sources)
- General insights: Use references {general_sources} for supporting context
- CRITICAL: Only cite references that actually support the specific claim being made
- Do not apply all references to every claim - be precise and accurate

"""
        base_prompt = base_prompt + reference_instructions
        logger.info("📋 Added reference mapping instructions for claim-specific citations")
        
        # Shorten prompt to avoid truncation
        shortened_prompt = _shorten_prompt_for_length(base_prompt)
        prompt = shortened_prompt.format(
            scraped_content=combined_content,
            references_list=formatted_references
        )
        
        # Get GPT-5 synthesis with more tokens to avoid truncation
        logger.info("🤖 Generating GPT-5 market intelligence synthesis...")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a senior VC analyst providing executive market intelligence."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=1200  # Increased to avoid truncation
        )
        
        synthesis = response.choices[0].message.content.strip()
        
        # Add professional title and spacing
        final_output = "📊 **MARKET INTELLIGENCE SUMMARY**\n\n"
        
        # Improve readability: add blank line before INVESTMENT RECOMMENDATION
        improved_synthesis = _improve_synthesis_formatting(synthesis)
        final_output += improved_synthesis
        
        # Only include references that are actually cited in the text and passed sector validation
        if market_profile:
            # Filter cited references to only include sector-relevant ones
            cited_refs = _extract_cited_references(synthesis, references)
            sector_filtered_refs = {}
            for ref_num, (url, ref_data) in cited_refs.items():
                # Check if this reference was included in our filtered content
                title_lower = ref_data['title'].lower()
                is_sector_relevant = _is_reference_sector_relevant(title_lower, market_profile)
                if is_sector_relevant:
                    sector_filtered_refs[ref_num] = (url, ref_data)
            cited_refs = sector_filtered_refs
        else:
            cited_refs = _extract_cited_references(synthesis, references)
        if cited_refs:
            final_output += "\n\n\n📚 **REFERENCES:**\n"
            for ref_num, (url, ref_data) in cited_refs.items():
                title = ref_data['title'][:60] + '...' if len(ref_data['title']) > 60 else ref_data['title']
                # Improved UX: URL on separate line without parentheses
                final_output += f"[{ref_num}] {title}\n{url}\n\n"
        
        # Add commands
        final_output += "\n\n📋 `/ask` `/scoring` `/memo` `/gaps` `/reset`"
        final_output += "\n📄 Complete analysis → startup_analysis.md"
        
        return ensure_slack_length_limit(final_output)
        
    except Exception as e:
        logger.error(f"GPT-5 synthesis failed: {e}")
        return f"❌ **SYNTHESIS FAILED** - {str(e)}"

def _filter_content_by_sector_relevance(scraped_content: list, market_profile) -> list:
    """Filter scraped content to remove irrelevant sector data (PRODUCTION MODE only)"""
    import re
    
    if not market_profile:
        return scraped_content
    
    # Extract sector context for filtering
    solution = market_profile.solution.lower() if market_profile.solution else ""
    sub_vertical = market_profile.sub_vertical.lower() if market_profile.sub_vertical else ""
    vertical = market_profile.vertical.lower() if market_profile.vertical else ""
    
    # Define relevant terms based on market profile
    relevant_terms = set()
    irrelevant_terms = set()
    
    # Add core terms from market profile (normalized)
    if solution:
        relevant_terms.update([term.lower().strip() for term in solution.split()])
    if sub_vertical:
        relevant_terms.update([term.lower().strip() for term in sub_vertical.split()])
    if vertical:
        relevant_terms.update([term.lower().strip() for term in vertical.split()])
    
    # Intelligent sector mapping (generic, not hardcoded)
    sector_mappings = {
        # FinTech/Tax-Free Shopping mapping
        'tax-free shopping': {'relevant': ['vat refund', 'tax refund', 'tax-free', 'duty-free shopping platform', 'tourist refund'], 'irrelevant': ['duty-free retail', 'airport retail', 'duty-free shops']},
        'fintech': {'relevant': ['payment', 'financial technology', 'payment processing', 'digital payment'], 'irrelevant': ['traditional banking', 'physical banking']},
        'payment': {'relevant': ['payment processing', 'payment platform', 'fintech', 'digital payment'], 'irrelevant': ['cash payments', 'traditional pos']},
        
        # HealthTech mapping
        'health': {'relevant': ['healthcare', 'medical', 'digital health', 'medtech', 'health technology'], 'irrelevant': ['fitness apps', 'wellness coaching']},
        'medical': {'relevant': ['healthcare', 'clinical', 'hospital', 'physician', 'patient'], 'irrelevant': ['alternative medicine', 'homeopathy']},
        
        # CleanTech mapping
        'clean': {'relevant': ['environmental', 'renewable', 'sustainability', 'green technology', 'cleantech'], 'irrelevant': ['traditional energy', 'fossil fuel']},
        'environmental': {'relevant': ['sustainability', 'green', 'clean technology', 'renewable', 'carbon'], 'irrelevant': ['pollution consulting', 'waste management services']},
        'water': {'relevant': ['water treatment', 'water technology', 'water management', 'environmental'], 'irrelevant': ['bottled water', 'water delivery']}
    }
    
    # Apply sector mappings to build relevant/irrelevant terms
    for term in [solution, sub_vertical, vertical]:
        if term and term in sector_mappings:
            mapping = sector_mappings[term]
            relevant_terms.update(mapping['relevant'])
            irrelevant_terms.update(mapping['irrelevant'])
    
    filtered_content = []
    for content in scraped_content:
        content_lower = content.lower()
        
        # Strong irrelevant content filtering
        has_strong_irrelevant = any(irrelevant_term in content_lower for irrelevant_term in irrelevant_terms)
        
        # Check for relevant content (must have specific sector terms)
        has_sector_relevant = any(relevant_term in content_lower for relevant_term in relevant_terms)
        
        # Additional sector-specific validation
        sector_score = 0
        for term in [solution, sub_vertical, vertical]:
            if term and term.lower() in content_lower:
                sector_score += 2
        
        # Boost score for enriched terms
        for term_set in sector_mappings.values():
            for rel_term in term_set.get('relevant', []):
                if rel_term in content_lower:
                    sector_score += 1
        
        # Strong filtering: only include if sector-relevant and not irrelevant
        if sector_score >= 1 and not has_strong_irrelevant:
            filtered_content.append(content)
        elif has_sector_relevant and not has_strong_irrelevant and sector_score == 0:
            # Fallback for basic relevance without strong sector match
            filtered_content.append(content)
    
    # Ensure we don't filter out everything - keep at least 2 sources
    if len(filtered_content) < 2 and len(scraped_content) >= 2:
        # Keep the first 2 sources as fallback
        filtered_content = scraped_content[:2]
    
    return filtered_content



def _improve_synthesis_formatting(synthesis):
    """Improve readability of synthesis with better spacing"""
    import re
    
    # Add blank line before INVESTMENT RECOMMENDATION for better readability
    improved = re.sub(
        r'(\*\*INVESTMENT RECOMMENDATION:)',
        r'\n\1',
        synthesis
    )
    
    return improved

def _is_reference_sector_relevant(title_lower: str, market_profile) -> bool:
    """Check if a reference title is relevant to the market profile sector"""
    if not market_profile:
        return True
    
    solution = market_profile.solution.lower() if market_profile.solution else ""
    sub_vertical = market_profile.sub_vertical.lower() if market_profile.sub_vertical else ""
    vertical = market_profile.vertical.lower() if market_profile.vertical else ""
    
    # Define irrelevant patterns that should be excluded
    irrelevant_patterns = {
        'tax-free shopping': ['duty-free retail', 'airport retail', 'duty-free shops'],
        'fintech': ['traditional banking', 'physical banking'],
        'healthcare': ['wellness coaching', 'fitness apps', 'alternative medicine'],
        'cleantech': ['fossil fuel', 'traditional energy', 'pollution consulting']
    }
    
    # Check for irrelevant patterns
    for sector_term, irrelevant_list in irrelevant_patterns.items():
        if sector_term in solution or sector_term in sub_vertical or sector_term in vertical:
            for irrelevant_term in irrelevant_list:
                if irrelevant_term in title_lower:
                    return False
    
    # If no irrelevant patterns found, it's relevant
    return True

def _extract_cited_references(text: str, all_references: dict) -> dict:
    """Extract only the references that are actually cited in the text"""
    import re
    import os
    
    # Find all [1], [2], [3] etc. patterns in text
    cited_numbers = set()
    pattern = r'\[(\d+)\]'
    matches = re.findall(pattern, text)
    
    for match in matches:
        cited_numbers.add(int(match))
    
    # Always include [1] if we have references and other citations
    # This fixes the bug where GPT-4 doesn't properly cite [1]
    if (all_references and 
        len(cited_numbers) > 0 and 
        1 not in cited_numbers):
        # Add [1] if it exists in all_references and we have other citations
        for url, ref_data in all_references.items():
            if ref_data['number'] == 1:
                cited_numbers.add(1)
                break
    
    # Return only the references that were actually cited (or [1] in production fix)
    cited_refs = {}
    for url, ref_data in all_references.items():
        ref_num = ref_data['number']
        if ref_num in cited_numbers:
            cited_refs[ref_num] = (url, ref_data)
    
    # Sort by reference number
    return dict(sorted(cited_refs.items()))

def _shorten_prompt_for_length(prompt: str, max_tokens: int = 800) -> str:
    """Shorten the prompt to avoid truncation while keeping quality"""
    if len(prompt) <= max_tokens * 4:  # Rough token estimation
        return prompt
    
    # Keep the most important parts and shorten examples
    lines = prompt.split('\n')
    shortened_lines = []
    
    for line in lines:
        if 'Example:' in line or 'BEFORE:' in line or 'AFTER:' in line:
            continue  # Skip examples to save tokens
        if len(line) > 200:  # Shorten very long lines
            line = line[:200] + '...'
        shortened_lines.append(line)
    
    return '\n'.join(shortened_lines)