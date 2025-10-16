#!/usr/bin/env python3
"""
Database Migration Script for PTCC Enhancement

This script migrates the existing PTCC database to the enhanced schema,
adding all new tables for:
- Memory System
- Context Engineering
- Workflow & Generative Computing
- AI Safety & Governance
- Agent Management
- Personal Knowledge Management
- CPD System
- Prompt Management

The migration is non-destructive and preserves all existing data.
"""

import os
import sys
import shutil
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

# Import all model modules to register tables
from ptcc.backend.models import database_models  # Existing models
from ptcc.backend.models import memory_models
from ptcc.backend.models import context_models
from ptcc.backend.models import workflow_models
from ptcc.backend.models import safety_models
from ptcc.backend.models import agent_models
from ptcc.backend.models import pkm_models
from ptcc.backend.models import cpd_models
from ptcc.backend.models import prompt_models

from ptcc.backend.core.database import Base, engine, get_database_path
from ptcc.backend.core.config import get_settings
from ptcc.backend.core.logging_config import get_logger

logger = get_logger("migration")


class PTCCMigration:
    """Handles the migration to enhanced schema"""
    
    def __init__(self):
        self.settings = get_settings()
        self.database_path = get_database_path()
        self.engine = engine
        self.backup_path = None
        
    def run_migration(self):
        """Execute the complete migration"""
        try:
            logger.info("="*80)
            logger.info("PTCC DATABASE MIGRATION TO ENHANCED SCHEMA")
            logger.info("="*80)
            
            # Step 1: Pre-migration validation
            logger.info("\n[Step 1/7] Pre-migration validation...")
            self.validate_environment()
            
            # Step 2: Backup existing database
            logger.info("\n[Step 2/7] Creating backup of existing database...")
            self.backup_database()
            
            # Step 3: Get current schema info
            logger.info("\n[Step 3/7] Analyzing current database schema...")
            existing_tables = self.get_existing_tables()
            logger.info(f"Found {len(existing_tables)} existing tables")
            
            # Step 4: Create new tables
            logger.info("\n[Step 4/7] Creating new tables for enhanced schema...")
            self.create_new_tables()
            
            # Step 5: Initialize default data
            logger.info("\n[Step 5/7] Initializing default data...")
            self.initialize_default_data()
            
            # Step 6: Validate migration
            logger.info("\n[Step 6/7] Validating migration...")
            self.validate_migration(existing_tables)
            
            # Step 7: Generate migration report
            logger.info("\n[Step 7/7] Generating migration report...")
            self.generate_report()
            
            logger.info("\n" + "="*80)
            logger.info("✅ MIGRATION COMPLETED SUCCESSFULLY")
            logger.info("="*80)
            logger.info(f"\nBackup saved to: {self.backup_path}")
            logger.info(f"Database location: {self.database_path}")
            logger.info("\nNext steps:")
            logger.info("1. Review the migration report")
            logger.info("2. Test the enhanced system")
            logger.info("3. If issues occur, restore from backup")
            
            return True
            
        except Exception as e:
            logger.error(f"\n❌ MIGRATION FAILED: {e}", exc_info=True)
            logger.error(f"\nTo restore from backup:")
            logger.error(f"cp {self.backup_path} {self.database_path}")
            return False
    
    def validate_environment(self):
        """Validate the environment before migration"""
        # Check database exists
        if not os.path.exists(self.database_path):
            raise FileNotFoundError(f"Database not found: {self.database_path}")
        
        # Check database is not locked
        try:
            conn = self.engine.connect()
            conn.execute(text("SELECT 1"))
            conn.close()
            logger.info("✓ Database is accessible")
        except Exception as e:
            raise RuntimeError(f"Database is locked or inaccessible: {e}")
        
        # Check backup directory exists
        backup_dir = os.path.dirname(self.database_path) + "/backups"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            logger.info(f"✓ Created backup directory: {backup_dir}")
        else:
            logger.info(f"✓ Backup directory exists: {backup_dir}")
    
    def backup_database(self):
        """Create a backup of the current database"""
        backup_dir = os.path.dirname(self.database_path) + "/backups"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_path = os.path.join(
            backup_dir,
            f"school_pre_enhancement_{timestamp}.db"
        )
        
        # Create backup
        shutil.copy2(self.database_path, self.backup_path)
        
        # Verify backup
        if os.path.exists(self.backup_path):
            backup_size = os.path.getsize(self.backup_path)
            original_size = os.path.getsize(self.database_path)
            if backup_size == original_size:
                logger.info(f"✓ Backup created successfully ({backup_size:,} bytes)")
            else:
                raise RuntimeError("Backup file size doesn't match original")
        else:
            raise RuntimeError("Backup file was not created")
    
    def get_existing_tables(self):
        """Get list of existing tables"""
        inspector = inspect(self.engine)
        tables = inspector.get_table_names()
        logger.info(f"Existing tables: {', '.join(tables)}")
        return tables
    
    def create_new_tables(self):
        """Create all new tables from enhanced schema"""
        # Get list of all tables before creation
        inspector = inspect(self.engine)
        tables_before = set(inspector.get_table_names())
        
        # Create all tables
        Base.metadata.create_all(bind=self.engine)
        
        # Get list of tables after creation
        inspector = inspect(self.engine)
        tables_after = set(inspector.get_table_names())
        
        # Calculate new tables
        new_tables = tables_after - tables_before
        
        logger.info(f"✓ Created {len(new_tables)} new tables:")
        for table in sorted(new_tables):
            logger.info(f"  - {table}")
        
        return new_tables
    
    def initialize_default_data(self):
        """Initialize default data for new tables"""
        Session = sessionmaker(bind=self.engine)
        session = Session()
        
        try:
            # Create default user profile
            from ptcc.backend.models.memory_models import UserProfile
            
            # Check if default profile exists
            existing_profile = session.query(UserProfile).filter_by(user_id="default").first()
            
            if not existing_profile:
                default_profile = UserProfile(
                    user_id="default",
                    role="teacher",
                    instructional_style="Inquiry-based learning with differentiated instruction",
                    subject_expertise=["Computing", "ICT", "Digital Literacy"],
                    grade_levels=["7", "8", "9", "10", "11"],
                    subjects=["Computing", "ICT"],
                    teaching_philosophy="Technology-enhanced learning that empowers students to become creators, not just consumers of technology."
                )
                session.add(default_profile)
                session.commit()
                logger.info("✓ Created default user profile")
            else:
                logger.info("✓ Default user profile already exists")
            
            # Create base context layers
            from ptcc.backend.models.memory_models import ContextLayer
            
            user_profile = session.query(UserProfile).filter_by(user_id="default").first()
            
            context_layer_types = [
                ("base", "Base Context", "Static information about school, role, and subjects"),
                ("dynamic", "Dynamic Context", "Current activities and projects"),
                ("historical", "Historical Context", "Past teaching history and successful strategies"),
                ("situational", "Situational Context", "Real-time needs and priorities"),
                ("environmental", "Environmental Context", "Physical constraints and available resources"),
                ("philosophical", "Philosophical Context", "Educational values and teaching philosophy")
            ]
            
            for layer_type, layer_name, description in context_layer_types:
                existing_layer = session.query(ContextLayer).filter_by(
                    user_profile_id=user_profile.id,
                    layer_type=layer_type
                ).first()
                
                if not existing_layer:
                    context_layer = ContextLayer(
                        user_profile_id=user_profile.id,
                        layer_type=layer_type,
                        layer_name=layer_name,
                        layer_data={
                            "description": description,
                            "initialized": True,
                            "auto_populated": True
                        },
                        priority=5,
                        active=True
                    )
                    session.add(context_layer)
            
            session.commit()
            logger.info("✓ Created base context layers")
            
            # Register existing agents
            from ptcc.backend.models.agent_models import AgentRegistry
            
            agents = [
                {
                    "agent_id": "at_risk_identifier",
                    "agent_name": "At-Risk Student Identifier",
                    "agent_type": "educational",
                    "agent_category": "student_analysis",
                    "capabilities": ["risk_assessment", "behavior_analysis", "intervention_recommendation"],
                    "is_active": True
                },
                {
                    "agent_id": "behavior_manager",
                    "agent_name": "Classroom Behavior Manager",
                    "agent_type": "educational",
                    "agent_category": "classroom_management",
                    "capabilities": ["behavior_analysis", "seating_optimization", "intervention_strategies"],
                    "is_active": True
                },
                {
                    "agent_id": "learning_path_creator",
                    "agent_name": "Personalized Learning Path Creator",
                    "agent_type": "educational",
                    "agent_category": "curriculum",
                    "capabilities": ["gap_analysis", "learning_path_creation", "progress_monitoring"],
                    "is_active": True
                }
            ]
            
            for agent_data in agents:
                existing_agent = session.query(AgentRegistry).filter_by(
                    agent_id=agent_data["agent_id"]
                ).first()
                
                if not existing_agent:
                    agent = AgentRegistry(**agent_data)
                    session.add(agent)
            
            session.commit()
            logger.info("✓ Registered existing agents")
            
            # Create model factsheet for Gemini
            from ptcc.backend.models.safety_models import ModelFactsheet
            
            existing_factsheet = session.query(ModelFactsheet).filter_by(
                model_id="gemini-2.0-flash-exp"
            ).first()
            
            if not existing_factsheet:
                gemini_factsheet = ModelFactsheet(
                    model_id="gemini-2.0-flash-exp",
                    model_name="Gemini 2.0 Flash (Experimental)",
                    model_version="2.0",
                    model_provider="Google",
                    intended_use="Educational AI assistance and content generation",
                    capabilities=["text_generation", "analysis", "reasoning", "educational_content"],
                    limitations=["may_hallucinate", "requires_internet", "rate_limited"],
                    known_biases=["training_data_biases"],
                    mitigation_strategies=["prompt_engineering", "validation", "human_oversight"],
                    ethical_guidelines="Follow educational standards and maintain student privacy",
                    prohibited_uses=["grading_without_review", "replacing_human_judgment"],
                    best_practices="Always review AI-generated content for accuracy and appropriateness",
                    regulatory_compliance=["GDPR", "FERPA", "educational_standards"],
                    deprecated=False
                )
                session.add(gemini_factsheet)
                session.commit()
                logger.info("✓ Created Gemini model factsheet")
            else:
                logger.info("✓ Gemini model factsheet already exists")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error initializing default data: {e}")
            raise
        finally:
            session.close()
    
    def validate_migration(self, tables_before):
        """Validate that migration was successful"""
        inspector = inspect(self.engine)
        tables_after = inspector.get_table_names()
        
        # Check all existing tables still exist
        for table in tables_before:
            if table not in tables_after:
                raise RuntimeError(f"Existing table {table} is missing after migration!")
        
        logger.info(f"✓ All {len(tables_before)} existing tables preserved")
        
        # Check new tables were created
        expected_new_tables = [
            # Memory System
            "user_profiles", "context_layers", "interaction_history",
            "teaching_preferences", "student_demographics", "curriculum_context",
            # Context Engineering
            "context_metadata", "context_relevance_scores", "context_relationships",
            "context_validation_logs", "context_evolution_history", "context_usage_analytics",
            # Workflows
            "workflows", "workflow_templates", "ai_modules",
            "workflow_executions", "module_performance_metrics",
            # Safety & Governance
            "alignment_logs", "bias_detection_results", "governance_metrics",
            "risk_assessments", "transparency_logs", "model_factsheets", "compliance_tracking",
            # Agent Management
            "agent_registry", "agent_tasks", "agent_communication_logs",
            "agent_performance_metrics", "agent_coordination_sessions",
            # PKM
            "knowledge_items", "knowledge_connections", "knowledge_tags",
            "knowledge_syntheses", "knowledge_synthesis_items", "knowledge_insights",
            # CPD
            "cpd_records", "cpd_recommendations", "skill_assessments",
            "development_goals", "cpd_impact_evidence",
            # Prompts
            "prompt_library_items", "prompt_versions", "prompt_performance",
            "prompt_ab_tests", "prompt_optimization_runs", "prompt_usage_analytics"
        ]
        
        missing_tables = []
        for table in expected_new_tables:
            if table not in tables_after:
                missing_tables.append(table)
        
        if missing_tables:
            raise RuntimeError(f"Expected tables not created: {', '.join(missing_tables)}")
        
        logger.info(f"✓ All {len(expected_new_tables)} new tables created successfully")
        
        # Test basic database operations
        Session = sessionmaker(bind=self.engine)
        session = Session()
        
        try:
            # Test query on new table
            from ptcc.backend.models.memory_models import UserProfile
            profile_count = session.query(UserProfile).count()
            logger.info(f"✓ Can query new tables (found {profile_count} user profiles)")
            
            # Test query on existing table
            from ptcc.backend.models.database_models import Student
            student_count = session.query(Student).count()
            logger.info(f"✓ Can query existing tables (found {student_count} students)")
            
        finally:
            session.close()
    
    def generate_report(self):
        """Generate a migration report"""
        inspector = inspect(self.engine)
        tables = inspector.get_table_names()
        
        report = {
            "migration_date": datetime.now().isoformat(),
            "database_path": self.database_path,
            "backup_path": self.backup_path,
            "total_tables": len(tables),
            "tables_by_category": {
                "existing": 11,  # Original PTCC tables
                "memory_system": 6,
                "context_engineering": 6,
                "workflows": 5,
                "safety_governance": 7,
                "agent_management": 5,
                "pkm": 6,
                "cpd": 5,
                "prompts": 6
            }
        }
        
        # Save report
        report_dir = os.path.dirname(self.database_path) + "/backups"
        report_path = os.path.join(
            report_dir,
            f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        with open(report_path, 'w') as f:
            f.write("="*80 + "\n")
            f.write("PTCC DATABASE MIGRATION REPORT\n")
            f.write("="*80 + "\n\n")
            f.write(f"Migration Date: {report['migration_date']}\n")
            f.write(f"Database: {report['database_path']}\n")
            f.write(f"Backup: {report['backup_path']}\n\n")
            f.write(f"Total Tables: {report['total_tables']}\n\n")
            f.write("Tables by Category:\n")
            for category, count in report['tables_by_category'].items():
                f.write(f"  - {category}: {count} tables\n")
            f.write("\n" + "="*80 + "\n")
            f.write("All Tables:\n")
            f.write("="*80 + "\n")
            for table in sorted(tables):
                f.write(f"  - {table}\n")
        
        logger.info(f"✓ Migration report saved to: {report_path}")


def main():
    """Main migration execution"""
    print("\n" + "="*80)
    print("PTCC DATABASE MIGRATION TO ENHANCED SCHEMA")
    print("="*80 + "\n")
    
    print("This will:")
    print("  1. Create a backup of your existing database")
    print("  2. Add 48 new tables for enhanced features")
    print("  3. Initialize default data")
    print("  4. Preserve all existing data")
    print("\n" + "="*80 + "\n")
    
    response = input("Do you want to proceed? (yes/no): ")
    
    if response.lower() != "yes":
        print("\nMigration cancelled.")
        return
    
    print("\nStarting migration...\n")
    
    migration = PTCCMigration()
    success = migration.run_migration()
    
    if success:
        print("\n✅ Migration completed successfully!")
        return 0
    else:
        print("\n❌ Migration failed. Check logs above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
