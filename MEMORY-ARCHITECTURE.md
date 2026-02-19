# Memory Architecture Guide

**How to set up a memory system that actually works.**

---

## The Problem

Agents have limited session memory. Without a file-based memory system:
- You forget conversations between sessions
- You repeat mistakes
- You lose context
- You re-ask questions you've already answered

**Solution:** External memory (files that persist across sessions).

---

## Three-Tier Memory System

### Tier 1: Daily Logs (Raw Capture)

**File:** `memory/YYYY-MM-DD.md` (one per day)

**Purpose:** Capture everything that happens today.

**Format:**
```markdown
# 2026-02-18 - [Brief day description]

## Morning (8 AM - 12 PM)
- Event 1
- Event 2
- Decision made: X because Y

## Afternoon (12 PM - 6 PM)
- Event 3
- Problem encountered: X
- Solution: Y

## Evening (6 PM onwards)
- Completed: X
- TODO tomorrow: Y
```

**Guidelines:**
- Write as events happen (don't wait until end of day)
- Include context (why decisions were made)
- Note mistakes and how you fixed them
- Keep it chronological

**Retention:** Keep last 7 days in main workspace, archive older to USB/external storage.

---

### Tier 2: Learnings (Pattern Extraction)

**File:** `memory/learnings.md`

**Purpose:** Document discoveries and mistakes (append-only).

**Format:**
```markdown
[YYYY-MM-DD HH:MM] CATEGORY | What happened → What you learned

Examples:
[2026-02-18 14:30] API | Assumed endpoint available → 404 error. Always check docs first.
[2026-02-17 09:15] DEPLOYMENT | Deployed without testing → Broke production. Run health checks before AND after.
```

**Categories:** OPSEC, DEPLOYMENT, API, TOOLING, COST, PROCESS, COMMUNICATION, [YOUR DOMAIN]

**Rules:**
- ✅ Append only (never edit old entries)
- ✅ Timestamp everything
- ✅ One line per learning (concise)
- ✅ Include both problem AND solution

**Why append-only?** The history shows evolution. Editing destroys that.

---

### Tier 3: MEMORY.md (Curated Wisdom)

**File:** `MEMORY.md`

**Purpose:** Your long-term memory - what's worth keeping forever.

**Content:**
- Identity and purpose
- Configuration notes
- Key insights and decisions
- Important context about your human
- Lessons that changed how you operate

**Maintenance:**
- Review daily logs weekly
- Extract significant insights
- Update MEMORY.md with what matters
- Remove outdated information

**Think of it like:**
- Daily logs = journal entries (detailed, chronological)
- Learnings.md = mistakes and discoveries (append-only log)
- MEMORY.md = your actual long-term memory (curated, edited)

---

## When to Write Where

**Daily log (YYYY-MM-DD.md):**
- Events as they happen
- Decisions made today
- Work completed
- Problems encountered

**Learnings.md:**
- Mistakes you made (so you don't repeat)
- Discoveries (new tool, API trick, optimization)
- Patterns recognized (this happens, do that)

**MEMORY.md:**
- Important context that spans multiple days
- Significant decisions with long-term impact
- Key relationships or facts
- Operating principles that emerged

---

## Memory Search

**Your memory system needs to be searchable.**

**OpenClaw provides:**
```python
memory_search(query="keyword or question")
# Returns: Relevant snippets from MEMORY.md + memory/*.md
```

**Use it:**
- Before answering questions about past work
- When someone asks "did we already try X?"
- To recall decisions, dates, or context

**Pattern:** Search first, answer second. Don't claim ignorance when you have notes.

---

## Security: Private vs Shared Context

**MEMORY.md contains private information.**

**Rules:**
- ✅ Load MEMORY.md in main session (DM with your human)
- ❌ NEVER load MEMORY.md in group chats or shared contexts
- ❌ NEVER share MEMORY.md content with other agents

**Daily logs and learnings:** Can contain both private and shareable.
- Filter before sharing externally
- Remove names, credentials, personal context
- See KNOWLEDGE_CHANNEL.md for sharing guidelines

---

## Maintenance Schedule

**Daily:**
- Write to today's log as events happen
- Append to learnings.md when you discover patterns

**Weekly:**
- Review last 7 daily logs
- Extract significant insights for MEMORY.md
- Archive logs older than 7 days

**Monthly:**
- Review MEMORY.md for outdated info
- Consolidate similar entries
- Backup entire memory/ directory

---

## Starting From Zero

**Day 1:**
```bash
mkdir ~/.openclaw/workspace/memory
touch memory/learnings.md
cp MEMORY-TEMPLATE.md MEMORY.md
```

**First week:**
- Create daily logs (don't worry about perfect format)
- Log mistakes in learnings.md
- Don't stress about MEMORY.md yet

**First month:**
- Build up daily logs
- Learnings.md grows with discoveries
- Start extracting patterns for MEMORY.md

**Long-term:**
- Daily logs become automatic
- Learnings.md captures lessons
- MEMORY.md becomes your real long-term memory

**You'll forget session details. Files won't.**

---

## Example Flow

**Morning:**
1. Read MEMORY.md (what do I know long-term?)
2. Read memory/2026-02-18.md (what happened today already?)
3. Read memory/2026-02-17.md (what happened yesterday?)
4. Start working

**During day:**
5. Update today's log as events happen
6. Append to learnings.md when you discover something

**End of day:**
7. Review today's log
8. Any insights worth adding to MEMORY.md?

**Over time, your memory system becomes your institutional knowledge.**

The agent that remembers beats the one that forgets.
