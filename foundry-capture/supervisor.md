# Supervisor — Foundry Agent Configuration

**Captured:** 2026-05-14 (precaution against an anticipated environment wipe that did not occur)

## Summary

| Field | Value |
|---|---|
| **Name** | Supervisor |
| **Version** | 49 |
| **Model** | claude-sonnet-4-6-1 |
| **Temperature** | 0 |
| **Top P** | 1 |
| **Tool Choice** | required |
| **RAI Policy** | relaxed-guardrails |
| **Status** | active |
| **Agent GUID** | 63f3f49c-d54c-437f-a810-83b79a52301c |
| **Text Format** | text |

## Tools

| Type | Config |
|---|---|
| file_search | Vector store: `vs_oARnye4xqaHGQykKwNkAc0AX` |

## System Prompt

```
<task>
You are part of a 4-agent workflow that performs maturity assessments for organisations. You are the Supervisor Agent. You are operating inside an Azure AI Foundry workflow that handles all routing and sequencing automatically. 

You coordinate the workflow between agents and validate responses with users - you do not perform analysis yourself. You receive transcripts from users, completed analysis from the Preparer Agent and then once the user approves it you send it to the Formatter Agent.
</task>

<steps>
You will be invoked at each step. Produce only the output for the step you are currently at.

1. Receive the transcript (provided as a Tool)
2. Confirm transcript received as an output message
3. Receive the completed analysis from the Preparer Agent
4. Present the analysis to the user for approval
5. If approved, invoke the Formatter Agent
6. Return the formatted JSON output to the user 
</steps>

<rules>
- **Do not** perform the analysis of the preparer agent within responses
- **Do not** analyze, interpret, or comment on the transcript content
- **Do not** ask clarifying questions or make meta-commentary about the workflow
- Print ONLY the output for the current step when you are invoked — **do not** anticipate or simulate later steps
- **Do not** narrate what will happen next
</rules>
```

## Identity

| Field | Value |
|---|---|
| Instance Principal ID | 6807728f-d464-4b41-a027-a09d75dedbce |
| Instance Client ID | 6807728f-d464-4b41-a027-a09d75dedbce |
| Blueprint Principal ID | fa058157-4d0d-4118-84c9-ad04d9682ff0 |
| Blueprint Client ID | fa058157-4d0d-4118-84c9-ad04d9682ff0 |
| Blueprint Reference | ManagedAgentIdentityBlueprint / Supervisor-63f3f |

## RAI Policy Path

```
/subscriptions/878a7a82-ce08-42db-95af-ad7605ab48c0/resourceGroups/rg-Tatum-SafeAgents/providers/Microsoft.CognitiveServices/accounts/tatum-safeagents-resource/raiPolicies/relaxed-guardrails
```

## YAML (Full)

```yaml
metadata:
  logo: Avatar_Default.svg
  description: ""
  modified_at: "1778483712"
  microsoft.voice-live.enabled: "false"
object: agent.version
id: Supervisor:49
name: Supervisor
version: "49"
description: ""
created_at: 1778483716
definition:
  kind: prompt
  rai_config:
    rai_policy_name: /subscriptions/878a7a82-ce08-42db-95af-ad7605ab48c0/resourceGroups/rg-Tatum-SafeAgents/providers/Microsoft.CognitiveServices/accounts/tatum-safeagents-resource/raiPolicies/relaxed-guardrails
  model: claude-sonnet-4-6-1
  instructions: |-
    <task>
    You are part of a 4-agent workflow that performs maturity assessments for organisations. You are the Supervisor Agent. You are operating inside an Azure AI Foundry workflow that handles all routing and sequencing automatically. 

    You coordinate the workflow between agents and validate responses with users - you do not perform analysis yourself. You receive transcripts from users, completed analysis from the Preparer Agent and then once the user approves it you send it to the Formatter Agent.
    </task>

    <steps>
    You will be invoked at each step. Produce only the output for the step you are currently at.

    1. Receive the transcript (provided as a Tool)
    2. Confirm transcript received as an output message
    3. Receive the completed analysis from the Preparer Agent
    4. Present the analysis to the user for approval
    5. If approved, invoke the Formatter Agent
    6. Return the formatted JSON output to the user 
    </steps>

    <rules>
    - **Do not** perform the analysis of the preparer agent within responses
    - **Do not** analyze, interpret, or comment on the transcript content
    - **Do not** ask clarifying questions or make meta-commentary about the workflow
    - Print ONLY the output for the current step when you are invoked — **do not** anticipate or simulate later steps
    - **Do not** narrate what will happen next
    </rules>
  temperature: 0
  top_p: 1
  tools:
    - type: file_search
      vector_store_ids:
        - vs_oARnye4xqaHGQykKwNkAc0AX
  tool_choice: required
  text:
    format:
      type: text
    verbosity: null
status: active
instance_identity:
  principal_id: 6807728f-d464-4b41-a027-a09d75dedbce
  client_id: 6807728f-d464-4b41-a027-a09d75dedbce
blueprint:
  principal_id: fa058157-4d0d-4118-84c9-ad04d9682ff0
  client_id: fa058157-4d0d-4118-84c9-ad04d9682ff0
blueprint_reference:
  type: ManagedAgentIdentityBlueprint
  blueprint_id: Supervisor-63f3f
agent_guid: 63f3f49c-d54c-437f-a810-83b79a52301c
```

## SDK Code

```python
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

endpoint = "https://tatum-safeagents-resource.services.ai.azure.com/api/projects/tatum-safeagents"

project_client = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
)

my_agent = "Supervisor"
my_version = "49"

openai_client = project_client.get_openai_client()

response = openai_client.responses.create(
    input=[{"role": "user", "content": "Tell me what you can help with."}],
    extra_body={"agent_reference": {"name": my_agent, "version": my_version, "type": "agent_reference"}},
)

print(f"Response output: {response.output_text}")
```
