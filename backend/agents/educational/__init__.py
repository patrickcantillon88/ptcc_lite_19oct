"""
Educational Agents Package

Contains core educational AI agents for PTCC:
- Lesson Plan Generator
- Assessment Generator
- Feedback Composer
- Differentiation Specialist
"""

from .lesson_plan_generator.agent import LessonPlanGeneratorAgent
from .assessment_generator.agent import AssessmentGeneratorAgent
from .feedback_composer.agent import FeedbackComposerAgent
from .differentiation_specialist.agent import DifferentiationSpecialistAgent

__version__ = '1.0.0'

__all__ = [
    'LessonPlanGeneratorAgent',
    'AssessmentGeneratorAgent',
    'FeedbackComposerAgent',
    'DifferentiationSpecialistAgent'
]
