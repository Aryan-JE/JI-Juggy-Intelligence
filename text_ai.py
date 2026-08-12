import random
import json
import os

# =========================
# JI - Version 6
# Persistent Memory
# =========================

MEMORY_FILE = "ji_memory.json"


# =========================
# Load Memory
# =========================

def load_memory():

    if os.path.exists(MEMORY_FILE):

        try:

            with open(MEMORY_FILE, "r") as file:
                return json.load(file)

        except:
            return {}

    return {}


# =========================
# Save Memory
# =========================

def save_memory():

    with open(MEMORY_FILE, "w") as file:

        json.dump(memory, file, indent=4)


# Load existing memory
memory = load_memory()


# =========================
# Responses
# =========================

responses = {

    "greeting": [
        "Hey! I'm JI 😎",
        "Yo! What's up?",
        "Hello bro! 🔥",
        "Hey! Good to see you."
    ],

    "how_are_you": [
        "I'm doing great! 😎",
        "All systems are running!",
        "I'm good bro 🔥",
        "Running perfectly!"
    ],

    "thanks": [
        "You're welcome! 😎",
        "Anytime bro!",
        "No problem!",
        "Always!"
    ],

    "goodbye": [
        "Goodbye bro! 👋",
        "See you later!",
        "JI signing off. 🫡",
        "Catch you later!"
    ],

    "positive": [
        "That's awesome! 🔥",
        "Glad to hear that!",
        "Nice bro! 😎",
        "That's great!"
    ],

    "negative": [
        "I understand bro.",
        "Hope things get better.",
        "Don't worry.",
        "I'm here."
    ],

    "unknown": [
        "I'm still learning that.",
        "I don't understand that yet.",
        "Teach me more about that.",
        "I'm not sure what you mean yet."
    ]
}


# =========================
# Understand Messages
# =========================

def understand(sentence):

    text = sentence.lower()

    if any(word in text for word in [
        "hello", "hi", "hey", "yo"
    ]):
        return "greeting"

    if any(phrase in text for phrase in [
        "how are you",
        "how r u",
        "how are u"
    ]):
        return "how_are_you"

    if any(word in text for word in [
        "thanks", "thank you", "thx"
    ]):
        return "thanks"

    if any(word in text for word in [
        "bye", "goodbye", "see you"
    ]):
        return "goodbye"

    if any(word in text for word in [
        "love", "amazing", "great",
        "awesome", "good", "like"
    ]):
        return "positive"

    if any(word in text for word in [
        "hate", "bad", "terrible",
        "awful", "dislike"
    ]):
        return "negative"

    return "unknown"


# =========================
# Memory System
# =========================

def check_memory(sentence):

    text = sentence.lower().strip()


    # -------------------------
    # Remember Name
    # -------------------------

    if text.startswith("my name is"):

        name = sentence[11:].strip()

        if name:

            memory["name"] = name.title()

            save_memory()

            return f"Got it! I'll remember your name is {memory['name']}."


    # -------------------------
    # Remember Likes
    # -------------------------

    if text.startswith("i like"):

        thing = sentence[6:].strip()

        if thing:

            memory["likes"] = thing

            save_memory()

            return f"Got it! You like {thing} 😎"


    # -------------------------
    # Remember Study
    # -------------------------

    if "i study at" in text:

        university = text.split("i study at", 1)[1].strip()

        if university:

            memory["study"] = university.title()

            save_memory()

            return f"Got it! You study at {memory['study']}."


    # -------------------------
    # Ask Name
    # -------------------------

    if any(phrase in text for phrase in [
        "what is my name",
        "what's my name",
        "do you know my name"
    ]):

        if "name" in memory:

            return f"Your name is {memory['name']} 😎"

        return "You haven't told me your name yet."


    # -------------------------
    # Ask Likes
    # -------------------------

    if "what do i like" in text:

        if "likes" in memory:

            return f"You like {memory['likes']} 🔥"

        return "You haven't told me what you like yet."


    # -------------------------
    # Ask University
    # -------------------------

    if any(phrase in text for phrase in [
        "where do i study",
        "where am i studying",
        "what university do i study at"
    ]):

        if "study" in memory:

            return f"You study at {memory['study']}."

        return "You haven't told me where you study yet."


    # -------------------------
    # Show Memory
    # -------------------------

    if any(phrase in text for phrase in [
        "what do you know about me",
        "what do you remember about me",
        "show my memory"
    ]):

        if not memory:

            return "I don't remember anything yet."


        result = "Here's what I remember:\n"


        if "name" in memory:
            result += f"• Name: {memory['name']}\n"


        if "likes" in memory:
            result += f"• Likes: {memory['likes']}\n"


        if "study" in memory:
            result += f"• University: {memory['study']}\n"


        return result


    return None


# =========================
# Start JI
# =========================

print("============================")
print("        JI AI v6")
print("============================")
print("JI: Persistent memory activated 🧠")
print("JI: I can remember things!")
print("JI: Type 'exit' to stop.")


# =========================
# Chat Loop
# =========================

while True:

    user_sentence = input("\nYou: ")


    if user_sentence.lower() == "exit":

        print("JI:", random.choice(responses["goodbye"]))

        break


    # Check memory

    memory_reply = check_memory(user_sentence)


    if memory_reply:

        print("JI:", memory_reply)

        continue


    # Normal conversation

    intent = understand(user_sentence)

    reply = random.choice(responses[intent])

    print("JI:", reply)