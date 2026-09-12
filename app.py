import streamlit as st
import time

# ----------------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="DocuMind Red-Teamer",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "active_page" not in st.session_state:
    st.session_state.active_page = "Home"

NAV_ITEMS = [
    ("Home", "fa-house"),
    ("Upload Contract", "fa-file-lines"),
    ("Scan & Analyze", "fa-magnifying-glass"),
    ("Risks Found", "fa-triangle-exclamation"),
    ("History", "fa-clock-rotate-left"),
]

# ----------------------------------------------------------------------------
# FONT AWESOME + GLOBAL CSS
# ----------------------------------------------------------------------------
st.markdown(
    """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #060a17;
            color: #e6ecff;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        [data-testid="stHeader"] { background: rgba(0,0,0,0); }
        .block-container { padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1440px; }

        /* ---------- Sidebar ---------- */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0a0f24 0%, #070b1a 100%);
            border-right: 1px solid rgba(90,110,255,0.15);
        }
        [data-testid="stSidebar"] .block-container { padding-top: 1.2rem; }

        .brand-wrap { display: flex; align-items: center; gap: 12px; margin-bottom: 4px; }
        .brand-icon {
            width: 46px; height: 46px; border-radius: 12px;
            background: linear-gradient(135deg, #7b5cff, #3aa6ff);
            display: flex; align-items: center; justify-content: center;
            font-size: 20px; color: white;
            box-shadow: 0 0 18px rgba(90,140,255,0.45);
        }
        .brand-title { font-size: 21px; font-weight: 800; color: #ffffff; line-height: 1.15; }
        .brand-title span {
            display: block;
            background: linear-gradient(90deg, #7b8cff, #b28bff);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            font-weight: 800;
        }
        .brand-subtitle { color: #93a1c9; font-size: 13px; margin: 12px 0 24px 0; line-height: 1.45; }

        div[data-testid="stSidebar"] button {
            width: 100%; text-align: left !important; border-radius: 10px !important;
            border: 1px solid transparent !important; background: transparent !important;
            color: #b7c2e6 !important; font-size: 15px !important;
            padding: 11px 14px !important; margin-bottom: 5px !important;
            transition: all 0.15s ease-in-out;
        }
        div[data-testid="stSidebar"] button:hover {
            background: rgba(90,110,255,0.12) !important;
            border-color: rgba(90,110,255,0.25) !important; color: #ffffff !important;
        }
        div[data-testid="stSidebar"] button:focus { box-shadow: none !important; }

        .nav-active-tag {
            margin-top: -9px; margin-bottom: 7px; font-size: 11px;
            color: #7b93ff; padding-left: 8px;
        }

        .sidebar-footer {
            margin-top: 46px; display: flex; align-items: center; gap: 10px;
            color: #8b98c4; font-size: 13px; border-top: 1px solid rgba(255,255,255,0.06);
            padding-top: 18px;
        }
        .sidebar-footer i { color: #6f8bff; font-size: 18px; }

        /* ---------- Top bar ---------- */
        .top-bar {
            display: flex; justify-content: flex-end; align-items: center; gap: 8px;
            color: #cfd8ff; font-size: 15px; margin-bottom: 10px;
        }
        .top-bar i { color: #8ea2ff; }

        /* ---------- Hero banner ---------- */
        .hero-box {
            position: relative; overflow: hidden;
            background: radial-gradient(circle at 15% 20%, rgba(90,70,220,0.35), transparent 60%),
                        radial-gradient(circle at 85% 65%, rgba(40,110,220,0.30), transparent 55%),
                        linear-gradient(135deg, #0c1230 0%, #0a1128 60%, #0c1330 100%);
            border: 1px solid rgba(110,140,255,0.18);
            border-radius: 20px;
            padding: 36px 40px;
            margin-bottom: 22px;
        }
        .hero-brand { display: flex; align-items: center; gap: 16px; margin-bottom: 6px; }
        .hero-brand-icon {
            width: 58px; height: 58px; border-radius: 14px;
            background: linear-gradient(135deg, #7b5cff, #3aa6ff);
            display: flex; align-items: center; justify-content: center;
            font-size: 26px; color: white;
            box-shadow: 0 0 22px rgba(100,140,255,0.5);
        }
        .hero-title { font-size: 36px; font-weight: 800; color: #ffffff; margin: 0; line-height: 1.15; }
        .hero-title .grad {
            display: block;
            background: linear-gradient(90deg, #7b8cff, #c07bff);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .hero-tagline { font-size: 19px; font-weight: 600; color: #eef1ff; margin-top: 16px; }
        .hero-desc { color: #a6b2d9; font-size: 15px; margin-top: 8px; max-width: 560px; line-height: 1.55; }

        /* Hero right-side document graphic */
        .hero-graphic {
            position: relative;
            height: 190px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .doc-card {
            position: relative;
            width: 130px; height: 165px;
            background: linear-gradient(160deg, #f4f7ff, #d8e2ff);
            border-radius: 14px;
            box-shadow: 0 10px 40px rgba(60,90,255,0.35);
            padding: 22px 16px;
        }
        .doc-line { height: 7px; border-radius: 4px; background: #7f8fc9; margin-bottom: 12px; }
        .doc-line.short { width: 55%; background: #2f3b6b; }
        .doc-line.w1 { width: 90%; }
        .doc-line.w2 { width: 75%; }
        .doc-line.w3 { width: 85%; }
        .doc-line.w4 { width: 60%; }
        .warn-badge {
            position: absolute; bottom: -18px; right: -22px;
            width: 66px; height: 66px; border-radius: 50%;
            background: #0b1330;
            border: 4px solid #e2e8ff;
            display: flex; align-items: center; justify-content: center;
            box-shadow: 0 6px 20px rgba(0,0,0,0.4);
        }
        .warn-badge i { color: #ff4d5e; font-size: 26px; }
        .sparkle { position: absolute; color: #a68bff; opacity: 0.8; }
        .sparkle.s1 { top: 18px; left: -6px; font-size: 20px; transform: rotate(-15deg);}
        .sparkle.s2 { bottom: 30px; left: 6px; font-size: 14px; }
        .sparkle.s3 { top: 10px; right: 4px; font-size: 16px; }

        /* ---------- Feature cards ---------- */
        .feature-card {
            background: #0d1326;
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 14px; padding: 18px 16px; height: 100%;
            transition: transform 0.15s ease, border-color 0.15s ease;
        }
        .feature-card:hover { border-color: rgba(120,140,255,0.4); transform: translateY(-2px); }
        .feature-icon {
            width: 42px; height: 42px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-size: 18px; margin-bottom: 12px;
        }
        .icon-purple { background: rgba(140,90,255,0.18); color: #b98bff; }
        .icon-blue   { background: rgba(60,120,255,0.18); color: #6fa8ff; }
        .icon-green  { background: rgba(30,190,150,0.15); color: #35d9ab; }
        .icon-indigo { background: rgba(120,90,255,0.18); color: #a48bff; }
        .feature-title { color: #f2f4ff; font-weight: 700; font-size: 15px; margin-bottom: 6px; }
        .feature-text { color: #93a1c9; font-size: 13px; line-height: 1.4; }

        /* ---------- Upload card ---------- */
        .upload-card {
            background: #0d1326; border: 1px solid rgba(255,255,255,0.06);
            border-radius: 16px; padding: 24px 28px; margin-top: 22px;
        }
        .upload-card h3 { color: #ffffff; margin: 0 0 2px 0; font-size: 19px; }
        .upload-card h3 i { color: #6fa8ff; margin-right: 8px; }
        .upload-card p { color: #93a1c9; font-size: 13.5px; margin: 0 0 14px 0; }

        [data-testid="stFileUploaderDropzone"] {
            background: rgba(20,28,60,0.4) !important;
            border: 2px dashed rgba(100,130,255,0.45) !important;
            border-radius: 14px !important;
        }
        [data-testid="stFileUploaderDropzone"] button {
            background: linear-gradient(90deg, #3a6dff, #7b5cff) !important;
            color: white !important; border: none !important; border-radius: 8px !important;
        }

        .tip-box {
            margin-top: 16px; background: rgba(60,110,255,0.08);
            border: 1px solid rgba(100,130,255,0.25); border-radius: 10px;
            padding: 12px 16px; color: #b9c4ea; font-size: 13.5px;
        }
        .tip-box i { color: #ffd166; margin-right: 6px; }

        /* ---------- Right side panels ---------- */
        .panel {
            background: #0d1326; border: 1px solid rgba(255,255,255,0.06);
            border-radius: 16px; padding: 20px 20px; margin-bottom: 18px;
        }
        .panel-header { display: flex; align-items: center; gap: 10px; margin-bottom: 14px; }
        .panel-header-icon {
            width: 36px; height: 36px; border-radius: 10px;
            display: flex; align-items: center; justify-content: center; font-size: 16px;
        }
        .panel-title { color: #ffffff; font-weight: 700; font-size: 16px; }

        .step-row { display: flex; gap: 12px; align-items: flex-start; padding-bottom: 16px; }
        .step-num {
            min-width: 26px; height: 26px; border-radius: 50%;
            background: linear-gradient(135deg, #3a6dff, #7b5cff); color: white;
            display: flex; align-items: center; justify-content: center;
            font-size: 12.5px; font-weight: 700;
        }
        .step-text { color: #c7d0f0; font-size: 14px; padding-top: 3px; }

        .sample-desc { color: #93a1c9; font-size: 13.5px; line-height: 1.5; margin-bottom: 14px; }

        .dont-worry { text-align: center; }
        .dont-worry .shield {
            width: 50px; height: 50px; border-radius: 12px;
            background: rgba(110,140,255,0.15);
            display: flex; align-items: center; justify-content: center;
            font-size: 22px; margin: 0 auto 12px auto; color: #7b93ff; position: relative;
        }
        .dont-worry .shield .check {
            position: absolute; bottom: -4px; right: -4px;
            background: #2ee6a6; color: #08351f; border-radius: 50%;
            width: 18px; height: 18px; display: flex; align-items: center; justify-content: center;
            font-size: 10px; border: 2px solid #0d1326;
        }
        .dont-worry h4 { color: #ffffff; margin: 0 0 8px 0; }
        .dont-worry p { color: #93a1c9; font-size: 13.5px; line-height: 1.5; }

        div.stButton > button { border-radius: 8px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="brand-wrap">
            <div class="brand-icon"><i class="fa-solid fa-shield-halved"></i></div>
            <div class="brand-title">DocuMind<span>Red-Teamer</span></div>
        </div>
        <div class="brand-subtitle">Legal &amp; Contract<br/>Vulnerability Agent</div>
        """,
        unsafe_allow_html=True,
    )

    for label, icon_class in NAV_ITEMS:
        is_active = st.session_state.active_page == label
        if st.button(label, key=f"nav_{label}", use_container_width=True):
            st.session_state.active_page = label
        if is_active:
            st.markdown(f"<div class='nav-active-tag'>● currently viewing</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="sidebar-footer">
            <i class="fa-solid fa-shield-halved"></i>
            <div>Smarter Contracts.<br/>Safer Decisions.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ----------------------------------------------------------------------------
# TOP BAR
# ----------------------------------------------------------------------------
st.markdown(
    """
    <div class="top-bar"><i class="fa-solid fa-user"></i>&nbsp; Samia &nbsp;<i class="fa-solid fa-chevron-down"></i></div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# MAIN LAYOUT
# ----------------------------------------------------------------------------
main_col, side_col = st.columns([3, 1], gap="large")

with main_col:
    hero_left, hero_right = st.columns([2, 1])
    with hero_left:
        st.markdown(
            """
            <div class="hero-brand">
                <div class="hero-brand-icon"><i class="fa-solid fa-shield-halved"></i></div>
                <p class="hero-title">DocuMind<span class="grad">Red-Teamer</span></p>
            </div>
            <p class="hero-tagline">Find hidden risks in your legal &amp; contract documents.</p>
            <p class="hero-desc">Upload a document, and let DocuMind check for issues like
            unfair terms, compliance gaps and security risks.</p>
            """,
            unsafe_allow_html=True,
        )
    with hero_right:
        st.markdown(
            """
            <div class="hero-graphic">
                <i class="fa-solid fa-sparkle sparkle s1"></i>
                <i class="fa-solid fa-sparkle sparkle s2"></i>
                <i class="fa-solid fa-sparkle sparkle s3"></i>
                <div class="doc-card">
                    <div class="doc-line short"></div>
                    <div class="doc-line w1"></div>
                    <div class="doc-line w2"></div>
                    <div class="doc-line w3"></div>
                    <div class="doc-line w4"></div>
                    <div class="warn-badge"><i class="fa-solid fa-triangle-exclamation"></i></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)

    # We need to close the hero-box container that visually wraps both columns.
    # Since Streamlit columns can't be nested inside one raw div easily, we
    # simulate the boxed look by wrapping the whole hero row instead (see CSS
    # trick below via markdown wrapper before/after using st.container).

    # ---- Feature cards ----
    f1, f2, f3, f4 = st.columns(4, gap="medium")
    features = [
        (f1, "icon-purple", "fa-shield-halved", "Find Hidden Clauses", "Detect unfair or risky language."),
        (f2, "icon-blue", "fa-file-lines", "Check Compliance", "Ensure policy & law alignment."),
        (f3, "icon-green", "fa-triangle-exclamation", "Assess Legal Risks", "Identify potential liabilities."),
        (f4, "icon-indigo", "fa-lightbulb", "Get Simple Insights", "Clear results, easy to understand."),
    ]
    for col, icon_cls, icon, title, text in features:
        with col:
            st.markdown(
                f"""
                <div class="feature-card">
                    <div class="feature-icon {icon_cls}"><i class="fa-solid {icon}"></i></div>
                    <div class="feature-title">{title}</div>
                    <div class="feature-text">{text}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ---- Upload section ----
    st.markdown(
        """
        <div class="upload-card">
            <h3><i class="fa-solid fa-file-lines"></i>Upload Your Contract</h3>
            <p>Choose a file (PDF, DOCX or TXT) and click Analyze.</p>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Drag & drop your file here",
        type=["pdf", "docx", "txt"],
        label_visibility="collapsed",
    )
    st.caption("Supported formats: PDF, DOCX, TXT (Max 10MB)")

    analyze_col, _ = st.columns([1, 3])
    with analyze_col:
        analyze_clicked = st.button("Analyze", use_container_width=True, type="primary")

    if uploaded_file is not None:
        st.success(f"Uploaded: **{uploaded_file.name}**")
        if analyze_clicked:
            with st.spinner("Analyzing contract for risks..."):
                time.sleep(1.2)
            st.info("✅ Demo mode — hook this up to your risk-analysis backend to show real results.")
    elif analyze_clicked:
        st.warning("Please upload a contract file first.")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="tip-box"><i class="fa-solid fa-lightbulb"></i><b>Tip:</b> You can also try the sample contract from the sidebar to see how it works!</div>
        """,
        unsafe_allow_html=True,
    )

with side_col:
    st.markdown(
        """
        <div class="panel">
            <div class="panel-header">
                <div class="panel-header-icon icon-blue"><i class="fa-solid fa-rocket"></i></div>
                <div class="panel-title">Quick Start</div>
            </div>
            <div class="step-row"><div class="step-num">1</div><div class="step-text">Upload a contract file</div></div>
            <div class="step-row"><div class="step-num">2</div><div class="step-text">Click on Analyze</div></div>
            <div class="step-row"><div class="step-num">3</div><div class="step-text">View the risks and insights</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="panel">
            <div class="panel-header">
                <div class="panel-header-icon icon-blue"><i class="fa-solid fa-file-lines"></i></div>
                <div class="panel-title">Sample Document</div>
            </div>
            <div class="sample-desc">You can test the app with a sample contract.</div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Use Sample Contract", use_container_width=True):
        st.session_state.active_page = "Upload Contract"
        st.toast("Sample contract loaded!")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="panel dont-worry">
            <div class="shield">
                <i class="fa-solid fa-shield-halved"></i>
                <div class="check"><i class="fa-solid fa-check"></i></div>
            </div>
            <h4>Don't worry!</h4>
            <p>This is just a learning project made for the hackathon. 🙂</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
