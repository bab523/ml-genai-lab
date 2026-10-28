import re, shutil, subprocess, sys, os
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama", timeout=600)
MODEL = os.getenv("LLM_MODEL", "qwen2.5:7b")
MAX_ROUNDS = 3
TARGET = "data/target"
WORK = "outputs/work"
log = []

def say(who, msg):
    print(f"[{who}] {msg[:160]}")
    log.append(f"### {who}\n{msg}\n")

def llm(system, user):
    r = client.chat.completions.create(model=MODEL, temperature=0,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}])
    return r.choices[0].message.content

def strip_code(t):
    m = re.search(r"```(?:python)?\n(.*?)```", t, re.S)
    return (m.group(1) if m else t).strip() + "\n"

def scanner(code):
    notes = open("data/owasp_notes.md").read()
    out = llm("You are a Security Scanner agent. Use the OWASP notes to find vulnerabilities in the code. "
              "List each as: line/function, vulnerability type, one-line fix hint. Be concise.",
              f"OWASP notes:\n{notes}\n\nCode:\n```python\n{code}\n```")
    say("Scanner", out)
    return out

def remediation(code, findings, feedback=""):
    out = llm("You are a Remediation agent. Rewrite the COMPLETE Python file so every listed vulnerability is fixed. "
              "Keep function names and signatures. Return ONLY the full file in one ```python block.",
              f"Findings:\n{findings}\n\nQA feedback from the previous attempt:\n{feedback or 'none'}\n\n"
              f"Current code:\n```python\n{code}\n```")
    patched = strip_code(out)
    say("Remediation", f"Produced patch ({len(patched.splitlines())} lines)")
    return patched

def qa(patched):
    shutil.rmtree(WORK, ignore_errors=True)
    shutil.copytree(TARGET, WORK)
    open(f"{WORK}/app.py", "w").write(patched)
    try:
        compile(patched, "app.py", "exec")
    except SyntaxError as e:
        say("QA", f"FAIL - syntax error: {e}")
        return False, f"SyntaxError: {e}"
    p = subprocess.run([sys.executable, "-m", "pytest", "-q", "--tb=short"], cwd=WORK,
                       capture_output=True, text=True, timeout=120)
    tail = (p.stdout + p.stderr)[-900:]
    ok = p.returncode == 0
    say("QA", ("PASS - all tests passed" if ok else "FAIL - tests failed") + f"\n```\n{tail}\n```")
    return ok, tail

code = open(f"{TARGET}/app.py").read()
findings = scanner(code)
patched, feedback, passed = code, "", False
for rnd in range(1, MAX_ROUNDS + 1):
    say("Orchestrator", f"Round {rnd}: sending findings to Remediation")
    patched = remediation(code, findings, feedback)
    passed, feedback = qa(patched)
    if passed:
        break
    say("Orchestrator", "QA rejected the patch, sending feedback back to Remediation (self-correction loop)")

os.makedirs("outputs", exist_ok=True)
open("outputs/app_patched.py", "w").write(patched)
verdict = f"PASSED after {rnd} round(s)" if passed else f"NOT FIXED after {MAX_ROUNDS} rounds"
say("Orchestrator", f"Final verdict: {verdict}")
open("outputs/audit_log.md", "w").write("# Multi-agent security audit log\n\n" + "\n".join(log))
print("\nVerdict:", verdict, "| log: outputs/audit_log.md | patched file: outputs/app_patched.py")
