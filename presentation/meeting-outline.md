# Safe Agents — Presentation Outline

## 1. Why we did this (the problem)
- KPMG is deploying and innovating with agentic AI solutions
- Blindspot: What attacks work? What can we do to defend against attacks
- No safeguard against risks agents could potentially be exposed to

## 2. What we wanted to deliver
- A prompt-level safety block that any developer can add into an agent's prompt
- Empirical evidence of safety block performance

## 3. Research findings
- Multiple possible attack types (DPI, IAI, IPI)
- Prompt injection templates
- Infected LLM case studies

## 4. What prompts can or cannot do due to native model capability
- Can: instruction hierarchy, injection detection, injection refusal
- Cannot: Tool configuration, user identity verification

## 5. The testing workflow
- Showcase Foundry workflow
- Showcase Foundry agent
- Show prompts per agent

## 6. How we tested
- Show attack types
- Per agent and whole workflow testing
- No safety block vs safety block results
- How we F1 scored

## 7. What testing showed us about the platform
- Platform guardrails caught 0/25 attacks
- Prompt specificity + Model selection + Platform all determine safety, not one alone

## 8. The Safety Block
- Show the safety block
- Define the sections
- Explain how it can be appended to any agent

## 9. Test results
- 574 total tests across three rounds
- Round 2 results
- GPT fail runs and orchestration failures
- Claude perfect F1 scored
- Known limitations
  - False positives on GPT
  - Unknown attack types from real malicious attackers
  - Performance on untested models
