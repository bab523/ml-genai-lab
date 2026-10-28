# P7: ReAct Financial Analyst Agent
- Tools: sql_query (read-only SQLite), market_search (embedding search over PDFs), calculator (safe AST arithmetic).
- Agent: hand-written ReAct loop (Thought, Action, Observation) with JSON actions, message history as memory, a 10-step limit and error feedback for bad tool calls.
- Data: synthetic clients database and fictional market and tax PDFs (make_data.py).
- Deliverables: outputs/trace_customer_x.md and trace_customer_y.md show the thought-action-observation cycles.
- Why an agent and not plain RAG: the question needs SQL data, document facts and arithmetic combined across several steps.
- Limitation: a small local model sometimes skips steps or miscalculates; a larger model (qwen2.5:7b) improves tool use.
