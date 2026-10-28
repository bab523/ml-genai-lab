import json, re, sys
from openai import OpenAI
from tools import TOOLS

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama", timeout=300)
MODEL = "qwen2.5:7b"
MAX_STEPS = 10

SYSTEM = """You are a financial analyst agent. Answer the user's question by using tools step by step.

Tools:
- sql_query(query): SELECT on clients(client_id,name,risk_profile,tax_bracket) and holdings(client_id,asset_class,sector,balance).
- market_search(question): search the Q3 market outlook and tax notes (expected returns per sector).
- calculator(expression): arithmetic only, numbers and + - * / ** and parentheses.

On EVERY turn reply with exactly one JSON object, nothing else:
{"thought": "your reasoning", "action": "tool_name", "input": "tool input"}
When you have everything needed, reply with:
{"thought": "your reasoning", "final_answer": "the full answer with numbers"}

Rules:
- Never guess numbers. Get balances from SQL, expected returns from market_search, and do ALL maths with calculator.
- Use one tool call per turn. Use the observation before your next step.
- Projected tax risk = projected gain x the client's tax_bracket (only on positive gains)."""

def run(question, log_path="outputs/trace.md"):
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    trace = [f"# Question\n{question}\n"]
    for step in range(1, MAX_STEPS + 1):
        r = client.chat.completions.create(model=MODEL, messages=messages, temperature=0,
                                           response_format={"type": "json_object"})
        raw = r.choices[0].message.content.strip()
        messages.append({"role": "assistant", "content": raw})
        try:
            data = json.loads(raw)
        except Exception:
            messages.append({"role": "user", "content": "Invalid JSON. Reply with one JSON object only."})
            trace.append(f"## Step {step}\n(invalid JSON: {raw[:100]})\n")
            continue
        thought = data.get("thought", "")
        if "final_answer" in data:
            trace.append(f"## Step {step}\n**Thought:** {thought}\n\n**Final Answer:** {data['final_answer']}\n")
            break
        action, inp = data.get("action"), str(data.get("input", ""))
        if action not in TOOLS:
            obs = f"ERROR: unknown tool '{action}'. Use sql_query, market_search or calculator."
        else:
            obs = TOOLS[action](inp)
        trace.append(f"## Step {step}\n**Thought:** {thought}\n\n**Action:** `{action}`\n\n**Input:** `{inp}`\n\n**Observation:**\n```\n{obs}\n```\n")
        print(f"step {step}: {action}({inp[:70]})")
        messages.append({"role": "user", "content": f"Observation: {obs}"})
    else:
        trace.append("## Stopped\nReached the step limit without a final answer.\n")
    open(log_path, "w").write("\n".join(trace))
    return "\n".join(trace)

if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or ("Compare Customer X's current portfolio balance in SQL against our Q3 market outlook "
                                   "and calculate their projected tax risk.")
    out = run(q)
    print("\n" + out[-900:])
