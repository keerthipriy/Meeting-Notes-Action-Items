import streamlit as st
import anthropic
import json
import re
from datetime import date

st.set_page_config(
    page_title="Meeting Notes → Action Items",
    page_icon="🗒️",
    layout="wide",
)

st.markdown("""
<style>
    .stButton > button {
        background: #1E3A5F; color: white; border: none;
        border-radius: 8px; padding: 0.6rem 2rem;
        font-weight: 500; width: 100%;
    }
    .stButton > button:hover { background: #2C5282; }
    .action-card {
        background: #F0F7FF; border: 1px solid #BFD9F2;
        border-left: 4px solid #1E3A5F;
        border-radius: 8px; padding: 0.9rem 1.1rem; margin-bottom: 10px;
    }
    .decision-card {
        background: #F0FDF4; border: 1px solid #BBF7D0;
        border-left: 4px solid #16A34A;
        border-radius: 8px; padding: 0.9rem 1.1rem; margin-bottom: 10px;
    }
    .risk-card {
        background: #FFF7ED; border: 1px solid #FED7AA;
        border-left: 4px solid #EA580C;
        border-radius: 8px; padding: 0.9rem 1.1rem; margin-bottom: 10px;
    }
    .question-card {
        background: #FDF4FF; border: 1px solid #E9D5FF;
        border-left: 4px solid #9333EA;
        border-radius: 8px; padding: 0.9rem 1.1rem; margin-bottom: 10px;
    }
    .section-header {
        font-size: 1rem; font-weight: 600; color: #1E3A5F;
        margin: 1.2rem 0 0.6rem;
    }
    .badge {
        display: inline-block; font-size: 11px; font-weight: 600;
        padding: 2px 8px; border-radius: 99px; margin-right: 6px;
    }
    .badge-owner { background: #DBEAFE; color: #1D4ED8; }
    .badge-deadline { background: #DCF5E8; color: #166534; }
    .badge-priority-high { background: #FEE2E2; color: #991B1B; }
    .badge-priority-medium { background: #FEF9C3; color: #854D0E; }
    .badge-priority-low { background: #F1F5F9; color: #475569; }
</style>
""", unsafe_allow_html=True)

EXAMPLE_NOTES = """Project: CRM Platform Launch — Sprint Review & Planning
Date: May 7, 2026
Attendees: Sarah (PM), James (Tech Lead), Priya (Design), Tom (BD), Rachel (QA)

Sarah opened by saying the sprint went reasonably well but we missed the API integration story again — third time now. James said the blocker is still the third-party vendor not providing sandbox access. Tom mentioned he has a contact at the vendor and can chase them directly. Sarah asked Tom to send a follow-up email by end of week.

Priya showed the updated onboarding screens. Everyone liked the new flow. Rachel raised a concern that the form validation on step 3 is still broken on mobile — she'll log a bug ticket today with full repro steps.

James said the backend is ready for the dashboard feature and we can start frontend work in the next sprint. Priya confirmed she has the designs ready. They agreed to kick off the dashboard sprint on Monday.

Tom gave a BD update — two enterprise clients are ready to pilot but need an NDA signed before they can proceed. Sarah said she'll loop in Legal today and target having NDAs ready by next Friday.

Rachel flagged that we have no automated test coverage for the payment flow. James said that's a risk for the launch. They agreed to add a testing spike to the next sprint — James to scope it and add to the backlog by Thursday.

Priya asked who owns the copy for the email notifications — nobody knew. Sarah said she'll check with Marketing and report back before end of week.

Next sprint planning is Monday at 10am. Sarah to send calendar invite."""

PROMPT_TEMPLATE = """You are a senior Project Manager analyzing meeting notes. Extract structured information and return ONLY valid JSON with no markdown, no code fences, no extra text.

Meeting notes:
\"\"\"
{notes}
\"\"\"

Return exactly this JSON structure:
{{
  "meeting_title": "string — infer from context or use 'Team Meeting'",
  "meeting_date": "string — use date from notes or 'Not specified'",
  "attendees": ["list of names/roles mentioned"],
  "summary": "2-3 sentence executive summary of what was discussed and decided",
  "action_items": [
    {{
      "action": "clear description of what needs to be done",
      "owner": "person responsible — use 'Unassigned' if unclear",
      "deadline": "specific date or relative deadline — use 'No deadline set' if none",
      "priority": "High / Medium / Low — infer from context",
      "context": "one sentence of why this matters"
    }}
  ],
  "decisions": [
    {{
      "decision": "what was decided",
      "made_by": "who decided or 'Group decision'",
      "impact": "one sentence on what this unblocks or changes"
    }}
  ],
  "risks_and_blockers": [
    {{
      "issue": "description of the risk or blocker",
      "raised_by": "who raised it",
      "severity": "High / Medium / Low",
      "mitigation": "what's being done about it or 'No mitigation discussed'"
    }}
  ],
  "open_questions": [
    {{
      "question": "what still needs an answer",
      "owner": "who should answer or 'Unassigned'",
      "due": "when it's needed by or 'No deadline'"
    }}
  ],
  "next_steps_summary": "2-3 sentence wrap-up of the most important next steps and who's driving them"
}}"""


def parse_meeting_notes(api_key: str, notes: str) -> dict:
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        messages=[{"role": "user", "content": PROMPT_TEMPLATE.format(notes=notes)}],
    )
    raw = message.content[0].text.strip()
    raw = re.sub(r"^```(?:json)?", "", raw).strip()
    raw = re.sub(r"```$", "", raw).strip()
    return json.loads(raw)


def priority_badge(priority: str) -> str:
    cls = {
        "High": "badge-priority-high",
        "Medium": "badge-priority-medium",
        "Low": "badge-priority-low",
    }.get(priority, "badge-priority-low")
    return f'<span class="badge {cls}">{priority}</span>'


def render_results(data: dict):
    # Header summary
    st.markdown(f"### 📋 {data.get('meeting_title', 'Meeting Summary')}")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.caption(f"📅 {data.get('meeting_date', 'Date not specified')}")
    with col2:
        attendees = data.get("attendees", [])
        st.caption(f"👥 {', '.join(attendees)}" if attendees else "")

    st.info(data.get("summary", ""))
    st.divider()

    # Action items
    actions = data.get("action_items", [])
    st.markdown(f'<div class="section-header">✅ Action Items ({len(actions)})</div>', unsafe_allow_html=True)
    if actions:
        for item in actions:
            priority = item.get("priority", "Medium")
            st.markdown(f"""
            <div class="action-card">
                {priority_badge(priority)}
                <strong>{item.get('action', '')}</strong><br>
                <span class="badge badge-owner">👤 {item.get('owner', 'Unassigned')}</span>
                <span class="badge badge-deadline">📅 {item.get('deadline', 'No deadline')}</span><br>
                <small style="color:#6B7280">{item.get('context', '')}</small>
            </div>""", unsafe_allow_html=True)
    else:
        st.caption("No action items identified.")

    st.divider()

    # Two columns: decisions + open questions
    col_a, col_b = st.columns(2)

    with col_a:
        decisions = data.get("decisions", [])
        st.markdown(f'<div class="section-header">🟢 Decisions Made ({len(decisions)})</div>', unsafe_allow_html=True)
        for d in decisions:
            st.markdown(f"""
            <div class="decision-card">
                <strong>{d.get('decision', '')}</strong><br>
                <small style="color:#6B7280">By: {d.get('made_by', 'Group')} · {d.get('impact', '')}</small>
            </div>""", unsafe_allow_html=True)
        if not decisions:
            st.caption("No decisions recorded.")

    with col_b:
        questions = data.get("open_questions", [])
        st.markdown(f'<div class="section-header">❓ Open Questions ({len(questions)})</div>', unsafe_allow_html=True)
        for q in questions:
            st.markdown(f"""
            <div class="question-card">
                <strong>{q.get('question', '')}</strong><br>
                <small style="color:#6B7280">Owner: {q.get('owner', 'Unassigned')} · Due: {q.get('due', 'No deadline')}</small>
            </div>""", unsafe_allow_html=True)
        if not questions:
            st.caption("No open questions recorded.")

    st.divider()

    # Risks
    risks = data.get("risks_and_blockers", [])
    st.markdown(f'<div class="section-header">🔶 Risks & Blockers ({len(risks)})</div>', unsafe_allow_html=True)
    if risks:
        for r in risks:
            severity = r.get("severity", "Medium")
            st.markdown(f"""
            <div class="risk-card">
                {priority_badge(severity)}
                <strong>{r.get('issue', '')}</strong><br>
                <small style="color:#6B7280">Raised by: {r.get('raised_by', 'Unknown')} · Mitigation: {r.get('mitigation', 'None discussed')}</small>
            </div>""", unsafe_allow_html=True)
    else:
        st.caption("No risks or blockers identified.")

    st.divider()

    # Next steps
    st.markdown('<div class="section-header">🚀 Next Steps Summary</div>', unsafe_allow_html=True)
    st.success(data.get("next_steps_summary", ""))


def generate_markdown(data: dict) -> str:
    lines = [
        f"# Meeting Summary: {data.get('meeting_title', 'Meeting')}",
        f"_Date: {data.get('meeting_date', 'Not specified')} · Generated {date.today().strftime('%B %d, %Y')}_",
        f"\n**Attendees:** {', '.join(data.get('attendees', []))}",
        f"\n## Summary\n{data.get('summary', '')}",
        "\n## ✅ Action Items\n",
    ]
    for i, a in enumerate(data.get("action_items", []), 1):
        lines.append(f"**{i}. {a.get('action', '')}**")
        lines.append(f"- Owner: {a.get('owner', 'Unassigned')}")
        lines.append(f"- Deadline: {a.get('deadline', 'No deadline')}")
        lines.append(f"- Priority: {a.get('priority', 'Medium')}")
        lines.append(f"- Context: {a.get('context', '')}\n")

    lines.append("\n## 🟢 Decisions Made\n")
    for d in data.get("decisions", []):
        lines.append(f"- **{d.get('decision', '')}** _(by {d.get('made_by', 'Group')})_")
        lines.append(f"  - Impact: {d.get('impact', '')}\n")

    lines.append("\n## 🔶 Risks & Blockers\n")
    for r in data.get("risks_and_blockers", []):
        lines.append(f"- **[{r.get('severity', 'Medium')}]** {r.get('issue', '')}")
        lines.append(f"  - Raised by: {r.get('raised_by', 'Unknown')}")
        lines.append(f"  - Mitigation: {r.get('mitigation', 'None discussed')}\n")

    lines.append("\n## ❓ Open Questions\n")
    for q in data.get("open_questions", []):
        lines.append(f"- **{q.get('question', '')}**")
        lines.append(f"  - Owner: {q.get('owner', 'Unassigned')} · Due: {q.get('due', 'No deadline')}\n")

    lines.append(f"\n## 🚀 Next Steps\n{data.get('next_steps_summary', '')}")
    return "\n".join(lines)


# ── UI ─────────────────────────────────────────────────────────────────────

st.title("🗒️ Meeting Notes → Action Items")
st.caption("Paste raw meeting notes — get structured action items, decisions, risks, and open questions instantly.")
st.divider()

col1, col2 = st.columns([1.4, 1])

with col1:
    notes_input = st.text_area(
        "Paste your meeting notes here *",
        height=340,
        placeholder="Paste raw notes, bullet points, or even a rough transcript...",
    )
    use_example = st.button("Load example notes", use_container_width=False)
    if use_example:
        st.session_state["example_loaded"] = True
        st.rerun()

    if st.session_state.get("example_loaded") and not notes_input:
        notes_input = EXAMPLE_NOTES
        st.text_area("Paste your meeting notes here *", value=EXAMPLE_NOTES, height=340, key="example_area")

with col2:
    st.markdown("**Settings**")
    api_key = st.text_input(
        "Anthropic API key",
        type="password",
        placeholder="sk-ant-...",
        help="Get yours at console.anthropic.com",
    )
    st.markdown("---")
    st.markdown("**What this extracts:**")
    st.markdown("""
- ✅ Action items with owner, deadline & priority  
- 🟢 Decisions made and their impact  
- 🔶 Risks and blockers with mitigation  
- ❓ Open questions with owners  
- 🚀 Next steps summary
""")

st.divider()

if st.button("Extract Action Items ✨", use_container_width=True):
    active_notes = notes_input or st.session_state.get("example_area", "")
    if not active_notes.strip():
        st.error("Please paste your meeting notes first.")
    elif not api_key.strip():
        st.error("Please enter your Anthropic API key.")
    else:
        with st.spinner("Reading your notes..."):
            try:
                result = parse_meeting_notes(api_key, active_notes)
                st.divider()
                render_results(result)

                md = generate_markdown(result)
                title_slug = re.sub(r"[^a-z0-9]+", "-", result.get("meeting_title", "meeting").lower()).strip("-")
                filename = f"meeting-summary_{title_slug}_{date.today().isoformat()}.md"

                st.download_button(
                    "⬇️  Download Summary as Markdown",
                    data=md,
                    file_name=filename,
                    mime="text/markdown",
                    use_container_width=True,
                )

            except json.JSONDecodeError:
                st.error("Couldn't parse the response. Try again — occasionally the model returns unexpected formatting.")
            except anthropic.AuthenticationError:
                st.error("Invalid API key. Check your key at console.anthropic.com")
            except Exception as e:
                st.error(f"Something went wrong: {e}")

with st.expander("How to use this tool"):
    st.markdown("""
**Supported input formats:**
- Raw typed notes from a meeting
- Bullet-point summaries
- Rough transcripts or voice-to-text output
- Any unstructured text from a meeting

**Tips for best results:**
- Include attendee names so owners can be assigned correctly
- Mention dates and deadlines if discussed
- The messier the notes, the more useful the output

**After generating:**
- Download the Markdown and paste into Notion, Confluence, or send as a follow-up email
- Use the action items table as your post-meeting checklist
""")
