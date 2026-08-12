import speech_recognition as sr

recognizer = sr.Recognizer()

MIC_NAME = "Microphone (JBL Tune Beam 2)"


# ==========================================
# FIND JBL MICROPHONE
# ==========================================

mic_index = None

for i, name in enumerate(
    sr.Microphone.list_microphone_names()
):

    if name == MIC_NAME:

        mic_index = i
        break


if mic_index is None:

    print("❌ JBL microphone not found!")

    print()
    print("Available microphones:")

    for i, name in enumerate(
        sr.Microphone.list_microphone_names()
    ):

        print(i, name)

    input("\nPress Enter to exit...")
    exit()


# ==========================================
# START
# ==========================================

print()
print("========================================")
print("          JI WAKE WORD TEST")
print("========================================")
print()
print("Microphone:", MIC_NAME)
print("Device index:", mic_index)
print()
print("Wake words:")
print("  Hey JI")
print("  Hey G")
print("  AJ")
print("  A J")
print()
print("Say 'Hey JI'...")
print()


# ==========================================
# WAKE WORD LOOP
# ==========================================

while True:

    with sr.Microphone(
        device_index=mic_index
    ) as source:

        print("👂 Listening...")

        try:

            audio = recognizer.listen(
                source,
                timeout=None,
                phrase_time_limit=5
            )

        except Exception as error:

            print("Microphone error:", error)

            continue


    # ======================================
    # SPEECH RECOGNITION
    # ======================================

    try:

        text = recognizer.recognize_google(
            audio
        )

        heard = text.lower().strip()

        print("Heard:", text)


    except sr.UnknownValueError:

        print("Couldn't understand.")

        continue


    except sr.RequestError:

        print()
        print(
            "❌ Speech recognition requires internet."
        )

        break


    # ======================================
    # WAKE WORD DETECTION
    # ======================================

    wake_words = [
        "hey ji",
        "hey g",
        "hey gee",
        "aj",
        "a j",
        "hey jay",
        "hey j"
    ]


    woke_up = False


    for wake_word in wake_words:

        if wake_word in heard:

            woke_up = True
            break


    # ======================================
    # WAKE UP
    # ======================================

    if woke_up:

        print()
        print("========================================")
        print("          🔥 JI WOKE UP 🔥")
        print("========================================")
        print()

        break

