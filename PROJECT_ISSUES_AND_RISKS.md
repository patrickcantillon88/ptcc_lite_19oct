# PTCC Project: Issues, Workarounds, Risks, and Time Sinks

Last updated: 2025-10-17

## 1) Biggest Hang‑ups and Bugs We’ve Hit

- Naming/Module Drift
  - Legacy routers still present alongside renamed ones: `backend/api/guardian.py` vs `digital_citizenship.py`, `ict_behavior.py` vs `behaviour_management.py` (also a UK/US spelling mix).
  - Frontend remnants (`frontend/project-guardian`) can cause confusion and double maintenance.
  - Impact: duplicate code paths, inconsistent routes/tags, brittle tests.

- LLM/Gemini Setup Friction
  - Env var inconsistencies, lazy init race conditions, Streamlit reruns re-creating clients, first-call latency perceived as “hang”.
  - Model ID drift across files: `gemini-2.5-flash`, `-flash-lite`, `-flash-exp` appear in different modules.
  - Impact: intermittent failures, user confusion, non-deterministic behavior.

- RAG Engine Warts
  - Async search path calls `run_until_complete` in a running loop (falls back to sequential). Parallelism effectively disabled.
  - Document IDs use Python `hash(file_path)` → not stable across runs (salted hash). Breaks dedupe/update.
  - Index includes names within metadata; safe locally, but requires strict prompt sanitization before any external LLM.

- Behavior Module Inconsistencies
  - Categories differ across legacy/new modules (`ict_strike` vs `behaviour_strike`), analytics can miscount unless both are handled.
  - Mixed “behaviour/behavior” spellings complicate filters/queries.

- CORS/Networking
  - Hardcoded origin/IP lists; brittle across environments and networks.

- Tests/Fixtures
  - Tests that touch AI/RAG can be flaky when keys/models/indexes change.
  - Example files in root (multiple `test_*.py`) can create noise and duplicate coverage paths.

## 2) Where We Took Different (Simpler) Routes

- Local‑first RAG + Privacy Layer
  - Chose local Chroma + sentence-transformers and a de‑identification layer before any LLM call.
  - Deferred RAG init to speed startup; singletons for heavy clients.

- Scope Reduction for Behaviour Management
  - Focused on strikes/positives, simplified session model, pushed admin flags to explicit fields.

- Renaming Modules for Clarity
  - “Project Guardian” → “Digital Citizenship”; “ICT Behavior” → “Behaviour Management” for teacher comprehension.

- Avoided Tight Coupling
  - Agents, prompts, RAG, and UI remain loosely coupled; each useful independently to reduce blast radius.

## 3) Current Frictions (What Is Slowing Us Now)

- Authentication/Authorization Absent
  - Blocks safe multi-user use; role-based filtering currently enforced at query level, not session identity.

- Data Hygiene for RAG
  - No automated vector hygiene on updates/deletes; risk of stale/duplicated embeddings.

- UI/UX Constraints
  - Streamlit is fast to iterate but limits interactivity and navigation polish; state/reruns cause surprises.

- Legacy Artifacts
  - Old routers and frontend remnants increase cognitive load and risk of calling the wrong endpoint.

## 4) Potential Blockers for Future Development

- Security & Compliance
  - Without auth/RBAC/audit trails, production deployment will stall.

- Performance at Scale
  - Chroma persistence, model load, and sequential search may struggle with >100k chunks; needs caching, reranking, and background indexing.

- Multi‑Tenant/School Rollout
  - Namespacing data, per-tenant configs, and isolation not yet designed.

- Data Migration & ETL
  - Real school data ingestion (varied spreadsheets/docs) will consume significant time without robust parsers.

- Provider Dependence
  - Model ID drift, rate limits, safety refusals; must maintain provider-agnostic templates and local fallback.

## 5) Past, Present, Future: Biggest Time‑Rich Implementations

- Past (already spent most time)
  - RAG scaffolding and indexing, data models/migrations.
  - Behaviour logging flows and lesson session state.
  - Building privacy‑preserving LLM pipeline and guardrails.

- Present (consuming time now)
  - Renaming/consistency sweep across backend/frontend.
  - Stabilizing LLM integration (keys, models, refusal handling).
  - Streamlit state management and navigation polish.

- Future (likely to consume the most time)
  - Authentication/RBAC/audit logging end-to-end.
  - Document ingestion pipeline (robust parsing, categorization, dedupe, updates).
  - Daily briefing generation (context assembly + performance tuning).
  - Vector hygiene & retrieval quality (MMR/rerankers, caching, background jobs).
  - Multi-tenant architecture and environment promotion (dev→prod).

## 6) Technical Debt Hotspots to Address Soon

- Remove legacy routers and directories; standardize naming (behaviour vs behavior) and categories.
- Centralize model IDs and provider config; expose via config only.
- Fix RAG IDs (stable deterministic IDs) and replace async search shim with a clean sync path or proper async API.
- Parameterize CORS origins via config/env.
- Add boot‑time health checks for keys, indexes, and model availability; clear admin UI for status.

## 7) Risk Summary (What Could Hold Us Back)

- Privacy slip through prompting if de‑ID isn’t enforced everywhere.
- Auth/RBAC delay preventing real multi-user testing.
- RAG performance/regressions with larger datasets.
- Organizational readiness (DPO/IT) and network constraints (proxies, SSL interception).

## 8) Recommended Near‑Term Actions (High ROI)

1) Auth/RBAC baseline: JWT, roles (Teacher/Admin/DSL), route guards, audit logs.  
2) Consistency pass: remove legacy files, unify routes/tags, normalize category names.  
3) RAG hygiene: stable IDs, background reindex, basic caching, MMR/reranker toggle.  
4) LLM config hardening: single config for provider/model IDs, warmup, refusal templates, local fallback.  
5) Ops visibility: /status endpoint extended (keys configured, index size, cache hits), plus a small admin panel.

---

These notes synthesize issues observed across code (routers, RAG, privacy, LLM integration), tests, and the UI stack. Addressing the “Near‑Term Actions” will remove most friction and unlock safe pilot deployments.