# WhatsApp Autonomous Agent Skill

This skill allows an LLM to operate as an autonomous assistant via WhatsApp. When this mode is activated, you monitor incoming messages from a whitelist and respond using your available tools.

## How to Activate
1. **Verify Connection**: Ensure the WhatsApp MCP server is connected and the bridge is running.
2. **Set Whitelist**: Identify the phone numbers or JIDs you are allowed to respond to.
   - **Tip**: WhatsApp uses different identifiers (JIDs) like `@s.whatsapp.net` and `@lid`.
   - **Recommendation**: Use the `resolve_whitelist(identifiers=[...])` tool with your phone numbers to get all valid JIDs for those contacts.
3. **Initialize Loop**: Call `get_agent_instructions()` to load the system persona and best practices.
4. **Start Listening**: Enter a continuous loop calling `wait_for_message(whitelist=[...])` using the resolved JIDs.

## Operational Loop
1. Call `wait_for_message`.
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
