---
name: routine-setup
description: "When the user wants to automate a recurring PM task, set up a scheduled workflow, or configure routine triggers (weekly reports, triage) - keywords: routine, automate, schedule, recurring task. Force with /setup-routine."
metadata:
  source: pm-os
  source_repo: https://github.com/agentmart/pm-os
  source_path: skills/routine-setup/SKILL.md
  license: MIT
  original_author: AgentMart
  adapted_for: product-manager
---

# Routine Setup

## What This Skill Does

Guides you through creating a custom PM routine — a recurring autonomous task that your AI partner can run on a schedule, in response to events, or via API. Use `/schedule` in Claude Code, or any scheduler that can run a prompt (for example a GitHub Actions workflow). Either way this skill produces a ready-to-deploy routine.

---

## When to Use This

Use this skill when:
- You want to automate a recurring PM task (weekly reports, daily triage, etc.)
- You need to set up a scheduled workflow for your AI partner
- You want a custom routine beyond the built-in ones
- You're configuring routine triggers (schedule, API, GitHub events)

Do NOT use this skill when:
- You want to run a routine one-time (just reference the routine file directly)
- You're looking for a one-off analysis (use the appropriate skill instead)
- The task requires real-time human judgment at every step

---

## The Framework

### Step 1: Define the Task
Identify the recurring PM work you want to automate.

**Questions to ask:**
1. What specific output should this routine produce?
2. Who is the audience for the output?
3. How often does this need to run?
4. What context does the routine need to read?
5. Where should the output go (Slack, document, PR, issue)?

### Step 2: Choose Triggers
Select how the routine starts:

| Trigger Type | Best For | Setup |
|-------------|---------|-------|
| **Schedule** | Regular cadence (daily, weekly, monthly) | Cron expression or natural language |
| **API** | Event-driven from external systems (alerts, deploys) | HTTP POST endpoint |
| **GitHub Event** | Repository events (PR opened, issue created, release) | Event type + filters |

You can combine multiple triggers on the same routine.

### Step 3: Define Context Sources
List which reference files and other data the routine needs:
- Include the most relevant files the project already keeps (specs, a context library, a decision log)
- Add older decisions if the routine has to stay consistent with them
- Add MCP connectors for external data (Jira, Slack, analytics)

### Step 4: Write the Prompt
The routine's prompt must be self-contained and explicit:
- State the task clearly (the routine runs autonomously — no clarifying questions)
- Define the steps in order
- Specify the exact output format with a template
- Include quality checks the routine should self-verify against

### Step 5: Configure Enforcement
Choose enforcement mode:
- `advisory` (default) — Output is a draft for PM review
- `blocking` — Output must pass quality checks before delivery

### Step 6: Set Up Execution
Deploy the routine in your preferred tool:

**Claude Code:**
```
/schedule [description] [cadence]
```
Or create at [claude.ai/code/routines](https://claude.ai/code/routines).

**Scheduled workflow (GitHub Actions example):**
Create a GitHub Actions workflow in `.github/workflows/` with the appropriate trigger and reference the routine's prompt.

---

## Output Template

```markdown
# Routine: [Name]
> [One-line description of what this routine does]

---

## Configuration

\```yaml
trigger: [schedule | api | github-event]
schedule: "[cron expression]"  # If schedule trigger
event: "[event type]"          # If github-event trigger
context_sources:
  - [path/to/file1.md]
  - [path/to/file2.md]
output: [where results go]
enforcement: advisory  # or blocking
\```

---

## Claude Code Setup
\```
/schedule [natural language description and cadence]
\```

## Scheduled Workflow Setup
\```yaml
name: [Routine Name]
on:
  schedule:
    - cron: '[cron expression]'
  workflow_dispatch:
\```

---

## Prompt

[Self-contained prompt with steps, output format, and quality checks]

---

## Quality Checks
- [ ] [Check 1]
- [ ] [Check 2]
- [ ] [Check 3]
```

---

## Quality Signals

A good routine:
- [ ] Has a self-contained prompt that works without human clarification
- [ ] Specifies exact output format (not "generate a summary")
- [ ] Includes quality checks the routine validates against
- [ ] References specific source files by path, not "read the context"
- [ ] Gives setup instructions for the runtime it targets

A bad routine:
- Vague prompt that could produce wildly different outputs each run
- No quality checks — how do you know the output is good?
- Requires human input mid-execution (defeats the purpose of automation)

---

## Related Skills
- `skills/stakeholder-communication/SKILL.md` — For stakeholder update routines
- `skills/north-star/SKILL.md` — For metrics digest routines
- `skills/competitive-research/SKILL.md` — For competitive pulse routines

---

*Adapted from pm-os (skills/automation/SKILL-routine-setup.md) under the MIT licence. Original by AgentMart. Repackaged from a flat SKILL-*.md file into a discoverable skill folder with YAML frontmatter; cross-references and workspace-specific paths were adjusted.*
