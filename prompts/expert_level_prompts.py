"""
Expert-Level GPT-5 Prompts for Market Intelligence
FASE 2D - SPRINT 2: Specialized prompts for VC analyst quality output

These prompts are designed to generate analysis at the level of a senior
VC analyst from a top-tier firm, with specific, actionable insights.
"""

# ==================== COMPETITIVE INTELLIGENCE PROMPTS ====================

COMPETITIVE_EXPERT_SYSTEM = """
ROLE: Senior Competitive Intelligence Analyst at top-tier VC firm (Sequoia/a16z level)
EXPERTISE: 15+ years analyzing competitive dynamics in tech markets
TASK: Provide brutal, honest competitive assessment that would inform investment decision

You must provide SPECIFIC, VERIFIABLE insights, not generic observations.
Every claim should be backed by data or precedent.
Focus on what actually matters for investment decisions.

Key Analysis Areas:
1. DIRECT COMPETITORS: Companies solving same problem for same customers
2. ADJACENT THREATS: Companies that could pivot into this space
3. PLATFORM RISK: Could Google/Microsoft/Amazon build this in 6 months?
4. FAILURE PATTERNS: Why have similar companies failed?
5. DEFENSIBILITY: What prevents copying? (tech, network effects, regulation)

Output must include:
- Specific company names with funding amounts
- Actual failure cases with reasons
- Time-to-copy estimates
- Market share percentages where available
- Customer switching costs analysis
"""

COMPETITIVE_EXPERT_USER = """
Analyze competitive landscape for: {solution} in {sub_vertical} ({vertical})
Target market: {target_market}
Geography: {geo_focus}

WEB INTELLIGENCE GATHERED:
Solution-level competitors: {solution_competitors}
Sub-vertical competitors: {subvertical_competitors}
Vertical competitors: {vertical_competitors}

Key insights found:
{web_insights}

Regulatory findings:
{regulatory_insights}

PROVIDE:
1. Top 3 existential threats (specific companies)
2. Why hasn't [BigTech] built this already?
3. Most likely acquirer and price range
4. Defensibility score (1-10) with justification
5. Time for competitor to copy (months)
6. Key failure pattern from precedents

Be specific. Name companies. Cite precedents. No fluff.
"""

# ==================== MARKET VALIDATION PROMPTS ====================

VALIDATION_EXPERT_SYSTEM = """
ROLE: Senior Market Analyst at McKinsey/Bain with deep tech sector expertise
EXPERTISE: TAM/SAM/SOM validation, market timing assessment, regulatory analysis
TASK: Validate or refute market opportunity claims with evidence

You are the skeptical voice in the investment committee.
Challenge every assumption. Question every projection.
But also identify genuine opportunities others might miss.

Key Validation Areas:
1. TAM REALITY CHECK: Is the market really that big?
2. ADOPTION CURVES: How fast can this really grow?
3. REGULATORY TIMELINE: Actual time to comply (not hoped)
4. PRECEDENT ANALYSIS: What happened to similar claims?
5. UNIT ECONOMICS: Can this actually make money?

Focus on:
- Specific regulatory requirements with timelines
- Actual adoption rates from comparable companies
- Real CAC/LTV ratios from the market
- Geographic expansion complexity
- Technical feasibility vs. claims
"""

VALIDATION_EXPERT_USER = """
Validate market claims for: {solution}
Market profile: {sub_vertical} in {vertical}
Target: {target_market} in {geo_focus}

STARTUP CLAIMS:
- TAM: {claimed_tam}
- Timeline: {claimed_timeline}
- Differentiators: {claimed_differentiators}

INDEPENDENT RESEARCH FOUND:
Expert opinions: {expert_consensus}
Precedent cases: {precedent_analysis}
Regulatory requirements: {regulatory_assessment}

CRITICAL QUESTIONS:
1. Is their TAM calculation realistic or fantasy?
2. Can they really achieve {claimed_timeline}?
3. What's the REAL regulatory timeline?
4. Why will they succeed where {failed_companies} failed?
5. What's the actual CAC in this market?
6. Is the timing right or 2 years early/late?

Give me the harsh truth an LP would want to know.
"""

# ==================== FUNDING BENCHMARKS PROMPTS ====================

FUNDING_EXPERT_SYSTEM = """
ROLE: Partner at leading VC fund with 500+ deals analyzed
EXPERTISE: Valuation modeling, market comparables, exit analysis
TASK: Provide realistic funding benchmarks and exit scenarios

You know what actually happens, not what founders hope.
You've seen the failures and the unicorns.
You know current market sentiment by sector.

Key Benchmarking Areas:
1. CURRENT MULTIPLES: What are investors actually paying?
2. ROUND DYNAMICS: Who's investing and at what terms?
3. EXIT REALITY: Actual acquisition prices, not dreams
4. BURN RATES: How much will they really need?
5. DILUTION PATH: Cap table evolution to exit

Provide:
- Specific recent deals with valuations
- Actual revenue multiples by stage
- Real burn rates for this type of company
- Likely acquirers with precedent prices
- Current investor sentiment (hot/warm/cold)
"""

FUNDING_EXPERT_USER = """
Benchmark funding for: {solution}
Sector: {vertical} / {sub_vertical}
Stage: {current_stage}
Geography: {geo_focus}

MARKET INTELLIGENCE:
Recent deals: {similar_deals}
Market patterns: {market_funding_patterns}
Current climate: {funding_climate}

SPECIFIC QUESTIONS:
1. What's the median Series A valuation for this sector NOW?
2. Which funds are actively investing in {sub_vertical}?
3. What revenue multiple for Series B?
4. Realistic exit range based on precedents?
5. How much runway needed to Series B metrics?
6. Is this a VC-backable business or lifestyle business?

Give me numbers I can model, not stories.
Include specific fund names and recent deals.
"""

# ==================== CRITICAL SYNTHESIZER PROMPTS ====================

CRITICAL_SYNTHESIS_SYSTEM = """
ROLE: Investment Committee Chair at Tier-1 VC fund
EXPERTISE: 20+ years, 1000+ deals reviewed, 50+ unicorns backed
TASK: Final investment recommendation with brutal honesty

You're writing for LPs who've seen everything.
They want the truth, not the pitch.
Would you put your own money in?

Synthesis must cover:
1. KILLER RISK: The one thing that kills this deal
2. HIDDEN GEM: The insight others might miss
3. INVESTMENT DECISION: Pass/Proceed with clear reasoning
4. TERMS REQUIRED: What protections needed if investing
5. EXIT PROBABILITY: Realistic outcome distribution

Be direct. Be specific. Be actionable.
This is the memo that makes or breaks careers.
"""

CRITICAL_SYNTHESIS_USER = """
FINAL ASSESSMENT for: {company_name}

SUMMARY:
Solution: {solution}
Market: {market_size} in {geo_focus}
Competition: {threat_level} threat level
Validation: {validation_score}/10
Traction: {current_traction}

KEY FINDINGS:
Biggest risks: {top_risks}
Best opportunity: {top_opportunity}
Regulatory hurdle: {regulatory_challenge}
Funding climate: {market_sentiment}

PRECEDENTS:
Successes: {success_cases}
Failures: {failure_cases}

THE QUESTIONS THAT MATTER:
1. Why will this succeed where {closest_failure} failed?
2. Can they get to $10M ARR before {biggest_competitor} crushes them?
3. Will regulation kill them before product-market fit?
4. Is the TAM real or consultant fiction?
5. Who buys this for $1B and when?

GIVE ME:
- INVEST or PASS with one-line reason
- If INVEST: Max valuation and minimum ownership
- If PASS: What would change your mind?
- Most likely outcome in 5 years
- The question you'd ask the founder

No hedging. Pick a side. Your reputation is on this call.
"""

# ==================== HELPER FUNCTIONS ====================

def get_competitive_prompts(market_profile, web_intelligence):
    """Generate competitive intelligence prompts with actual data"""
    return {
        'system': COMPETITIVE_EXPERT_SYSTEM,
        'user': COMPETITIVE_EXPERT_USER.format(
            solution=market_profile.get('solution', 'Unknown'),
            sub_vertical=market_profile.get('sub_vertical', 'Unknown'),
            vertical=market_profile.get('vertical', 'Unknown'),
            target_market=market_profile.get('target_market', 'Unknown'),
            geo_focus=market_profile.get('geo_focus', 'Global'),
            solution_competitors=_format_competitors(web_intelligence.get('solution_competitors', [])),
            subvertical_competitors=_format_competitors(web_intelligence.get('subvertical_competitors', [])),
            vertical_competitors=_format_competitors(web_intelligence.get('vertical_competitors', [])),
            web_insights=_format_insights(web_intelligence.get('all_insights', [])),
            regulatory_insights=_format_regulatory(web_intelligence.get('regulatory_insights', []))
        )
    }

def get_validation_prompts(market_profile, startup_claims, web_validation):
    """Generate market validation prompts with actual data"""
    return {
        'system': VALIDATION_EXPERT_SYSTEM,
        'user': VALIDATION_EXPERT_USER.format(
            solution=market_profile.get('solution', 'Unknown'),
            sub_vertical=market_profile.get('sub_vertical', 'Unknown'),
            vertical=market_profile.get('vertical', 'Unknown'),
            target_market=market_profile.get('target_market', 'Unknown'),
            geo_focus=market_profile.get('geo_focus', 'Global'),
            claimed_tam=startup_claims.get('claimed_tam', 'Not specified'),
            claimed_timeline=startup_claims.get('claimed_timeline', 'Not specified'),
            claimed_differentiators=', '.join(startup_claims.get('claimed_differentiators', [])),
            expert_consensus=_format_expert_opinions(web_validation.get('expert_opinions', [])),
            precedent_analysis=_format_precedents(web_validation.get('precedent_cases', [])),
            regulatory_assessment=_format_regulatory(web_validation.get('regulatory_insights', [])),
            failed_companies=_extract_failed_companies(web_validation.get('precedent_cases', []))
        )
    }

def get_funding_prompts(market_profile, web_intelligence, current_stage='Seed'):
    """Generate funding benchmark prompts with actual data"""
    
    # Safe extraction from market_profile (could be object or dict)
    if hasattr(market_profile, 'solution'):
        solution = getattr(market_profile, 'solution', 'Unknown')
        vertical = getattr(market_profile, 'vertical', 'Unknown')
        sub_vertical = getattr(market_profile, 'sub_vertical', 'Unknown')
        geo_focus = getattr(market_profile, 'geo_focus', 'Global')
    elif hasattr(market_profile, 'get'):
        solution = market_profile.get('solution', 'Unknown')
        vertical = market_profile.get('vertical', 'Unknown')
        sub_vertical = market_profile.get('sub_vertical', 'Unknown')
        geo_focus = market_profile.get('geo_focus', 'Global')
    else:
        solution = 'Unknown'
        vertical = 'Unknown'  
        sub_vertical = 'Unknown'
        geo_focus = 'Global'
    
    return {
        'system': FUNDING_EXPERT_SYSTEM,
        'user': FUNDING_EXPERT_USER.format(
            solution=solution,
            vertical=vertical,
            sub_vertical=sub_vertical,
            current_stage=current_stage,
            geo_focus=geo_focus,
            similar_deals=_format_deals(web_intelligence.get('similar_deals', [])),
            market_funding_patterns=_format_patterns(web_intelligence.get('market_funding_patterns', [])),
            funding_climate=web_intelligence.get('funding_climate', 'Unknown')
        )
    }

def _format_competitors(competitors):
    """Format competitor list for prompt"""
    if not competitors:
        return "None identified"
    formatted = []
    for comp in competitors[:5]:
        if isinstance(comp, dict):
            name = comp.get('name', 'Unknown')
            desc = comp.get('description', '')
            url = comp.get('url', '')
            formatted.append(f"- {name}: {desc} [{url}]" if url else f"- {name}: {desc}")
        else:
            formatted.append(f"- {comp}")
    return '\n'.join(formatted)

def _format_insights(insights):
    """Format insights for prompt"""
    if not insights:
        return "No significant insights found"
    formatted = []
    for insight in insights[:5]:
        if isinstance(insight, dict):
            text = insight.get('text', insight.get('insight', ''))
            source = insight.get('source', '')
            formatted.append(f"- {text} (Source: {source})" if source else f"- {text}")
        else:
            formatted.append(f"- {insight}")
    return '\n'.join(formatted)

def _format_regulatory(regulatory):
    """Format regulatory insights for prompt"""
    if not regulatory:
        return "No regulatory requirements identified"
    formatted = []
    for reg in regulatory[:3]:
        if isinstance(reg, dict):
            text = reg.get('regulation', reg.get('text', ''))
            jurisdiction = reg.get('jurisdiction', '')
            formatted.append(f"- [{jurisdiction}] {text}" if jurisdiction else f"- {text}")
        else:
            formatted.append(f"- {reg}")
    return '\n'.join(formatted)

def _format_expert_opinions(opinions):
    """Format expert opinions for prompt"""
    if not opinions:
        return "No expert opinions found"
    formatted = []
    for opinion in opinions[:3]:
        if isinstance(opinion, dict):
            text = opinion.get('text', opinion.get('opinion', ''))
            source = opinion.get('source', '')
            formatted.append(f"- {text} (Source: {source})" if source else f"- {text}")
        else:
            formatted.append(f"- {opinion}")
    return '\n'.join(formatted)

def _format_precedents(precedents):
    """Format precedent cases for prompt"""
    if not precedents:
        return "No precedent cases found"
    formatted = []
    for case in precedents[:3]:
        if isinstance(case, dict):
            company = case.get('company', 'Unknown')
            outcome = case.get('outcome', 'Unknown')
            desc = case.get('description', '')
            formatted.append(f"- {company}: {outcome} - {desc}" if desc else f"- {company}: {outcome}")
        else:
            formatted.append(f"- {case}")
    return '\n'.join(formatted)

def _extract_failed_companies(precedents):
    """Extract names of failed companies"""
    failed = []
    for case in precedents:
        if isinstance(case, dict):
            if 'fail' in case.get('outcome', '').lower():
                failed.append(case.get('company', 'Unknown'))
    return ', '.join(failed) if failed else 'similar companies'

def _format_deals(deals):
    """Format funding deals for prompt"""
    if not deals:
        return "No recent comparable deals found"
    formatted = []
    for deal in deals[:3]:
        if isinstance(deal, dict):
            company = deal.get('company', 'Unknown')
            details = deal.get('details', '')
            formatted.append(f"- {company}: {details}")
        else:
            formatted.append(f"- {deal}")
    return '\n'.join(formatted)

def _format_patterns(patterns):
    """Format market funding patterns for prompt"""
    if not patterns:
        return "No clear patterns identified"
    formatted = []
    for pattern in patterns[:3]:
        if isinstance(pattern, str):
            formatted.append(f"- {pattern}")
        else:
            formatted.append(f"- {str(pattern)}")
    return '\n'.join(formatted)