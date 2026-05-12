import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def generate_llm_response(user_query, analytics_context):

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

    return response.choices[0].message.content