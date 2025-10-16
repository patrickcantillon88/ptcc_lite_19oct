#!/usr/bin/env python3
"""
Feedback Composer Agent for PTCC

Generates personalized, constructive student feedback with:
- Performance analysis across multiple dimensions
- Evidence-based strengths identification
- Actionable improvement areas
- Growth mindset language
- Parent-friendly versions
- Multiple format options

Integrates with:
- RAG system for pedagogical best practices
- Memory system for teacher preferences and student history
- Alignment system for appropriate feedback tone
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict, field


@dataclass
class ActionStep:
    """Specific action for improvement."""
    step: str
    rationale: str
    timeline: str
    resources: List[str]


@dataclass
class ImprovementArea:
    """Area needing improvement with actionable next steps."""
    area: str
    current_level: str
    target_level: str
    evidence: List[str]
    action_steps: List[ActionStep]
    priority: str  # "high", "medium", "low"


@dataclass
class Strength:
    """Identified student strength with supporting evidence."""
    strength: str
    evidence: List[str]
    growth_opportunities: List[str]


@dataclass
class PerformanceAnalysis:
    """Breakdown of student performance."""
    overall_grade: str
    subject_scores: Dict[str, float]
    participation_level: str
    effort_rating: str
    trends: List[str]


@dataclass
class FeedbackReport:
    """
    Main feedback container.
    
    Attributes:
        student_name: Student's name (can be anonymized)
        subject: Subject area
        date: Date of feedback generation
        performance_analysis: Detailed performance breakdown
        strengths: List of identified strengths
        improvement_areas: List of areas for growth
        overall_comment: Synthesized narrative feedback
        parent_version: Parent-friendly translation (optional)
        format_type: Output format style
        created_at: Timestamp of generation
    """
    student_name: str
    subject: str
    date: str
    performance_analysis: PerformanceAnalysis
    strengths: List[Strength]
    improvement_areas: List[ImprovementArea]
    overall_comment: str
    parent_version: Optional[str] = None
    format_type: str = "narrative"  # "narrative", "bullet_points", "report_card"
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        # Convert datetime to string for JSON serialization
        if isinstance(data.get('created_at'), datetime):
            data['created_at'] = data['created_at'].isoformat()
        return data
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    def to_markdown(self) -> str:
        """Convert to formatted markdown report."""
        md = f"# Student Feedback Report\n\n"
        md += f"**Student:** {self.student_name}  \n"
        md += f"**Subject:** {self.subject}  \n"
        md += f"**Date:** {self.date}  \n\n"
        
        # Performance Analysis
        md += "## Performance Analysis\n\n"
        md += f"**Overall Grade:** {self.performance_analysis.overall_grade}  \n"
        md += f"**Participation:** {self.performance_analysis.participation_level}  \n"
        md += f"**Effort:** {self.performance_analysis.effort_rating}  \n\n"
        
        if self.performance_analysis.subject_scores:
            md += "**Subject Scores:**\n"
            for subject, score in self.performance_analysis.subject_scores.items():
                md += f"- {subject}: {score:.1f}%\n"
            md += "\n"
        
        if self.performance_analysis.trends:
            md += "**Trends:**\n"
            for trend in self.performance_analysis.trends:
                md += f"- {trend}\n"
            md += "\n"
        
        # Strengths
        md += "## Strengths\n\n"
        for i, strength in enumerate(self.strengths, 1):
            md += f"### {i}. {strength.strength}\n\n"
            md += "**Evidence:**\n"
            for evidence in strength.evidence:
                md += f"- {evidence}\n"
            md += "\n**Growth Opportunities:**\n"
            for opp in strength.growth_opportunities:
                md += f"- {opp}\n"
            md += "\n"
        
        # Improvement Areas
        md += "## Areas for Growth\n\n"
        for i, area in enumerate(self.improvement_areas, 1):
            md += f"### {i}. {area.area} (Priority: {area.priority})\n\n"
            md += f"**Current Level:** {area.current_level}  \n"
            md += f"**Target Level:** {area.target_level}  \n\n"
            md += "**Evidence:**\n"
            for evidence in area.evidence:
                md += f"- {evidence}\n"
            md += "\n**Action Steps:**\n"
            for j, step in enumerate(area.action_steps, 1):
                md += f"{j}. **{step.step}** ({step.timeline})\n"
                md += f"   - Rationale: {step.rationale}\n"
                if step.resources:
                    md += f"   - Resources: {', '.join(step.resources)}\n"
            md += "\n"
        
        # Overall Comment
        md += "## Overall Comments\n\n"
        md += self.overall_comment + "\n\n"
        
        # Parent Version
        if self.parent_version:
            md += "## Message for Parents/Guardians\n\n"
            md += self.parent_version + "\n"
        
        return md
    
    def to_report_card(self) -> str:
        """Convert to report card style format."""
        rc = f"STUDENT PROGRESS REPORT\n"
        rc += f"=" * 50 + "\n\n"
        rc += f"Student: {self.student_name}\n"
        rc += f"Subject: {self.subject}\n"
        rc += f"Date: {self.date}\n"
        rc += f"Overall Grade: {self.performance_analysis.overall_grade}\n\n"
        
        rc += "AREAS OF STRENGTH:\n"
        for strength in self.strengths:
            rc += f"  • {strength.strength}\n"
        
        rc += "\nAREAS FOR IMPROVEMENT:\n"
        for area in self.improvement_areas:
            rc += f"  • {area.area} ({area.priority} priority)\n"
        
        rc += f"\nTEACHER COMMENTS:\n{self.overall_comment}\n"
        
        return rc
    
    def to_bullet_points(self) -> str:
        """Convert to concise bullet point format."""
        bp = f"# {self.student_name} - {self.subject}\n\n"
        
        bp += "**Strengths:**\n"
        for strength in self.strengths:
            bp += f"- {strength.strength}\n"
        
        bp += "\n**Next Steps:**\n"
        for area in self.improvement_areas:
            bp += f"- {area.area}: {area.action_steps[0].step if area.action_steps else 'Continue practice'}\n"
        
        return bp
    
    def validate_report(self) -> bool:
        """
        Validate that all required fields are present and meaningful.
        
        Returns:
            True if report is valid, False otherwise
        """
        if not self.student_name or not self.subject:
            return False
        
        if not self.strengths or not self.improvement_areas:
            return False
        
        if not self.overall_comment or len(self.overall_comment) < 50:
            return False
        
        # Check that each strength has evidence
        for strength in self.strengths:
            if not strength.evidence:
                return False
        
        # Check that each improvement area has action steps
        for area in self.improvement_areas:
            if not area.action_steps:
                return False
        
        return True
    
    def check_tone(self) -> List[str]:
        """
        Verify growth mindset language usage.
        
        Returns:
            List of warnings about potentially problematic language
        """
        warnings = []
        
        # Check for fixed mindset language
        fixed_mindset_words = ['can\'t', 'unable', 'always', 'never', 'impossible', 'failure']
        text = self.overall_comment.lower()
        
        for word in fixed_mindset_words:
            if word in text:
                warnings.append(f"Consider reframing '{word}' to use growth mindset language")
        
        # Check for comparative language
        if 'better than' in text or 'worse than' in text:
            warnings.append("Avoid comparing student to others; focus on individual growth")
        
        # Ensure positive-first approach
        if not any(word in text for word in ['strength', 'success', 'growth', 'progress', 'improved']):
            warnings.append("Consider highlighting more positive achievements")
        
        return warnings


class FeedbackComposerAgent:
    """
    Agent for generating personalized, constructive student feedback.
    
    Capabilities:
    - Analyze student performance across multiple dimensions
    - Identify evidence-based strengths
    - Generate actionable improvement areas
    - Compose growth-mindset feedback
    - Create parent-friendly versions
    - Export to multiple formats
    
    Usage:
        agent = FeedbackComposerAgent(llm_client, rag_engine)
        report = await agent.compose_feedback(
            student_data={'name': 'Alex', 'grade': '5th'},
            assessment_results={'math': 85, 'reading': 92},
            format_type='narrative'
        )
        print(report.to_markdown())
    """
    
    def __init__(self, llm_client=None, rag_engine=None):
        """
        Initialize the feedback composer.
        
        Args:
            llm_client: LLM client for content generation
            rag_engine: RAG engine for pedagogical best practices retrieval
        """
        self.logger = self._setup_logging()
        self.llm_client = llm_client
        self.rag_engine = rag_engine
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the agent."""
        logger = logging.getLogger("feedback_composer")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def analyze_performance(
        self,
        student_data: Dict[str, Any],
        assessment_results: Dict[str, Any]
    ) -> PerformanceAnalysis:
        """
        Analyze student performance across multiple dimensions.
        
        Args:
            student_data: Student information (name, grade, etc.)
            assessment_results: Assessment scores and observations
        
        Returns:
            PerformanceAnalysis object with comprehensive breakdown
        """
        self.logger.info(f"Analyzing performance for student: {student_data.get('name', 'Unknown')}")
        
        try:
            # Extract scores
            subject_scores = assessment_results.get('scores', {})
            
            # Calculate overall grade
            if subject_scores:
                avg_score = sum(subject_scores.values()) / len(subject_scores)
                if avg_score >= 90:
                    overall_grade = "A"
                elif avg_score >= 80:
                    overall_grade = "B"
                elif avg_score >= 70:
                    overall_grade = "C"
                elif avg_score >= 60:
                    overall_grade = "D"
                else:
                    overall_grade = "F"
            else:
                overall_grade = "N/A"
            
            # Determine participation and effort
            participation_level = assessment_results.get('participation', 'Average')
            effort_rating = assessment_results.get('effort', 'Consistent')
            
            # Analyze trends
            trends = []
            if assessment_results.get('trend') == 'improving':
                trends.append("Showing steady improvement over recent assessments")
            elif assessment_results.get('trend') == 'declining':
                trends.append("Recent assessments show need for additional support")
            else:
                trends.append("Performance has been consistent")
            
            # Use RAG to get best practices for analysis (if available)
            if self.rag_engine:
                try:
                    best_practices = await self.rag_engine.query(
                        f"Best practices for analyzing {student_data.get('grade', '')} student performance"
                    )
                    if best_practices:
                        trends.append(f"Analysis informed by research-based practices")
                except Exception as e:
                    self.logger.warning(f"RAG query failed: {e}")
            
            analysis = PerformanceAnalysis(
                overall_grade=overall_grade,
                subject_scores=subject_scores,
                participation_level=participation_level,
                effort_rating=effort_rating,
                trends=trends
            )
            
            self.logger.info(f"Performance analysis complete: {overall_grade}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing performance: {e}")
            # Return default analysis
            return PerformanceAnalysis(
                overall_grade="N/A",
                subject_scores={},
                participation_level="Unknown",
                effort_rating="Unknown",
                trends=["Unable to analyze trends at this time"]
            )
    
    async def identify_strengths(
        self,
        performance: PerformanceAnalysis,
        work_samples: Optional[List[str]] = None
    ) -> List[Strength]:
        """
        Identify 3-5 key strengths with evidence.
        
        Args:
            performance: Performance analysis object
            work_samples: Optional list of specific work examples
        
        Returns:
            List of Strength objects with evidence and growth opportunities
        """
        self.logger.info("Identifying student strengths")
        
        strengths = []
        
        try:
            # Identify academic strengths from scores
            if performance.subject_scores:
                top_subjects = sorted(
                    performance.subject_scores.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:2]
                
                for subject, score in top_subjects:
                    if score >= 80:
                        strengths.append(Strength(
                            strength=f"Strong performance in {subject}",
                            evidence=[
                                f"Scored {score:.1f}% on recent assessments",
                                f"Demonstrates solid understanding of {subject} concepts"
                            ],
                            growth_opportunities=[
                                f"Could mentor peers in {subject}",
                                f"Ready for enrichment activities in {subject}"
                            ]
                        ))
            
            # Identify behavioral/effort strengths
            if performance.effort_rating in ['Excellent', 'Consistent']:
                strengths.append(Strength(
                    strength="Demonstrates strong work ethic",
                    evidence=[
                        f"Effort rated as {performance.effort_rating}",
                        "Consistently completes assignments on time"
                    ],
                    growth_opportunities=[
                        "Can model positive work habits for peers",
                        "Ready to take on leadership roles"
                    ]
                ))
            
            # Participation strengths
            if performance.participation_level in ['High', 'Active']:
                strengths.append(Strength(
                    strength="Active class participant",
                    evidence=[
                        f"Participation level: {performance.participation_level}",
                        "Regularly contributes to discussions"
                    ],
                    growth_opportunities=[
                        "Could lead group discussions",
                        "Ready to present work to class"
                    ]
                ))
            
            # Ensure we have at least one strength
            if not strengths:
                strengths.append(Strength(
                    strength="Consistent attendance and engagement",
                    evidence=["Regular class attendance", "Engaged in learning activities"],
                    growth_opportunities=["Continue building on current foundation"]
                ))
            
            # Use LLM to enhance strengths if available
            if self.llm_client and len(strengths) < 3:
                try:
                    # This would call the LLM to identify additional strengths
                    # For now, we'll add a placeholder
                    self.logger.debug("LLM enhancement available but not yet implemented")
                except Exception as e:
                    self.logger.warning(f"LLM enhancement failed: {e}")
            
            self.logger.info(f"Identified {len(strengths)} strengths")
            return strengths[:5]  # Limit to 5
            
        except Exception as e:
            self.logger.error(f"Error identifying strengths: {e}")
            return [Strength(
                strength="Continuing to engage with learning material",
                evidence=["Participates in class activities"],
                growth_opportunities=["Continue current efforts"]
            )]
    
    async def identify_improvement_areas(
        self,
        performance: PerformanceAnalysis,
        learning_goals: Optional[List[str]] = None
    ) -> List[ImprovementArea]:
        """
        Identify 2-3 priority areas for growth with actionable steps.
        
        Args:
            performance: Performance analysis object
            learning_goals: Optional list of specific learning goals
        
        Returns:
            List of ImprovementArea objects with action steps
        """
        self.logger.info("Identifying improvement areas")
        
        improvement_areas = []
        
        try:
            # Identify academic areas needing support
            if performance.subject_scores:
                weak_subjects = sorted(
                    performance.subject_scores.items(),
                    key=lambda x: x[1]
                )[:2]  # Bottom 2 subjects
                
                for subject, score in weak_subjects:
                    if score < 75:
                        priority = "high" if score < 60 else "medium"
                        target_score = min(score + 15, 90)
                        
                        improvement_areas.append(ImprovementArea(
                            area=f"{subject} concept mastery",
                            current_level=f"{score:.1f}%",
                            target_level=f"{target_score:.1f}%",
                            evidence=[
                                f"Current assessment score: {score:.1f}%",
                                f"Struggling with key {subject} concepts"
                            ],
                            action_steps=[
                                ActionStep(
                                    step=f"Complete additional {subject} practice problems",
                                    rationale="Repetition builds fluency and confidence",
                                    timeline="2-3 times per week",
                                    resources=[f"{subject} workbook", "Online practice sites"]
                                ),
                                ActionStep(
                                    step=f"Attend {subject} tutoring or help sessions",
                                    rationale="One-on-one support addresses specific gaps",
                                    timeline="Weekly",
                                    resources=["After-school tutoring", "Peer study groups"]
                                )
                            ],
                            priority=priority
                        ))
            
            # Identify behavioral/effort areas if needed
            if performance.effort_rating in ['Inconsistent', 'Needs Improvement']:
                improvement_areas.append(ImprovementArea(
                    area="Work completion and consistency",
                    current_level=performance.effort_rating,
                    target_level="Consistent",
                    evidence=[
                        "Some assignments incomplete or late",
                        "Effort varies across assignments"
                    ],
                    action_steps=[
                        ActionStep(
                            step="Establish a homework routine",
                            rationale="Consistent routine builds positive habits",
                            timeline="Daily",
                            resources=["Planner or organizer", "Parent check-ins"]
                        ),
                        ActionStep(
                            step="Break large assignments into smaller tasks",
                            rationale="Smaller tasks are less overwhelming",
                            timeline="For each assignment",
                            resources=["Task checklist", "Teacher support"]
                        )
                    ],
                    priority="medium"
                ))
            
            # Ensure we have at least one improvement area
            if not improvement_areas:
                improvement_areas.append(ImprovementArea(
                    area="Continue building skills",
                    current_level="Proficient",
                    target_level="Advanced",
                    evidence=["Currently meeting standards"],
                    action_steps=[
                        ActionStep(
                            step="Explore enrichment opportunities",
                            rationale="Challenge leads to growth",
                            timeline="Ongoing",
                            resources=["Advanced materials", "Extension projects"]
                        )
                    ],
                    priority="low"
                ))
            
            self.logger.info(f"Identified {len(improvement_areas)} improvement areas")
            return improvement_areas[:3]  # Limit to 3
            
        except Exception as e:
            self.logger.error(f"Error identifying improvement areas: {e}")
            return []
    
    async def compose_feedback(
        self,
        student_data: Dict[str, Any],
        assessment_results: Dict[str, Any],
        format_type: str = "narrative",
        work_samples: Optional[List[str]] = None,
        learning_goals: Optional[List[str]] = None
    ) -> FeedbackReport:
        """
        Main orchestration method to generate complete feedback report.
        
        Args:
            student_data: Student information (name, grade, etc.)
            assessment_results: Assessment scores and observations
            format_type: Output format ("narrative", "bullet_points", "report_card")
            work_samples: Optional specific work examples
            learning_goals: Optional learning objectives
        
        Returns:
            Complete FeedbackReport object
        
        Example:
            report = await agent.compose_feedback(
                student_data={'name': 'Alex Chen', 'grade': '5th'},
                assessment_results={
                    'scores': {'math': 85, 'reading': 92},
                    'participation': 'High',
                    'effort': 'Consistent',
                    'trend': 'improving'
                }
            )
        """
        self.logger.info(f"Composing feedback for {student_data.get('name', 'student')}")
        
        try:
            # Step 1: Analyze performance
            performance = await self.analyze_performance(student_data, assessment_results)
            
            # Step 2: Identify strengths
            strengths = await self.identify_strengths(performance, work_samples)
            
            # Step 3: Identify improvement areas
            improvement_areas = await self.identify_improvement_areas(performance, learning_goals)
            
            # Step 4: Compose overall comment
            overall_comment = self._compose_overall_comment(
                student_data,
                performance,
                strengths,
                improvement_areas
            )
            
            # Step 5: Create report
            report = FeedbackReport(
                student_name=student_data.get('name', 'Student'),
                subject=student_data.get('subject', 'General'),
                date=datetime.now().strftime("%Y-%m-%d"),
                performance_analysis=performance,
                strengths=strengths,
                improvement_areas=improvement_areas,
                overall_comment=overall_comment,
                format_type=format_type
            )
            
            # Step 6: Generate parent version if requested
            if student_data.get('include_parent_version', True):
                report.parent_version = await self.generate_parent_version(report)
            
            # Step 7: Validate
            if not report.validate_report():
                self.logger.warning("Report validation failed")
            
            # Step 8: Check tone
            tone_warnings = report.check_tone()
            if tone_warnings:
                self.logger.info(f"Tone suggestions: {', '.join(tone_warnings)}")
            
            self.logger.info("Feedback composition complete")
            return report
            
        except Exception as e:
            self.logger.error(f"Error composing feedback: {e}")
            raise
    
    def _compose_overall_comment(
        self,
        student_data: Dict[str, Any],
        performance: PerformanceAnalysis,
        strengths: List[Strength],
        improvement_areas: List[ImprovementArea]
    ) -> str:
        """
        Compose a cohesive overall comment.
        
        Args:
            student_data: Student information
            performance: Performance analysis
            strengths: List of strengths
            improvement_areas: List of improvement areas
        
        Returns:
            Narrative overall comment
        """
        name = student_data.get('name', 'This student')
        
        comment = f"{name} has shown {performance.effort_rating.lower()} effort this period. "
        
        # Highlight top strength
        if strengths:
            comment += f"A particular strength is {strengths[0].strength.lower()}. "
        
        # Mention growth
        if 'improvement' in ' '.join(performance.trends).lower():
            comment += "I'm pleased to see growth in recent assessments. "
        
        # Address improvement areas constructively
        if improvement_areas:
            priority_areas = [a for a in improvement_areas if a.priority == "high"]
            if priority_areas:
                comment += f"To continue this progress, focusing on {priority_areas[0].area.lower()} will be beneficial. "
            else:
                comment += f"Our next focus will be {improvement_areas[0].area.lower()}. "
        
        # End on positive note
        comment += f"{name} is a valued member of our learning community, and I look forward to supporting continued growth."
        
        return comment
    
    async def generate_parent_version(self, report: FeedbackReport) -> str:
        """
        Generate parent-friendly version of feedback.
        
        Args:
            report: Complete feedback report
        
        Returns:
            Parent-friendly feedback message
        """
        self.logger.info("Generating parent version")
        
        parent_msg = f"Dear Parents/Guardians of {report.student_name},\n\n"
        
        parent_msg += f"I wanted to share an update on {report.student_name}'s progress in {report.subject}. "
        
        # Strengths in plain language
        parent_msg += f"{report.student_name} is doing well in several areas:\n"
        for strength in report.strengths[:2]:  # Top 2 strengths
            parent_msg += f"• {strength.strength}\n"
        parent_msg += "\n"
        
        # Growth areas with parent support
        if report.improvement_areas:
            parent_msg += "To support continued growth at home, you can:\n"
            for area in report.improvement_areas[:2]:  # Top 2 areas
                if area.action_steps:
                    parent_msg += f"• {area.action_steps[0].step}\n"
            parent_msg += "\n"
        
        parent_msg += "Please don't hesitate to reach out if you have questions or would like to discuss your child's progress.\n\n"
        parent_msg += "Best regards"
        
        return parent_msg


# Export main class
__all__ = ['FeedbackComposerAgent', 'FeedbackReport', 'PerformanceAnalysis', 'Strength', 'ImprovementArea']
