from ollama import chat
import json
import os

# =========================
# JI v3 - Smart Memory
# =========================

MEMORY_FILE = "ji_memory.json"
MODEL = "qwen3:8b"


# =========================
# Memory
# =========================

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except:
            return {}

    return {}


def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(memory, file, indent=4, ensure_ascii=False)


memory = load_memory()


# =========================
# Main AI personality
# =========================

def build_system_prompt():

    return f"""
You are JI, a personal AI assistant created by the user.

Your personality:
- Friendly
- Natural
- Casual
- Intelligent
- Helpful
- Sometimes playful
- You may say "bro" naturally, but don't overuse it.

You are an AI, so never claim to be a human.

You have access to the user's long-term memory below.

Use memory naturally when it is relevant.

LONG-TERM MEMORY:
{json.dumps(memory, indent=2, ensure_ascii=False)}
"""


# =========================
# Smart Memory Extraction
# =========================

def extract_memory(user_message):

    prompt = f"""
You are JI's memory system.

Read the user's message and decide whether it contains
a useful personal fact that should be remembered for future
conversations.

Only remember useful long-term information such as:
- name
- education
- hobbies
- interests
- goals
- preferences
- projects
- important personal facts

Do NOT remember:
- temporary questions
- greetings
- random conversation
- jokes
- sensitive information
- passwords
- private security information
- one-time requests

Return ONLY valid JSON.

If there is nothing worth remembering, return:

{{"remember": false}}

If there is something worth remembering, return:

{{
    "remember": true,
    "key": "short_key",
    "value": "short fact"
}}

User message:
{user_message}
"""

    try:

        response = chat(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": 0
            }
        )

        result = response.message.content.strip()

        # Remove markdown fences if the model adds them
        result = result.replace("```json", "")
        result = result.replace("```", "")
        result = result.strip()

        data = json.loads(result)

        if data.get("remember") is True:

            key = data.get("key")
            value = data.get("value")

            if key and value:

                memory[key] = value
                save_memory(memory)

                return key, value

    except Exception as error:

        print("Memory system:", error)

    return None


# =========================
# Start JI
# =========================

print("============================")
print("          JI AI v3")
print("============================")
print("JI: I'm online. 🧠")
print("JI: Smart memory activated.")
print("JI: Type 'exit' to shut me down.")
print()


# =========================
# Conversation History
# =========================

messages = [
    {
        "role": "system",
        "content": build_system_prompt()
    }
]


# =========================
# Chat Loop
# =========================

while True:

    user_message = input("You: ").strip()

    if not user_message:
        continue


    # Exit
    if user_message.lower() == "exit":

        print("JI: Goodbye bro! 👋")
        break


    # Show memory
    if user_message.lower() in [
        "show memory",
        "what do you remember",
        "what do you remember about me",
        "what do you know about me"
    ]:

        if memory:

            print("\nJI's Memory 🧠")

            for key, value in memory.items():
                print(f"• {key}: {value}")

        else:

            print("JI: I don't have any memories yet.")

        continue


    # Clear memory
    if user_message.lower() == "forget everything":

        memory.clear()
        save_memory(memory)

        print("JI: Done. I forgot everything I had saved. 🗑️")
        continue


    # =========================
    # Smart Memory
    # =========================

    new_memory = extract_memory(user_message)

    if new_memory:

        key, value = new_memory

        print(f"JI: I'll remember that. 🧠")


    # Update JI's system prompt with latest memory
    messages[0]["content"] = build_system_prompt()


    # Add user message
    messages.append({
        "role": "user",
        "content": user_message
    })


    # =========================
    # Ask Ollama
    # =========================

    try:

        response = chat(
            model=MODEL,
            messages=messages
        )

        reply = response.message.content

    except Exception as error:

        print("JI: Something went wrong.")
        print("Error:", error)
        continue


    # Save conversation history
    messages.append({
        "role": "assistant",
        "content": reply
    })


    print("JI:", reply)