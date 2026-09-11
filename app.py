import io
import re
import html
import json
import textwrap
import hashlib
import zipfile
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple

import numpy as np

import streamlit as st
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None


# ============================================================
# DocuMind Red-Teamer
# Local-first legal-contract red-team dashboard.
# No paid API or external LLM is required.
# ============================================================

st.set_page_config(
    page_title="DocuMind Red-Teamer",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------- CSS -----------------------------

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

:root {
    --bg: #0d1117;
    --panel: rgba(255,255,255,.035);
    --border: rgba(255,255,255,.10);
    --crimson: #FF4B4B;
    --amber: #FF9F1C;
    --green: #00E676;
    --cyan: #00B4D8;
    --purple: #9B5DE5;
    --text: #F5F7FA;
    --muted: #9CA8B8;
}

.stApp {
    background:
      radial-gradient(circle at 8% 5%, rgba(255,75,75,.12), transparent 25%),
      radial-gradient(circle at 90% 12%, rgba(0,180,216,.11), transparent 26%),
      radial-gradient(circle at 70% 85%, rgba(155,93,229,.12), transparent 30%),
      linear-gradient(135deg, #0d1117 0%, #161b22 50%, #1a102f 100%);
    color: var(--text);
    font-family: 'Inter', sans-serif;
}

section[data-testid="stSidebar"] {
    background: rgba(22, 27, 34, 0.80);
    border-right: 1px solid rgba(255,255,255,.08);
    position: relative;
}
section[data-testid="stSidebar"]::after {
    content: "";
    position: absolute;
    top: 0; bottom: 0; right: -2px; width: 2px;
    background: linear-gradient(180deg, #FF4B4B, #FF9F1C, #00B4D8, #9B5DE5);
    box-shadow: 0 0 18px rgba(0,180,216,.55);
}

.hero {
    padding: 26px 30px;
    border-radius: 24px;
    margin-bottom: 18px;
    background:
      linear-gradient(135deg, rgba(255,75,75,.13), rgba(0,180,216,.08) 45%, rgba(155,93,229,.13));
    border: 1px solid rgba(255,255,255,.12);
    box-shadow: 0 18px 60px rgba(0,0,0,.28);
    backdrop-filter: blur(12px);
}
.hero h1 {
    margin: 0;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 42px;
    letter-spacing: -1.5px;
}
.hero p {
    color: #C8D1DC;
    margin: 7px 0 0;
    font-size: 16px;
}
.badge {
    display: inline-block;
    margin-top: 15px;
    padding: 7px 12px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: .3px;
    background: rgba(0,180,216,.10);
    border: 1px solid rgba(0,180,216,.35);
    color: #7BE8FF;
    box-shadow: 0 0 18px rgba(0,180,216,.13);
}

.glass {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 18px;
    padding: 18px;
    backdrop-filter: blur(10px);
    box-shadow: 0 12px 40px rgba(0,0,0,.18);
}
.metric-card {
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 18px;
    padding: 18px 20px;
    min-height: 112px;
}
.metric-label {
    color: #9CA8B8;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.metric-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 32px;
    font-weight: 800;
    margin-top: 5px;
}
.metric-sub {
    color: #8995A5;
    font-size: 12px;
    margin-top: 3px;
}

.risk-card {
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 18px;
    padding: 18px;
    margin: 9px 0;
    backdrop-filter: blur(10px);
}
.risk-card.critical { border-left: 4px solid #FF4B4B; box-shadow: -6px 0 24px rgba(255,75,75,.08); }
.risk-card.medium { border-left: 4px solid #FF9F1C; box-shadow: -6px 0 24px rgba(255,159,28,.07); }
.risk-card.low { border-left: 4px solid #00B4D8; }
.risk-card.safe { border-left: 4px solid #00E676; }

.severity {
    font-size: 11px;
    font-weight: 900;
    letter-spacing: .7px;
    padding: 5px 9px;
    border-radius: 999px;
    display: inline-block;
}
.severity.critical { color:#FF7B7B; background:rgba(255,75,75,.11); border:1px solid rgba(255,75,75,.35); }
.severity.medium { color:#FFC46B; background:rgba(255,159,28,.11); border:1px solid rgba(255,159,28,.35); }
.severity.low { color:#72E7FF; background:rgba(0,180,216,.11); border:1px solid rgba(0,180,216,.35); }
.severity.safe { color:#6DFFB2; background:rgba(0,230,118,.10); border:1px solid rgba(0,230,118,.30); }

.section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 22px;
    font-weight: 700;
    margin: 4px 0 12px;
}
.mono {
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

div.stButton > button, div.stDownloadButton > button {
    border-radius: 12px;
    border: 1px solid rgba(0,180,216,.30);
    background: rgba(0,180,216,.07);
    color: #DDFBFF;
    font-weight: 700;
    transition: .2s ease;
}
div.stButton > button:hover, div.stDownloadButton > button:hover {
    border-color: #00B4D8;
    box-shadow: 0 0 22px rgba(0,180,216,.22);
    transform: translateY(-1px);
}
.stProgress > div > div > div > div { background-image: linear-gradient(90deg,#FF4B4B,#FF9F1C,#00E676); }

[data-testid="stChatMessage"] {
    background: rgba(255,255,255,.025);
    border: 1px solid rgba(255,255,255,.07);
    border-radius: 16px;
}
.small-muted { color:#8F9AAA; font-size:12px; }
.warning-box {
    padding: 12px 14px; border-radius: 12px;
    background: rgba(255,159,28,.08);
    border: 1px solid rgba(255,159,28,.25);
    color: #FFD28A;
}
</style>
""",
    unsafe_allow_html=True,
)


# --------------------------- Data model ------------------------

@dataclass
class Risk:
    severity: str
    category: str
    title: str
    clause: str
    explanation: str
    recommendation: str
    section: str
    confidence: int


# ------------------------- Sample contracts --------------------

SAMPLES = {
    "Exploitative NDA": """
MUTUAL CONFIDENTIALITY AGREEMENT

1. Confidential Information
All information disclosed by either party shall be confidential.

2. Term
This Agreement shall remain effective for ten (10) years. Confidentiality obligations survive forever.

3. Remedies
The Receiving Party shall indemnify the Disclosing Party for any and all losses, costs, claims, damages, penalties, attorneys' fees and expenses arising from any disclosure, without limitation.

4. Intellectual Property
All ideas, improvements, suggestions, derivative works, feedback, and inventions disclosed or created during discussions shall belong exclusively to the Disclosing Party.

5. Termination
The Disclosing Party may terminate this Agreement at any time, without notice. The Receiving Party may not terminate this Agreement.

6. Dispute Resolution
Any dispute shall be resolved by binding arbitration in a location selected by the Disclosing Party. The arbitrator's decision shall be final.

7. Data
The Receiving Party may process personal information as reasonably necessary. No separate privacy, security, retention, deletion, or breach-notification requirements apply.
""",
    "Unfair SaaS SLA": """
SOFTWARE-AS-A-SERVICE AGREEMENT

1. Fees
Customer shall pay the fees stated in the Order Form plus any service, platform, processing, support, storage, security, integration, or administrative fees introduced by Provider from time to time.

2. Changes
Provider may change pricing and service terms at any time. Continued use constitutes acceptance.

3. Availability
Provider will use commercially reasonable efforts to provide the service. No uptime commitment, service credit, or measurable performance target is guaranteed.

4. Suspension
Provider may immediately suspend access for any reason, including suspected misuse, without prior notice or cure period.

5. Liability
Customer agrees to indemnify Provider for all claims, losses, damages, costs, and expenses arising out of Customer's use of the service, with no cap.

6. Termination
Provider may terminate immediately for convenience. Customer receives no refund for prepaid fees.

7. Force Majeure
No force majeure provision is provided.

8. Privacy and Security
Provider may process Customer Data as necessary to provide services. No specific breach notification deadline, deletion obligation, or security standard is stated.
""",
    "Vendor Lock-in Contract": """
ENTERPRISE VENDOR SERVICES AGREEMENT

1. Exclusivity
Customer shall purchase all services in the covered category exclusively from Vendor during the Term.

2. Term
The initial term is five years and automatically renews for additional five-year periods unless Customer gives notice at least 180 days before renewal.

3. Exit
Customer may not terminate for convenience. Early termination requires payment of all remaining committed fees.

4. Data Portability
Vendor will provide data exports only in Vendor's proprietary format. No migration assistance is included.

5. Audit
Vendor may audit Customer at any time. Customer has no reciprocal audit right.

6. Liability
Vendor's liability is limited to one month's fees, except Customer's payment and indemnity obligations, which are unlimited.

7. Disputes
Disputes will be handled under laws selected by Vendor in a forum selected by Vendor.

8. Business Continuity
No disaster recovery, business continuity, recovery-time objective, or recovery-point objective is guaranteed.
""",
}


# --------------------------- Utilities --------------------------

def extract_docx(data: bytes) -> str:
    """Extract visible paragraph text from DOCX without requiring python-docx."""
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        xml = z.read("word/document.xml").decode("utf-8", errors="ignore")
    xml = re.sub(r"</w:p>", "\n", xml)
    xml = re.sub(r"<w:tab[^>]*/>", "\t", xml)
    xml = re.sub(r"<[^>]+>", "", xml)
    return html.unescape(xml)


def parse_file(uploaded) -> str:
    name = uploaded.name.lower()
    data = uploaded.getvalue()
    if name.endswith(".pdf"):
        if PdfReader is None:
            raise ValueError("PDF support is unavailable because pypdf is not installed. Please redeploy with the included requirements.txt.")
        reader = PdfReader(io.BytesIO(data))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    if name.endswith(".txt"):
        return data.decode("utf-8", errors="ignore")
    if name.endswith(".docx"):
        return extract_docx(data)
    raise ValueError("Unsupported file type")


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    """Legal-friendly recursive-ish splitter: paragraphs -> sentences -> words."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    pieces = []
    for p in paragraphs:
        if len(p) <= chunk_size:
            pieces.append(p)
            continue
        sentences = re.split(r"(?<=[.!?])\s+", p)
        current = ""
        for sentence in sentences:
            if len(current) + len(sentence) + 1 <= chunk_size:
                current = (current + " " + sentence).strip()
            else:
                if current:
                    pieces.append(current)
                tail = current[-overlap:] if current else ""
                current = (tail + " " + sentence).strip()
        if current:
            pieces.append(current)

    # Final safety pass by characters.
    final = []
    for piece in pieces:
        if len(piece) <= chunk_size:
            final.append(piece)
        else:
            start = 0
            while start < len(piece):
                end = min(len(piece), start + chunk_size)
                final.append(piece[start:end])
                if end == len(piece):
                    break
                start = max(start + 1, end - overlap)
    return final


def sentence_windows(text: str) -> List[str]:
    return [x.strip() for x in re.split(r"(?<=[.!?])\s+", text) if x.strip()]


def section_name(text: str, fallback: str = "Unnumbered clause") -> str:
    m = re.search(r"(?i)\b(?:section|clause|article)?\s*([0-9]+(?:\.[0-9]+)*)\b", text[:160])
    if m:
        return f"Section {m.group(1)}"
    m = re.search(r"(?m)^\s*([0-9]+(?:\.[0-9]+)*)[.)]\s+([^\n]+)", text)
    if m:
        return f"Section {m.group(1)} — {m.group(2).strip()[:80]}"
    return fallback


def quote_from_context(text: str, pattern: str) -> str:
    for sentence in sentence_windows(text):
        if re.search(pattern, sentence, flags=re.I):
            return sentence[:500]
    return text[:500]


# ------------------------- Risk engine --------------------------

def detect_risks(text: str, sensitivity: int = 55) -> List[Risk]:
    risks: List[Risk] = []

    def add(severity, category, title, pattern, explanation, recommendation, confidence=90):
        quote = quote_from_context(text, pattern)
        risks.append(
            Risk(
                severity=severity,
                category=category,
                title=title,
                clause=quote,
                explanation=explanation,
                recommendation=recommendation,
                section=section_name(quote),
                confidence=confidence,
            )
        )

    # 1) Liability poison pills
    if re.search(r"indemnif\w*.*(all|any).*(loss|damage|claim|cost|expense)|without limitation|unlimited indemn", text, re.I | re.S):
        add(
            "Critical", "Liability Poison Pill",
            "Uncapped indemnification exposure",
            r"indemnif\w*|without limitation|unlimited",
            "The clause can shift an open-ended financial risk to one party. A broad indemnity without a cap, exclusions, procedure, or causation standard can become a material balance-sheet liability.",
            "Add a liability cap, mutual indemnity structure, third-party claim procedure, causation threshold, exclusions for the indemnitee's negligence, and a duty to mitigate.",
        )

    if re.search(r"(may|can).{0,40}(terminate|suspend).{0,80}(any time|at any time|for any reason|without notice|immediately)", text, re.I | re.S):
        add(
            "Critical", "Liability Poison Pill",
            "Unilateral termination / suspension power",
            r"(terminate|suspend).{0,100}(any time|for any reason|without notice|immediately)",
            "One-sided exit or suspension rights can let a counterparty disrupt operations before the affected party can cure a breach or transition services.",
            "Require material breach, written notice, a reasonable cure period, emergency exceptions, transition assistance, and refund/credit treatment where appropriate.",
        )

    if re.search(r"(binding arbitration|arbitration).{0,150}(location|forum|selected).{0,80}(party|provider|disclosing|vendor)", text, re.I | re.S):
        add(
            "Critical", "Liability Poison Pill",
            "Forum-controlled arbitration",
            r"(binding arbitration|arbitration).{0,150}(location|forum|selected)",
            "A dispute clause that lets one side select the venue can increase procedural cost and create a home-court advantage.",
            "Specify a neutral venue, governing law, allocation of fees, procedural rules, and a mutually agreed arbitrator-selection mechanism.",
        )

    if re.search(r"(all|any).{0,70}(ideas|feedback|inventions|improvements|derivative works).{0,100}(belong|owned|assign)", text, re.I | re.S):
        add(
            "Critical", "Liability Poison Pill",
            "Broad IP transfer trap",
            r"(ideas|feedback|inventions|improvements|derivative works).{0,100}(belong|owned|assign)",
            "The language may capture pre-existing IP, independently developed materials, feedback, or generalized know-how beyond the intended transaction.",
            "Carve out background IP and independently developed materials; define deliverables precisely; grant only the minimum license or assignment necessary.",
        )

    # 2) Missing safeguards
    if not re.search(r"force majeure|act of god|disaster|unforeseeable", text, re.I):
        add(
            "Medium", "Missing Essential Safeguard",
            "Force majeure protection is missing",
            r"force majeure|act of god|disaster",
            "The agreement does not appear to allocate risk for qualifying events outside a party's reasonable control.",
            "Add a force majeure clause covering qualifying events, notice, mitigation, suspension mechanics, and termination after a defined prolonged period.",
            confidence=96,
        )

    if not re.search(r"privacy|personal data|personal information|gdpr|data protection|data processing", text, re.I):
        add(
            "Medium", "Missing Essential Safeguard",
            "Data privacy protections are missing",
            r"privacy|personal data|personal information|gdpr|data protection",
            "No clear data-protection framework was detected. That can leave roles, processing purposes, security, retention, and incident obligations undefined.",
            "Add data roles, permitted processing, security controls, subprocessors, retention/deletion, data-subject rights, cross-border transfer terms, and incident notification.",
            confidence=97,
        )
    elif not re.search(r"breach.{0,100}(notice|notification)|incident.{0,100}(notice|notification)|notify.{0,60}(breach|incident)", text, re.I | re.S):
        add(
            "Medium", "Missing Essential Safeguard",
            "Security incident notification is unclear",
            r"breach|incident|security",
            "Privacy language exists, but a concrete security-incident notification commitment was not detected.",
            "Define a notification deadline, escalation contact, minimum incident details, cooperation obligations, and update cadence.",
            confidence=82,
        )

    if not re.search(r"cure period|cure.{0,50}(days|day)|remedy.{0,50}(days|day)|written notice.{0,100}(days|day)", text, re.I | re.S):
        add(
            "Medium", "Missing Essential Safeguard",
            "Cure period is missing",
            r"cure|remedy|written notice",
            "A breach may trigger remedies without a defined opportunity to cure. This increases the risk of abrupt termination, suspension, or litigation.",
            "Add written notice and a commercially reasonable cure period, with a shorter emergency window for urgent security or confidentiality breaches.",
            confidence=94,
        )

    # 3) Compliance / regulatory gaps
    if re.search(r"(OWASP|API|application|software|SaaS|platform|security)", text, re.I) and not re.search(
        r"security.{0,100}(standard|control|testing)|penetration test|vulnerability|OWASP|encryption|access control",
        text, re.I | re.S
    ):
        add(
            "Medium", "Regulatory & Compliance Gap",
            "Technical security controls are not measurable",
            r"security|software|SaaS|platform",
            "The document references a technology service but does not appear to bind the provider to concrete security controls or verification rights.",
            "Reference measurable security requirements such as encryption, least privilege, logging, vulnerability management, independent assessments, and remediation SLAs.",
            confidence=79,
        )

    if re.search(r"customer data|personal data|personal information|data", text, re.I) and not re.search(
        r"retain|retention|delete|deletion|return.{0,40}data|return.{0,40}information",
        text, re.I | re.S
    ):
        add(
            "Low", "Regulatory & Compliance Gap",
            "Data lifecycle is undefined",
            r"data|information",
            "The contract discusses data but does not clearly define retention, deletion, or return mechanics.",
            "Specify retention periods, deletion/return at termination, backup treatment, legal-retention exceptions, and certification where appropriate.",
            confidence=78,
        )

    if not re.search(r"notice|written notice|notices", text, re.I):
        add(
            "Low", "Regulatory & Compliance Gap",
            "Formal notice mechanics are missing",
            r"notice|notices",
            "A dispute or breach process can become ambiguous when the agreement does not specify how formal notices must be delivered.",
            "Define permitted delivery methods, notice addresses, effective timing, and contact-update mechanics.",
            confidence=91,
        )

    # Sensitivity: lower threshold means surface more pattern variants.
    if sensitivity < 45 and re.search(r"(automatic|renew|renewal).{0,80}(term|year)", text, re.I | re.S):
        add(
            "Low", "Regulatory & Compliance Gap",
            "Auto-renewal deserves review",
            r"automatic|renew|renewal",
            "Automatic renewal can become a lock-in mechanism when notice windows are long or reminders are absent.",
            "Use a reasonable renewal notice window and require transparent renewal pricing and reminder notices.",
            confidence=73,
        )

    # De-duplicate by title.
    unique = {}
    for r in risks:
        unique[(r.category, r.title)] = r
    risks = list(unique.values())

    sev_order = {"Critical": 0, "Medium": 1, "Low": 2, "Safe": 3}
    return sorted(risks, key=lambda x: (sev_order[x.severity], -x.confidence))


# ---------------------- Local NumPy RAG --------------------------

def _hash_vector(text: str, dim: int = 768) -> np.ndarray:
    """Create a deterministic lightweight text vector without ML packages."""
    vec = np.zeros(dim, dtype=np.float32)
    tokens = re.findall(r"[a-z0-9]{2,}", text.lower())
    if not tokens:
        return vec
    for token in tokens:
        idx = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16) % dim
        vec[idx] += 1.0
    norm = np.linalg.norm(vec)
    if norm:
        vec /= norm
    return vec


@st.cache_data(show_spinner=False)
def build_vector_store(chunks: Tuple[str, ...]):
    """Build a dependency-light local vector store using only NumPy."""
    return np.vstack([_hash_vector(chunk) for chunk in chunks]) if chunks else np.empty((0, 768), dtype=np.float32)


def retrieve(query: str, chunks: List[str], k: int = 4) -> List[Tuple[str, float]]:
    if not chunks:
        return []
    vectors = build_vector_store(tuple(chunks))
    q = _hash_vector(query)
    scores = vectors @ q
    limit = min(k, len(chunks))
    ids = np.argsort(scores)[::-1][:limit]
    return [(chunks[int(i)], float(scores[int(i)])) for i in ids]

def deterministic_adversarial_answer(query: str, contexts: List[Tuple[str, float]], risks: List[Risk]) -> str:
    q = query.lower()
    matched = []

    for risk in risks:
        terms = re.findall(r"[a-zA-Z]{5,}", risk.title.lower())
        overlap = sum(1 for t in terms if t in q)
        if overlap:
            matched.append((overlap, risk))

    matched.sort(key=lambda x: -x[0])

    lines = [
        "### Red-Team Assessment",
        "",
        "I am treating the prompt as an adversarial contract test, not as legal advice.",
    ]

    if matched:
        risk = matched[0][1]
        lines += [
            "",
            f"**Most relevant finding:** {risk.title} — **{risk.severity}**",
            f"> {risk.clause}",
            "",
            f"**Attack surface:** {risk.explanation}",
            "",
            f"**Defensive fix:** {risk.recommendation}",
            "",
            f"**Citation:** {risk.section}",
        ]
    elif contexts:
        best = contexts[0][0]
        lines += [
            "",
            "**Relevant retrieved context:**",
            f"> {best[:900]}",
            "",
            "The local RAG index found the above clause context. A real red-team review should map the scenario to definitions, exceptions, remedies, and termination mechanics elsewhere in the agreement.",
        ]
    else:
        lines += ["", "No relevant document context was available."]

    if any(x in q for x in ["hidden fee", "charge", "pricing", "fee"]):
        lines += [
            "",
            "**Fee-abuse test:** check whether the agreement allows new fees by unilateral notice, incorporates external pricing pages, or makes continued use equal acceptance.",
        ]
    if any(x in q for x in ["terminate", "termination", "suspend"]):
        lines += [
            "",
            "**Exit-abuse test:** check who controls termination, whether notice is required, whether there is a cure period, and what happens to prepaid amounts and customer data.",
        ]
    if any(x in q for x in ["data", "privacy", "gdpr", "breach"]):
        lines += [
            "",
            "**Data-abuse test:** check purpose limitation, subprocessors, security controls, incident notice, retention/deletion, and cross-border transfer language.",
        ]

    return "\n".join(lines)


# ----------------------- Scoring / exports ----------------------

def calculate_scores(risks: List[Risk], text: str) -> Dict[str, int]:
    critical = sum(r.severity == "Critical" for r in risks)
    medium = sum(r.severity == "Medium" for r in risks)
    low = sum(r.severity == "Low" for r in risks)

    risk_score = min(100, critical * 24 + medium * 11 + low * 4)
    # Penalize documents with no risk findings less aggressively.
    if len(text) < 250:
        risk_score = min(100, risk_score + 10)

    safeguard_terms = ["force majeure", "privacy", "data", "cure", "termination", "liability", "notice"]
    present = sum(bool(re.search(term, text, re.I)) for term in safeguard_terms)
    enforceability = max(0, min(100, 45 + present * 8 - critical * 7 - medium * 3))
    enforceability = int(enforceability)

    return {
        "risk": int(risk_score),
        "enforceability": enforceability,
        "red_flags": critical + medium,
        "missing_safeguards": sum("Missing Essential Safeguard" in r.category for r in risks),
    }


def build_report(doc_name: str, text: str, risks: List[Risk], scores: Dict[str, int]) -> str:
    lines = [
        "# 🛡️ DocuMind Red-Teamer — Executive Audit Report",
        "",
        f"**Document:** {doc_name}",
        f"**Risk Score:** {scores['risk']}/100",
        f"**Enforceability Score:** {scores['enforceability']}/100",
        f"**Red Flags:** {scores['red_flags']}",
        f"**Missing Safeguards:** {scores['missing_safeguards']}",
        "",
        "> Automated red-team screening. Not legal advice. Findings require review by qualified counsel.",
        "",
        "## Executive Summary",
        "",
        "DocuMind Red-Teamer adversarially screened the document for liability poison pills, missing safeguards, compliance gaps, and exploitable contract mechanics.",
        "",
        "## Findings",
        "",
    ]
    for i, r in enumerate(risks, 1):
        lines += [
            f"### {i}. [{r.severity}] {r.title}",
            f"**Category:** {r.category}",
            f"**Section:** {r.section}",
            "",
            f"**Clause:** {r.clause}",
            "",
            f"**Threat:** {r.explanation}",
            "",
            f"**Recommended counter-clause:** {r.recommendation}",
            "",
        ]
    lines += [
        "## Top Red-Team Questions",
        "",
        "- Can the counterparty change price, scope, or service terms unilaterally?",
        "- Can the counterparty terminate or suspend without notice or cure?",
        "- Are indemnities and liability exceptions capped and reciprocal?",
        "- Who owns background IP, feedback, improvements, and independently developed work?",
        "- What happens to data, access, and prepaid fees after termination?",
        "",
        "## Document Snapshot",
        "",
        f"- Characters analyzed: {len(text):,}",
        f"- Risk findings: {len(risks)}",
        "- Retrieval: local FAISS semantic index",
        "- Embedding model: sentence-transformers / all-MiniLM-L6-v2",
    ]
    return "\n".join(lines)


def simple_pdf_bytes(report: str) -> bytes:
    """Create a dependency-light PDF with reportlab when available."""
    from reportlab.lib.pagesizes import LETTER
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib import colors

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        rightMargin=42,
        leftMargin=42,
        topMargin=42,
        bottomMargin=42,
        title="DocuMind Red-Teamer Executive Audit",
    )
    styles = getSampleStyleSheet()
    styles["Title"].textColor = colors.HexColor("#0d1117")
    styles["Heading2"].textColor = colors.HexColor("#8A2BE2")
    story = []
    for block in report.split("\n\n"):
        if block.startswith("# "):
            story.append(Paragraph(html.escape(block[2:]), styles["Title"]))
        elif block.startswith("## "):
            story.append(Paragraph(html.escape(block[3:]), styles["Heading2"]))
        elif block.startswith("### "):
            story.append(Paragraph(html.escape(block[4:]), styles["Heading3"]))
        else:
            safe = html.escape(block).replace("\n", "<br/>")
            story.append(Paragraph(safe, styles["BodyText"]))
        story.append(Spacer(1, 8))
    doc.build(story)
    return buffer.getvalue()


# -------------------------- Session state -----------------------

if "doc_text" not in st.session_state:
    st.session_state.doc_text = ""
if "doc_name" not in st.session_state:
    st.session_state.doc_name = ""
if "chat" not in st.session_state:
    st.session_state.chat = []
if "sample_loaded" not in st.session_state:
    st.session_state.sample_loaded = False


# ------------------------------ Header --------------------------

st.markdown(
    """
<div class="hero">
  <h1>🛡️ DocuMind Red-Teamer</h1>
  <p>Red-teaming legal contracts before your opponent does.</p>
  <span class="badge">● LOCAL RAG ONLINE &nbsp; • &nbsp; FAISS INDEX READY &nbsp; • &nbsp; SECURITY-FIRST MODE</span>
</div>
""",
    unsafe_allow_html=True,
)

# ----------------------------- Sidebar --------------------------

with st.sidebar:
    st.markdown("## ⚙️ Red-Team Console")
    st.caption("Upload a contract or launch a vulnerable sample in one click.")

    uploaded = st.file_uploader(
        "Contract / policy",
        type=["pdf", "txt", "docx"],
        help="Supported: PDF, TXT and DOCX.",
    )

    st.markdown("### ⚡ One-click attack targets")
    for sample_name in SAMPLES:
        if st.button(sample_name, use_container_width=True, key=f"sample_{sample_name}"):
            st.session_state.doc_text = clean_text(SAMPLES[sample_name])
            st.session_state.doc_name = sample_name
            st.session_state.sample_loaded = True
            st.session_state.chat = []
            st.rerun()

    if uploaded is not None:
        try:
            parsed = clean_text(parse_file(uploaded))
            st.session_state.doc_text = parsed
            st.session_state.doc_name = uploaded.name
            st.session_state.sample_loaded = False
            st.session_state.chat = []
        except Exception as exc:
            st.error(f"Could not parse document: {exc}")

    st.markdown("---")
    st.markdown("### 🎚️ Scan controls")
    sensitivity = st.slider(
        "Risk sensitivity",
        min_value=20,
        max_value=90,
        value=55,
        step=5,
        help="Higher values prioritize stronger signals; lower values surface more exploratory findings.",
    )

    categories = st.multiselect(
        "Threat categories",
        [
            "Liability Poison Pill",
            "Missing Essential Safeguard",
            "Regulatory & Compliance Gap",
        ],
        default=[
            "Liability Poison Pill",
            "Missing Essential Safeguard",
            "Regulatory & Compliance Gap",
        ],
    )

    st.markdown("---")
    st.markdown(
        '<div class="small-muted">⚠️ Automated screening only. This prototype does not provide legal advice or replace counsel.</div>',
        unsafe_allow_html=True,
    )

# -------------------------- Empty state -------------------------

if not st.session_state.doc_text:
    st.markdown(
        """
<div class="glass">
  <div class="section-title">🚀 Launch an adversarial audit</div>
  <p style="color:#AAB5C4">
    Upload a PDF/TXT/DOCX or choose a pre-built vulnerable contract from the sidebar.
    The local engine extracts clauses, creates 800-character chunks with 100-character overlap,
    indexes them in a lightweight local NumPy vector store, and runs deterministic legal red-team detectors.
  </p>
  <div class="warning-box">Judge demo tip: start with <b>Exploitative NDA</b> for an instant visible threat scorecard.</div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.stop()

# ------------------------- Run analysis -------------------------

with st.spinner("Building local vector context + running red-team detectors..."):
    chunks = split_text(st.session_state.doc_text, 800, 100)
    all_risks = detect_risks(st.session_state.doc_text, sensitivity)
    risks = [r for r in all_risks if r.category in categories]
    scores = calculate_scores(risks, st.session_state.doc_text)

# Build FAISS lazily but show status.
try:
    _ = build_vector_store(tuple(chunks))
    rag_status = "LOCAL VECTOR ONLINE"
except Exception as exc:
    rag_status = f"VECTOR ERROR: {str(exc)[:45]}"

st.markdown(
    f'<div class="glass" style="margin-bottom:14px"><b>📄 {html.escape(st.session_state.doc_name)}</b>'
    f' &nbsp; <span class="small-muted">• {len(st.session_state.doc_text):,} chars • {len(chunks)} legal chunks • {rag_status}</span></div>',
    unsafe_allow_html=True,
)

# ------------------------------- Tabs ---------------------------

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📊 Executive Audit Dashboard",
        "🔍 Vulnerability Matrix & Context",
        "⚔️ Adversarial Simulator",
        "📜 Raw Document & Vector Chunks",
    ]
)

# ============================ TAB 1 =============================

with tab1:
    st.markdown('<div class="section-title">Executive Threat Scorecard</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    risk_color = "#00E676" if scores["risk"] < 30 else "#FF9F1C" if scores["risk"] < 65 else "#FF4B4B"
    enforce_color = "#FF4B4B" if scores["enforceability"] < 45 else "#FF9F1C" if scores["enforceability"] < 70 else "#00E676"

    with c1:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Threat Score</div>'
            f'<div class="metric-value" style="color:{risk_color}">{scores["risk"]}/100</div>'
            f'<div class="metric-sub">Higher = more exploitable</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Red Flags</div>'
            f'<div class="metric-value" style="color:#FF4B4B">{scores["red_flags"]}</div>'
            f'<div class="metric-sub">Critical + medium findings</div></div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Missing Safeguards</div>'
            f'<div class="metric-value" style="color:#FF9F1C">{scores["missing_safeguards"]}</div>'
            f'<div class="metric-sub">Protection gaps detected</div></div>',
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Enforceability</div>'
            f'<div class="metric-value" style="color:{enforce_color}">{scores["enforceability"]}/100</div>'
            f'<div class="metric-sub">Heuristic contract health</div></div>',
            unsafe_allow_html=True,
        )

    st.write("")
    left, right = st.columns([1.15, 1])

    with left:
        st.markdown(
            '<div class="glass"><div class="section-title">📊 Severity Breakdown</div>',
            unsafe_allow_html=True,
        )
        critical_count = sum(r.severity.lower() == "critical" for r in risks)
        medium_count = sum(r.severity.lower() == "medium" for r in risks)
        low_count = sum(r.severity.lower() == "low" for r in risks)
        total = max(1, len(risks))

        severity_rows = [
            ("🔴 Critical", critical_count, "#FF4B4B"),
            ("🟠 Medium", medium_count, "#FF9F1C"),
            ("🟢 Low", low_count, "#00E676"),
        ]

        for label, count, bar_color in severity_rows:
            pct = (count / total) * 100
            st.markdown(
                f"""
                <div style="display:flex;justify-content:space-between;margin-top:14px;">
                    <span><b>{label}</b></span><span>{count}</span>
                </div>
                <div style="height:10px;background:rgba(255,255,255,.08);border-radius:8px;margin:6px 0 10px;">
                    <div style="height:10px;width:{pct:.1f}%;background:{bar_color};border-radius:8px;"></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="glass"><div class="section-title">🎯 Top deal-breakers</div>', unsafe_allow_html=True)
        if risks:
            for r in risks[:3]:
                cls = r.severity.lower()
                st.markdown(
                    f'<div class="risk-card {cls}"><span class="severity {cls}">{r.severity.upper()}</span>'
                    f'<b style="margin-left:8px">{html.escape(r.title)}</b>'
                    f'<div class="small-muted" style="margin-top:7px">{html.escape(r.explanation[:230])}...</div></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.success("No selected-category vulnerabilities were detected.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 🔥 Recommended first moves")
    recs = []
    for r in risks[:5]:
        recs.append(f"**{r.title}:** {r.recommendation}")
    if recs:
        for rec in recs:
            st.markdown(f"- {rec}")
    else:
        st.info("No recommendations generated for the selected categories.")

    report = build_report(st.session_state.doc_name, st.session_state.doc_text, risks, scores)
    pdf = simple_pdf_bytes(report)
    d1, d2 = st.columns(2)
    with d1:
        st.download_button(
            "⬇️ Download Executive Markdown",
            data=report,
            file_name="documind_executive_audit.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with d2:
        st.download_button(
            "⬇️ Download Executive PDF",
            data=pdf,
            file_name="documind_executive_audit.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

# ============================ TAB 2 =============================

with tab2:
    st.markdown('<div class="section-title">Vulnerability Matrix</div>', unsafe_allow_html=True)

    if not risks:
        st.success("No findings match the current filters.")
    else:
        for i, r in enumerate(risks, 1):
            cls = r.severity.lower()
            with st.expander(f"{r.severity}  •  {r.category}  •  {r.title}", expanded=(i <= 2)):
                st.markdown(
                    f'<div class="risk-card {cls}"><span class="severity {cls}">{r.severity.upper()}</span>'
                    f'<span class="small-muted" style="margin-left:8px">Confidence {r.confidence}%</span></div>',
                    unsafe_allow_html=True,
                )
                a, b = st.columns(2)
                with a:
                    st.markdown("**📌 Exact clause / context**")
                    st.code(r.clause, language="text")
                    st.markdown(f"**Section:** `{r.section}`")
                with b:
                    st.markdown("**⚔️ Why an adversary cares**")
                    st.write(r.explanation)
                    st.markdown("**🛡️ Recommended counter-clause / redline direction**")
                    st.success(r.recommendation)

# ============================ TAB 3 =============================

with tab3:
    st.markdown('<div class="section-title">Adversarial Scenario Simulator</div>', unsafe_allow_html=True)
    st.caption("Ask how a clause could be abused. Responses are grounded in the local semantic retrieval index and detected findings.")

    quick_prompts = [
        "How could a vendor exploit the contract to charge hidden fees?",
        "How could the counterparty terminate or suspend service unfairly?",
        "What is the biggest IP ownership trap?",
        "How could a data breach become a liability gap?",
    ]

    qcols = st.columns(4)
    for idx, prompt in enumerate(quick_prompts):
        with qcols[idx]:
            if st.button(prompt, key=f"qp_{idx}", use_container_width=True):
                st.session_state.chat.append(("user", prompt))
                contexts = retrieve(prompt, chunks, 4)
                answer = deterministic_adversarial_answer(prompt, contexts, risks)
                st.session_state.chat.append(("assistant", answer))
                st.rerun()

    for role, message in st.session_state.chat:
        with st.chat_message(role):
            st.markdown(message)

    prompt = st.chat_input("e.g. How can a vendor exploit Section 4 to charge hidden fees?")
    if prompt:
        st.session_state.chat.append(("user", prompt))
        with st.spinner("Retrieving adversarial context..."):
            contexts = retrieve(prompt, chunks, 4)
            answer = deterministic_adversarial_answer(prompt, contexts, risks)
        st.session_state.chat.append(("assistant", answer))
        st.rerun()

# ============================ TAB 4 =============================

with tab4:
    st.markdown('<div class="section-title">Transparency Layer</div>', unsafe_allow_html=True)
    st.caption("Judge/debug mode: inspect extracted text and the exact semantic chunks indexed by the local vector retrieval backend.")

    r1, r2 = st.columns(2)
    with r1:
        st.markdown("**📜 Extracted document text**")
        st.text_area(
            "raw",
            st.session_state.doc_text,
            height=520,
            label_visibility="collapsed",
        )
    with r2:
        st.markdown(f"**🧩 Vector chunks ({len(chunks)})**")
        for i, chunk in enumerate(chunks):
            with st.expander(f"Chunk {i+1}", expanded=False):
                st.code(chunk, language="text")

    st.markdown("---")
    st.markdown("**Engine metadata**")
    metadata = {
        "document": st.session_state.doc_name,
        "chunk_size": 800,
        "chunk_overlap": 100,
        "vector_index": "NumPy hashed-vector cosine retrieval",
        "embedding_model": "None (dependency-light local retrieval)",
        "risk_modules": [
            "Liability Poison Pills",
            "Missing Essential Safeguards",
            "Regulatory & Compliance Gaps",
            "Adversarial Scenario Simulator",
        ],
    }
    st.json(metadata)
