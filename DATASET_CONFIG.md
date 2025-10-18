# PTCC Dataset Configuration

**Updated: 2025-10-17**

## Authoritative Source

**PDF**: `Example docs/Mock School Dataset for RAG System Testing.pdf`

This PDF contains the complete, official dataset for PTCC.

---

## Current Dataset

### Classes & Students
- **3A (Year 3)**: 10 students
- **4B (Year 4)**: 10 students
- **5C (Year 5)**: 10 students
- **6D (Year 6)**: 10 students
- **Total**: 40 students

### Support Level Distribution
- Level 0 (No support): 14 students
- Level 1 (Low support): 22 students
- Level 2 (Medium support): 4 students
- Level 3 (High support): 0 students

---

## Database Architecture

### SQL Database (`data/school.db`)
**Purpose**: Structured, queryable operational data

**Tables**:
- `students` - 40 student records (name, class_code, support_level)
- `quick_logs` - Behavior incidents, positive actions
- `assessments` - Academic scores
- `class_rosters` - Student-class assignments
- `schedule` - Timetable data
- `communications` - Parent/staff messaging

**Key constraint**: Only students with class_code in ['3A', '4B', '5C', '6D']

### ChromaDB Vector Store (`data/chroma/`)
**Purpose**: AI-powered semantic search via embeddings

**Function**: 
- Vectorizes student profiles and context from SQL
- Enables RAG (Retrieval Augmented Generation)
- Auto-populated on first RAG engine initialization

**Relationship**: Derived from SQL data, not a duplicate

---

## Consistency Guarantees

### SQL ↔ ChromaDB Synchronization
1. **SQL is source of truth** for student records
2. **ChromaDB is derived** from SQL for semantic search
3. **When to update**:
   - Update SQL directly → ChromaDB becomes stale (requires re-indexing)
   - Clear both → reimport from PDF → both fresh

### Class Validation
- **Valid classes only**: 3A, 4B, 5C, 6D
- **Code enforcement**: 
  - `backend/api/chat.py` line 135
  - `backend/scripts/import_sample.py` line 42
  - `backend/scripts/populate_class_rosters.py` line 31
  - `frontend/desktop-web/app.py` line 2650
  - `backend/scripts/migrate_pdf_dataset.py` lines 742, 828, 833

---

## Student Reference

### Class 3A (Year 3) - Teacher: Ms Elena Rodriguez
1. Aisha Kumar (Support: 0)
2. Marcus Thompson (Support: 1)
3. Sophie Chen (Support: 1)
4. Liam O'Brien (Support: 1)
5. Priya Patel (Support: 0)
6. Noah Williams (Support: 2) [AT-RISK]
7. Zoe Martinez (Support: 1)
8. James Park (Support: 1)
9. Emma Novak (Support: 0)
10. Oliver Grant (Support: 1)

### Class 4B (Year 4) - Teacher: Mr Tariq Hassan
1. Isabella Rossi (Support: 0)
2. Kai Tanaka (Support: 1)
3. Thomas Bradley (Support: 1)
4. Amelia Hassan (Support: 0)
5. Dylan Murphy (Support: 1)
6. Marta Silva (Support: 1)
7. Joshua Finch (Support: 2) [AT-RISK]
8. Natalia Kowalski (Support: 1)
9. Ravi Gupta (Support: 1)
10. Lucia Fernandez (Support: 0)

### Class 5C (Year 5) - Teacher: Mr James Watson
1. Lucas Santos (Support: 0)
2. Grace Pham (Support: 1)
3. Sebastian White (Support: 1)
4. Yuki Yamamoto (Support: 0)
5. Freya Nielsen (Support: 1)
6. Mohammed Al-Rashid (Support: 2) [AT-RISK, SAFEGUARDING]
7. Ivy Chen (Support: 0)
8. Ethan Hughes (Support: 1)
9. Sofia Delgado (Support: 1)
10. Alexander Petrov (Support: 0)

### Class 6D (Year 6) - Teacher: Ms Rebecca Singh
1. Charlotte Webb (Support: 0)
2. Dmitri Sokolov (Support: 1)
3. Amal Al-Noor (Support: 1)
4. Kenji Nakamura (Support: 0)
5. Sienna Brown (Support: 2) [AT-RISK]
6. Lars Andersen (Support: 1)
7. Maya Goldstein (Support: 0)
8. Cairo Lopez (Support: 1)
9. Priya Verma (Support: 1)
10. Harry Chen (Support: 0)

---

## Maintenance

### Adding New Data
1. Update PDF with new student information
2. Clear both SQL and ChromaDB
3. Run import script: `python3 import_pdf_students.py`
4. System is fresh and consistent

### Verifying Consistency
```bash
# Check SQL
sqlite3 data/school.db "SELECT COUNT(*) FROM students WHERE class_code NOT IN ('3A', '4B', '5C', '6D');"

# Should return: 0 (no invalid classes)
```

### Re-indexing ChromaDB
ChromaDB will auto-populate from SQL on first RAG query. To force re-index:
1. Delete `data/chroma/*`
2. Restart backend
3. Trigger any RAG query (search, briefing generation, etc.)

---

## Important Notes

- ✅ SQL database contains authoritative student records
- ✅ ChromaDB is derived for semantic search only
- ✅ Both databases reflect the PDF dataset
- ✅ Only classes 3A, 4B, 5C, 6D are valid
- ✅ 40 students total across 4 classes
- ✅ All code validated against this dataset
