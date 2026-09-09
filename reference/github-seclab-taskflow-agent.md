KPMG Code Docs
GitHub Security
Lab Taskflow
Agent
https://docs.code.kpmg.com/GTK/GISG/Tool-
Evaluations/Github-Security-Lab-Taskflow-Agent/
Git rev. f1ea100
Apr 03, 2026
© 2025 Copyright owned by one or more of the KPMG International entities. KPMG International entities provide no services to clients. All rights
reserved. KPMG refers to the global organization or to one or more of the member firms of KPMG International Limited (“KPMG International”), each
of which is a separate legal entity. KPMG International Limited is a private English company limited by guarantee and does not provide services to
clients. Document Classification: KPMG Confidential


---

GitHub Security Lab Taskflow Agent
This tool is maintained by GitHub Security Lab and is licensed under MIT. It is classified as an experimental framework
and is not intended for production deployments without additional review.
Summary
The GitHub Security Lab Taskflow Agent ( seclab-taskflow-agent ) is an MCP-enabled, multi-agent CLI framework
built on the OpenAI Agents SDK. It allows users to define and execute agentic security workflows entirely through
YAML files using a GitHub Workflow-inspired grammar called a taskflow.
GitHub Security Lab primarily uses the framework as:
A code auditing tool for identifying vulnerabilities (e.g., using CodeQL + AI)
An automated triage tool for code scanning alerts
The framework is extensible through MCP servers (called toolboxes) and supports multi-agent cooperation via agent
handoffs.
What It Does (High Level)
Defines reusable Agents (called personalities) with system-level instructions and MCP toolsets.
Chains those agents into taskflows — sequences of interdependent tasks executed end-to-end.
Integrates with MCP servers (toolboxes) to give agents access to tools: GitHub API, CodeQL, memory cache,
echo, and more.
Supports iterative (repeat prompt), parallel (async), and shell-based tasks.
Includes a CodeQL MCP server so agents can navigate source code via templated CodeQL queries — enabling
LLM-powered code review without the model writing CodeQL directly.
Note


---

Supports human-in-the-loop via tool-call confirmations (configurable per toolbox), and a headless mode for fully
automated pipelines.
Core Concepts
Concept
Description
Personality
YAML file defining an agent's system prompt and default toolboxes
Toolbox
YAML file configuring an MCP server that provides tools to an agent
Taskflow
YAML list of tasks; the main orchestration unit. Each task specifies agents, toolboxes, and a user
prompt
Prompt
Reusable prompt fragment that can be injected into taskflow user prompts via {{ PROMPTS_<path>
}}
Model
Config
YAML file centralizing model version and parameter settings shared across taskflows
How Tasks Are Structured
Agent Handoffs
A task can specify a primary agent and one or more handoff agents. The primary agent can choose to pass
execution to a handoff agent mid-task, enabling triage patterns such as:
1. Primary agent reviews findings and routes low-confidence cases.
2. Specialist (handoff) agent performs deeper analysis.
Repeat Prompts (Batch / Iteration)
seclab-taskflow-agent:
version: "1.0"
filetype: taskflow
taskflow:
- task:
model: GPT-5.1
must_complete: true
agents:
- seclab_taskflow_agent.personalities.c_auditer
user_prompt: |
Review the C code in the `vulnerable_c_example` memory key for security issues.
toolboxes:
- seclab_taskflow_agent.toolboxes.codeql
- seclab_taskflow_agent.toolboxes.memcache


---

Tasks with repeat_prompt: true  iterate over the JSON list output of the previous task. This is useful for bulk
analysis — for example, fetching a list of functions and auditing each one individually:
Use Cases
Use Case
Description
Vulnerability triage
Automate the triage of code scanning alerts using AI agents that review code
and context
Code auditing
Combine CodeQL databases with LLM agents to audit source code for
vulnerabilities
CVE reproduction / research
Define taskflows that reproduce a CVE pattern and validate whether a target
codebase is affected
Agentic workflow
experimentation
General-purpose scaffold for building and testing multi-agent workflows via
YAML
Requirements
Requirement
Detail
Python
>= 3.10 (or Docker)
AI_API_TOKEN
GitHub personal access token (PAT) entitled to GitHub Models
GH_TOKEN
GitHub PAT for MCP servers that access the GitHub API (can be the same PAT)
CodeQL
Required only when using the CodeQL MCP toolbox; CodeQL databases must be pre-built and
available on disk
- task:
repeat_prompt: true
async: true
# run iterations in parallel
async_limit: 5
agents:
- seclab_taskflow_agent.personalities.c_auditer
user_prompt: |
The function is named {{ result.name }}.
Body: {{ result.body }}
Identify any security issues.


---

Minimal End-to-End Usage
Option A: From Source
Option B: Docker
The Docker image is not a security boundary — it is a deployment convenience only. Do not assume container isolation
provides meaningful sandboxing for agent-executed code.
Security Considerations
Never store credentials on disk. Use environment variables or CI secrets for AI_API_TOKEN  and GH_TOKEN . The
framework supports a .env  file for non-sensitive configuration only.
Scope tokens to least privilege. Use fine-grained PATs with only the repository permissions required for the
taskflow (e.g., read-only for code review, no write permissions unless necessary).
Scope toolboxes tightly. Each toolbox is an MCP server that the agent can call freely. Review and limit the tools
exposed in each taskflow to prevent agents from taking unintended actions.
Use confirm  lists for destructive tools. Configure confirm  in toolbox YAML files to require human approval
before tools that modify state or make external calls are executed.
git clone <https://github.com/GitHubSecurityLab/seclab-taskflow-agent.git>
cd seclab-taskflow-agent
python -m venv .venv
source .venv/bin/activate
pip install hatch
hatch build
# Set required tokens
export AI_API_TOKEN=<your_github_token>
export GH_TOKEN=$AI_API_TOKEN
# Run a built-in example taskflow (CodeQL-based C code audit)
hatch run main -t examples.taskflows.CVE-2023-2283
export AI_API_TOKEN=<your_github_token>
export GH_TOKEN=$AI_API_TOKEN
# Run a built-in taskflow
docker/run.sh -t example
# Mount custom taskflows
MY_TASKFLOWS=~/my_taskflows docker/run.sh -t my_custom_taskflow
Warning


---

Avoid headless mode in sensitive environments. headless: true  disables all tool-call confirmation prompts —
use only in controlled CI pipelines where all tool calls have been pre-reviewed.
Treat Docker as a deployment convenience, not a security boundary. Do not assume isolation from the host
system.
Review MCP server supply chain. Third-party or custom MCP servers introduce their own trust surface —
evaluate them for vulnerabilities and pin to reviewed versions.
Apply MAESTRO threat modeling before deploying taskflows that access production systems or sensitive code
repositories.
References
GISG AppSec Context
GitHub Repository
GitHub Blog
CodeQL MCP Server Demo — YouTube
📅 Last Updated: April 2026 | 📌 Version: 1.0 | 👥 Maintained by: GISG
