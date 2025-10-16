#!/usr/bin/env python3
"""
Differentiation Specialist Agent for PTCC

Generates multi-tiered, differentiated instructional content with:
- Learner profile analysis
- Multi-level content tiers (4 levels)
- Universal Design for Learning (UDL) principles
- Scaffolding strategies
- IEP/504 accommodations
- ELL supports
- Flexible grouping strategies

Integrates with:
- RAG system for UDL and differentiation best practices
- Memory system for teacher preferences and student needs
- Alignment system for appropriate content adaptation
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict, field


@dataclass
class LearnerProfile:
    """Student needs profile for differentiation."""
    student_id: str
    grade_level: str
    current_performance_level: str  # "below", "at", "above", "advanced"
    learning_styles: List[str]  # "visual", "auditory", "kinesthetic", "read_write"
    accommodations_needed: List[str]
    language_needs: Optional[str] = None  # ELL level if applicable
    iep_504_status: Optional[str] = None
    strengths: Optional[List[str]] = None
    challenges: Optional[List[str]] = None


@dataclass
class UDLPrinciple:
    """Universal Design for Learning implementation."""
    principle: str  # "engagement", "representation", "action_expression"
    strategy: str
    implementation_notes: str
    examples: List[str]


@dataclass
class Scaffold:
    """Scaffolding support structure."""
    scaffold_type: str  # "graphic_organizer", "sentence_frames", "think_aloud", "modeling", "chunking"
    description: str
    when_to_use: str
    when_to_remove: str
    resources_needed: List[str]


@dataclass
class Accommodation:
    """Individual accommodation for specific needs."""
    accommodation_type: str  # "presentation", "response", "setting", "timing"
    description: str
    rationale: str
    implementation_steps: List[str]
    applicable_to: List[str]  # Which student IDs or groups


@dataclass
class ContentTier:
    """Single tier of differentiated content."""
    tier_level: str  # "tier1_support", "tier2_core", "tier3_extension", "tier4_advanced"
    target_audience: str
    readability_level: str
    objectives: List[str]
    activities: List[str]
    materials: List[str]
    assessment_adaptations: List[str]
    scaffolds: List[Scaffold]
    estimated_time: str
    success_criteria: List[str]


@dataclass
class DifferentiatedContent:
    """
    Main differentiation container.
    
    Attributes:
        lesson_topic: Topic being differentiated
        grade_level: Grade level
        subject: Subject area
        content_tiers: Multiple tiers of content
        accommodations: Specific accommodations
        udl_principles: UDL strategies applied
        ell_supports: English Language Learner supports
        extension_opportunities: Enrichment options
        grouping_suggestions: Flexible grouping strategies
        created_at: Timestamp of generation
    """
    lesson_topic: str
    grade_level: str
    subject: str
    content_tiers: List[ContentTier]
    accommodations: List[Accommodation]
    udl_principles: List[UDLPrinciple]
    ell_supports: List[str]
    extension_opportunities: List[str]
    grouping_suggestions: Optional[Dict[str, List[str]]] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        if isinstance(data.get('created_at'), datetime):
            data['created_at'] = data['created_at'].isoformat()
        return data
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    def to_markdown(self) -> str:
        """Convert to teacher-friendly markdown format."""
        md = f"# Differentiated Lesson: {self.lesson_topic}\n\n"
        md += f"**Grade Level:** {self.grade_level}  \n"
        md += f"**Subject:** {self.subject}  \n"
        md += f"**Date Created:** {self.created_at.strftime('%Y-%m-%d')}  \n\n"
        
        # UDL Principles
        md += "## Universal Design for Learning (UDL)\n\n"
        for udl in self.udl_principles:
            md += f"### {udl.principle.title()}\n"
            md += f"**Strategy:** {udl.strategy}  \n"
            md += f"**Implementation:** {udl.implementation_notes}  \n"
            if udl.examples:
                md += "**Examples:**\n"
                for example in udl.examples:
                    md += f"- {example}\n"
            md += "\n"
        
        # Content Tiers
        md += "## Content Tiers\n\n"
        for tier in self.content_tiers:
            md += f"### {tier.tier_level.replace('_', ' ').title()}\n"
            md += f"**Target:** {tier.target_audience}  \n"
            md += f"**Readability:** {tier.readability_level}  \n"
            md += f"**Time:** {tier.estimated_time}  \n\n"
            
            md += "**Objectives:**\n"
            for obj in tier.objectives:
                md += f"- {obj}\n"
            md += "\n"
            
            md += "**Activities:**\n"
            for i, activity in enumerate(tier.activities, 1):
                md += f"{i}. {activity}\n"
            md += "\n"
            
            if tier.scaffolds:
                md += "**Scaffolds:**\n"
                for scaffold in tier.scaffolds:
                    md += f"- **{scaffold.scaffold_type}**: {scaffold.description}\n"
                md += "\n"
            
            md += "**Materials:**\n"
            for material in tier.materials:
                md += f"- {material}\n"
            md += "\n"
            
            md += "**Success Criteria:**\n"
            for criterion in tier.success_criteria:
                md += f"- {criterion}\n"
            md += "\n---\n\n"
        
        # Accommodations
        if self.accommodations:
            md += "## Individual Accommodations\n\n"
            for acc in self.accommodations:
                md += f"### {acc.accommodation_type.title()}\n"
                md += f"**Description:** {acc.description}  \n"
                md += f"**Rationale:** {acc.rationale}  \n"
                md += f"**For:** {', '.join(acc.applicable_to)}  \n\n"
                md += "**Implementation:**\n"
                for step in acc.implementation_steps:
                    md += f"1. {step}\n"
                md += "\n"
        
        # ELL Supports
        if self.ell_supports:
            md += "## English Language Learner Supports\n\n"
            for support in self.ell_supports:
                md += f"- {support}\n"
            md += "\n"
        
        # Extensions
        if self.extension_opportunities:
            md += "## Extension Opportunities\n\n"
            for ext in self.extension_opportunities:
                md += f"- {ext}\n"
            md += "\n"
        
        # Grouping
        if self.grouping_suggestions:
            md += "## Flexible Grouping Suggestions\n\n"
            for group_type, students in self.grouping_suggestions.items():
                md += f"**{group_type}:** {', '.join(students)}  \n"
            md += "\n"
        
        return md
    
    def to_lesson_plan(self) -> str:
        """Convert to integrated lesson plan format."""
        lp = f"DIFFERENTIATED LESSON PLAN\n"
        lp += f"{'=' * 60}\n\n"
        lp += f"Topic: {self.lesson_topic}\n"
        lp += f"Grade: {self.grade_level} | Subject: {self.subject}\n\n"
        
        lp += "OBJECTIVES (Multi-Level):\n"
        for tier in self.content_tiers:
            lp += f"\n{tier.tier_level.upper()}:\n"
            for obj in tier.objectives:
                lp += f"  • {obj}\n"
        
        lp += "\n\nACTIVITIES:\n"
        for tier in self.content_tiers:
            lp += f"\n{tier.target_audience}:\n"
            for activity in tier.activities:
                lp += f"  - {activity}\n"
        
        return lp
    
    def validate_differentiation(self) -> bool:
        """
        Validate quality standards for differentiation.
        
        Returns:
            True if differentiation meets quality standards
        """
        # Must have at least 2 tiers
        if len(self.content_tiers) < 2:
            return False
        
        # Each tier must have objectives and activities
        for tier in self.content_tiers:
            if not tier.objectives or not tier.activities:
                return False
        
        # Must have at least one UDL principle
        if not self.udl_principles:
            return False
        
        # Must have grouping suggestions
        if not self.grouping_suggestions:
            return False
        
        return True
    
    def check_accessibility(self) -> List[str]:
        """
        Verify accessibility features.
        
        Returns:
            List of accessibility recommendations
        """
        recommendations = []
        
        # Check for visual supports
        visual_scaffolds = [s for tier in self.content_tiers 
                           for s in tier.scaffolds 
                           if 'visual' in s.scaffold_type.lower() or 'graphic' in s.scaffold_type.lower()]
        if not visual_scaffolds:
            recommendations.append("Consider adding visual aids/graphic organizers")
        
        # Check for auditory supports
        has_auditory = any('read' in s.lower() or 'audio' in s.lower() for s in self.ell_supports)
        if not has_auditory:
            recommendations.append("Consider adding audio/read-aloud supports")
        
        # Check for kinesthetic options
        kinesthetic_activities = [a for tier in self.content_tiers 
                                 for a in tier.activities 
                                 if 'hands-on' in a.lower() or 'manipulative' in a.lower()]
        if not kinesthetic_activities:
            recommendations.append("Consider adding hands-on/kinesthetic activities")
        
        # Check UDL coverage
        udl_principles_covered = set(p.principle for p in self.udl_principles)
        required_principles = {'engagement', 'representation', 'action_expression'}
        missing_principles = required_principles - udl_principles_covered
        if missing_principles:
            recommendations.append(f"Missing UDL principles: {', '.join(missing_principles)}")
        
        return recommendations
    
    def get_tier_for_student(self, profile: LearnerProfile) -> ContentTier:
        """
        Match student to appropriate tier.
        
        Args:
            profile: Student learner profile
        
        Returns:
            Most appropriate ContentTier for student
        """
        # Match based on performance level
        level_to_tier = {
            'below': 'tier1_support',
            'at': 'tier2_core',
            'above': 'tier3_extension',
            'advanced': 'tier4_advanced'
        }
        
        target_tier = level_to_tier.get(profile.current_performance_level, 'tier2_core')
        
        # Find matching tier
        for tier in self.content_tiers:
            if tier.tier_level == target_tier:
                return tier
        
        # Default to core tier if specific tier not found
        return self.content_tiers[0] if self.content_tiers else None


class DifferentiationSpecialistAgent:
    """
    Agent for generating differentiated instructional content.
    
    Capabilities:
    - Create learner profiles from student data
    - Generate multi-tier content (4 levels)
    - Apply UDL principles
    - Create scaffolds and accommodations
    - Provide ELL supports
    - Suggest flexible grouping
    - Export in multiple formats
    
    Usage:
        agent = DifferentiationSpecialistAgent(llm_client, rag_engine)
        diff_content = await agent.differentiate_content(
            lesson_topic="Photosynthesis",
            grade_level="5th Grade",
            subject="Science",
            learner_profiles=[profile1, profile2, ...]
        )
        print(diff_content.to_markdown())
    """
    
    def __init__(self, llm_client=None, rag_engine=None):
        """
        Initialize the differentiation specialist.
        
        Args:
            llm_client: LLM client for content generation
            rag_engine: RAG engine for UDL and differentiation best practices
        """
        self.logger = self._setup_logging()
        self.llm_client = llm_client
        self.rag_engine = rag_engine
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the agent."""
        logger = logging.getLogger("differentiation_specialist")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def create_learner_profiles(
        self,
        student_data: List[Dict[str, Any]]
    ) -> List[LearnerProfile]:
        """
        Analyze student needs and create learner profiles.
        
        Args:
            student_data: List of student information dictionaries
        
        Returns:
            List of LearnerProfile objects
        """
        self.logger.info(f"Creating learner profiles for {len(student_data)} students")
        
        profiles = []
        
        try:
            for student in student_data:
                profile = LearnerProfile(
                    student_id=student.get('id', 'unknown'),
                    grade_level=student.get('grade_level', ''),
                    current_performance_level=student.get('performance_level', 'at'),
                    learning_styles=student.get('learning_styles', ['visual', 'auditory']),
                    accommodations_needed=student.get('accommodations', []),
                    language_needs=student.get('ell_level'),
                    iep_504_status=student.get('iep_504'),
                    strengths=student.get('strengths', []),
                    challenges=student.get('challenges', [])
                )
                profiles.append(profile)
            
            self.logger.info(f"Created {len(profiles)} learner profiles")
            return profiles
            
        except Exception as e:
            self.logger.error(f"Error creating learner profiles: {e}")
            return []
    
    async def generate_content_tiers(
        self,
        lesson_topic: str,
        grade_level: str,
        subject: str,
        num_tiers: int = 4
    ) -> List[ContentTier]:
        """
        Create tiered versions of content.
        
        Args:
            lesson_topic: Topic to differentiate
            grade_level: Grade level
            subject: Subject area
            num_tiers: Number of tiers to create (default 4)
        
        Returns:
            List of ContentTier objects at different levels
        """
        self.logger.info(f"Generating {num_tiers} content tiers for {lesson_topic}")
        
        tiers = []
        
        try:
            # Tier 1: Support (below grade level)
            tier1 = ContentTier(
                tier_level="tier1_support",
                target_audience="Students needing additional support",
                readability_level="Below grade level",
                objectives=[
                    f"Understand basic concepts of {lesson_topic}",
                    "Identify key vocabulary with support",
                    "Complete tasks with scaffolding"
                ],
                activities=[
                    "Pre-teach vocabulary with visuals",
                    f"Guided exploration of {lesson_topic} with sentence frames",
                    "Complete simplified graphic organizer with teacher support",
                    "Partner work with structured roles"
                ],
                materials=[
                    "Simplified texts with visuals",
                    "Vocabulary cards with pictures",
                    "Graphic organizers (partially completed)",
                    "Manipulatives or models"
                ],
                assessment_adaptations=[
                    "Oral responses accepted",
                    "Multiple choice with 3 options",
                    "Demonstrate understanding with visuals",
                    "Extended time provided"
                ],
                scaffolds=[
                    Scaffold(
                        scaffold_type="sentence_frames",
                        description="Sentence starters for responses",
                        when_to_use="During discussions and written work",
                        when_to_remove="When student demonstrates fluency",
                        resources_needed=["Sentence frame templates"]
                    ),
                    Scaffold(
                        scaffold_type="graphic_organizer",
                        description="Structured organizer with prompts",
                        when_to_use="For note-taking and organizing ideas",
                        when_to_remove="Gradually as student gains confidence",
                        resources_needed=["Printed organizers"]
                    )
                ],
                estimated_time="50-60 minutes",
                success_criteria=[
                    "Can explain basic concepts with support",
                    "Uses key vocabulary correctly",
                    "Completes tasks with minimal frustration"
                ]
            )
            tiers.append(tier1)
            
            # Tier 2: Core (at grade level)
            tier2 = ContentTier(
                tier_level="tier2_core",
                target_audience="Students at grade level",
                readability_level="At grade level",
                objectives=[
                    f"Explain key concepts of {lesson_topic}",
                    "Apply understanding to new situations",
                    "Work independently with occasional support"
                ],
                activities=[
                    f"Read and discuss {lesson_topic} text",
                    "Complete guided inquiry activity",
                    "Create graphic organizer independently",
                    "Small group discussion and problem-solving"
                ],
                materials=[
                    "Grade-level texts",
                    "Standard graphic organizers",
                    "Lab materials or manipulatives",
                    "Discussion prompts"
                ],
                assessment_adaptations=[
                    "Written and oral responses",
                    "Multiple formats accepted",
                    "Standard time limits"
                ],
                scaffolds=[
                    Scaffold(
                        scaffold_type="modeling",
                        description="Teacher demonstrates first example",
                        when_to_use="At introduction of new concepts",
                        when_to_remove="After first guided practice",
                        resources_needed=["Example problems"]
                    )
                ],
                estimated_time="45 minutes",
                success_criteria=[
                    "Explains concepts clearly",
                    "Applies knowledge to new problems",
                    "Works independently most of the time"
                ]
            )
            tiers.append(tier2)
            
            # Tier 3: Extension (above grade level)
            tier3 = ContentTier(
                tier_level="tier3_extension",
                target_audience="Students above grade level",
                readability_level="Above grade level",
                objectives=[
                    f"Analyze {lesson_topic} in depth",
                    "Make connections to other concepts",
                    "Work independently on complex tasks"
                ],
                activities=[
                    f"Independent research on advanced aspects of {lesson_topic}",
                    "Design and conduct experiment or investigation",
                    "Create presentation or model",
                    "Lead peer discussion"
                ],
                materials=[
                    "Advanced texts and articles",
                    "Open-ended project materials",
                    "Technology tools",
                    "Authentic resources"
                ],
                assessment_adaptations=[
                    "Student choice in format",
                    "Higher-level questioning",
                    "Presentations to class"
                ],
                scaffolds=[],  # Minimal scaffolding
                estimated_time="45 minutes plus extension time",
                success_criteria=[
                    "Demonstrates deep understanding",
                    "Makes meaningful connections",
                    "Produces high-quality work independently"
                ]
            )
            tiers.append(tier3)
            
            # Tier 4: Advanced (gifted/advanced)
            tier4 = ContentTier(
                tier_level="tier4_advanced",
                target_audience="Advanced/gifted students",
                readability_level="Advanced",
                objectives=[
                    f"Evaluate and synthesize information about {lesson_topic}",
                    "Create original work or solutions",
                    "Teach others or contribute to class learning"
                ],
                activities=[
                    f"Independent inquiry project on {lesson_topic}",
                    "Develop and test hypothesis",
                    "Create instructional materials for peers",
                    "Explore real-world applications"
                ],
                materials=[
                    "Professional/academic resources",
                    "Open-ended project supplies",
                    "Advanced technology tools",
                    "Mentorship opportunities"
                ],
                assessment_adaptations=[
                    "Self-directed projects",
                    "Product creation",
                    "Portfolio assessment",
                    "Peer teaching opportunities"
                ],
                scaffolds=[],  # Independent work
                estimated_time="Flexible, student-directed",
                success_criteria=[
                    "Demonstrates mastery and originality",
                    "Creates meaningful products",
                    "Contributes to class learning"
                ]
            )
            tiers.append(tier4)
            
            self.logger.info(f"Generated {len(tiers)} content tiers")
            return tiers[:num_tiers]
            
        except Exception as e:
            self.logger.error(f"Error generating content tiers: {e}")
            return []
    
    async def apply_udl_principles(
        self,
        lesson_topic: str
    ) -> List[UDLPrinciple]:
        """
        Apply Universal Design for Learning principles.
        
        Args:
            lesson_topic: Topic to apply UDL to
        
        Returns:
            List of UDLPrinciple objects
        """
        self.logger.info(f"Applying UDL principles to {lesson_topic}")
        
        udl_strategies = []
        
        try:
            # Engagement
            udl_strategies.append(UDLPrinciple(
                principle="engagement",
                strategy="Multiple means of engagement",
                implementation_notes="Provide choice in activities, use real-world connections, allow collaboration",
                examples=[
                    f"Student choice in how to demonstrate understanding of {lesson_topic}",
                    "Connect to real-world applications",
                    "Flexible grouping options"
                ]
            ))
            
            # Representation
            udl_strategies.append(UDLPrinciple(
                principle="representation",
                strategy="Multiple means of representation",
                implementation_notes="Present information in multiple formats (visual, auditory, kinesthetic)",
                examples=[
                    "Use videos, diagrams, and text",
                    f"Provide audio recordings of {lesson_topic} content",
                    "Hands-on models or manipulatives",
                    "Digital and print resources"
                ]
            ))
            
            # Action & Expression
            udl_strategies.append(UDLPrinciple(
                principle="action_expression",
                strategy="Multiple means of action and expression",
                implementation_notes="Allow students to show learning in various ways",
                examples=[
                    "Written, oral, or visual presentations",
                    "Digital or hands-on projects",
                    "Individual or group work options",
                    "Technology tools available"
                ]
            ))
            
            # Query RAG for additional UDL strategies if available
            if self.rag_engine:
                try:
                    best_practices = await self.rag_engine.query(
                        f"UDL strategies for teaching {lesson_topic}"
                    )
                    if best_practices:
                        self.logger.info("Enhanced UDL strategies with RAG")
                except Exception as e:
                    self.logger.warning(f"RAG query for UDL failed: {e}")
            
            self.logger.info(f"Applied {len(udl_strategies)} UDL principles")
            return udl_strategies
            
        except Exception as e:
            self.logger.error(f"Error applying UDL principles: {e}")
            return []
    
    async def generate_accommodations(
        self,
        learner_profiles: List[LearnerProfile]
    ) -> List[Accommodation]:
        """
        Create specific accommodations for IEP/504 and other needs.
        
        Args:
            learner_profiles: List of learner profiles
        
        Returns:
            List of Accommodation objects
        """
        self.logger.info(f"Generating accommodations for {len(learner_profiles)} students")
        
        accommodations = []
        
        try:
            # Analyze profiles for common needs
            iep_504_students = [p for p in learner_profiles if p.iep_504_status]
            ell_students = [p for p in learner_profiles if p.language_needs]
            
            # Presentation accommodations
            if iep_504_students or ell_students:
                accommodations.append(Accommodation(
                    accommodation_type="presentation",
                    description="Provide information in multiple formats",
                    rationale="Supports diverse learning needs and language processing",
                    implementation_steps=[
                        "Provide written and oral instructions",
                        "Use visual supports and diagrams",
                        "Highlight key vocabulary",
                        "Break information into smaller chunks"
                    ],
                    applicable_to=[p.student_id for p in iep_504_students + ell_students]
                ))
            
            # Response accommodations
            if iep_504_students:
                accommodations.append(Accommodation(
                    accommodation_type="response",
                    description="Allow alternative ways to respond",
                    rationale="Supports students with writing or expression difficulties",
                    implementation_steps=[
                        "Accept oral responses",
                        "Allow use of scribe or voice-to-text",
                        "Provide graphic organizers",
                        "Accept demonstrations instead of written work"
                    ],
                    applicable_to=[p.student_id for p in iep_504_students]
                ))
            
            # Setting accommodations
            setting_needs = [p for p in learner_profiles 
                           if any('quiet' in a.lower() or 'separate' in a.lower() 
                                 for a in p.accommodations_needed)]
            if setting_needs:
                accommodations.append(Accommodation(
                    accommodation_type="setting",
                    description="Modify learning environment",
                    rationale="Reduces distractions and supports focus",
                    implementation_steps=[
                        "Provide quiet workspace option",
                        "Allow movement breaks",
                        "Flexible seating available",
                        "Small group work space"
                    ],
                    applicable_to=[p.student_id for p in setting_needs]
                ))
            
            # Timing accommodations
            timing_needs = [p for p in learner_profiles 
                          if any('time' in a.lower() or 'extended' in a.lower() 
                                for a in p.accommodations_needed)]
            if timing_needs:
                accommodations.append(Accommodation(
                    accommodation_type="timing",
                    description="Provide extended time and breaks",
                    rationale="Reduces anxiety and supports processing needs",
                    implementation_steps=[
                        "Allow 1.5x time on tasks",
                        "Provide scheduled breaks",
                        "Allow work completion over multiple sessions",
                        "No penalty for timing needs"
                    ],
                    applicable_to=[p.student_id for p in timing_needs]
                ))
            
            self.logger.info(f"Generated {len(accommodations)} accommodations")
            return accommodations
            
        except Exception as e:
            self.logger.error(f"Error generating accommodations: {e}")
            return []
    
    async def create_scaffolds(
        self,
        lesson_topic: str,
        difficulty_level: str
    ) -> List[Scaffold]:
        """
        Generate appropriate scaffolding strategies.
        
        Args:
            lesson_topic: Topic being taught
            difficulty_level: Target difficulty level
        
        Returns:
            List of Scaffold objects
        """
        self.logger.info(f"Creating scaffolds for {lesson_topic} at {difficulty_level} level")
        
        scaffolds = []
        
        try:
            # Common scaffolds for support levels
            if difficulty_level in ['below', 'support']:
                scaffolds.extend([
                    Scaffold(
                        scaffold_type="graphic_organizer",
                        description=f"Visual organizer for {lesson_topic} concepts",
                        when_to_use="During note-taking and concept organization",
                        when_to_remove="When student can organize independently",
                        resources_needed=["Printed organizers", "Digital templates"]
                    ),
                    Scaffold(
                        scaffold_type="sentence_frames",
                        description="Sentence starters for discussions and writing",
                        when_to_use="During all communication activities",
                        when_to_remove="When fluency is demonstrated",
                        resources_needed=["Sentence frame cards or posters"]
                    ),
                    Scaffold(
                        scaffold_type="think_aloud",
                        description="Teacher models thinking process",
                        when_to_use="When introducing new concepts",
                        when_to_remove="After several examples",
                        resources_needed=["Example problems"]
                    ),
                    Scaffold(
                        scaffold_type="chunking",
                        description="Break content into smaller, manageable parts",
                        when_to_use="For complex or lengthy tasks",
                        when_to_remove="As stamina builds",
                        resources_needed=["Task breakdown sheets"]
                    )
                ])
            
            # Moderate scaffolds for grade-level
            elif difficulty_level in ['at', 'core']:
                scaffolds.extend([
                    Scaffold(
                        scaffold_type="modeling",
                        description="Demonstrate expected outcome",
                        when_to_use="At task introduction",
                        when_to_remove="After first guided practice",
                        resources_needed=["Example work"]
                    ),
                    Scaffold(
                        scaffold_type="graphic_organizer",
                        description="Blank organizer for student use",
                        when_to_use="As needed for organization",
                        when_to_remove="When no longer helpful",
                        resources_needed=["Blank templates"]
                    )
                ])
            
            # Minimal scaffolds for advanced
            else:
                scaffolds.append(
                    Scaffold(
                        scaffold_type="resource_list",
                        description="Curated list of advanced resources",
                        when_to_use="For independent research",
                        when_to_remove="Not needed",
                        resources_needed=["Resource guide"]
                    )
                )
            
            self.logger.info(f"Created {len(scaffolds)} scaffolds")
            return scaffolds
            
        except Exception as e:
            self.logger.error(f"Error creating scaffolds: {e}")
            return []
    
    async def differentiate_content(
        self,
        lesson_topic: str,
        grade_level: str,
        subject: str,
        learner_profiles: List[LearnerProfile],
        num_tiers: int = 4
    ) -> DifferentiatedContent:
        """
        Main orchestration method to generate complete differentiated content.
        
        Args:
            lesson_topic: Topic to differentiate
            grade_level: Grade level
            subject: Subject area
            learner_profiles: List of student learner profiles
            num_tiers: Number of content tiers to create
        
        Returns:
            Complete DifferentiatedContent object
        
        Example:
            profiles = await agent.create_learner_profiles(student_data)
            diff_content = await agent.differentiate_content(
                lesson_topic="Photosynthesis",
                grade_level="5th Grade",
                subject="Science",
                learner_profiles=profiles
            )
        """
        self.logger.info(f"Differentiating content for {lesson_topic}")
        
        try:
            # Step 1: Generate content tiers
            content_tiers = await self.generate_content_tiers(
                lesson_topic, grade_level, subject, num_tiers
            )
            
            # Step 2: Apply UDL principles
            udl_principles = await self.apply_udl_principles(lesson_topic)
            
            # Step 3: Generate accommodations
            accommodations = await self.generate_accommodations(learner_profiles)
            
            # Step 4: Create ELL supports
            ell_supports = self._generate_ell_supports(learner_profiles)
            
            # Step 5: Create extension opportunities
            extension_opportunities = self._generate_extensions(lesson_topic, subject)
            
            # Step 6: Suggest groupings
            grouping_suggestions = self._suggest_groupings(learner_profiles)
            
            # Step 7: Create differentiated content package
            diff_content = DifferentiatedContent(
                lesson_topic=lesson_topic,
                grade_level=grade_level,
                subject=subject,
                content_tiers=content_tiers,
                accommodations=accommodations,
                udl_principles=udl_principles,
                ell_supports=ell_supports,
                extension_opportunities=extension_opportunities,
                grouping_suggestions=grouping_suggestions
            )
            
            # Step 8: Validate
            if not diff_content.validate_differentiation():
                self.logger.warning("Differentiation validation failed")
            
            # Step 9: Check accessibility
            accessibility_recommendations = diff_content.check_accessibility()
            if accessibility_recommendations:
                self.logger.info(f"Accessibility recommendations: {', '.join(accessibility_recommendations)}")
            
            self.logger.info("Differentiation complete")
            return diff_content
            
        except Exception as e:
            self.logger.error(f"Error differentiating content: {e}")
            raise
    
    def _generate_ell_supports(self, learner_profiles: List[LearnerProfile]) -> List[str]:
        """Generate ELL-specific supports."""
        ell_students = [p for p in learner_profiles if p.language_needs]
        
        if not ell_students:
            return []
        
        return [
            "Pre-teach key vocabulary with visuals and native language support",
            "Provide bilingual glossaries",
            "Use sentence frames and language models",
            "Allow extra processing time",
            "Pair with language buddy",
            "Provide audio recordings of texts",
            "Use visuals and gestures extensively",
            "Accept responses in native language initially",
            "Provide word banks for writing tasks",
            "Use simplified language for instructions"
        ]
    
    def _generate_extensions(self, lesson_topic: str, subject: str) -> List[str]:
        """Generate extension opportunities for advanced learners."""
        return [
            f"Research advanced aspects of {lesson_topic}",
            f"Develop and test hypothesis related to {lesson_topic}",
            "Create instructional video or presentation for peers",
            "Design real-world application project",
            f"Explore career connections to {subject}",
            "Lead inquiry investigation",
            "Mentor peers in small groups",
            "Create assessment questions for class"
        ]
    
    def _suggest_groupings(self, learner_profiles: List[LearnerProfile]) -> Dict[str, List[str]]:
        """Suggest flexible grouping strategies."""
        groupings = {}
        
        # Group by performance level
        by_level = {}
        for profile in learner_profiles:
            level = profile.current_performance_level
            if level not in by_level:
                by_level[level] = []
            by_level[level].append(profile.student_id)
        
        groupings["homogeneous_ability"] = [
            f"{level}: {', '.join(students)}" 
            for level, students in by_level.items()
        ]
        
        # Mixed ability groups (combine levels)
        mixed_groups = []
        all_students = [p.student_id for p in learner_profiles]
        group_size = 4
        for i in range(0, len(all_students), group_size):
            group = all_students[i:i+group_size]
            mixed_groups.append(f"Group {i//group_size + 1}: {', '.join(group)}")
        
        groupings["heterogeneous_mixed"] = mixed_groups
        
        # Learning style groups
        by_style = {}
        for profile in learner_profiles:
            primary_style = profile.learning_styles[0] if profile.learning_styles else 'mixed'
            if primary_style not in by_style:
                by_style[primary_style] = []
            by_style[primary_style].append(profile.student_id)
        
        groupings["learning_style"] = [
            f"{style}: {', '.join(students)}" 
            for style, students in by_style.items()
        ]
        
        return groupings


# Export main class
__all__ = [
    'DifferentiationSpecialistAgent',
    'DifferentiatedContent',
    'LearnerProfile',
    'ContentTier',
    'UDLPrinciple',
    'Scaffold',
    'Accommodation'
]
