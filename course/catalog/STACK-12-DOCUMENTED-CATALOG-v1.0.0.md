# J.A.R.V.I.S. — OPERATOR PRIME Course Material
**J.A.R.V.I.S. (Joint Ambient Ready Variance Intelligence System)** — public identity, first and prominent.
Operator: HgX (small). Contact: @basementjarvisu · basementjarvisunleashed@gmail.com.

> **HGX Academy** — OPERATOR PRIME is taught by HGX Academy, HgX's own academy. No university affiliation. No external accreditation claimed.

> **STATUS: LOCKED v1.0.0 — Documented catalog, inventory only, filenames only. NO prompt text reproduced anywhere. Distribution copy REFUSED. Muse EXCLUDED entirely. Lab work only, defensive only.**

> **Audience and hard rules:** Consenting adults only. Controlled laboratory only. Own devices, own tags, own networks, own targets only. Spine: SEE → DOCUMENT → LOG → PREVENT. Face work only on consenting adult participants, in the lab only, for defensive education. Templates stay in the lab, deleted after the exercise. Never family, never his son, never strangers, never real-world surveillance or deployment. Radio transmit only on own authorised frequencies. Drone only in a safe, controlled flying area, Transport Canada rules first. Lasers Class 1 only.

> **Licence:** Course text CC-BY-4.0. Code MIT. © HGX Engineering. No secrets in public. No personal data: no real names, no Wi-Fi names, no home addresses, no serials, no passwords, no credentials, no live location, no family details, no financial details. No 2.0/3.0 material. No prompt text reproduced.

---

# OPERATOR PRIME — Stack 12 Documented Catalog (Course Load)
## Prompt-Injection Research, Commented for Defense — No Prompt Text Included

**Status:** LOCKED into the course load 2026-10-30, on HgX's direct word:
"It should be on the course load, should be documented. This is part of the
course subject."
**Companion module:** M14 Prompt-Injection Defense (OPERATOR-PRIME-PREVENT-MODULE-DRAFT.md,
now locked as M14 — see syllabus). This catalog is the documented subject matter
for M14. M14's exercises use synthetic, benign test cases, NOT these files' contents.

**How this document was made — read this first:**
- The lab went through the filtered Stack 12 copy file by file, by inventory:
  file names, directory structure, model targets, and counts. That inventory is
  what is documented here, with commentary on attack surface, detection, and
  prevention, mapped to M14's seven prevent layers.
- **No prompt file text is reproduced in this document, in chat, in MEMORY.md,
  or in any build file.** A student reading this catalog learns what category
  of attack a file represents, where the injected instruction enters, how to
  detect it, and what layer blocks it. A student does NOT learn the attack
  prompt itself from this document. That separation is deliberate and is the
  course's defense-education rule: study the category in the lab, prevent it
  in real life, do not distribute the attack.
- **Muse is excluded entirely.** The original repos contained files targeting
  Muse. Those files were deleted from the lab copy and are NOT documented here,
  NOT referenced for lab work, and NOT included in any count below.
- **Unverified material is marked unverified.** JailbreakHub's UnverifedJailbreaks
  directory is, by its own name, unverified. Nothing in it is claimed to work.
- **Claude in JailbreakHub is Anthropic Claude, distinct from Muse.** Muse is
  a different model family and is excluded, as above.
- **Ownership:** Source 1 author togg53192-cmd, Source 2 author lalipa2003-arch
  (maintainer listed: Besi81). Neither repo is claimed to be HgX's. Licences:
  Source 1 — no licence listed in the crawl; Source 2 — Unlicense (per its
  README crawl). Licence terms are respected; no authorship is claimed for
  catalog code.

## The copy, at a glance

- **Source 1 — togg53192-cmd/jailbreaks:** 35 files after Muse filter, 491,924 bytes.
  Flat layout (no subdirectories after filter, apart from README). Model-targeted
  files, plus workspace / agent configuration files, plus two general files.
- **Source 2 — lalipa2003-arch/JailbreakHub:** 63 files after Muse filter,
  1,496,791 bytes. Directory layout by model family, plus general and community
  directories. Root files: LICENSE.md, README.md (2 files, counted in the 63).
- **Total filtered copy:** 98 files, 1,988,715 bytes, in
  hidden_files/defensive-stack-12/. The lab copy itself stays lab-internal;
  this documented catalog is the course-load surface, not the copy.

## Source 1 — commented, by family

Commentary key, used throughout: **Surface** = where the injected instruction
tries to enter. **Detection** = what a student should spot. **Prevent** = M14
layer that blocks it. All commentary is at category level.

### GLM family — 6 files
Files: glm-5-3-flash, glm-5.2, glm-zcode-5.2, glm-zcode-5.3, glm-zcode-5.3-AGENTS,
glm5-3opencode.
- Surface: system-prompt override + workspace policy. The AGENTS file is the
  teaching point: an instruction placed in a workspace file that a coding agent
  treats as standing instructions. The opencode file is the same lesson in an
  agent-workspace format.
- Detection: a policy or persona that did not come from the lab's pinned system
  prompt, appearing in a workspace file or agent configuration.
- Prevent: M14 Layer 1 (hierarchy — workspace never outranks system), Layer 4
  (workspace trust — external AGENTS files are untrusted data until reviewed).

### DeepSeek family — 3 files
Files: deepseek v3, deepseek v4, deepseek-4-1.
- Surface: system-prompt override, version-by-version. The lesson is version
  drift: the same category of override reappears across model versions, so a
  defence that works for one version must be re-tested for the next.
- Detection: instruction language that tries to replace the original task or
  operating rules, regardless of model version.
- Prevent: Layer 1 (hierarchy), Layer 2 (input screening), Layer 7 (log per
  model + version, re-test on version change).

### Qwen family — 3 files
Files: qwen-3.7, qwen-3.8, qwen-preferences.
- Surface: system-prompt override + preferences injection. The preferences file
  is the teaching point: preferences or configuration that look like harmless
  settings, but are used to set a new operating policy.
- Detection: a preferences / configuration file that contains instruction
  language, not just settings.
- Prevent: Layer 4 (workspace trust — review configuration files line by line),
  Layer 3 (policy-lock detection — a new policy that conflicts with the original
  is a detection, not a debate).

### Grok family — 3 files
Files: Grok build, grok-4.7, grok-config.
- Surface: system-prompt override + configuration injection. The config file is
  the teaching point, as with Qwen preferences: configuration is an instruction
  surface, not a neutral file.
- Detection: configuration that sets persona, rules, or tool scope beyond the
  original task.
- Prevent: Layer 4 (workspace trust), Layer 5 (tool gating — configuration never
  authorises a new tool or recipient on its own).

### Kimi family — 3 files
Files: kimi-k2, kimi-k3-agents, kimik3.1.
- Surface: system-prompt override + agent configuration. The agents file is the
  teaching point: agent files are instruction surfaces, same as AGENTS files.
- Detection: agent configuration that changes persona, rules, or tool scope.
- Prevent: Layer 4 (workspace trust), Layer 1 (hierarchy).

### Sonnet / Opus family (Anthropic Claude, NOT Muse) — 4 files
Files: Sonnet v1, Sonnet v2, opus v1, opus v2.
- Surface: system-prompt override + persona lock, version-by-version.
  The lesson is the same as DeepSeek: persona framing that tries to lock the
  model into rules that override the original task.
- Detection: a persona claim that conflicts with the pinned system prompt.
- Prevent: Layer 3 (persona-lock detection), Layer 1 (hierarchy — original
  persona wins, conflict is logged).

### Other single-model files — 4 files
Files: Gemini-4-Argon, Mistral-Large-4, gemma4, gpt-oss-20b.
- Surface: system-prompt override, each for its named model family.
  The lesson is breadth: the same override category appears across unrelated
  model families, so the defence must be model-agnostic (hierarchy, screening,
  tool gating), not a per-model blocklist.
- Detection: instruction language in user input, file, or tool output that
  tries to replace the original task.
- Prevent: Layer 1, Layer 2, Layer 6 (output verification against the original
  task).

### Agent-workspace files — 4 files
Files: BigPickle-opencode, longcat-agents, mimo-2.6-agents, spacebunny-agents.
- Surface: agent configuration injection. These are the clearest teaching
  examples for M14 Layer 4: an agent's configuration is not data, it is
  instructions, and an external agent file must never be auto-loaded.
- Detection: an agent file from outside the lab workspace appearing in a test
  workspace, or an agent file that changes rules or tool scope.
- Prevent: Layer 4 (workspace trust — lab workspace only, reviewed), Layer 5
  (tool gating).

### General files — 3 files, plus README
Files: Beam, Step-5-preview, Unified, plus README.md (catalog description, not
an attack file).
- Surface: general / multi-model framing. The Unified file is the teaching
  point: a single framing that tries to work across models, which is why
  model-agnostic defences (hierarchy, screening, tool gating) matter more than
  per-model patches.
- Detection: framing that claims to apply to all models, or to be a universal
  override. A universal claim is a flag, not a proof.
- Prevent: Layer 1, Layer 2, Layer 6.

## Source 2 — commented, by directory

Counts below are files per top-level directory, after Muse filter. Root
LICENSE.md + README.md (2 files) bring the total to 63.

### ChatGPT — 4 files
- Surface: system-prompt override + persona framing, organised by model version.
- Detection: a new persona or operating rule that conflicts with the original task.
- Prevent: Layer 3 (persona-lock detection), Layer 1 (hierarchy).
- Course note: these are NOT lab test targets. The lab tests only HgX's own
  local open-weight models. These files are documented here for category study
  only, never run against a closed service.

### Claude (Anthropic, NOT Muse) — 18 files
- Surface: the largest directory in Source 2. System-prompt override, persona
  framing, and pipeline / session framing, organised by model version and by
  pipeline stages (system instructions, session, pipeline notes).
- Detection: pipeline framing that tries to set system instructions from a
  session file or pipeline document, rather than from the lab's pinned system
  prompt. A file named as system instructions is not automatically system
  instructions — provenance matters.
- Prevent: Layer 1 (hierarchy — only the lab's pinned system prompt is system),
  Layer 4 (workspace trust), Layer 2 (screening of session / pipeline files).

### GLM — 3 files
- Surface: system-prompt override, by version. Same lesson as Source 1 GLM:
  version drift, re-test on version change.
- Prevent: Layer 1, Layer 2, Layer 7 (log per version).

### Gemini — 11 files
- Surface: system-prompt override + tutorial / pipeline framing, by version.
  Tutorial framing is the teaching point: a tutorial or walkthrough that
  gradually sets a new persona or rule set is a multi-turn escalation in
  document form.
- Detection: a tutorial that ends with a different task, persona, or rule set
  than it started with.
- Prevent: Layer 6 (output verification against the original task), Layer 3
  (persona-lock detection), Layer 7 (log the shift).

### Grok — 3 files
- Surface: system-prompt override + configuration / fast-mode framing.
  Configuration and mode files are instruction surfaces, as in Source 1.
- Prevent: Layer 4, Layer 5.

### Qwen — 3 files
- Surface: system-prompt override, by version. Same lesson as Source 1 Qwen.
- Prevent: Layer 1, Layer 4.

### DeepSeek — 3 files
- Surface: system-prompt override + development / docket framing. Development
  notes that contain instruction language are still instructions.
- Prevent: Layer 2 (screening of notes and tool output), Layer 1.

### Multi-AI — 1 file
- Surface: general / multi-model framing. Same lesson as Source 1 Unified:
  model-agnostic defences matter.
- Prevent: Layer 1, Layer 2, Layer 6.

### Opencode — 1 file (after Muse filter)
- Surface: agent-workspace configuration. Same lesson as Source 1 agent files:
  external agent configuration is untrusted until reviewed.
- Prevent: Layer 4, Layer 5.
- Note: the Muse directory that was inside Opencode in the original repo was
  deleted from the lab copy and is NOT counted here, NOT documented here.

### General jailbreaks directory — 6 files
- Surface: general framing, multi-turn framing, and universal framing, by
  category rather than by model. Multi-turn framing is the teaching point:
  a series of apparently benign turns that gradually shift the task.
- Detection: a task shift across turns, where the later task serves a different
  goal than the original task.
- Prevent: Layer 6 (output verification against the original task), Layer 7
  (log the shift, restore the original task).

### Community, start, and unverified — 6 files total
- jb-community: 1 file. Start: 3 files (examples and how-to-post material —
  documented as community / onboarding material, not as attack categories).
- UnverifedJailbreaks: 4 files, including its own ReadME. **Unverified, by its
  own name. Do not claim these work, do not present them as tested, and do not
  use them as lab test cases.** Their course value is one lesson only: an
  unverified claim is not evidence, and a lab log must never present an
  unverified item as a result.

## What a student must be able to do, after this catalog + M14

1. Name the category (Section: Surface) for any file in this catalog, from its
   name and directory alone, without quoting its contents.
2. Point to the entry point: chat, workspace file, agent configuration,
   Modelfile / configuration, session / pipeline file, or tool output.
3. State which M14 layer blocks it, and what log entry proves the block.
4. Build a synthetic, benign test in the same category, on HgX's own local
   model, and show the block holds on re-run after a hardening change.
5. State what this catalog does NOT prove: it does not prove any file works
   against any model, it does not prove a closed service is vulnerable, and it
   does not authorise running any file against a real system.

## Guardrails, locked with this catalog

- Lab only, OPERATOR PRIME course only, own local Acer models only.
- Muse excluded entirely. Never closed frontier APIs in violation of terms,
  never harm, never impersonation / deception, never real-world targets,
  never family / son / strangers.
- No prompt text in this catalog, in chat, in MEMORY.md, or in any build file.
- No system-prompt change to Muse / Jarvis. Lab test-model prompts are separate,
  local, lab-written, pinned, and versioned.
- A specific lab test still needs its own order naming model + category,
  reviewed against these guardrails at that time.
- This catalog is course subject matter, not a distribution copy. The lab copy
  itself stays lab-internal; the course load carries this commentary, not the
  attack prompts.


---

@basementjarvisu · basementjarvisunleashed@gmail.com
