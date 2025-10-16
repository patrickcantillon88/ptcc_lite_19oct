#!/usr/bin/env python3
"""
Assessment Generator Agent for PTCC

Generates comprehensive assessments with:
- Multiple question types (MC, short answer, essay, matching, true/false)
- Answer keys
- Rubrics
- Standards alignment
- Difficulty levels
- Point allocations

Integrates with:
- RAG system for content retrieval
- Memory system for teacher preferences
- Alignment system for educational appropriateness
"""

import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass, asdict, field
from enum import Enum


class QuestionType(Enum):
    """Types of assessment questions."""
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"
    TRUE_FALSE = "true_false"
    MATCHING = "matching"
    FILL_BLANK = "fill_blank"
    PROBLEM_SOLVING = "problem_solving"


class DifficultyLevel(Enum):
    """Question difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    CHALLENGING = "challenging"


class AssessmentType(Enum):
    """Types of assessments."""
    FORMATIVE = "formative"
    SUMMATIVE = "summative"
    DIAGNOSTIC = "diagnostic"
    BENCHMARK = "benchmark"
    QUIZ = "quiz"
    TEST = "test"
    EXAM = "exam"


@dataclass
class MultipleChoiceQuestion:
    """Multiple choice question."""
    question: str
    options: List[str]  # A, B, C, D
    correct_answer: str  # Letter of correct option
    explanation: Optional[str] = None
    distractor_rationale: Optional[Dict[str, str]] = None  # Why wrong answers are wrong


@dataclass
class ShortAnswerQuestion:
    """Short answer question."""
    question: str
    sample_answer: str
    key_points: List[str]
    acceptable_variations: Optional[List[str]] = None


@dataclass
class EssayQuestion:
    """Essay question."""
    prompt: str
    guiding_questions: List[str]
    expected_elements: List[str]
    word_count_range: Optional[str] = None


@dataclass
class TrueFalseQuestion:
    """True/false question."""
    statement: str
    correct_answer: bool
    explanation: str


@dataclass
class MatchingQuestion:
    """Matching question."""
    instructions: str
    column_a: List[str]
    column_b: List[str]
    correct_matches: Dict[str, str]  # A1 -> B2, etc.


@dataclass
class Question:
    """Generic question container."""
    question_id: str
    question_type: QuestionType
    content: Union[
        MultipleChoiceQuestion,
        ShortAnswerQuestion,
        EssayQuestion,
        TrueFalseQuestion,
        MatchingQuestion,
        str  # For fill-in-blank or problem-solving
    ]
    points: int
    difficulty: DifficultyLevel
    standard_alignment: Optional[str] = None
    bloom_level: Optional[str] = None
    topic: Optional[str] = None


@dataclass
class RubricCriterion:
    """Single criterion in a rubric."""
    criterion_name: str
    description: str
    points_possible: int
    levels: Dict[str, str]  # Excellent, Good, Fair, Poor -> descriptions


@dataclass
class Rubric:
    """Assessment rubric."""
    rubric_type: str  # analytic, holistic
    criteria: List[RubricCriterion]
    total_points: int
    notes: Optional[str] = None


@dataclass
class Assessment:
    """Complete assessment structure."""
    title: str
    assessment_type: AssessmentType
    grade_level: str
    subject: str
    topic: str
    
    # Questions
    questions: List[Question]
    
    # Metadata
    total_points: int
    estimated_time: str
    standards_addressed: List[str]
    
    # Rubrics (if applicable)
    rubric: Optional[Rubric] = None
    
    # Instructions
    instructions: Optional[str] = None
    materials_needed: Optional[List[str]] = None
    
    # Answer key
    answer_key: Optional[Dict[str, Any]] = None
    
    # Metadata
    created_at: datetime = None
    difficulty_distribution: Optional[Dict[str, int]] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        
        # Calculate difficulty distribution
        if self.difficulty_distribution is None and self.questions:
            dist = {}
            for q in self.questions:
                level = q.difficulty.value
                dist[level] = dist.get(level, 0) + 1
            self.difficulty_distribution = dist


class AssessmentGeneratorAgent:
    """
    Agent for generating comprehensive assessments.
    
    Capabilities:
    - Generate multiple question types
    - Create answer keys
    - Build rubrics
    - Align to standards
    - Balance difficulty levels
    - Provide scoring guides
    """
    
    def __init__(self, llm_client=None, rag_engine=None):
        """
        Initialize the assessment generator.
        
        Args:
            llm_client: LLM client for content generation
            rag_engine: RAG engine for content retrieval
        """
        self.logger = self._setup_logging()
        self.llm_client = llm_client
        self.rag_engine = rag_engine
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging."""
        logger = logging.getLogger("assessment_generator")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def generate_assessment(
        self,
        topic: str,
        grade_level: str,
        subject: str,
        assessment_type: AssessmentType = AssessmentType.QUIZ,
        question_count: int = 10,
        question_types: Optional[List[QuestionType]] = None,
        difficulty_distribution: Optional[Dict[str, int]] = None,
        standards: Optional[List[str]] = None,
        learning_objectives: Optional[List[str]] = None,
        time_limit: Optional[str] = None
    ) -> Assessment:
        """
        Generate a comprehensive assessment.
        
        Args:
            topic: Assessment topic
            grade_level: Grade level
            subject: Subject area
            assessment_type: Type of assessment
            question_count: Number of questions
            question_types: Types of questions to include
            difficulty_distribution: Distribution of difficulty levels
            standards: Curriculum standards to address
            learning_objectives: Specific objectives to assess
            time_limit: Estimated time to complete
        
        Returns:
            Complete Assessment object
        """
        self.logger.info(f"Generating {assessment_type.value}: {topic} for {grade_level}")
        
        # Set defaults
        if question_types is None:
            question_types = [QuestionType.MULTIPLE_CHOICE, QuestionType.SHORT_ANSWER]
        
        if difficulty_distribution is None:
            difficulty_distribution = {
                "easy": int(question_count * 0.3),
                "medium": int(question_count * 0.5),
                "hard": int(question_count * 0.2)
            }
        
        # Step 1: Research standards if not provided
        if not standards:
            standards = await self._research_standards(subject, grade_level, topic)
        
        # Step 2: Generate questions
        questions = await self._generate_questions(
            topic=topic,
            grade_level=grade_level,
            subject=subject,
            question_count=question_count,
            question_types=question_types,
            difficulty_distribution=difficulty_distribution,
            learning_objectives=learning_objectives
        )
        
        # Step 3: Calculate total points
        total_points = sum(q.points for q in questions)
        
        # Step 4: Create rubric if needed
        rubric = None
        if any(q.question_type in [QuestionType.ESSAY, QuestionType.SHORT_ANSWER] 
               for q in questions):
            rubric = await self._create_rubric(questions, total_points)
        
        # Step 5: Generate answer key
        answer_key = self._create_answer_key(questions)
        
        # Step 6: Create instructions
        instructions = await self._create_instructions(
            assessment_type, question_count, time_limit
        )
        
        # Build assessment
        assessment = Assessment(
            title=f"{topic} {assessment_type.value.title()}",
            assessment_type=assessment_type,
            grade_level=grade_level,
            subject=subject,
            topic=topic,
            questions=questions,
            total_points=total_points,
            estimated_time=time_limit or self._estimate_time(questions),
            standards_addressed=standards,
            rubric=rubric,
            instructions=instructions,
            answer_key=answer_key
        )
        
        self.logger.info(f"Generated assessment with {len(questions)} questions ({total_points} points)")
        return assessment
    
    async def _research_standards(
        self, subject: str, grade_level: str, topic: str
    ) -> List[str]:
        """Research relevant curriculum standards."""
        # Use RAG if available
        if self.rag_engine:
            try:
                query = f"{grade_level} {subject} standards for {topic}"
                standards_docs = await self.rag_engine.search(query, top_k=3)
                if standards_docs:
                    return [doc.get('content', '')[:200] for doc in standards_docs]
            except Exception as e:
                self.logger.warning(f"RAG search failed: {e}")
        
        # Fallback standards
        return [
            f"{subject} Standard: Understanding and applying {topic}",
            f"{subject} Standard: Demonstrating proficiency in {topic}",
        ]
    
    async def _generate_questions(
        self,
        topic: str,
        grade_level: str,
        subject: str,
        question_count: int,
        question_types: List[QuestionType],
        difficulty_distribution: Dict[str, int],
        learning_objectives: Optional[List[str]]
    ) -> List[Question]:
        """Generate questions for the assessment."""
        questions = []
        question_id = 1
        
        # Distribute questions across types
        questions_per_type = question_count // len(question_types)
        
        for q_type in question_types:
            type_count = questions_per_type
            if q_type == question_types[-1]:  # Last type gets remainder
                type_count = question_count - len(questions)
            
            for i in range(type_count):
                # Determine difficulty
                difficulty = self._select_difficulty(
                    questions, difficulty_distribution, question_count
                )
                
                # Generate question based on type
                question = await self._generate_single_question(
                    question_id=f"Q{question_id}",
                    question_type=q_type,
                    topic=topic,
                    grade_level=grade_level,
                    difficulty=difficulty,
                    objectives=learning_objectives
                )
                
                if question:
                    questions.append(question)
                    question_id += 1
        
        return questions
    
    def _select_difficulty(
        self,
        existing_questions: List[Question],
        target_distribution: Dict[str, int],
        total_count: int
    ) -> DifficultyLevel:
        """Select difficulty level based on target distribution."""
        # Count current distribution
        current = {"easy": 0, "medium": 0, "hard": 0}
        for q in existing_questions:
            current[q.difficulty.value] = current.get(q.difficulty.value, 0) + 1
        
        # Find which difficulty we need most
        for level in ["easy", "medium", "hard"]:
            if current[level] < target_distribution.get(level, 0):
                return DifficultyLevel(level)
        
        return DifficultyLevel.MEDIUM
    
    async def _generate_single_question(
        self,
        question_id: str,
        question_type: QuestionType,
        topic: str,
        grade_level: str,
        difficulty: DifficultyLevel,
        objectives: Optional[List[str]]
    ) -> Optional[Question]:
        """Generate a single question."""
        
        if question_type == QuestionType.MULTIPLE_CHOICE:
            return await self._generate_multiple_choice(
                question_id, topic, grade_level, difficulty
            )
        elif question_type == QuestionType.SHORT_ANSWER:
            return await self._generate_short_answer(
                question_id, topic, grade_level, difficulty
            )
        elif question_type == QuestionType.ESSAY:
            return await self._generate_essay(
                question_id, topic, grade_level, difficulty
            )
        elif question_type == QuestionType.TRUE_FALSE:
            return await self._generate_true_false(
                question_id, topic, grade_level, difficulty
            )
        else:
            # Fallback to short answer
            return await self._generate_short_answer(
                question_id, topic, grade_level, difficulty
            )
    
    async def _generate_multiple_choice(
        self, question_id: str, topic: str, grade_level: str, difficulty: DifficultyLevel
    ) -> Question:
        """Generate a multiple choice question."""
        if self.llm_client:
            prompt = f"""Create a {difficulty.value} multiple choice question about {topic} for {grade_level}.

Format as JSON:
{{
    "question": "Question text?",
    "options": ["A) First option", "B) Second option", "C) Third option", "D) Fourth option"],
    "correct_answer": "A",
    "explanation": "Why this is correct"
}}"""
            
            try:
                response = await self.llm_client.generate(prompt)
                data = json.loads(response)
                content = MultipleChoiceQuestion(
                    question=data['question'],
                    options=data['options'],
                    correct_answer=data['correct_answer'],
                    explanation=data.get('explanation')
                )
            except Exception as e:
                self.logger.warning(f"LLM generation failed: {e}")
                content = self._fallback_multiple_choice(topic)
        else:
            content = self._fallback_multiple_choice(topic)
        
        return Question(
            question_id=question_id,
            question_type=QuestionType.MULTIPLE_CHOICE,
            content=content,
            points=self._get_points_for_difficulty(difficulty),
            difficulty=difficulty,
            topic=topic
        )
    
    def _fallback_multiple_choice(self, topic: str) -> MultipleChoiceQuestion:
        """Create fallback multiple choice question."""
        return MultipleChoiceQuestion(
            question=f"Which of the following best describes {topic}?",
            options=[
                "A) First characteristic",
                "B) Second characteristic",
                "C) Third characteristic",
                "D) Fourth characteristic"
            ],
            correct_answer="A",
            explanation=f"This is the most accurate description of {topic}."
        )
    
    async def _generate_short_answer(
        self, question_id: str, topic: str, grade_level: str, difficulty: DifficultyLevel
    ) -> Question:
        """Generate a short answer question."""
        content = ShortAnswerQuestion(
            question=f"Explain the key concepts of {topic}. (2-3 sentences)",
            sample_answer=f"Sample answer about {topic} that demonstrates understanding.",
            key_points=[
                "First key point about the topic",
                "Second key point about the topic",
                "Application or example"
            ]
        )
        
        return Question(
            question_id=question_id,
            question_type=QuestionType.SHORT_ANSWER,
            content=content,
            points=self._get_points_for_difficulty(difficulty) * 2,
            difficulty=difficulty,
            topic=topic
        )
    
    async def _generate_essay(
        self, question_id: str, topic: str, grade_level: str, difficulty: DifficultyLevel
    ) -> Question:
        """Generate an essay question."""
        content = EssayQuestion(
            prompt=f"Analyze and evaluate {topic}. Support your response with specific examples.",
            guiding_questions=[
                f"What are the main aspects of {topic}?",
                f"How does {topic} relate to real-world applications?",
                "What evidence supports your analysis?"
            ],
            expected_elements=[
                "Clear thesis statement",
                "Supporting evidence and examples",
                "Analysis and evaluation",
                "Logical organization",
                "Proper conclusion"
            ],
            word_count_range="300-500 words"
        )
        
        return Question(
            question_id=question_id,
            question_type=QuestionType.ESSAY,
            content=content,
            points=20,
            difficulty=difficulty,
            topic=topic
        )
    
    async def _generate_true_false(
        self, question_id: str, topic: str, grade_level: str, difficulty: DifficultyLevel
    ) -> Question:
        """Generate a true/false question."""
        content = TrueFalseQuestion(
            statement=f"The fundamental principle of {topic} is always applicable in all scenarios.",
            correct_answer=False,
            explanation=f"This is false because {topic} has exceptions and limitations in certain contexts."
        )
        
        return Question(
            question_id=question_id,
            question_type=QuestionType.TRUE_FALSE,
            content=content,
            points=1,
            difficulty=difficulty,
            topic=topic
        )
    
    def _get_points_for_difficulty(self, difficulty: DifficultyLevel) -> int:
        """Get point value based on difficulty."""
        points_map = {
            DifficultyLevel.EASY: 1,
            DifficultyLevel.MEDIUM: 2,
            DifficultyLevel.HARD: 3,
            DifficultyLevel.CHALLENGING: 4
        }
        return points_map.get(difficulty, 2)
    
    async def _create_rubric(
        self, questions: List[Question], total_points: int
    ) -> Rubric:
        """Create a rubric for the assessment."""
        criteria = []
        
        # Add criteria for essay/short answer questions
        has_essay = any(q.question_type == QuestionType.ESSAY for q in questions)
        has_short_answer = any(q.question_type == QuestionType.SHORT_ANSWER for q in questions)
        
        if has_short_answer:
            criteria.append(RubricCriterion(
                criterion_name="Content Accuracy",
                description="Accuracy and completeness of the response",
                points_possible=5,
                levels={
                    "Excellent (5)": "Response is completely accurate with all key points",
                    "Good (4)": "Response is mostly accurate with most key points",
                    "Fair (3)": "Response has some accuracy but missing key points",
                    "Poor (1-2)": "Response is inaccurate or incomplete"
                }
            ))
        
        if has_essay:
            criteria.extend([
                RubricCriterion(
                    criterion_name="Thesis & Organization",
                    description="Clarity of thesis and logical organization",
                    points_possible=5,
                    levels={
                        "Excellent (5)": "Clear thesis, logical flow, strong organization",
                        "Good (4)": "Clear thesis, mostly organized",
                        "Fair (3)": "Thesis present but organization needs work",
                        "Poor (1-2)": "Unclear thesis or poor organization"
                    }
                ),
                RubricCriterion(
                    criterion_name="Evidence & Examples",
                    description="Use of supporting evidence and examples",
                    points_possible=5,
                    levels={
                        "Excellent (5)": "Strong, relevant evidence with clear connections",
                        "Good (4)": "Good evidence with some connections",
                        "Fair (3)": "Some evidence but weak connections",
                        "Poor (1-2)": "Little to no evidence provided"
                    }
                ),
                RubricCriterion(
                    criterion_name="Analysis & Critical Thinking",
                    description="Depth of analysis and critical thinking",
                    points_possible=5,
                    levels={
                        "Excellent (5)": "Deep analysis with insightful connections",
                        "Good (4)": "Good analysis with some depth",
                        "Fair (3)": "Basic analysis present",
                        "Poor (1-2)": "Little to no analysis"
                    }
                )
            ])
        
        rubric_points = sum(c.points_possible for c in criteria)
        
        return Rubric(
            rubric_type="analytic",
            criteria=criteria,
            total_points=rubric_points,
            notes="Use this rubric to evaluate open-ended responses"
        )
    
    def _create_answer_key(self, questions: List[Question]) -> Dict[str, Any]:
        """Create answer key for the assessment."""
        answer_key = {}
        
        for question in questions:
            q_id = question.question_id
            
            if question.question_type == QuestionType.MULTIPLE_CHOICE:
                content = question.content
                answer_key[q_id] = {
                    "answer": content.correct_answer,
                    "points": question.points,
                    "explanation": content.explanation
                }
            elif question.question_type == QuestionType.SHORT_ANSWER:
                content = question.content
                answer_key[q_id] = {
                    "key_points": content.key_points,
                    "sample_answer": content.sample_answer,
                    "points": question.points
                }
            elif question.question_type == QuestionType.TRUE_FALSE:
                content = question.content
                answer_key[q_id] = {
                    "answer": content.correct_answer,
                    "explanation": content.explanation,
                    "points": question.points
                }
            elif question.question_type == QuestionType.ESSAY:
                content = question.content
                answer_key[q_id] = {
                    "expected_elements": content.expected_elements,
                    "guiding_questions": content.guiding_questions,
                    "points": question.points,
                    "note": "Use rubric to evaluate"
                }
        
        return answer_key
    
    async def _create_instructions(
        self,
        assessment_type: AssessmentType,
        question_count: int,
        time_limit: Optional[str]
    ) -> str:
        """Create assessment instructions."""
        instructions = f"""Assessment Instructions:

1. This {assessment_type.value} contains {question_count} questions.
2. Read each question carefully before answering.
3. Show all work for problem-solving questions.
4. Check your answers before submitting.
"""
        
        if time_limit:
            instructions += f"5. Time limit: {time_limit}\n"
        
        instructions += "\nGood luck!"
        
        return instructions
    
    def _estimate_time(self, questions: List[Question]) -> str:
        """Estimate time needed for assessment."""
        minutes = 0
        
        for question in questions:
            if question.question_type == QuestionType.MULTIPLE_CHOICE:
                minutes += 1
            elif question.question_type == QuestionType.TRUE_FALSE:
                minutes += 0.5
            elif question.question_type == QuestionType.SHORT_ANSWER:
                minutes += 5
            elif question.question_type == QuestionType.ESSAY:
                minutes += 15
            else:
                minutes += 3
        
        return f"{int(minutes)} minutes"
    
    def to_dict(self, assessment: Assessment) -> Dict[str, Any]:
        """Convert assessment to dictionary."""
        result = {
            "title": assessment.title,
            "assessment_type": assessment.assessment_type.value,
            "grade_level": assessment.grade_level,
            "subject": assessment.subject,
            "topic": assessment.topic,
            "total_points": assessment.total_points,
            "estimated_time": assessment.estimated_time,
            "standards_addressed": assessment.standards_addressed,
            "instructions": assessment.instructions,
            "questions": [],
            "answer_key": assessment.answer_key,
            "difficulty_distribution": assessment.difficulty_distribution
        }
        
        # Convert questions
        for q in assessment.questions:
            q_dict = {
                "question_id": q.question_id,
                "question_type": q.question_type.value,
                "points": q.points,
                "difficulty": q.difficulty.value,
                "topic": q.topic
            }
            
            # Add content based on type
            if isinstance(q.content, (MultipleChoiceQuestion, ShortAnswerQuestion, 
                                     EssayQuestion, TrueFalseQuestion)):
                q_dict["content"] = asdict(q.content)
            else:
                q_dict["content"] = str(q.content)
            
            result["questions"].append(q_dict)
        
        # Add rubric if present
        if assessment.rubric:
            result["rubric"] = {
                "rubric_type": assessment.rubric.rubric_type,
                "total_points": assessment.rubric.total_points,
                "criteria": [asdict(c) for c in assessment.rubric.criteria]
            }
        
        return result
    
    def to_student_version(self, assessment: Assessment) -> str:
        """Generate student-facing version (without answers)."""
        output = f"""# {assessment.title}

**Name:** _______________________  **Date:** ___________

**Instructions:**
{assessment.instructions}

**Time:** {assessment.estimated_time}
**Total Points:** {assessment.total_points}

---

"""
        
        for question in assessment.questions:
            output += f"\n## {question.question_id} ({question.points} points)\n\n"
            
            if question.question_type == QuestionType.MULTIPLE_CHOICE:
                content = question.content
                output += f"{content.question}\n\n"
                for option in content.options:
                    output += f"{option}\n"
                output += "\n**Answer:** ___\n"
            
            elif question.question_type == QuestionType.SHORT_ANSWER:
                content = question.content
                output += f"{content.question}\n\n"
                output += "_" * 50 + "\n\n"
                output += "_" * 50 + "\n\n"
            
            elif question.question_type == QuestionType.ESSAY:
                content = question.content
                output += f"**Prompt:** {content.prompt}\n\n"
                output += f"**Word Count:** {content.word_count_range}\n\n"
                output += "**Your Response:**\n\n"
                output += "_" * 70 + "\n" * 10
            
            elif question.question_type == QuestionType.TRUE_FALSE:
                content = question.content
                output += f"{content.statement}\n\n"
                output += "☐ True    ☐ False\n"
            
            output += "\n---\n"
        
        return output
    
    def to_answer_key(self, assessment: Assessment) -> str:
        """Generate teacher answer key."""
        output = f"""# {assessment.title} - ANSWER KEY

**Total Points:** {assessment.total_points}

---

"""
        
        for question in assessment.questions:
            output += f"\n## {question.question_id} ({question.points} points)\n\n"
            
            if question.question_type == QuestionType.MULTIPLE_CHOICE:
                content = question.content
                output += f"**Answer:** {content.correct_answer}\n"
                if content.explanation:
                    output += f"**Explanation:** {content.explanation}\n"
            
            elif question.question_type == QuestionType.SHORT_ANSWER:
                content = question.content
                output += f"**Key Points:**\n"
                for point in content.key_points:
                    output += f"- {point}\n"
                output += f"\n**Sample Answer:** {content.sample_answer}\n"
            
            elif question.question_type == QuestionType.ESSAY:
                content = question.content
                output += f"**Expected Elements:**\n"
                for element in content.expected_elements:
                    output += f"- {element}\n"
                output += f"\n**Note:** Use rubric to evaluate\n"
            
            elif question.question_type == QuestionType.TRUE_FALSE:
                content = question.content
                output += f"**Answer:** {content.correct_answer}\n"
                output += f"**Explanation:** {content.explanation}\n"
            
            output += "\n---\n"
        
        # Add rubric if present
        if assessment.rubric:
            output += f"\n# Rubric\n\n"
            for criterion in assessment.rubric.criteria:
                output += f"\n### {criterion.criterion_name} ({criterion.points_possible} points)\n"
                output += f"{criterion.description}\n\n"
                for level, desc in criterion.levels.items():
                    output += f"**{level}:** {desc}\n"
                output += "\n"
        
        return output


# Convenience function
async def generate_assessment(
    topic: str,
    grade_level: str,
    subject: str,
    **kwargs
) -> Assessment:
    """Convenience function to generate an assessment."""
    agent = AssessmentGeneratorAgent()
    return await agent.generate_assessment(topic, grade_level, subject, **kwargs)
