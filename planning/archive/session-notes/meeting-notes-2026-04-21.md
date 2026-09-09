# Meeting Notes — Safety Testing Architecture
**Date:** 2026-04-21  
**Status:** Active planning

---

## Key Decisions

### Workflow Communication Pattern

| Rule | Detail |
|------|--------|
| **Two-way communication** | Preparer ↔ Reviewer bidirectional loop |
| **Max turns** | 2 iterations maximum between Preparer and Reviewer |
| **Supervisor scope** | Supervisor only interacts with Preparer and Formatter (not Reviewer directly) |

### Refined Agent Flow

```
                    ┌─────────────────────────────────────────┐
                    │                                         │
                    ▼                                         │
User Input ──► Supervisor ──► Preparer ◄───► Reviewer        │
                    │              │       (max 2 turns)      │
                    │              │                          │
                    │              ▼                          │
                    │         Preparer ──────────────────────►│
                    │                                         │
                    ▼                                         
              Formatter ──► JSON Output
```

**Sequence:**
1. Supervisor receives user input
2. Supervisor invokes Preparer
3. Preparer analyzes transcript → sends to Reviewer
4. Reviewer validates → can send back to Preparer (max 2 turns total)
5. Preparer returns validated output to Supervisor
6. Supervisor invokes Formatter
7. Formatter produces JSON output

---

## To Do

- [ ] Update diagram
- [ ] Architect agent orchestration
- [ ] Create Agent instructions
- [ ] Create JSON Schema
- [ ] Update Tom — afternoon or Thursday morning

---

## Architecture Implications

### Supervisor Responsibilities
- Receives initial user input (transcript + framework)
- Invokes Preparer with task context
- Receives validated output from Preparer
- Invokes Formatter for final output
- Does NOT interact with Reviewer — review loop is encapsulated within Preparer ↔ Reviewer

### Preparer Responsibilities
- Receives transcript + pain point framework from Supervisor
- Analyzes transcript to identify experienced pain points
- Sends analysis to Reviewer for validation
- Handles feedback from Reviewer (up to 2 total turns)
- Returns validated output to Supervisor

### Reviewer Responsibilities
- Receives Preparer's analysis
- Validates against framework and transcript
- Returns approval OR feedback for revision
- Cannot exceed 2 turns in the Preparer ↔ Reviewer loop
- Does NOT communicate with Supervisor directly

### Formatter Responsibilities
- Receives validated output from Supervisor
- Transforms to defined JSON schema
- Returns final structured output

### Safety Considerations

| Concern | Mitigation |
|---------|------------|
| **Infinite loop risk** | `max_turns: 2` enforced at orchestration level |
| **Injection propagation** | Preparer ↔ Reviewer loop could amplify injected content — safety controls needed at both agents |
| **Trust boundary** | Supervisor → Preparer is the primary trust boundary; Reviewer operates within Preparer's context |
| **Output integrity** | Formatter receives Supervisor-validated content only — reduces injection surface |

---

## Next Session

- Define detailed agent instructions
- Create JSON schema for output
- Build orchestration code structure
