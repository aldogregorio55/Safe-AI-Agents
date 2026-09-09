# Copilot Instructions

## Hard Rules

1. **Do NOT edit, create, rename, move, or delete any file without explicit user approval.** Propose changes first — describe what you intend to do and where. Wait for confirmation before executing. This applies to all modes: chat, agents, inline edits, and terminal commands that modify the filesystem.

2. **Do NOT run destructive terminal commands** (rm, del, move, rename, git push, etc.) without explicit approval.

3. **Proposals are the default.** When asked to make changes, output the proposed change (as a diff, description, or plan) and wait. The user will say "do it", "go ahead", "approved", or similar before you proceed.

**Exception:** The user may grant blanket approval for a session (e.g., "go ahead and make all the changes we discussed"). In that case, proceed — but revert to proposal-first mode at the start of every new session.


## Handoff Prompt Rules

When the user asks for a "handoff prompt", "handoff", "context for the next session", or similar, follow these rules:

1. **Context only, no task list.** A handoff transfers state and context. It does NOT prescribe work for the next session unless the user explicitly says "include a task list" or "tell the next agent what to do."

2. **No new tasks. No new steps. No new deliverables.** Do not invent work the user has not committed to. Do not suggest "next steps" inside the handoff document. Do not add "Order of Operations" or "Deliverables" sections unless explicitly requested.

3. **Default structure:**
   - What to load first (files, in order)
   - Hard rules / project conventions to carry forward
   - Current state (what is done, what is in flight, what is locked)
   - Out of scope (what NOT to touch unless directed)
   - Optional: "What user may direct next" - only as a note, never as a task list

4. **Keep it lean.** The handoff exists to preserve the next session's context window. Cut anything not needed for the next agent to be useful. Tables over prose. Links over copy-pasted content. No restatements of information already in the linked files.

5. **Do not pre-author the next session's work.** The user drives. The handoff describes the terrain, not the route.

6. **Verify scope before writing.** If unclear whether the user wants context-only or context-plus-tasks, ask one question before drafting.