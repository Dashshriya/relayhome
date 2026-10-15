# Product notes

## The problem

Care coordination is often a string of small jobs spread across family chats, reminders, and someone's memory. A missed pickup or check-in can happen even when everyone is trying to help.

## What RelayHome does

A family member describes what needs to happen. RelayHome drafts a short list of practical tasks and check-ins. The person coordinating reviews the details, approves the plan, and can see what was saved in the shared list.

## What to demonstrate

The important interaction is the pause before action: the app proposes a plan, shows the details, and waits for approval. After approval, it records the changes and shows them in the activity feed.

## Boundaries

- The planner uses deterministic local rules; it is not an LLM.
- Names and household records are fictional.
- The prototype does not send messages, write to calendars, or provide medical advice.
- The current task state lives in memory and resets when the MCP server restarts.

## Next steps

1. Verify MCP initialize, tool listing, and tool calls in the target environment.
2. Test the full approval and task-completion flow in a browser.
3. Add an easy demo reset and clearer tool-call visibility.
4. Capture a short demo using only verified behavior.
