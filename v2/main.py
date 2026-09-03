
import tkinter as tk
from tkinter import scrolledtext
import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import webbrowser
import pyjokes
import threading


# ============================================================
# VOICE ENGINE
# ============================================================

try:
    engine = pyttsx3.init()
    engine.setProperty("rate", 170)
    engine.setProperty("volume", 1.0)
except Exception as e:
    print(f"Warning: Could not initialize pyttsx3: {e}")
    engine = None


# ============================================================
# SPEECH RECOGNIZER
# ============================================================

recognizer = sr.Recognizer()


# ============================================================
# GUI
# ============================================================

root = tk.Tk()
root.title("Voice Assistant")
root.geometry("850x650")
root.minsize(700, 550)
root.configure(bg="#111827")


# ============================================================
# COLORS
# ============================================================

BG_COLOR = "#111827"
CHAT_BG = "#1F2937"
INPUT_BG = "#374151"
TEXT_COLOR = "#F9FAFB"
SECONDARY = "#9CA3AF"
ACCENT = "#6366F1"
ACCENT_HOVER = "#818CF8"
USER_COLOR = "#22C55E"
ASSISTANT_COLOR = "#60A5FA"
ERROR_COLOR = "#EF4444"


# ============================================================
# FUNCTIONS
# ============================================================

def add_message(sender, message, color):
    """
    Add a message to the chat window.
    """

    chat_box.config(state=tk.NORMAL)

    chat_box.insert(
        tk.END,
        f"{sender}\n",
        ("sender", color)
    )

    chat_box.insert(
        tk.END,
        f"{message}\n\n",
        ("message", TEXT_COLOR)
    )

    chat_box.config(state=tk.DISABLED)
    chat_box.see(tk.END)


def speak(text):
    """
    Speak text using pyttsx3 and display it in the GUI.
    """

    add_message("Assistant", text, ASSISTANT_COLOR)

    if engine:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"Speech processing error: {e}")


def update_status(text, color=SECONDARY):
    """
    Update microphone/status label.
    """

    status_label.config(
        text=text,
        fg=color
    )


def wish_user():
    """
    Greet the user based on the current time.
    """

    hour = datetime.datetime.now().hour

    if hour < 12:
        greeting = "Good Morning!"
    elif hour < 18:
        greeting = "Good Afternoon!"
    else:
        greeting = "Good Evening!"

    speak(greeting)
    speak("I'm your voice assistant. How can I help you today?")


# ============================================================
# COMMAND PROCESSING
# ============================================================

def process_command(query):
    """
    Process the user's command.
    """

    query = query.lower().strip()

    if not query:
        return

    add_message("You", query, USER_COLOR)

    # --------------------------------------------------------
    # WIKIPEDIA
    # --------------------------------------------------------

    if "wikipedia" in query:

        speak("Searching Wikipedia...")

        search_query = query.replace("wikipedia", "").strip()

        if not search_query:
            speak("What would you like me to search for?")
            return

        try:

            result = wikipedia.summary(
                search_query,
                sentences=2
            )

            speak("According to Wikipedia:")
            speak(result)

        except Exception:
            speak(
                "Sorry, I couldn't find anything matching that on Wikipedia."
            )

    # --------------------------------------------------------
    # YOUTUBE
    # --------------------------------------------------------

    elif "open youtube" in query:

        speak("Opening YouTube...")

        webbrowser.open(
            "https://www.youtube.com/"
        )

    # --------------------------------------------------------
    # GOOGLE
    # --------------------------------------------------------

    elif "open google" in query:

        speak("Opening Google...")

        webbrowser.open(
            "https://www.google.com/"
        )

    # --------------------------------------------------------
    # TIME
    # --------------------------------------------------------

    elif "time" in query:

        current_time = datetime.datetime.now().strftime(
            "%H:%M:%S"
        )

        speak(
            f"The current time is {current_time}"
        )

    # --------------------------------------------------------
    # JOKE
    # --------------------------------------------------------

    elif "joke" in query:

        try:

            joke = pyjokes.get_joke()

            speak(joke)

        except Exception:

            speak(
                "Sorry, I couldn't get a joke right now."
            )

    # --------------------------------------------------------
    # EXIT
    # --------------------------------------------------------

    elif (
        "exit" in query
        or "bye" in query
        or "goodbye" in query
    ):

        speak(
            "Goodbye! Have a nice day!"
        )

        root.after(
            1500,
            root.destroy
        )

    # --------------------------------------------------------
    # UNKNOWN COMMAND
    # --------------------------------------------------------

    else:

        speak(
            "Sorry, I didn't understand that. "
            "Try saying Wikipedia, open YouTube, "
            "open Google, time, or joke."
        )


# ============================================================
# MICROPHONE
# ============================================================

def listen_microphone():
    """
    Listen to the microphone and convert speech to text.
    """

    update_status(
        "🎙 Listening...",
        ACCENT_HOVER
    )

    try:

        with sr.Microphone() as source:

            # Adjust microphone for background noise
            recognizer.adjust_for_ambient_noise(
                source,
                duration=0.7
            )

            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=10
            )

        update_status(
            "🔄 Processing...",
            ACCENT_HOVER
        )

        query = recognizer.recognize_google(
            audio
        )

        update_status(
            "🎙 Ready",
            USER_COLOR
        )

        process_command(query)

    except sr.WaitTimeoutError:

        update_status(
            "🎙 Ready",
            USER_COLOR
        )

        speak(
            "I didn't hear anything."
        )

    except sr.UnknownValueError:

        update_status(
            "🎙 Ready",
            USER_COLOR
        )

        speak(
            "Sorry, I couldn't understand what you said."
        )

    except sr.RequestError:

        update_status(
            "❌ Speech service error",
            ERROR_COLOR
        )

        speak(
            "I couldn't connect to the speech recognition service."
        )

    except Exception as e:

        update_status(
            "❌ Microphone error",
            ERROR_COLOR
        )

        print(
            f"Microphone error: {e}"
        )

        speak(
            "There was a problem accessing your microphone."
        )


def start_listening():
    """
    Start microphone listening in a separate thread
    so the GUI doesn't freeze.
    """

    listen_button.config(
        state=tk.DISABLED
    )

    thread = threading.Thread(
        target=listen_thread,
        daemon=True
    )

    thread.start()


def listen_thread():

    try:
        listen_microphone()

    finally:

        root.after(
            0,
            lambda: listen_button.config(
                state=tk.NORMAL
            )
        )


# ============================================================
# TEXT INPUT
# ============================================================

def send_text():

    query = input_entry.get().strip()

    if not query:
        return

    input_entry.delete(
        0,
        tk.END
    )

    process_command(query)


def on_enter(event):

    send_text()


# ============================================================
# GUI HEADER
# ============================================================

header = tk.Frame(
    root,
    bg=BG_COLOR
)

header.pack(
    fill=tk.X,
    padx=25,
    pady=(20, 10)
)


title_label = tk.Label(
    header,
    text="🎙 Voice Assistant",
    font=("Arial", 24, "bold"),
    bg=BG_COLOR,
    fg=TEXT_COLOR
)

title_label.pack(
    side=tk.LEFT
)


status_label = tk.Label(
    header,
    text="🎙 Ready",
    font=("Arial", 11),
    bg=BG_COLOR,
    fg=USER_COLOR
)

status_label.pack(
    side=tk.RIGHT,
    pady=8
)


# ============================================================
# CHAT AREA
# ============================================================

chat_frame = tk.Frame(
    root,
    bg=BG_COLOR
)

chat_frame.pack(
    fill=tk.BOTH,
    expand=True,
    padx=25,
    pady=10
)


chat_box = scrolledtext.ScrolledText(
    chat_frame,
    wrap=tk.WORD,
    font=("Arial", 12),
    bg=CHAT_BG,
    fg=TEXT_COLOR,
    insertbackground=TEXT_COLOR,
    relief=tk.FLAT,
    borderwidth=0,
    padx=15,
    pady=15
)

chat_box.pack(
    fill=tk.BOTH,
    expand=True
)


chat_box.tag_config(
    "sender",
    font=("Arial", 11, "bold")
)

chat_box.tag_config(
    "message",
    font=("Arial", 12)
)

chat_box.config(
    state=tk.DISABLED
)


# ============================================================
# INPUT AREA
# ============================================================

input_frame = tk.Frame(
    root,
    bg=BG_COLOR
)

input_frame.pack(
    fill=tk.X,
    padx=25,
    pady=(5, 20)
)


input_entry = tk.Entry(
    input_frame,
    font=("Arial", 13),
    bg=INPUT_BG,
    fg=TEXT_COLOR,
    insertbackground=TEXT_COLOR,
    relief=tk.FLAT
)

input_entry.pack(
    side=tk.LEFT,
    fill=tk.X,
    expand=True,
    ipady=12,
    padx=(0, 10)
)

input_entry.bind(
    "<Return>",
    on_enter
)


send_button = tk.Button(
    input_frame,
    text="Send",
    font=("Arial", 11, "bold"),
    bg=ACCENT,
    fg="white",
    activebackground=ACCENT_HOVER,
    activeforeground="white",
    relief=tk.FLAT,
    padx=20,
    pady=10,
    command=send_text
)

send_button.pack(
    side=tk.LEFT,
    padx=(0, 10)
)


listen_button = tk.Button(
    input_frame,
    text="🎙 Listen",
    font=("Arial", 11, "bold"),
    bg=ACCENT,
    fg="white",
    activebackground=ACCENT_HOVER,
    activeforeground="white",
    relief=tk.FLAT,
    padx=20,
    pady=10,
    command=start_listening
)

listen_button.pack(
    side=tk.LEFT
)


# ============================================================
# START ASSISTANT
# ============================================================

def start_assistant():

    # Give the UI a moment to appear first
    root.after(
        500,
        wish_user
    )


root.after(
    500,
    start_assistant
)


# ============================================================
# RUN GUI
# ============================================================

root.mainloop()

