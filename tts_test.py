import pyttsx3

engine = pyttsx3.init()

engine.setProperty("rate", 175)
engine.setProperty("volume", 1.0)

print("JI is speaking...")

engine.say("Hello bro. I am JI. I can finally talk to you.")
engine.runAndWait()

print("Done.")