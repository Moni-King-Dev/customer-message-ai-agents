
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
    response = client.interactions.create(
        model=MODEL,
        input=prompt
    )

    if not response.output_text:
        raise RuntimeError("Gemini returned an empty response.")

    return response.output_text.strip()


# ==========================================
# 2. APPROVAL AGENT
# ==========================================

def approval_agent():

    print("\n====================================")
    print(" CUSTOMER MESSAGE APPROVAL AGENT")
    print("====================================\n")

    # STEP 1: Get the customer's details

    company = input("Company or shop name: ").strip()
    product = input("Product or service: ").strip()
    issue = input("Explain your issue: ").strip()

    if not company or not product or not issue:
        print("All fields are required.")
        return

    # STEP 2: Generate a message from the customer's POV

    prompt = f"""
You are helping a CUSTOMER write a message TO a company.

Company: {company}
Product or service: {product}
Customer's issue: {issue}

Write a clear, polite message from the customer's point of view.

Rules:
- The customer is writing to the company.
- Use first-person wording where appropriate.
- Do not write as the company or shop.
- Do not invent order numbers, dates, purchases, or facts.
- Do not claim that a refund or replacement has happened.
- Return only the draft message.
- Do not send the message.
"""

    print("\n[AI] Drafting your message...")

    try:
        draft = ask_ai(prompt)
    except Exception as error:
        print("[Error] Could not generate the draft:", error)
        return

    # STEP 3: Show the draft

    print("\n========== MESSAGE DRAFT ==========")
    print(draft)
    print("===================================\n")

    # STEP 4: Approval gate

    while True:
        decision = input(
            "Choose: APPROVE / REVISE / REJECT: "
        ).strip().upper()

        if decision in ("APPROVE", "REVISE", "REJECT"):
            break

        print("Invalid choice. Please try again.")

    # STEP 5: Handle the decision

    if decision == "APPROVE":

        print("\n[Approval Agent] Human approval received.")
        print("The message is approved for you to use.")
        print("\n========== APPROVED MESSAGE ==========")
        print(draft)
        print("======================================")
        print("Nothing was sent automatically.")

    elif decision == "REVISE":

        feedback = input(
            "What would you like to change? "
        ).strip()

        if not feedback:
            print("No feedback supplied. Approval not granted.")
            return

        revision_prompt = f"""
You help a customer write to a company.

Company: {company}
Product or service: {product}
Original customer issue: {issue}

Current draft:
{draft}

Customer's requested changes:
{feedback}

Rewrite the message from the customer's point of view.

Do not write as the company.
Do not invent facts.
Return only the revised message.
Do not send it.
"""

        try:
            revised = ask_ai(revision_prompt)
        except Exception as error:
            print("[Error] Revision failed:", error)
            return

        print("\n========== REVISED DRAFT ==========")
        print(revised)
        print("===================================\n")

        # Revised draft must be approved separately
        final_decision = input(
            "Approve this revised message? (YES/NO): "
        ).strip().upper()

        if final_decision == "YES":
            print("\n[Approval Agent] Revised message approved.")
            print(revised)
            print("Nothing was sent automatically.")
        else:
            print("\n[Approval Agent] Approval not granted.")
            print("The message has not been sent.")

    elif decision == "REJECT":

        print("\n[Approval Agent] Message rejected.")
        print("No message was sent.")


# ==========================================
# 3. START THE AGENT
# ==========================================

if __name__ == "__main__":
    try:
        approval_agent()
    except Exception as error:
        print("[Error]", error)
