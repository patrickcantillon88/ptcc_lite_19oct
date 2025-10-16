#!/usr/bin/env python3
"""
Lesson Plan Generator Agent for PTCC

Generates comprehensive, standards-aligned lesson plans with:
- Learning objectives
- Instructional activities
- Assessment methods
- Differentiation strategies
- Materials lists
- Time allocations

Integrates with:
- RAG system for curriculum standards
- Memory system for teacher preferences
- Alignment system for educational appropriateness
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum


class LessonStructure(Enum):
    """Common lesson plan structures."""
    FIVE_E = "5E"  # Engage, Explore, Explain, Elaborate, Evaluate
    GRADUAL_RELEASE = "gradual_release"  # I do, We do, You do
    INQUIRY_BASED = "inquiry_based"
    DIRECT_INSTRUCTION = "direct_instruction"
    PROJECT_BASED = "project_based"


class BloomLevel(Enum):
    """Bloom's Taxonomy cognitive levels."""
    REMEMBER = "remember"
    UNDERSTAND = "understand"
    APPLY = "apply"
    ANALYZE = "analyze"
    EVALUATE = "evaluate"
    CREATE = "create"


@dataclass
class LearningObjective:
    """A single learning objective."""
    description: str
    bloom_level: str
    standard_alignment: Optional[str] = None
    measurable: bool = True


@dataclass
class Activity:
    """An instructional activity."""
    name: str
    description: str
    duration_minutes: int
    activity_type: str  # opening, main, practice, closure
    materials: List[str]
    differentiation_notes: Optional[str] = None


@dataclass
class Assessment:
    """Assessment method."""
    type: str  # formative, summative, diagnostic
    description: str
    success_criteria: List[str]
    timing: str  # during, end, after


@dataclass
class LessonPlan:
    """Complete lesson plan structure."""
    title: str
    grade_level: str
    subject: str
    topic: str
    duration: str
    
    # Core components
    learning_objectives: List[LearningObjective]
    standards_addressed: List[str]
    essential_question: str
    
    # Activities
    activities: List[Activity]
    
    # Assessment
    assessments: List[Assessment]
    
    # Resources
    materials_needed: List[str]
    technology_needed: List[str]
    vocabulary: List[str]
    
    # Differentiation
    differentiation_strategies: Dict[str, str]
    
    # Additional
    homework_assignment: Optional[str] = None
    extensions: Optional[List[str]] = None
    accommodations: Optional[List[str]] = None
    
    # Metadata
    created_at: datetime = None
    lesson_structure: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class LessonPlanGeneratorAgent:
    """
    Agent for generating comprehensive lesson plans.
    
    Capabilities:
    - Generate standards-aligned lesson plans
    - Create learning objectives at various Bloom levels
    - Design engaging activities
    - Include formative and summative assessments
    - Provide differentiation strategies
    - Suggest materials and resources
    """
    
    def __init__(self, llm_client=None, rag_engine=None):
        """
        Initialize the lesson plan generator.
        
        Args:
            llm_client: LLM client for content generation
            rag_engine: RAG engine for curriculum standards retrieval
        """
        self.logger = self._setup_logging()
        self.llm_client = llm_client
        self.rag_engine = rag_engine
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging."""
        logger = logging.getLogger("lesson_plan_generator")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def generate_lesson_plan(
        self,
        topic: str,
        grade_level: str,
        subject: str,
        duration: str = "45 minutes",
        lesson_structure: Optional[LessonStructure] = None,
        learning_goals: Optional[List[str]] = None,
        prior_knowledge: Optional[str] = None,
        student_needs: Optional[Dict[str, Any]] = None
    ) -> LessonPlan:
        """
        Generate a comprehensive lesson plan.
        
        Args:
            topic: Main topic of the lesson
            grade_level: Grade level (e.g., "5th grade", "High School")
            subject: Subject area (e.g., "Science", "Math")
            duration: Lesson duration (e.g., "45 minutes", "90 minutes")
            lesson_structure: Preferred lesson structure (5E, gradual release, etc.)
            learning_goals: Specific learning goals to address
            prior_knowledge: What students already know
            student_needs: Special considerations (ELL, IEP, etc.)
        
        Returns:
            Complete LessonPlan object
        """
        self.logger.info(f"Generating lesson plan: {topic} for {grade_level} {subject}")
        
        # Step 1: Research curriculum standards
        standards = await self._research_standards(subject, grade_level, topic)
        
        # Step 2: Create learning objectives
        objectives = await self._create_learning_objectives(
            topic, grade_level, standards, learning_goals
        )
        
        # Step 3: Create essential question
        essential_question = await self._create_essential_question(topic, objectives)
        
        # Step 4: Design activities
        activities = await self._design_activities(
            topic, grade_level, duration, lesson_structure, objectives, prior_knowledge
        )
        
        # Step 5: Create assessments
        assessments = await self._create_assessments(objectives, activities)
        
        # Step 6: Compile materials and vocabulary
        materials = self._extract_materials(activities)
        technology = self._extract_technology(activities)
        vocabulary = await self._identify_vocabulary(topic, grade_level)
        
        # Step 7: Create differentiation strategies
        differentiation = await self._create_differentiation(
            grade_level, objectives, student_needs
        )
        
        # Step 8: Add extensions and homework
        extensions = await self._create_extensions(topic, objectives)
        homework = await self._create_homework(topic, objectives)
        
        # Build lesson plan
        lesson_plan = LessonPlan(
            title=f"{topic}: {essential_question}",
            grade_level=grade_level,
            subject=subject,
            topic=topic,
            duration=duration,
            learning_objectives=objectives,
            standards_addressed=standards,
            essential_question=essential_question,
            activities=activities,
            assessments=assessments,
            materials_needed=materials,
            technology_needed=technology,
            vocabulary=vocabulary,
            differentiation_strategies=differentiation,
            homework_assignment=homework,
            extensions=extensions,
            lesson_structure=lesson_structure.value if lesson_structure else None
        )
        
        self.logger.info(f"Generated lesson plan with {len(activities)} activities")
        return lesson_plan
    
    async def _research_standards(
        self, subject: str, grade_level: str, topic: str
    ) -> List[str]:
        """Research relevant curriculum standards."""
        self.logger.info(f"Researching standards for {subject} - {topic}")
        
        # Use RAG to find relevant standards if available
        if self.rag_engine:
            query = f"{grade_level} {subject} standards for {topic}"
            try:
                standards_docs = await self.rag_engine.search(query, top_k=5)
                standards = [doc.get('content', '') for doc in standards_docs]
                if standards:
                    return standards[:3]
            except Exception as e:
                self.logger.warning(f"RAG search failed: {e}")
        
        # Fallback: Use LLM to identify standards
        if self.llm_client:
            prompt = f"""Identify 3 relevant curriculum standards for:
Grade Level: {grade_level}
Subject: {subject}
Topic: {topic}

Provide specific standard codes and descriptions (e.g., CCSS.MATH.CONTENT.5.NF.A.1).
Format as a JSON list of strings."""
            
            try:
                response = await self.llm_client.generate(prompt)
                standards = json.loads(response)
                return standards if isinstance(standards, list) else []
            except Exception as e:
                self.logger.warning(f"LLM standards generation failed: {e}")
        
        # Default standards
        return [
            f"{subject} Standard 1: Understanding core concepts of {topic}",
            f"{subject} Standard 2: Applying knowledge of {topic} to real-world situations",
            f"{subject} Standard 3: Analyzing and evaluating {topic}"
        ]
    
    async def _create_learning_objectives(
        self,
        topic: str,
        grade_level: str,
        standards: List[str],
        learning_goals: Optional[List[str]] = None
    ) -> List[LearningObjective]:
        """Create measurable learning objectives."""
        self.logger.info("Creating learning objectives")
        
        if self.llm_client:
            prompt = f"""Create 3-4 measurable learning objectives for:
Topic: {topic}
Grade Level: {grade_level}
Standards: {', '.join(standards[:2])}

Requirements:
- Use action verbs (analyze, create, explain, etc.)
- Make them measurable
- Align to different Bloom's Taxonomy levels
- Be grade-appropriate

Format as JSON:
[
    {{
        "description": "Students will...",
        "bloom_level": "understand|apply|analyze|evaluate|create",
        "standard_alignment": "standard code"
    }}
]"""
            
            try:
                response = await self.llm_client.generate(prompt)
                objectives_data = json.loads(response)
                return [
                    LearningObjective(
                        description=obj['description'],
                        bloom_level=obj['bloom_level'],
                        standard_alignment=obj.get('standard_alignment')
                    )
                    for obj in objectives_data
                ]
            except Exception as e:
                self.logger.warning(f"LLM objective generation failed: {e}")
        
        # Fallback objectives
        return [
            LearningObjective(
                description=f"Students will understand the key concepts of {topic}",
                bloom_level="understand",
                standard_alignment=standards[0] if standards else None
            ),
            LearningObjective(
                description=f"Students will apply {topic} to solve problems",
                bloom_level="apply",
                standard_alignment=standards[1] if len(standards) > 1 else None
            ),
            LearningObjective(
                description=f"Students will analyze examples of {topic}",
                bloom_level="analyze"
            )
        ]
    
    async def _create_essential_question(
        self, topic: str, objectives: List[LearningObjective]
    ) -> str:
        """Create an engaging essential question."""
        if self.llm_client:
            prompt = f"""Create an engaging essential question for a lesson on: {topic}

The question should:
- Be open-ended
- Spark curiosity
- Connect to real-world applications
- Guide the lesson

Objectives:
{chr(10).join(['- ' + obj.description for obj in objectives])}

Provide just the question, no explanation."""
            
            try:
                response = await self.llm_client.generate(prompt)
                return response.strip().strip('"')
            except Exception as e:
                self.logger.warning(f"LLM question generation failed: {e}")
        
        return f"How does understanding {topic} help us in our daily lives?"
    
    async def _design_activities(
        self,
        topic: str,
        grade_level: str,
        duration: str,
        structure: Optional[LessonStructure],
        objectives: List[LearningObjective],
        prior_knowledge: Optional[str]
    ) -> List[Activity]:
        """Design instructional activities."""
        self.logger.info("Designing activities")
        
        # Parse duration
        try:
            total_minutes = int(duration.split()[0])
        except:
            total_minutes = 45
        
        if self.llm_client:
            structure_name = structure.value if structure else "standard"
            prompt = f"""Design a complete {total_minutes}-minute lesson on {topic} for {grade_level}.

Structure: {structure_name}
Objectives:
{chr(10).join(['- ' + obj.description for obj in objectives])}

Create 4-5 activities with:
- Opening/Hook (5-10 min)
- Main instruction (15-20 min)
- Guided practice (10-15 min)
- Independent practice (5-10 min)
- Closure (5 min)

Format as JSON:
[
    {{
        "name": "Activity name",
        "description": "What students do",
        "duration_minutes": 10,
        "activity_type": "opening|main|practice|closure",
        "materials": ["item1", "item2"],
        "differentiation_notes": "How to adapt"
    }}
]"""
            
            try:
                response = await self.llm_client.generate(prompt)
                activities_data = json.loads(response)
                return [
                    Activity(
                        name=act['name'],
                        description=act['description'],
                        duration_minutes=act['duration_minutes'],
                        activity_type=act['activity_type'],
                        materials=act['materials'],
                        differentiation_notes=act.get('differentiation_notes')
                    )
                    for act in activities_data
                ]
            except Exception as e:
                self.logger.warning(f"LLM activity generation failed: {e}")
        
        # Fallback activities
        return [
            Activity(
                name="Hook: Engaging Question",
                description=f"Present an intriguing question about {topic} to activate prior knowledge",
                duration_minutes=5,
                activity_type="opening",
                materials=["Whiteboard", "Markers"]
            ),
            Activity(
                name="Direct Instruction",
                description=f"Explain key concepts of {topic} with examples",
                duration_minutes=15,
                activity_type="main",
                materials=["Presentation slides", "Examples"]
            ),
            Activity(
                name="Guided Practice",
                description=f"Work through {topic} problems together as a class",
                duration_minutes=15,
                activity_type="practice",
                materials=["Practice worksheets", "Manipulatives"]
            ),
            Activity(
                name="Independent Practice",
                description=f"Students apply {topic} concepts independently",
                duration_minutes=15,
                activity_type="practice",
                materials=["Practice problems", "Exit ticket"]
            ),
            Activity(
                name="Closure and Review",
                description="Review key concepts and preview next lesson",
                duration_minutes=5,
                activity_type="closure",
                materials=["Review questions"]
            )
        ]
    
    async def _create_assessments(
        self, objectives: List[LearningObjective], activities: List[Activity]
    ) -> List[Assessment]:
        """Create formative and summative assessments."""
        assessments = [
            Assessment(
                type="formative",
                description="Monitor student understanding during guided practice",
                success_criteria=[obj.description for obj in objectives],
                timing="during"
            ),
            Assessment(
                type="formative",
                description="Exit ticket to assess objective mastery",
                success_criteria=[objectives[0].description] if objectives else ["Basic understanding"],
                timing="end"
            )
        ]
        
        return assessments
    
    def _extract_materials(self, activities: List[Activity]) -> List[str]:
        """Extract unique materials from activities."""
        materials = set()
        for activity in activities:
            materials.update(activity.materials)
        return sorted(list(materials))
    
    def _extract_technology(self, activities: List[Activity]) -> List[str]:
        """Extract technology needs."""
        tech_keywords = ['computer', 'tablet', 'projector', 'smartboard', 'internet', 'app', 'software']
        technology = set()
        
        for activity in activities:
            for material in activity.materials:
                if any(keyword in material.lower() for keyword in tech_keywords):
                    technology.add(material)
        
        return sorted(list(technology))
    
    async def _identify_vocabulary(self, topic: str, grade_level: str) -> List[str]:
        """Identify key vocabulary terms."""
        if self.llm_client:
            prompt = f"""List 5-8 key vocabulary terms for teaching {topic} to {grade_level}.
Include terms students need to understand.
Format as a JSON list of strings."""
            
            try:
                response = await self.llm_client.generate(prompt)
                vocab = json.loads(response)
                return vocab if isinstance(vocab, list) else []
            except Exception as e:
                self.logger.warning(f"Vocabulary generation failed: {e}")
        
        return [topic, "concept", "example", "application"]
    
    async def _create_differentiation(
        self,
        grade_level: str,
        objectives: List[LearningObjective],
        student_needs: Optional[Dict[str, Any]]
    ) -> Dict[str, str]:
        """Create differentiation strategies."""
        return {
            "for_advanced": "Provide extension activities with higher-order thinking challenges",
            "for_struggling": "Offer additional scaffolding, visual aids, and peer support",
            "for_ell": "Use visual supports, sentence frames, and vocabulary scaffolds",
            "for_special_needs": "Provide modifications as per IEP/504 plans"
        }
    
    async def _create_extensions(
        self, topic: str, objectives: List[LearningObjective]
    ) -> List[str]:
        """Create extension activities."""
        return [
            f"Research real-world applications of {topic}",
            f"Create a project demonstrating {topic} concepts",
            f"Teach {topic} to a younger student"
        ]
    
    async def _create_homework(
        self, topic: str, objectives: List[LearningObjective]
    ) -> str:
        """Create homework assignment."""
        return f"Complete practice problems on {topic}. Review key vocabulary and concepts covered in class."
    
    def to_dict(self, lesson_plan: LessonPlan) -> Dict[str, Any]:
        """Convert lesson plan to dictionary."""
        return {
            "title": lesson_plan.title,
            "grade_level": lesson_plan.grade_level,
            "subject": lesson_plan.subject,
            "topic": lesson_plan.topic,
            "duration": lesson_plan.duration,
            "learning_objectives": [asdict(obj) for obj in lesson_plan.learning_objectives],
            "standards_addressed": lesson_plan.standards_addressed,
            "essential_question": lesson_plan.essential_question,
            "activities": [asdict(act) for act in lesson_plan.activities],
            "assessments": [asdict(assess) for assess in lesson_plan.assessments],
            "materials_needed": lesson_plan.materials_needed,
            "technology_needed": lesson_plan.technology_needed,
            "vocabulary": lesson_plan.vocabulary,
            "differentiation_strategies": lesson_plan.differentiation_strategies,
            "homework_assignment": lesson_plan.homework_assignment,
            "extensions": lesson_plan.extensions,
            "created_at": lesson_plan.created_at.isoformat()
        }
    
    def to_markdown(self, lesson_plan: LessonPlan) -> str:
        """Convert lesson plan to markdown format."""
        md = f"""# {lesson_plan.title}

**Grade Level:** {lesson_plan.grade_level}  
**Subject:** {lesson_plan.subject}  
**Duration:** {lesson_plan.duration}

## Essential Question
{lesson_plan.essential_question}

## Learning Objectives
"""
        for i, obj in enumerate(lesson_plan.learning_objectives, 1):
            md += f"{i}. {obj.description} _(Bloom's: {obj.bloom_level})_\n"
        
        md += f"\n## Standards Addressed\n"
        for std in lesson_plan.standards_addressed:
            md += f"- {std}\n"
        
        md += f"\n## Activities\n"
        for act in lesson_plan.activities:
            md += f"\n### {act.name} ({act.duration_minutes} minutes)\n"
            md += f"{act.description}\n\n"
            md += f"**Materials:** {', '.join(act.materials)}\n"
            if act.differentiation_notes:
                md += f"**Differentiation:** {act.differentiation_notes}\n"
        
        md += f"\n## Assessments\n"
        for assess in lesson_plan.assessments:
            md += f"- **{assess.type.title()}**: {assess.description}\n"
        
        md += f"\n## Materials Needed\n"
        for mat in lesson_plan.materials_needed:
            md += f"- {mat}\n"
        
        if lesson_plan.technology_needed:
            md += f"\n## Technology\n"
            for tech in lesson_plan.technology_needed:
                md += f"- {tech}\n"
        
        md += f"\n## Key Vocabulary\n"
        md += ", ".join(lesson_plan.vocabulary)
        
        md += f"\n\n## Differentiation Strategies\n"
        for key, value in lesson_plan.differentiation_strategies.items():
            md += f"**{key.replace('_', ' ').title()}:** {value}\n\n"
        
        if lesson_plan.homework_assignment:
            md += f"\n## Homework\n{lesson_plan.homework_assignment}\n"
        
        if lesson_plan.extensions:
            md += f"\n## Extensions\n"
            for ext in lesson_plan.extensions:
                md += f"- {ext}\n"
        
        return md


# Convenience function for direct usage
async def generate_lesson_plan(
    topic: str,
    grade_level: str,
    subject: str,
    **kwargs
) -> LessonPlan:
    """
    Convenience function to generate a lesson plan.
    
    Args:
        topic: Lesson topic
        grade_level: Grade level
        subject: Subject area
        **kwargs: Additional arguments passed to generate_lesson_plan
    
    Returns:
        LessonPlan object
    """
    agent = LessonPlanGeneratorAgent()
    return await agent.generate_lesson_plan(topic, grade_level, subject, **kwargs)
