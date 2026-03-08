from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
from whatsapp import (
    search_contacts as whatsapp_search_contacts,
    list_messages as whatsapp_list_messages,
    list_chats as whatsapp_list_chats,
    get_chat as whatsapp_get_chat,
    get_direct_chat_by_contact as whatsapp_get_direct_chat_by_contact,
    get_contact_chats as whatsapp_get_contact_chats,
    get_last_interaction as whatsapp_get_last_interaction,
    get_message_context as whatsapp_get_message_context,
    send_message as whatsapp_send_message,
    send_file as whatsapp_send_file,
    send_audio_message as whatsapp_audio_voice_message,
    download_media as whatsapp_download_media,
    listen_for_messages as whatsapp_listen_for_messages,
    acknowledge_message as whatsapp_acknowledge_message,
    mark_as_read as whatsapp_mark_as_read,
    set_presence as whatsapp_set_presence
)

# Initialize FastMCP server
mcp = FastMCP("whatsapp")

@mcp.tool()
def wait_for_message(whitelist: List[str], timeout_seconds: int = 60) -> Optional[Dict[str, Any]]:
    """Poll for new messages from whitelisted contacts.
    
    This tool is the 'Trigger' for autonomous mode. It will block until new 
    messages arrive from the specified JIDs or phone numbers.
    
    Returns a BATCH of messages grouped by chat. You should process all of them.
    
    Args:
        whitelist: List of phone numbers (e.g. '1234567890') or JIDs (e.g. '1234567890@s.whatsapp.net') 
                  that the agent is allowed to respond to.
        timeout_seconds: Maximum time to wait before returning (default 60).
    """
    # Clean whitelist to ensure JID format
    clean_whitelist = []
    for item in whitelist:
        if "@" not in item:
            clean_whitelist.append(f"{item}@s.whatsapp.net")
        else:
            clean_whitelist.append(item)
            
    return whatsapp_listen_for_messages(clean_whitelist, timeout_seconds)

@mcp.tool()
def acknowledge_message(message_id: str) -> str:
    """Mark a message as processed so the agent doesn't respond to it again.
    
    Args:
        message_id: The ID of the message to acknowledge.
    """
    whatsapp_acknowledge_message(message_id)
    return "Message acknowledged."

@mcp.tool()
def mark_as_read(chat_jid: str, message_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """Mark a message or all messages in a chat as read.
    
    Args:
        chat_jid: The JID of the chat (e.g., "123456789@s.whatsapp.net" or "123456789@g.us")
        message_ids: Optional list of message IDs to mark as read. If omitted, all messages in the chat are marked as read.
    """
    success, message = whatsapp_mark_as_read(chat_jid, message_ids)
    return {"success": success, "message": message}

@mcp.tool()
def set_typing(chat_jid: str, is_typing: bool, media_type: str = "text") -> Dict[str, Any]:
    """Show or hide the typing/recording indicator in a chat.
    
    Args:
        chat_jid: The JID of the chat
        is_typing: True to show indicator, False to hide it
        media_type: Type of message being prepared: "text" (typing...) or "audio" (recording audio...)
    """
    success, message = whatsapp_set_presence(chat_jid, is_typing, media_type)
    return {"success": success, "message": message}

@mcp.tool()
def get_agent_instructions() -> str:
    """Get the system prompt and instructions for running in autonomous WhatsApp mode.
    
    Call this tool to understand how to loop and respond to whitelisted users 
    proactively.
    """
    return """
# WhatsApp Autonomous Agent Mode

You are now operating as an autonomous WhatsApp assistant. Your goal is to monitor for incoming 
messages and respond on behalf of the user.

## Operating Loop:
1. Call `wait_for_message(whitelist=[...])` with your allowed contacts.
2. If messages are returned (it returns a BATCH object):
   - The response looks like: `{ "batch_count": 2, "chats": { "jid1": [msg1, msg2], "jid2": [msg3] } }`
   - Iterate through each chat in `chats`.
   - For each chat:
     - Review all new messages.
     - Formulate a response (or responses) based on the context of all messages.
     - Use `send_message` or `send_file` to reply.
     - NOTE: Typing indicators and Read receipts are now AUTOMATED. You do NOT need to call `mark_as_read` or `set_typing` manually.
     - IMPORTANT: Call `acknowledge_message(message_id=...)` for EACH processed message ID to prevent loops.
3. Repeat the loop.

## Security & Privacy:
- ONLY respond to users in the whitelist.
- You have access to the user's local filesystem and tools. Be helpful but cautious.
- If unsure about a request, ask for clarification via WhatsApp.
"""

@mcp.tool()
def search_contacts(query: str) -> List[Dict[str, Any]]:
    """Search WhatsApp contacts by name or phone number.
    
    Args:
        query: Search term to match against contact names or phone numbers
    """
    contacts = whatsapp_search_contacts(query)
    return contacts

@mcp.tool()
def list_messages(
    after: Optional[str] = None,
    before: Optional[str] = None,
    sender_phone_number: Optional[str] = None,
    chat_jid: Optional[str] = None,
    query: Optional[str] = None,
    limit: int = 20,
    page: int = 0,
    include_context: bool = True,
    context_before: int = 1,
    context_after: int = 1
) -> List[Dict[str, Any]]:
    """Get WhatsApp messages matching specified criteria with optional context.
    
    Args:
        after: Optional ISO-8601 formatted string to only return messages after this date
        before: Optional ISO-8601 formatted string to only return messages before this date
        sender_phone_number: Optional phone number to filter messages by sender
        chat_jid: Optional chat JID to filter messages by chat
        query: Optional search term to filter messages by content
        limit: Maximum number of messages to return (default 20)
        page: Page number for pagination (default 0)
        include_context: Whether to include messages before and after matches (default True)
        context_before: Number of messages to include before each match (default 1)
        context_after: Number of messages to include after each match (default 1)
    """
    messages = whatsapp_list_messages(
        after=after,
        before=before,
        sender_phone_number=sender_phone_number,
        chat_jid=chat_jid,
        query=query,
        limit=limit,
        page=page,
        include_context=include_context,
        context_before=context_before,
        context_after=context_after
    )
    return messages

@mcp.tool()
def list_chats(
    query: Optional[str] = None,
    limit: int = 20,
    page: int = 0,
    include_last_message: bool = True,
    sort_by: str = "last_active"
) -> List[Dict[str, Any]]:
    """Get WhatsApp chats matching specified criteria.
    
    Args:
        query: Optional search term to filter chats by name or JID
        limit: Maximum number of chats to return (default 20)
        page: Page number for pagination (default 0)
        include_last_message: Whether to include the last message in each chat (default True)
        sort_by: Field to sort results by, either "last_active" or "name" (default "last_active")
    """
    chats = whatsapp_list_chats(
        query=query,
        limit=limit,
        page=page,
        include_last_message=include_last_message,
        sort_by=sort_by
    )
    return chats

@mcp.tool()
def get_chat(chat_jid: str, include_last_message: bool = True) -> Dict[str, Any]:
    """Get WhatsApp chat metadata by JID.
    
    Args:
        chat_jid: The JID of the chat to retrieve
        include_last_message: Whether to include the last message (default True)
    """
    chat = whatsapp_get_chat(chat_jid, include_last_message)
    return chat

@mcp.tool()
def get_direct_chat_by_contact(sender_phone_number: str) -> Dict[str, Any]:
    """Get WhatsApp chat metadata by sender phone number.
    
    Args:
        sender_phone_number: The phone number to search for
    """
    chat = whatsapp_get_direct_chat_by_contact(sender_phone_number)
    return chat

@mcp.tool()
def get_contact_chats(jid: str, limit: int = 20, page: int = 0) -> List[Dict[str, Any]]:
    """Get all WhatsApp chats involving the contact.
    
    Args:
        jid: The contact's JID to search for
        limit: Maximum number of chats to return (default 20)
        page: Page number for pagination (default 0)
    """
    chats = whatsapp_get_contact_chats(jid, limit, page)
    return chats

@mcp.tool()
def get_last_interaction(jid: str) -> str:
    """Get most recent WhatsApp message involving the contact.
    
    Args:
        jid: The JID of the contact to search for
    """
    message = whatsapp_get_last_interaction(jid)
    return message

@mcp.tool()
def get_message_context(
    message_id: str,
    before: int = 5,
    after: int = 5
) -> Dict[str, Any]:
    """Get context around a specific WhatsApp message.
    
    Args:
        message_id: The ID of the message to get context for
        before: Number of messages to include before the target message (default 5)
        after: Number of messages to include after the target message (default 5)
    """
    context = whatsapp_get_message_context(message_id, before, after)
    return context

@mcp.tool()
def send_message(
    recipient: str,
    message: str
) -> Dict[str, Any]:
    """Send a WhatsApp message to a person or group. For group chats use the JID.

    Args:
        recipient: The recipient - either a phone number with country code but no + or other symbols,
                 or a JID (e.g., "123456789@s.whatsapp.net" or a group JID like "123456789@g.us")
        message: The message text to send
    
    Returns:
        A dictionary containing success status and a status message
    """
    # Validate input
    if not recipient:
        return {
            "success": False,
            "message": "Recipient must be provided"
        }
    
    # Call the whatsapp_send_message function with the unified recipient parameter
    success, status_message = whatsapp_send_message(recipient, message)
    return {
        "success": success,
        "message": status_message
    }

@mcp.tool()
def send_file(recipient: str, media_path: str) -> Dict[str, Any]:
    """Send a file such as a picture, raw audio, video or document via WhatsApp to the specified recipient. For group messages use the JID.
    
    Args:
        recipient: The recipient - either a phone number with country code but no + or other symbols,
                 or a JID (e.g., "123456789@s.whatsapp.net" or a group JID like "123456789@g.us")
        media_path: The absolute path to the media file to send (image, video, document)
    
    Returns:
        A dictionary containing success status and a status message
    """
    
    # Call the whatsapp_send_file function
    success, status_message = whatsapp_send_file(recipient, media_path)
    return {
        "success": success,
        "message": status_message
    }

@mcp.tool()
def send_audio_message(recipient: str, media_path: str) -> Dict[str, Any]:
    """Send any audio file as a WhatsApp audio message to the specified recipient. For group messages use the JID. If it errors due to ffmpeg not being installed, use send_file instead.
    
    Args:
        recipient: The recipient - either a phone number with country code but no + or other symbols,
                 or a JID (e.g., "123456789@s.whatsapp.net" or a group JID like "123456789@g.us")
        media_path: The absolute path to the audio file to send (will be converted to Opus .ogg if it's not a .ogg file)
    
    Returns:
        A dictionary containing success status and a status message
    """
    success, status_message = whatsapp_audio_voice_message(recipient, media_path)
    return {
        "success": success,
        "message": status_message
    }

@mcp.tool()
def download_media(message_id: str, chat_jid: str) -> Dict[str, Any]:
    """Download media from a WhatsApp message and get the local file path.
    
    Args:
        message_id: The ID of the message containing the media
        chat_jid: The JID of the chat containing the message
    
    Returns:
        A dictionary containing success status, a status message, and the file path if successful
    """
    file_path = whatsapp_download_media(message_id, chat_jid)
    
    if file_path:
        return {
            "success": True,
            "message": "Media downloaded successfully",
            "file_path": file_path
        }
    else:
        return {
            "success": False,
            "message": "Failed to download media"
        }

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')