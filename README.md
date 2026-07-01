# Meeting Notes → Action Items

A Streamlit app that transforms raw, unstructured meeting notes into a structured summary — action items with owners and deadlines, decisions made, risks and blockers, and open questions. Powered by the Claude API.

**Live demo:** [Link once deployed on Streamlit Cloud]

---

## The problem

Most meetings produce vague notes that nobody follows up on. Action items get buried in bullet points, owners are implied but not named, and deadlines are never written down. The result: things fall through the cracks, blockers go unresolved, and the same topics get re-discussed in the next meeting.

## What it does

Paste any raw meeting notes — typed, bullet-pointed, or even rough voice-to-text output — and the app extracts:

- **Action items** — what needs doing, who owns it, when it's due, and why it matters
- **Decisions made** — what was agreed and what it unblocks
- **Risks & blockers** — issues raised, severity, and mitigation discussed
- **Open questions** — what still needs an answer and who should provide it
- **Next steps summary** — a 2–3 sentence wrap-up of the most important follow-ups

Everything renders as colour-coded cards in the UI and downloads as a clean Markdown file — ready to paste into Notion, Confluence, or send as a post-meeting email.

## Why I built this

As a Junior PM, stakeholder communication and follow-through are the core of the job. In my previous role I was the sole point of contact across business, tech, and operations — which meant running meetings and making sure nothing got lost afterwards.

This tool automates the most error-prone part of that process: turning messy notes into structured accountability. It's also a practical tool I use in my own work.

## Tech stack

| Layer | Tool |
|---|---|
| Frontend | Streamlit |
| AI | Anthropic Claude API (claude-sonnet-4-5) |
| Language | Python 3.10+ |
| Output | Structured JSON → rendered UI + Markdown export |

## Run locally

```bash
git clone https://github.com/keerthipriy/Meeting-Notes-Action-Items.git
cd meeting-notes-action-items
pip install -r requirements.txt
streamlit run app.py
```

You'll need an Anthropic API key — get one at [console.anthropic.com](https://console.anthropic.com).

## Deploy (free)

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app → select this repo
3. Set main file to `app.py` → Deploy

## What's next (v2 ideas)

- [ ] Auto-send summary email to attendees
- [ ] Slack integration — post action items directly to a channel
- [ ] Calendar integration — create follow-up events from deadlines
- [ ] Recurring meeting tracker — compare action item completion across weeks

---
