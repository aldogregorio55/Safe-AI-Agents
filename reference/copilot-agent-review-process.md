KPMG Code Docs
Copilot Studio
Agent Review
Process
https://docs.code.kpmg.com/GTK/GISG/Security-
Enablement-and-Assessment-Guide/processes/copilot-
agent-review-process/
Git rev. f1ea100
Apr 03, 2026
© 2025 Copyright owned by one or more of the KPMG International entities. KPMG International entities provide no services to clients. All rights
reserved. KPMG refers to the global organization or to one or more of the member firms of KPMG International Limited (“KPMG International”), each
of which is a separate legal entity. KPMG International Limited is a private English company limited by guarantee and does not provide services to
clients. Document Classification: KPMG Confidential


---

Copilot Studio Agent Review Process
Overview
This document describes the end-to-end process for using the GISG Copilot Studio Reviewer Agent to support
security assessments of Copilot Studio Agents. The process ensures that all agents are evaluated against KPMG
security requirements before being approved for use, with clear ownership at every stage.
Process Flow Diagram
Process Stages
Stage 1 — Assessment Requested
Responsible: GATE COE
A new security assessment request is raised for a Copilot Studio Agent. The GATE Centre of Excellence (COE)
initiates the process by formally requesting a security review of the agent from GISG, providing relevant details such
as agent name, purpose, source code, owning team, etc.
Stage 2 — Obtain Copilot Studio Agent Source Code
Responsible: GISG
flowchart TD
A([🟢 Start]) --> B
B["📋 Stage 1: Assessment Requested\n──────────────────\nResponsible: GATE COE"]
B --> C["📦 Stage 2: Obtain Source Code\n──────────────────\nResponsible: GISG"]
C --> D["⚙️ Stage 3: Run Automated Scan\n──────────────────\nResponsible: GISG"]
D --> E["📊 Stage 4: Review Assessment Output\n──────────────────\nResponsible: GISG"]
E --> F{{"🧑 Stage 5: Human-in-the-Loop Review\n──────────────────\nResponsible: GISG"}}
F -- "❌ Does NOT Conform" --> G["🔧 Stage 5a: Return for
Remediation\n──────────────────\nResponsible: GATE COE"]
G --> B
F -- "✅ Conforms" --> H["✅ Stage 5b: Provide Assessment
Output\n──────────────────\nResponsible: GISG"]
H --> I([🔄 Update SAR Status in GSSR])


---

GISG obtains the source code or exported configuration of the Copilot Studio Agent under review. This may be
provided as a repository reference or a folder containing the agent's source artifacts.
Stage 3 — Run Scan Using the GISG Copilot Studio Reviewer Agent
Responsible: GISG
GISG initiates the automated assessment by submitting a prompt to the GISG Copilot Studio Reviewer Agent. The
prompt instructs the agent to scan the target:
Assess <repo-name>
Scan <folder containing agent source code>
Review the security posture of <agent-name>
The Reviewer Agent analyses the source code and configuration against KPMG security controls and known
patterns, identifies potential vulnerabilities, and produces a structured assessment report.
Stage 4 — Review Assessment Output
Responsible: GISG
The GISG team reviews the output produced by the Reviewer Agent. This includes:
Identified security findings and risk ratings
Compliance status against applicable security requirements
Recommended remediations for any findings
Stage 5 — Human-in-the-Loop Review
Responsible: GISG
A GISG security engineer performs a human-in-the-loop review of the assessment output to validate findings and
make a conformance determination.
Stage 5a — Does Not Conform: Return for Remediation
Responsible: GATE COE
If the agent does not conform to security requirements, the assessment output — including identified findings and
remediation guidance — is sent back to GATE COE. The owning team is expected to address all findings and re-
submit the agent for re-assessment (returning to Stage 1).
Example Prompts


---

Stage 5b — Conforms: Provide Assessment Output & Update GSSR
Responsible: GISG
If the agent conforms to security requirements, GISG:
1. Delivers the final assessment output to GATE COE.
2. Updates the Security Assessment Request (SAR) status in the GSSR system to reflect the completed and
passed assessment.
Roles & Responsibilities Summary
Stage
Activity
GATE COE
GISG
1
Request new security assessment
R / A
I
2
Obtain agent source code
C
R / A
3
Run automated scan via Reviewer Agent
I
R / A
4
Review assessment output
I
R / A
5
Human-in-the-loop conformance review
I
R / A
5a
Remediate findings and re-submit (non-conforming)
R / A
C
5b
Provide assessment output & update SAR in GSSR
I
R / A
Related Resources
GISG Security Enablement & Assessment Guide
📅 Last Updated: March 2026 | 📌 Version: 1.0 | 👥 Maintained by: GISG
