# app.py
import os, re, textwrap, datetime
from typing import List, Optional, Tuple, Dict, Any

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI


# --- youtube_transcript_api (per official docs-based flow) ---
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)
from youtube_transcript_api.formatters import TextFormatter


# =========================
# Setup
# =========================
load_dotenv()
ENV_OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
client: Optional[OpenAI] = None

st.set_page_config(page_title="YouTube Summarizer", layout="wide")





# =========================
# Styles / Header
# =========================
st.markdown(
    """
    <style>
      :root { --card: #ffffff; --muted: rgba(120,120,120,0.9); }
      .main .block-container { padding-top: 1.2rem; padding-bottom: 2.2rem; max-width: 1100px; }
      .hero {
        padding: 1.1rem 1.25rem; border-radius: 16px;
        background: linear-gradient(135deg, #111827, #0B1220);
        color: #E5E7EB; border: 1px solid rgba(255,255,255,0.06);
      }
      .pill {
        display:inline-flex; align-items:center; gap:.35rem;
        padding: 0.22rem 0.6rem; border-radius: 999px;
        border: 1px solid rgba(120,120,120,.25); font-size: 0.8rem;
        background: #ffffff08;
      }
      .muted { color: var(--muted); }
      .small { font-size: 0.9rem; }
      .card {
        border: 1px solid rgba(0,0,0,0.06);
        background: var(--card);
        border-radius: 14px; padding: 1rem;
      }
      textarea[readonly], textarea:disabled { background: #0a0a0a08 !important; }
      .footer { text-align:center; color: rgba(120,120,120,0.85); font-size: 0.9rem; padding-top: .75rem; }
      .badge {
        display:inline-block; padding: .2rem .55rem; border-radius: 8px;
        border: 1px solid rgba(0,0,0,0.08); background: #F3F4F6; font-size: .78rem; margin-right: .35rem;
      }
    </style>
    """,
    unsafe_allow_html=True
)

hc1, hc2 = st.columns([0.72, 0.28], vertical_alignment="center")
with hc1:
    st.title("YouTube Summarizer")
with hc2:
    st.markdown(
        '<div style="text-align:right;">'
        '<span class="pill">Transcripts API</span> '
        '<span class="pill">OpenAI</span>'
        '</div>',
        unsafe_allow_html=True
    )


# =========================
# Helpers
# =========================
def extract_video_id(s: str) -> str:
    """Accepts URL or 11-char ID, returns ID or raises."""
    s = s.strip()
    m = re.search(r"(?:v=|youtu\.be/|embed/)([A-Za-z0-9_-]{11})", s)
    if m:
        return m.group(1)
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", s):
        return s
    raise ValueError("Invalid YouTube URL/ID")


def _format_fetched(fetched) -> str:
    return TextFormatter().format_transcript(fetched, indent=2)


def fetch_transcript_per_docs(
    video_id: str,
    preferred_langs: Optional[List[str]] = None,
    translate_to: Optional[str] = None,
    preserve_formatting: bool = False,
) -> Tuple[str, Dict[str, Any]]:
    """
    Returns (formatted_text, meta) using docs workflow.
    Meta contains: language, language_code, is_generated, snippet_count, video_id, translated_to (if any).
    """
    try:
        ytt_api = YouTubeTranscriptApi()
        langs = preferred_langs if preferred_langs else ["en"]

        # Try direct fetch (docs)
        try:
            fetched = ytt_api.fetch(video_id, languages=langs, preserve_formatting=preserve_formatting)
            used_fetched = fetched
            translated_to = None
            if translate_to:
                # Translate via Transcript object
                tl = ytt_api.list(video_id)
                try:
                    tr = tl.find_transcript(langs)
                except Exception:
                    tr = next(iter(tl), None)
                if tr and tr.is_translatable:
                    used_fetched = tr.translate(translate_to).fetch()
                    translated_to = translate_to

            formatted = _format_fetched(used_fetched)
            meta = {
                "video_id": getattr(used_fetched, "video_id", video_id),
                "language": getattr(used_fetched, "language", None),
                "language_code": getattr(used_fetched, "language_code", None),
                "is_generated": getattr(used_fetched, "is_generated", None),
                "snippet_count": len(used_fetched) if hasattr(used_fetched, "__len__") else None,
                "translated_to": translated_to,
            }
            return formatted, meta

        except NoTranscriptFound:
            pass

        # Fallback: enumerate list() and pick best
        tl = ytt_api.list(video_id)

        tr = None
        if preferred_langs:
            try:
                tr = tl.find_transcript(preferred_langs)
            except Exception:
                tr = None

        if tr is None:
            try:
                tr = tl.find_manually_created_transcript(preferred_langs or [])
            except Exception:
                tr = None

        if tr is None:
            try:
                tr = tl.find_generated_transcript(preferred_langs or [])
            except Exception:
                tr = None

        if tr is None:
            tr = next(iter(tl), None)

        if tr is None:
            raise NoTranscriptFound("No transcript streams available.")

        used_fetched = tr.fetch()
        translated_to = None
        if translate_to and tr.is_translatable:
            used_fetched = tr.translate(translate_to).fetch()
            translated_to = translate_to

        formatted = _format_fetched(used_fetched)
        meta = {
            "video_id": getattr(used_fetched, "video_id", video_id),
            "language": getattr(used_fetched, "language", None),
            "language_code": getattr(used_fetched, "language_code", None),
            "is_generated": getattr(used_fetched, "is_generated", None),
            "snippet_count": len(used_fetched) if hasattr(used_fetched, "__len__") else None,
            "translated_to": translated_to,
        }
        return formatted, meta

    except TranscriptsDisabled:
        raise RuntimeError("Transcripts are disabled for this video.")
    except NoTranscriptFound:
        raise RuntimeError("No transcript found for this video.")
    except VideoUnavailable:
        raise RuntimeError("Video unavailable or invalid ID.")
    except Exception as e:
        raise RuntimeError(f"Transcript fetch failed: {e}")


def summarize(text: str, model: str, bullets: int, max_tokens: int, summary_lang: Optional[str]) -> str:
    lang_instruct = f"Write the bullets in {summary_lang}." if summary_lang else "Write in the transcript's language."
    prompt = f"""Summarize the transcript into {bullets} concise bullet points (1–2 sentences each).
Focus on the main ideas, steps, metrics, and conclusions. Avoid filler and timestamps.
{lang_instruct}

Transcript:
{textwrap.indent(text[:12000], ' ')}"""
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Summarize accurately. Do not fabricate."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content.strip()


def mask_key(k: str) -> str:
    if not k:
        return "—"
    if len(k) <= 8:
        return k[0:2] + "…" + k[-2:]
    return k[0:4] + "…" + k[-4:]


# =========================
# Sidebar (profile + settings)
# =========================
user= {"name": "Vinay Kaushik", "email": "kumar.vinay64@gmail.com"}
with st.sidebar:
    # Signed-in user (from OIDC)
    st.markdown("---")
    st.caption("Signed in as:")
    st.write(f"**{user.get('name','')}**")
    st.write(user.get("email",""))


    st.header("⚙️ Settings")

    # Show default env key info (masked), allow optional reveal & override
    st.subheader("OpenAI API Key")
    st.caption("Default (environment):")
    st.code(mask_key(ENV_OPENAI_API_KEY))
    reveal_env = st.checkbox("Reveal full env key (careful!)", value=False)
    if reveal_env and ENV_OPENAI_API_KEY:
        st.code(ENV_OPENAI_API_KEY)

    input_api_key = st.text_input(
        "Override API Key (optional)",
        type="password",
        help="If provided, overrides the environment key for this run."
    )
    st.caption("Active key source is shown at the top once you run.")

    st.divider()
    st.subheader("Model & Output")
    model = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o"], index=0)
    bullets = st.slider("Bullet points", 3, 12, 6, 1)
    max_tokens = st.slider("Max output tokens", 256, 2000, 600, 32)

    st.divider()
    st.subheader("Transcript Language")
    preferred_langs = st.multiselect(
        "Preferred languages (ISO codes, priority order)",
        options=[
            "en","en-US","en-GB","hi","es","fr","de","it","pt","pt-BR","ru","ja","ko",
            "ar","tr","id","vi","th","zh","zh-CN","zh-TW"
        ],
        default=["en","en-US","en-GB"]
    )
    preserve_formatting = st.checkbox("Preserve HTML formatting (<i>, <b>)", value=False)
    translate_to_en = st.checkbox("Translate transcript to English when possible", value=False)
    summary_lang_choice = st.selectbox("Summary language", ["Same as transcript", "English"], index=0)
    summary_lang = None if summary_lang_choice == "Same as transcript" else "English"


# =========================
# Main Form + Preview
# =========================
with st.form("yt_form", clear_on_submit=False):
    url = st.text_input(
        "YouTube URL or ID",
        placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ  •  or  •  dQw4w9WgXcQ",
    )
    submitted = st.form_submit_button("Summarize", use_container_width=True)

if "runs" not in st.session_state:
    st.session_state.runs = []

# Optional video preview
vid_preview = None
if url:
    try:
        vid_preview = extract_video_id(url)
    except Exception:
        vid_preview = None

if vid_preview:
    st.markdown("#### Preview")
    st.video(f"https://www.youtube.com/watch?v={vid_preview}")


# =========================
# Action
# =========================
if submitted:
    active_key = (input_api_key or "").strip() or ENV_OPENAI_API_KEY
    if not active_key:
        st.error("Missing OpenAI API key. Provide it in the sidebar or set OPENAI_API_KEY.")
    else:
        client = OpenAI(api_key=active_key)
        key_source = "Manual override" if (input_api_key or "").strip() else "Environment"
        st.info(f"🔑 Active key source: **{key_source}** — {mask_key(active_key)}")

        try:
            vid = extract_video_id(url)

            with st.status("Fetching transcript…", expanded=False) as status:
                transcript, meta = fetch_transcript_per_docs(
                    video_id=vid,
                    preferred_langs=preferred_langs if preferred_langs else None,
                    translate_to=("en" if translate_to_en else None),
                    preserve_formatting=preserve_formatting,
                )
                status.update(label="Transcript fetched", state="complete")

            with st.status("Summarizing…", expanded=False) as status:
                summary = summarize(transcript, model, bullets, max_tokens, summary_lang)
                status.update(label="Summary ready", state="complete")

            # --- Output cards ---
            t1, t2, t3 = st.tabs(["📝 Summary", "🧾 Transcript", "📤 Export"])
            with t1:
                st.markdown("#### Summary")
                st.markdown(f"<div class='card'>{summary}</div>", unsafe_allow_html=True)
                st.markdown(
                    "<div style='margin-top:.6rem;'>"
                    f"<span class='badge'>Lang: {meta.get('language_code') or meta.get('language') or '—'}</span>"
                    f"<span class='badge'>Generated: {meta.get('is_generated')}</span>"
                    f"<span class='badge'>Snippets: {meta.get('snippet_count') or '—'}</span>"
                    f"<span class='badge'>Translated→ {meta.get('translated_to') or 'no'}</span>"
                    "</div>",
                    unsafe_allow_html=True
                )

            with t2:
                st.markdown("#### Transcript")
                st.text_area("Transcript (read-only)", transcript, height=420, key="transcript_box", disabled=True)

            with t3:
                st.markdown("#### Export")
                now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                sum_name = f"summary_{vid}_{now}.md"
                tr_name = f"transcript_{vid}_{now}.txt"
                st.download_button(
                    "Download Summary (.md)",
                    data=summary.encode("utf-8"),
                    file_name=sum_name,
                    mime="text/markdown",
                    use_container_width=True
                )
                st.download_button(
                    "Download Transcript (.txt)",
                    data=transcript.encode("utf-8"),
                    file_name=tr_name,
                    mime="text/plain",
                    use_container_width=True
                )
                st.code(summary, language="markdown")

            # Store run history
            st.session_state.runs.insert(0, {
                "id": vid,
                "url": url,
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "summary": summary,
                "transcript": transcript,
                "meta": meta,
                "model": model,
                "bullets": bullets,
                "max_tokens": max_tokens,
                "preferred_langs": preferred_langs,
                "preserve_formatting": preserve_formatting,
                "translate_to_en": translate_to_en,
                "summary_lang": summary_lang_choice,
                "key_source": key_source,
                "user_email": user.get("email"),
                "user_name": user.get("name"),
            })
            st.toast("Done", icon="✅")

        except Exception as e:
            st.error(str(e))


# =========================
# History (polished)
# =========================
with st.expander("📚 Recent runs"):
    if not st.session_state.runs:
        st.caption("No runs yet.")
    else:
        for i, r in enumerate(st.session_state.runs[:6], start=1):
            c1, c2 = st.columns([0.74, 0.26])
            with c1:
                st.markdown(
                    f"**{i}.** `{r['id']}`  •  {r['time']}  \n"
                    f"<span class='muted small'>{r['url']}</span>",
                    unsafe_allow_html=True
                )
                meta = r.get("meta", {}) or {}
                st.markdown(
                    f"<span class='badge'>Lang: {meta.get('language_code') or meta.get('language') or '—'}</span>"
                    f"<span class='badge'>Gen: {meta.get('is_generated')}</span>"
                    f"<span class='badge'>Snips: {meta.get('snippet_count') or '—'}</span>"
                    f"<span class='badge'>Tr→ {meta.get('translated_to') or 'no'}</span>"
                    f"<span class='badge'>Key: {r.get('key_source')}</span>"
                    f"<span class='badge'>User: {r.get('user_name') or '—'}</span>",
                    unsafe_allow_html=True
                )
            with c2:
                with st.popover("Preview"):
                    st.markdown("**Summary**")
                    st.markdown(r["summary"][:900] + ("…" if len(r["summary"]) > 900 else ""))
                    st.divider()
                    st.markdown("**Settings**")
                    st.caption(
                        f"Model: `{r['model']}`  •  Bullets: `{r['bullets']}`  •  Max tokens: `{r['max_tokens']}`  \n"
                        f"Pref langs: `{', '.join(r.get('preferred_langs', [])) or '—'}`  •  "
                        f"Preserve fmt: `{r.get('preserve_formatting')}`  •  "
                        f"Translate→EN: `{r.get('translate_to_en')}`  •  "
                        f"Summary lang: `{r.get('summary_lang')}`"
                    )


# =========================
# Footer
# =========================
st.markdown(
    '<div class="footer">Signed in with Google • Streamlit YouTube Summarizer</div>',
    unsafe_allow_html=True
)
