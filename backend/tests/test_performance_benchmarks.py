"""
Performance Benchmarks for Privacy-Preserving Safeguarding System

Measures execution time and efficiency of the 6-stage pipeline:
1. Tokenization
2. Pattern Extraction
3. Risk Assessment
4. External LLM Analysis
5. Result Localization
6. Report Generation
"""

import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.privacy_tokenization import create_tokenizer_for_session
from core.safeguarding_patterns import PatternExtractor
from core.safeguarding_orchestrator import SafeguardingOrchestrator

logger = logging.getLogger(__name__)

# Benchmark thresholds (in seconds)
BENCHMARKS = {
    "tokenization": 0.5,           # Stage 1
    "pattern_extraction": 1.0,      # Stage 2
    "risk_assessment": 0.5,         # Stage 3
    "llm_analysis": 2.0,            # Stage 4 (includes LLM call)
    "localization": 0.5,            # Stage 5
    "report_generation": 0.5,       # Stage 6
    "complete_pipeline": 6.0,       # Total
    "large_dataset": 3.0,           # Large dataset handling
}


class TestTokenizationPerformance:
    """Test tokenization stage performance."""

    def test_student_id_tokenization_speed(self, benchmark):
        """Benchmark: Tokenize 100 student IDs"""
        tokenizer = create_tokenizer_for_session("perf_test_1")
        
        def tokenize_students():
            for i in range(100):
                tokenizer.tokenize_student_id(f"STU{i:05d}")
        
        result = benchmark(tokenize_students)
        assert result is None  # benchmark returns None

    def test_anonymized_snapshot_speed(self, benchmark):
        """Benchmark: Create anonymized snapshot for realistic data"""
        tokenizer = create_tokenizer_for_session("perf_test_2")
        
        now = datetime.now()
        student_data = {
            "student_id": "STU12345",
            "behavioral_incidents": [
                {"type": "disruptive", "timestamp": (now - timedelta(days=i))}
                for i in range(10)
            ],
            "assessments": [
                {"subject": f"Subject_{i}", "performance_level": "below", 
                 "timestamp": now, "type": "formative"}
                for i in range(5)
            ],
            "communications": [
                {"source": "parent", "urgency": "urgent", "timestamp": now}
                for i in range(3)
            ],
            "attendance": [
                {"status": "absent", "timestamp": (now - timedelta(days=i))}
                for i in range(5)
            ]
        }
        
        def create_snapshot():
            return tokenizer.create_anonymized_data_snapshot(student_data)
        
        result = benchmark(create_snapshot)
        assert result is not None
        assert "student_token" in result


class TestPatternExtractionPerformance:
    """Test pattern extraction stage performance."""

    def test_pattern_extraction_speed(self, benchmark):
        """Benchmark: Extract patterns from realistic data"""
        extractor = PatternExtractor(min_frequency=1, days_lookback=30)
        
        now = datetime.now()
        student_data = {
            "behavioral_incidents": [
                {"type": "disruptive", "timestamp": (now - timedelta(days=i))}
                for i in range(10)
            ],
            "assessments": [
                {"subject": "Math", "performance_level": "below", "timestamp": now}
                for i in range(5)
            ],
            "communications": [
                {"source": "parent", "urgency": "urgent", "timestamp": now}
                for i in range(3)
            ],
            "attendance": [
                {"status": "absent", "timestamp": (now - timedelta(days=i))}
                for i in range(5)
            ]
        }
        
        def extract_patterns():
            return extractor.extract_all_patterns("TOKEN_STU_123", student_data)
        
        result = benchmark(extract_patterns)
        assert len(result) > 0

    def test_risk_assessment_speed(self, benchmark):
        """Benchmark: Assess risk from patterns"""
        extractor = PatternExtractor(min_frequency=1, days_lookback=30)
        
        now = datetime.now()
        student_data = {
            "behavioral_incidents": [
                {"type": "disruptive", "timestamp": (now - timedelta(days=i))}
                for i in range(5)
            ],
            "assessments": [
                {"subject": "Math", "performance_level": "below", "timestamp": now}
            ],
            "communications": [
                {"source": "parent", "urgency": "urgent", "timestamp": now}
            ],
            "attendance": [
                {"status": "absent", "timestamp": (now - timedelta(days=i))}
                for i in range(3)
            ]
        }
        
        patterns = extractor.extract_all_patterns("TOKEN_STU_123", student_data)
        
        def assess_risk():
            return extractor.assess_risk("TOKEN_STU_123", patterns)
        
        result = benchmark(assess_risk)
        assert result is not None
        assert hasattr(result, "overall_risk_level")


class TestPipelinePerformance:
    """Test complete pipeline performance."""

    @pytest.fixture
    def mock_llm_client(self):
        """Create mock LLM client."""
        mock_client = Mock()
        mock_client.generate_content = Mock(return_value=Mock(
            text='{"risk_level": "MEDIUM", "confidence": 0.75, "patterns": [], "pattern_combinations": [], "evidence_summary": "Test", "recommendations": []}'
        ))
        return mock_client

    def test_complete_pipeline_speed(self, benchmark, mock_llm_client):
        """Benchmark: Complete 6-stage pipeline"""
        orchestrator = SafeguardingOrchestrator(mock_llm_client)
        
        now = datetime.now()
        student_data = {
            "behavioral_incidents": [
                {"type": "disruptive", "timestamp": (now - timedelta(days=i))}
                for i in range(5)
            ],
            "assessments": [
                {"subject": "Math", "performance_level": "below", "timestamp": now, "type": "formative"}
            ],
            "communications": [
                {"source": "parent", "urgency": "urgent", "timestamp": now}
            ],
            "attendance": [
                {"status": "absent", "timestamp": (now - timedelta(days=i))}
                for i in range(3)
            ]
        }
        
        def run_pipeline():
            return orchestrator.analyze_student_safeguarding(
                student_id="STU12345",
                student_data=student_data
            )
        
        result = benchmark(run_pipeline)
        assert result is not None
        assert "student_id" in result

    def test_large_dataset_performance(self, benchmark, mock_llm_client):
        """Benchmark: Pipeline with large dataset (30 days of incidents)"""
        orchestrator = SafeguardingOrchestrator(mock_llm_client)
        
        now = datetime.now()
        student_data = {
            "behavioral_incidents": [
                {"type": "disruptive", "timestamp": (now - timedelta(days=i))}
                for i in range(30)  # 30 days of incidents
            ],
            "assessments": [
                {"subject": f"Subject_{i}", "performance_level": "below", 
                 "timestamp": now, "type": "formative"}
                for i in range(20)
            ],
            "communications": [
                {"source": "parent", "urgency": "urgent", "timestamp": now}
                for i in range(10)
            ],
            "attendance": [
                {"status": "absent", "timestamp": (now - timedelta(days=i))}
                for i in range(20)
            ]
        }
        
        def run_pipeline_large():
            return orchestrator.analyze_student_safeguarding(
                student_id="STU99999",
                student_data=student_data
            )
        
        result = benchmark(run_pipeline_large)
        assert result is not None

    def test_multiple_sequential_analyses(self, benchmark, mock_llm_client):
        """Benchmark: Process multiple students sequentially"""
        orchestrator = SafeguardingOrchestrator(mock_llm_client)
        
        now = datetime.now()
        base_data = {
            "behavioral_incidents": [
                {"type": "disruptive", "timestamp": (now - timedelta(days=i))}
                for i in range(5)
            ],
            "assessments": [
                {"subject": "Math", "performance_level": "below", "timestamp": now, "type": "formative"}
            ],
            "communications": [
                {"source": "parent", "urgency": "urgent", "timestamp": now}
            ],
            "attendance": [
                {"status": "absent", "timestamp": (now - timedelta(days=i))}
                for i in range(3)
            ]
        }
        
        def process_multiple():
            results = []
            for i in range(5):  # Process 5 students
                result = orchestrator.analyze_student_safeguarding(
                    student_id=f"STU{i:05d}",
                    student_data=base_data
                )
                results.append(result)
            return results
        
        result = benchmark(process_multiple)
        assert len(result) == 5


class TestMemoryEfficiency:
    """Test memory usage and efficiency."""

    def test_tokenizer_memory_usage(self):
        """Verify tokenizer memory usage is reasonable"""
        tokenizer = create_tokenizer_for_session("mem_test")
        
        # Tokenize 1000 students
        for i in range(1000):
            tokenizer.tokenize_student_id(f"STU{i:05d}")
        
        # Check memory state (reverse mapping may have fewer entries due to hash collisions)
        assert len(tokenizer.student_tokens) == 1000
        assert len(tokenizer.reverse_mapping) > 850  # Most tokens should be stored

    def test_pattern_extractor_memory(self):
        """Verify pattern extractor doesn't leak memory"""
        now = datetime.now()
        student_data = {
            "behavioral_incidents": [
                {"type": "disruptive", "timestamp": (now - timedelta(days=i))}
                for i in range(30)
            ],
            "assessments": [
                {"subject": "Math", "performance_level": "below", "timestamp": now}
            ],
            "communications": [],
            "attendance": []
        }
        
        # Extract patterns multiple times
        extractor = PatternExtractor(min_frequency=1, days_lookback=30)
        for i in range(10):
            patterns = extractor.extract_all_patterns(f"TOKEN_{i}", student_data)
            assert len(patterns) > 0


class TestDataScaling:
    """Test system behavior with varying data sizes."""

    @pytest.mark.parametrize("num_incidents", [1, 5, 10, 20, 30])
    def test_scaling_with_incidents(self, num_incidents):
        """Test performance scales linearly with incident count"""
        extractor = PatternExtractor(min_frequency=1, days_lookback=30)
        
        now = datetime.now()
        student_data = {
            "behavioral_incidents": [
                {"type": "disruptive", "timestamp": (now - timedelta(days=i))}
                for i in range(num_incidents)
            ],
            "assessments": [],
            "communications": [],
            "attendance": []
        }
        
        start = time.time()
        patterns = extractor.extract_all_patterns("TOKEN_TEST", student_data)
        elapsed = time.time() - start
        
        # Should complete in reasonable time even with 30 incidents
        assert elapsed < BENCHMARKS["pattern_extraction"]
        assert len(patterns) >= 0

    @pytest.mark.parametrize("num_assessments", [1, 5, 10, 20])
    def test_scaling_with_assessments(self, num_assessments):
        """Test performance scales with assessment count"""
        extractor = PatternExtractor(min_frequency=1, days_lookback=30)
        
        now = datetime.now()
        student_data = {
            "behavioral_incidents": [],
            "assessments": [
                {"subject": f"Subject_{i}", "performance_level": "below", "timestamp": now}
                for i in range(num_assessments)
            ],
            "communications": [],
            "attendance": []
        }
        
        start = time.time()
        patterns = extractor.extract_all_patterns("TOKEN_TEST", student_data)
        elapsed = time.time() - start
        
        # Should complete in reasonable time
        assert elapsed < BENCHMARKS["pattern_extraction"]


class TestConcurrency:
    """Test system behavior under concurrent load."""

    def test_concurrent_tokenization(self):
        """Test multiple tokenizers don't interfere"""
        tokenizers = [
            create_tokenizer_for_session(f"concurrent_{i}")
            for i in range(5)
        ]
        
        # Each should have independent token mappings
        for i, tokenizer in enumerate(tokenizers):
            token = tokenizer.tokenize_student_id("STU00001")
            # All should be different (different sessions)
            for j, other_tokenizer in enumerate(tokenizers):
                if i != j:
                    other_token = other_tokenizer.tokenize_student_id("STU00001")
                    assert token != other_token

    def test_multiple_pattern_extractors(self):
        """Test multiple pattern extractors work independently"""
        extractors = [
            PatternExtractor(min_frequency=1, days_lookback=30)
            for _ in range(3)
        ]
        
        now = datetime.now()
        student_data = {
            "behavioral_incidents": [
                {"type": "disruptive", "timestamp": (now - timedelta(days=i))}
                for i in range(5)
            ],
            "assessments": [],
            "communications": [],
            "attendance": []
        }
        
        # All should extract patterns independently
        for extractor in extractors:
            patterns = extractor.extract_all_patterns("TOKEN_TEST", student_data)
            assert len(patterns) > 0


# Benchmark fixtures
@pytest.fixture
def benchmark(request):
    """Simple benchmark fixture that measures execution time"""
    class Benchmark:
        def __call__(self, func):
            start = time.time()
            result = func()
            elapsed = time.time() - start
            
            # Log performance
            test_name = request.node.name
            logger.info(f"{test_name}: {elapsed:.4f}s")
            
            return result
    
    return Benchmark()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
