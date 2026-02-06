# AgentOS

**Zero-Trust Execution for AI Agents**

AgentOS is a **security gateway** that sits between AI agents (LLMs) and real-world systems. Agents may **request** actions, but they **never execute** them directly. AgentOS enforces policy, isolates execution, injects secrets just-in-time (BYOK), and writes a mandatory audit record for every attempt.

> **Agents request. The Kernel decides. The Kernel executes.**

---

## Why AgentOS

Modern agent frameworks often:

* Let agents hold API keys
* Execute tools inline
* Provide weak or no audit trails

AgentOS fixes this by treating agents as **untrusted requesters** and execution as a **privileged operation**.

---

## Core Axioms

* **Separation of Concerns**: Reasoning (LLM) ≠ Execution (AgentOS)
* **Isolation**: One-shot OS subprocess per action (no shared memory)
* **BYOK**: Secrets injected JIT into workers; never visible to agents
* **Mandatory Audit**: No action without policy check and post-flight log

---

## High-Level Architecture

```
Planner (LLM)  ──►  AgentOS Kernel  ──►  Worker (Subprocess)
   Untrusted          Trusted                Isolated
```

* **Planner**: Generates structured action requests
* **Kernel**: Validates, authorizes, injects secrets, spawns workers, audits
* **Worker**: Executes exactly one side-effect and exits

---

## Repository Structure (v0)

```
agent-os/
├── actions/            # Worker scripts (one action each)
├── kernel/
│   ├── gate.py         # Execution gate (subprocess orchestration)
│   ├── policy.py       # ACL evaluation (deny by default)
│   ├── vault.py        # Secret lookup & JIT injection
│   └── audit.py        # Append-only audit logger
├── logs/               # JSONL audit records
├── policy.yaml         # Agent → allowed actions
├── main.py             # Thin FastAPI ingress
└── .env                # Dev-only secret source (never for production)
```

---

## Action Request (Contract)

Agents emit **data**, never code:

```json
{
  "agent_id": "agent_1",
  "action": "hello_world",
  "inputs": {}
}
```

---

## Hello World (v0 Goal)

**Prove isolation + BYOK + audit in one shot.**

**Success criteria:**

1. Agent requests `hello_world`
2. Kernel approves via policy
3. Worker runs in a fresh subprocess
4. Worker receives an injected **dummy key**
5. Worker **cannot** see any master secrets
6. Audit record is written

---

## Security Posture (v0)

**Protected against:**

* Key exfiltration via prompts
* Unbounded tool execution
* Non-auditable actions

**Out of scope (v0):**

* Kernel/OS compromise
* Side-channel attacks
* Distributed adversaries

---

## Positioning

AgentOS is **security & governance infrastructure**, comparable to Zero-Trust systems (e.g., network security) but applied to **AI execution**.

* Not an agent framework
* Not a chatbot
* Not an autonomy engine

---

## Roadmap (Explicitly Parked)

* JWT capabilities
* SQLite audit ledger
* Human-in-the-loop approvals
* Stronger sandboxing (containers/VMs)

---

## License

TBD

---

## Immediate Next Step

See `NEXT_STEP.md` for the selected implementation step and completion criteria.
