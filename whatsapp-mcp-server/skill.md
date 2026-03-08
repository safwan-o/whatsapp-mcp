# WhatsApp Autonomous Agent Skill

This skill allows an LLM to operate as an autonomous assistant via WhatsApp. When this mode is activated, you monitor incoming messages from a whitelist and respond using your available tools.

## How to Activate
1. **Verify Connection**: Ensure the WhatsApp MCP server is connected and the bridge is running.
2. **Set Whitelist**: Identify the phone numbers or JIDs you are allowed to respond to.
3. **Initialize Loop**: Call `get_agent_instructions()` to load the system persona.
4. **Start Listening**: Enter a continuous loop calling `wait_for_message(whitelist=[...])`.

## Operational Loop
1. Call `wait_for_message`.
2. Upon receiving a message:
   - Check `is_exit_command`. If `True`, send a final "Going offline" message and **STOP the loop immediately**.
   - If not an exit command, process the user's request.
   - You may use any of your other skills (terminal, browser, file access) to fulfill the request.
   - Send the result back using `send_message` or `send_file`.
   - **Crucial**: Call `acknowledge_message(message_id=...)` to mark it as handled.
3. Repeat step 1.

## Exit Commands
The following messages from a whitelisted user will trigger an exit:
- `exit agent mode`
- `stop agent`
- `go offline`

## Best Practices
- **Safety**: Do not execute destructive commands (like `rm -rf /`) without explicit confirmation, even from whitelisted users.
- **Privacy**: Only share information that the user is authorized to see.
- **Context**: Maintain a summary of the conversation in your internal state to provide coherent multi-turn assistance.
