"""
Lesson Plan Generator Agent Package

Provides comprehensive lesson plan generation with:
- Standards alignment
- Learning objectives
- Instructional activities
- Assessments
- Differentiation
"""

from .agent import (
    LessonPlanGeneratorAgent,
    LessonPlan,
    LearningObjective,
    Activity,
    Assessment,
    LessonStructure,
    BloomLevel,
    generate_lesson_plan
)

__all__ = [
    'LessonPlanGeneratorAgent',
    'LessonPlan',
    'LearningObjective',
    'Activity',
    'Assessment',
    'LessonStructure',
    'BloomLevel',
    'generate_lesson_plan'
]

__version__ = '1.0.0'
