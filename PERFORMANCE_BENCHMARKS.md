# Performance Benchmarks

Comprehensive performance and efficiency tests for the Privacy-Preserving Safeguarding System.

## Overview

The benchmark suite measures execution time, memory usage, and scalability across all 6 pipeline stages:

1. **Tokenization** - Student ID anonymization and data snapshot creation
2. **Pattern Extraction** - Identifying behavioral, academic, and attendance patterns
3. **Risk Assessment** - Evaluating risk levels from identified patterns
4. **External LLM Analysis** - Advanced analysis with LLM integration
5. **Result Localization** - Adapting results for specific contexts
6. **Report Generation** - Creating comprehensive safeguarding reports

## Test Coverage

### 1. Tokenization Performance (2 tests)
- **Student ID Tokenization Speed**: Tokenize 100 student IDs
  - Measures throughput of token generation
  - Ensures consistent performance under load
  
- **Anonymized Snapshot Speed**: Create anonymized data snapshot for realistic data
  - Tests full snapshot creation with multiple data categories
  - Validates performance with heterogeneous data types

### 2. Pattern Extraction Performance (2 tests)
- **Pattern Extraction Speed**: Extract patterns from realistic data
  - Includes behavioral incidents, assessments, communications, and attendance
  - Measures end-to-end pattern discovery performance
  
- **Risk Assessment Speed**: Assess risk from patterns
  - Converts identified patterns into risk scores
  - Tests risk calculation efficiency

### 3. Complete Pipeline Performance (3 tests)
- **Complete Pipeline Speed**: Full 6-stage pipeline execution
  - Tests integrated flow with realistic data
  - Validates orchestration efficiency
  
- **Large Dataset Performance**: Pipeline with 30 days of incidents
  - Tests scalability with increased data volume
  - Ensures performance remains acceptable with realistic workloads
  
- **Multiple Sequential Analyses**: Process 5 students sequentially
  - Tests throughput of batch processing
  - Validates consistent performance across multiple analyses

### 4. Memory Efficiency (2 tests)
- **Tokenizer Memory Usage**: Verify reasonable memory consumption
  - Tokenizes 1000 students
  - Validates memory state without leaks
  
- **Pattern Extractor Memory**: Verify no memory leaks during repeated extraction
  - Extracts patterns 10 times
  - Ensures resources are properly managed

### 5. Data Scaling (9 tests)
- **Scaling with Incidents**: Test with 1, 5, 10, 20, 30 incidents
  - Parameterized tests measuring linear scaling
  - Validates sub-second performance even with 30 incidents
  
- **Scaling with Assessments**: Test with 1, 5, 10, 20 assessments
  - Verifies assessment processing scales efficiently
  - Ensures consistent performance across data volumes

### 6. Concurrency (2 tests)
- **Concurrent Tokenization**: Multiple tokenizers operate independently
  - Validates session isolation
  - Ensures concurrent access doesn't cause interference
  
- **Multiple Pattern Extractors**: Multiple extractors work independently
  - Tests concurrent pattern extraction
  - Validates thread-safe operation

## Benchmark Thresholds

The system targets these performance benchmarks:

```python
BENCHMARKS = {
    "tokenization": 0.5,           # Stage 1 - 500ms
    "pattern_extraction": 1.0,      # Stage 2 - 1000ms
    "risk_assessment": 0.5,         # Stage 3 - 500ms
    "llm_analysis": 2.0,            # Stage 4 - 2000ms (includes LLM call)
    "localization": 0.5,            # Stage 5 - 500ms
    "report_generation": 0.5,       # Stage 6 - 500ms
    "complete_pipeline": 6.0,       # Total - 6000ms
    "large_dataset": 3.0,           # Large dataset - 3000ms
}
```

## Running the Benchmarks

### Run All Performance Tests
```bash
python -m pytest backend/tests/test_performance_benchmarks.py -v
```

### Run Specific Test Classes
```bash
# Tokenization tests
python -m pytest backend/tests/test_performance_benchmarks.py::TestTokenizationPerformance -v

# Pipeline performance tests
python -m pytest backend/tests/test_performance_benchmarks.py::TestPipelinePerformance -v

# Memory efficiency tests
python -m pytest backend/tests/test_performance_benchmarks.py::TestMemoryEfficiency -v

# Data scaling tests
python -m pytest backend/tests/test_performance_benchmarks.py::TestDataScaling -v

# Concurrency tests
python -m pytest backend/tests/test_performance_benchmarks.py::TestConcurrency -v
```

### Run with Timing Output
```bash
python -m pytest backend/tests/test_performance_benchmarks.py -v --tb=short -s
```

### Run with Coverage
```bash
python -m pytest backend/tests/test_performance_benchmarks.py --cov=core --cov-report=html
```

## Expected Results

All 20 tests should pass with the following characteristics:

### Execution Time
- Individual stage operations complete in <1 second
- Complete pipeline completes in <6 seconds
- Large dataset handling completes in <3 seconds
- Scaling tests show linear performance growth

### Memory Usage
- Tokenizer handles 1000+ student IDs without memory leaks
- Pattern extractor maintains consistent memory across multiple extractions
- No observable memory growth during concurrent operations

### Concurrency
- Concurrent tokenizers produce different tokens for same student ID (different sessions)
- Multiple pattern extractors operate independently
- No race conditions or cross-contamination

## Performance Optimization Guidelines

### Tokenization
- Use batch tokenization when available for large numbers of student IDs
- Consider token caching for repeated queries
- Monitor hash collision rates in token generation

### Pattern Extraction
- Filter data by date range to reduce unnecessary processing
- Use parallel processing for independent pattern extractions
- Cache pattern results for frequently analyzed students

### Risk Assessment
- Consider incremental risk assessment for streaming data
- Cache risk calculations for unchanged pattern sets
- Optimize pattern matching algorithms for large datasets

### LLM Analysis
- Implement result caching to avoid redundant LLM calls
- Use batch LLM processing when available
- Consider timeout mechanisms for LLM responses

### Pipeline Optimization
- Process students in batches for better resource utilization
- Implement early termination for obvious risk cases
- Use asynchronous processing for I/O-bound operations

## Monitoring and Alerts

### Key Metrics to Monitor
1. **Tokenization Throughput**: Tokens per second
2. **Pattern Extraction Speed**: Patterns per second
3. **Pipeline Latency**: End-to-end processing time
4. **Memory Usage**: Peak memory during processing
5. **Concurrent Throughput**: Students processed per second under load

### Alert Thresholds
- Single stage execution > 2x baseline threshold
- Pipeline execution > 12 seconds (2x normal threshold)
- Memory usage increase > 20% over baseline
- Error rates > 0.1%

## Test Results Summary

- **Total Tests**: 20
- **Test Categories**: 6
- **Coverage Areas**: Tokenization, Pattern Extraction, Risk Assessment, Pipeline, Memory, Scalability, Concurrency
- **All tests**: ✅ PASSING

## Future Enhancements

1. Add distributed processing benchmarks
2. Implement stress testing for sustained load
3. Add memory profiling with detailed heap analysis
4. Benchmark with realistic production data volumes
5. Add performance regression detection
6. Implement automated performance reporting
7. Add machine learning prediction performance tests

---

*Last Updated: 2024*
*Benchmarks run on development machine with typical performance characteristics*
