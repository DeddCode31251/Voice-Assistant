# Import All necessary Modules
import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import webbrowser
import os
import pyjokes

# FIX: Initialize the engine globally to prevent the ReferenceError on Linux
try:
    engine = pyttsx3.init()
except Exception as e:
    print(f"Warning: Could not initialize pyttsx3 engine: {e}")
    engine = None

# Corrected spelling and simplified logic
def speak(text):
    print(f"Assistant: {text}")
    
    if engine:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"Speech processing error: {e}")
    else:
        print("[Audio output unavailable]")

# Function to greet the user based on the current time
def wish_user():
    hour = datetime.datetime.now().hour
    if hour < 12:
        speak("Good Morning!")
    elif hour < 18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")
    speak("I'm your voice assistant. How can I help you today?")
    
# Take text commands
def take_cmd():
    # Built-in spacing fix so your typing cursor isn't glued to the prompt
    return input('You (type your command): ').lower()

def run_assistant():
    wish_user()
    while True:
        query = take_cmd()

        if 'wikipedia' in query:
            speak("Searching Wikipedia...")
            query = query.replace("wikipedia", "").strip()
            try:
                result = wikipedia.summary(query, sentences=2)
                speak("According to Wikipedia:")
                speak(result)
            except Exception:
                speak("Sorry, I couldn't find anything matching that on Wikipedia.")

        elif 'open youtube' in query:
            speak("Opening YouTube...")
            webbrowser.open("https://www.youtube.com/")

        elif 'open google' in query:
            speak("Opening Google...")
            webbrowser.open("https://google.com")

        elif 'time' in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"The current time is {strTime}")

        elif 'joke' in query:
            joke = pyjokes.get_joke()
            speak(joke)

        elif 'exit' in query or 'bye' in query:
            speak("Goodbye! Have a nice day!")
            break

        else:
            speak("Sorry, I didn't understand that. Try again.")
            
if __name__ == '__main__':
    run_assistant()

