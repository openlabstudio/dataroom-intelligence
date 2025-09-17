"""
Analyst Schema Constants - Fixed format for VC analyst output
Defines canonical sections, fields, and priorities for deck analysis
"""

from typing import Dict, List, Set

# Fixed order of sections for output
SECTIONS_ORDER: List[str] = [
    "business_model_pricing",
    "value_prop_diff",
    "unit_economics",
    "gtm_sales",
    "qualified_traction",
    "base_financials",
    "competition",
    "risks_regulation",
    "evidence_pmf",
    "roadmap",
    "team",
]

# Section titles in Spanish for display
SECTION_TITLE: Dict[str, str] = {
    "business_model_pricing": "Modelo de negocio y pricing:",
    "value_prop_diff": "Propuesta de valor / diferenciación:",
    "unit_economics": "Unit economics:",
    "gtm_sales": "GTM/ventas:",
    "qualified_traction": "Tracción cualificada:",
    "base_financials": "Finanzas base:",
    "competition": "Competencia:",
    "risks_regulation": "Riesgos/regulación:",
    "evidence_pmf": "Evidencia de PMF:",
    "roadmap": "Roadmap con hitos medibles:",
    "team": "Equipo:",
}

# Canonical fields per section
FIELDS: Dict[str, List[str]] = {
    "business_model_pricing": ["pricing_model", "payer", "take_rate", "pricing_examples"],
    "value_prop_diff": ["value_prop", "differentiation", "product_modules"],
    "unit_economics": ["cac_by_channel", "ltv_or_proxy", "payback_months", "gross_margin", "contribution_per_tx"],
    "gtm_sales": ["icp", "channels", "funnel", "acv", "sales_cycle_days", "win_loss", "pipeline_prob_weight"],
    "qualified_traction": ["merchants_active_mom", "travelers_active_mom", "transactions_mom", "gmv_mom", "cohorts_retention"],
    "base_financials": ["revenue", "gmv", "vat", "burn", "runway_months", "funding_rounds", "pl_forecast", "cash_plan", "bridge", "use_of_funds"],
    "competition": ["competitors_table", "advantages_vs"],
    "risks_regulation": ["risks", "regulatory"],
    "evidence_pmf": ["nps", "expansion", "case_studies"],
    "roadmap": ["roadmap"],
    "team": ["team", "hiring_gaps", "cap_table", "governance"],
}

# Field aliases for flexible matching
FIELD_ALIASES: Dict[str, List[str]] = {
    # Financials
    "revenue": ["revenue", "ingresos", "arr", "mrr"],
    "gmv": ["gmv", "gross_merchandise_value", "volumen"],
    "vat": ["vat", "iva", "tax"],
    "burn": ["burn", "burn_rate", "cash_burn", "quemado"],
    "runway_months": ["runway", "runway_months", "pista"],
    "funding_rounds": ["funding_rounds", "funding", "investment", "rounds"],

    # Traction
    "merchants_active_mom": ["merchants", "active_merchants", "comercios"],
    "travelers_active_mom": ["travelers", "viajeros", "users"],
    "transactions_mom": ["transactions", "trx", "transacciones"],
    "gmv_mom": ["gmv_growth", "gmv_mom", "monthly_gmv"],
    "cohorts_retention": ["retention", "cohorts", "cohort_retention"],

    # Unit Economics
    "cac_by_channel": ["cac", "customer_acquisition_cost", "acquisition_cost"],
    "ltv_or_proxy": ["ltv", "lifetime_value", "clv", "customer_lifetime_value"],
    "payback_months": ["payback", "payback_period", "payback_time"],
    "gross_margin": ["gross_margin", "margin", "margen_bruto"],

    # GTM/Sales
    "icp": ["icp", "ideal_customer", "target_customer"],
    "channels": ["channels", "sales_channels", "distribution"],
    "funnel": ["funnel", "sales_funnel", "conversion_funnel"],
    "acv": ["acv", "average_contract_value", "deal_size"],

    # Team
    "team": ["team", "founders", "equipo", "fundadores"],
    "cap_table": ["cap_table", "captable", "shareholding", "ownership"],

    # Product/Competition
    "value_prop": ["value_proposition", "value_prop", "propuesta_valor"],
    "product_modules": ["product", "modules", "features", "productos"],
    "competitors_table": ["competition", "competitors", "competencia"],

    # PMF/Risk
    "nps": ["nps", "net_promoter_score"],
    "risks": ["risks", "riesgos", "challenges"],
    "regulatory": ["regulatory", "regulation", "compliance", "regulacion"],

    # Other
    "roadmap": ["roadmap", "milestones", "hitos"],
    "why_now": ["why_now", "timing", "market_timing"],
}

# Critical sections (must have for investment decision)
CRITICAL_SECTIONS: Set[str] = {
    "business_model_pricing",
    "unit_economics",
    "gtm_sales",
    "qualified_traction",
    "base_financials"
}

# Nice-to-have sections
NICE_TO_HAVE_SECTIONS: Set[str] = {
    "value_prop_diff",
    "competition",
    "risks_regulation",
    "evidence_pmf",
    "roadmap",
    "team"
}

# Flexible bullet limits per section
BULLETS_LIMITS: Dict[str, int] = {
    "unit_economics": 5,      # Critical - allow more
    "base_financials": 5,      # Critical - allow more
    "qualified_traction": 4,   # Important
    "business_model_pricing": 3,
    "gtm_sales": 3,
    "value_prop_diff": 3,
    "competition": 3,
    "evidence_pmf": 3,
    "team": 2,                 # Less critical
    "roadmap": 2,              # Less critical
    "risks_regulation": 2,
}

# Default bullet limit if not specified
DEFAULT_BULLET_LIMIT: int = 3

# Maximum total bullets across all sections
MAX_TOTAL_BULLETS: int = 35