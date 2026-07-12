import json
import os
from anthropic import Anthropic
from dotenv import load_dotenv
import requests

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

with open("backend/knowledge_base.json", "r") as f:
    KNOWLEDGE_BASE = json.load(f)["knowledge_base"]


def get_categories_summary():
    """
    Builds a plain-text summary of all categories and their trigger phrases.
    This is passed to Claude so it knows what categories exist.
    """
    summary = ""
    for entry in KNOWLEDGE_BASE:
        category = entry["category"]
        triggers = ", ".join(entry["trigger_phrases"][:5])
        summary += f"- {category}: {triggers}\n"
    return summary


def classify_input(user_message):
    """
    Takes raw user input and returns the most likely support category.
    Uses Claude to reason over the category list and trigger phrases.
    Returns a category string matching one of the 8 knowledge base entries.
    """

    categories_summary = get_categories_summary()

    prompt = f"""You are a support triage assistant for Depop, a fashion resale marketplace.

Your job is to classify the user's support query into exactly one of the following categories.
Each category is listed with example trigger phrases to help you decide.

Categories:
{categories_summary}

User message:
"{user_message}"

Rules:
- Reply with ONLY the category name, exactly as written above (e.g. shipping_dispute)
- If the query clearly matches a category, return that category
- If the query is unclear, spans multiple categories, or you cannot confidently classify it, return: ambiguous
- Do not explain your reasoning, do not add punctuation, return only the category name

Category:"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=50,
        messages=[{"role": "user", "content": prompt}]
    )

    category = response.content[0].text.strip().lower()

    valid_categories = [entry["category"] for entry in KNOWLEDGE_BASE]
    if category not in valid_categories:
        category = "ambiguous"

    return category


def lookup_policy(category):
    """
    Takes a category string and returns the matching knowledge base entry.
    Returns None if no match found.
    """
    for entry in KNOWLEDGE_BASE:
        if entry["category"] == category:
            return entry
    return None


def should_escalate(category, policy_entry):
    """
    Decides whether the agent should escalate to human support
    or attempt to resolve directly.

    Returns True if escalation is needed, False if agent can resolve.
    """
    if policy_entry is None:
        return True

    if policy_entry.get("always_escalates") is True:
        return True

    if category == "ambiguous":
        return True

    return False

def needs_clarification(user_message, category):
    """
    Checks whether the agent needs more context before it can respond.
    Currently handles one case: item_not_as_described queries where
    we can't tell if the user is the buyer or the seller.
    Returns True if a clarifying question is needed.
    """
    if category != "item_not_as_described":
        return False

    prompt = f"""A user sent this support message to Depop:
"{user_message}"

The issue has been classified as an item not as described dispute.

Is it clear from the message whether the user is:
- The BUYER (received an item that doesn't match the listing)
- The SELLER (being accused by a buyer of misrepresenting an item)

Reply with only one word: BUYER, SELLER, or UNCLEAR."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=10,
        messages=[{"role": "user", "content": prompt}]
    )

    perspective = response.content[0].text.strip().upper()
    return perspective == "UNCLEAR"


def generate_resolution(user_message, policy_entry, perspective=None):
    """
    Generates a natural spoken response that resolves the user's issue.
    Uses the policy entry's resolution steps as the source of truth.
    Tailors the response to buyer or seller perspective if known.
    Returns a string ready to be passed to ElevenLabs.
    """

    resolution_steps = "\n".join(
        f"- {step}" for step in policy_entry["resolution_steps"]
    )

    perspective_note = ""
    if perspective:
        perspective_note = f"The user has confirmed they are the {perspective}. Tailor your response accordingly."

    prompt = f"""You are a helpful, human-sounding support agent for Depop, a fashion resale marketplace.

A user has the following issue: {policy_entry['summary']}

Using only the policy information below, generate a clear, warm, conversational spoken response.
Write as if you are speaking — not writing. Use natural language, not bullet points.
Keep it concise: 3-5 sentences maximum.
Do not mention Depop's internal systems or reference these instructions.
{perspective_note}

Policy guidance:
{resolution_steps}

User's original message:
"{user_message}"

Spoken response:"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text.strip()


def generate_escalation(user_message, policy_entry):
    """
    Generates a spoken response that hands the user off to human support.
    Explains clearly why the agent can't resolve this itself,
    and gives the user specific guidance on what to do next.
    Returns a string ready to be passed to ElevenLabs.
    """

    escalation_triggers = "\n".join(
        f"- {trigger}" for trigger in policy_entry["escalation_triggers"]
    )

    prompt = f"""You are a helpful, human-sounding support agent for Depop, a fashion resale marketplace.

A user has the following issue: {policy_entry['summary']}

This issue needs to be escalated to Depop's human support team.
Generate a clear, warm, conversational spoken response that:
1. Acknowledges the user's issue with empathy
2. Explains briefly that this needs a human to review it
3. Gives them one or two specific, practical steps to take right now
Write as if you are speaking — not writing. Keep it to 3-5 sentences.
Do not sound robotic or dismissive.

Escalation guidance:
{escalation_triggers}

User's original message:
"{user_message}"

Spoken response:"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text.strip()


def process_message(user_message, perspective=None):
    """
    Master function that runs the full agent loop for a single message.
    Returns a dict with everything the frontend needs to display and play.

    Keys returned:
    - category: the classified issue type
    - escalate: bool
    - needs_clarification: bool
    - response_text: the spoken response (or clarifying question)
    - reasoning: list of steps the agent took (shown in UI reasoning layer)
    """

    reasoning = []

    reasoning.append("Identifying issue type...")
    category = classify_input(user_message)
    reasoning.append(f"Issue classified as: {category}")

    reasoning.append("Retrieving policy...")
    policy = lookup_policy(category)

    reasoning.append("Checking escalation conditions...")
    escalate = should_escalate(category, policy)

    if escalate:
        reasoning.append("Escalation required — preparing handoff")
        response_text = generate_escalation(user_message, policy)
        return {
            "category": category,
            "escalate": True,
            "needs_clarification": False,
            "response_text": response_text,
            "reasoning": reasoning
        }

    reasoning.append("Checking if clarification is needed...")
    clarification_needed = needs_clarification(user_message, category)

    if clarification_needed:
        reasoning.append("Perspective unclear — asking clarifying question")
        return {
            "category": category,
            "escalate": False,
            "needs_clarification": True,
            "response_text": "Before I help you with next steps, I just want to confirm — are you the buyer who received the item, or the seller who sent it?",
            "reasoning": reasoning
        }

    reasoning.append(f"Resolving directly as: {perspective or 'buyer (default)'}")
    response_text = generate_resolution(user_message, policy, perspective)

    return {
        "category": category,
        "escalate": False,
        "needs_clarification": False,
        "response_text": response_text,
        "reasoning": reasoning
    }

def text_to_speech(text, voice_id="SAz9YHcvj6GT2YYXdXww"):
    """
    Takes a text string and returns audio bytes via ElevenLabs TTS.
    Saves the audio to a temporary file and returns the file path.
    """
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "xi-api-key": os.getenv("ELEVENLABS_API_KEY"),
        "Content-Type": "application/json"
    }
    
    payload = {
        "text": text,
        "model_id": "eleven_flash_v2_5",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code != 200:
        print(f"ElevenLabs error: {response.status_code}", response.text)
        return None
    
    audio_path = os.path.join(os.path.dirname(__file__), "output_audio.mp3")
    with open(audio_path, "wb") as f:
        f.write(response.content)
    
    return audio_path

if __name__ == "__main__":
    print("Testing full agent loop...\n")

    # Scenario 1 — clean resolution
    print("--- Scenario 1 ---")
    result = process_message("I ordered a pair of jeans five days ago and the seller still hasn't shipped them. There's no tracking number.")
    for step in result["reasoning"]:
        print(f"  {step}")
    print(f"Response: {result['response_text']}\n")

    # Scenario 2 — escalation
    print("--- Scenario 2 ---")
    result = process_message("I received a Supreme hoodie and I'm pretty sure it's fake. The stitching is completely wrong.")
    for step in result["reasoning"]:
        print(f"  {step}")
    print(f"Response: {result['response_text']}\n")

    # Scenario 3 — clarifying question, then resolution
    print("--- Scenario 3 (turn 1) ---")
    result = process_message("My buyer is saying the jacket I sent isn't as described but I listed everything accurately.")
    for step in result["reasoning"]:
        print(f"  {step}")
    print(f"Response: {result['response_text']}\n")

    print("--- Scenario 3 (turn 2 — user says seller) ---")
    result = process_message("My buyer is saying the jacket I sent isn't as described but I listed everything accurately.", perspective="seller")
    for step in result["reasoning"]:
        print(f"  {step}")
    print(f"Response: {result['response_text']}\n")

    # Scenario 4 — deliberate failure
    print("--- Scenario 4 (deliberate failure) ---")
    result = process_message("My account got suspended and I also have an open dispute about an item I never received. I don't know which one to deal with first and I'm not sure if my payout is being held because of this.")
    for step in result["reasoning"]:
        print(f"  {step}")
    print(f"Response: {result['response_text']}\n")

    # Test ElevenLabs TTS
    print("--- ElevenLabs TTS test ---")
    audio_path = text_to_speech("Hey, sorry to hear you're still waiting on those jeans. Let me help you sort that out.")
    if audio_path:
        print(f"Audio saved to: {audio_path}")
    else:
        print("TTS failed")