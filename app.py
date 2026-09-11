import os
import io
import json
import streamlit as st

# Safe import for Plotly to prevent hard app crashes on Streamlit Cloud
try:
    import plotly.graph_objects as go
    import plotly.express as px
    HAS_PLOTLY = True
except ModuleNotFoundError:
    HAS_PLOTLY = False

# PDF Processing
import pdfplumber
from pypdf import PdfReader

# LangChain & Vector Store
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Optional Groq Support
try:
    from langchain_groq import ChatGroq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

# ------------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & SESSION STATE INITIALIZATION
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="DocuMind Red-Teamer | Legal Contract Vulnerability Agent",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session States
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "contract_text" not in st.session_state:
    st.session_state.contract_text = ""
if "redteam_results" not in st.session_state:
    st.session_state.redteam_results = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "processed_filename" not in st.session_state:
    st.session_state.processed_filename = None

# Missing module alert for user guidance
if not HAS_PLOTLY:
    st.error("⚠️ `plotly` package is missing in your deployment environment! Please add `plotly` to your `requirements.txt` file and reboot the Streamlit Cloud app.")

# ------------------------------------------------------------------------------
# 2. CUSTOM CSS STYLING
# ------------------------------------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #111827 100%);
        color: #f8fafc;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(12px);
        border-radius: 12px;
        border: 1px solid rgba(99, 102, 241, 0.2);
        padding: 1rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    section[data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.95);
        border-right: 1px solid rgba(99, 102, 241, 0.2);
    }
    div[data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 10px;
        padding: 12px 16px;
    }
    .badge-critical {
        background-color: rgba(239, 68, 68, 0.2);
        color: #fca5a5;
        border: 1px solid #ef4444;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-block;
    }
    .badge-warning {
        background-color: rgba(245, 158, 11, 0.2);
        color: #fde047;
        border: 1px solid #f59e0b;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-block;
    }
    .badge-safe {
        background-color: rgba(16, 185, 129, 0.2);
        color: #6ee7b7;
        border: 1px solid #10b981;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-block;
    }
    .clause-box-original {
        background: rgba(239, 68, 68, 0.08);
        border-left: 4px solid #ef4444;
        padding: 12px;
        border-radius: 4px;
        font-size: 0.9rem;
        color: #e2e8f0;
        margin-bottom: 10px;
    }
    .clause-box-exploit {
        background: rgba(245, 158, 11, 0.08);
        border-left: 4px solid #f59e0b;
        padding: 12px;
        border-radius: 4px;
        font-size: 0.9rem;
        color: #e2e8f0;
        margin-bottom: 10px;
    }
    .clause-box-redline {
        background: rgba(16, 185, 129, 0.08);
        border-left: 4px solid #10b981;
        padding: 12px;
        border-radius: 4px;
        font-size: 0.9rem;
        color: #e2e8f0;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 3. SAMPLE CONTRACT DATA
# ------------------------------------------------------------------------------
SAMPLE_SAAS_CONTRACT = """MASTER SERVICES AGREEMENT

This Master Services Agreement ("Agreement") is entered into by and between CloudScale Systems Inc. ("Provider") and the customer agreeing to these terms ("Client").

1. INDEMNIFICATION AND LIABILITY TRAPS
Client agrees to defend, indemnify, and hold harmless Provider, its officers, directors, and employees from and against any and all claims, damages, liabilities, losses, costs, and expenses (including attorneys' fees) arising out of or related to Client's use of the Services, regardless of whether caused by Provider's negligence or willful misconduct. PROVIDER'S TOTAL AGGREGATE LIABILITY ARISING OUT OF OR RELATED TO THIS AGREEMENT SHALL BE LIMITED TO $100. PROVIDER SHALL NOT BE LIABLE FOR ANY INDIRECT, CONSEQUENTIAL, OR SPECIAL DAMAGES UNDER ANY CIRCUMSTANCES.

2. INTELLECTUAL PROPERTY RIGHTS & OWNERSHIP LEAKAGE
All deliverables, custom code, workflows, inventions, modifications, and enhancements developed or created by Provider or Client during the term of this Agreement shall be the sole and exclusive property of Provider. Client hereby assigns all right, title, and interest in any intellectual property created during the performance of this agreement to Provider, including proprietary Client business data embedded within custom models.

3. TERMINATION AND RENEWAL HAZARDS
This Agreement shall automatically renew for successive 3-year terms unless Client provides written notice of non-renewal at least 180 days prior to the expiration of the then-current term. Provider may terminate this Agreement immediately for convenience without notice and without refund of any prepaid fees. In the event of Client's termination, all remaining unpaid fees for the full term shall become immediately due and payable.

4. JURISDICTION, DISPUTE RESOLUTION, AND AMBIGUITY
This Agreement shall be governed by and construed in accordance with the laws of the Cayman Islands, without regard to conflict of law principles. Any dispute arising out of or in connection with this Agreement shall be settled by binding arbitration in London, UK, conducted in English. Client waives any right to jury trial or participation in class actions. Fees for arbitration shall be split equally, and the prevailing party shall not be entitled to recover legal fees.
"""

# ------------------------------------------------------------------------------
# 4. HELPER FUNCTIONS & RAG PIPELINE
# ------------------------------------------------------------------------------
def extract_text_from_pdf(pdf_file) -> str:
    text = ""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception:
        pdf_file.seek(0)
        reader = PdfReader(pdf_file)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    return text

def build_vector_store(text: str, openai_api_key: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_text(text)
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    vectorstore = FAISS.from_texts(texts=chunks, embedding=embeddings)
    return vectorstore

def get_llm_instance(provider: str, api_key: str):
    if provider == "Groq" and HAS_GROQ:
        return ChatGroq(
            model_name="llama-3.3-70b-versatile",
            groq_api_key=api_key,
            temperature=0.1,
            model_kwargs={"response_format": {"type": "json_object"}}
        )
    else:
        return ChatOpenAI(
            model="gpt-4o",
            temperature=0.1,
            openai_api_key=api_key,
            response_format={"type": "json_object"}
        )

def run_red_team_analysis(vectorstore: FAISS, contract_type: str, risk_tolerance: str, provider: str, api_key: str):
    llm = get_llm_instance(provider, api_key)
    
    categories = [
        "Indemnification & Liability Traps",
        "IP Ownership Leakage",
        "Termination & Renewal Hazards",
        "Jurisdiction & Dispute Ambiguities"
    ]
    
    analysis_results = {
        "overall_risk_score": 0,
        "summary": "",
        "categories": {}
    }
    
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    
    prompt_template = ChatPromptTemplate.from_template("""
    You are an expert Legal Red-Teamer and Senior Corporate Counsel performing adversarial analysis on a contract.
    Analyze the provided legal text excerpts specifically for vulnerabilities, traps, and high-risk terms related to: **{category}**.
    
    Contract Type: {contract_type}
    Risk Tolerance Level: {risk_tolerance}
    
    Contract Excerpts:
    {context}
    
    Respond in strict JSON format with the following structure:
    {{
      "category_risk_score": <number between 0 and 100 representing risk level>,
      "findings": [
        {{
          "severity": "CRITICAL" | "WARNING" | "LOW RISK",
          "title": "<Brief title of issue>",
          "original_clause": "<Exact quote or near-quote from contract>",
          "exploit_analysis": "<Detailed explanation of how the counterparty could abuse or exploit this clause>",
          "recommended_redline": "<Specific, ready-to-use amended text that protects our client>"
        }}
      ]
    }}
    """)
    
    total_score = 0
    category_count = 0

    for category in categories:
        docs = retriever.invoke(category)
        context = "\n\n".join([doc.page_content for doc in docs])
        
        chain = prompt_template | llm | StrOutputParser()
        raw_response = chain.invoke({
            "category": category,
            "contract_type": contract_type,
            "risk_tolerance": risk_tolerance,
            "context": context
        })
        
        try:
            parsed = json.loads(raw_response)
            analysis_results["categories"][category] = parsed
            total_score += parsed.get("category_risk_score", 50)
            category_count += 1
        except Exception:
            analysis_results["categories"][category] = {
                "category_risk_score": 60,
                "findings": [{
                    "severity": "WARNING",
                    "title": f"Potential risk identified in {category}",
                    "original_clause": "Refer to context clauses.",
                    "exploit_analysis": "Ambiguous terms may expose your organization to liabilities.",
                    "recommended_redline": "Insert mutual liability protections and standard caps."
                }]
            }
            total_score += 60
            category_count += 1

    overall_score = min(100, max(0, int(total_score / max(1, category_count))))
    analysis_results["overall_risk_score"] = overall_score
    
    if overall_score >= 70:
        analysis_results["summary"] = "CRITICAL RISK PROFILE: Severe unilateral indemnities, potential IP loss, and aggressive renewal clauses detected."
    elif overall_score >= 40:
        analysis_results["summary"] = "MODERATE RISK PROFILE: Noticeable imbalances, missing liability caps, or unfavorable dispute terms present."
    else:
        analysis_results["summary"] = "LOW RISK PROFILE: Contract terms are largely standard and balanced."
        
    return analysis_results

def answer_rag_question(query: str, vectorstore: FAISS, provider: str, api_key: str) -> str:
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    docs = retriever.invoke(query)
    context = "\n\n".join([doc.page_content for doc in docs])
    
    prompt = ChatPromptTemplate.from_template("""
    You are DocuMind Red-Teamer, an AI legal expert assistant. Answer the user's question based strictly on the provided contract context.
    
    Contract Context:
    {context}
    
    User Question: {question}
    
    Answer clearly and concisely:
    """)
    
    if provider == "Groq" and HAS_GROQ:
        llm = ChatGroq(model_name="llama-3.3-70b-versatile", groq_api_key=api_key, temperature=0.2)
    else:
        llm = ChatOpenAI(model="gpt-4o", temperature=0.2, openai_api_key=api_key)
        
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"context": context, "question": query})

# ------------------------------------------------------------------------------
# 5. SIDEBAR CONTROLS
# ------------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚖️🛡️ DocuMind Red-Teamer")
    st.markdown("*Adversarial Contract Vulnerability Scanner*")
    st.divider()

    provider_choice = st.radio("LLM Provider", ["OpenAI", "Groq"])

    # Fetch keys from st.secrets or env variables automatically
    default_openai_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY", "")
    default_groq_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY", "")

    if provider_choice == "OpenAI":
        api_key = st.text_input("OpenAI API Key", value=default_openai_key, type="password")
    else:
        api_key = st.text_input("Groq API Key", value=default_groq_key, type="password")
        # OpenAI key needed for vector embeddings
        openai_embed_key = st.text_input("OpenAI Key (for Embeddings)", value=default_openai_key, type="password")

    st.divider()
    st.markdown("### ⚙️ Parameters")
    contract_type = st.selectbox(
        "Contract Category",
        ["SaaS Agreement / MSA", "Non-Disclosure Agreement (NDA)", "Employment Agreement", "Vendor/Procurement Contract", "M&A / Asset Purchase"]
    )
    
    risk_tolerance = st.select_slider(
        "Risk Tolerance",
        options=["Strict (Protect Us)", "Moderate (Balanced)", "Aggressive (Deal-First)"],
        value="Strict (Protect Us)"
    )

    st.divider()
    if st.button("⚡ Load Sample SaaS Contract"):
        st.session_state.contract_text = SAMPLE_SAAS_CONTRACT
        st.session_state.processed_filename = "Sample_SaaS_Master_Agreement.txt"
        st.success("Loaded Sample Contract!")

# ------------------------------------------------------------------------------
# 6. MAIN INTERFACE
# ------------------------------------------------------------------------------
st.markdown("""
<div style="display: flex; align-items: center; justify-content: space-between; padding-bottom: 10px;">
    <div>
        <h1 style="margin: 0; color: #f8fafc; font-size: 2.2rem; font-weight: 800;">DocuMind Red-Teamer</h1>
        <p style="color: #94a3b8; font-size: 1.05rem; margin-top: 4px;">Expose legal traps and contract vulnerabilities before signing.</p>
    </div>
    <div>
        <span class="badge-critical" style="font-size: 0.85rem; padding: 6px 14px;">AI Red-Teamer Active</span>
    </div>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload Legal Document (.pdf, .txt)", type=["pdf", "txt"])

if uploaded_file is not None and uploaded_file.name != st.session_state.processed_filename:
    if uploaded_file.type == "application/pdf":
        st.session_state.contract_text = extract_text_from_pdf(uploaded_file)
    else:
        st.session_state.contract_text = uploaded_file.read().decode("utf-8")
    st.session_state.processed_filename = uploaded_file.name
    st.session_state.redteam_results = None

if st.session_state.contract_text:
    st.info(f"📄 Active Document: **{st.session_state.processed_filename or 'Loaded Document'}** ({len(st.session_state.contract_text)} characters)")
    
    if st.button("🔍 Execute Red-Team Vulnerability Scan"):
        embed_key = openai_embed_key if provider_choice == "Groq" else api_key
        if not api_key or not embed_key:
            st.error("Please enter the required API Key(s) in the sidebar.")
        else:
            with st.spinner("Indexing text and running Red-Team Agent..."):
                try:
                    vstore = build_vector_store(st.session_state.contract_text, embed_key)
                    st.session_state.vectorstore = vstore
                    
                    results = run_red_team_analysis(vstore, contract_type, risk_tolerance, provider_choice, api_key)
                    st.session_state.redteam_results = results
                    st.success("Analysis Complete!")
                except Exception as e:
                    st.error(f"Execution Error: {str(e)}")

# ------------------------------------------------------------------------------
# 7. DASHBOARD & TABS
# ------------------------------------------------------------------------------
if st.session_state.redteam_results is not None:
    results = st.session_state.redteam_results
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Executive Risk Scorecard",
        "🔴 Vulnerability Matrix",
        "💬 Ask the Red-Teamer",
        "📥 Audit Report Export"
    ])

    with tab1:
        col_gauge, col_metrics = st.columns([1, 1])
        score = results["overall_risk_score"]
        
        with col_gauge:
            if HAS_PLOTLY:
                gauge_fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=score,
                    title={'text': "Composite Risk Score", 'font': {'size': 18, 'color': '#f8fafc'}},
                    number={'font': {'size': 48, 'color': '#ef4444' if score >= 70 else '#f59e0b' if score >= 40 else '#10b981'}},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "#ef4444" if score >= 70 else "#f59e0b" if score >= 40 else "#10b981"},
                        'steps': [
                            {'range': [0, 40], 'color': 'rgba(16, 185, 129, 0.2)'},
                            {'range': [40, 70], 'color': 'rgba(245, 158, 11, 0.2)'},
                            {'range': [70, 100], 'color': 'rgba(239, 68, 68, 0.2)'}
                        ],
                    }
                ))
                gauge_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': "#f8fafc"}, height=280)
                st.plotly_chart(gauge_fig, use_container_width=True)
            else:
                st.metric("Composite Risk Score", f"{score}/100")

        with col_metrics:
            st.markdown("### Executive Findings")
            st.markdown(f"> **Assessment:** {results['summary']}")
            
            m1, m2, m3 = st.columns(3)
            crit_count = sum(1 for c in results["categories"].values() for f in c.get("findings", []) if f.get("severity") == "CRITICAL")
            warn_count = sum(1 for c in results["categories"].values() for f in c.get("findings", []) if f.get("severity") == "WARNING")
            safe_count = sum(1 for c in results["categories"].values() for f in c.get("findings", []) if f.get("severity") == "LOW RISK")
            
            m1.metric("Critical Traps", f"{crit_count}")
            m2.metric("Warnings", f"{warn_count}")
            m3.metric("Low Risk Items", f"{safe_count}")

    with tab2:
        for cat_name, cat_data in results["categories"].items():
            st.markdown(f"#### {cat_name} (Risk Score: `{cat_data.get('category_risk_score', 0)}/100`)")
            for finding in cat_data.get("findings", []):
                severity = finding.get("severity", "WARNING")
                with st.expander(f"[{severity}] {finding.get('title', 'Risk Item')}"):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("**Original Clause:**")
                        st.markdown(f'<div class="clause-box-original">{finding.get("original_clause", "N/A")}</div>', unsafe_allow_html=True)
                        st.markdown("**Exploit Analysis:**")
                        st.markdown(f'<div class="clause-box-exploit">{finding.get("exploit_analysis", "N/A")}</div>', unsafe_allow_html=True)
                    with c2:
                        st.markdown("**Recommended Redline:**")
                        st.markdown(f'<div class="clause-box-redline">{finding.get("recommended_redline", "N/A")}</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown("### Ask Questions About This Contract")
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        user_input = st.chat_input("Ask a question...")
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)

            with st.chat_message("assistant"):
                if st.session_state.vectorstore and api_key:
                    bot_response = answer_rag_question(user_input, st.session_state.vectorstore, provider_choice, api_key)
                else:
                    bot_response = "Please run the scan first."
                st.write(bot_response)
                st.session_state.chat_history.append({"role": "assistant", "content": bot_response})

    with tab4:
        report_md = f"# RED-TEAM AUDIT REPORT\n\nScore: {results['overall_risk_score']}/100\nSummary: {results['summary']}\n\n"
        for cat_name, cat_data in results["categories"].items():
            report_md += f"## {cat_name}\n Score: {cat_data.get('category_risk_score', 0)}/100\n"
            for f in cat_data.get("findings", []):
                report_md += f"### [{f.get('severity')}] {f.get('title')}\n- Clause: {f.get('original_clause')}\n- Exploit: {f.get('exploit_analysis')}\n- Redline: {f.get('recommended_redline')}\n\n"
        
        st.download_button(
            label="📥 Download Audit Report (.md)",
            data=report_md,
            file_name="DocuMind_RedTeam_Report.md",
            mime="text/markdown"
        )
