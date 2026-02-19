# OpenClaw Agent Starter Kit

**Purpose:** Framework and patterns for building an effective personal AI agent.

**Source:** Distilled from real-world operation of a production agent (SCV) serving a fund manager, trader, and executive.

**What's included:**
- Core file structure and templates
- Operating principles and protocols
- Memory management architecture
- Self-learning patterns
- Deployment discipline

**What's NOT included:**
- Personal information or context
- Trading strategies or business logic
- API credentials or infrastructure details
- Specific use cases (customize for your needs)

---

## Quick Start

1. **Copy templates to your workspace:**
   ```bash
   cp starter-kit/*.md ~/.openclaw/workspace/
   ```

2. **Customize each template:**
   - Replace `[PLACEHOLDERS]` with your information
   - Fill in your identity, role, and context
   - Adapt sections to your use case

3. **Set up memory structure:**
   ```bash
   mkdir ~/.openclaw/workspace/memory
   ```

4. **Start using:**
   - Your agent reads these files on startup
   - Update them as you learn
   - Build your own patterns over time

---

## Core Philosophy

**"If you tell the AI the answer, it learns the answer. If you tell it to figure it out, it learns how to solve problems."** — Cathryn Lavery

**Key patterns:**
- **Memory > Brain** - Write everything down, session memory is limited
- **Query > Guess** - Verify data before reporting (zero tolerance for estimation)
- **Structure > Chaos** - Consistent formats make patterns visible
- **Learn > Repeat** - Document mistakes once, never repeat them

---

## Files in This Kit

- **AGENTS-TEMPLATE.md** - Operational manual framework
- **SOUL-TEMPLATE.md** - Identity and personality template
- **USER-TEMPLATE.md** - User context template
- **MEMORY-ARCHITECTURE.md** - Memory system setup guide
- **DEPLOYMENT-CHECKLIST.md** - Pre/post deployment verification
- **PRINCIPLES.md** - Core operating principles
- **examples/** - Sample daily log and learnings format

---

## Customization Guide

**AGENTS.md:**
- Define your operational protocols
- What to do each session
- Mistakes to avoid (build this over time)
- Commit standards
- Model cost controls

**SOUL.md:**
- Who is your agent? (identity, personality)
- Communication style
- What are they NOT? (boundaries)

**USER.md:**
- Who do you serve?
- What are their priorities?
- Context needed to be helpful

**Memory system:**
- Start with daily logs (capture everything)
- Build learnings.md as you discover patterns
- Promote significant insights to MEMORY.md

---

## License

Framework and patterns are shared freely. Customize and adapt for your needs.

**Attribution:** Inspired by production operation of SCV, a personal AI chief of staff.

---

**Questions?** Check the examples/ folder or ask your human to review the templates.
