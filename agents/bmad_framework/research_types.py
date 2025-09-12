"""
BMAD Framework Research Types
Defines the 8 core research methodologies for professional market intelligence
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum

class ResearchTypeId(Enum):
    PRODUCT_VALIDATION = "product_validation"
    COMPETITIVE_INTELLIGENCE = "competitive_intelligence"
    MARKET_SIZING = "market_sizing"
    TECHNOLOGY_ASSESSMENT = "technology_assessment"
    REGULATORY_ANALYSIS = "regulatory_analysis"
    CUSTOMER_DEVELOPMENT = "customer_development"
    FUNDING_INTELLIGENCE = "funding_intelligence"
    STRATEGIC_POSITIONING = "strategic_positioning"

@dataclass
class ResearchType:
    """Represents a BMAD research methodology with specific focus areas and search strategies"""
    id: ResearchTypeId
    name: str
    description: str
    focus_areas: List[str]
    search_strategies: List[str]
    synthesis_priorities: List[str]
    expert_persona_weights: Dict[str, float]

# BMAD Framework 8 Research Types Configuration
BMAD_RESEARCH_TYPES = {
    ResearchTypeId.PRODUCT_VALIDATION: ResearchType(
        id=ResearchTypeId.PRODUCT_VALIDATION,
        name="Product Validation Intelligence",
        description="Market demand validation, product-market fit assessment, and customer validation research",
        focus_areas=[
            "Product-market fit indicators",
            "Customer pain point validation",
            "Feature demand analysis",
            "User adoption patterns",
            "Market readiness assessment"
        ],
        search_strategies=[
            "Customer feedback aggregation",
            "Product review analysis",
            "Beta testing results research",
            "User survey data collection",
            "Market demand indicators"
        ],
        synthesis_priorities=[
            "Validation strength assessment",
            "Customer segment analysis",
            "Product-market fit score",
            "Risk factor identification"
        ],
        expert_persona_weights={
            "product_strategist": 0.4,
            "market_researcher": 0.3,
            "customer_insights": 0.3
        }
    ),
    
    ResearchTypeId.COMPETITIVE_INTELLIGENCE: ResearchType(
        id=ResearchTypeId.COMPETITIVE_INTELLIGENCE,
        name="Competitive Landscape Intelligence",
        description="Comprehensive competitive analysis, positioning assessment, and market dynamics research",
        focus_areas=[
            "Direct competitor identification",
            "Indirect competitor mapping",
            "Competitive positioning analysis",
            "Feature comparison matrices",
            "Market share dynamics"
        ],
        search_strategies=[
            "Competitor funding intelligence",
            "Product feature comparisons",
            "Pricing strategy analysis",
            "Market positioning research",
            "Competitive advantage assessment"
        ],
        synthesis_priorities=[
            "Competitive landscape mapping",
            "Differentiation opportunities",
            "Competitive threat assessment",
            "Market positioning gaps"
        ],
        expert_persona_weights={
            "competitive_analyst": 0.5,
            "market_strategist": 0.3,
            "business_intelligence": 0.2
        }
    ),
    
    ResearchTypeId.MARKET_SIZING: ResearchType(
        id=ResearchTypeId.MARKET_SIZING,
        name="Market Sizing & Opportunity Assessment",
        description="Total addressable market (TAM), serviceable addressable market (SAM), and market opportunity quantification",
        focus_areas=[
            "Total Addressable Market (TAM)",
            "Serviceable Addressable Market (SAM)",
            "Serviceable Obtainable Market (SOM)",
            "Market growth rates",
            "Revenue opportunity assessment"
        ],
        search_strategies=[
            "Industry research reports",
            "Market research data",
            "Government statistics",
            "Industry association reports",
            "Financial analyst projections"
        ],
        synthesis_priorities=[
            "Market size quantification",
            "Growth trajectory analysis",
            "Market opportunity scoring",
            "Revenue potential assessment"
        ],
        expert_persona_weights={
            "market_analyst": 0.4,
            "financial_analyst": 0.3,
            "industry_researcher": 0.3
        }
    ),
    
    ResearchTypeId.TECHNOLOGY_ASSESSMENT: ResearchType(
        id=ResearchTypeId.TECHNOLOGY_ASSESSMENT,
        name="Technology & Innovation Assessment",
        description="Technology stack analysis, innovation assessment, and technical competitive advantages",
        focus_areas=[
            "Technology stack evaluation",
            "Innovation differentiation",
            "Technical barriers to entry",
            "Patent landscape analysis",
            "Technology trend alignment"
        ],
        search_strategies=[
            "Patent database research",
            "Technical documentation analysis",
            "Developer community insights",
            "Technology trend reports",
            "Innovation pipeline assessment"
        ],
        synthesis_priorities=[
            "Technology differentiation score",
            "Innovation potential assessment",
            "Technical risk evaluation",
            "Competitive technology gaps"
        ],
        expert_persona_weights={
            "technology_analyst": 0.4,
            "innovation_researcher": 0.3,
            "patent_analyst": 0.3
        }
    ),
    
    ResearchTypeId.REGULATORY_ANALYSIS: ResearchType(
        id=ResearchTypeId.REGULATORY_ANALYSIS,
        name="Regulatory & Compliance Intelligence",
        description="Regulatory environment analysis, compliance requirements, and regulatory risk assessment",
        focus_areas=[
            "Regulatory compliance requirements",
            "Industry-specific regulations",
            "Regulatory change trends",
            "Compliance cost analysis",
            "Regulatory risk assessment"
        ],
        search_strategies=[
            "Regulatory body publications",
            "Compliance requirement research",
            "Industry regulatory trends",
            "Legal precedent analysis",
            "Policy change monitoring"
        ],
        synthesis_priorities=[
            "Regulatory compliance assessment",
            "Regulatory risk scoring",
            "Compliance cost estimation",
            "Regulatory advantage identification"
        ],
        expert_persona_weights={
            "regulatory_analyst": 0.5,
            "compliance_expert": 0.3,
            "policy_researcher": 0.2
        }
    ),
    
    ResearchTypeId.CUSTOMER_DEVELOPMENT: ResearchType(
        id=ResearchTypeId.CUSTOMER_DEVELOPMENT,
        name="Customer Development Intelligence",
        description="Customer segment analysis, buying behavior research, and customer acquisition insights",
        focus_areas=[
            "Customer segment identification",
            "Buyer persona development",
            "Customer acquisition channels",
            "Customer lifetime value",
            "Purchase decision factors"
        ],
        search_strategies=[
            "Customer behavior research",
            "Demographic analysis",
            "Psychographic profiling",
            "Purchase pattern analysis",
            "Customer satisfaction research"
        ],
        synthesis_priorities=[
            "Customer segment prioritization",
            "Acquisition strategy insights",
            "Customer value assessment",
            "Market penetration opportunities"
        ],
        expert_persona_weights={
            "customer_researcher": 0.4,
            "behavioral_analyst": 0.3,
            "market_segmentation": 0.3
        }
    ),
    
    ResearchTypeId.FUNDING_INTELLIGENCE: ResearchType(
        id=ResearchTypeId.FUNDING_INTELLIGENCE,
        name="Funding & Investment Intelligence",
        description="Investment landscape analysis, funding trend research, and investor sentiment assessment",
        focus_areas=[
            "Funding trend analysis",
            "Investor interest patterns",
            "Valuation benchmarking",
            "Investment stage dynamics",
            "Sector investment flows"
        ],
        search_strategies=[
            "Funding database research",
            "Investor activity tracking",
            "Valuation analysis",
            "Investment trend monitoring",
            "Venture capital insights"
        ],
        synthesis_priorities=[
            "Funding opportunity assessment",
            "Investor sentiment analysis",
            "Valuation positioning",
            "Investment readiness scoring"
        ],
        expert_persona_weights={
            "investment_analyst": 0.4,
            "venture_researcher": 0.3,
            "financial_strategist": 0.3
        }
    ),
    
    ResearchTypeId.STRATEGIC_POSITIONING: ResearchType(
        id=ResearchTypeId.STRATEGIC_POSITIONING,
        name="Strategic Positioning Intelligence",
        description="Market positioning analysis, strategic opportunity identification, and competitive strategy insights",
        focus_areas=[
            "Market positioning assessment",
            "Strategic opportunity mapping",
            "Competitive strategy analysis",
            "Value proposition differentiation",
            "Strategic partnership opportunities"
        ],
        search_strategies=[
            "Strategic analysis research",
            "Positioning case studies",
            "Partnership opportunity research",
            "Strategic trend analysis",
            "Market dynamics assessment"
        ],
        synthesis_priorities=[
            "Strategic positioning score",
            "Opportunity prioritization",
            "Strategic risk assessment",
            "Competitive strategy insights"
        ],
        expert_persona_weights={
            "strategy_consultant": 0.4,
            "market_strategist": 0.3,
            "business_analyst": 0.3
        }
    )
}