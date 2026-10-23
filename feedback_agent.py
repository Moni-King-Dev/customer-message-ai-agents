
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
# 2. FEEDBACK-IN-THE-LOOP AGENT
# ==========================================

def feedback_agent():

    print("\n====================================")
    print(" CUSTOMER MESSAGE IMPROVEMENT AGENT")
    print(" Feedback-in-the-Loop")
    print("====================================\n")

    # STEP 1: Get customer information

    company = input("Company or shop name: ").strip()
    product = input("Product or service: ").strip()
    issue = input("Explain your issue or request: ").strip()

    if not company or not product or not issue:
        print("All fields are required.")
        return

    # STEP 2: Generate the first draft

    prompt = f"""
You are helping a CUSTOMER write a message TO a company.

Company: {company}
Product or service: {product}
Customer's issue or request: {issue}

Write a natural, clear, polite message from the customer's
point of view.

Rules:
- The customer is writing to the company.
- Use first-person wording where appropriate.
- Do not write as the company or shop.
- Do not invent order details, purchases, or facts.
- Do not claim that any action has already happened.
- Return only the message.
"""

    try:
        draft = ask_ai(prompt)
    except Exception as error:
        print("[Error] Could not generate draft:", error)
        return

    print("\n========== FIRST DRAFT ==========")
    print(draft)
    print("=================================\n")

    # STEP 3: Feedback and improvement loop

    max_revisions = 5
    revision_count = 0

    while revision_count < max_revisions:

        print("\nWhat would you like to do?")
        print("1. Give feedback and improve the message")
        print("2. Finish with the current draft")
        print("3. Stop")

        choice = input("Choose (1-3): ").strip()

        if choice == "2":
            print("\n[Agent] You selected the current draft.")
            print("\n========== FINAL MESSAGE ==========")
            print(draft)
            print("===================================")
            print("Nothing was sent automatically.")
            return

        elif choice == "3":
            print("\n[Agent] Stopped by the customer.")
            print("Nothing was sent.")
            return

        elif choice == "1":

            feedback = input(
                "\nWhat should be changed? "
            ).strip()

            if not feedback:
                print("Please enter feedback.")
                continue

            revision_prompt = f"""
You help a CUSTOMER write a message TO a company.

Company: {company}
Product or service: {product}
Customer's original issue:
{issue}

Current draft:
{draft}

Customer feedback:
{feedback}

Improve the current draft according to the feedback.

Rules:
- Write from the customer's point of view.
- Address the company, not the customer.
- Do not write as the company or shop.
- Keep the original purpose of the message.
- Do not invent facts or make unsupported claims.
- Return only the improved message.
- Do not send the message.
"""

            print("\n[Agent] Using your feedback to improve the draft...")

            try:
                draft = ask_ai(revision_prompt)
            except Exception as error:
                print("[Error] Revision failed:", error)
                continue

            revision_count += 1

            print(f"\n========== REVISION {revision_count} ==========")
            print(draft)
            print("============================================")

        else:
            print("Invalid choice. Try again.")

    print("\n[Agent] Maximum revision limit reached.")
    print("\n========== CURRENT FINAL DRAFT ==========")
    print(draft)
    print("=========================================")
    print("Review the draft before sending it yourself.")
    print("Nothing was sent automatically.")


# ==========================================
# 3. START THE AGENT
# ==========================================

if __name__ == "__main__":
    try:
        feedback_agent()
    except Exception as error:
        print("[Error]", error)
