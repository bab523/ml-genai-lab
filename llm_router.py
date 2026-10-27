import os, re, time
from typing import Literal, Optional
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()
client = OpenAI(base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434/v1"),
                api_key=os.getenv("LLM_API_KEY", "ollama"),
                timeout=180, max_retries=0)
MODEL = os.getenv("LLM_MODEL", "llama3.2:3b")

class TicketResult(BaseModel):
    priority: Literal["low", "medium", "high"]
    category: Literal["billing", "technical", "feature_request"]
    draft_response: str
    reasoning: Optional[str] = None

RULES = ("You are a support-ticket triage assistant for a B2B SaaS company. "
         "Return ONLY a JSON object with keys: priority (low|medium|high), "
         "category (billing|technical|feature_request), draft_response (a polite reply of at most 3 sentences). "
         "high = outage, money lost, or customers affected; medium = needs action soon; low = minor or nice-to-have.")

EXAMPLES = [
 ("My payment failed twice and now my whole team is locked out.",
  '{"priority":"high","category":"billing","draft_response":"Sorry about the lockout. We are restoring access now and will check the failed payments."}'),
 ("Please add a Slack integration someday.",
  '{"priority":"low","category":"feature_request","draft_response":"Thanks for the idea. We have added it to our roadmap feedback list."}'),
 ("The /v2/items API returns 503 for all our requests.",
  '{"priority":"high","category":"technical","draft_response":"Sorry for the disruption. Our engineers are investigating the 503 errors right now."}'),
]

def build_messages(text, variant):
    if variant == "zero_shot":
        return [{"role": "system", "content": RULES}, {"role": "user", "content": text}]
    if variant == "few_shot":
        msgs = [{"role": "system", "content": RULES}]
        for q, a in EXAMPLES:
            msgs += [{"role": "user", "content": q}, {"role": "assistant", "content": a}]
        return msgs + [{"role": "user", "content": text}]
    if variant == "cot":
        sys = RULES + (" Also include a key 'reasoning' with 1-2 sentences explaining your decision. "
                       "Write 'reasoning' FIRST, before the other keys.")
        return [{"role": "system", "content": sys}, {"role": "user", "content": text}]
    raise ValueError(variant)

@retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=1, min=1, max=20), reraise=True)
def _call(messages):
    r = client.chat.completions.create(model=MODEL, messages=messages, temperature=0,
                                       response_format={"type": "json_object"})
    txt = r.choices[0].message.content.strip()
    txt = re.sub(r"^```(?:json)?|```$", "", txt, flags=re.M).strip()
    return TicketResult.model_validate_json(txt)   # raises if JSON or schema is wrong -> retried

def classify(text, variant="few_shot"):
    t = time.time()
    result = _call(build_messages(text, variant))
    return result, time.time() - t

if __name__ == "__main__":
    demo = "We were billed $4,000 twice and our CFO is furious. Please fix today."
    for v in ["zero_shot", "few_shot", "cot"]:
        res, sec = classify(demo, v)
        print(f"[{v}] {sec:.1f}s ->", res.model_dump())
