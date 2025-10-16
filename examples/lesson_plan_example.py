#!/usr/bin/env python3
"""
Lesson Plan Generator Example

Demonstrates how to use the LessonPlanGeneratorAgent to create
comprehensive lesson plans.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from agents.educational.lesson_plan_generator import (
    LessonPlanGeneratorAgent,
    LessonStructure
)


async def example_basic_lesson_plan():
    """Generate a basic lesson plan."""
    print("=" * 70)
    print("EXAMPLE 1: Basic Lesson Plan")
    print("=" * 70)
    
    agent = LessonPlanGeneratorAgent()
    
    lesson_plan = await agent.generate_lesson_plan(
        topic="Photosynthesis",
        grade_level="5th Grade",
        subject="Science",
        duration="45 minutes"
    )
    
    # Convert to markdown
    markdown = agent.to_markdown(lesson_plan)
    print(markdown)
    
    return lesson_plan


async def example_5e_lesson_plan():
    """Generate a 5E model lesson plan."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: 5E Model Lesson Plan")
    print("=" * 70)
    
    agent = LessonPlanGeneratorAgent()
    
    lesson_plan = await agent.generate_lesson_plan(
        topic="Fractions",
        grade_level="4th Grade",
        subject="Mathematics",
        duration="60 minutes",
        lesson_structure=LessonStructure.FIVE_E,
        learning_goals=[
            "Understand equivalent fractions",
            "Compare fractions with different denominators"
        ],
        prior_knowledge="Students know basic fraction concepts and can identify numerators and denominators"
    )
    
    print(f"\n**Title:** {lesson_plan.title}")
    print(f"**Duration:** {lesson_plan.duration}")
    print(f"**Structure:** {lesson_plan.lesson_structure}")
    print(f"\n**Learning Objectives:**")
    for i, obj in enumerate(lesson_plan.learning_objectives, 1):
        print(f"  {i}. {obj.description}")
        print(f"     (Bloom's Level: {obj.bloom_level})")
    
    print(f"\n**Activities:** {len(lesson_plan.activities)} activities")
    for act in lesson_plan.activities:
        print(f"  - {act.name} ({act.duration_minutes} min)")
    
    print(f"\n**Materials:**")
    for mat in lesson_plan.materials_needed:
        print(f"  - {mat}")
    
    return lesson_plan


async def example_differentiated_lesson():
    """Generate a lesson with differentiation."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Differentiated Lesson Plan")
    print("=" * 70)
    
    agent = LessonPlanGeneratorAgent()
    
    lesson_plan = await agent.generate_lesson_plan(
        topic="The Solar System",
        grade_level="3rd Grade",
        subject="Science",
        duration="45 minutes",
        student_needs={
            "ell_students": 5,
            "gifted": 3,
            "iep": 2
        }
    )
    
    print(f"\n**Title:** {lesson_plan.title}")
    print(f"\n**Essential Question:**")
    print(f"{lesson_plan.essential_question}")
    
    print(f"\n**Differentiation Strategies:**")
    for strategy_type, strategy in lesson_plan.differentiation_strategies.items():
        print(f"\n**{strategy_type.replace('_', ' ').title()}:**")
        print(f"  {strategy}")
    
    print(f"\n**Extensions:**")
    for ext in lesson_plan.extensions:
        print(f"  - {ext}")
    
    return lesson_plan


async def example_json_export():
    """Generate and export as JSON."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: JSON Export")
    print("=" * 70)
    
    agent = LessonPlanGeneratorAgent()
    
    lesson_plan = await agent.generate_lesson_plan(
        topic="World War II",
        grade_level="High School",
        subject="History",
        duration="90 minutes"
    )
    
    # Convert to dictionary
    lesson_dict = agent.to_dict(lesson_plan)
    
    import json
    print(json.dumps(lesson_dict, indent=2, default=str))
    
    return lesson_plan


async def example_comparison():
    """Generate multiple lesson plans and compare."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Lesson Plan Comparison")
    print("=" * 70)
    
    agent = LessonPlanGeneratorAgent()
    
    # Generate three different structures for the same topic
    structures = [
        LessonStructure.DIRECT_INSTRUCTION,
        LessonStructure.INQUIRY_BASED,
        LessonStructure.PROJECT_BASED
    ]
    
    print(f"\nGenerating lesson plans for 'Climate Change' using different structures...\n")
    
    for structure in structures:
        lesson_plan = await agent.generate_lesson_plan(
            topic="Climate Change",
            grade_level="8th Grade",
            subject="Science",
            duration="45 minutes",
            lesson_structure=structure
        )
        
        print(f"**{structure.value.upper()}:**")
        print(f"  Activities: {len(lesson_plan.activities)}")
        print(f"  Objectives: {len(lesson_plan.learning_objectives)}")
        print(f"  First Activity: {lesson_plan.activities[0].name}")
        print()


async def main():
    """Run all examples."""
    print("\n" + "🎓" * 35)
    print("LESSON PLAN GENERATOR - EXAMPLES")
    print("🎓" * 35 + "\n")
    
    # Run examples
    await example_basic_lesson_plan()
    await example_5e_lesson_plan()
    await example_differentiated_lesson()
    await example_json_export()
    await example_comparison()
    
    print("\n" + "=" * 70)
    print("✅ All examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
