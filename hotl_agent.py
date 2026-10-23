
import os
import json
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
# 2. HUMAN-ON-THE-LOOP CUSTOMER AGENT
# ==========================================

def human_on_the_loop_agent():

    print("\n========================================")
    print("     CUSTOMER MESSAGE ASSISTANT")
    print("     Human-on-the-Loop AI Agent")
    print("========================================\n")

    # STEP 1: Collect information from the customer

    company = input("Company or shop name: ").strip()
    product = input("Product or service: ").strip()

    issue = input(
        "Explain your problem or what you want to ask: "
    ).strip()

    if not company or not product or not issue:
        print("\nAll fields are required. Agent stopped.")
        return

    # STEP 2: Gemini analyzes the customer's situation

    print("\n[AI] Analyzing your request...")

    analysis_prompt = f"""
You are an AI assistant helping a CUSTOMER communicate
with a company or shop.

You represent the customer's perspective, NOT the company.

Customer's recipient company: {company}
Product or service: {product}
Customer's situation: {issue}

Analyze the customer's situation and return ONLY valid JSON
with these exact keys:

{{
  "category": "short issue category",
  "urgency": "LOW, MEDIUM, or HIGH",
  "explanation": "brief explanation of the situation",
  "draft_message": "a message written by the customer to the company",
  "human_review": true,
  "reason": "why human review is or is not recommended"
}}

Rules:
- Write the draft message in first person from the customer's POV.
- Address the company or its customer support team.
- Use "I", "my", and "me" where appropriate.
- Do not write as the shop or company.
- Do not write a reply on behalf of the company.
- Do not invent purchases, order IDs, dates, or other facts.
- Do not claim a refund or other action has already happened.
- Set urgency to LOW, MEDIUM, or HIGH.
- Set human_review to true for serious complaints, payment
  disputes, safety issues, threats, or uncertainty.
- Set human_review to false for routine, straightforward requests.
- The message is a draft. Do not send it.
"""

    try:
        raw_result = ask_ai(analysis_prompt)
        result = json.loads(raw_result)

    except (json.JSONDecodeError, TypeError, ValueError) as error:
        print("\n[Monitor] The AI response could not be verified.")
        print("[Monitor] Please review the result manually.")
        print("Details:", error)
        return

    # STEP 3: Display the analysis and customer's draft

    print("\n========== AI ANALYSIS ==========")
    print("Company:", company)
    print("Product/service:", product)
    print("Category:", result.get("category", "Unknown"))
    print("Urgency:", result.get("urgency", "Unknown"))
    print("Explanation:", result.get("explanation", "Not provided"))
    print("=================================\n")

    draft = result.get("draft_message", "")

    if not isinstance(draft, str) or not draft.strip():
        print("[Monitor] No valid draft was generated.")
        print("[Monitor] Human review is required.")
        return

    print("======= YOUR MESSAGE TO THE COMPANY =======")
    print(draft)
    print("===========================================\n")

    # STEP 4: Human-on-the-Loop monitoring

    human_review = result.get("human_review")

    if human_review is True:
        print("[ALERT] Human review is recommended.")
        print("Please check the draft carefully.")

        decision = input(
            "\nChoose: ACCEPT / EDIT / HOLD: "
        ).strip().upper()

    elif human_review is False:
        print("[Monitor] No human review was flagged.")
        print("[Monitor] You can still inspect your draft.")

        decision = input(
            "\nChoose: ACCEPT / EDIT / HOLD: "
        ).strip().upper()

    else:
        print("[Monitor] The review status is invalid.")
        print("[Monitor] Human review is required.")
        return

    # STEP 5: Act on the customer's decision

    if decision == "ACCEPT":

        print("\n[Agent] Draft accepted by you.")
        print("You can copy this message and send it yourself.")

        print("\n========== FINAL MESSAGE ==========")
        print(draft)
        print("===================================\n")

        print("[Agent] Nothing was sent automatically.")

    elif decision == "EDIT":

        feedback = input(
            "What would you like to change in your message? "
        ).strip()

        if not feedback:
            print("[Agent] No feedback provided. Draft unchanged.")
            return

        print("\n[AI] Revising your message...")

        revision_prompt = f"""
You help a CUSTOMER write to a company.

Company: {company}
Product or service: {product}
Customer's original situation: {issue}

Current draft written by the customer:
{draft}

Customer's requested changes:
{feedback}

Rewrite the message using the customer's feedback.

Important:
- Write from the customer's point of view.
- The customer is writing TO the company.
- Do not write as the company or shop.
- Do not invent facts or make unsupported accusations.
- Keep the customer's original purpose.
- Return only the revised message.
- Do not send the message.
"""

        try:
            revised_message = ask_ai(revision_prompt)

            print("\n======= REVISED CUSTOMER MESSAGE =======")
            print(revised_message)
            print("========================================\n")

            print("[Agent] Review the revised message before using it.")
            print("[Agent] Nothing was sent automatically.")

        except Exception as error:
            print("[Agent] Revision failed:", error)

    elif decision == "HOLD":

        print("\n[Agent] Draft placed on hold.")
        print("[Agent] No message was sent.")

    else:
        print("\nInvalid choice. No message was sent.")


# ==========================================
# 3. START THE AGENT
# ==========================================

if __name__ == "__main__":

    try:
        human_on_the_loop_agent()

    except Exception as error:
        print("\n[Error]", error)
        print(
            "Check your API key, internet connection, "
            "model availability, and API quota."
        )
