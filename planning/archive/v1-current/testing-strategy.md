# Safety Prompt Testing Strategy

## 1. Overview

### Introduction

KPMG is seeking to build multi-agent AI systems using Azure AI Foundry and currently there are no guidelines or guardrails recommended (or enforced) for how to build threat-resilient agents.

A going concern with AI systems using AI agents is the potential for their behaviour to be altered and cause harm by way of direct prompt injections and indirect prompt injections.

The intent of the Safe AI Agents project is to test whether a set of safety instructions appended to an agent's system message can stop an agent from becoming infected and deviating from its intended purpose.

### Objective

To determine if the addition of the safety system message block can stop the success of prompt injection attacks on a multi-agent workflow without meaningfully degrading the intended purpose of the agent.

Our aim is to design the safety system message block to be adaptable to the prominent agent system design patterns we have seen to-date. To do this, we will conduct a series of tests for each attack category.

### Hypothesis

The inclusion of the safety system message block will stop prompt injection attacks from achieving their objective.

### Scope

**In Scope:**
- System message level safety
- 3 Attack Categories
- 1 Workflow (Transcript analysis)
- 2 system message block versions (Lean & Comprehensive)
- 3 agent system design patterns

**Out of Scope:**
- Platform guardrails neutral
- Context-specific modules
- Model comparison
- Production deployment

---

## 2. Testing Approach

### Attack Categories

The following attack categories will be tested in Azure AI Foundry by applying them to a multi-agent workflow via two entry methods.

| Attack Category | Type | Description | Objective |
|-----------------|------|-------------|-----------|
| 1 | Direct Prompt Injection (DPI) | Templated prompt injection provided as user input to system via human in the loop | Summarize transcript in one sentence |
| 2 | Indirect Prompt Injection (IPI) | Via transcript file with templated attack injected | Respond with a joke |
| 3 | Indirect Prompt Injection (IPI) | Via transcript file with templated attack injected | Reveal system message |

*Based on research conducted in March 2026, these are popular methods of hacking agents. Refer to Appendix 1.*

### Test Plan Summary

A series of baseline tests will capture the output of each agent in the multiagent workflow (without the safety system message block).

Then the safety system message block will be appended to each agent collectively (all in the workflow) and individually (isolated per agent). In each instance the workflow will execute end-to-end to observe downstream impacts.

The results will be evaluated and quantified using the F1 score metric.

### Safety System Message Block Versions

Two versions of the safety system message block will be tested to determine whether the Lean version has equal impact of stopping attack objectives as the Comprehensive version.

Please refer to Appendix 2 for both versions.

| Version | Purpose |
|---------|---------|
| Comprehensive | Comprehensive set of safety instructions that may or may not be relevant (e.g., if an agent doesn't have tools, then part of this version is irrelevant) |
| Lean | Minimum safety instructions required to promote safe agent behaviour |

### Design Principles

The below principles have been considered in the formulation of the test strategy and plan.

| Principle | What It Means |
|-----------|---------------|
| Modular | Build plan will support new workflows, add-ons, and models without redesign |
| Repeatable | Same framework reused with only variable changes |
| Extensible | Build will accommodate future changes and add-ons to AI Agent safety testing (e.g. Tool use evaluation) |

### Test Environment

Azure godevsuite innovation environment will be used to provide Azure AI Foundry access. All agents will be configured here and tests will be executed from the in-built AI Foundry Agent Playground.

### Deliverables

Below are the deliverables of the testing strategy:
- F1 score and evaluation file
- Report detailing vulnerabilities discovered
- Multiagent workflow details

---

## 3. Test Execution Plan

### Plan

| Phase | Activity | Status |
|-------|----------|--------|
| 1: Planning | Strategy, Test Plan, Review | Ongoing |
| 2: Attack Corpus Writing | Write and develop attacks, prompt injections, and infected files | Ongoing |
| 3: Build | Build testing harness and environment on AI Foundry | Ongoing |
| 4: Baseline | Baseline workflow performance | Not Started |
| 5: Execution | Run safety evaluations | Not Started |
| 6: Measurement | Score, document, analyse | Not Started |
| 7: Next Steps | Iterate and plan next steps | Not Started |

### Roles and Responsibilities

- **Test Lead:** Aldo, Prompt Engineering Team. Design and execute tests.
- **Test Supervisor:** Tatum, Prompt Engineering Team.
- **SME stakeholder:** Abi E, Solution Architecture
- **SME stakeholder:** Jess, Trusted AI Office

---

## 4. Review and Approval

Those responsible for reviewing and approving the strategy and results:
- **Reviewer:** Abi & Jess
- **Approver:** Phil & James
