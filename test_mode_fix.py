"""
Test Mode Fix for app.py
This patch fixes the TEST_MODE logic issues in perform_dataroom_analysis function
"""

def perform_dataroom_analysis_fixed(client, channel_id, user_id, drive_link, message_ts):
    """Perform the complete data room analysis with AI - FIXED VERSION"""
    try:
        import os
        test_mode_value = os.getenv('TEST_MODE', 'false')
        logger.info(f"🔍 DEBUG - Starting analysis for user {user_id}")
        logger.info(f"🔍 DEBUG - TEST_MODE environment variable: '{test_mode_value}'")
        logger.info(f"🔍 DEBUG - TEST_MODE lower: '{test_mode_value.lower()}'")
        
        # FIX: Define test_mode_check at the beginning
        test_mode_check = test_mode_value.lower() == 'true'
        logger.info(f"🔍 DEBUG - Test mode enabled: {test_mode_check}")

        # Step 1: Download documents
        client.chat_update(
            channel=channel_id,
            ts=message_ts,
            text="🔍 **Analysis in Progress**\n\n" +
                 f"📁 Link: {drive_link}\n" +
                 f"📥 **Downloading documents from Google Drive...**"
        )

        downloaded_files = drive_handler.download_dataroom(drive_link)

        if not downloaded_files:
            client.chat_update(
                channel=channel_id,
                ts=message_ts,
                text="❌ **Analysis Failed**\n\n" +
                     "No supported documents found in the Google Drive folder.\n" +
                     "Supported formats: PDF, Excel, Word, CSV, TXT"
            )
            return

        # Step 2: Process documents
        client.chat_update(
            channel=channel_id,
            ts=message_ts,
            text="🔍 **Analysis in Progress**\n\n" +
                 f"📄 Found {len(downloaded_files)} documents\n" +
                 f"📖 **Processing document contents...**"
        )

        processed_documents = doc_processor.process_dataroom_documents(downloaded_files)
        document_summary = doc_processor.get_content_summary(processed_documents)

        # Check for test mode - skip expensive AI analysis
        if test_mode_check:
            logger.info("🧪 TEST MODE: Skipping AI analysis, using mock session data")
            # Create mock response
            mock_response = "✅ **ANALYSIS COMPLETE (TEST MODE)**\n\n"
            mock_response += f"📊 **Processing Summary:**\n"
            mock_response += f"• **Documents Processed:** {len(processed_documents)}\n"
            mock_response += f"• **Total Content:** Successfully extracted\n\n"
            mock_response += "🎯 **Available Commands:**\n"
            mock_response += "• `/ask [question]` - Ask questions about documents\n"
            mock_response += "• `/scoring` - Get VC scoring\n"
            mock_response += "• `/memo` - Generate investment memo\n"
            mock_response += "• `/gaps` - Analyze information gaps\n"
            mock_response += "• `/market-research` - NEW: Market intelligence (TEST)\n"
            mock_response += "• `/reset` - Clear session\n"

            client.chat_update(
                channel=channel_id,
                ts=message_ts,
                text=mock_response
            )

            # Store mock session data
            user_sessions[user_id] = {
                'processed_documents': processed_documents,
                'document_summary': document_summary,
                'drive_link': drive_link,
                'test_mode': True
            }

            # IMPORTANT: Don't cleanup temp files in test mode until reset
            logger.info(f"✅ Analysis completed (TEST MODE) for user {user_id}")
            logger.info("📁 Keeping temp files for session persistence")
            return

        # Step 3: AI Analysis (if configured and not in test mode)
        if ai_analyzer and config.openai_configured:
            client.chat_update(
                channel=channel_id,
                ts=message_ts,
                text="🔍 **Analysis in Progress**\n\n" +
                     f"📄 Processed {document_summary['successful_processing']} documents\n" +
                     f"🧠 **Analyzing with AI (GPT-4)...**"
            )

            analysis_result = ai_analyzer.analyze_dataroom(processed_documents, document_summary)

            # Format and send AI analysis response
            formatted_response = format_analysis_response(analysis_result, document_summary)

            # Enhanced response to mention market research
            if market_research_orchestrator:
                formatted_response += "\n\n🎯 **NEW: Market Research Available!**\n"
                formatted_response += "Use `/market-research` for comprehensive market intelligence analysis."

            client.chat_update(
                channel=channel_id,
                ts=message_ts,
                text=formatted_response
            )

            # CRITICAL: Store analysis in user session BEFORE cleanup
            user_sessions[user_id] = {
                'analysis_result': analysis_result,
                'document_summary': document_summary,
                'processed_documents': processed_documents,
                'drive_link': drive_link
            }

        else:
            # Fallback: Document processing only
            client.chat_update(
                channel=channel_id,
                ts=message_ts,
                text="🔍 **Analysis in Progress**\n\n" +
                     f"📄 Processed {document_summary['successful_processing']} documents\n" +
                     f"⚠️ **AI analysis disabled** - showing document processing results"
            )

            response = format_processing_results(processed_documents, document_summary, drive_link)

            client.chat_update(
                channel=channel_id,
                ts=message_ts,
                text=response
            )

            # CRITICAL: Store documents in user session BEFORE cleanup
            user_sessions[user_id] = {
                'processed_documents': processed_documents,
                'document_summary': document_summary,
                'drive_link': drive_link
            }

        # Only cleanup if not in test mode
        if not test_mode_check:
            logger.info("✅ AI analysis completed successfully")
            drive_handler.cleanup_temp_files()
            logger.info("🗑️ Cleaned up temporary files")
            logger.info("💾 Freed temp storage: ./temp")
        else:
            logger.info("📁 TEST MODE: Keeping temp files for session")

        logger.info(f"✅ Analysis completed for user {user_id}")

    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        client.chat_update(
            channel=channel_id,
            ts=message_ts,
            text=format_error_response("analysis", str(e))
        )
