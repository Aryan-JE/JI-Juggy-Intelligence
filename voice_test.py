import speech_recognition as sr

recognizer = sr.Recognizer()

MIC_NAME = "Microphone (JBL Tune Beam 2)"

mic_index = None

# Find the JBL microphone
for i, name in enumerate(sr.Microphone.list_microphone_names()):
    if name == MIC_NAME:
        mic_index = i
        break

if mic_index is None:
    print("❌ JBL microphone not found!")
    print()
    print("Available microphones:")

    for i, name in enumerate(sr.Microphone.list_microphone_names()):
        print(i, name)

    exit()

print("================================")
print("       JI MICROPHONE TEST")
print("================================")
print()
print("Using:")
print(MIC_NAME)
print("Device index:", mic_index)
print()
print("🎤 Get ready...")

with sr.Microphone(device_index=mic_index) as source:

    print("Adjusting microphone...")
    recognizer.adjust_for_ambient_noise(
        source,
        duration=1
    )

    print()
    print("🔴 LISTENING NOW")
    print("Speak clearly into your JBL microphone.")
    print()

    try:
        audio = recognizer.listen(
            source,
            timeout=10,
            phrase_time_limit=10
        )

    except sr.WaitTimeoutError:
        print("❌ I didn't hear anything.")
        exit()


print("🧠 Processing your voice...")

try:

    text = recognizer.recognize_google(audio)

    print()
    print("================================")
    print("✅ YOU SAID:")
    print(text)
    print("================================")

except sr.UnknownValueError:

    print()
    print("❌ I heard audio, but couldn't understand the words.")

except sr.RequestError as error:

    print()
    print("❌ Speech recognition error:")
    print(error)