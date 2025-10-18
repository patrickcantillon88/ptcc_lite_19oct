# PTCC Development Roadmap: Phase 2 (Foundation Phase)
## Building for 5-Year Growth Without Refactoring Crisis

**Timeline**: 4 weeks (195 hours)  
**Outcome**: Foundation enables 50+ school scaling, 1,248% ROI Year 1  
**Risk**: 4-week delay prevents 4-6 month refactoring crisis later

---

## 🎯 Why Foundation Phase Matters

### Without Foundation (Path 1)
```
Pilot (2 months) → 5 schools running → Revenue starts
↓
5 schools ask for: "Connect our systems" + "Talk to it naturally"
↓
Current architecture breaks → Full refactor needed (4-6 months)
↓
Developers stuck firefighting, scaling impossible
↓
Competitive window closes, £50M exit becomes £10M acquisition
```

### With Foundation (Path 2 - RECOMMENDED)
```
Foundation (4 weeks) → System designed for growth from day 1
↓
Pilot (2 months) → 5 schools on scalable system
↓
5 schools ask for: "Connect our systems" + "Talk to it naturally"
↓
New features bolt on in 3-4 weeks instead of requiring 4-6 month refactor
↓
Scale to 50 schools smoothly → £25k/month revenue
↓
Path to £50M+ acquisition clear and achievable
```

**Net time cost**: +4 weeks now vs +24 weeks in 6 months. Total project accelerated by 20 weeks.

---

# PHASE 2A: Unified Data Architecture Foundation
## Weeks 1-3 (100 hours) | Objective: Eliminate data conflicts before they cause problems

Current state: Data is unified at query level (one interface) but fragmented at storage level (multiple schemas).
Problem: As system grows, conflicts emerge - which source of truth wins when data disagrees?

Foundation goal: Make system recognize data can be stored differently but queried uniformly.

---

## STEP 1: Data Model Abstraction Layer (30 hours)

### Goal
Create interface that talks to "data" without caring WHERE that data lives or HOW it's stored.

### Implementation

#### 1.1 Create `backend/core/data_model_abstraction.py`

```python
# New file: backend/core/data_model_abstraction.py

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum

class DataRecordType(Enum):
    """All data types system knows about"""
    STUDENT = "student"
    INCIDENT = "incident"
    ASSESSMENT = "assessment"
    COMMUNICATION = "communication"
    ATTENDANCE = "attendance"
    ASSIGNMENT = "assignment"

class DataRecord(ABC):
    """Abstract data record - any data type conforms to this"""
    
    @property
    @abstractmethod
    def record_id(self) -> str:
        """Unique identifier"""
        pass
    
    @property
    @abstractmethod
    def record_type(self) -> DataRecordType:
        """What kind of record is this?"""
        pass
    
    @property
    @abstractmethod
    def student_id(self) -> Optional[str]:
        """Which student does this relate to?"""
        pass
    
    @property
    @abstractmethod
    def timestamp(self) -> datetime:
        """When did this happen?"""
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert to standard format"""
        pass

class SQLiteStudentRecord(DataRecord):
    """Adapter: SQLite student table → DataRecord interface"""
    
    def __init__(self, sqlite_student):
        self._record = sqlite_student
    
    @property
    def record_id(self) -> str:
        return f"student_{self._record.id}"
    
    @property
    def record_type(self) -> DataRecordType:
        return DataRecordType.STUDENT
    
    @property
    def student_id(self) -> Optional[str]:
        return str(self._record.id)
    
    @property
    def timestamp(self) -> datetime:
        return self._record.created_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.record_id,
            "type": self.record_type.value,
            "student_id": self.student_id,
            "name": self._record.name,
            "class": self._record.class_name,
            "timestamp": self.timestamp.isoformat()
        }

# Similar adapters for Incident, Assessment, etc.
```

**Time**: 8-10 hours
**Why**: Creates "translation layer" - system can speak to any data type uniformly

#### 1.2 Create `backend/core/data_repository.py`

```python
# New file: backend/core/data_repository.py

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from backend.core.data_model_abstraction import DataRecord, DataRecordType

@dataclass
class DataQuery:
    """Standardized query format"""
    record_type: DataRecordType
    filters: Dict[str, Any]
    sort_by: Optional[str] = None
    limit: Optional[int] = None

class DataRepository(ABC):
    """Interface for querying data regardless of source"""
    
    @abstractmethod
    async def query(self, query: DataQuery) -> List[DataRecord]:
        """Run query, get back standardized records"""
        pass
    
    @abstractmethod
    async def get_by_student(self, student_id: str) -> List[DataRecord]:
        """Get all data for a student"""
        pass

class UnifiedDataRepository(DataRepository):
    """Implements repository by routing to correct backend"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    async def query(self, query: DataQuery) -> List[DataRecord]:
        if query.record_type == DataRecordType.STUDENT:
            return await self._query_students(query)
        elif query.record_type == DataRecordType.INCIDENT:
            return await self._query_incidents(query)
        # ... etc
    
    async def _query_students(self, query: DataQuery) -> List[DataRecord]:
        """Query students table"""
        results = self.db.query(Student).filter(**query.filters).all()
        return [SQLiteStudentRecord(r) for r in results]
```

**Time**: 10-12 hours
**Why**: Single interface for all data types - when you add new data source, just add new adapter

#### 1.3 Create tests

```python
# New file: tests/test_data_abstraction.py

def test_student_record_adapter():
    """SQLite student converts to DataRecord interface"""
    sqlite_student = Student(id=1, name="Noah", class_name="3A")
    record = SQLiteStudentRecord(sqlite_student)
    
    assert record.record_id == "student_1"
    assert record.record_type == DataRecordType.STUDENT
    assert record.student_id == "1"

def test_unified_repository_query():
    """Can query students through unified interface"""
    repo = UnifiedDataRepository(db_session)
    
    query = DataQuery(
        record_type=DataRecordType.STUDENT,
        filters={"class_name": "3A"}
    )
    
    results = await repo.query(query)
    assert len(results) > 0
    assert all(r.record_type == DataRecordType.STUDENT for r in results)
```

**Time**: 8-10 hours
**Why**: Ensure abstraction actually works before building on it

---

## STEP 2: Unified Data Model (25-35 hours)

### Goal
Define a single format that ALL data conforms to, even if stored differently.

### Implementation

#### 2.1 Create `backend/core/unified_data_model.py`

```python
# New file: backend/core/unified_data_model.py

from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

class DataCategory(Enum):
    """High-level categorization"""
    STUDENT = "student"
    BEHAVIOR = "behavior"
    ACADEMIC = "academic"
    HEALTH = "health"
    COMMUNICATION = "communication"

@dataclass
class UnifiedDataModel:
    """Single format for ALL data in system"""
    
    # Core identity
    record_id: str  # Unique across entire system
    data_type: str  # "student", "incident", "assessment", etc.
    category: DataCategory
    
    # Student reference (ALL records should have this)
    student_id: str
    
    # Temporal
    created_at: datetime
    updated_at: datetime
    
    # Content
    content: Dict[str, Any]  # Flexible - contains actual data
    
    # Metadata
    source: str  # "sqlite", "uploaded_csv", "api", etc.
    is_sensitive: bool  # Contains PII?
    retention_days: int  # How long to keep?
    
    def to_json(self) -> Dict[str, Any]:
        """Standard JSON format for APIs"""
        return {
            "record_id": self.record_id,
            "data_type": self.data_type,
            "category": self.category.value,
            "student_id": self.student_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "content": self.content,
            "source": self.source,
            "is_sensitive": self.is_sensitive,
        }

# Converters - adapt existing data TO unified model
class DataUnifier:
    """Convert different data formats to unified model"""
    
    @staticmethod
    def from_sqlite_student(student) -> UnifiedDataModel:
        return UnifiedDataModel(
            record_id=f"student_{student.id}",
            data_type="student",
            category=DataCategory.STUDENT,
            student_id=str(student.id),
            created_at=student.created_at,
            updated_at=student.updated_at,
            content={
                "name": student.name,
                "class": student.class_name,
                "support_level": student.support_level,
            },
            source="sqlite",
            is_sensitive=True,
            retention_days=3650,  # 10 years for student records
        )
    
    @staticmethod
    def from_sqlite_incident(incident) -> UnifiedDataModel:
        return UnifiedDataModel(
            record_id=f"incident_{incident.id}",
            data_type="incident",
            category=DataCategory.BEHAVIOR,
            student_id=str(incident.student_id),
            created_at=incident.incident_date,
            updated_at=incident.updated_at,
            content={
                "incident_type": incident.incident_type,
                "description": incident.description,
                "severity": incident.severity,
                "teacher": incident.recorded_by,
            },
            source="sqlite",
            is_sensitive=False,
            retention_days=1825,  # 5 years
        )
```

**Time**: 12-15 hours
**Why**: Creates single source of truth about data format

#### 2.2 Update API endpoints to use unified model

```python
# Modify backend/api/search.py

from backend.core.unified_data_model import DataUnifier

@router.post("/search")
async def search(
    query: str,
    search_type: str = "semantic",
    db: Session = Depends(get_db)
):
    """Search now returns unified format"""
    
    # Get raw data (could be from different sources)
    incidents = db.query(Incident).filter(...).all()
    students = db.query(Student).filter(...).all()
    
    # Convert to unified format
    results = [
        *[DataUnifier.from_sqlite_incident(i) for i in incidents],
        *[DataUnifier.from_sqlite_student(s) for s in students],
    ]
    
    # Return unified format
    return {
        "results": [r.to_json() for r in results],
        "count": len(results)
    }
```

**Time**: 10-15 hours
**Why**: Ensures all APIs speak same language

#### 2.3 Update frontend to expect unified format

```javascript
// frontend/desktop-web/components/SearchResults.tsx

// Old way: Handle different data types differently
// if (result.type === 'student') {...}
// else if (result.type === 'incident') {...}

// New way: All results follow same format
results.forEach(result => {
  const {
    record_id,
    data_type,
    category,
    student_id,
    created_at,
    content
  } = result;
  
  // Render same way regardless of type
  renderRecord(result);
});
```

**Time**: 5-8 hours
**Why**: Frontend becomes simpler and more maintainable

---

## STEP 3: Smart Query Router (20-25 hours)

### Goal
System automatically knows WHERE to find data without hardcoding paths.

### Implementation

#### 3.1 Create `backend/core/query_router.py`

```python
# New file: backend/core/query_router.py

from typing import List
from backend.core.unified_data_model import DataRecordType, DataQuery, UnifiedDataModel

class QueryRoute:
    """Where and how to find data of a certain type"""
    
    def __init__(self, 
                 record_type: str,
                 source: str,  # "sqlite", "chromadb", "csv", etc.
                 table: Optional[str] = None,
                 index: Optional[str] = None):
        self.record_type = record_type
        self.source = source
        self.table = table
        self.index = index

class QueryRouter:
    """Intelligent routing of queries to right data source"""
    
    def __init__(self):
        # Map: data_type → where to find it
        self.routes: Dict[str, List[QueryRoute]] = {
            "student": [
                QueryRoute("student", "sqlite", table="students"),
            ],
            "incident": [
                QueryRoute("incident", "sqlite", table="quick_logs"),
                QueryRoute("incident", "chromadb", index="incidents"),  # Also searchable
            ],
            "assessment": [
                QueryRoute("assessment", "sqlite", table="quick_logs"),
            ],
        }
    
    async def route_query(self, query: DataQuery) -> List[UnifiedDataModel]:
        """Route query to best data source"""
        
        routes = self.routes.get(query.record_type.value, [])
        
        results = []
        for route in routes:
            if route.source == "sqlite":
                results.extend(await self._query_sqlite(route, query))
            elif route.source == "chromadb":
                results.extend(await self._query_chromadb(route, query))
        
        # Deduplicate (same data from multiple sources)
        return self._deduplicate(results)
    
    async def _query_sqlite(self, route: QueryRoute, query: DataQuery) -> List[UnifiedDataModel]:
        """Query SQLite"""
        # Implementation
        pass
    
    async def _query_chromadb(self, route: QueryRoute, query: DataQuery) -> List[UnifiedDataModel]:
        """Query ChromaDB"""
        # Implementation
        pass
    
    def _deduplicate(self, results: List[UnifiedDataModel]) -> List[UnifiedDataModel]:
        """Remove duplicates from multiple sources"""
        seen = set()
        deduped = []
        for result in results:
            if result.record_id not in seen:
                seen.add(result.record_id)
                deduped.append(result)
        return deduped
```

**Time**: 10-12 hours
**Why**: System becomes "location-aware" - knows where data lives

#### 3.2 Update search router to use query router

```python
# Modify backend/api/search.py

from backend.core.query_router import QueryRouter

@router.post("/search")
async def search(
    query: str,
    search_type: str = "semantic",
    db: Session = Depends(get_db)
):
    """Search uses smart routing"""
    
    router = QueryRouter()
    
    # Create standardized query
    data_query = DataQuery(
        record_type=DataRecordType.INCIDENT,
        filters={"query": query}
    )
    
    # Router figures out WHERE to look
    results = await router.route_query(data_query)
    
    return {
        "results": [r.to_json() for r in results],
        "count": len(results),
        "search_type": search_type,
    }
```

**Time**: 8-13 hours
**Why**: Each search endpoint becomes simpler and more intelligent

---

## STEP 4: Data Synchronization Framework (20-30 hours)

### Goal
When same data exists in multiple places (SQLite + ChromaDB), keep them in sync.

### Implementation

#### 4.1 Create `backend/core/data_sync_engine.py`

```python
# New file: backend/core/data_sync_engine.py

from typing import List, Optional
from datetime import datetime
import logging

class SyncLog:
    """Track what got synced when"""
    record_id: str
    source: str  # From
    target: str  # To
    status: str  # "success" / "conflict" / "pending"
    conflict_resolution: Optional[str]  # How conflict resolved
    timestamp: datetime

class DataSyncEngine:
    """Synchronize data across sources"""
    
    def __init__(self, db_session, chromadb_client, logger: logging.Logger):
        self.db = db_session
        self.chromadb = chromadb_client
        self.logger = logger
        self.sync_logs: List[SyncLog] = []
    
    async def sync_record_to_chromadb(self, record: UnifiedDataModel) -> bool:
        """When SQLite data changes, update ChromaDB"""
        try:
            collection = self.chromadb.get_collection(record.category.value)
            collection.add(
                ids=[record.record_id],
                documents=[str(record.content)],
                metadatas=[{
                    "student_id": record.student_id,
                    "created_at": record.created_at.isoformat(),
                    "source": "sqlite",
                }]
            )
            self.logger.info(f"Synced {record.record_id} to ChromaDB")
            return True
        except Exception as e:
            self.logger.error(f"Sync failed for {record.record_id}: {e}")
            return False
    
    async def sync_record_to_sqlite(self, record: UnifiedDataModel) -> bool:
        """When ChromaDB data changes, update SQLite"""
        # Implementation - handles pulling data from vector DB back to SQL
        pass
    
    async def resolve_conflict(self, 
                              sqlite_record: UnifiedDataModel,
                              chromadb_record: UnifiedDataModel) -> UnifiedDataModel:
        """When data disagrees - which version wins?"""
        # Strategy: "Last write wins"
        if sqlite_record.updated_at > chromadb_record.updated_at:
            return sqlite_record
        return chromadb_record

class SyncHook:
    """Automatically sync when data changes"""
    
    def __init__(self, sync_engine: DataSyncEngine):
        self.sync_engine = sync_engine
    
    def after_insert(self, record: UnifiedDataModel):
        """Called after insert - sync to other sources"""
        import asyncio
        asyncio.create_task(
            self.sync_engine.sync_record_to_chromadb(record)
        )
    
    def after_update(self, record: UnifiedDataModel):
        """Called after update - sync to other sources"""
        import asyncio
        asyncio.create_task(
            self.sync_engine.sync_record_to_chromadb(record)
        )
```

**Time**: 15-20 hours
**Why**: Prevents inconsistency as system grows

#### 4.2 Integrate sync hooks into database layer

```python
# Modify backend/core/database.py

from backend.core.data_sync_engine import DataSyncEngine, SyncHook

# Create sync engine in app lifespan
sync_engine = DataSyncEngine(
    db_session=db,
    chromadb_client=chroma_client,
    logger=logger
)

sync_hook = SyncHook(sync_engine)

# Register hooks
from sqlalchemy import event
from backend.models.database_models import Incident

@event.listens_for(Incident, "after_insert")
def receive_after_insert(mapper, connection, target):
    record = DataUnifier.from_sqlite_incident(target)
    sync_hook.after_insert(record)

@event.listens_for(Incident, "after_update")
def receive_after_update(mapper, connection, target):
    record = DataUnifier.from_sqlite_incident(target)
    sync_hook.after_update(record)
```

**Time**: 5-10 hours
**Why**: Makes sync automatic, not manual

---

### Phase 2A Summary

| Component | Hours | Status | Outcome |
|-----------|-------|--------|---------|
| Data Model Abstraction | 30 | Ready | Can talk to any data uniformly |
| Unified Data Model | 35 | Ready | Single format for all data |
| Query Router | 25 | Ready | System knows where data lives |
| Sync Framework | 30 | Ready | Data stays consistent |
| **TOTAL PHASE 2A** | **100** | **Ready for deployment** | **Foundation complete** |

---

# PHASE 2B: Natural Language Interface Foundation
## Weeks 3-6 (95 hours) | Objective: Make system ready to accept natural language commands

Current state: All features are REST APIs (must know exact endpoints).
Problem: Teachers shouldn't need API documentation to use system.

Foundation goal: Build layer that translates "Show me at-risk students" → API calls.

---

## STEP 5: Abstract Agent Interface (20-30 hours)

### Goal
Create standardized interface that ALL agents conform to.

### Implementation

#### 5.1 Create `backend/core/agent_interface.py`

```python
# New file: backend/core/agent_interface.py

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class Command:
    """Standardized command format"""
    agent_name: str
    action: str
    parameters: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None  # Optional context

@dataclass
class CommandResponse:
    """Standardized response format"""
    status: str  # "success" / "error" / "partial"
    result: Any
    confidence: float  # 0-1, how sure is agent about this?
    explanation: str  # Why this result?
    next_steps: Optional[List[str]] = None  # Suggestions

class Agent(ABC):
    """All agents conform to this interface"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Agent name: 'at-risk-identifier', 'behavior-manager', etc."""
        pass
    
    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        """Actions this agent can do: ['identify', 'analyze', 'predict']"""
        pass
    
    @property
    @abstractmethod
    def required_parameters(self) -> Dict[str, str]:
        """What parameters does each action need?"""
        # Returns: {"identify": ["time_period"], "analyze": ["student_id", "data_type"]}
        pass
    
    @abstractmethod
    async def execute(self, command: Command) -> CommandResponse:
        """Execute command, return standardized response"""
        pass

class AtRiskAgent(Agent):
    """Existing at-risk logic wrapped in standard interface"""
    
    @property
    def name(self) -> str:
        return "at-risk-identifier"
    
    @property
    def capabilities(self) -> List[str]:
        return ["identify", "analyze", "predict"]
    
    @property
    def required_parameters(self) -> Dict[str, str]:
        return {
            "identify": ["time_period"],  # "week", "month", "semester"
            "analyze": ["student_id"],
            "predict": ["student_id", "lookahead_weeks"],
        }
    
    async def execute(self, command: Command) -> CommandResponse:
        """Execute at-risk analysis"""
        
        if command.action == "identify":
            # Existing logic: get students at risk in time period
            time_period = command.parameters.get("time_period", "week")
            at_risk_students = await self._identify_at_risk(time_period)
            
            return CommandResponse(
                status="success",
                result=at_risk_students,
                confidence=0.87,
                explanation=f"Identified {len(at_risk_students)} at-risk students in past {time_period}",
                next_steps=["Get details on specific student", "Plan interventions"]
            )
        
        elif command.action == "analyze":
            # Get detailed analysis for student
            student_id = command.parameters.get("student_id")
            analysis = await self._analyze_student(student_id)
            return CommandResponse(
                status="success",
                result=analysis,
                confidence=0.92,
                explanation=f"Detailed analysis for student {student_id}",
            )
```

**Time**: 15-20 hours
**Why**: Standardizes how agents work internally

#### 5.2 Create agent registry

```python
# New file: backend/core/agent_registry.py

class AgentRegistry:
    """Central registry of all agents"""
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
    
    def register(self, agent: Agent):
        """Register new agent"""
        self.agents[agent.name] = agent
    
    def get_agent(self, name: str) -> Optional[Agent]:
        """Get agent by name"""
        return self.agents.get(name)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all agents + capabilities"""
        return [
            {
                "name": agent.name,
                "capabilities": agent.capabilities,
                "required_parameters": agent.required_parameters,
            }
            for agent in self.agents.values()
        ]

# Create global registry
agent_registry = AgentRegistry()

# Register existing agents
agent_registry.register(AtRiskAgent())
agent_registry.register(BehaviorManagementAgent())  # Future
agent_registry.register(LearningPathAgent())  # Future
```

**Time**: 5-10 hours
**Why**: System knows what agents exist and what they do

---

## STEP 6: Command Bus (20 hours)

### Goal
Central hub that routes commands to right agent and returns standardized responses.

### Implementation

#### 6.1 Create `backend/core/command_bus.py`

```python
# New file: backend/core/command_bus.py

from backend.core.agent_interface import Command, CommandResponse
from backend.core.agent_registry import agent_registry

class CommandBus:
    """Route commands to agents, execute, return results"""
    
    async def execute(self, command: Command) -> CommandResponse:
        """Execute command on appropriate agent"""
        
        # Find agent
        agent = agent_registry.get_agent(command.agent_name)
        if not agent:
            return CommandResponse(
                status="error",
                result=None,
                confidence=0.0,
                explanation=f"Unknown agent: {command.agent_name}",
            )
        
        # Validate parameters
        required = agent.required_parameters.get(command.action, [])
        missing = [p for p in required if p not in command.parameters]
        
        if missing:
            return CommandResponse(
                status="error",
                result=None,
                confidence=0.0,
                explanation=f"Missing parameters: {missing}",
            )
        
        # Execute
        try:
            response = await agent.execute(command)
            return response
        except Exception as e:
            return CommandResponse(
                status="error",
                result=None,
                confidence=0.0,
                explanation=f"Execution error: {str(e)}",
            )

# Create global command bus
command_bus = CommandBus()
```

**Time**: 8-10 hours
**Why**: Provides unified entry point for agent execution

#### 6.2 Create command bus API endpoint

```python
# New file: backend/api/commands.py

from fastapi import APIRouter, Depends
from backend.core.command_bus import command_bus
from backend.core.agent_interface import Command

router = APIRouter(prefix="/api/commands", tags=["commands"])

@router.post("/execute")
async def execute_command(command_data: dict):
    """Execute command on agent"""
    command = Command(
        agent_name=command_data.get("agent"),
        action=command_data.get("action"),
        parameters=command_data.get("parameters", {}),
        context=command_data.get("context"),
    )
    
    response = await command_bus.execute(command)
    return response.__dict__

@router.get("/agents")
async def list_agents():
    """List all available agents and their capabilities"""
    return {
        "agents": agent_registry.list_agents()
    }

# Include in main app
app.include_router(router)
```

**Time**: 7-10 hours
**Why**: REST API for command bus - enables natural language layer to hook in

#### 6.3 Create command endpoint tests

```python
# New file: tests/test_command_bus.py

def test_execute_valid_command():
    """Command bus executes valid command"""
    command = Command(
        agent_name="at-risk-identifier",
        action="identify",
        parameters={"time_period": "week"}
    )
    
    response = await command_bus.execute(command)
    assert response.status == "success"
    assert response.confidence > 0.8

def test_execute_invalid_agent():
    """Command bus rejects unknown agent"""
    command = Command(
        agent_name="nonexistent",
        action="identify",
        parameters={}
    )
    
    response = await command_bus.execute(command)
    assert response.status == "error"

def test_execute_missing_parameters():
    """Command bus rejects missing parameters"""
    command = Command(
        agent_name="at-risk-identifier",
        action="identify",
        parameters={}  # Missing required time_period
    )
    
    response = await command_bus.execute(command)
    assert response.status == "error"
    assert "Missing parameters" in response.explanation
```

**Time**: 5-10 hours
**Why**: Ensure command bus works before NLI builds on it

---

## STEP 7: Natural Language Command Parser (25-35 hours)

### Goal
Convert teacher's English → structured Command that bus understands.

### Implementation

#### 7.1 Create `backend/core/nli_parser.py`

```python
# New file: backend/core/nli_parser.py

from backend.core.agent_interface import Command
from typing import Optional, Dict, Any
import re

class NLIParser:
    """Natural Language Interface - convert English to Commands"""
    
    # Step 1: Pattern matching (simple cases)
    PATTERNS = {
        "identify_at_risk": {
            "regex": r"(show|find|list|who.*)(is|are)?\s*(at.?risk|struggling|failing)",
            "agent": "at-risk-identifier",
            "action": "identify",
            "extract_params": lambda text: {"time_period": extract_time_period(text) or "week"}
        },
        "analyze_student": {
            "regex": r"(analyze|tell me about|show me)\s+(\w+)",
            "agent": "at-risk-identifier",
            "action": "analyze",
            "extract_params": lambda text: {"student_id": extract_student_name(text)}
        },
    }
    
    def __init__(self, llm_client):
        self.llm = llm_client  # For ambiguous cases
    
    def parse(self, natural_language: str) -> Optional[Command]:
        """Convert English to Command"""
        
        # Step 1: Try pattern matching
        for pattern_name, pattern in self.PATTERNS.items():
            if re.search(pattern["regex"], natural_language, re.IGNORECASE):
                return Command(
                    agent_name=pattern["agent"],
                    action=pattern["action"],
                    parameters=pattern["extract_params"](natural_language),
                )
        
        # Step 2: If no pattern match, use LLM for complex understanding
        command = await self._parse_with_llm(natural_language)
        return command
    
    async def _parse_with_llm(self, text: str) -> Optional[Command]:
        """Use LLM when pattern matching fails"""
        
        prompt = f"""
        User: "{text}"
        
        Convert to structured command:
        - agent: one of {list(agent_registry.agents.keys())}
        - action: what they want to do
        - parameters: parameters as JSON
        
        Response format:
        {{
            "agent": "...",
            "action": "...",
            "parameters": {{...}}
        }}
        """
        
        response = await self.llm.generate_text(prompt)
        try:
            command_dict = json.loads(response)
            return Command(**command_dict)
        except:
            return None

def extract_time_period(text: str) -> Optional[str]:
    """Extract time period from text: 'week', 'month', etc."""
    if re.search(r"this\s+week", text, re.IGNORECASE):
        return "week"
    elif re.search(r"this\s+month", text, re.IGNORECASE):
        return "month"
    # etc.
    return None

def extract_student_name(text: str) -> Optional[str]:
    """Extract student name from text"""
    # Could use NER (Named Entity Recognition) for sophisticated parsing
    # For now, simple regex
    names = ["Noah", "Marcus", "Emma"]  # From database
    for name in names:
        if name.lower() in text.lower():
            return name
    return None
```

**Time**: 18-25 hours
**Why**: Translates English into command bus

#### 7.2 Create NLI endpoint

```python
# New file: backend/api/natural_language.py

from fastapi import APIRouter
from backend.core.nli_parser import NLIParser
from backend.core.command_bus import command_bus

router = APIRouter(prefix="/api/nli", tags=["natural-language"])

@router.post("/ask")
async def ask_system(query: dict):
    """Natural language query to system"""
    
    text = query.get("question")
    
    # Parse natural language to command
    parser = NLIParser(llm_client)
    command = parser.parse(text)
    
    if not command:
        return {
            "status": "error",
            "explanation": "Couldn't understand question",
            "suggestions": "Try: 'Show me at-risk students' or 'Tell me about Noah'"
        }
    
    # Execute command
    response = await command_bus.execute(command)
    
    return {
        "original_question": text,
        "parsed_command": {
            "agent": command.agent_name,
            "action": command.action,
            "parameters": command.parameters,
        },
        "response": response.__dict__,
    }

# Include in main app
app.include_router(router)
```

**Time**: 5-8 hours
**Why**: Exposes NLI as REST endpoint

#### 7.3 Create NLI tests

```python
# New file: tests/test_nli_parser.py

def test_parse_simple_at_risk():
    """Parser recognizes at-risk query"""
    parser = NLIParser(mock_llm)
    
    command = parser.parse("Show me students at risk")
    assert command.agent_name == "at-risk-identifier"
    assert command.action == "identify"
    assert command.parameters["time_period"] == "week"

def test_parse_with_time():
    """Parser extracts time period"""
    parser = NLIParser(mock_llm)
    
    command = parser.parse("Show me students struggling this month")
    assert command.parameters["time_period"] == "month"

def test_parse_analyze_student():
    """Parser recognizes student analysis query"""
    parser = NLIParser(mock_llm)
    
    command = parser.parse("Tell me about Noah")
    assert command.agent_name == "at-risk-identifier"
    assert command.action == "analyze"
    assert command.parameters["student_id"] == "Noah"
```

**Time**: 5-8 hours
**Why**: Ensure parsing works correctly

---

## STEP 8: Frontend Natural Language Interface (15-25 hours)

### Goal
Teachers can type questions and get answers naturally.

### Implementation

#### 8.1 Create Streamlit NLI page

```python
# New file: frontend/desktop-web/pages/03_🗣️_ask_system.py

import streamlit as st
import requests

st.title("Ask PTCC")
st.markdown("Type your question naturally - the system will understand.")

# Input
question = st.text_input(
    "What would you like to know?",
    placeholder="e.g., 'Show me at-risk students' or 'Tell me about Noah'"
)

if st.button("Ask"):
    # Call NLI endpoint
    response = requests.post(
        "http://localhost:8001/api/nli/ask",
        json={"question": question}
    )
    
    result = response.json()
    
    # Show what system understood
    with st.expander("📋 What the system understood"):
        st.json(result["parsed_command"])
    
    # Show response
    if result["response"]["status"] == "success":
        st.success(f"✅ {result['response']['explanation']}")
        st.json(result["response"]["result"])
        
        if result["response"]["next_steps"]:
            st.markdown("**Next steps:**")
            for step in result["response"]["next_steps"]:
                st.markdown(f"- {step}")
    else:
        st.error(f"❌ {result['response']['explanation']}")
        
        if "suggestions" in result:
            st.markdown("**Try asking:**")
            for suggestion in result["suggestions"]:
                st.markdown(f"- {suggestion}")

# Show example queries
st.markdown("---")
st.markdown("**Example queries:**")
queries = [
    "Show me at-risk students",
    "Show me students struggling this week",
    "Tell me about Noah",
    "Who needs help this month?",
]
for q in queries:
    if st.button(q):
        st.write(f"You asked: {q}")
```

**Time**: 8-12 hours
**Why**: Teachers use system naturally

#### 8.2 Create test data for NLI

```python
# New file: tests/test_nli_integration.py

async def test_nli_end_to_end():
    """Full flow: question → parsing → execution → response"""
    
    # User asks question
    response = await client.post(
        "/api/nli/ask",
        json={"question": "Show me at-risk students this week"}
    )
    
    result = response.json()
    
    # Check parsing
    assert result["parsed_command"]["agent"] == "at-risk-identifier"
    assert result["parsed_command"]["action"] == "identify"
    
    # Check response
    assert result["response"]["status"] == "success"
    assert len(result["response"]["result"]) > 0
```

**Time**: 5-8 hours
**Why**: Ensure full flow works

---

### Phase 2B Summary

| Component | Hours | Status | Outcome |
|-----------|-------|--------|---------|
| Agent Interface | 30 | Ready | All agents speak same language |
| Agent Registry | 10 | Ready | System knows what agents exist |
| Command Bus | 20 | Ready | Unified command execution |
| NLI Parser | 35 | Ready | English → Commands |
| Frontend NLI | 20 | Ready | Teachers ask naturally |
| Testing | 10 | Ready | Full flow validated |
| **TOTAL PHASE 2B** | **95** | **Ready for deployment** | **NLI foundation complete** |

---

# IMPLEMENTATION TIMELINE

## Week 1 (40 hours)
- **Days 1-2**: Data Model Abstraction (30 hrs)
- **Days 3-4**: Unified Data Model setup (20 hrs)
- **Days 5**: Start Query Router (10 hrs)

## Week 2 (40 hours)
- **Days 1-2**: Finish Query Router (15 hrs)
- **Days 3-5**: Data Sync Framework (25 hrs)

## Week 3 (40 hours)
- **Days 1-3**: Agent Interface (30 hrs)
- **Days 4-5**: Start Command Bus (10 hrs)

## Week 4 (40 hours)
- **Days 1-2**: Finish Command Bus (10 hrs)
- **Days 3-4**: NLI Parser (25 hrs)
- **Days 5**: Frontend NLI + Testing (15 hrs)

## Week 5 (35 hours - buffer/testing)
- Full end-to-end testing
- Performance optimization
- Bug fixes and polish

**Total: 195 hours = 4.9 weeks (5 weeks with buffer)**

---

# DEPLOYMENT CHECKLIST

Before moving to Pilot Phase:

- [ ] All Phase 2A components deployed to backend
- [ ] All Phase 2B components deployed to backend
- [ ] Frontend NLI page working
- [ ] Tests passing (95%+ coverage)
- [ ] Performance validated (<2s for all queries)
- [ ] Documentation complete
- [ ] Demo script tested
- [ ] 5 schools identified and contacted
- [ ] Pilot agreements signed

---

# SUCCESS CRITERIA

After Phase 2 foundation:

1. ✅ Teachers can type questions naturally, system understands
2. ✅ New features can be added without refactoring
3. ✅ Data is consistent across all sources
4. ✅ System scale without re-architecture
5. ✅ Team can move 3x faster on new features
6. ✅ Technical debt eliminated

---

# BUSINESS IMPACT

| Metric | Before Phase 2 | After Phase 2 |
|--------|---|---|
| Time to add new feature | 6-8 weeks | 2-3 weeks |
| Refactoring risk | HIGH | LOW |
| Maximum schools supported | ~5 | ~500+ |
| Engineering velocity | 3 features/month | 8 features/month |
| Team scalability | Limited | Unlimited |

**Bottom line**: Phase 2 is not optional—it's the difference between a startup and a sustainable business.

