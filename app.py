def handle_market_research_logic(ack, body, client):
    """Shared logic for market research command variants"""
    ack()
    
    try:
        user_id = body['user_id']
        channel_id = body['channel_id']
        
        logger.info(f"🔍 Market research command received from user {user_id} in channel {channel_id}")
        
        # DEBUGGING: Log current session state
        logger.info(f"🔍 Active sessions: {list(user_sessions.keys())}")
        logger.info(f"🔍 Total active sessions: {len(user_sessions)}")
        
        if user_id in user_sessions:
            session_keys = list(user_sessions[user_id].keys())
            logger.info(f"🔍 User {user_id} session contains: {session_keys}")
        else:
            logger.warning(f"❌ User {user_id} not found in sessions")
        
        # Check if user has analyzed documents
        if user_id not in user_sessions:
            logger.warning(f"❌ No session found for user {user_id}")
            client.chat_postMessage(
                channel=channel_id,
                text="❌ No data room analysis found. Please run `/analyze [google-drive-link]` first to analyze documents before market research.\n\n**Debug Info:** No active session found. Please ensure you've completed the `/analyze` command successfully first."
            )
            return
        
        if not market_research_orchestrator or not config.openai_configured:
            logger.warning("❌ Market research orchestrator not available")
            client.chat_postMessage(
                channel=channel_id,
                text="❌ Market research requires OpenAI configuration. Please configure OpenAI API key."
            )
            return
        
        # Get processed documents from session
        processed_documents = user_sessions[user_id].get('processed_documents', [])
        document_summary = user_sessions[user_id].get('document_summary', {})
        
        logger.info(f"🔍 Found {len(processed_documents)} processed documents for user {user_id}")
        logger.info(f"🔍 Document summary keys: {list(document_summary.keys()) if document_summary else 'None'}")
        
        if not processed_documents:
            logger.warning(f"❌ No processed documents found for user {user_id}")
            client.chat_postMessage(
                channel=channel_id,
                text="❌ No processed documents found. Please run `/analyze` first.\n\n**Debug Info:** Session exists but no processed documents found."
            )
            return
        
        logger.info(f"✅ Starting market research for user {user_id} with {len(processed_documents)} documents")
        
        # Send initial response with progress tracking
        initial_response = client.chat_postMessage(
            channel=channel_id,
            text=format_market_research_progress("started", processed_documents, document_summary)
        )
        
        # Start background market research processing
        threading.Thread(
            target=perform_market_research_analysis,
            args=(client, channel_id, user_id, processed_documents, document_summary, initial_response['ts']),
            daemon=True
        ).start()
        
    except Exception as e:
        logger.error(f"❌ Error in market-research command: {e}")
        import traceback
        logger.error(f"❌ Full traceback: {traceback.format_exc()}")
        client.chat_postMessage(
            channel=channel_id,
            text=format_error_response("market-research", str(e))
        )