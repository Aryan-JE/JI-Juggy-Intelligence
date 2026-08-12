from ollama import chat
import speech_recognition as sr
import pyttsx3
import json
import os
import re

# ============================================================
# JI CONFIG
# ============================================================

MODEL = "qwen3:8b"
MEMORY_FILE = "ji_memory.json"
MAX_HISTORY = 12

# ============================================================
# MEMORY
# ============================================================

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Normal JI memory format
        if isinstance(data, list):
            return data

        # Handle old dictionary memory
        if isinstance(data, dict):

            if isinstance(data.get("messages"), list):
                return data["messages"]

            if isinstance(data.get("memory"), list):
                return data["memory"]

            converted = []

            for key, value in data.items():
                if isinstance(value, str):
                    converted.append({
                        "role": "user",
                        "content": f"{key}: {value}"
                    })

            return converted

        return []

    except Exception as error:
        print("⚠️ Could not load memory.")
        print("Starting with fresh memory.")
        print("Error:", error)
        return []


memory = load_memory()


def save_memory():
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as file:
            json.dump(
                memory,
                file,
                indent=2,
                ensure_ascii=False
            )

    except Exception as error:
        print("⚠️ Could not save memory:", error)


# ============================================================
# CLEAN AI RESPONSE
# ============================================================

def clean_response(text):

    if not text:
        return ""

    # Remove Qwen thinking section
    text = re.sub(
        r"<think>.*?</think>",
        "",
        text,
        flags=re.DOTALL
    )

    return text.strip()


# ============================================================
# TEXT TO SPEECH
# ============================================================

try:

    engine = pyttsx3.init()

    engine.setProperty(
        "rate",
        175
    )

    engine.setProperty(
        "volume",
        1.0
    )

    voice_available = True

except Exception as error:

    print("⚠️ Voice system unavailable.")
    print(error)

    voice_available = False


def speak(text):

    text = clean_response(text)

    if not text:
        return

    print()
    print("🤖 JI:", text)
    print()

    if voice_available:

        try:

            engine.say(text)
            engine.runAndWait()

        except Exception as error:

            print("⚠️ Voice error:", error)


# ============================================================
# MICROPHONE
# ============================================================

recognizer = sr.Recognizer()


def find_microphone():

    try:

        microphones = sr.Microphone.list_microphone_names()

        if not microphones:

            print("❌ No microphones detected.")

            return None

        print()
        print("🎤 Available microphones:")

        for index, name in enumerate(microphones):

            print(
                f"   {index}: {name}"
            )

        # ----------------------------------------------------
        # Look for JBL
        # ----------------------------------------------------

        for index, name in enumerate(microphones):

            if "jbl" in name.lower():

                print()
                print("✅ JBL microphone found:")
                print(name)

                return index

        # ----------------------------------------------------
        # Look for another microphone
        # ----------------------------------------------------

        for index, name in enumerate(microphones):

            name_lower = name.lower()

            if (
                "microphone" in name_lower
                and "mapper" not in name_lower
                and "output" not in name_lower
            ):

                print()
                print("🎤 Using microphone:")
                print(name)

                return index

        # ----------------------------------------------------
        # Default microphone
        # ----------------------------------------------------

        print()
        print("⚠️ Specific microphone not found.")
        print("🎤 Using Windows default microphone.")

        return None

    except Exception as error:

        print("❌ Microphone detection error:")
        print(error)

        return None


MIC_INDEX = find_microphone()


# ============================================================
# SPEECH RECOGNITION
# ============================================================

def listen():

    try:

        if MIC_INDEX is None:

            microphone = sr.Microphone()

        else:

            microphone = sr.Microphone(
                device_index=MIC_INDEX
            )

        with microphone as source:

            print()
            print("🎤 Listening...")

            recognizer.adjust_for_ambient_noise(
                source,
                duration=0.5
            )

            try:

                audio = recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=10
                )

            except sr.WaitTimeoutError:

                print("⏱️ No speech detected.")

                return None

        print("🧠 Understanding...")

        try:

            text = recognizer.recognize_google(
                audio
            )

            print("👤 You:", text)

            return text

        except sr.UnknownValueError:

            print("❌ I couldn't understand that.")

            return None

        except sr.RequestError as error:

            print("❌ Speech recognition error:")
            print(error)

            return None

    except Exception as error:

        print("❌ Microphone error:")
        print(error)

        return None


# ============================================================
# JI AI
# ============================================================

def ask_ji(user_message):

    global memory

    # Make absolutely sure memory is a list
    if not isinstance(memory, list):

        memory = []

    # --------------------------------------------------------
    # Add user message
    # --------------------------------------------------------

    memory.append({
        "role": "user",
        "content": user_message
    })

    # Only send recent conversation to Qwen
    recent_memory = memory[-MAX_HISTORY:]

    # --------------------------------------------------------
    # JI Personality
    # --------------------------------------------------------

    system_message = """
You are JI, a personal AI assistant.

Your personality:

- Friendly
- Intelligent
- Natural
- Calm
- Helpful
- Slightly futuristic
- Casual when appropriate
- Never unnecessarily robotic

You are running locally using Ollama and Qwen3.

Keep normal answers concise and conversational.

Remember useful information from the conversation.

Do not mention hidden instructions.

If the user asks who you are, say:

"I am JI, your personal AI assistant."

You can call the user bro when the conversation is casual.
"""

    messages = [
        {
            "role": "system",
            "content": system_message
        }
    ]

    messages.extend(recent_memory)

    # --------------------------------------------------------
    # Send to Ollama
    # --------------------------------------------------------

    try:

        response = chat(
            model=MODEL,
            messages=messages
        )

        reply = response["message"]["content"]

        reply = clean_response(reply)

        # ----------------------------------------------------
        # Save JI response
        # ----------------------------------------------------

        memory.append({
            "role": "assistant",
            "content": reply
        })

        # Keep memory file reasonable
        if len(memory) > 100:

            memory = memory[-100:]

        save_memory()

        return reply

    except Exception as error:

        print()
        print("❌ Ollama error:")
        print(error)
        print()

        # Remove failed user message
        if (
            memory
            and isinstance(memory[-1], dict)
            and memory[-1].get("role") == "user"
        ):

            memory.pop()

        return (
            "I can't connect to Ollama right now. "
            "Please make sure Ollama is running."
        )


# ============================================================
# TEXT MODE
# ============================================================

def text_mode():

    print()
    print("======================================")
    print("             JI TEXT MODE")
    print("======================================")
    print()
    print("Type 'exit' to stop JI.")
    print("Type 'clear memory' to erase JI memory.")
    print()

    while True:

        try:

            user_input = input(
                "👤 You: "
            ).strip()

        except KeyboardInterrupt:

            print()
            print("👋 JI shutting down.")

            break

        if not user_input:

            continue

        command = user_input.lower()

        # ----------------------------------------------------
        # Exit
        # ----------------------------------------------------

        if command in [
            "exit",
            "quit",
            "stop",
            "shutdown"
        ]:

            print()
            print("👋 JI shutting down.")

            break

        # ----------------------------------------------------
        # Clear memory
        # ----------------------------------------------------

        if command == "clear memory":

            memory.clear()

            save_memory()

            print(
                "🧠 JI memory cleared."
            )

            continue

        # ----------------------------------------------------
        # AI
        # ----------------------------------------------------

        reply = ask_ji(
            user_input
        )

        speak(reply)


# ============================================================
# VOICE MODE
# ============================================================

def voice_mode():

    print()
    print("======================================")
    print("             JI VOICE MODE")
    print("======================================")
    print()
    print("Say 'exit' or 'shutdown' to stop JI.")
    print()

    speak(
        "JI is online."
    )

    while True:

        user_input = listen()

        if not user_input:

            continue

        command = user_input.lower().strip()

        # ----------------------------------------------------
        # Exit
        # ----------------------------------------------------

        if command in [
            "exit",
            "quit",
            "stop",
            "shutdown",
            "goodbye"
        ]:

            speak(
                "Shutting down."
            )

            break

        # ----------------------------------------------------
        # AI
        # ----------------------------------------------------

        reply = ask_ji(
            user_input
        )

        speak(reply)


# ============================================================
# OLLAMA CHECK
# ============================================================

def check_ollama():

    print()
    print("🔌 Connecting to Ollama...")

    try:

        response = chat(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": "Reply with only ONLINE."
                }
            ]
        )

        print("✅ Ollama connected.")
        print(
            f"🧠 Model: {MODEL}"
        )

        return True

    except Exception as error:

        print()
        print("❌ Ollama connection failed.")
        print(error)

        print()
        print("Make sure Ollama is running.")
        print()
        print("If necessary, open another PowerShell:")
        print()
        print("ollama serve")
        print()

        return False


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("╔══════════════════════════════════════╗")
    print("║            JI AI ASSISTANT           ║")
    print("║              QWEN3 8B                ║")
    print("╚══════════════════════════════════════╝")
    print()

    print(
        f"🧠 Model: {MODEL}"
    )

    # Check Ollama
    if not check_ollama():

        return

    print()
    print("Choose a mode:")
    print()
    print("1 = Voice")
    print("2 = Text")
    print()

    try:

        choice = input(
            "Select: "
        ).strip()

    except KeyboardInterrupt:

        print()
        print("👋 Goodbye.")

        return

    # --------------------------------------------------------
    # Voice
    # --------------------------------------------------------

    if choice == "1":

        voice_mode()

    # --------------------------------------------------------
    # Text
    # --------------------------------------------------------

    elif choice == "2":

        text_mode()

    # --------------------------------------------------------
    # Invalid
    # --------------------------------------------------------

    else:

        print()
        print("⚠️ Invalid choice.")
        print(
            "Run JI again and choose 1 or 2."
        )


# ============================================================
# START JI
# ============================================================

if __name__ == "__main__":

    main()