# AI Implementation Notes: Keys, Setup, and Practical Pitfalls

Last updated: 2025-10-17

## 1) API Keys, Config, and Environment
- Missing/incorrect env var: library names vary (`GEMINI_API_KEY`, `GOOGLE_API_KEY`, `GOOGLE_GENAI_API_KEY`). Standardize in one place; map internally.
- Multiple .env locations: root vs `backend/`. Ensure a single loader with clear precedence; document it.
- Process not picking up .env: uvicorn/Streamlit reloads spawn new processes without inherited env. Load with python-dotenv on app start.
- Quoting/whitespace: stray quotes, BOM, or trailing spaces in `.env` cause auth failures. Validate on boot.
- Service/daemon env: when running via launchd/systemd/PM2, export env in unit file; shell `export` is insufficient.
- Frontend leakage risk: never expose keys to Streamlit/React; all LLM calls from backend only.
- Key restrictions: HTTP referrer/IP restrictions break local dev. Use appropriately scoped restrictions per environment.
- Rotation & quotas: track usage per project; rotate keys safely; surface quota errors clearly to users.

## 2) Google/Gemini Setup Hurdles
- API enablement: ensure “Generative Language API” enabled on the correct GCP project with billing.
- No-retention settings: verify data logging/training is disabled at org/project level and per request where supported.
- Model IDs drift: libraries update model names (e.g., `gemini-1.5-pro`, `-flash`). Centralize IDs in config with safe fallbacks.
- Regional constraints: some org policies restrict regions; mismatched endpoints cause 403/404.
- Service account vs API key: some SDK paths prefer service accounts; decide one approach and document it.

## 3) “Lazy” Initialization Pitfalls (and fixes)
- Race conditions: creating the LLM client lazily on first request caused concurrent double-inits. Use a thread-safe singleton.
- Stale config: changing provider/keys at runtime wasn’t picked up. Watch config file or require explicit reload.
- Cold starts: first call latency high (TLS, model warmup). Add app warmup ping on boot.
- Streamlit reruns: re-inits clients on every interaction. Use `st.cache_resource`/module-level singleton.
- Connection reuse: enable HTTP keep-alive; reuse session to cut latency.

## 4) Privacy & Safeguarding Integration
- De-identification first: placeholders applied before prompt assembly; re-ID map kept strictly local.
- Overexposure via citations: source snippets could leak names. Redact sources before inclusion.
- Output leakage: LLM may infer names from context. Post-process and blocklist checks before display.
- Role scoping: retrieval filtered by role before chunk selection; prompts contain only authorized snippets.

## 5) Prompting, Safety, and Provider Responses
- Safety filters: Gemini may refuse content categories (self-harm, bullying). Provide policy context and safer framing; catch and explain refusals.
- Token budget: raw snippets overflow context. Summarize/dedupe before prompt; use top-k with MMR.
- Determinism: for assessments/reports, lower temperature and enforce JSON schema when needed.
- Function/tool calls: validate outputs; never trust free-text for actions without parsing/guards.

## 6) RAG & Embeddings Practicalities
- Model mismatch: mixed embedding models produced inconsistent dimensions; standardize.
- Stale vectors: changes in student data require vector deletes/updates; add hygiene tasks.
- Chunking: too large → token overflow; too small → loss of meaning. Tune size/overlap; dedupe near-duplicates.
- Retrieval quality: add domain rerankers or MMR to avoid repeating similar chunks.

## 7) Networking, Reliability, and Limits
- Proxies/SSL: school networks inject proxies; configure trust store/HTTPS proxy explicitly.
- Timeouts/retries: add exponential backoff for 429/5xx; circuit breaker to fallback (local model or non-AI path).
- Rate limits: queue requests per user; surface polite UI errors instead of hard failures.

## 8) Logging, Monitoring, and Testing
- No PII in logs: log placeholders + hashes only; redact prompts/responses.
- Correlation IDs: trace a user query through retrieval → prompt → response.
- Offline tests: mock LLM client for unit tests; golden files for deterministic flows.
- Telemetry: capture latency, token counts, refusal rates to guide tuning.

## 9) Product UX Considerations
- Clear states: “AI unavailable” vs “Privacy block” vs “Safety refusal” with actionable guidance.
- Manual override: let teachers proceed with non-AI results (search, policies) when AI declines.
- Explainability: show “Why you’re seeing this” (sources, role filters, date ranges).

## 10) Config & Ops Playbook
- Single source of truth: central `config.yaml` + `.env` keys; document precedence and required fields.
- Environment separation: dev vs prod keys/projects; prevent accidental prod usage in dev.
- Secrets handling: never echo secrets; load into env and reference only as variables.
- Health checks: startup verifies API enabled, model reachable, no-retention set, and a test prompt succeeds.

## 11) Model/Provider Choices
- Use `-flash` models for UI responsiveness; fallback to `-pro` for complex reasoning if needed.
- Local fallback: Ollama/other local models for zero-egress or outages.
- Content policies: keep prompt templates provider-agnostic; inject policy text relevant to refusals.

## 12) Known Gotchas We Hit
- Wrong env var name led to silent fallback to “no-LLM” mode; added explicit boot-time validation.
- Streamlit reruns recreated clients and exhausted rate limits; fixed with cached singleton.
- First-call latency looked like a “hang”; added warmup and clearer UI spinner.
- Safety refusals on bullying/incident text; improved de-identification and added school policy framing.
- Citations exposed names in edge cases; redaction layer now runs on sources and outputs.
- Mixed embedding models after upgrades; reindexed and pinned versions.

## 13) Action Items Remaining
- Add automated vector hygiene on student updates/deletions.
- Bake in circuit breaker + local-LLM fallback for outages.
- Expand refusal handling templates for common safeguarding scenarios.
- Add admin dashboard for token usage, latency, and refusal/error rates.
