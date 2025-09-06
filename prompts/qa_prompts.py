"""
Q&A and specialized prompts for DataRoom Intelligence Bot
FIXED VERSION - Gaps analysis error resolved
"""

QA_PROMPT = """
You are an expert analyst who has just completed a comprehensive data room analysis. Answer the following question based EXCLUSIVELY on the documents you have analyzed.

EXTRACTED FINANCIAL DATA (CONFIRMED TO BE PRESENT):
{extracted_financials}

CONTEXT OF ANALYZED DATA ROOM:
{analyzed_documents_summary}

USER QUESTION:
{user_question}

INSTRUCTIONS:
- ALWAYS check the EXTRACTED FINANCIAL DATA first before answering financial questions
- If funding, KPIs, or P&L data are listed in EXTRACTED FINANCIAL DATA, they ARE present in the documents
- Respond specifically and practically based on available data
- Cite specific documents when relevant
- If specific details are not available, acknowledge what IS available from extracted data
- Maintain perspective of experienced VC analyst
- Maximum 200 words per response

RESPONSE:
"""

MEMO_PROMPT = """
You are a senior partner at a VC firm writing an investment memo for the partnership based on data room analysis.

ANALYSIS SUMMARY:
{analysis_summary}

DOCUMENT CONTEXT:
{document_context}

Generate a structured investment memo with the following sections:

**COMPANY SUMMARY**
[Brief company description and what they do]

**INVESTMENT THESIS**
[Why this could be a good investment - 2-3 key points]

**KEY STRENGTHS & OPPORTUNITIES**
[Main competitive advantages and market opportunities]

**RISK FACTORS & MITIGATION**
[Primary risks and how they might be addressed]

**FINANCIAL ANALYSIS**
[Revenue, growth, unit economics based on available data]

**RECOMMENDATION**
[Pass/Investigate/No Go with clear reasoning]

**NEXT STEPS**
[Specific actions for further due diligence]

Keep the memo concise but comprehensive. Focus on actionable insights that will help the partnership make an investment decision.
"""

# FIXED: Remove {detected_stage} variable that was causing the error
GAPS_PROMPT = """
As a VC expert, identify what critical information is missing from this data room for a complete due diligence evaluation.

AVAILABLE DOCUMENTS:
{available_documents}

CONTENT SUMMARY:
{content_summary}

Based on the documents provided, analyze what stage this company appears to be at (Seed, Series A, Series B, etc.) and identify critical gaps.

CRITICAL GAPS IDENTIFIED:

**FINANCIALS:**
[Missing financial documents critical for this investment stage]

**LEGAL & COMPLIANCE:**
[Missing legal documentation]

**PRODUCT/MARKET:**
[Missing market analysis or product specifications]

**TEAM:**
[Missing team information]

**OPERATIONS:**
[Missing operational metrics or customer contracts]

**CUSTOMER VALIDATION:**
[Missing customer data or validation materials]

PRIORITY OF GAPS (CRITICAL/IMPORTANT/NICE-TO-HAVE):

**CRITICAL** (Deal blockers):
- [List items that prevent investment decision]

**IMPORTANT** (Needed for final decision):
- [List items needed before term sheet]

**NICE-TO-HAVE** (Helpful but not essential):
- [List items that would strengthen the case]

**RECOMMENDED REQUESTS:**
[Specific documents/information to request from the company]

**STAGE ASSESSMENT:**
[Based on available documents, what investment stage does this appear to be, and what documents are typically expected at this stage]
"""
