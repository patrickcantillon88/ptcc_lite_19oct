#!/usr/bin/env python3
"""
Test Suite for Feedback Composer Agent

Tests all functionality of the FeedbackComposerAgent including:
- Performance analysis
- Strengths identification
- Improvement areas generation
- Feedback composition
- Parent version generation
- Export formats
- Validation
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.agents.educational.feedback_composer.agent import (
    FeedbackComposerAgent,
    PerformanceAnalysis,
    Strength,
    ImprovementArea,
    ActionStep
)


# Test Data
SAMPLE_STUDENT_DATA = {
    'name': 'Alex Chen',
    'grade': '5th Grade',
    'subject': 'Mathematics',
    'include_parent_version': True
}

SAMPLE_ASSESSMENT_HIGH_PERFORMER = {
    'scores': {
        'math': 92,
        'reading': 88,
        'science': 90,
        'social_studies': 85
    },
    'participation': 'High',
    'effort': 'Excellent',
    'trend': 'improving'
}

SAMPLE_ASSESSMENT_NEEDS_SUPPORT = {
    'scores': {
        'math': 58,
        'reading': 65,
        'science': 62,
        'social_studies': 70
    },
    'participation': 'Average',
    'effort': 'Inconsistent',
    'trend': 'declining'
}

SAMPLE_ASSESSMENT_AVERAGE = {
    'scores': {
        'math': 78,
        'reading': 82,
        'science': 75,
        'social_studies': 80
    },
    'participation': 'Active',
    'effort': 'Consistent',
    'trend': 'stable'
}


class FeedbackComposerTester:
    """Test harness for Feedback Composer Agent."""
    
    def __init__(self):
        self.agent = FeedbackComposerAgent()
        self.test_results = []
        
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result."""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = f"{status} - {test_name}"
        if details:
            result += f"\n    {details}"
        self.test_results.append((passed, result))
        print(result)
    
    async def test_performance_analysis(self):
        """Test performance analysis method."""
        print("\n" + "="*60)
        print("TEST: Performance Analysis")
        print("="*60)
        
        try:
            # Test with high performer
            analysis = await self.agent.analyze_performance(
                SAMPLE_STUDENT_DATA,
                SAMPLE_ASSESSMENT_HIGH_PERFORMER
            )
            
            # Validate analysis
            assert analysis.overall_grade in ['A', 'B', 'C', 'D', 'F'], "Invalid grade"
            assert isinstance(analysis.subject_scores, dict), "Scores should be dict"
            assert len(analysis.trends) > 0, "Should have trends"
            
            self.log_test(
                "Performance Analysis - High Performer",
                True,
                f"Grade: {analysis.overall_grade}, Trends: {len(analysis.trends)}"
            )
            
            # Test with student needing support
            analysis_support = await self.agent.analyze_performance(
                SAMPLE_STUDENT_DATA,
                SAMPLE_ASSESSMENT_NEEDS_SUPPORT
            )
            
            self.log_test(
                "Performance Analysis - Needs Support",
                True,
                f"Grade: {analysis_support.overall_grade}, Effort: {analysis_support.effort_rating}"
            )
            
        except Exception as e:
            self.log_test("Performance Analysis", False, str(e))
    
    async def test_strengths_identification(self):
        """Test strengths identification method."""
        print("\n" + "="*60)
        print("TEST: Strengths Identification")
        print("="*60)
        
        try:
            # First get performance analysis
            analysis = await self.agent.analyze_performance(
                SAMPLE_STUDENT_DATA,
                SAMPLE_ASSESSMENT_HIGH_PERFORMER
            )
            
            # Identify strengths
            strengths = await self.agent.identify_strengths(analysis)
            
            # Validate strengths
            assert len(strengths) >= 1, "Should identify at least one strength"
            assert len(strengths) <= 5, "Should not exceed 5 strengths"
            
            for strength in strengths:
                assert strength.strength, "Strength should have description"
                assert len(strength.evidence) > 0, "Strength should have evidence"
                assert len(strength.growth_opportunities) > 0, "Should have growth opportunities"
            
            self.log_test(
                "Strengths Identification",
                True,
                f"Identified {len(strengths)} strengths with evidence"
            )
            
            # Display strengths
            for i, s in enumerate(strengths, 1):
                print(f"\n  Strength {i}: {s.strength}")
                print(f"    Evidence: {s.evidence[0]}")
            
        except Exception as e:
            self.log_test("Strengths Identification", False, str(e))
    
    async def test_improvement_areas(self):
        """Test improvement areas identification method."""
        print("\n" + "="*60)
        print("TEST: Improvement Areas Identification")
        print("="*60)
        
        try:
            # Get performance analysis
            analysis = await self.agent.analyze_performance(
                SAMPLE_STUDENT_DATA,
                SAMPLE_ASSESSMENT_NEEDS_SUPPORT
            )
            
            # Identify improvement areas
            areas = await self.agent.identify_improvement_areas(analysis)
            
            # Validate improvement areas
            assert len(areas) >= 1, "Should identify at least one improvement area"
            assert len(areas) <= 3, "Should not exceed 3 improvement areas"
            
            for area in areas:
                assert area.area, "Area should have description"
                assert area.current_level, "Should have current level"
                assert area.target_level, "Should have target level"
                assert len(area.evidence) > 0, "Should have evidence"
                assert len(area.action_steps) > 0, "Should have action steps"
                assert area.priority in ['high', 'medium', 'low'], "Invalid priority"
            
            self.log_test(
                "Improvement Areas Identification",
                True,
                f"Identified {len(areas)} improvement areas with action steps"
            )
            
            # Display areas
            for i, area in enumerate(areas, 1):
                print(f"\n  Area {i}: {area.area} (Priority: {area.priority})")
                print(f"    Current: {area.current_level} → Target: {area.target_level}")
                print(f"    Action Steps: {len(area.action_steps)}")
            
        except Exception as e:
            self.log_test("Improvement Areas Identification", False, str(e))
    
    async def test_compose_feedback(self):
        """Test complete feedback composition."""
        print("\n" + "="*60)
        print("TEST: Complete Feedback Composition")
        print("="*60)
        
        try:
            # Compose feedback for average student
            report = await self.agent.compose_feedback(
                SAMPLE_STUDENT_DATA,
                SAMPLE_ASSESSMENT_AVERAGE,
                format_type='narrative'
            )
            
            # Validate report
            assert report.student_name == SAMPLE_STUDENT_DATA['name'], "Student name mismatch"
            assert len(report.strengths) > 0, "Should have strengths"
            assert len(report.improvement_areas) > 0, "Should have improvement areas"
            assert len(report.overall_comment) >= 50, "Overall comment too short"
            assert report.parent_version is not None, "Should have parent version"
            
            # Validate report
            is_valid = report.validate_report()
            assert is_valid, "Report validation failed"
            
            # Check tone
            tone_warnings = report.check_tone()
            
            self.log_test(
                "Complete Feedback Composition",
                True,
                f"Generated report with {len(report.strengths)} strengths, {len(report.improvement_areas)} areas"
            )
            
            if tone_warnings:
                print(f"\n  Tone Warnings: {len(tone_warnings)}")
                for warning in tone_warnings:
                    print(f"    - {warning}")
            
        except Exception as e:
            self.log_test("Complete Feedback Composition", False, str(e))
    
    async def test_export_formats(self):
        """Test all export formats."""
        print("\n" + "="*60)
        print("TEST: Export Formats")
        print("="*60)
        
        try:
            # Generate report
            report = await self.agent.compose_feedback(
                SAMPLE_STUDENT_DATA,
                SAMPLE_ASSESSMENT_AVERAGE
            )
            
            # Test Markdown export
            md = report.to_markdown()
            assert "# Student Feedback Report" in md, "Markdown should have header"
            assert len(md) > 500, "Markdown export too short"
            self.log_test("Export to Markdown", True, f"{len(md)} characters")
            
            # Test JSON export
            json_str = report.to_json()
            assert "student_name" in json_str, "JSON should have student_name"
            assert len(json_str) > 200, "JSON export too short"
            self.log_test("Export to JSON", True, f"{len(json_str)} characters")
            
            # Test Dictionary export
            data_dict = report.to_dict()
            assert isinstance(data_dict, dict), "Should return dictionary"
            assert 'student_name' in data_dict, "Dict should have student_name"
            self.log_test("Export to Dictionary", True, f"{len(data_dict)} keys")
            
            # Test Report Card export
            report_card = report.to_report_card()
            assert "STUDENT PROGRESS REPORT" in report_card, "Should have header"
            assert len(report_card) > 100, "Report card too short"
            self.log_test("Export to Report Card", True, f"{len(report_card)} characters")
            
            # Test Bullet Points export
            bullets = report.to_bullet_points()
            assert "Strengths:" in bullets, "Should have strengths section"
            assert "Next Steps:" in bullets, "Should have next steps section"
            self.log_test("Export to Bullet Points", True, f"{len(bullets)} characters")
            
            # Save sample outputs
            print("\n  Saving sample outputs...")
            with open('/Users/cantillonpatrick/Desktop/RAG_2/ptcc/sample_feedback_report.md', 'w') as f:
                f.write(md)
            print("    ✓ Saved sample_feedback_report.md")
            
        except Exception as e:
            self.log_test("Export Formats", False, str(e))
    
    async def test_parent_version(self):
        """Test parent-friendly version generation."""
        print("\n" + "="*60)
        print("TEST: Parent Version Generation")
        print("="*60)
        
        try:
            # Generate report
            report = await self.agent.compose_feedback(
                SAMPLE_STUDENT_DATA,
                SAMPLE_ASSESSMENT_AVERAGE
            )
            
            # Validate parent version
            assert report.parent_version is not None, "Should have parent version"
            assert len(report.parent_version) > 100, "Parent version too short"
            assert "Dear Parents" in report.parent_version, "Should address parents"
            assert "Best regards" in report.parent_version, "Should have closing"
            
            # Check for jargon-free language
            parent_text = report.parent_version.lower()
            jargon_words = ['formative', 'summative', 'metacognition', 'pedagogy']
            jargon_found = [word for word in jargon_words if word in parent_text]
            
            self.log_test(
                "Parent Version Generation",
                len(jargon_found) == 0,
                f"Length: {len(report.parent_version)} chars, Jargon-free: {len(jargon_found) == 0}"
            )
            
            print(f"\n  Sample Parent Message:")
            print("  " + report.parent_version[:200] + "...")
            
        except Exception as e:
            self.log_test("Parent Version Generation", False, str(e))
    
    async def test_validation(self):
        """Test report validation."""
        print("\n" + "="*60)
        print("TEST: Report Validation")
        print("="*60)
        
        try:
            # Generate valid report
            report = await self.agent.compose_feedback(
                SAMPLE_STUDENT_DATA,
                SAMPLE_ASSESSMENT_AVERAGE
            )
            
            # Should pass validation
            is_valid = report.validate_report()
            self.log_test("Valid Report Validation", is_valid, "Complete report passed validation")
            
            # Test tone checking
            tone_warnings = report.check_tone()
            self.log_test(
                "Tone Checking",
                True,
                f"Generated {len(tone_warnings)} tone suggestions"
            )
            
        except Exception as e:
            self.log_test("Report Validation", False, str(e))
    
    async def test_multiple_scenarios(self):
        """Test multiple student scenarios."""
        print("\n" + "="*60)
        print("TEST: Multiple Student Scenarios")
        print("="*60)
        
        scenarios = [
            ("High Performer", SAMPLE_ASSESSMENT_HIGH_PERFORMER),
            ("Needs Support", SAMPLE_ASSESSMENT_NEEDS_SUPPORT),
            ("Average Student", SAMPLE_ASSESSMENT_AVERAGE)
        ]
        
        for scenario_name, assessment_data in scenarios:
            try:
                report = await self.agent.compose_feedback(
                    {**SAMPLE_STUDENT_DATA, 'name': f'Student - {scenario_name}'},
                    assessment_data
                )
                
                is_valid = report.validate_report()
                self.log_test(
                    f"Scenario: {scenario_name}",
                    is_valid,
                    f"Grade: {report.performance_analysis.overall_grade}, "
                    f"Strengths: {len(report.strengths)}, "
                    f"Areas: {len(report.improvement_areas)}"
                )
            except Exception as e:
                self.log_test(f"Scenario: {scenario_name}", False, str(e))
    
    async def run_all_tests(self):
        """Run all tests."""
        print("\n" + "="*70)
        print(" FEEDBACK COMPOSER AGENT - COMPREHENSIVE TEST SUITE")
        print("="*70)
        
        await self.test_performance_analysis()
        await self.test_strengths_identification()
        await self.test_improvement_areas()
        await self.test_compose_feedback()
        await self.test_export_formats()
        await self.test_parent_version()
        await self.test_validation()
        await self.test_multiple_scenarios()
        
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
    tester = FeedbackComposerTester()
    success = await tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
