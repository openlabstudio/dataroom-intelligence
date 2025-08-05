# Also register a short variant
@app.command("/market")
def handle_market_command_short(ack, body, client):
    """Handle /market command (short variant)"""
    logger.info("📨 Received /market command (short variant)")
    handle_market_research_logic(ack, body, client)

# Debug command to check sessions
@app.command("/debug-sessions")
def handle_debug_sessions_command(ack, body, client):
    """Handle /debug-sessions command - Check active sessions"""
    ack()
    
    try:
        user_id = body['user_id']
        channel_id = body['channel_id']
        
        logger.info(f"🔍 Debug sessions command from user {user_id}")
        
        response = "🔍 **DEBUG: ACTIVE SESSIONS**\n\n"
        response += f"**Total Sessions:** {len(user_sessions)}\n"
        response += f"**Active Users:** {list(user_sessions.keys())}\n\n"
        
        if user_id in user_sessions:
            session_data = user_sessions[user_id]
            response += f"**Your Session (ID: {user_id}):**\n"
            response += f"• Session keys: {list(session_data.keys())}\n"
            
            if 'processed_documents' in session_data:
                response += f"• Processed documents: {len(session_data['processed_documents'])}\n"
            
            if 'document_summary' in session_data:
                response += f"• Document summary available: ✅\n"
            
            if 'analysis_result' in session_data:
                response += f"• Analysis result available: ✅\n"
                
            response += "\n✅ **Market research should work!**"
        else:
            response += f"**Your Session (ID: {user_id}):** ❌ Not found\n"
            response += "\n⚠️ **Please run `/analyze [link]` first**"
        
        client.chat_postMessage(
            channel=channel_id,
            text=response
        )
        
    except Exception as e:
        logger.error(f"❌ Error in debug-sessions command: {e}")
        client.chat_postMessage(
            channel=channel_id,
            text=f"❌ Debug error: {str(e)}"
        )