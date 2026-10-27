import sys
from openai import OpenAI
from retrievers import chunks, retrieve

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama", timeout=180)

def answer(question, top_n=3):
    idxs = retrieve(question, "hybrid_rerank", top_n)
    ctx = "\n".join(f"[{chunks[i]['id']}] {chunks[i]['text']}" for i in idxs)
    prompt = ("Answer ONLY from the contract excerpts below. Cite the clause id in square brackets, "
              "like [MSA-2025-107#3], after each claim. If the excerpts do not contain the answer, "
              "reply exactly: Not found in the provided contracts.\n\n"
              f"Excerpts:\n{ctx}\n\nQuestion: {question}")
    r = client.chat.completions.create(model="llama3.2:3b", temperature=0,
                                       messages=[{"role": "user", "content": prompt}])
    return r.choices[0].message.content, [chunks[i]["id"] for i in idxs]

if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "What is the liability cap in the Aldrin Logistics and Nimbus Cloud agreement?"
    a, srcs = answer(q)
    print("Q:", q, "\nA:", a, "\nSources:", srcs)
