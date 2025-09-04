# Product Requirements Document: Market Intelligence Report Generation

## Executive Summary
Feature to generate comprehensive market intelligence reports in Markdown format, providing VCs with professional, data-driven analysis of investment categories/solutions (not specific companies). Reports assess whether a market/solution is venture-backable, overcoming Slack's 4000-character limitation.

## Problem Statement

### Current Limitations
- **4000-character Slack limit** forces extreme summarization
- **Lost insights**: Only 4 references shown vs 24+ collected sources
- **No market depth**: Can't show full competitive landscape (20+ players)
- **Poor shareability**: Can't attach comprehensive market analysis to IC meetings
- **Missing intelligence**: Surface-level market assessment when VCs need deep category analysis

### User Pain Points (VC Analyst Perspective)
1. **Investment Thesis Validation**: Need to validate if a category is worth investing in
2. **Market Intelligence**: Require comprehensive competitive landscape analysis
3. **Category Assessment**: Need data-driven decision on market opportunity
4. **IC Documentation**: Require professional market reports for investment committees
5. **Trend Analysis**: Can't see full market dynamics and timing windows

## Solution Overview

### Core Capability
Generate comprehensive 20+ page Market Intelligence Reports analyzing the investment viability of a solution/category (not specific startups), automatically generated after `/market-research` command completion.

### Key Benefits
- **Pure Market Focus**: Analyzes category opportunity, not specific companies
- **Complete Intelligence**: All 24+ sources with full competitive landscape
- **Investment Decision**: Clear GO/NO-GO for the category
- **Professional Format**: IC-ready market assessment
- **Data-Driven**: Based on 300+ data points from Tavily searches

## User Personas

### Primary: Senior VC Analyst
- **Needs**: Market category assessment before evaluating specific startups
- **Uses**: When exploring new verticals or solutions
- **Values**: Data accuracy, market timing, competitive dynamics

### Secondary: VC Partner
- **Needs**: Category investment thesis for IC presentation
- **Uses**: Decide whether to pursue deals in this space
- **Values**: Clear recommendations, risk assessment, return potential

## Report Structure - Pure Market Intelligence

### 1. Executive Market Assessment (2 pages)
- **Category Verdict**: ATTRACTIVE / UNATTRACTIVE for VC investment
- **Investment Window**: Open/Closing/Closed
- **Key Market Signals Dashboard**: TAM, CAGR, Competition, Exits
- **Core Investment Thesis**: Why invest or avoid this category

### 2. Market Opportunity Analysis (5 pages)
- **TAM/SAM/SOM** with transparent methodology
- **Growth Trajectory**: 10-year market evolution
- **Market Timing**: Why NOW analysis
- **Market Drivers**: Tech/regulatory/social catalysts

### 3. Competitive Landscape Intelligence (8 pages)
- **Complete Ecosystem Map**: All 20+ players identified
- **Competitive Dynamics**: Concentration, barriers, differentiation
- **Failed Companies**: Lessons from the graveyard
- **Platform Risk**: Big Tech entry probability

### 4. Investment Landscape (4 pages)
- **Funding Trends**: Investment by stage, valuations
- **Active Investors**: Who's investing and their thesis
- **Exit Analysis**: Recent exits and multiples
- **Acquirer Landscape**: Strategic buyers and appetite

### 5. Technology & Regulatory (3 pages)
- **Technical Feasibility**: Core tech requirements and costs
- **Infrastructure Economics**: Cost at different scales
- **Regulatory Landscape**: Requirements by geography
- **Compliance Complexity**: Time and cost to comply

### 6. Risks & Opportunities (3 pages)
- **Risk Matrix**: Probability vs Impact assessment
- **Mitigation Strategies**: How to reduce key risks
- **Opportunity Windows**: Underserved segments
- **Geographic Arbitrage**: Regional opportunities

### 7. Investment Recommendation (2 pages)
- **Category Verdict**: Clear GO/NO-GO decision
- **Ideal Investment Profile**: Stage, check size, ownership
- **Success Criteria**: Must-haves for investments
- **DD Questions**: Key areas to probe

### 8. Appendices (10+ pages)
- **All Sources**: 100+ sources with abstracts
- **Methodology**: Data collection approach
- **Glossary**: Technical terms explained

## Technical Implementation

### Generation Flow
```python
# Automatically triggered at end of /market-research
def complete_market_research():
    # ... existing market research ...
    
    # Generate comprehensive report
    markdown_report = generate_market_intelligence_report(
        market_data=market_intelligence_result,
        all_sources=collected_sources,
        analysis_results=session_data
    )
    
    # Upload to Slack
    client.files_upload(
        channels=channel_id,
        content=markdown_report,
        filename=f"market_intelligence_{vertical}_{timestamp}.md",
        title="📊 Market Intelligence Report - Full Analysis"
    )
```

### Enhanced Data Collection Strategy

#### Current State (Limited)
- 9 Tavily searches total
- 1 GPT-4 synthesis
- ~24 sources analyzed

#### Enhanced State (Comprehensive)
```python
COMPREHENSIVE_SEARCHES = {
    "market_sizing": 5 queries,
    "competitive_landscape": 8 queries,
    "investment_activity": 6 queries,
    "market_validation": 5 queries,
    "technology_assessment": 4 queries,
    "regulatory_analysis": 3 queries
}
# Total: 31 Tavily searches = 300+ sources
```

### Specialized GPT-4 Prompts

```python
MARKET_INTELLIGENCE_PROMPTS = {
    "category_viability": "Analyze if this category is venture-backable",
    "competitive_dynamics": "Map complete ecosystem and dynamics",
    "investment_thesis": "Build investment case for the category",
    "risk_assessment": "Identify category-level risks",
    "timing_analysis": "Assess market timing and windows"
}
# 5 specialized GPT-4 analyses for depth
```

## Content Requirements

### Data Completeness
- **Minimum Sources**: 100+ analyzed
- **Competitors Mapped**: 20+ companies
- **Time Period**: Last 24 months of data
- **Geographic Coverage**: Primary markets covered

### Analysis Depth
- **Not company-specific**: Pure market/category analysis
- **Investment-focused**: Clear VC decision framework
- **Data-driven**: Every claim backed by sources
- **Actionable**: Specific recommendations for VCs

## User Workflow

### Automatic Generation
1. User executes `/analyze [drive-link]`
2. User executes `/market-research`
3. System performs enhanced market analysis (3-5 min)
4. **Automatic**: .md report generated and uploaded
5. User downloads comprehensive market intelligence

### Report Includes
- Same data shown in Slack summary (coherent)
- PLUS 10x more depth and sources
- PLUS complete competitive landscape
- PLUS investment recommendation framework

## Success Metrics

### Quality Metrics
- **Comprehensiveness**: 20+ page reports standard
- **Accuracy**: 95%+ fact verification
- **Actionability**: Clear GO/NO-GO decision
- **Professional**: IC-ready without editing

### Business Value
- **Time Saved**: 40-60 hours of analyst work
- **Decision Quality**: Data-driven category assessment
- **Cost Efficiency**: $1.20 per comprehensive report
- **Speed**: 3-5 minutes vs weeks of research

## Implementation Phases

### Phase 1: Core Report Generation
- Template-based markdown generation
- All 8 sections with real data
- Automatic upload to Slack
- 20+ page comprehensive reports

### Phase 2: Enhanced Intelligence
- 31 Tavily searches (vs current 9)
- 5 specialized GPT-4 analyses
- Dynamic visualizations (Mermaid)
- Confidence scoring per data point

### Phase 3: Advanced Features
- Comparative category analysis
- Trend analysis over time
- Auto-update capabilities
- Multi-language support

## Technical Requirements

### Dependencies
- **Current**: Existing market_research_orchestrator
- **Markdown Generation**: Built-in Python
- **File Upload**: Slack SDK (already integrated)
- **Templates**: Jinja2 for report structure

### Performance
- **Generation Time**: <30 seconds after analysis
- **File Size**: ~200-500KB markdown
- **No additional API calls**: Uses already collected data

## Cost Analysis

### Current Costs
- 9 Tavily searches: $0.09
- 2 GPT-4 calls: $0.30
- Total: ~$0.40 per analysis

### Enhanced Costs (Proposed)
- 31 Tavily searches: $0.31
- 5 GPT-4 calls: $0.75
- Total: ~$1.06 per comprehensive report
- **ROI**: 5000x (vs $5,000 consulting report)

## Risk Mitigation

### Technical Risks
- **Large file handling**: Chunked generation if needed
- **Timeout issues**: Background processing already implemented
- **Data consistency**: Single source of truth from session

### Content Risks
- **Data freshness**: Clear timestamps on all data
- **Conflicting info**: Explicitly note contradictions
- **Missing data**: Clear notation of gaps

## Acceptance Criteria

### Minimum Viable Product
- [ ] Generates 15+ page market intelligence reports
- [ ] Focuses on category, not specific companies
- [ ] Includes all 8 major sections
- [ ] Contains 100+ source references
- [ ] Uploads automatically after /market-research
- [ ] Clear GO/NO-GO investment recommendation
- [ ] Complete competitive landscape (20+ players)
- [ ] Market timing and window assessment
- [ ] Professional formatting in markdown

### Definition of Done
- [ ] Report generation < 30 seconds
- [ ] No additional user commands needed
- [ ] Coherent with Slack summary
- [ ] 10x more comprehensive than summary
- [ ] Ready for IC presentation
- [ ] All data properly cited

## Appendix: Sample Report Sections

### A. Executive Summary Example
```markdown
# Investment Analysis: TechStartup Inc.

## Executive Summary

**Investment Recommendation**: PROCEED WITH DUE DILIGENCE

**Investment Thesis**: TechStartup represents a compelling Series A opportunity 
in the high-growth B2B SaaS market, with demonstrated product-market fit, 
strong unit economics (LTV/CAC of 3.5x), and a clear path to $100M ARR within 
3 years.

**Key Metrics**:
- Overall Score: 8.2/10
- Market Size: $45B (15% CAGR)
- Current ARR: $5.2M (230% YoY growth)
- Funding Ask: $20M Series A
- Pre-money Valuation: $80M
```

### B. Competitive Matrix Example
```markdown
## Competitive Landscape

| Company | Funding | Revenue | Growth | Market Share | Key Differentiator |
|---------|---------|---------|--------|--------------|-------------------|
| **TechStartup** | $3M | $5.2M | 230% | 2% | AI-powered automation |
| Competitor A | $45M | $25M | 120% | 8% | Enterprise focus |
| Competitor B | $15M | $8M | 90% | 3% | Low-cost provider |
| Competitor C | $78M | $40M | 85% | 12% | Market leader |
```

---

**Document Status**: DRAFT v1.0
**Author**: DataRoom Intelligence System
**Date**: 2025-09-03
**Review Status**: Pending user feedback