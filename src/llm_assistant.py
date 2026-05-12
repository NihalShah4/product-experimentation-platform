"""
llm_assistant.py

Purpose:
Provides LLM-powered strategic analytics interpretation
for the Product Intelligence Platform.

Core Responsibilities:
- translate analytics metrics into business narratives
- provide executive-facing recommendations
- summarize experimentation outcomes
- support product decision-making workflows

LLM Provider:
- OpenAI API

Current Model:
- gpt-4.1-mini

Design Philosophy:
The LLM layer is intentionally positioned as:
- an interpretation system
- not a source-of-truth analytics engine

All numerical analytics are computed locally using:
- PostgreSQL
- pandas
- statistical methods

The LLM is used only for:
- summarization
- reasoning
- communication
- recommendation framing

This separation mirrors real-world analytics architecture.
"""

import os

from dotenv import load_dotenv
from openai import OpenAI


# =========================================================
# ENVIRONMENT CONFIGURATION
# =========================================================

load_dotenv()

OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY"
)

client = OpenAI(
    api_key=OPENAI_API_KEY
)


# =========================================================
# LLM-POWERED ANALYTICS INTERPRETATION
# =========================================================

def generate_llm_response(
    user_query,
    analytics_context
):
    """
    Generates an executive-style analytics interpretation
    using structured analytical context plus a user query.

    Parameters:
        user_query (str):
            Strategic analytics question from the user.

        analytics_context (str):
            Structured platform metrics injected into
            the LLM prompt.

    Returns:
        str:
            LLM-generated analytics interpretation.
    """

    # =====================================================
    # PROMPT ENGINEERING
    # =====================================================
    #
    # The prompt is intentionally structured to:
    # - constrain hallucinations
    # - keep responses analytics-focused
    # - encourage business interpretation
    # - generate actionable recommendations
    #
    # The model is explicitly guided toward:
    # - analytical reasoning
    # - product strategy
    # - experimentation interpretation

    prompt = f"""
    You are a senior product analytics analyst.

    Use the analytics context below to answer the user's question.

    Analytics Context:
    {analytics_context}

    User Question:
    {user_query}

    Provide:
    - analytical interpretation
    - business insight
    - recommendation

    Keep the answer concise and professional.
    """

    # =====================================================
    # OPENAI CHAT COMPLETION
    # =====================================================
    #
    # temperature=0.3 is intentionally conservative:
    # - lower hallucination risk
    # - more deterministic responses
    # - better executive consistency

    response = client.chat.completions.create(

        model="gpt-4.1-mini",

        messages=[
            {
                "role": "system",

                "content": (
                    "You are an expert in product analytics, "
                    "experimentation, retention, and growth analytics."
                )
            },

            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.3
    )

    # =====================================================
    # RETURN FINAL RESPONSE
    # =====================================================

    return response.choices[0].message.content