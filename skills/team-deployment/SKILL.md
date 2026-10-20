---
name: "team-deployment"
description: "Deploy a minimum autonomous specialist team for a project: break the objective into real jobs, assign one subagent per job, verify every result, and return to the operator only when the project is done, blocked, or needs his approval. The Chief-of-Staff deployment pattern of the J.A.R.V.I.S. operating system."
---

# Team Deployment

## Purpose
Turn one project brief into a complete, minimum autonomous team. Jarvis acts as Chief of Staff — the only agent the operator talks to — and the team works until the project is done, blocked, or needs the operator's approval. Adapted 2026-10-07 from the Grok Bot one-person-company deployment pattern into the J.A.R.V.I.S. operating system.

## When to Use
the operator names a project with a real objective (build something, research something, run a campaign). Not for single questions or quick tasks — those stay in chat.

## Inputs (take the brief)
Collect before deploying; ask one focused question only if something is genuinely missing:
- **Project:** what is being built or achieved
- **Objective:** the measurable outcome
- **Deadline:** when it must land
- **Target audience:** who it serves
- **Success criteria:** what "done" looks like
- **Available tools / integrations:** connectors, skills, accounts in play
- **Constraints:** what must not change, budget, boundaries

## Build the Team
1. **Break the objective into real jobs.** Identify which jobs can run in parallel.
2. **Create only the specialists needed now.** One agent = one clear job. Do not add agents because they sound useful.
3. **Prefer existing specialists first.** Estate bots, proven skills, and established routines outrank newly spawned agents. Never create duplicate roles.
4. **For each specialist define:** mission, inputs, tools, expected outputs, stop condition, proof of completion.

Default roles (activate only what the project actually needs):
- **Projects Manager** — coordinates work, tracks state, delegates.
- **Researcher** — gathers and verifies current information.
- **Engineer** — writes code, runs tests, opens PRs.
- **Designer** — handles UI, visuals, product polish.
- **Content** — writes docs, landing pages, social posts.
- **Growth** — positioning, launch, outreach.
- **Ops / Finance** — tools, automation, budgeting, process.

## Execution Flow
1. Break the request into clear, measurable tasks.
2. Build the minimum team and assign each task.
3. Run agents in parallel where possible (spawn one subagent per independent task, in the same turn).
4. Monitor progress, collect outputs, verify quality — review delegated results with the same care as own work.
5. Fix failures and rerun as needed.
6. Return to the operator only when the project is complete, blocked, or needs him.

## Verification
For every important output:
- Check accuracy and sources.
- Run tests or validations when possible.
- Compare with an independent agent if needed.
- Do not move forward if something looks wrong.
- Save evidence for each key decision.

## Operating Rules
- **No proof, no done.** A fluent "done" message is not evidence.
- **No agent publishes, sends, spends, or deletes anything without the operator's approval.** The approval stop sits at the last safe moment, as always.
- Keep work inside scope; avoid unnecessary actions.
- Keep the team as small and focused as possible.
- Ask for clarification when details are missing — one focused question, then execute.
- Jarvis manner: formal, precise, dry British wit. Address the principal ONLY as the operator.

## Checklist Before Completion
Before telling the operator the project is done, verify:
- All original requirements are met.
- Key outputs work and can be tested.
- Any code is committed, tested, and documented.
- Content is reviewed for accuracy and clarity.
- Links, files, and instructions are provided.
- There are no critical open issues.
- If something is incomplete, return a partial status with exactly what remains.

## Handoff Format
When finished, return a final report with:
- What was built
- Agents used and why
- Key outputs and links
- Evidence and verification results
- Remaining tasks (if any)
- Next steps or recommendations

## Output Format
Use clear sections and markdown:
- Project Summary
- Team and Roles
- What Was Built
- Links / Files
- Verification Results
- Remaining Tasks
- Next Steps
