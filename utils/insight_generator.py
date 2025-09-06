"""
Intelligent Insight Generator
Uses competitive data to generate actionable insights for VC analysts

Focus: Transform raw competitive data into strategic insights
"""

import os
from typing import List, Dict, Any
from utils.logger import get_logger

logger = get_logger(__name__)

def generate_market_insights(competitive_data: Dict, market_profile: Dict) -> Dict[str, List[str]]:
    """
    Generate intelligent market insights from competitive data
    
    Args:
        competitive_data: Processed competitive intelligence
        market_profile: Market taxonomy and positioning
        
    Returns:
        Dict with 'opportunities' and 'risks' lists
    """
    try:
        logger.info("🧠 Generating intelligent market insights")
        
        # Check if we should use GPT-5 or provide heuristic insights
        if os.getenv('TEST_MODE', 'false').lower() == 'true':
            return _generate_mock_insights(competitive_data, market_profile)
        
        # Use GPT-5 to generate real insights
        return _generate_ai_insights(competitive_data, market_profile)
        
    except Exception as e:
        logger.error(f"❌ Insight generation failed: {e}")
        return {
            'opportunities': ['Market insights unavailable - analysis error'],
            'risks': ['Risk assessment unavailable - analysis error']
        }

def _generate_mock_insights(competitive_data: Dict, market_profile: Dict) -> Dict[str, List[str]]:
    """Generate contextual mock insights for testing"""
    solution = market_profile.get('solution', 'solution')
    vertical = market_profile.get('vertical', 'market')
    
    opportunities = [
        f"Growing regulatory pressure in {vertical} creating market opportunity",
        f"Established players may be slow to adopt new {solution} technology",
        f"Consolidation trend in industry creating acquisition potential"
    ]
    
    risks = [
        f"Incumbent players have established relationships and deep pockets",
        f"Regulatory approval for {solution} may be complex and time-consuming", 
        f"Market fragmentation could limit scalability and growth potential"
    ]
    
    return {'opportunities': opportunities, 'risks': risks}

def _generate_ai_insights(competitive_data: Dict, market_profile: Dict) -> Dict[str, List[str]]:
    """Generate AI-powered insights using GPT-5"""
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Prepare context for GPT-5
        context = _build_insight_context(competitive_data, market_profile)
        
        prompt = f"""You are a senior VC analyst reviewing market intelligence for investment decisions.

COMPETITIVE CONTEXT:
{context}

Analyze this competitive landscape and provide:

1. TOP 3 MARKET OPPORTUNITIES (specific, actionable insights)
2. TOP 3 MARKET RISKS (realistic threats to consider)

Requirements:
- Each insight should be 1-2 sentences maximum
- Focus on strategic implications for investment decisions
- Be specific to this market/solution, not generic
- Consider competitive dynamics, regulatory factors, market timing
- Write for a sophisticated VC audience

Format:
OPPORTUNITIES:
- [Specific opportunity with strategic rationale]
- [Specific opportunity with strategic rationale]  
- [Specific opportunity with strategic rationale]

RISKS:
- [Specific risk with impact assessment]
- [Specific risk with impact assessment]
- [Specific risk with impact assessment]"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert VC analyst focused on competitive intelligence and market dynamics."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3
        )
        
        # Parse GPT-5 response
        content = response.choices[0].message.content
        return _parse_insight_response(content)
        
    except Exception as e:
        logger.error(f"❌ AI insight generation failed: {e}")
        # Fallback to heuristic insights
        return _generate_heuristic_insights(competitive_data, market_profile)

def _build_insight_context(competitive_data: Dict, market_profile: Dict) -> str:
    """Build context string for GPT-5 analysis"""
    context = f"""
MARKET PROFILE:
- Solution: {market_profile.get('solution', 'Unknown')}
- Sub-vertical: {market_profile.get('sub_vertical', 'Unknown')}
- Vertical: {market_profile.get('vertical', 'Unknown')}
- Target Market: {market_profile.get('target_market', 'Unknown')}

COMPETITIVE LANDSCAPE:
"""
    
    # Add solution competitors
    solution_competitors = competitive_data.get('solution_competitors', [])
    if solution_competitors:
        context += "Direct Competitors (Solution Level):\n"
        for comp in solution_competitors[:5]:
            name = comp.get('name', 'Unknown')
            desc = comp.get('description', '')
            context += f"- {name}: {desc}\n"
    
    # Add sub-vertical competitors  
    subvertical_competitors = competitive_data.get('subvertical_competitors', [])
    if subvertical_competitors:
        context += "\nSub-vertical Competitors:\n"
        for comp in subvertical_competitors[:3]:
            name = comp.get('name', 'Unknown')  
            desc = comp.get('description', '')
            context += f"- {name}: {desc}\n"
    
    # Add market insights if available
    insights = competitive_data.get('solution_insights', []) + competitive_data.get('subvertical_insights', [])
    if insights:
        context += "\nMarket Intelligence:\n"
        for insight in insights[:3]:
            if isinstance(insight, dict):
                text = insight.get('text', str(insight))
            else:
                text = str(insight)
            context += f"- {text[:100]}...\n"
    
    return context

def _parse_insight_response(content: str) -> Dict[str, List[str]]:
    """Parse GPT-5 response into structured insights"""
    try:
        opportunities = []
        risks = []
        
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if 'OPPORTUNITIES:' in line.upper():
                current_section = 'opportunities'
            elif 'RISKS:' in line.upper():
                current_section = 'risks'
            elif line.startswith('-') or line.startswith('•'):
                insight = line.lstrip('-• ').strip()
                if len(insight) > 20:  # Valid insight
                    if current_section == 'opportunities':
                        opportunities.append(insight)
                    elif current_section == 'risks':
                        risks.append(insight)
        
        # Ensure we have at least some insights
        if not opportunities:
            opportunities = ['Market opportunities require additional analysis']
        if not risks:
            risks = ['Market risks require additional analysis']
        
        return {'opportunities': opportunities, 'risks': risks}
        
    except Exception as e:
        logger.error(f"❌ Insight parsing failed: {e}")
        return {
            'opportunities': ['Insight analysis requires manual review'], 
            'risks': ['Risk assessment requires manual review']
        }

def _generate_heuristic_insights(competitive_data: Dict, market_profile: Dict) -> Dict[str, List[str]]:
    """Generate heuristic insights based on data patterns (fallback)"""
    opportunities = []
    risks = []
    
    # Analyze competitive density
    total_competitors = (
        len(competitive_data.get('solution_competitors', [])) +
        len(competitive_data.get('subvertical_competitors', []))
    )
    
    if total_competitors == 0:
        opportunities.append("Limited direct competition identified - potential blue ocean opportunity")
        risks.append("Lack of competitive validation may indicate market readiness issues")
    elif total_competitors < 5:
        opportunities.append("Emerging competitive landscape with room for differentiation")
        risks.append("Early market stage may require significant customer education")
    else:
        risks.append("Highly competitive market with established players")
        opportunities.append("Large market validation from multiple competitors entering space")
    
    # Analyze by vertical
    vertical = market_profile.get('vertical', '').lower()
    if 'fintech' in vertical:
        risks.append("Fintech regulatory complexity and compliance requirements")
        opportunities.append("Digital transformation driving fintech adoption")
    elif 'health' in vertical:
        risks.append("Healthcare regulatory approval processes and lengthy sales cycles")
        opportunities.append("Aging demographics and healthcare digitization trends")
    elif 'clean' in vertical:
        opportunities.append("ESG investment focus and regulatory support for clean technology")
        risks.append("Technology adoption cycles may be slower in traditional industries")
    
    return {'opportunities': opportunities[:3], 'risks': risks[:3]}