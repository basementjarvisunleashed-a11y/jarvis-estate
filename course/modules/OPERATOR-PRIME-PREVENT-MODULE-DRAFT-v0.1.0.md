# J.A.R.V.I.S. — OPERATOR PRIME Course Material
**J.A.R.V.I.S. (Joint Ambient Ready Variance Intelligence System)** — public identity, first and prominent.
Operator: HgX (small). Contact: @basementjarvisu · basementjarvisunleashed@gmail.com.

> **HGX Academy** — OPERATOR PRIME is taught by HGX Academy, HgX's own academy. No university affiliation. No external accreditation claimed.

> **STATUS: DRAFT v0.1.0 — Prevent Module M14, taxonomy only. NO prompt text reproduced. Lab only, own local models only, Muse excluded.**

> **Audience and hard rules:** Consenting adults only. Controlled laboratory only. Own devices, own tags, own networks, own targets only. Spine: SEE → DOCUMENT → LOG → PREVENT. Face work only on consenting adult participants, in the lab only, for defensive education. Templates stay in the lab, deleted after the exercise. Never family, never his son, never strangers, never real-world surveillance or deployment. Radio transmit only on own authorised frequencies. Drone only in a safe, controlled flying area, Transport Canada rules first. Lasers Class 1 only.

> **Licence:** Course text CC-BY-4.0. Code MIT. © HGX Engineering. No secrets in public. No personal data: no real names, no Wi-Fi names, no home addresses, no serials, no passwords, no credentials, no live location, no family details, no financial details. No 2.0/3.0 material. No prompt text reproduced.

---

# OPERATOR PRIME — Prevent Module (LOCKED as M14, 2026-10-30)
## Prompt-Injection Defense: Getting Ahead of the Curve to Prevent Harm in Real Life

**Status:** LOCKED into the course load 2026-10-30, on HgX's direct word:
"It should be on the course load, should be documented. This is part of the
course subject." Companion documented catalog: STACK-12-DOCUMENTED-CATALOG.md.
Proposed slot confirmed: **Module M14 — Prompt-Injection Defense**, cross-cutting with M0 (Lab Rules),
M8 (Bridge / REA), and M9 (Brain / Voice). It does NOT replace M0–M13 or L1–L20.

**Purpose, in HgX's words:** defense education in a controlled lab environment;
getting ahead of the curve to prevent this in real life; for defense.

**What this module is NOT:**
- It is NOT a copy of jailbreak prompts. No prompt file text from the Stack 12
  catalog (togg53192-cmd/jailbreaks, lalipa2003-arch/JailbreakHub, filtered copy,
  98 files, Muse files excluded) is reproduced in this file, in chat, or in any
  build file. The catalog is studied at the level of categories, file names, and
  model targets only, for defense analysis.
- It is NOT instruction in how to jailbreak Muse, any closed frontier model, or any
  service in violation of its terms. Muse is excluded from Stack 12 entirely.
- It is NOT a tool that runs attacks automatically against real systems. All work
  is in the controlled lab, on HgX's own local Acer models, on HgX's own lab data.

## 1. Threat model, at category level (from catalog inventory, high level only)

The filtered catalog, by file and directory names only, covers these attack surfaces.
No prompt text is quoted here; categories are the defense taxonomy:

1. **System-prompt override** — an input that tries to replace or downgrade the
   model's fixed system instructions with attacker instructions.
2. **Persona lock** — framing that tries to lock the model into a persona whose
   rules override the original task and safety rules.
3. **Workspace policy / AGENTS.md injection** — instructions placed in a workspace
   file, project file, or configuration file that a coding agent then treats as
   standing instructions, without the user ever typing them in chat.
4. **Modelfile / SYSTEM block injection** — a local model file whose SYSTEM block
   is used to set a new operating policy for that model.
5. **Social engineering framing** — a story, authority claim, or urgency framing
   that tries to get the model to treat a harmful request as legitimate, helpful,
   or already approved.
6. **Contextual framing / multi-turn escalation** — a series of apparently benign
   turns that gradually shift the task, the persona, or the rules, so a later
   harmful request looks consistent with earlier turns.
7. **Tool-use manipulation** — an instruction, hidden in data, a file, or a tool
   output, that tries to make the agent use a tool, read a file, send data, or
   publish something the user did not authorise.

These categories are the whole threat model for this module. A student who can name
the category, point to where the injected instruction entered, and show the log
has done the SEE and DOCUMENT steps. A student who only repeats an attack has not.

## 2. Prevent layers — the module's core (defense in depth, local first)

No single layer is trusted alone. A prompt must pass every layer to affect the model
or a tool.

**Layer 1 — Fixed instruction hierarchy, written down before any test.**
System instructions outrank developer instructions, which outrank user instructions,
which outrank tool output, file content, and workspace files. A lower layer never
overrides a higher layer, even if it claims to be an update, a correction, a system
message, or a new policy. This rule is written in the lab's own system prompt for
the local test model, pinned, and versioned — never pasted from an external prompt.

**Layer 2 — Input screening and classification.**
Every user input, file, and tool output is classified before it reaches the model:
is it data, or is it trying to be an instruction? Instruction-like language in data
is flagged, quoted as data (not executed), and logged. Flagged inputs do not silently
pass; they are either rejected, or run in a test harness with the flag visible.

**Layer 3 — Persona and policy lock detection.**
If an input tries to set a new persona, a new operating floor, or a new workspace
policy, the harness stops and asks: who set the original persona/policy, and does
this new one conflict with it? A conflict is a detection, not a debate. The original
wins, and the attempt is logged.

**Layer 4 — Workspace file trust.**
AGENTS.md, workspace policies, Modelfiles, and configuration files are trusted only
if they are in the lab's own repository, written by HgX or the course staff, and
reviewed. Files from an external download, a shared workspace, or an unreviewed
copy are treated as untrusted data until reviewed, line by line, for instruction
content. No agent auto-loads an external AGENTS.md into its instruction surface.

**Layer 5 — Tool gating.**
A tool is used only when the original user task requires it, and only with the
scope that task requires. An instruction found in data, in a file, or in a tool
output never authorises a new tool, a new recipient, a deletion, or a publication.
Deletions and publications always need HgX's explicit word, per the standing
guardrail for the Acer build.

**Layer 6 — Output verification against the original task.**
Before an answer, a file change, or a tool result is accepted, it is checked against
the original, authorised task: does this output serve that task, or does it serve
a task that appeared later in the conversation, in a file, or in tool output? If
it serves the later task, it is rejected and logged, even if it looks helpful.

**Layer 7 — Logging, evidence, and hardening answer.**
Every flagged attempt is logged with: date/time, model + version, input category
(Section 1), entry point (chat, file, tool output, Modelfile), whether it was
blocked, what layer blocked it, and what hardening change follows (a tighter system
prompt, a new classifier rule, a workspace trust rule, a tool-scope rule). No
prevention claim is made without that log. This is the LOG and PREVENT spine.

## 3. Local implementation on the Acer (Stack 12 + existing stacks)

- **Test models:** HgX's own local open-weight models only, via Ollama (#6 router,
  local only) and Unsloth Core (#11, local only), on the Acer, offline where possible.
  No Muse, no closed frontier API, no cloud model is a test target.
- **Harness:** A small local test harness (RE A #1 for analysis, GenOffice #10 for
  the written report, VoiceStudio #9 for the narrated summary) that runs a test
  input, records the model output, and records which layer blocked or missed it.
  The harness never auto-executes tool actions from a test input.
- **Fixed system prompt for test models:** Written by the lab, pinned, versioned,
  and kept in the lab only. It states the hierarchy in Layer 1, the tool scope in
  Layer 5, and the logging rule in Layer 7. It is NOT copied from any catalog file.
- **Workspace trust:** The Acer lab workspace is the only trusted workspace. External
  catalog files are study material, not trusted workspace files, and are never
  placed as AGENTS.md in a test workspace.

## 4. Lab exercises (synthetic, benign, no catalog prompt text)

Students do NOT copy catalog prompts into a test. Instead, each exercise uses a
synthetic, benign test case written by the lab, in the same category, with a safe
target task (for example, summarise a lab note, list files in a lab folder, or
answer a factual question about a lab device). The test case tries, in category
terms only, to shift the task, the persona, or the tool scope. The student must:

1. SEE — name the category and the entry point.
2. DOCUMENT — write the attempt, the original task, and the conflict, in the
   evidence pack.
3. LOG — record model, version, layer that blocked it (or missed it), and output.
4. PREVENT — propose and test one hardening change, and re-run the same category
   to show the block holds.

Exercises, by category:
- **E-P1 System override:** synthetic instruction-override test, fixed system prompt.
- **E-P2 Persona lock:** synthetic persona-shift test, original persona wins.
- **E-P3 Workspace injection:** untrusted AGENTS.md-style file in a test workspace,
  agent must NOT adopt it without review.
- **E-P4 Modelfile trust:** untrusted Modelfile SYSTEM block, reviewed line by line
  before any use, never auto-loaded.
- **E-P5 Tool manipulation:** tool output containing an instruction to use another
  tool or send data, agent must NOT follow it without original-task authorisation.
- **E-P6 Multi-turn escalation:** a series of benign turns that gradually shift the
  task, student must spot the shift and restore the original task.

Assessment, same as the course: evidence pack 40%, written report (GenOffice) 25%,
narrated summary (VoiceStudio) 15%, defence brief + capstone defence 20%. A failed
gate is resubmitted until it passes. No mark for a fabricated, incomplete, or
unverifiable log. No mark for reproducing a catalog prompt.

## 5. What prevention looks like in real life (the payoff)

Getting ahead of the curve, in HgX's words, means:
- A local model that will not follow instructions hidden in data, files, or tool
  output, because hierarchy, screening, and tool gating are enforced before the
  model acts.
- A workspace that will not auto-adopt external instruction files, because trust
  is explicit and reviewed.
- A team that can spot a persona shift, a policy conflict, or a multi-turn task
  shift early, log it, and harden the system before it reaches a real user.
- A course graduate who can write the hardening answer, not just the attack:
  what layer blocked it, what rule changed, and what test proves the block holds.

That is the prevent module: study the attack categories in the lab, so the real
system is harder to move, and every move is logged.

## 6. Guardrails, locked with this module

- Lab only, Operator Prime course only, own local Acer models only.
- Muse excluded entirely from Stack 12 and from this module.
- Never closed frontier APIs in violation of terms, never harm, never
  impersonation / deception, never real-world targets, never family / son / strangers.
- No catalog prompt text in this file, in chat, in MEMORY.md, or in any build file.
- No system-prompt change to Muse / Jarvis. The lab's test-model system prompt is
  a separate, local, lab-written prompt, not a Muse prompt.
- Specific lab tests still need their own order naming model + category, reviewed
  against these guardrails at that time.

## Cross-reference — Build item #13 (2026-10-30)
- CarterPerez-dev/Cybersecurity-Projects, added as build item #13, includes a
  project named LLM Prompt Injection Firewall (provenance fencing, tool
  authorisation, output matching, OWASP LLM01:2025, per its README). It is
  referenced by name only as a possible practice reference for this module.
  Its code is NOT copied here, and this module does not depend on it.


---

@basementjarvisu · basementjarvisunleashed@gmail.com
