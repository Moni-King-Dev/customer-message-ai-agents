
import os
from dotenv import load_dotenv
from google import genai

# ==========================================
# 1. CONNECT TO GEMINI
# ==========================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)
MODEL = "gemini-3.8-flash"


def ask_ai(prompt):
    """Send a prompt to Gemini and return its response."""

    response = client.interactions.create(
        model=MODEL,
        input=prompt
    )

    if not response.output_text:
        raise RuntimeError("Gemini returned an empty response.")

    return response.output_text.strip()


# ==========================================
# 2. REFLECTION AGENT
# ==========================================

def reflection_agent():

    print("\n======================================")
    print(" CUSTOMER MESSAGE REFLECTION AGENT")
    print("======================================\n")

    # STEP 1: Collect customer information

    company = input("Company or shop name: ").strip()
    product = input("Product or service: ").strip()
    issue = input("Explain your issue or request: ").strip()

    if not company or not product or not issue:
        print("All fields are required.")
        return

    # STEP 2: Generate the initial draft

    draft_prompt = f"""
You are helping a CUSTOMER write a message TO a company.

Company: {company}
Product or service: {product}
Customer's issue or request: {issue}

Write a clear, polite, natural message from the customer's
point of view.

Rules:
- The customer is writing to the company.
- Use first-person wording where appropriate.
- Do not write as the company or shop.
- Do not invent purchases, order numbers, dates, or facts.
- Do not claim that an action has already happened.
- Return only the message.
"""

    try:
        print("\n[AI] Generating the initial draft...")
        draft = ask_ai(draft_prompt)
    except Exception as error:
        print("[Error] Draft generation failed:", error)
        return

    print("\n========== INITIAL DRAFT ==========")
    print(draft)
    print("===================================\n")

    # STEP 3: AI reflects on its own draft

    reflection_prompt = f"""
You are reviewing a draft written by a CUSTOMER to a company.

Company: {company}
Product or service: {product}
Customer's original issue:
{issue}

Draft to review:
{draft}

Evaluate the draft for:
1. Does it represent the customer's point of view?
2. Is the request clear?
3. Is the tone appropriate?
4. Does it contain unsupported or invented facts?
5. Does it address the company rather than reply as the company?

Give a brief review and identify specific improvements.
Do not invent any facts.
"""

    try:
        print("[AI] Reflecting on its draft...")
        reflection = ask_ai(reflection_prompt)
    except Exception as error:
        print("[Error] Reflection failed:", error)
        return

    print("\n========== SELF-REFLECTION ==========")
    print(reflection)
    print("=====================================\n")

    # STEP 4: Improve the draft using the reflection

    improvement_prompt = f"""
You are helping a CUSTOMER write a message TO a company.

Company: {company}
Product or service: {product}
Customer's original issue:
{issue}

Initial draft:
{draft}

Review and improvement suggestions:
{reflection}

Rewrite the draft to address the identified weaknesses.

Rules:
- Write from the customer's point of view.
- Address the company or its support team.
- Keep the original purpose of the request.
- Use a clear, natural, appropriate tone.
- Do not invent facts or make unsupported claims.
- Do not write as the company.
- Return only the improved message.
- Do not send the message.
"""

    try:
        print("[AI] Improving the draft...")
        improved_draft = ask_ai(improvement_prompt)
    except Exception as error:
        print("[Error] Improvement failed:", error)
        return

    # STEP 5: Display the improved result

    print("\n========== IMPROVED MESSAGE ==========")
    print(improved_draft)
    print("======================================\n")

    # STEP 6: Customer remains in control

    choice = input(
        "Use this draft? (YES / NO): "
    ).strip().upper()

    if choice == "YES":
        print("\n[Agent] Draft accepted by the customer.")
        print("You can copy it and send it yourself.")
    else:
        print("\n[Agent] Draft not accepted.")

    print("[Agent] No message was sent automatically.")


# ==========================================
# 3. START THE AGENT
# ==========================================

if __name__ == "__main__":
    try:
        reflection_agent()
    except Exception as error:
        print("[Error]", error)
