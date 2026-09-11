# 🛡️ DocuMind Red-Teamer

## Red-team legal contracts before your opponent does.

**DocuMind Red-Teamer** is a hackathon-ready Streamlit security tool that adversarially scans legal contracts, NDAs, SaaS agreements, and corporate policies for hidden liabilities, poison pills, missing safeguards, compliance gaps, and exploitable enforcement mechanics.

> **Pitch:** Traditional contract review asks, “What does this clause say?”  
> **DocuMind asks, “How could an adversary abuse it?”**

---

## 🏆 Why this can win a hackathon

DocuMind is designed around the first 30 seconds of a judge demo:

1. **Upload or one-click launch a vulnerable contract.**
2. Instantly reveal a **0–100 Threat Score**.
3. Show **Critical / Medium / Low** findings in a visual risk dashboard.
4. Drill into the exact clause and the recommended counter-clause.
5. Ask the **Adversarial Simulator** how an opponent could exploit the agreement.
6. Export an executive Markdown or PDF audit.

The result is a security product experience rather than a generic “chat with a PDF” application.

---

# 🎯 Problem Statement

Legal contracts can hide asymmetric risk in ordinary-looking language:

- uncapped indemnification
- unilateral termination or suspension
- vague arbitration/forum selection
- overbroad IP assignments
- unilateral pricing changes
- missing cure periods
- missing force majeure protection
- weak privacy/security language
- unclear breach notification
- poor data-retention and deletion mechanics
- vendor lock-in and weak exit rights

A conventional document chatbot can retrieve a clause, but retrieval alone does not answer the security question:

> **“What happens if the other side intentionally interprets this clause against us?”**

---

# 💡 Solution

DocuMind combines:

### 🔎 Adversarial rule engine
Specialized detectors search for high-impact contract attack surfaces.

### 🧠 Local RAG
The document is split into legal-friendly chunks:

- **Chunk size:** 800 characters
- **Overlap:** 100 characters

Chunks are embedded locally with `all-MiniLM-L6-v2` and indexed using **FAISS**.

### ⚔️ Red-team scenario simulator
The user can ask questions such as:

> “How could a vendor exploit this agreement to charge hidden fees?”

The system retrieves relevant document context and connects it to detected findings.

### 📊 Executive scorecard
The dashboard converts technical findings into judge-friendly metrics:

- Threat Score
- Red Flags
- Missing Safeguards
- Enforceability Score
- Severity Breakdown
- Top Deal-Breakers

### 📜 Explainable findings
Every finding exposes:

- severity
- category
- confidence
- exact clause/context
- why an adversary cares
- recommended defensive redline

---

# 🏗️ Architecture

```text
                         ┌──────────────────────────┐
                         │     Streamlit UI/UX      │
                         │ Cyber-Legal Glassmorphism │
                         └────────────┬─────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                    ▼                 ▼                 ▼
             Document Parser    Red-Team Engine    Export Engine
             PDF / TXT / DOCX   Rule-based scans   MD / PDF
                    │                 │
                    ▼                 ▼
             Legal Chunker      Risk Findings
             800 / 100           Critical / Medium / Low
                    │
                    ▼
          Sentence-Transformer Embeddings
                    │
                    ▼
             ┌──────────────┐
             │    FAISS     │
             │ Vector Index │
             └──────┬───────┘
                    │
                    ▼
          Adversarial Scenario Retrieval
                    │
                    ▼
             Explainable Answer
```

---

# 🧰 Tech Stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| Language | Python |
| Vector Search | FAISS |
| Embeddings | Sentence Transformers |
| RAG | Local retrieval pipeline |
| PDF Parsing | pypdf |
| DOCX Parsing | Python standard library / ZIP XML |
| Analytics | Pandas |
| Charts | Plotly |
| PDF Export | ReportLab |
| Styling | Custom CSS + glassmorphism |
| LLM API | **Not required** |

The project is intentionally **local-first**. There is no paid API, database, or external AI service required at runtime.

---

# 🧪 Red-Team Modules

## 1. Liability Poison Pills

Detects patterns such as:

- uncapped indemnification
- unlimited liability
- unilateral termination
- immediate suspension
- forum-controlled arbitration
- broad IP transfer language

### Example

```text
Customer shall indemnify Provider for all claims...
with no cap.
```

DocuMind flags this as a potential **Critical Liability Poison Pill**.

---

## 2. Missing Essential Safeguards

Checks for:

- Force Majeure
- Privacy / Data Protection
- Security incident notification
- Cure periods
- Data lifecycle language

A contract does not need to contain every possible clause, but missing safeguards become visible for human review.

---

## 3. Regulatory & Compliance Gaps

The engine looks for measurable security and governance concepts such as:

- encryption
- access controls
- vulnerability management
- penetration testing
- OWASP/security references
- retention
- deletion
- formal notice mechanics

These are **screening heuristics**, not a certification that a contract is legally compliant.

---

## 4. Adversarial Scenario Simulator

Try questions like:

```text
How can a vendor exploit the contract to charge hidden fees?

How could the provider terminate service unfairly?

What is the biggest IP ownership trap?

How could a data breach become a liability gap?

What happens if the vendor suffers a disaster?

How can the renewal clause create lock-in?
```

The simulator retrieves semantic document context using FAISS and connects the result to the detected red-team findings.

---

# 🎨 UX / Visual Design

DocuMind uses a cyber-legal visual language:

- dark gradient mesh background
- glassmorphism panels
- glowing severity accents
- crimson Critical findings
- amber Medium findings
- emerald Safe signals
- cyan RAG/AI context
- large executive metrics
- interactive Plotly charts
- expandable vulnerability cards
- chat-style adversarial simulator
- judge-friendly one-click samples

---

# ⚡ Quickstart

## 1. Clone / copy the three project files

```text
DocuMind-Red-Teamer/
├── app.py
├── requirements.txt
└── README.md
```

## 2. Create a virtual environment

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Start Streamlit

```bash
streamlit run app.py
```

Then open the local Streamlit address shown in your terminal.

---

# 🚀 30-Second Judge Demo

### Step 1

Launch the application.

### Step 2

Click:

**Exploitative NDA**

### Step 3

Point to:

- Threat Score
- Critical findings
- Missing safeguards
- Enforceability score

### Step 4

Open:

**🔍 Vulnerability Matrix & Context**

Show the exact risky clause and defensive redline direction.

### Step 5

Open:

**⚔️ Adversarial Simulator**

Ask:

```text
How could the counterparty exploit the IP clause?
```

Then ask:

```text
How could the indemnification clause create unlimited exposure?
```

### Step 6

Download:

**Executive PDF**

This gives judges a tangible audit artifact.

---

# 🔐 Security-First RAG Design

DocuMind deliberately avoids pretending that retrieval is the same thing as legal reasoning.

The pipeline is:

```text
Document
   ↓
Parser
   ↓
Chunking
   ↓
Local Embeddings
   ↓
FAISS
   ↓
Relevant Context
   ↓
Red-Team Rules
   ↓
Explainable Finding
```

This provides:

- local document processing
- transparent retrieval
- inspectable vector chunks
- deterministic core risk detection
- no mandatory API key
- no mandatory database
- no hidden external agent

---

# 📈 Risk Scoring

The prototype uses a transparent heuristic rather than an opaque model.

Conceptually:

```text
Critical finding  → large risk contribution
Medium finding    → moderate risk contribution
Low finding       → small risk contribution
```

The dashboard then maps the result onto:

```text
0 ───────────── 30 ───────────── 65 ───────────── 100
      Lower              Elevated             High
```

The **Enforceability Score** is also heuristic and should be treated as a screening signal, not a legal opinion.

---

# 📦 Project Files

Only three files are required:

### `app.py`
Complete Streamlit application, parsing, chunking, FAISS retrieval, red-team engine, dashboard, simulator, and exports.

### `requirements.txt`
Pinned runtime dependencies.

### `README.md`
This project guide.

---

# ⚠️ Legal / Security Disclaimer

DocuMind Red-Teamer is a **hackathon prototype and automated screening tool**.

It does **not** provide legal advice, determine whether a clause is legally enforceable, or replace a qualified lawyer.

A detected finding means:

> **“This deserves adversarial human review.”**

It does not automatically mean:

> **“This clause is unlawful or unenforceable.”**

---

# 🏅 Hackathon Value Props

## 🔥 Security-first RAG

Not just “chat with a PDF.”  
The product asks how contractual language can be abused.

## 📊 Real-time risk heatmaps

Judges immediately understand the contract's risk posture without reading pages of legal text.

## ⚔️ Adversarial simulation

The user can think like the counterparty and test attack scenarios.

## 🧩 Explainability

Every finding connects a risk to a clause and a recommended defensive direction.

## ⚡ Instant compliance audit

Upload → index → scan → visualize → export.

## 💻 Local-first

No mandatory paid API or database.

---

# 🌟 Future Extensions

For a production version, the architecture can be extended with:

- jurisdiction-specific clause libraries
- OWASP ASVS / API Security mappings
- configurable corporate playbooks
- contract-to-contract diffing
- semantic clause normalization
- attorney review workflow
- SSO / RBAC
- encrypted document storage
- human-in-the-loop approval
- optional enterprise LLM with strict prompt-injection defenses
- evidence-backed citations to internal policy sources

---

## Final Pitch

> **DocuMind Red-Teamer doesn't just read the contract. It attacks the contract on your behalf—before the other side does.**
