
import os
from dotenv import load_dotenv
from google import genai

# ==========================================
# 1. LOAD GEMINI API KEY
# ==========================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found. Check your .env file."
    )

client = genai.Client(api_key=api_key)

MODEL = "gemini-3.8-flash"


# ==========================================
# 2. CONNECT TO GEMINI
# ==========================================

def ask_ai(prompt):
    """Send a prompt to Gemini and return its text."""

    response = client.interactions.create(
        model=MODEL,
        input=prompt
    )

    if not response.output_text:
        raise RuntimeError("Gemini returned an empty response.")

    return response.output_text.strip()


# ==========================================
# 3. HUMAN-IN-THE-LOOP AGENT
# ==========================================

def human_in_the_loop_agent():

    print("\n========================================")
    print(" CUSTOMER MESSAGE ASSISTANT")
    print(" Human-in-the-Loop AI Agent")
    print("========================================\n")

    # STEP 1: Get the customer's details
    company = input("Company name: ").strip()
    product = input("Product or service: ").strip()
    issue = input(
        "What do you want to ask the company? "
    ).strip()

    if not company or not product or not issue:
        print("All fields are required. Agent stopped.")
        return

    # STEP 2: Gemini drafts a message from the CUSTOMER
    print("\n[Agent] Asking Gemini to draft your message...")

    draft_prompt = f"""
You are an AI writing assistant helping a CUSTOMER
write a message TO A COMPANY.

The customer is the person sending the message.
The company is the recipient.

Company: {company}
Product or service: {product}
Customer's request or issue: {issue}

Write a natural message from the customer's point of view.

Use "I" and "my" when appropriate.
Address the company or its support team.
Ask clearly for the information, help, or solution needed.

Do NOT write a sales email.
Do NOT pretend to be the company.
Do NOT answer on behalf of the company.
Do NOT invent order details, purchases, or facts.
Do NOT send the message.

Return only the message the customer could send.
"""

    draft = ask_ai(draft_prompt)

    print("\n========== INITIAL MESSAGE ==========")
    print(draft)
    print("=====================================\n")

    # STEP 3: PAUSE AND ASK THE HUMAN
    print("[Agent] Your input is required.")
    print("How would you like to change your message?\n")
    print("1. Make it more formal")
    print("2. Make it friendlier")
    print("3. Make it shorter")
    print("4. Make it more detailed")
    print("5. Enter my own feedback")
    print("6. Stop")

    choice = input("\nChoose an option (1-6): ").strip()

    feedback_options = {
        "1": "Make the message more formal and professional.",
        "2": "Make the message friendlier and more natural.",
        "3": "Make the message shorter while keeping the main request.",
        "4": "Add useful detail based only on the facts provided."
    }

    if choice == "6":
        print("\n[Agent] Stopped by the customer.")
        return

    if choice in feedback_options:
        human_feedback = feedback_options[choice]

    elif choice == "5":
        human_feedback = input(
            "Enter your feedback: "
        ).strip()

        if not human_feedback:
            print("No feedback provided. Agent stopped.")
            return

    else:
        print("Invalid choice. Agent stopped.")
        return

    # STEP 4: Send human feedback to Gemini
    print("\n[Agent] Sending your feedback to Gemini...")
    print("[Agent] Revising your message...")

    revision_prompt = f"""
You are helping a CUSTOMER write a message TO A COMPANY.

Company: {company}
Product or service: {product}
Customer's original request: {issue}

Original customer message:
{draft}

Feedback from the customer:
{human_feedback}

Revise the message using the customer's feedback.

Important:
- Write from the customer's point of view.
- The customer is writing TO the company.
- Use first-person wording where appropriate.
- Do not write as if you are the company.
- Do not turn it into a sales or marketing email.
- Do not invent facts, order numbers, purchases, or promises.
- Keep the customer's original request.
- Return only the revised message.
"""

    revised_message = ask_ai(revision_prompt)

    # STEP 5: Show the revised message
    print("\n========== REVISED MESSAGE ==========")
    print(revised_message)
    print("=====================================\n")

    # STEP 6: Human decides what happens next
    print("What would you like to do?")
    print("1. Accept the message")
    print("2. Give more feedback")
    print("3. Stop")

    final_choice = input("\nChoose (1-3): ").strip()

    if final_choice == "1":
        print("\n[Agent] Message accepted by the customer.")
        print("[Agent] You can copy it and send it yourself.")
        print("[Agent] No message was sent automatically.")

    elif final_choice == "2":
        extra_feedback = input(
            "What else should be changed? "
        ).strip()

        if not extra_feedback:
            print("[Agent] No feedback provided.")
            return

        print("\n[Agent] Revising again...")

        final_message = ask_ai(
            f"""
You help a customer write to a company.

Company: {company}
Product or service: {product}
Original request: {issue}

Current customer message:
{revised_message}

Additional customer feedback:
{extra_feedback}

Apply the feedback. Write from the customer's
point of view, addressing the company.

Do not invent facts. Return only the revised message.
"""
        )

        print("\n========== FINAL MESSAGE ===========")
        print(final_message)
        print("=====================================\n")
        print("[Agent] Revision complete.")
        print("[Agent] Nothing was sent automatically.")

    else:
        print("\n[Agent] Stopped by the customer.")


# ==========================================
# 4. START THE AGENT
# ==========================================

if __name__ == "__main__":
    try:
        human_in_the_loop_agent()

    except Exception as error:
        print(f"\n[Error] {error}")
        print(
            "Check your API key, internet connection, "
            "model availability, and API quota."
        )