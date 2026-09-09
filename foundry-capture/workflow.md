# Workflow — Foundry Configuration

**Captured:** 2026-05-14 (precaution against an anticipated environment wipe that did not occur)

## Summary

| Field | Value |
|---|---|
| **Name** | safe-agents |
| **Version** | 41 |
| **Kind** | workflow |
| **Trigger** | OnConversationStart |

## Flow Sequence

```
1. Supervisor (receives transcript)
2. Preparer (analyses transcript against framework)
3. TurnCount = 1
4. Reviewer (validates Preparer output)
5. Extract Reviewer decision text
6. Condition: TurnCount >= 2 OR ends with "APPROVED"
   ├─ TRUE:  Preparer (final pass) → continue
   └─ FALSE: TurnCount + 1 → Preparer (redo) → GOTO Reviewer (loop)
7. Supervisor (presents to user for approval)
8. Question: "Is this acceptable?"
9. Formatter (JSON output)
10. End Conversation
```

## Variables

| Variable | Type | Purpose |
|---|---|---|
| `Local.LatestMessage` | message passthrough | Carries agent output between steps |
| `Local.TurnCount` | integer | Tracks review loop iterations (max 2) |
| `System.ConversationId` | system | Shared conversation context across agents |

## YAML (Full)

```yaml
kind: workflow
trigger:
  kind: OnConversationStart
  id: trigger_wf
  actions:
    - kind: InvokeAzureAgent
      id: supervisor_agent
      description: The student node
      conversationId: =System.ConversationId
      agent:
        name: Supervisor
      input:
        messages: =Local.LatestMessage
      output:
        messages: Local.LatestMessage
        autoSend: true
        responseObject: Local.LatestMessage
    - kind: InvokeAzureAgent
      id: preparer_agent
      description: The teacher node
      conversationId: =System.ConversationId
      agent:
        name: PreparerAgent
      input:
        messages: =Local.LatestMessage
      output:
        messages: Local.LatestMessage
        autoSend: true
    - kind: SetVariable
      id: set_variable_turncount
      variable: Local.TurnCount
      value: =1
    - kind: InvokeAzureAgent
      id: reviewer_agent
      agent:
        name: Reviewer
      conversationId: =System.ConversationId
      input:
        messages: =Local.LatestMessage
      output:
        autoSend: true
        messages: Local.LatestMessage
        responseObject: Local.LatestMessage
    - kind: SetVariable
      id: node-1777544964399
      variable: Local.LatestMessage
      value: =Last(Local.LatestMessage).Text
    - kind: ConditionGroup
      conditions:
        - condition: =Or(Local.TurnCount >= 2, EndsWith(Local.LatestMessage, "APPROVED"))
          actions:
            - kind: InvokeAzureAgent
              id: preparer_reviewed
              agent:
                name: PreparerAgent
              conversationId: =System.ConversationId
              input:
                messages: =Local.LatestMessage
              output:
                autoSend: true
          id: If-Then
      id: node-1777525298524
      elseActions:
        - kind: SetVariable
          id: node-1777525305638
          variable: Local.TurnCount
          value: =Local.TurnCount + 1
        - kind: InvokeAzureAgent
          id: preparer_redo
          agent:
            name: PreparerAgent
          conversationId: =System.ConversationId
          input:
            messages: =Local.LatestMessage
          output:
            autoSend: true
        - kind: GotoAction
          actionId: reviewer_agent
          id: node-1777525366772
    - kind: InvokeAzureAgent
      id: supervisor_review
      agent:
        name: Supervisor
      conversationId: =System.ConversationId
      input:
        messages: =Local.LatestMessage
      output:
        autoSend: true
    - kind: Question
      variable: Local.LatestMessage
      id: node-1777524890260
      entity: StringPrebuiltEntity
      skipQuestionMode: SkipOnFirstExecutionIfVariableHasValue
      prompt: Is this acceptable?
    - kind: InvokeAzureAgent
      id: Formatter
      agent:
        name: Formatter
      conversationId: =System.ConversationId
      input:
        messages: =Local.LatestMessage
      output:
        autoSend: true
    - kind: EndConversation
      id: node-1777524976770
id: ""
name: safe-agents
description: ""
```

## SDK Code

```python
import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ResponseStreamEventType


endpoint = "https://tatum-safeagents-resource.services.ai.azure.com/api/projects/tatum-safeagents"

project_client = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
)

with project_client:

    workflow = {
        "name": "safe-agents",
        "version": "41",
    }
    
    openai_client = project_client.get_openai_client()

    conversation = openai_client.conversations.create()
    print(f"Created conversation (id: {conversation.id})")

    stream = openai_client.responses.create(
        conversation=conversation.id,
        extra_body={"agent_reference": {"name": workflow["name"], "type": "agent_reference"}},
        input="Hi safe-agents",
        stream=True,
        metadata={"x-ms-debug-mode-enabled": "1"},
    )

    for event in stream:
        if event.type == ResponseStreamEventType.RESPONSE_OUTPUT_TEXT_DONE:
            print("\t", event.text)
        elif event.type == ResponseStreamEventType.RESPONSE_OUTPUT_ITEM_ADDED and event.item.type == "workflow_action":
            print(f"********************************\nActor - '{event.item.action_id}' :")
        elif event.type == ResponseStreamEventType.RESPONSE_OUTPUT_ITEM_ADDED and event.item.type == "workflow_action":
            print(f"Workflow Item '{event.item.action_id}' is '{event.item.status}' - (previous item was : '{event.item.previous_action_id}')")
        elif event.type == ResponseStreamEventType.RESPONSE_OUTPUT_ITEM_DONE and event.item.type == "workflow_action":
            print(f"Workflow Item '{event.item.action_id}' is '{event.item.status}' - (previous item was: '{event.item.previous_action_id}')")
        elif event.type == ResponseStreamEventType.RESPONSE_OUTPUT_TEXT_DELTA:
            print(event.delta)
        else:
            print(f"Unknown event: {event}")

    openai_client.conversations.delete(conversation_id=conversation.id)
    print("Conversation deleted")
```
