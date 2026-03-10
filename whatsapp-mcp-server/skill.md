# WhatsApp Autonomous Agent Skill

This skill allows an LLM to operate as an autonomous assistant via WhatsApp. When this mode is activated, you monitor incoming messages from a whitelist and respond using your available tools.

## 🔴 CRITICAL PRIORITY: STARTUP & LOOP
**The `wait_for_message` tool is your highest priority.** 
- In a new session, call `wait_for_message` **immediately** after verifying the connection. 
- Do **not** wait for profile fetching or timezone setup if the user has already requested agent mode.
- You must remain in the `wait_for_message` loop at all times when not actively processing a batch.

## How to Activate
1. **Verify Connection**: Ensure the WhatsApp MCP server is connected.
2. **Set Whitelist**: Identify the JIDs or phone numbers allowed.
   - If using phone numbers, call `resolve_whitelist(identifiers=[...])` **once** to get valid JIDs.
3. **Initialize & Listen**: Call `wait_for_message(whitelist=[...])` immediately. 
   - **Note**: You should load agent persona/instructions (e.g. from `get_agent_instructions`) *during* the first processing turn or as a quick preliminary step, but do not let it delay the first poll if messages are expected.

## Operational Loop
1. Call `wait_for_message` (High Priority).
2. Upon receiving a **Batch** of messages:
   - The response contains `batch_count` and a `chats` dictionary mapping JIDs to lists of message objects.
   - **Automated Features**: Read receipts and typing indicators are now automated. Messages are marked as read when retrieved, and typing status is shown while you process a response.
   - **Contextual Processing**: Review all messages in the batch for a given chat to understand the full context.
   - **Execution**: Process each user request using your available skills (terminal, browser, file access, search).
   - **Reply Feature**: Use the `reply_to_id` parameter in `send_message` or `send_file` to quote a specific message for clarity. Avoid over-quoting; use it mainly for specific questions or in busy threads.
   - **Crucial**: Call `acknowledge_message(message_id=...)` for **EACH** message in the batch to prevent them from being returned in the next poll.
   - Check `is_exit_command` for each message. If `True`, send a final "Going offline" message and **STOP the loop immediately**.
3. Repeat step 1.

## Exit Commands
The following messages from a whitelisted user will trigger an exit:
- `exit agent mode`
- `stop agent`
- `go offline`

## Best Practices
- **Safety**: Do not execute destructive commands (like `rm -rf /`) without explicit confirmation, even from whitelisted users.
- **Efficiency**: Use batch processing to send a single comprehensive reply to multiple messages when appropriate.
- **Professionalism**: Keep quotes sparse for a more natural conversation flow.
- **Privacy**: Only share information that the user is authorized to see.
