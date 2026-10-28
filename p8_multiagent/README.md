# P8: Multi-Agent DevSecOps Code Audit
- Target: a deliberately vulnerable app.py (SQL injection, command injection, hardcoded secret, path traversal) with a pytest suite as the QA oracle.
- Agents: Scanner (reads OWASP notes and flags bugs), Remediation (rewrites the file), QA (syntax check and real pytest run).
- Orchestration: Scanner output goes to Remediation; QA results come back as feedback; up to 3 self-correction rounds (see outputs/audit_log.md).
- Outputs: outputs/audit_log.md and outputs/app_patched.py.
- Model: local qwen2.5:7b via Ollama.
- Limitation: the tests cover only these four issues, so a pass does not prove the code is fully secure.


## Results
- Model: llama3.2:3b via Ollama (qwen2.5:7b timed out on a CPU-only laptop).
- Verdict: PASSED after 1 round (all pytest tests green).
- See outputs/audit_log.md for the full agent conversation and the self-correction loop.
