    def single_pass_analysis(self, pdf_path: str, file_name: str) -> Dict[str, Any]:
        """
        Single-pass VC analyst summary - Option A approach
        Direct PDF to analyst summary without extract-then-analyze pattern
        """
        logger.info(f"🎯 Starting single-pass analysis for: {file_name}")

        try:
            # Upload file
            logger.info(f"📤 Uploading {file_name} for single-pass analysis...")
            with open(pdf_path, 'rb') as f:
                file_obj = self.client.files.create(file=f, purpose='assistants')
            logger.info(f"✅ File uploaded successfully: {file_obj.id}")

            # Single comprehensive prompt for VC analysis
            analyst_prompt = """You are a senior venture capital analyst. Analyze this startup pitch deck and produce a comprehensive investment analysis.

REQUIREMENTS:
1. Extract EVERY piece of financial data, especially valuations (pre-money, post-money)
2. Include ALL metrics with specific numbers and time periods
3. Reference slide/page numbers for each fact
4. Use the exact format below

OUTPUT FORMAT:

EXECUTIVE SUMMARY
[One paragraph with company description, key traction metric, and current funding round WITH VALUATION]

COMPANY
• [What the company does] [Page X]
• [Vision/Mission] [Page X]
• [Locations if stated] [Page X]

BUSINESS MODEL
• [Type: B2B/B2C/etc.] [Page X]
• [Revenue model with specific pricing] [Page X]
• [Key offerings: freemium/premium details] [Page X]

METRICS & TRACTION
• [TAM/SAM/SOM with specific amounts] [Page X]
• [Growth metrics with percentages] [Page X]
• [User/merchant/transaction numbers] [Page X]
• [GMV/Revenue with amounts and periods] [Page X]
• [Any other KPIs] [Page X]

TEAM & FUNDING
• [Current round: amount and valuation - MUST INCLUDE VALUATION IF PRESENT] [Page X]
• [Team size] [Page X]
• [Founders with backgrounds] [Page X]
• [Projections post-funding] [Page X]

CUSTOMERS / LOGOS
• [List of notable customers] [Page X]

CRITICAL GAPS
• [Missing information that would be needed for investment decision]

IMPORTANT:
- Extract ALL financial figures with currency symbols and time periods
- Include exact numbers from the deck, don't round or approximate
- Pay special attention to valuations, funding amounts, and growth metrics"""

            logger.info("🧠 Processing with single-pass analysis...")
            response = self.client.chat.completions.create(
                model='gpt-4o',
                messages=[{
                    'role': 'user',
                    'content': [
                        {'type': 'text', 'text': analyst_prompt},
                        {'type': 'file', 'file': {'file_id': file_obj.id}}
                    ]
                }],
                max_tokens=4000,
                temperature=0.1
            )

            analysis = response.choices[0].message.content
            logger.info(f"✅ Single-pass analysis completed ({len(analysis)} chars)")

            # Clean up
            self.client.files.delete(file_obj.id)
            logger.info(f"🧹 Temporary file cleaned up")

            return {
                'name': file_name,
                'type': 'pdf',
                'content': analysis,
                'analyst_summary': analysis,  # For compatibility
                'metadata': {
                    'extraction_method': 'single_pass_analysis',
                    'has_content': True,
                    'processing_time': 'single_pass'
                }
            }

        except Exception as e:
            logger.error(f"❌ Single-pass analysis failed for {file_name}: {e}")
            return {
                'name': file_name,
                'type': 'pdf',
                'content': '',
                'error': str(e),
                'metadata': {
                    'extraction_method': 'single_pass_failed',
                    'has_content': False,
                    'error': str(e)
                }
            }