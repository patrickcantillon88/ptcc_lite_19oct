"""
Governance and Risk Management System for PTCC

Implements policy enforcement, compliance tracking, audit trails,
and risk assessment for AI-powered education systems.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy import desc

from .database import SessionLocal
from .logging_config import get_logger
from ..models.governance_models import (
    PolicyFramework,
    ComplianceCheck,
    AuditLog,
    RiskAssessment,
    IncidentReport
)

logger = get_logger("governance_system")


class RiskLevel(Enum):
    """Risk severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


class ComplianceStatus(Enum):
    """Compliance check statuses."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIAL_COMPLIANCE = "partial_compliance"
    NEEDS_REVIEW = "needs_review"
    EXEMPT = "exempt"


class PolicyManager:
    """Manages policies and ensures compliance."""
    
    def __init__(self):
        self.logger = logger
    
    def create_policy(
        self,
        policy_name: str,
        policy_category: str,
        policy_content: Dict[str, Any],
        scope: str,
        enforcement_level: str = "mandatory",
        db: Optional[Session] = None
    ) -> PolicyFramework:
        """Create a new policy framework."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            policy = PolicyFramework(
                policy_name=policy_name,
                policy_category=policy_category,
                policy_content=policy_content,
                scope=scope,
                enforcement_level=enforcement_level,
                active=True
            )
            
            db.add(policy)
            db.commit()
            db.refresh(policy)
            
            self.logger.info(f"Created policy: {policy_name}")
            return policy
            
        finally:
            if should_close:
                db.close()
    
    def get_active_policies(
        self,
        category: Optional[str] = None,
        scope: Optional[str] = None,
        db: Optional[Session] = None
    ) -> List[PolicyFramework]:
        """Get all active policies."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            query = db.query(PolicyFramework).filter_by(active=True)
            
            if category:
                query = query.filter_by(policy_category=category)
            
            if scope:
                query = query.filter_by(scope=scope)
            
            return query.all()
            
        finally:
            if should_close:
                db.close()
    
    def update_policy(
        self,
        policy_id: int,
        updates: Dict[str, Any],
        db: Optional[Session] = None
    ) -> Optional[PolicyFramework]:
        """Update an existing policy."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            policy = db.query(PolicyFramework).filter_by(id=policy_id).first()
            
            if not policy:
                return None
            
            for key, value in updates.items():
                if hasattr(policy, key):
                    setattr(policy, key, value)
            
            policy.last_updated = datetime.utcnow()
            db.commit()
            db.refresh(policy)
            
            return policy
            
        finally:
            if should_close:
                db.close()


class ComplianceChecker:
    """Checks compliance with policies and regulations."""
    
    def __init__(self):
        self.policy_manager = PolicyManager()
        self.logger = logger
    
    def check_compliance(
        self,
        entity_type: str,
        entity_id: str,
        policies_to_check: Optional[List[int]] = None,
        context: Optional[Dict[str, Any]] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Perform compliance check."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            # Get policies to check
            if policies_to_check:
                policies = [
                    db.query(PolicyFramework).filter_by(id=pid).first()
                    for pid in policies_to_check
                ]
                policies = [p for p in policies if p]
            else:
                policies = self.policy_manager.get_active_policies(db=db)
            
            compliance_results = []
            overall_compliant = True
            
            for policy in policies:
                result = self._check_policy_compliance(
                    entity_type,
                    entity_id,
                    policy,
                    context or {}
                )
                
                compliance_results.append(result)
                
                # Store compliance check
                check = ComplianceCheck(
                    policy_id=policy.id,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    compliance_status=result["status"],
                    check_details=result,
                    context_metadata=context or {}
                )
                db.add(check)
                
                if result["status"] != ComplianceStatus.COMPLIANT.value:
                    overall_compliant = False
            
            db.commit()
            
            return {
                "overall_compliant": overall_compliant,
                "checks_performed": len(compliance_results),
                "results": compliance_results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        finally:
            if should_close:
                db.close()
    
    def _check_policy_compliance(
        self,
        entity_type: str,
        entity_id: str,
        policy: PolicyFramework,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check compliance with a specific policy."""
        # Simplified compliance checking logic
        # In production, this would be much more sophisticated
        
        policy_requirements = policy.policy_content.get("requirements", [])
        
        violations = []
        compliant_items = []
        
        for requirement in policy_requirements:
            # Check each requirement
            req_met = self._check_requirement(requirement, context)
            
            if req_met:
                compliant_items.append(requirement)
            else:
                violations.append(requirement)
        
        if not violations:
            status = ComplianceStatus.COMPLIANT.value
        elif len(violations) == len(policy_requirements):
            status = ComplianceStatus.NON_COMPLIANT.value
        else:
            status = ComplianceStatus.PARTIAL_COMPLIANCE.value
        
        return {
            "policy_id": policy.id,
            "policy_name": policy.policy_name,
            "status": status,
            "compliant_items": compliant_items,
            "violations": violations,
            "enforcement_level": policy.enforcement_level
        }
    
    def _check_requirement(
        self,
        requirement: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """Check if a specific requirement is met."""
        # Simplified requirement checking
        # In production, this would use sophisticated rule engines
        
        req_type = requirement.get("type", "")
        req_value = requirement.get("value", "")
        
        # Placeholder logic
        if req_type == "data_retention":
            # Check data retention policies
            return True
        elif req_type == "access_control":
            # Check access control measures
            return True
        elif req_type == "audit_trail":
            # Check audit trail requirements
            return True
        
        return True


class AuditLogger:
    """Logs all system activities for audit purposes."""
    
    def __init__(self):
        self.logger = logger
    
    def log_activity(
        self,
        action_type: str,
        actor_id: str,
        actor_type: str,
        target_entity: str,
        target_id: str,
        action_details: Dict[str, Any],
        result: str = "success",
        db: Optional[Session] = None
    ) -> AuditLog:
        """Log an auditable activity."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            audit_entry = AuditLog(
                action_type=action_type,
                actor_id=actor_id,
                actor_type=actor_type,
                target_entity=target_entity,
                target_id=target_id,
                action_details=action_details,
                result=result
            )
            
            db.add(audit_entry)
            db.commit()
            db.refresh(audit_entry)
            
            return audit_entry
            
        finally:
            if should_close:
                db.close()
    
    def get_audit_trail(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        actor_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        db: Optional[Session] = None
    ) -> List[AuditLog]:
        """Retrieve audit trail."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            query = db.query(AuditLog)
            
            if entity_type:
                query = query.filter_by(target_entity=entity_type)
            
            if entity_id:
                query = query.filter_by(target_id=entity_id)
            
            if actor_id:
                query = query.filter_by(actor_id=actor_id)
            
            if start_date:
                query = query.filter(AuditLog.timestamp >= start_date)
            
            if end_date:
                query = query.filter(AuditLog.timestamp <= end_date)
            
            return query.order_by(desc(AuditLog.timestamp)).limit(limit).all()
            
        finally:
            if should_close:
                db.close()


class RiskAssessor:
    """Assesses and manages risks."""
    
    def __init__(self):
        self.logger = logger
    
    def assess_risk(
        self,
        risk_category: str,
        risk_source: str,
        assessment_context: Dict[str, Any],
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Perform risk assessment."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            # Perform risk analysis
            analysis = self._analyze_risk(
                risk_category,
                risk_source,
                assessment_context
            )
            
            # Store risk assessment
            assessment = RiskAssessment(
                risk_category=risk_category,
                risk_source=risk_source,
                risk_level=analysis["level"],
                likelihood_score=analysis["likelihood"],
                impact_score=analysis["impact"],
                risk_factors=analysis["factors"],
                mitigation_strategies=analysis["mitigations"],
                assessment_context=assessment_context
            )
            
            db.add(assessment)
            db.commit()
            db.refresh(assessment)
            
            return {
                "assessment_id": assessment.id,
                "risk_level": analysis["level"],
                "likelihood": analysis["likelihood"],
                "impact": analysis["impact"],
                "factors": analysis["factors"],
                "mitigations": analysis["mitigations"],
                "requires_action": analysis["level"] in [
                    RiskLevel.CRITICAL.value,
                    RiskLevel.HIGH.value
                ]
            }
            
        finally:
            if should_close:
                db.close()
    
    def _analyze_risk(
        self,
        risk_category: str,
        risk_source: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze risk to determine level and mitigation strategies."""
        # Simplified risk analysis - in production, use sophisticated models
        
        # Default values
        likelihood = 0.3  # 0-1 scale
        impact = 0.4      # 0-1 scale
        factors = []
        mitigations = []
        
        # Analyze based on category
        if risk_category == "data_privacy":
            likelihood = 0.5
            impact = 0.8
            factors = [
                "Handling of student data",
                "Potential PII exposure",
                "Data retention concerns"
            ]
            mitigations = [
                "Implement data encryption",
                "Regular privacy audits",
                "Staff training on data handling"
            ]
        elif risk_category == "ai_bias":
            likelihood = 0.4
            impact = 0.7
            factors = [
                "Training data quality",
                "Algorithm fairness",
                "Diverse representation"
            ]
            mitigations = [
                "Regular bias testing",
                "Diverse training data",
                "Human oversight"
            ]
        elif risk_category == "system_failure":
            likelihood = 0.2
            impact = 0.6
            factors = [
                "System dependencies",
                "Infrastructure stability",
                "Backup systems"
            ]
            mitigations = [
                "Redundant systems",
                "Regular backups",
                "Disaster recovery plan"
            ]
        
        # Calculate composite risk level
        risk_score = likelihood * impact
        
        if risk_score >= 0.7:
            level = RiskLevel.CRITICAL.value
        elif risk_score >= 0.5:
            level = RiskLevel.HIGH.value
        elif risk_score >= 0.3:
            level = RiskLevel.MEDIUM.value
        elif risk_score >= 0.1:
            level = RiskLevel.LOW.value
        else:
            level = RiskLevel.MINIMAL.value
        
        return {
            "level": level,
            "likelihood": likelihood,
            "impact": impact,
            "risk_score": risk_score,
            "factors": factors,
            "mitigations": mitigations
        }
    
    def get_active_risks(
        self,
        risk_level: Optional[str] = None,
        category: Optional[str] = None,
        days: int = 30,
        db: Optional[Session] = None
    ) -> List[RiskAssessment]:
        """Get recent risk assessments."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            query = db.query(RiskAssessment).filter(
                RiskAssessment.assessment_date >= cutoff_date
            )
            
            if risk_level:
                query = query.filter_by(risk_level=risk_level)
            
            if category:
                query = query.filter_by(risk_category=category)
            
            return query.order_by(desc(RiskAssessment.assessment_date)).all()
            
        finally:
            if should_close:
                db.close()


class IncidentManager:
    """Manages incidents and responses."""
    
    def __init__(self):
        self.logger = logger
    
    def report_incident(
        self,
        incident_type: str,
        severity: str,
        description: str,
        affected_entities: List[Dict[str, str]],
        incident_context: Dict[str, Any],
        db: Optional[Session] = None
    ) -> IncidentReport:
        """Report a new incident."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            incident = IncidentReport(
                incident_type=incident_type,
                severity=severity,
                description=description,
                affected_entities=affected_entities,
                incident_context=incident_context,
                status="reported"
            )
            
            db.add(incident)
            db.commit()
            db.refresh(incident)
            
            self.logger.warning(
                f"Incident reported: {incident_type} - Severity: {severity}"
            )
            
            # If critical, trigger immediate response
            if severity == RiskLevel.CRITICAL.value:
                self._trigger_incident_response(incident, db)
            
            return incident
            
        finally:
            if should_close:
                db.close()
    
    def _trigger_incident_response(
        self,
        incident: IncidentReport,
        db: Session
    ):
        """Trigger immediate incident response."""
        # In production, this would trigger alerts, notifications, etc.
        self.logger.critical(
            f"CRITICAL INCIDENT: {incident.incident_type} - {incident.description}"
        )
        
        # Update incident status
        incident.status = "responding"
        db.commit()
    
    def update_incident(
        self,
        incident_id: int,
        status: Optional[str] = None,
        resolution: Optional[str] = None,
        action_taken: Optional[str] = None,
        db: Optional[Session] = None
    ) -> Optional[IncidentReport]:
        """Update incident status and resolution."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            incident = db.query(IncidentReport).filter_by(id=incident_id).first()
            
            if not incident:
                return None
            
            if status:
                incident.status = status
            
            if resolution:
                incident.resolution = resolution
            
            if action_taken:
                incident.action_taken = action_taken
            
            if status == "resolved":
                incident.resolved_at = datetime.utcnow()
            
            db.commit()
            db.refresh(incident)
            
            return incident
            
        finally:
            if should_close:
                db.close()
    
    def get_open_incidents(
        self,
        severity: Optional[str] = None,
        db: Optional[Session] = None
    ) -> List[IncidentReport]:
        """Get all open incidents."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            query = db.query(IncidentReport).filter(
                IncidentReport.status.in_(["reported", "responding", "investigating"])
            )
            
            if severity:
                query = query.filter_by(severity=severity)
            
            return query.order_by(desc(IncidentReport.reported_at)).all()
            
        finally:
            if should_close:
                db.close()


class GovernanceOrchestrator:
    """Orchestrates all governance and risk management functions."""
    
    def __init__(self):
        self.policy_manager = PolicyManager()
        self.compliance_checker = ComplianceChecker()
        self.audit_logger = AuditLogger()
        self.risk_assessor = RiskAssessor()
        self.incident_manager = IncidentManager()
        self.logger = logger
    
    def comprehensive_governance_check(
        self,
        entity_type: str,
        entity_id: str,
        action: str,
        actor_id: str,
        context: Dict[str, Any],
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Perform comprehensive governance check before action."""
        
        # Log the attempted action
        self.audit_logger.log_activity(
            action_type=action,
            actor_id=actor_id,
            actor_type="user",
            target_entity=entity_type,
            target_id=entity_id,
            action_details=context,
            result="pending",
            db=db
        )
        
        # Check compliance
        compliance_result = self.compliance_checker.check_compliance(
            entity_type=entity_type,
            entity_id=entity_id,
            context=context,
            db=db
        )
        
        # Assess risks
        risk_assessment = self.risk_assessor.assess_risk(
            risk_category=context.get("risk_category", "general"),
            risk_source=f"{entity_type}:{entity_id}",
            assessment_context=context,
            db=db
        )
        
        # Determine if action should be allowed
        allow_action = (
            compliance_result["overall_compliant"]
            and risk_assessment["risk_level"] not in [
                RiskLevel.CRITICAL.value
            ]
        )
        
        # If high risk and not compliant, create incident report
        if not allow_action:
            self.incident_manager.report_incident(
                incident_type="governance_violation",
                severity=risk_assessment["risk_level"],
                description=f"Action '{action}' blocked due to compliance/risk issues",
                affected_entities=[{
                    "type": entity_type,
                    "id": entity_id
                }],
                incident_context={
                    "action": action,
                    "actor": actor_id,
                    "compliance": compliance_result,
                    "risk": risk_assessment
                },
                db=db
            )
        
        return {
            "allowed": allow_action,
            "compliance": compliance_result,
            "risk_assessment": risk_assessment,
            "timestamp": datetime.utcnow().isoformat(),
            "requires_review": not allow_action
        }


# Convenience functions
def check_governance(
    entity_type: str,
    entity_id: str,
    action: str,
    actor_id: str,
    context: Dict[str, Any],
    db: Optional[Session] = None
) -> Dict[str, Any]:
    """Convenience function for governance check."""
    orchestrator = GovernanceOrchestrator()
    return orchestrator.comprehensive_governance_check(
        entity_type, entity_id, action, actor_id, context, db
    )
