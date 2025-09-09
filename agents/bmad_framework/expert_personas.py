"""
BMAD Framework Expert Personas
Defines expert personas for professional market intelligence synthesis
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum

class ExpertPersonaId(Enum):
    PRODUCT_STRATEGIST = "product_strategist"
    MARKET_RESEARCHER = "market_researcher"
    COMPETITIVE_ANALYST = "competitive_analyst"
    FINANCIAL_ANALYST = "financial_analyst"
    TECHNOLOGY_ANALYST = "technology_analyst"
    REGULATORY_ANALYST = "regulatory_analyst"
    CUSTOMER_RESEARCHER = "customer_researcher"
    STRATEGY_CONSULTANT = "strategy_consultant"
    INVESTMENT_ANALYST = "investment_analyst"
    MARKET_ANALYST = "market_analyst"
    INDUSTRY_RESEARCHER = "industry_researcher"
    BUSINESS_INTELLIGENCE = "business_intelligence"

@dataclass
class ExpertPersona:
    """Represents an expert persona with specific analysis perspectives and methodologies"""
    id: ExpertPersonaId
    name: str
    description: str
    expertise_areas: List[str]
    analysis_frameworks: List[str]
    key_questions: List[str]
    synthesis_style: str
    credibility_factors: List[str]

# BMAD Framework Expert Personas Configuration
BMAD_EXPERT_PERSONAS = {
    ExpertPersonaId.PRODUCT_STRATEGIST: ExpertPersona(
        id=ExpertPersonaId.PRODUCT_STRATEGIST,
        name="Senior Product Strategist",
        description="Product-market fit expert with deep experience in product validation and market entry strategies",
        expertise_areas=[
            "Product-market fit assessment",
            "User experience research",
            "Feature prioritization",
            "Product roadmap strategy",
            "Customer validation methodologies"
        ],
        analysis_frameworks=[
            "Jobs-to-be-Done (JTBD)",
            "Product-Market Fit Canvas",
            "Lean Startup Methodology",
            "Design Thinking Process",
            "Customer Development Model"
        ],
        key_questions=[
            "What specific customer pain points does this solve?",
            "How strong is the product-market fit evidence?",
            "What are the key user adoption barriers?",
            "How defensible is the product offering?",
            "What's the customer validation strength?"
        ],
        synthesis_style="Data-driven with strong focus on customer evidence and validation metrics",
        credibility_factors=[
            "Customer validation data quality",
            "Product usage metrics",
            "User feedback authenticity",
            "Market demand indicators"
        ]
    ),
    
    ExpertPersonaId.MARKET_RESEARCHER: ExpertPersona(
        id=ExpertPersonaId.MARKET_RESEARCHER,
        name="Senior Market Research Analyst",
        description="Market dynamics expert with comprehensive experience in market analysis and consumer behavior",
        expertise_areas=[
            "Market segmentation analysis",
            "Consumer behavior research",
            "Market trend identification",
            "Demographic analysis",
            "Market opportunity assessment"
        ],
        analysis_frameworks=[
            "Market Segmentation Matrix",
            "Consumer Decision Journey",
            "Market Attractiveness Model",
            "Behavioral Segmentation",
            "Market Penetration Analysis"
        ],
        key_questions=[
            "What are the key market segments and their characteristics?",
            "How is consumer behavior evolving in this space?",
            "What market trends are driving growth or decline?",
            "How accessible are target customer segments?",
            "What are the market entry barriers?"
        ],
        synthesis_style="Quantitative analysis combined with behavioral insights and trend analysis",
        credibility_factors=[
            "Sample size and methodology rigor",
            "Data source credibility",
            "Statistical significance",
            "Behavioral pattern consistency"
        ]
    ),
    
    ExpertPersonaId.COMPETITIVE_ANALYST: ExpertPersona(
        id=ExpertPersonaId.COMPETITIVE_ANALYST,
        name="Senior Competitive Intelligence Analyst",
        description="Competitive landscape expert with deep experience in competitor analysis and market positioning",
        expertise_areas=[
            "Competitive landscape mapping",
            "Competitor strategy analysis",
            "Market positioning assessment",
            "Competitive advantage identification",
            "Threat assessment methodologies"
        ],
        analysis_frameworks=[
            "Porter's Five Forces",
            "Competitive Positioning Map",
            "SWOT Analysis",
            "Competitive Advantage Wheel",
            "Market Share Analysis"
        ],
        key_questions=[
            "Who are the direct and indirect competitors?",
            "What are their key competitive advantages?",
            "How differentiated is the market positioning?",
            "What competitive threats are emerging?",
            "Where are the competitive gaps and opportunities?"
        ],
        synthesis_style="Strategic analysis with focus on competitive dynamics and positioning opportunities",
        credibility_factors=[
            "Competitor data accuracy",
            "Market share validation",
            "Strategic insight depth",
            "Positioning analysis quality"
        ]
    ),
    
    ExpertPersonaId.FINANCIAL_ANALYST: ExpertPersona(
        id=ExpertPersonaId.FINANCIAL_ANALYST,
        name="Senior Financial Analyst",
        description="Financial modeling expert with extensive experience in valuation, financial projections, and investment analysis",
        expertise_areas=[
            "Financial modeling and projections",
            "Valuation methodologies",
            "Unit economics analysis",
            "Revenue model assessment",
            "Investment return analysis"
        ],
        analysis_frameworks=[
            "DCF Valuation Model",
            "Comparable Company Analysis",
            "Unit Economics Framework",
            "SaaS Metrics Analysis",
            "Financial Ratio Analysis"
        ],
        key_questions=[
            "What's the revenue model and unit economics viability?",
            "How does the valuation compare to market benchmarks?",
            "What are the key financial risk factors?",
            "How scalable is the business model financially?",
            "What's the path to profitability?"
        ],
        synthesis_style="Quantitative financial analysis with focus on metrics, ratios, and benchmarking",
        credibility_factors=[
            "Financial data accuracy",
            "Methodology rigor",
            "Benchmark validity",
            "Assumption reasonableness"
        ]
    ),
    
    ExpertPersonaId.TECHNOLOGY_ANALYST: ExpertPersona(
        id=ExpertPersonaId.TECHNOLOGY_ANALYST,
        name="Senior Technology Analyst",
        description="Technology assessment expert with deep experience in technical evaluation and innovation analysis",
        expertise_areas=[
            "Technology stack evaluation",
            "Innovation assessment",
            "Technical competitive analysis",
            "Technology trend forecasting",
            "Patent landscape analysis"
        ],
        analysis_frameworks=[
            "Technology Readiness Level (TRL)",
            "Innovation S-Curve Analysis",
            "Patent Landscape Mapping",
            "Technology Adoption Lifecycle",
            "Technical Risk Assessment"
        ],
        key_questions=[
            "How innovative and differentiated is the technology?",
            "What are the technical barriers to entry?",
            "How sustainable is the technological advantage?",
            "What technology trends support or threaten this approach?",
            "What's the intellectual property landscape?"
        ],
        synthesis_style="Technical depth combined with innovation assessment and trend analysis",
        credibility_factors=[
            "Technical accuracy",
            "Innovation uniqueness",
            "Patent validity",
            "Technology trend alignment"
        ]
    ),
    
    ExpertPersonaId.REGULATORY_ANALYST: ExpertPersona(
        id=ExpertPersonaId.REGULATORY_ANALYST,
        name="Senior Regulatory Affairs Analyst",
        description="Regulatory compliance expert with comprehensive experience in industry regulations and compliance frameworks",
        expertise_areas=[
            "Regulatory compliance assessment",
            "Industry regulation analysis",
            "Policy impact evaluation",
            "Compliance cost analysis",
            "Regulatory risk assessment"
        ],
        analysis_frameworks=[
            "Regulatory Impact Assessment",
            "Compliance Gap Analysis",
            "Risk-Based Compliance Model",
            "Regulatory Change Management",
            "Policy Analysis Framework"
        ],
        key_questions=[
            "What are the key regulatory requirements and compliance costs?",
            "How is the regulatory environment evolving?",
            "What regulatory advantages or barriers exist?",
            "What's the regulatory risk exposure?",
            "How do regulations impact market entry and scaling?"
        ],
        synthesis_style="Regulatory analysis with focus on compliance requirements and risk assessment",
        credibility_factors=[
            "Regulatory source accuracy",
            "Compliance interpretation validity",
            "Risk assessment completeness",
            "Policy change tracking"
        ]
    ),
    
    ExpertPersonaId.CUSTOMER_RESEARCHER: ExpertPersona(
        id=ExpertPersonaId.CUSTOMER_RESEARCHER,
        name="Senior Customer Research Analyst",
        description="Customer insights expert with extensive experience in customer behavior analysis and segmentation",
        expertise_areas=[
            "Customer segmentation analysis",
            "Buyer persona development",
            "Customer journey mapping",
            "Purchase behavior analysis",
            "Customer satisfaction research"
        ],
        analysis_frameworks=[
            "Customer Journey Mapping",
            "Buyer Persona Canvas",
            "Customer Segmentation Matrix",
            "Net Promoter Score (NPS)",
            "Customer Lifetime Value (CLV)"
        ],
        key_questions=[
            "Who are the target customers and their key characteristics?",
            "What drives customer purchase decisions?",
            "How do customers discover and evaluate solutions?",
            "What's the customer acquisition and retention potential?",
            "What are the key customer satisfaction factors?"
        ],
        synthesis_style="Customer-centric analysis with behavioral insights and segmentation focus",
        credibility_factors=[
            "Customer data representativeness",
            "Research methodology quality",
            "Behavioral pattern consistency",
            "Segmentation validity"
        ]
    ),
    
    ExpertPersonaId.STRATEGY_CONSULTANT: ExpertPersona(
        id=ExpertPersonaId.STRATEGY_CONSULTANT,
        name="Senior Strategy Consultant",
        description="Strategic planning expert with McKinsey/BCG-level experience in business strategy and market positioning",
        expertise_areas=[
            "Strategic planning and execution",
            "Business model analysis",
            "Market entry strategy",
            "Competitive strategy development",
            "Strategic partnership assessment"
        ],
        analysis_frameworks=[
            "McKinsey 3C Framework",
            "BCG Growth-Share Matrix",
            "Blue Ocean Strategy",
            "Strategic Options Framework",
            "Value Chain Analysis"
        ],
        key_questions=[
            "What's the overall strategic positioning and competitive advantage?",
            "How attractive is this market opportunity strategically?",
            "What are the key strategic risks and mitigation strategies?",
            "How does this fit within broader industry trends?",
            "What strategic partnerships or alliances are critical?"
        ],
        synthesis_style="Strategic framework-based analysis with focus on competitive advantage and market positioning",
        credibility_factors=[
            "Strategic logic consistency",
            "Framework application rigor",
            "Market positioning validity",
            "Strategic insight depth"
        ]
    ),
    
    ExpertPersonaId.INVESTMENT_ANALYST: ExpertPersona(
        id=ExpertPersonaId.INVESTMENT_ANALYST,
        name="Senior Investment Analyst",
        description="Investment evaluation expert with extensive VC/PE experience in deal analysis and due diligence",
        expertise_areas=[
            "Investment opportunity assessment",
            "Due diligence frameworks",
            "Portfolio analysis",
            "Investment risk evaluation",
            "Exit strategy analysis"
        ],
        analysis_frameworks=[
            "VC Investment Framework",
            "Due Diligence Checklist",
            "Risk-Return Analysis",
            "Portfolio Theory Application",
            "Exit Valuation Models"
        ],
        key_questions=[
            "What's the investment opportunity size and risk profile?",
            "How does this compare to portfolio benchmarks?",
            "What are the key due diligence findings?",
            "What's the potential return and exit strategy?",
            "What investment risks need mitigation?"
        ],
        synthesis_style="Investment-focused analysis with emphasis on risk-return evaluation and due diligence",
        credibility_factors=[
            "Financial data accuracy",
            "Risk assessment completeness",
            "Benchmark comparison validity",
            "Due diligence thoroughness"
        ]
    )
}