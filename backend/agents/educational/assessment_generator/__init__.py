"""
Assessment Generator Agent Package

Provides comprehensive assessment generation with:
- Multiple question types
- Answer keys
- Rubrics
- Standards alignment
- Difficulty balancing
"""

from .agent import (
    AssessmentGeneratorAgent,
    Assessment,
    Question,
    QuestionType,
    AssessmentType,
    DifficultyLevel,
    MultipleChoiceQuestion,
    ShortAnswerQuestion,
    EssayQuestion,
    TrueFalseQuestion,
    Rubric,
    RubricCriterion,
    generate_assessment
)

__all__ = [
    'AssessmentGeneratorAgent',
    'Assessment',
    'Question',
    'QuestionType',
    'AssessmentType',
    'DifficultyLevel',
    'MultipleChoiceQuestion',
    'ShortAnswerQuestion',
    'EssayQuestion',
    'TrueFalseQuestion',
    'Rubric',
    'RubricCriterion',
    'generate_assessment'
]

__version__ = '1.0.0'
