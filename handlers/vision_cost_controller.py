"""
Story 1.2 AC4: Intelligent Cost Control System with Budget Tracking

Advanced cost management for GPT Vision API usage with real-time tracking,
budget enforcement, intelligent processing decisions, and cost optimization
strategies to maintain development budget control.
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class VisionAPICall:
    """Track individual Vision API calls for cost analysis"""
    timestamp: float
    page_number: int
    cost_usd: float
    image_size_kb: float
    processing_time_seconds: float
    success: bool
    model_used: str = "gpt-4-vision-preview"

@dataclass 
class DailyCostSummary:
    """Daily cost tracking summary"""
    date: str
    total_calls: int
    total_cost_usd: float
    successful_calls: int
    failed_calls: int
    avg_cost_per_call: float
    budget_utilization_pct: float

class VisionCostController:
    """
    Intelligent cost control system for GPT Vision API usage.
    Manages budgets, tracks spending, and makes cost-optimization decisions.
    """
    
    def __init__(self):
        # Budget configuration
        self.daily_budget = float(os.getenv('VISION_DAILY_BUDGET', '5.0'))  # $5 default
        self.weekly_budget = float(os.getenv('VISION_WEEKLY_BUDGET', '25.0'))  # $25 default
        self.monthly_budget = float(os.getenv('VISION_MONTHLY_BUDGET', '100.0'))  # $100 default
        
        # Cost thresholds for decision making
        self.budget_warning_threshold = float(os.getenv('VISION_WARNING_THRESHOLD', '0.8'))  # 80%
        self.budget_stop_threshold = float(os.getenv('VISION_STOP_THRESHOLD', '0.95'))  # 95%
        
        # Cost optimization settings
        self.cost_per_call = float(os.getenv('VISION_COST_PER_CALL', '0.00765'))  # High detail pricing
        self.enable_cost_optimization = os.getenv('VISION_COST_OPTIMIZATION', 'true').lower() == 'true'
        
        # Storage for cost tracking (in-memory for now, could be extended to persistent storage)
        self.api_calls_history: List[VisionAPICall] = []
        self.daily_summaries: Dict[str, DailyCostSummary] = {}
        
        # Initialize cost tracking
        self._initialize_cost_tracking()
        
        logger.info(f"💰 Vision Cost Controller initialized:")
        logger.info(f"   Daily Budget: ${self.daily_budget:.2f}")
        logger.info(f"   Weekly Budget: ${self.weekly_budget:.2f}")
        logger.info(f"   Monthly Budget: ${self.monthly_budget:.2f}")
        logger.info(f"   Cost per Call: ${self.cost_per_call:.5f}")
        logger.info(f"   Warning Threshold: {self.budget_warning_threshold:.0%}")
        logger.info(f"   Stop Threshold: {self.budget_stop_threshold:.0%}")
    
    def _initialize_cost_tracking(self):
        """Initialize cost tracking system"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        if today not in self.daily_summaries:
            self.daily_summaries[today] = DailyCostSummary(
                date=today,
                total_calls=0,
                total_cost_usd=0.0,
                successful_calls=0,
                failed_calls=0,
                avg_cost_per_call=0.0,
                budget_utilization_pct=0.0
            )
    
    def check_budget_availability(self, pages_to_process: int) -> Dict[str, Any]:
        """
        Check if processing pages is within budget limits
        
        Args:
            pages_to_process: Number of pages to process with Vision
            
        Returns:
            Budget check results with recommendations
        """
        
        estimated_cost = pages_to_process * self.cost_per_call
        
        # Get current spending
        daily_spent = self._get_daily_spending()
        weekly_spent = self._get_weekly_spending()
        monthly_spent = self._get_monthly_spending()
        
        # Calculate remaining budgets
        daily_remaining = max(0, self.daily_budget - daily_spent)
        weekly_remaining = max(0, self.weekly_budget - weekly_spent)
        monthly_remaining = max(0, self.monthly_budget - monthly_spent)
        
        # Determine limiting budget
        limiting_budget = min(daily_remaining, weekly_remaining, monthly_remaining)
        max_affordable_pages = int(limiting_budget / self.cost_per_call) if self.cost_per_call > 0 else pages_to_process
        
        # Budget status analysis
        can_afford_all = estimated_cost <= limiting_budget
        budget_status = self._determine_budget_status(daily_spent / self.daily_budget)
        
        # Generate recommendations
        recommendations = []
        if not can_afford_all:
            recommendations.append(f"Reduce pages from {pages_to_process} to {max_affordable_pages} to stay within budget")
        
        if budget_status == 'WARNING':
            recommendations.append("Approaching budget limit - consider text-only processing for remaining documents")
        elif budget_status == 'CRITICAL':
            recommendations.append("Budget nearly exhausted - prioritize only highest-value pages")
        
        return {
            'can_afford_all_pages': can_afford_all,
            'estimated_cost': estimated_cost,
            'max_affordable_pages': max_affordable_pages,
            'budget_status': budget_status,
            'budget_details': {
                'daily': {'spent': daily_spent, 'remaining': daily_remaining, 'limit': self.daily_budget},
                'weekly': {'spent': weekly_spent, 'remaining': weekly_remaining, 'limit': self.weekly_budget},
                'monthly': {'spent': monthly_spent, 'remaining': monthly_remaining, 'limit': self.monthly_budget}
            },
            'recommendations': recommendations,
            'limiting_factor': self._get_limiting_budget_factor(daily_remaining, weekly_remaining, monthly_remaining)
        }
    
    def should_process_with_vision(self, page_complexity_score: float, page_number: int, 
                                 total_pages_in_doc: int) -> Dict[str, Any]:
        """
        Intelligent decision on whether to use Vision for a specific page
        
        Args:
            page_complexity_score: Visual complexity score (0.0 - 1.0)
            page_number: Page number being evaluated
            total_pages_in_doc: Total pages in document
            
        Returns:
            Processing decision with reasoning
        """
        
        # Get current budget status
        budget_check = self.check_budget_availability(1)  # Check for 1 page
        
        # Base decision factors
        decision_factors = {
            'complexity_score': page_complexity_score,
            'budget_available': budget_check['can_afford_all_pages'],
            'budget_status': budget_check['budget_status'],
            'page_priority': self._calculate_page_priority(page_number, total_pages_in_doc),
            'cost_optimization_enabled': self.enable_cost_optimization
        }
        
        # Decision logic
        should_process = False
        reasoning = []
        
        # 1. Budget check - must have budget
        if not budget_check['can_afford_all_pages']:
            reasoning.append("Insufficient budget for Vision processing")
            return {
                'should_process': False,
                'decision_factors': decision_factors,
                'reasoning': reasoning,
                'alternative': 'text_only'
            }
        
        # 2. Critical budget status - only highest priority
        if budget_check['budget_status'] == 'CRITICAL':
            if page_complexity_score >= 0.9 and decision_factors['page_priority'] >= 0.8:
                should_process = True
                reasoning.append("Critical budget but extremely high priority page")
            else:
                reasoning.append("Critical budget status - conserving for highest priority pages")
        
        # 3. Warning status - selective processing
        elif budget_check['budget_status'] == 'WARNING':
            if page_complexity_score >= 0.7 or decision_factors['page_priority'] >= 0.7:
                should_process = True
                reasoning.append("Warning status but high value page")
            else:
                reasoning.append("Warning status - processing only high-value pages")
        
        # 4. Normal budget status - standard complexity threshold
        else:
            complexity_threshold = 0.6 if self.enable_cost_optimization else 0.4
            if page_complexity_score >= complexity_threshold:
                should_process = True
                reasoning.append(f"Complexity score {page_complexity_score:.2f} exceeds threshold {complexity_threshold:.2f}")
            else:
                reasoning.append(f"Complexity score {page_complexity_score:.2f} below threshold {complexity_threshold:.2f}")
        
        # 5. Special cases - always process certain page types
        if page_number <= 3:  # First 3 pages often contain key visuals
            if not should_process and page_complexity_score >= 0.5:
                should_process = True
                reasoning.append("First 3 pages with moderate complexity - strategic processing")
        
        return {
            'should_process': should_process,
            'decision_factors': decision_factors,
            'reasoning': reasoning,
            'alternative': 'text_only' if not should_process else 'vision',
            'estimated_cost': self.cost_per_call if should_process else 0.0
        }
    
    def record_api_call(self, page_number: int, cost_usd: float, image_size_kb: float, 
                       processing_time: float, success: bool) -> None:
        """Record Vision API call for cost tracking"""
        
        api_call = VisionAPICall(
            timestamp=time.time(),
            page_number=page_number,
            cost_usd=cost_usd,
            image_size_kb=image_size_kb,
            processing_time_seconds=processing_time,
            success=success
        )
        
        self.api_calls_history.append(api_call)
        self._update_daily_summary(api_call)
        
        # Log the call
        status = "✅ SUCCESS" if success else "❌ FAILED"
        logger.info(f"💰 Vision API Call Recorded: Page {page_number}, ${cost_usd:.5f}, {status}")
        
        # Check for budget warnings
        daily_spent = self._get_daily_spending()
        utilization = daily_spent / self.daily_budget
        
        if utilization >= self.budget_stop_threshold:
            logger.warning(f"🚨 CRITICAL: Daily budget {utilization:.0%} used (${daily_spent:.2f}/${self.daily_budget:.2f})")
        elif utilization >= self.budget_warning_threshold:
            logger.warning(f"⚠️ WARNING: Daily budget {utilization:.0%} used (${daily_spent:.2f}/${self.daily_budget:.2f})")
    
    def get_cost_summary(self, period: str = 'daily') -> Dict[str, Any]:
        """
        Get comprehensive cost summary for specified period
        
        Args:
            period: 'daily', 'weekly', or 'monthly'
            
        Returns:
            Detailed cost summary
        """
        
        if period == 'daily':
            spent = self._get_daily_spending()
            budget = self.daily_budget
            calls = self._get_daily_calls()
        elif period == 'weekly':
            spent = self._get_weekly_spending()
            budget = self.weekly_budget
            calls = self._get_weekly_calls()
        elif period == 'monthly':
            spent = self._get_monthly_spending()
            budget = self.monthly_budget
            calls = self._get_monthly_calls()
        else:
            raise ValueError(f"Invalid period: {period}")
        
        utilization = (spent / budget) * 100 if budget > 0 else 0
        remaining = max(0, budget - spent)
        
        return {
            'period': period,
            'total_spent_usd': spent,
            'budget_usd': budget,
            'remaining_usd': remaining,
            'utilization_pct': utilization,
            'total_calls': len(calls),
            'successful_calls': len([call for call in calls if call.success]),
            'failed_calls': len([call for call in calls if not call.success]),
            'avg_cost_per_call': spent / len(calls) if calls else 0,
            'budget_status': self._determine_budget_status(utilization / 100),
            'cost_efficiency': {
                'avg_processing_time': sum(call.processing_time_seconds for call in calls) / len(calls) if calls else 0,
                'avg_image_size_kb': sum(call.image_size_kb for call in calls) / len(calls) if calls else 0,
                'success_rate_pct': (len([call for call in calls if call.success]) / len(calls)) * 100 if calls else 0
            }
        }
    
    def optimize_page_selection(self, page_analyses: List[Dict], max_budget_usd: float) -> List[Dict]:
        """
        Optimize page selection based on value/cost ratio within budget
        
        Args:
            page_analyses: List of page analysis results with complexity scores
            max_budget_usd: Maximum budget to spend
            
        Returns:
            Optimized list of pages to process with Vision
        """
        
        max_pages = int(max_budget_usd / self.cost_per_call)
        
        # Calculate value score for each page
        scored_pages = []
        for page in page_analyses:
            value_score = self._calculate_page_value_score(page)
            scored_pages.append({
                **page,
                'value_score': value_score,
                'cost_usd': self.cost_per_call
            })
        
        # Sort by value score (descending)
        sorted_pages = sorted(scored_pages, key=lambda x: x['value_score'], reverse=True)
        
        # Select top pages within budget
        selected_pages = sorted_pages[:max_pages]
        
        total_cost = len(selected_pages) * self.cost_per_call
        cost_savings = (len(page_analyses) - len(selected_pages)) * self.cost_per_call
        
        logger.info(f"💡 Page Selection Optimization:")
        logger.info(f"   Total Pages: {len(page_analyses)}")
        logger.info(f"   Selected for Vision: {len(selected_pages)}")
        logger.info(f"   Estimated Cost: ${total_cost:.3f}")
        logger.info(f"   Cost Savings: ${cost_savings:.3f}")
        
        return selected_pages
    
    def _get_daily_spending(self) -> float:
        """Get spending for current day"""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.daily_summaries.get(today, DailyCostSummary("", 0, 0.0, 0, 0, 0.0, 0.0)).total_cost_usd
    
    def _get_weekly_spending(self) -> float:
        """Get spending for current week"""
        week_ago = datetime.now() - timedelta(days=7)
        return sum(call.cost_usd for call in self.api_calls_history 
                  if call.timestamp >= week_ago.timestamp() and call.success)
    
    def _get_monthly_spending(self) -> float:
        """Get spending for current month"""
        month_ago = datetime.now() - timedelta(days=30)
        return sum(call.cost_usd for call in self.api_calls_history 
                  if call.timestamp >= month_ago.timestamp() and call.success)
    
    def _get_daily_calls(self) -> List[VisionAPICall]:
        """Get API calls for current day"""
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
        return [call for call in self.api_calls_history if call.timestamp >= today_start]
    
    def _get_weekly_calls(self) -> List[VisionAPICall]:
        """Get API calls for current week"""
        week_ago = datetime.now() - timedelta(days=7)
        return [call for call in self.api_calls_history if call.timestamp >= week_ago.timestamp()]
    
    def _get_monthly_calls(self) -> List[VisionAPICall]:
        """Get API calls for current month"""
        month_ago = datetime.now() - timedelta(days=30)
        return [call for call in self.api_calls_history if call.timestamp >= month_ago.timestamp()]
    
    def _update_daily_summary(self, api_call: VisionAPICall):
        """Update daily cost summary with new API call"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        if today not in self.daily_summaries:
            self._initialize_cost_tracking()
        
        summary = self.daily_summaries[today]
        summary.total_calls += 1
        summary.total_cost_usd += api_call.cost_usd
        
        if api_call.success:
            summary.successful_calls += 1
        else:
            summary.failed_calls += 1
        
        summary.avg_cost_per_call = summary.total_cost_usd / summary.total_calls if summary.total_calls > 0 else 0
        summary.budget_utilization_pct = (summary.total_cost_usd / self.daily_budget) * 100
    
    def _determine_budget_status(self, utilization_ratio: float) -> str:
        """Determine budget status based on utilization"""
        if utilization_ratio >= self.budget_stop_threshold:
            return 'CRITICAL'
        elif utilization_ratio >= self.budget_warning_threshold:
            return 'WARNING'
        else:
            return 'NORMAL'
    
    def _get_limiting_budget_factor(self, daily_remaining: float, weekly_remaining: float, 
                                  monthly_remaining: float) -> str:
        """Identify which budget is the limiting factor"""
        min_remaining = min(daily_remaining, weekly_remaining, monthly_remaining)
        
        if min_remaining == daily_remaining:
            return 'daily'
        elif min_remaining == weekly_remaining:
            return 'weekly'
        else:
            return 'monthly'
    
    def _calculate_page_priority(self, page_number: int, total_pages: int) -> float:
        """Calculate page priority score (0.0 - 1.0)"""
        # Higher priority for early pages and last few pages
        if page_number <= 3:  # First 3 pages
            return 0.9
        elif page_number >= total_pages - 2:  # Last 2 pages
            return 0.7
        else:
            # Middle pages have lower priority
            return 0.5
    
    def _calculate_page_value_score(self, page_analysis: Dict) -> float:
        """Calculate overall value score for a page"""
        complexity = page_analysis.get('visual_score', 0.0)
        has_images = page_analysis.get('has_images', False)
        has_drawings = page_analysis.get('has_drawings', False)
        page_num = page_analysis.get('page_number', 0)
        
        # Base score from complexity
        value_score = complexity * 0.6
        
        # Bonus for images and drawings
        if has_images:
            value_score += 0.2
        if has_drawings:
            value_score += 0.15
        
        # Priority bonus for early pages
        if page_num <= 3:
            value_score += 0.1
        
        return min(value_score, 1.0)


# Global instance for easy access
vision_cost_controller = VisionCostController()