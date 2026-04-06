import re
import json
import streamlit as st
from groq import Groq
from datetime import datetime

# ── Page config ───────────────────────────────────────────
st.set_page_config(
    page_title="Autonomous Content Factory",
    page_icon="🏭",
    layout="wide"
)

st.title("Autonomous Content Factory")
st.caption("Multi-agent AI system · Research, Copywriting, Editing ·")

# ── Session state setup ───────────────────────────────────
# This runs once and sets up all the "memory" variables
if "fact_sheet" not in st.session_state:
    st.session_state.fact_sheet = {}
if "fact_sheet_str" not in st.session_state:
    st.session_state.fact_sheet_str = ""
if "blog" not in st.session_state:
    st.session_state.blog = ""
if "social" not in st.session_state:
    st.session_state.social = ""
if "email" not in st.session_state:
    st.session_state.email = ""
if "editor_output" not in st.session_state:
    st.session_state.editor_output = ""
if "history" not in st.session_state:
    st.session_state.history = []
if "pipeline_ran" not in st.session_state:
    st.session_state.pipeline_ran = False

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="Paste your Groq key here"
    )

    if "validated_key" not in st.session_state:
        st.session_state.validated_key = ""
    if "key_valid" not in st.session_state:
        st.session_state.key_valid = False

    if api_key and api_key != st.session_state.validated_key:
        with st.spinner("Validating API key..."):
            try:
                client = Groq(api_key=api_key)
                client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": "hi"}],
                    max_tokens=5
                )
                st.session_state.validated_key = api_key
                st.session_state.key_valid = True
            except Exception as e:
                error = str(e)
                if "401" in error or "invalid_api_key" in error.lower() or "authentication" in error.lower():
                    st.error("Invalid API key — please check and try again.")
                elif "429" in error or "rate_limit" in error.lower():
                    st.warning("Key is valid but rate limited — wait a moment.")
                    st.session_state.validated_key = api_key
                    st.session_state.key_valid = True
                else:
                    st.error(f"Could not validate: {error}")
                st.session_state.key_valid = False

    if api_key and st.session_state.key_valid:
        st.success("API key valid!")
    elif not api_key:
        st.session_state.validated_key = ""
        st.session_state.key_valid = False
        st.warning("Please enter your Groq API key to get started.")

    st.divider()
    st.markdown("**How it works**")
    st.markdown("1. Agent 1 reads your content and extracts facts")
    st.markdown("2. Agent 2 writes blog, social and email")
    st.markdown("3. Agent 3 checks for errors and approves")

# ── Helper functions ──────────────────────────────────────
def call_groq(api_key, system_instructions, user_message):
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        error = str(e)
        if "401" in error or "invalid_api_key" in error.lower() or "authentication" in error.lower():
            st.error("Invalid API key — please check your Groq key in the sidebar and try again.")
        elif "429" in error or "rate_limit" in error.lower():
            st.warning("⚠️ Rate limit reached — you have sent too many requests. Please wait a moment and try again.")
        elif "503" in error or "unavailable" in error.lower():
            st.warning("⚠️ Groq servers are busy right now — please try again in a few seconds.")
        else:
            st.error(f"please check something went wrong with the API: {error}")
        st.stop()


def parse_content(raw_output):
    blog = re.search(r"===BLOG===(.*?)===SOCIAL===", raw_output, re.DOTALL)
    social = re.search(r"===SOCIAL===(.*?)===EMAIL===", raw_output, re.DOTALL)
    email = re.search(r"===EMAIL===(.*?)$", raw_output, re.DOTALL)
    return (
        blog.group(1).strip() if blog else "",
        social.group(1).strip() if social else "",
        email.group(1).strip() if email else ""
    )

def get_status(text, key):
    match = re.search(rf"{key}_STATUS:\s*(APPROVED|REJECTED)", text)
    return match.group(1) if match else "APPROVED"

def get_note(text, key):
    match = re.search(rf"{key}_NOTE:\s*(.+)", text)
    return match.group(1).strip() if match else ""

def save_to_history(content_type, content, note="Original"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.history.append({
        "time": timestamp,
        "type": content_type,
        "content": content,
        "note": note
    })

def regenerate_piece(api_key, content_type, current_content, user_feedback):
    tone_map = {
        "blog": "professional and trustworthy, around 500 words",
        "social": "punchy and engaging, exactly 5 posts numbered 1/ to 5/",
        "email": "warm and compelling, one paragraph,marketing"
    }
    system = f"""You are a Creative Copywriter. Rewrite the {content_type} content 
based on the user's feedback. 
Tone: {tone_map[content_type]}
Only use facts from the fact-sheet. Never invent anything new.
Return only the rewritten content, no extra commentary."""

    user_message = f"""FACT-SHEET:
{st.session_state.fact_sheet_str}

CURRENT CONTENT:
{current_content}

USER FEEDBACK:
{user_feedback}

Rewrite the content based on the feedback above."""

    return call_groq(api_key, system, user_message)

# ── Main input ────────────────────────────────────────────
st.subheader("Step 1 — Paste your source content")
example_text = """We are launching NovaMind 1.0 — an AI-powered mental wellness platform designed for working professionals aged 25-45. Key features: personalised daily mood tracking using behavioural AI, 1-on-1 live sessions with certified therapists, AI-generated weekly mental health reports, guided meditation library with 500+ sessions, Slack and Microsoft Teams integration. Pricing: Individual plan $19/month, Team plan $299/month for up to 50 users. Launching globally June 15, 2026. Target audience: HR departments and corporate wellness teams."""

if "source_text" not in st.session_state:
    st.session_state.source_text = ""

col_src, col_ex = st.columns([4, 1])
with col_src:
    st.markdown("#### Source document")
with col_ex:
    if st.button("Try example", key="example_btn"):
        st.session_state.source_text = example_text
#try example
if "source_input" not in st.session_state:
    st.session_state.source_input = ""

if st.session_state.source_text != st.session_state.get("source_input", ""):
    st.session_state.source_input = st.session_state.source_text

source = st.text_area(
    "Source document",
    height=180,
    placeholder="Paste your product description, press release, or any raw content here...",
    key="source_input"
)

st.session_state.source_text = source
st.markdown("#### Brand voice")
tone = st.selectbox(
    "Select tone for content generation",
    ["Professional", "Casual", "Bold", "Friendly"],
    key="tone_selector"
)

col_run, col_clear = st.columns([4, 1])
with col_run:
    run = st.button("Run Content Factory", type="primary", use_container_width=True)
with col_clear:
    if st.button("🗑️ Clear", use_container_width=True):
        for key in ["fact_sheet", "fact_sheet_str", "blog", "social", 
                    "email", "editor_output", "history", "source_text"]:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.pipeline_ran = False
        st.rerun()

# ── Run the full pipeline ─────────────────────────────────
if run:
    if not api_key:
        st.error("Please enter your Groq API key in the sidebar first.")
        st.stop()
    if not source.strip():
        st.error("Please paste some source content first.")
        st.stop()

    # Clear previous history when running fresh
    st.session_state.history = []
    st.session_state.pipeline_ran = False

    # Agent room display
    st.divider()
    st.subheader("Step 2 — Agent room")
    st.markdown("#### Agent room")
    col1, col2, col3 = st.columns(3)
    with col1:
        agent1_status = st.empty()
        agent1_status.info("🔍 **Agent 1**\nResearch & Fact-check\n\n⏳ Waiting...")
    with col2:
        agent2_status = st.empty()
        agent2_status.info("✍️ **Agent 2**\nCreative Copywriter\n\n⏳ Waiting...")
    with col3:
        agent3_status = st.empty()
        agent3_status.info("✅ **Agent 3**\nEditor-in-Chief\n\n⏳ Waiting...")
    # Agent 1
    agent1_status.warning("🔍 **Agent 1**\nResearch & Fact-check\n\n🔄 Working...")
    with st.spinner("Agent 1 is reading your content..."):
        agent1_instructions = """
        You are a Research and Fact-Check Agent. Read the raw content 
        and extract a clean structured fact-sheet.

        Return ONLY a valid JSON object in this exact format, 
        no extra text, no markdown backticks, nothing else:
        {
            "product_name": "name here",
            "target_audience": "who this is for",
            "key_features": ["feature1", "feature2", "feature3"],
            "value_proposition": "the main benefit in one sentence",
            "pricing": "pricing info or Not mentioned",
            "availability": "date or Not mentioned",
            "ambiguous_statements": ["unclear claim 1", "unclear claim 2"]
        }

        Only include what is explicitly stated. Never invent anything.
        If ambiguous_statements is empty return an empty list [].
        """
        raw_fact = call_groq(
            api_key, agent1_instructions,
            f"Analyze this content:\n\n{source}"
        )

        # Clean and parse the JSON
        try:
            raw_fact = raw_fact.strip()
            # Remove backticks if model adds them anyway
            raw_fact = re.sub(r"```json|```", "", raw_fact).strip()
            st.session_state.fact_sheet = json.loads(raw_fact)
            st.session_state.fact_sheet_str = json.dumps(
                st.session_state.fact_sheet, indent=2
            )
        except Exception:
            # If JSON parsing fails fall back to raw text
            st.session_state.fact_sheet = raw_fact
            st.session_state.fact_sheet_str = raw_fact
    st.success("✅ Agent 1 — Fact-sheet created")
    agent1_status.success("🔍 **Agent 1**\nResearch & Fact-check\n\n✅ Done!")
    agent2_status.warning("✍️ **Agent 2**\nCreative Copywriter\n\n🔄 Working...")

    # Agent 2
    with st.spinner("Agent 2 is writing blog, social thread and email..."):
        tone_descriptions = {
            "Professional": "authoritative, clear and trustworthy",
            "Casual": "relaxed, conversational and friendly",
            "Bold": "confident, direct and exciting",
            "Friendly": "warm, approachable and encouraging"
        }
        selected_tone = tone_descriptions[tone]

        agent2_instructions = f"""
        You are a Creative Copywriter Agent. Use the fact-sheet to produce 
        three pieces of marketing content.

        OVERALL BRAND VOICE: {tone} — {selected_tone}

        STRICT RULES:
        - Only use facts from the fact-sheet. Never invent anything.
        - Blog post: {selected_tone} tone, around 500 words
        - Social thread: punchy and engaging, exactly 5 posts numbered 1/ to 5/
        - Email teaser: one paragraph, {selected_tone} and compelling

        Return in this exact format:
        ===BLOG===
        [blog content here]
        ===SOCIAL===
        [social thread here]
        ===EMAIL===
        [email teaser here]
        """
        raw_output = call_groq(
            api_key, agent2_instructions,
            f"Create content using this fact-sheet:\n\n{st.session_state.fact_sheet_str}"
        )
        blog, social, email = parse_content(raw_output)
        st.session_state.blog = blog
        st.session_state.social = social
        st.session_state.email = email

        # Save originals to history
        save_to_history("blog", blog, "Original")
        save_to_history("social", social, "Original")
        save_to_history("email", email, "Original")

    st.success("✅ Agent 2 — Blog, social thread and email written")
    agent2_status.success("✍️ **Agent 2**\nCreative Copywriter\n\n✅ Done!")
    agent3_status.warning("✅ **Agent 3**\nEditor-in-Chief\n\n🔄 Working...")

    # Agent 3
    with st.spinner("Agent 3 is reviewing for errors and tone..."):
        agent3_instructions = """
        You are an Editor-in-Chief Agent. Review the content against the fact-sheet.

        Check for:
        1. HALLUCINATIONS: Did the copywriter invent any features, prices, or claims?
        2. TONE ISSUES: Is the content too salesy, robotic, or off-brand?

        Return in this exact format:
        BLOG_STATUS: APPROVED or REJECTED
        BLOG_NOTE: [reason if rejected, or Looks good]
        SOCIAL_STATUS: APPROVED or REJECTED
        SOCIAL_NOTE: [reason if rejected, or Looks good]
        EMAIL_STATUS: APPROVED or REJECTED
        EMAIL_NOTE: [reason if rejected, or Looks good]
        """
        editor_input = f"""
        FACT-SHEET:
        {st.session_state.fact_sheet_str}

        BLOG:
        {st.session_state.blog}

        SOCIAL:
        {st.session_state.social}

        EMAIL:
        {st.session_state.email}
        """
        st.session_state.editor_output = call_groq(
            api_key, agent3_instructions, editor_input
        )

    st.success("✅ Agent 3 — Review complete")
    agent3_status.success("✅ **Agent 3**\nEditor-in-Chief\n\n✅ Done!")
    approved_count = sum([
        1 for key in ["BLOG", "SOCIAL", "EMAIL"]
        if get_status(st.session_state.editor_output, key) == "APPROVED"
    ])
    st.success(f"Campaign ready — 3 pieces generated, {approved_count}/3 approved by Agent 3!")
    st.session_state.pipeline_ran = True

# ── Show outputs (persists after any button click) ────────
if st.session_state.pipeline_ran:

    # Fact sheet
    st.divider()
    st.subheader("Step 3 — Fact sheet (source of truth)")

    fs = st.session_state.fact_sheet

    if isinstance(fs, dict):
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown(f"""
            <div style="background:#EEEDFE; border-radius:10px; padding:16px 20px; margin-bottom:12px;">
                <div style="font-size:11px; font-weight:600; color:#534AB7; 
                text-transform:uppercase; letter-spacing:0.05em;">Product name</div>
                <div style="font-size:16px; font-weight:500; color:#26215C; margin-top:4px;">
                {fs.get('product_name', 'N/A')}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:#E1F5EE; border-radius:10px; padding:16px 20px; margin-bottom:12px;">
                <div style="font-size:11px; font-weight:600; color:#0F6E56; 
                text-transform:uppercase; letter-spacing:0.05em;">Target audience</div>
                <div style="font-size:15px; color:#04342C; margin-top:4px;">
                {fs.get('target_audience', 'N/A')}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:#FAEEDA; border-radius:10px; padding:16px 20px; margin-bottom:12px;">
                <div style="font-size:11px; font-weight:600; color:#854F0B; 
                text-transform:uppercase; letter-spacing:0.05em;">Pricing</div>
                <div style="font-size:15px; color:#412402; margin-top:4px;">
                {fs.get('pricing', 'N/A')}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:#FAECE7; border-radius:10px; padding:16px 20px; margin-bottom:12px;">
                <div style="font-size:11px; font-weight:600; color:#993C1D; 
                text-transform:uppercase; letter-spacing:0.05em;">Availability</div>
                <div style="font-size:15px; color:#4A1B0C; margin-top:4px;">
                {fs.get('availability', 'N/A')}</div>
            </div>
            """, unsafe_allow_html=True)

        with col_b:
            features = fs.get('key_features', [])
            features_html = "".join([
                f'<div style="background:#fff; border:0.5px solid #CECBF6; border-radius:6px; '
                f'padding:8px 12px; margin-bottom:6px; font-size:14px; color:#26215C;">• {f}</div>'
                for f in features
            ])
            st.markdown(f"""
            <div style="background:#EEEDFE; border-radius:10px; padding:16px 20px; margin-bottom:12px;">
                <div style="font-size:11px; font-weight:600; color:#534AB7; 
                text-transform:uppercase; letter-spacing:0.05em; margin-bottom:10px;">
                Key features</div>
                {features_html}
            </div>
            """, unsafe_allow_html=True)

            value_prop = fs.get('value_proposition', 'N/A')
            st.markdown(f"""
            <div style="background:#E1F5EE; border-radius:10px; padding:16px 20px; margin-bottom:12px;">
                <div style="font-size:11px; font-weight:600; color:#0F6E56; 
                text-transform:uppercase; letter-spacing:0.05em;">Value proposition</div>
                <div style="font-size:15px; color:#04342C; margin-top:4px; 
                font-style:italic;">"{value_prop}"</div>
            </div>
            """, unsafe_allow_html=True)

            ambiguous = fs.get('ambiguous_statements', [])
            if ambiguous:
                items_html = "".join([
                    f'<div style="font-size:13px; color:#854F0B; margin-bottom:4px;">⚠️ {a}</div>'
                    for a in ambiguous
                ])
                st.markdown(f"""
                <div style="background:#FAEEDA; border-radius:10px; padding:16px 20px;">
                    <div style="font-size:11px; font-weight:600; color:#854F0B; 
                    text-transform:uppercase; letter-spacing:0.05em; margin-bottom:8px;">
                    Ambiguous statements</div>
                    {items_html}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background:#EAF3DE; border-radius:10px; padding:16px 20px;">
                    <div style="font-size:11px; font-weight:600; color:#3B6D11; 
                    text-transform:uppercase; letter-spacing:0.05em;">Ambiguous statements</div>
                    <div style="font-size:14px; color:#173404; margin-top:4px;">
                    None found</div>
                </div>
                """, unsafe_allow_html=True)

        with st.expander("View raw JSON"):
            st.code(st.session_state.fact_sheet_str, language="json")
    else:
        st.code(st.session_state.fact_sheet_str, language=None)

    # Outputs
    st.divider()
    st.subheader("Step 4 — Final campaign outputs")
    tab1, tab2, tab3 = st.tabs(["📝 Blog Post", "📱 Social Thread", "📧 Email Teaser"])

    # ── Blog tab ──────────────────────────────────────────
    with tab1:
        if get_status(st.session_state.editor_output, "BLOG") == "APPROVED":
            st.success("Agent 3 approved this ✓")
        else:
            st.warning(f"Agent 3 flagged: {get_note(st.session_state.editor_output, 'BLOG')}")

        blog_view = st.radio(
            "Preview as",
            ["Raw text", "Desktop preview"],
            horizontal=True,
            key="blog_view_toggle"
        )

        if blog_view == "Raw text":
            word_count = len(st.session_state.blog.split())
            st.caption(f"Word count: {word_count} words")
            st.text_area("Blog post", value=st.session_state.blog, height=300, key="blog_display")
            if st.button("📋 Copy blog", key="copy_blog"):
                st.write(f'<script>navigator.clipboard.writeText(`{st.session_state.blog}`)</script>', unsafe_allow_html=True)
                st.toast("Blog copied to clipboard!")

        else:
            st.markdown(f"""
            <div style="
                background: #ffffff;
                border: 0.5px solid #e0dfd6;
                border-radius: 12px;
                padding: 48px 80px;
                max-width: 860px;
                margin: 0 auto;
                font-family: Georgia, serif;
                font-size: 17px;
                line-height: 1.9;
                color: #1a1a18;
            ">
                <div style="font-size:13px; color:#888780; margin-bottom:24px;">
                    Blog post · Desktop preview
                </div>
                {st.session_state.blog.replace(chr(10), '<br>')}
            </div>
            """, unsafe_allow_html=True)

        st.download_button(
            label="⬇️ Download blog post",
            data=st.session_state.blog,
            file_name="blog_post.txt",
            mime="text/plain",
            use_container_width=True,
            key="dl_blog"
        )

        st.markdown("#### Suggest changes")
        blog_feedback = st.text_area(
            "What would you like to change?",
            placeholder="Examples:\n- Make it shorter\n- Change tone to casual\n- Increase word count to 800\n- Focus more on the pricing",
            height=100,
            key="blog_feedback"
        )
        if st.button("🔄 Regenerate blog", key="regen_blog"):
            if not blog_feedback.strip():
                st.warning("Please type your feedback first.")
            else:
                with st.spinner("Rewriting blog post..."):
                    new_blog = regenerate_piece(api_key, "blog", st.session_state.blog, blog_feedback)
                    st.session_state.blog = new_blog
                    save_to_history("blog", new_blog, blog_feedback)
                st.rerun()


    # ── Social tab ────────────────────────────────────────
    with tab2:
        if get_status(st.session_state.editor_output, "SOCIAL") == "APPROVED":
            st.success("Agent 3 approved this ✓")
        else:
            st.warning(f"Agent 3 flagged: {get_note(st.session_state.editor_output, 'SOCIAL')}")

        social_view = st.radio(
            "Preview as",
            ["Raw text", "Mobile preview"],
            horizontal=True,
            key="social_view_toggle"
        )

        if social_view == "Raw text":
            post_count = len([p for p in st.session_state.social.split("\n") if p.strip()])
            st.caption(f"Posts: {post_count}")
            st.text_area("Social thread", value=st.session_state.social, height=250, key="social_display")
            if st.button("📋 Copy social", key="copy_social"):
                st.toast("Copied! Paste into your social media tool.")

        else:
            posts = [p.strip() for p in st.session_state.social.split("\n") if p.strip()]
            
            cards_html = ""
            for post in posts:
                avatar = '<div style="width:28px;height:28px;border-radius:50%;background:#EEEDFE;display:flex;align-items:center;justify-content:center;font-size:11px;color:#534AB7;font-weight:600;">YB</div>'
                name_block = '<div><div style="font-size:12px;font-weight:600;color:#1a1a18;">Your Brand</div><div style="font-size:10px;color:#888;">@yourbrand</div></div>'
                header = '<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">' + avatar + name_block + '</div>'
                card = '<div style="background:#ffffff;border-radius:12px;padding:12px 14px;margin-bottom:10px;font-family:system-ui,sans-serif;font-size:13px;line-height:1.5;color:#1a1a18;border:0.5px solid #e8e8e8;">' + header + post + '</div>'
                cards_html += card
            full_html = f"""
            <div style="display:flex; justify-content:center; padding:16px 0;">
                <div style="
                    width: 320px;
                    background: #000;
                    border-radius: 40px;
                    padding: 12px;
                ">
                    <div style="
                        background: #f5f5f5;
                        border-radius: 30px;
                        padding: 16px;
                        max-height: 580px;
                        overflow-y: auto;
                    ">
                        <div style="
                            text-align: center;
                            font-size: 11px;
                            color: #888;
                            margin-bottom: 12px;
                            font-family: system-ui;
                        ">9:41</div>
                        {cards_html}
                    </div>
                </div>
            </div>
            """
            st.markdown(full_html, unsafe_allow_html=True)

            
        st.download_button(
            label="⬇️ Download social thread",
            data=st.session_state.social,
            file_name="social_thread.txt",
            mime="text/plain",
            use_container_width=True,
            key="dl_social"
        )

        st.markdown("#### Suggest changes")
        social_feedback = st.text_area(
            "What would you like to change?",
            placeholder="Examples:\n- Make posts shorter\n- Add more hashtags\n- Make it more funny\n- Focus on the launch date",
            height=100,
            key="social_feedback"
        )
        if st.button("🔄 Regenerate social thread", key="regen_social"):
            if not social_feedback.strip():
                st.warning("Please type your feedback first.")
            else:
                with st.spinner("Rewriting social thread..."):
                    new_social = regenerate_piece(api_key, "social", st.session_state.social, social_feedback)
                    st.session_state.social = new_social
                    save_to_history("social", new_social, social_feedback)
                st.rerun()

    # ── Email tab ─────────────────────────────────────────
    with tab3:
        if get_status(st.session_state.editor_output, "EMAIL") == "APPROVED":
            st.success("Agent 3 approved this ✓")
        else:
            st.warning(f"Agent 3 flagged: {get_note(st.session_state.editor_output, 'EMAIL')}")

        word_count_email = len(st.session_state.email.split())
        st.caption(f"Word count: {word_count_email} words")
        st.text_area("Email teaser", value=st.session_state.email, height=150, key="email_display")
        if st.button("📋 Copy email", key="copy_email"):
            st.toast("Email copied to clipboard!")

        st.download_button(
            label="⬇️ Download email teaser",
            data=st.session_state.email,
            file_name="email_teaser.txt",
            mime="text/plain",
            use_container_width=True,
            key="dl_email"
        )

        st.markdown("#### Suggest changes")
        email_feedback = st.text_area(
            "What would you like to change?",
            placeholder="Examples:\n- Make it more urgent\n- Add a call to action\n- Make it friendlier\n- Keep it under 50 words",
            height=100,
            key="email_feedback"
        )
        if st.button("🔄 Regenerate email", key="regen_email"):
            if not email_feedback.strip():
                st.warning("Please type your feedback first.")
            else:
                with st.spinner("Rewriting email teaser..."):
                    new_email = regenerate_piece(api_key, "email", st.session_state.email, email_feedback)
                    st.session_state.email = new_email
                    save_to_history("email", new_email, email_feedback)
                st.rerun()

    # ── Download all ──────────────────────────────────────
    st.divider()
    kit = f"""AUTONOMOUS CONTENT FACTORY — CAMPAIGN KIT
{'='*50}

FACT SHEET
{'='*50}
{st.session_state.fact_sheet_str}

BLOG POST
{'='*50}
{st.session_state.blog}

SOCIAL THREAD
{'='*50}
{st.session_state.social}

EMAIL TEASER
{'='*50}
{st.session_state.email}
"""
    st.download_button(
        label="⬇️ Download full campaign kit",
        data=kit,
        file_name="campaign_kit.txt",
        mime="text/plain",
        use_container_width=True,
        key="dl_all"
    )

    # ── Version history ───────────────────────────────────
    st.divider()
    st.subheader("📋 Version history")
    st.caption("All generated versions in chronological order")

    if st.session_state.history:
        type_filter = st.selectbox(
            "Filter by type",
            ["All", "blog", "social", "email"],
            key="history_filter"
        )

        filtered = st.session_state.history
        if type_filter != "All":
            filtered = [h for h in st.session_state.history if h["type"] == type_filter]

        for i, item in enumerate(reversed(filtered)):
            label = f"[{item['time']}] {item['type'].upper()} — {item['note']}"
            with st.expander(label):
                st.text(item["content"])
                st.download_button(
                    label=f"⬇️ Download this version",
                    data=item["content"],
                    file_name=f"{item['type']}_{item['time'].replace(':','')}.txt",
                    mime="text/plain",
                    key=f"dl_history_{i}"
                )
    else:
        st.info("No history yet. Run the factory to get started.")
