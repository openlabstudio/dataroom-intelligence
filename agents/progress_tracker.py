"""
Progress Tracker for Multi-Agent Market Research
Real-time progress updates for enhanced user experience

Phase 2B.1: Chain of Thought with Progress UX
"""

import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class AgentPhase:
    """Represents a single phase in the market research process"""
    id: str
    name: str
    description: str
    estimated_duration_minutes: int
    status: str = "pending"  # pending, running, completed, error
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    emoji: str = "⚪"

    def __post_init__(self):
        """Set status emojis based on phase status"""
        status_emojis = {
            "pending": "⚪",
            "running": "🔄",
            "completed": "✅",
            "error": "❌"
        }
        if self.status in status_emojis:
            self.emoji = status_emojis[self.status]

class ProgressTracker:
    """Tracks and reports progress for multi-agent market research"""

    def __init__(self, slack_client=None, channel=None, thread_ts=None):
        self.slack_client = slack_client
        self.channel = channel
        self.thread_ts = thread_ts
        self.start_time = datetime.now()
        self.message_ts = None  # Will store timestamp of progress message

        # Define all research phases
        self.phases = [
            AgentPhase(
                id="market_detection",
                name="Market Detection & Profiling",
                description="Identifying market vertical, target segments, and business model",
                estimated_duration_minutes=2
            ),
            AgentPhase(
                id="competitive_intelligence",
                name="Competitive Intelligence",
                description="Analyzing competitor landscape and market positioning",
                estimated_duration_minutes=3
            ),
            AgentPhase(
                id="market_validation",
                name="TAM/SAM Validation",
                description="Validating market size claims with external data",
                estimated_duration_minutes=3
            ),
            AgentPhase(
                id="funding_benchmarking",
                name="Funding & Metrics Benchmarking",
                description="Comparing financial metrics against industry standards",
                estimated_duration_minutes=2
            ),
            AgentPhase(
                id="critical_synthesis",
                name="Critical Assessment & Report",
                description="Synthesizing findings into investment-grade analysis",
                estimated_duration_minutes=2
            )
        ]

        self.current_phase_index = 0
        self.detected_market = "Unknown"

    def get_total_estimated_time(self) -> int:
        """Calculate total estimated time in minutes"""
        return sum(phase.estimated_duration_minutes for phase in self.phases)

    def get_elapsed_time(self) -> str:
        """Get formatted elapsed time"""
        elapsed = datetime.now() - self.start_time
        minutes = int(elapsed.total_seconds() // 60)
        seconds = int(elapsed.total_seconds() % 60)
        return f"{minutes}m {seconds}s"

    def get_estimated_remaining_time(self) -> str:
        """Calculate estimated time remaining"""
        remaining_phases = self.phases[self.current_phase_index:]
        remaining_minutes = sum(phase.estimated_duration_minutes for phase in remaining_phases)

        if remaining_minutes <= 0:
            return "Complete"
        elif remaining_minutes < 60:
            return f"{remaining_minutes}m"
        else:
            hours = remaining_minutes // 60
            mins = remaining_minutes % 60
            return f"{hours}h {mins}m"

    def format_progress_message(self) -> str:
        """Format the complete progress status message"""

        # Header with market detection and timing
        market_info = f"📊 Analyzing: {self.detected_market}" if self.detected_market != "Unknown" else "📊 Market Detection In Progress"
        elapsed = self.get_elapsed_time()
        remaining = self.get_estimated_remaining_time()

        header = f"""🔍 **MARKET RESEARCH IN PROGRESS**

{market_info}
⏱️ Elapsed: {elapsed} | Remaining: ~{remaining}
🔄 Real-time Analysis...

**Research Pipeline:**"""

        # Format each phase with current status
        phase_lines = []
        for i, phase in enumerate(self.phases):
            phase_line = f"{phase.emoji} {i+1}/5 {phase.name}"
            if phase.status == "running":
                phase_line += " (analyzing...)"
            elif phase.status == "completed" and phase.end_time:
                duration = (phase.end_time - phase.start_time).total_seconds() if phase.start_time else 0
                phase_line += f" ({duration:.0f}s)"

            phase_lines.append(phase_line)

        phases_text = "\n".join(phase_lines)

        # Footer with helpful info
        footer = "\n💡 *Comprehensive analysis in progress - detailed report will follow*"

        return f"{header}\n{phases_text}{footer}"

# Test mode helper for development
def create_test_progress_tracker() -> ProgressTracker:
    """Create progress tracker for testing without Slack integration"""
    logger.info("🧪 Creating test progress tracker (no Slack)")
    return ProgressTracker()

# Simple test function
def test_progress_tracker():
    """Test the progress tracker functionality"""
    tracker = create_test_progress_tracker()
    logger.info("✅ ProgressTracker test successful")
    print(tracker.format_progress_message())
    return True

if __name__ == "__main__":
    test_progress_tracker()
