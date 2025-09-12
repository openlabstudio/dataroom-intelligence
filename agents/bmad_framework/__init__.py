# BMAD Framework - Professional Market Intelligence Enhancement
# Integration module for enhancing market research with expert personas and research types

from .core import BMADFramework, BMADAnalysisRequest, BMADSynthesisResult, BMADResearchResult
from .research_types import ResearchType, BMAD_RESEARCH_TYPES
from .expert_personas import ExpertPersona, BMAD_EXPERT_PERSONAS

__all__ = ['BMADFramework', 'BMADAnalysisRequest', 'BMADSynthesisResult', 'BMADResearchResult', 'ResearchType', 'BMAD_RESEARCH_TYPES', 'ExpertPersona', 'BMAD_EXPERT_PERSONAS']