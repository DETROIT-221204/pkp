import requests, json
def generate_ai_advice(company):
    """Handles the OpenRouter API logic and returns formatted AI advice."""


    API_KEY = ""

    if not company:
        return "⚠️ Please provide a valid company name."

    user_message = f"Should I invest in {company}?"

    structured_prompt = f"""
    Reformat the answer in a clear, structured way using Markdown:

    - Start with a short introduction.
    - Use ### Headings for sections.
    - Use bullet points (-) or numbered lists where appropriate.
    - If there are Pros and Cons, format them in a Markdown table.
    - End with a clear **Bottom Line**.

    User Question: {user_message}
    """

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5000",
            "X-Title": "DhanGyan Investment Advisor",
        },
        data=json.dumps({
            "model": "nvidia/nemotron-nano-9b-v2:free",
            "messages": [
                {"role": "user", "content": structured_prompt}
            ],
        }),
    )

    if response.status_code != 200:
        return f"❌ API Error: {response.text}"

    response_data = response.json()
    message = (
        response_data.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
    )

    return message.strip() or "⚠️ No response from AI."
