"""
Critical Synthesizer Agent for DataRoom Intelligence
Final agent in 5-agent Chain of Thought - Investment Decision Framework

Synthesizes all agent outputs into actionable VC investment recommendation:
GO/CAUTION/NO-GO with detailed reasoning within 3000 char Slack limit
"""

import os
import json
from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent
from utils.logger import get_logger

logger = get_logger(__name__)

class InvestmentDecision:
    """Data structure for investment decision results"""
    
    def __init__(self):
        self.decision: str = ""  # GO, CAUTION, NO-GO
        self.executive_summary: str = ""
        self.key_rationale: List[str] = []
        self.key_risks: List[str] = []
        self.market_opportunity: str = ""
        self.confidence_level: str = ""  # High, Medium, Low
        self.confidence_reason: str = ""
        self.red_flags: List[Dict[str, Any]] = []
        self.character_count: int = 0
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            'decision': self.decision,
            'executive_summary': self.executive_summary,
            'key_rationale': self.key_rationale,
            'key_risks': self.key_risks,
            'market_opportunity': self.market_opportunity,
            'confidence_level': self.confidence_level,
            'confidence_reason': self.confidence_reason,
            'red_flags': self.red_flags,
            'character_count': self.character_count
        }

class CriticalSynthesizerAgent(BaseAgent):
    """Agent 5/5: Investment Decision Synthesizer with GPT-4 intelligence"""
    
    def __init__(self):
        super().__init__("Critical Synthesizer")
        
    def analyze(self, processed_documents: List[Dict[str, Any]], 
               document_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Required abstract method from BaseAgent - delegates to synthesize_investment_decision"""
        # This is called by orchestrator with market intelligence result
        # For Critical Synthesizer, we implement the main logic in synthesize_investment_decision
        return {"status": "ready", "message": "Critical Synthesizer ready for investment decision synthesis"}
        
    def synthesize_investment_decision(self, market_intelligence_result) -> InvestmentDecision:
        """
        Synthesize all agent outputs into investment recommendation
        
        Args:
            market_intelligence_result: Complete result from orchestrator
            
        Returns:
            InvestmentDecision with GO/CAUTION/NO-GO recommendation
        """
        try:
            logger.info("🧠 Starting critical investment decision synthesis...")
            
            # PHASE 1: Red Flags Detection (Rule-based)
            red_flags = self._detect_red_flags(market_intelligence_result)
            logger.info(f"🚨 Detected {len(red_flags)} red flags")
            
            # PHASE 2: GPT-4 Investment Synthesis  
            decision = self._generate_investment_recommendation(
                market_intelligence_result, red_flags
            )
            
            # PHASE 3: Character count and optimization
            decision.character_count = self._estimate_character_count(decision)
            logger.info(f"📏 Investment decision estimated at {decision.character_count} characters")
            
            # PHASE 4: Optimize if needed (within 800 char target)
            if decision.character_count > 800:
                decision = self._optimize_for_character_limit(decision)
                logger.info(f"✂️ Optimized to {decision.character_count} characters")
            
            logger.info(f"✅ Investment decision: {decision.decision}")
            return decision
            
        except Exception as e:
            logger.error(f"❌ Critical synthesis failed: {e}")
            return self._get_fallback_decision(str(e))
    
    def _detect_red_flags(self, result) -> List[Dict[str, Any]]:
        """Detect automatic red flags from market intelligence"""
        red_flags = []
        
        try:
            # Regulatory Red Flags
            competitive_analysis = result.competitive_analysis if hasattr(result, 'competitive_analysis') else {}
            
            # Check for regulatory complexity in competitive analysis
            if isinstance(competitive_analysis, dict):
                regulatory_insights = competitive_analysis.get('regulatory_insights', [])
                if len(regulatory_insights) > 2:  # Multiple regulatory concerns
                    red_flags.append({
                        'type': 'regulatory',
                        'severity': 'high',
                        'reason': f'Complex regulatory environment identified ({len(regulatory_insights)} requirements found)'
                    })
                elif len(regulatory_insights) == 1:
                    red_flags.append({
                        'type': 'regulatory', 
                        'severity': 'medium',
                        'reason': 'Regulatory requirements identified - due diligence required'
                    })
            
            # Market Validation Red Flags
            market_validation = result.market_validation if hasattr(result, 'market_validation') else {}
            if isinstance(market_validation, dict):
                validation_score = market_validation.get('validation_score', 5.0)
                if validation_score < 3.0:
                    red_flags.append({
                        'type': 'validation',
                        'severity': 'high',
                        'reason': f'Low market validation score ({validation_score}/10)'
                    })
                elif validation_score < 5.0:
                    red_flags.append({
                        'type': 'validation',
                        'severity': 'medium', 
                        'reason': f'Moderate market validation concerns (score: {validation_score}/10)'
                    })
            
            # Competitive Saturation Red Flags
            if isinstance(competitive_analysis, dict):
                threat_level = competitive_analysis.get('independent_analysis', {}).get('threat_level', 'medium')
                if threat_level == 'high':
                    red_flags.append({
                        'type': 'competition',
                        'severity': 'medium',
                        'reason': 'Highly competitive market environment detected'
                    })
            
            return red_flags
            
        except Exception as e:
            logger.error(f"❌ Red flags detection failed: {e}")
            return []
    
    def _generate_investment_recommendation(self, result, red_flags: List[Dict]) -> InvestmentDecision:
        """Generate GPT-4 powered investment recommendation"""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            # Build comprehensive context for GPT-4
            context = self._build_synthesis_context(result, red_flags)
            
            prompt = f"""You are a senior VC partner reviewing market intelligence for investment decision.

{context}

Provide investment recommendation with this EXACT format:

DECISION: [GO/CAUTION/NO-GO]
EXECUTIVE_SUMMARY: [2 sentences max - key opportunity and main consideration]
RATIONALE_1: [Primary factor supporting decision - max 100 chars]
RATIONALE_2: [Secondary factor supporting decision - max 100 chars]  
RATIONALE_3: [Third factor supporting decision - max 100 chars]
RISK_1: [Top risk to monitor - max 100 chars]
RISK_2: [Second risk to monitor - max 100 chars]
OPPORTUNITY: [Market size/timing assessment - max 100 chars]
CONFIDENCE: [High/Medium/Low]
CONFIDENCE_REASON: [Why this confidence level - max 50 chars]

Requirements:
- DECISION must be exactly: GO, CAUTION, or NO-GO
- Keep responses concise for 800 character total limit
- Focus on investment viability, not startup claims
- Consider red flags in decision making"""

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert VC partner focused on investment decision making."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.3
            )
            
            # Parse GPT-4 response
            content = response.choices[0].message.content
            return self._parse_investment_response(content, red_flags)
            
        except Exception as e:
            logger.error(f"❌ GPT-4 investment recommendation failed: {e}")
            return self._get_heuristic_decision(result, red_flags)
    
    def _build_synthesis_context(self, result, red_flags: List[Dict]) -> str:
        """Build comprehensive context string for GPT-4"""
        context = ""
        
        # Market Profile
        if hasattr(result, 'market_profile'):
            profile = result.market_profile
            context += f"""
MARKET PROFILE:
- Solution: {getattr(profile, 'solution', 'Unknown')}
- Sub-vertical: {getattr(profile, 'sub_vertical', 'Unknown')}
- Vertical: {getattr(profile, 'vertical', 'Unknown')}
- Target: {getattr(profile, 'target_market', 'Unknown')}
- Geographic Focus: {getattr(profile, 'geo_focus', 'Unknown')}
"""
        
        # Competitive Analysis Summary
        if hasattr(result, 'competitive_analysis'):
            comp_data = result.competitive_analysis
            if isinstance(comp_data, dict):
                independent = comp_data.get('independent_analysis', {})
                context += f"""
COMPETITIVE INTELLIGENCE:
- Market Position: {independent.get('market_position', 'Unknown')}
- Threat Level: {independent.get('threat_level', 'Unknown')}
- Confidence: {independent.get('confidence_score', 0):.2f}
- Sources Analyzed: {independent.get('sources_count', 0)}
"""
        
        # Market Validation Summary  
        if hasattr(result, 'market_validation'):
            validation = result.market_validation
            if isinstance(validation, dict):
                context += f"""
MARKET VALIDATION:
- Validation Score: {validation.get('validation_score', 0)}/10
- Expert Opinions: {len(validation.get('expert_opinions', []))}
- Precedent Cases: {len(validation.get('precedent_cases', []))}
"""
        
        # Funding Benchmarks Summary
        if hasattr(result, 'funding_benchmarks'):
            funding = result.funding_benchmarks
            if isinstance(funding, dict):
                context += f"""
FUNDING LANDSCAPE:
- Climate: {funding.get('funding_climate', 'Unknown')}
- Similar Deals: {len(funding.get('similar_deals', []))}
- Funding Patterns: {len(funding.get('funding_patterns', []))}
"""
        
        # Red Flags
        if red_flags:
            context += f"""
RED FLAGS DETECTED:
"""
            for flag in red_flags:
                context += f"- {flag['severity'].upper()}: {flag['reason']}\n"
        
        return context
    
    def _parse_investment_response(self, content: str, red_flags: List[Dict]) -> InvestmentDecision:
        """Parse GPT-4 response into InvestmentDecision structure"""
        decision = InvestmentDecision()
        decision.red_flags = red_flags
        
        try:
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('DECISION:'):
                    decision.decision = line.replace('DECISION:', '').strip()
                elif line.startswith('EXECUTIVE_SUMMARY:'):
                    decision.executive_summary = line.replace('EXECUTIVE_SUMMARY:', '').strip()
                elif line.startswith('RATIONALE_1:'):
                    decision.key_rationale.append(line.replace('RATIONALE_1:', '').strip())
                elif line.startswith('RATIONALE_2:'):
                    decision.key_rationale.append(line.replace('RATIONALE_2:', '').strip())
                elif line.startswith('RATIONALE_3:'):
                    decision.key_rationale.append(line.replace('RATIONALE_3:', '').strip())
                elif line.startswith('RISK_1:'):
                    decision.key_risks.append(line.replace('RISK_1:', '').strip())
                elif line.startswith('RISK_2:'):
                    decision.key_risks.append(line.replace('RISK_2:', '').strip())
                elif line.startswith('OPPORTUNITY:'):
                    decision.market_opportunity = line.replace('OPPORTUNITY:', '').strip()
                elif line.startswith('CONFIDENCE:'):
                    decision.confidence_level = line.replace('CONFIDENCE:', '').strip()
                elif line.startswith('CONFIDENCE_REASON:'):
                    decision.confidence_reason = line.replace('CONFIDENCE_REASON:', '').strip()
            
            # Validate decision
            if decision.decision not in ['GO', 'CAUTION', 'NO-GO']:
                decision.decision = 'CAUTION'  # Safe default
                
            return decision
            
        except Exception as e:
            logger.error(f"❌ Failed to parse investment response: {e}")
            return self._get_heuristic_decision(None, red_flags)
    
    def _get_heuristic_decision(self, result, red_flags: List[Dict]) -> InvestmentDecision:
        """Fallback heuristic decision when GPT-4 fails"""
        decision = InvestmentDecision()
        decision.red_flags = red_flags
        
        # Simple heuristic based on red flags
        high_severity_flags = [f for f in red_flags if f['severity'] == 'high']
        medium_severity_flags = [f for f in red_flags if f['severity'] == 'medium']
        
        if len(high_severity_flags) >= 2:
            decision.decision = 'NO-GO'
            decision.executive_summary = 'Multiple high-severity risks identified. Market requires significant due diligence before investment consideration.'
        elif len(high_severity_flags) == 1 or len(medium_severity_flags) >= 3:
            decision.decision = 'CAUTION'  
            decision.executive_summary = 'Market opportunity exists but significant risks require careful evaluation and mitigation strategies.'
        else:
            decision.decision = 'CAUTION'  # Conservative default
            decision.executive_summary = 'Market analysis indicates potential opportunity. Recommend detailed due diligence before investment decision.'
            
        decision.key_rationale = ['Heuristic analysis based on risk factors', 'Conservative approach due to analysis limitations']
        decision.key_risks = ['Analysis incomplete - manual review required', 'Decision based on limited automated assessment']
        decision.market_opportunity = 'Market opportunity assessment requires human review'
        decision.confidence_level = 'Low'
        decision.confidence_reason = 'Automated fallback analysis'
        
        return decision
    
    def _get_fallback_decision(self, error_msg: str) -> InvestmentDecision:
        """Ultimate fallback when everything fails"""
        decision = InvestmentDecision()
        decision.decision = 'CAUTION'
        decision.executive_summary = f'Investment decision analysis failed. Manual review required.'
        decision.key_rationale = ['Automated analysis unavailable']
        decision.key_risks = ['Analysis system error - human review needed']
        decision.market_opportunity = 'Cannot assess - system error'
        decision.confidence_level = 'Low'
        decision.confidence_reason = 'System error'
        decision.red_flags = [{
            'type': 'system',
            'severity': 'high', 
            'reason': f'Analysis failed: {error_msg[:100]}'
        }]
        
        return decision
    
    def _estimate_character_count(self, decision: InvestmentDecision) -> int:
        """Estimate character count of formatted decision"""
        count = 0
        count += len(f"🧠 **INVESTMENT DECISION: {decision.decision}**\n\n")
        count += len(f"📋 {decision.executive_summary}\n\n")
        count += len("⚖️ **RATIONALE:**\n")
        for rationale in decision.key_rationale:
            count += len(f"• {rationale}\n")
        count += len("\n🚨 **KEY RISKS:**\n")
        for risk in decision.key_risks:
            count += len(f"• {risk}\n")
        count += len(f"\n💰 **OPPORTUNITY:** {decision.market_opportunity}\n")
        count += len(f"📊 **CONFIDENCE:** {decision.confidence_level}")
        if decision.confidence_reason:
            count += len(f" - {decision.confidence_reason}")
        
        if decision.red_flags:
            count += len("\n🔍 **RED FLAGS:**\n")
            for flag in decision.red_flags:
                count += len(f"• {flag['reason']}\n")
        
        return count
    
    def _optimize_for_character_limit(self, decision: InvestmentDecision) -> InvestmentDecision:
        """Optimize decision for character limit by truncating less critical parts"""
        
        # Priority order: Decision > Executive Summary > Rationale > Risks > Opportunity
        
        # Truncate rationale items if too long
        for i, rationale in enumerate(decision.key_rationale):
            if len(rationale) > 90:
                decision.key_rationale[i] = rationale[:87] + "..."
        
        # Truncate risk items if too long
        for i, risk in enumerate(decision.key_risks):
            if len(risk) > 90:
                decision.key_risks[i] = risk[:87] + "..."
        
        # Truncate opportunity if too long
        if len(decision.market_opportunity) > 90:
            decision.market_opportunity = decision.market_opportunity[:87] + "..."
            
        # Truncate executive summary if desperate  
        if len(decision.executive_summary) > 200:
            decision.executive_summary = decision.executive_summary[:197] + "..."
        
        # Remove red flags display if still too long (will be in PDF)
        estimated_without_flags = self._estimate_character_count(decision) - sum(len(f"• {flag['reason']}\n") for flag in decision.red_flags)
        if estimated_without_flags > 800:
            decision.red_flags = []  # Remove from display, keep in data
        
        return decision