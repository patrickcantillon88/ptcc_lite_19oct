#!/usr/bin/env python3
"""
Test Suite for Differentiation Specialist Agent

Tests all functionality including:
- Learner profile creation
- Content tier generation (4 levels)
- UDL principles application
- Accommodations generation
- Scaffolding creation
- Complete differentiation orchestration
- Export formats
- Validation
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.agents.educational.differentiation_specialist.agent import (
    DifferentiationSpecialistAgent,
    LearnerProfile,
    ContentTier,
    UDLPrinciple,
    Scaffold,
    Accommodation,
    DifferentiatedContent
)


# Test Data - Sample Students
SAMPLE_STUDENTS = [
    {
        'id': 'student_001',
        'grade_level': '5th Grade',
        'performance_level': 'below',
        'learning_styles': ['visual', 'kinesthetic'],
        'accommodations': ['extended time', 'quiet workspace'],
        'ell_level': 'Intermediate',
        'iep_504': 'IEP',
        'strengths': ['hands-on activities', 'visual learning'],
        'challenges': ['reading comprehension', 'written expression']
    },
    {
        'id': 'student_002',
        'grade_level': '5th Grade',
        'performance_level': 'at',
        'learning_styles': ['auditory', 'read_write'],
        'accommodations': [],
        'strengths': ['verbal skills', 'note-taking'],
        'challenges': []
    },
    {
        'id': 'student_003',
        'grade_level': '5th Grade',
        'performance_level': 'above',
        'learning_styles': ['visual', 'read_write'],
        'accommodations': [],
        'strengths': ['critical thinking', 'independent work'],
        'challenges': []
    },
    {
        'id': 'student_004',
        'grade_level': '5th Grade',
        'performance_level': 'advanced',
        'learning_styles': ['kinesthetic', 'visual'],
        'accommodations': [],
        'strengths': ['problem solving', 'creativity'],
        'challenges': []
    }
]


class DifferentiationSpecialistTester:
    """Test harness for Differentiation Specialist Agent."""
    
    def __init__(self):
        self.agent = DifferentiationSpecialistAgent()
        self.test_results = []
        
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result."""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = f"{status} - {test_name}"
        if details:
            result += f"\n    {details}"
        self.test_results.append((passed, result))
        print(result)
    
    async def test_learner_profiles(self):
        """Test learner profile creation."""
        print("\n" + "="*60)
        print("TEST: Learner Profile Creation")
        print("="*60)
        
        try:
            profiles = await self.agent.create_learner_profiles(SAMPLE_STUDENTS)
            
            # Validate profiles
            assert len(profiles) == len(SAMPLE_STUDENTS), "Should create profile for each student"
            
            for profile in profiles:
                assert profile.student_id, "Should have student ID"
                assert profile.grade_level, "Should have grade level"
                assert profile.current_performance_level in ['below', 'at', 'above', 'advanced'], "Invalid performance level"
                assert isinstance(profile.learning_styles, list), "Learning styles should be list"
                assert isinstance(profile.accommodations_needed, list), "Accommodations should be list"
            
            self.log_test(
                "Learner Profile Creation",
                True,
                f"Created {len(profiles)} profiles - Performance levels: {[p.current_performance_level for p in profiles]}"
            )
            
            # Display sample profile
            print(f"\n  Sample Profile (student_001):")
            print(f"    Performance: {profiles[0].current_performance_level}")
            print(f"    Learning Styles: {', '.join(profiles[0].learning_styles)}")
            print(f"    Accommodations: {len(profiles[0].accommodations_needed)}")
            if profiles[0].ell_supports:
                print(f"    ELL Level: {profiles[0].language_needs}")
            
        except Exception as e:
            self.log_test("Learner Profile Creation", False, str(e))
    
    async def test_content_tiers(self):
        """Test content tier generation."""
        print("\n" + "="*60)
        print("TEST: Content Tier Generation")
        print("="*60)
        
        try:
            tiers = await self.agent.generate_content_tiers(
                lesson_topic="Photosynthesis",
                grade_level="5th Grade",
                subject="Science",
                num_tiers=4
            )
            
            # Validate tiers
            assert len(tiers) == 4, "Should generate 4 tiers"
            
            expected_levels = ['tier1_support', 'tier2_core', 'tier3_extension', 'tier4_advanced']
            for tier, expected in zip(tiers, expected_levels):
                assert tier.tier_level == expected, f"Tier level mismatch"
                assert len(tier.objectives) >= 2, "Should have multiple objectives"
                assert len(tier.activities) >= 2, "Should have multiple activities"
                assert len(tier.materials) >= 2, "Should have materials list"
                assert len(tier.success_criteria) >= 2, "Should have success criteria"
                assert tier.estimated_time, "Should have time estimate"
            
            self.log_test(
                "Content Tier Generation",
                True,
                f"Generated 4 tiers: {[t.tier_level for t in tiers]}"
            )
            
            # Display tier summaries
            for tier in tiers:
                print(f"\n  {tier.tier_level.replace('_', ' ').title()}:")
                print(f"    Target: {tier.target_audience}")
                print(f"    Objectives: {len(tier.objectives)}")
                print(f"    Activities: {len(tier.activities)}")
                print(f"    Scaffolds: {len(tier.scaffolds)}")
            
        except Exception as e:
            self.log_test("Content Tier Generation", False, str(e))
    
    async def test_udl_principles(self):
        """Test UDL principles application."""
        print("\n" + "="*60)
        print("TEST: UDL Principles Application")
        print("="*60)
        
        try:
            udl_strategies = await self.agent.apply_udl_principles("Photosynthesis")
            
            # Validate UDL
            assert len(udl_strategies) >= 3, "Should have at least 3 UDL principles"
            
            required_principles = {'engagement', 'representation', 'action_expression'}
            found_principles = {p.principle for p in udl_strategies}
            assert required_principles.issubset(found_principles), "Missing required UDL principles"
            
            for udl in udl_strategies:
                assert udl.strategy, "Should have strategy description"
                assert udl.implementation_notes, "Should have implementation notes"
                assert len(udl.examples) > 0, "Should have examples"
            
            self.log_test(
                "UDL Principles Application",
                True,
                f"Applied {len(udl_strategies)} UDL principles: {', '.join(found_principles)}"
            )
            
            # Display UDL strategies
            for udl in udl_strategies:
                print(f"\n  {udl.principle.title()}:")
                print(f"    Strategy: {udl.strategy}")
                print(f"    Examples: {len(udl.examples)}")
            
        except Exception as e:
            self.log_test("UDL Principles Application", False, str(e))
    
    async def test_accommodations(self):
        """Test accommodations generation."""
        print("\n" + "="*60)
        print("TEST: Accommodations Generation")
        print("="*60)
        
        try:
            # Create profiles first
            profiles = await self.agent.create_learner_profiles(SAMPLE_STUDENTS)
            
            # Generate accommodations
            accommodations = await self.agent.generate_accommodations(profiles)
            
            # Validate accommodations
            assert len(accommodations) > 0, "Should generate accommodations"
            
            accommodation_types = set()
            for acc in accommodations:
                assert acc.accommodation_type in ['presentation', 'response', 'setting', 'timing'], "Invalid type"
                assert acc.description, "Should have description"
                assert acc.rationale, "Should have rationale"
                assert len(acc.implementation_steps) > 0, "Should have implementation steps"
                assert len(acc.applicable_to) > 0, "Should list applicable students"
                accommodation_types.add(acc.accommodation_type)
            
            self.log_test(
                "Accommodations Generation",
                True,
                f"Generated {len(accommodations)} accommodations - Types: {', '.join(accommodation_types)}"
            )
            
            # Display accommodations
            for acc in accommodations:
                print(f"\n  {acc.accommodation_type.title()}:")
                print(f"    {acc.description}")
                print(f"    Applicable to: {len(acc.applicable_to)} students")
            
        except Exception as e:
            self.log_test("Accommodations Generation", False, str(e))
    
    async def test_scaffolds(self):
        """Test scaffolding creation."""
        print("\n" + "="*60)
        print("TEST: Scaffolding Creation")
        print("="*60)
        
        try:
            # Test scaffolds for different levels
            support_scaffolds = await self.agent.create_scaffolds("Photosynthesis", "support")
            core_scaffolds = await self.agent.create_scaffolds("Photosynthesis", "core")
            
            # Validate scaffolds
            assert len(support_scaffolds) > len(core_scaffolds), "Support should have more scaffolds"
            
            for scaffold in support_scaffolds:
                assert scaffold.scaffold_type, "Should have type"
                assert scaffold.description, "Should have description"
                assert scaffold.when_to_use, "Should specify when to use"
                assert scaffold.when_to_remove, "Should specify when to remove"
                assert len(scaffold.resources_needed) > 0, "Should list resources"
            
            self.log_test(
                "Scaffolding Creation",
                True,
                f"Support: {len(support_scaffolds)} scaffolds, Core: {len(core_scaffolds)} scaffolds"
            )
            
            # Display scaffold types
            print(f"\n  Support Level Scaffolds:")
            for scaffold in support_scaffolds[:3]:
                print(f"    - {scaffold.scaffold_type}: {scaffold.description[:50]}...")
            
        except Exception as e:
            self.log_test("Scaffolding Creation", False, str(e))
    
    async def test_complete_differentiation(self):
        """Test complete differentiation orchestration."""
        print("\n" + "="*60)
        print("TEST: Complete Differentiation")
        print("="*60)
        
        try:
            # Create profiles
            profiles = await self.agent.create_learner_profiles(SAMPLE_STUDENTS)
            
            # Generate complete differentiated content
            diff_content = await self.agent.differentiate_content(
                lesson_topic="Photosynthesis",
                grade_level="5th Grade",
                subject="Science",
                learner_profiles=profiles,
                num_tiers=4
            )
            
            # Validate differentiated content
            assert diff_content.lesson_topic == "Photosynthesis", "Topic mismatch"
            assert len(diff_content.content_tiers) == 4, "Should have 4 tiers"
            assert len(diff_content.udl_principles) >= 3, "Should have UDL principles"
            assert len(diff_content.accommodations) > 0, "Should have accommodations"
            assert len(diff_content.ell_supports) > 0, "Should have ELL supports"
            assert len(diff_content.extension_opportunities) > 0, "Should have extensions"
            assert diff_content.grouping_suggestions is not None, "Should have grouping suggestions"
            
            # Validate differentiation quality
            is_valid = diff_content.validate_differentiation()
            assert is_valid, "Differentiation validation failed"
            
            self.log_test(
                "Complete Differentiation",
                True,
                f"Tiers: {len(diff_content.content_tiers)}, "
                f"Accommodations: {len(diff_content.accommodations)}, "
                f"UDL: {len(diff_content.udl_principles)}"
            )
            
            # Check accessibility
            accessibility_recs = diff_content.check_accessibility()
            if accessibility_recs:
                print(f"\n  Accessibility Recommendations: {len(accessibility_recs)}")
                for rec in accessibility_recs[:3]:
                    print(f"    - {rec}")
            else:
                print("\n  ✓ No accessibility concerns")
            
        except Exception as e:
            self.log_test("Complete Differentiation", False, str(e))
    
    async def test_export_formats(self):
        """Test all export formats."""
        print("\n" + "="*60)
        print("TEST: Export Formats")
        print("="*60)
        
        try:
            # Generate differentiated content
            profiles = await self.agent.create_learner_profiles(SAMPLE_STUDENTS)
            diff_content = await self.agent.differentiate_content(
                lesson_topic="Photosynthesis",
                grade_level="5th Grade",
                subject="Science",
                learner_profiles=profiles
            )
            
            # Test Markdown export
            md = diff_content.to_markdown()
            assert "# Differentiated Lesson: Photosynthesis" in md, "Markdown should have header"
            assert len(md) > 2000, "Markdown export too short"
            self.log_test("Export to Markdown", True, f"{len(md)} characters")
            
            # Test JSON export
            json_str = diff_content.to_json()
            assert "lesson_topic" in json_str, "JSON should have lesson_topic"
            assert len(json_str) > 1000, "JSON export too short"
            self.log_test("Export to JSON", True, f"{len(json_str)} characters")
            
            # Test Dictionary export
            data_dict = diff_content.to_dict()
            assert isinstance(data_dict, dict), "Should return dictionary"
            assert 'lesson_topic' in data_dict, "Dict should have lesson_topic"
            self.log_test("Export to Dictionary", True, f"{len(data_dict)} keys")
            
            # Test Lesson Plan export
            lesson_plan = diff_content.to_lesson_plan()
            assert "DIFFERENTIATED LESSON PLAN" in lesson_plan, "Should have header"
            assert len(lesson_plan) > 500, "Lesson plan too short"
            self.log_test("Export to Lesson Plan", True, f"{len(lesson_plan)} characters")
            
            # Save sample outputs
            print("\n  Saving sample outputs...")
            with open('/Users/cantillonpatrick/Desktop/RAG_2/ptcc/sample_differentiation.md', 'w') as f:
                f.write(md)
            print("    ✓ Saved sample_differentiation.md")
            
        except Exception as e:
            self.log_test("Export Formats", False, str(e))
    
    async def test_tier_matching(self):
        """Test student-to-tier matching."""
        print("\n" + "="*60)
        print("TEST: Student-to-Tier Matching")
        print("="*60)
        
        try:
            # Create profiles and content
            profiles = await self.agent.create_learner_profiles(SAMPLE_STUDENTS)
            diff_content = await self.agent.differentiate_content(
                lesson_topic="Photosynthesis",
                grade_level="5th Grade",
                subject="Science",
                learner_profiles=profiles
            )
            
            # Test matching for each profile
            matches_correct = True
            for profile in profiles:
                tier = diff_content.get_tier_for_student(profile)
                assert tier is not None, f"Should find tier for {profile.student_id}"
                
                # Verify correct matching
                if profile.current_performance_level == 'below':
                    assert tier.tier_level == 'tier1_support', "Below should match tier1"
                elif profile.current_performance_level == 'at':
                    assert tier.tier_level == 'tier2_core', "At should match tier2"
                elif profile.current_performance_level == 'above':
                    assert tier.tier_level == 'tier3_extension', "Above should match tier3"
                elif profile.current_performance_level == 'advanced':
                    assert tier.tier_level == 'tier4_advanced', "Advanced should match tier4"
            
            self.log_test(
                "Student-to-Tier Matching",
                True,
                f"Successfully matched all {len(profiles)} students to appropriate tiers"
            )
            
            # Display matches
            for profile in profiles:
                tier = diff_content.get_tier_for_student(profile)
                print(f"\n  {profile.student_id} ({profile.current_performance_level}) → {tier.tier_level}")
            
        except Exception as e:
            self.log_test("Student-to-Tier Matching", False, str(e))
    
    async def test_grouping_suggestions(self):
        """Test flexible grouping suggestions."""
        print("\n" + "="*60)
        print("TEST: Flexible Grouping Suggestions")
        print("="*60)
        
        try:
            profiles = await self.agent.create_learner_profiles(SAMPLE_STUDENTS)
            diff_content = await self.agent.differentiate_content(
                lesson_topic="Photosynthesis",
                grade_level="5th Grade",
                subject="Science",
                learner_profiles=profiles
            )
            
            # Validate grouping suggestions
            groupings = diff_content.grouping_suggestions
            assert groupings is not None, "Should have grouping suggestions"
            assert 'homogeneous_ability' in groupings, "Should have ability groupings"
            assert 'heterogeneous_mixed' in groupings, "Should have mixed groupings"
            assert 'learning_style' in groupings, "Should have learning style groupings"
            
            self.log_test(
                "Flexible Grouping Suggestions",
                True,
                f"Generated {len(groupings)} grouping strategies"
            )
            
            # Display groupings
            for group_type, groups in groupings.items():
                print(f"\n  {group_type.replace('_', ' ').title()}:")
                for group in groups[:2]:  # Show first 2
                    print(f"    - {group}")
            
        except Exception as e:
            self.log_test("Flexible Grouping Suggestions", False, str(e))
    
    async def test_validation(self):
        """Test differentiation validation."""
        print("\n" + "="*60)
        print("TEST: Differentiation Validation")
        print("="*60)
        
        try:
            profiles = await self.agent.create_learner_profiles(SAMPLE_STUDENTS)
            diff_content = await self.agent.differentiate_content(
                lesson_topic="Photosynthesis",
                grade_level="5th Grade",
                subject="Science",
                learner_profiles=profiles
            )
            
            # Test validation
            is_valid = diff_content.validate_differentiation()
            self.log_test("Differentiation Validation", is_valid, "Complete differentiation passed validation")
            
            # Test accessibility checking
            accessibility_recs = diff_content.check_accessibility()
            self.log_test(
                "Accessibility Checking",
                True,
                f"Generated {len(accessibility_recs)} accessibility recommendations"
            )
            
        except Exception as e:
            self.log_test("Differentiation Validation", False, str(e))
    
    async def run_all_tests(self):
        """Run all tests."""
        print("\n" + "="*70)
        print(" DIFFERENTIATION SPECIALIST AGENT - COMPREHENSIVE TEST SUITE")
        print("="*70)
        
        await self.test_learner_profiles()
        await self.test_content_tiers()
        await self.test_udl_principles()
        await self.test_accommodations()
        await self.test_scaffolds()
        await self.test_complete_differentiation()
        await self.test_export_formats()
        await self.test_tier_matching()
        await self.test_grouping_suggestions()
        await self.test_validation()
        
        # Print summary
        print("\n" + "="*70)
        print(" TEST SUMMARY")
        print("="*70)
        
        passed = sum(1 for p, _ in self.test_results if p)
        total = len(self.test_results)
        
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! 🎉")
        else:
            print("\n⚠️  Some tests failed. Review details above.")
        
        return passed == total


async def main():
    """Main test runner."""
    tester = DifferentiationSpecialistTester()
    success = await tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
