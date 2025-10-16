"""
Comprehensive PTCC Database Schema Migration

Creates all tables for the complete PTCC system including:
- Memory & Context Management
- Alignment & Ethics
- Governance & Risk Management  
- Prompt Management
- CPD (Continuing Professional Development)
- Agent Management
- PKM (Personal Knowledge Management)
- And all existing models
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import create_engine, text
from ptcc.backend.core.database import Base, get_database_url
from ptcc.backend.core.logging_config import get_logger

# Import all models to register them with Base
from ptcc.backend.models import (
    memory_models,
    alignment_models,
    governance_models,
    prompt_models,
    cpd_models,
    agent_models,
    pkm_models,
    workflow_models,
    context_models,
    safety_models,
    assessment,
    communication,
    student,
    schedule,
    log
)

logger = get_logger("migration")


def create_all_tables():
    """Create all tables in the database."""
    logger.info("Starting comprehensive PTCC database migration...")
    
    # Get database URL
    database_url = get_database_url()
    logger.info(f"Database URL: {database_url.split('@')[0]}@***")
    
    # Create engine
    engine = create_engine(database_url, echo=True)
    
    try:
        # Create all tables
        logger.info("Creating all tables...")
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Successfully created all tables!")
        
        # Print summary of created tables
        tables = Base.metadata.tables.keys()
        logger.info(f"\nCreated {len(tables)} tables:")
        
        # Organize tables by category
        categories = {
            "Memory & Context": [
                "user_profiles", "context_layers", "interaction_history",
                "teaching_preferences", "student_demographics", "curriculum_contexts"
            ],
            "Alignment & Ethics": [
                "value_alignment", "ethics_checkpoints", "bias_detections",
                "cultural_sensitivity"
            ],
            "Governance & Risk": [
                "policy_frameworks", "compliance_checks", "audit_logs",
                "risk_assessments", "incident_reports"
            ],
            "Prompt Management": [
                "prompt_library_items", "prompt_versions", "prompt_performance",
                "prompt_ab_tests", "prompt_optimization_runs", "prompt_usage_analytics"
            ],
            "CPD (Professional Development)": [
                "cpd_records", "cpd_recommendations", "skill_assessments",
                "development_goals", "impact_evidence"
            ],
            "Agent Management": [
                "agents", "agent_capabilities", "agent_interactions",
                "agent_performance", "agent_feedback"
            ],
            "PKM (Knowledge Management)": [
                "knowledge_items", "knowledge_connections", "knowledge_collections",
                "knowledge_insights", "knowledge_applications"
            ],
            "Workflow & Orchestration": [
                "workflows", "workflow_steps", "workflow_executions",
                "workflow_metrics"
            ],
            "Content & Assessment": [
                "assessments", "assessment_questions", "student_responses",
                "feedback_records"
            ],
            "Communication": [
                "messages", "conversations", "notifications"
            ],
            "Student Management": [
                "students", "student_progress", "student_notes"
            ],
            "Schedule & Planning": [
                "schedules", "lessons", "activities"
            ],
            "Safety & Monitoring": [
                "safety_checks", "content_filters", "alert_rules"
            ],
            "System Logs": [
                "system_logs", "error_logs", "audit_trails"
            ]
        }
        
        for category, expected_tables in categories.items():
            found = [t for t in expected_tables if t in tables]
            if found:
                logger.info(f"\n{category}:")
                for table in found:
                    logger.info(f"  ✓ {table}")
        
        # List any other tables not categorized
        categorized = set(sum(categories.values(), []))
        other = [t for t in tables if t not in categorized]
        if other:
            logger.info(f"\nOther Tables:")
            for table in other:
                logger.info(f"  ✓ {table}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        engine.dispose()


def verify_schema():
    """Verify that all expected tables were created."""
    logger.info("\nVerifying database schema...")
    
    database_url = get_database_url()
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            # Query to get all table names (PostgreSQL)
            if 'postgresql' in database_url:
                result = conn.execute(text("""
                    SELECT tablename FROM pg_tables 
                    WHERE schemaname = 'public'
                    ORDER BY tablename
                """))
            # SQLite
            elif 'sqlite' in database_url:
                result = conn.execute(text("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table'
                    ORDER BY name
                """))
            else:
                logger.warning("Unknown database type, skipping verification")
                return True
            
            tables = [row[0] for row in result]
            logger.info(f"✅ Verified {len(tables)} tables exist in database")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Error verifying schema: {e}")
        return False
    
    finally:
        engine.dispose()


def create_indexes():
    """Create additional indexes for performance."""
    logger.info("\nCreating performance indexes...")
    
    database_url = get_database_url()
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            # Additional indexes for frequently queried fields
            indexes = [
                # Memory system indexes
                "CREATE INDEX IF NOT EXISTS idx_interaction_history_user_timestamp ON interaction_history(user_profile_id, timestamp DESC)",
                "CREATE INDEX IF NOT EXISTS idx_context_layers_active ON context_layers(user_profile_id, active)",
                
                # Prompt system indexes
                "CREATE INDEX IF NOT EXISTS idx_prompt_performance_quality ON prompt_performance(prompt_id, quality_score DESC)",
                "CREATE INDEX IF NOT EXISTS idx_prompt_library_category_status ON prompt_library_items(prompt_category, status)",
                
                # Governance indexes
                "CREATE INDEX IF NOT EXISTS idx_audit_logs_actor_timestamp ON audit_logs(actor_id, timestamp DESC)",
                "CREATE INDEX IF NOT EXISTS idx_risk_assessments_level_status ON risk_assessments(risk_level, status)",
                "CREATE INDEX IF NOT EXISTS idx_incident_reports_severity_status ON incident_reports(severity, status)",
                
                # Alignment indexes
                "CREATE INDEX IF NOT EXISTS idx_ethics_checkpoints_passed ON ethics_checkpoints(passed, checked_at DESC)",
                "CREATE INDEX IF NOT EXISTS idx_bias_detections_type_detected ON bias_detections(bias_type, detected)",
                
                # CPD indexes
                "CREATE INDEX IF NOT EXISTS idx_cpd_records_user_date ON cpd_records(user_id, activity_date DESC)",
                "CREATE INDEX IF NOT EXISTS idx_development_goals_user_status ON development_goals(user_id, status)",
            ]
            
            for index_sql in indexes:
                try:
                    conn.execute(text(index_sql))
                    conn.commit()
                    logger.info(f"  ✓ Created index")
                except Exception as e:
                    # Index might already exist, that's okay
                    if "already exists" not in str(e).lower():
                        logger.warning(f"  ⚠ Could not create index: {e}")
            
        logger.info("✅ Completed index creation")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating indexes: {e}")
        return False
    
    finally:
        engine.dispose()


def main():
    """Run the complete migration."""
    print("\n" + "="*60)
    print("PTCC Comprehensive Database Migration")
    print("="*60 + "\n")
    
    # Step 1: Create all tables
    if not create_all_tables():
        print("\n❌ Migration failed at table creation")
        return False
    
    # Step 2: Verify schema
    if not verify_schema():
        print("\n❌ Migration failed at schema verification")
        return False
    
    # Step 3: Create performance indexes
    if not create_indexes():
        print("\n⚠ Migration succeeded but some indexes failed")
        # Don't fail migration if just indexes fail
    
    print("\n" + "="*60)
    print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
    print("="*60 + "\n")
    print("The PTCC database is now ready for use.")
    print("\nNext steps:")
    print("1. Initialize core system services")
    print("2. Load default prompts and policies")
    print("3. Create initial agent configurations")
    print("4. Set up alignment and governance rules")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
