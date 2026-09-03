import tkinter as tk
from tkinter import scrolledtext
import speech_recognition as sr
import pyttsx3
import wikipedia
import pyjokes
import webbrowser
import datetime
import requests
import threading
import re



# CONFIGURATION


AI_MODEL = "qwen3:1.7b"
OLLAMA_URL = "http://localhost:11434/api/generate"

ASSISTANT_NAME = "Nyx"



# INITIALIZE VOICE ENGINE


try:
    engine = pyttsx3.init()

    # Voice speed
    engine.setProperty("rate", 175)

    # Volume
    engine.setProperty("volume", 1.0)

except Exception as e:
    engine = None
    print("TTS initialization error:", e)



# SPEECH RECOGNIZER


recognizer = sr.Recognizer()

# Adjust these if your microphone is noisy
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.8



# AI CONVERSATION MEMORY


conversation = []



# GUI


root = tk.Tk()

root.title("Nyx AI Assistant")
root.geometry("900x650")
root.minsize(700, 500)

root.configure(bg="#101010")



# COLORS


BG_COLOR = "#101010"
CHAT_BG = "#181818"
INPUT_BG = "#202020"
TEXT_COLOR = "#FFFFFF"
USER_COLOR = "#00D4FF"
AI_COLOR = "#7CFF6B"
STATUS_COLOR = "#AAAAAA"
BUTTON_COLOR = "#252525"



# TITLE


title_label = tk.Label(
    root,
    text="NYX AI ASSISTANT",
    font=("Arial", 24, "bold"),
    bg=BG_COLOR,
    fg=AI_COLOR
)

title_label.pack(pady=(20, 5))


subtitle_label = tk.Label(
    root,
    text="Voice Assistant • Qwen 3 1.7B • Ollama",
    font=("Arial", 10),
    bg=BG_COLOR,
    fg=STATUS_COLOR
)

subtitle_label.pack(pady=(0, 15))



# CHAT BOX


chat_box = scrolledtext.ScrolledText(
    root,
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
    expand=True,
    padx=20,
    pady=5
)

chat_box.config(state=tk.DISABLED)



# CHAT TAGS


chat_box.tag_config(
    "user",
    foreground=USER_COLOR,
    font=("Arial", 12, "bold")
)

chat_box.tag_config(
    "assistant",
    foreground=AI_COLOR,
    font=("Arial", 12, "bold")
)

chat_box.tag_config(
    "normal",
    foreground=TEXT_COLOR,
    font=("Arial", 12)
)

chat_box.tag_config(
    "system",
    foreground=STATUS_COLOR,
    font=("Arial", 10, "italic")
)



# ADD MESSAGE TO CHAT


def add_message(sender, message, tag):
    chat_box.config(state=tk.NORMAL)

    chat_box.insert(
        tk.END,
        f"{sender}: ",
        tag
    )

    chat_box.insert(
        tk.END,
        f"{message}\n\n",
        "normal"
    )

    chat_box.config(state=tk.DISABLED)

    chat_box.see(tk.END)



# STATUS


status_label = tk.Label(
    root,
    text="Ready",
    font=("Arial", 10),
    bg=BG_COLOR,
    fg=STATUS_COLOR
)

status_label.pack(pady=5)


def set_status(text):
    root.after(
        0,
        lambda: status_label.config(text=text)
    )



# SPEAK


def speak(text):
    if engine is None:
        return

    try:
        engine.say(text)
        engine.runAndWait()

    except Exception as e:
        print("TTS error:", e)



# CLEAN AI RESPONSE


def clean_ai_response(text):

    # Remove Qwen's thinking tags if present
    text = re.sub(
        r"<think>.*?</think>",
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE
    )

    text = text.strip()

    return text



# ASK QWEN


def ask_ai(prompt):

    conversation.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    # Keep memory reasonable
    recent_conversation = conversation[-12:]

    history = ""

    for message in recent_conversation:

        if message["role"] == "user":
            history += f"User: {message['content']}\n"

        else:
            history += f"Assistant: {message['content']}\n"

    system_prompt = """
You are Nyx, a helpful desktop AI voice assistant.

Rules:
- Give useful and accurate answers.
- Keep answers reasonably short because your responses are spoken aloud.
- Do not use unnecessary emojis.
- If the user asks for programming help, provide practical explanations and code when useful.
- If you don't know something, say so.
- Do not pretend that you performed actions you cannot perform.
"""

    prompt_for_qwen = f"""
{system_prompt}

Conversation:
{history}

Assistant:
"""

    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": AI_MODEL,
                "prompt": prompt_for_qwen,
                "stream": False
            },
            timeout=180
        )

        response.raise_for_status()

        data = response.json()

        answer = data.get("response", "").strip()

        answer = clean_ai_response(answer)

        if not answer:
            answer = "I couldn't generate a response."

        conversation.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        return answer

    except requests.exceptions.ConnectionError:

        return (
            "I can't connect to Ollama. "
            "Make sure Ollama is running."
        )

    except requests.exceptions.Timeout:

        return (
            "Qwen took too long to respond. "
            "Try asking a shorter question."
        )

    except requests.exceptions.RequestException as e:

        print("Ollama request error:", e)

        return "There was a problem communicating with Ollama."

    except Exception as e:

        print("AI error:", e)

        return "Something went wrong while processing your request."



# WIKIPEDIA


def search_wikipedia(query):

    try:

        wikipedia.set_lang("en")

        result = wikipedia.summary(
            query,
            sentences=2
        )

        return result

    except wikipedia.exceptions.DisambiguationError as e:

        options = e.options[:5]

        return (
            "There are several results for that topic. "
            "Some possibilities are: "
            + ", ".join(options)
        )

    except wikipedia.exceptions.PageError:

        return "I couldn't find that topic on Wikipedia."

    except Exception as e:

        print("Wikipedia error:", e)

        return "I couldn't search Wikipedia right now."



# OPEN WEBSITE


def open_website(url):
    try:
        webbrowser.open(url)
        return True

    except Exception as e:
        print("Browser error:", e)
        return False



# GET TIME


def get_time():

    now = datetime.datetime.now()

    return now.strftime(
        "It is %I:%M %p."
    )



# PROCESS COMMAND


def process_command(command):

    command = command.strip()

    if not command:
        return

    add_message(
        "You",
        command,
        "user"
    )

    lower_command = command.lower()

    # ========================================================
    # EXIT
    # ========================================================

    if lower_command in [
        "exit",
        "quit",
        "goodbye",
        "bye",
        "close assistant"
    ]:

        response = "Goodbye Dead."

        add_message(
            ASSISTANT_NAME,
            response,
            "assistant"
        )

        set_status("Closing...")

        threading.Thread(
            target=speak,
            args=(response,),
            daemon=True
        ).start()

        root.after(
            1800,
            root.destroy
        )

        return

    # ========================================================
    # TIME
    # ========================================================

    if (
        "what time" in lower_command
        or "current time" in lower_command
        or lower_command == "time"
    ):

        response = get_time()

    # ========================================================
    # JOKE
    # ========================================================

    elif (
        "tell me a joke" in lower_command
        or "tell a joke" in lower_command
        or lower_command == "joke"
    ):

        try:
            response = pyjokes.get_joke()

        except Exception:
            response = "Why do programmers prefer dark mode? Because light attracts bugs."

    # ========================================================
    # YOUTUBE
    # ========================================================

    elif (
        "open youtube" in lower_command
        or lower_command == "youtube"
    ):

        open_website(
            "https://www.youtube.com"
        )

        response = "Opening YouTube."

    # ========================================================
    # GOOGLE
    # ========================================================

    elif (
        "open google" in lower_command
        or lower_command == "google"
    ):

        open_website(
            "https://www.google.com"
        )

        response = "Opening Google."

    # ========================================================
    # GITHUB
    # ========================================================

    elif (
        "open github" in lower_command
        or lower_command == "github"
    ):

        open_website(
            "https://github.com"
        )

        response = "Opening GitHub."

    # ========================================================
    # CHATGPT
    # ========================================================

    elif (
        "open chatgpt" in lower_command
        or lower_command == "chatgpt"
    ):

        open_website(
            "https://chatgpt.com"
        )

        response = "Opening ChatGPT."

    # ========================================================
    # WIKIPEDIA
    # ========================================================

    elif lower_command.startswith(
        "wikipedia "
    ):

        query = command[10:].strip()

        if query:

            set_status("Searching Wikipedia...")

            response = search_wikipedia(query)

        else:

            response = "Tell me what you want me to search for."

    # ========================================================
    # SEARCH GOOGLE
    # ========================================================

    elif lower_command.startswith(
        "search google for "
    ):

        query = command[
            len("search google for "):
        ].strip()

        if query:

            url = (
                "https://www.google.com/search?q="
                + requests.utils.quote(query)
            )

            open_website(url)

            response = f"Searching Google for {query}."

        else:

            response = "What should I search for?"

    # ========================================================
    # SEARCH YOUTUBE
    # ========================================================

    elif lower_command.startswith(
        "search youtube for "
    ):

        query = command[
            len("search youtube for "):
        ].strip()

        if query:

            url = (
                "https://www.youtube.com/results?search_query="
                + requests.utils.quote(query)
            )

            open_website(url)

            response = f"Searching YouTube for {query}."

        else:

            response = "What should I search for?"

    # ========================================================
    # WHO ARE YOU
    # ========================================================

    elif (
        "who are you" in lower_command
        or "what are you" in lower_command
    ):

        response = (
            "I'm Nyx, your desktop AI assistant. "
            "I'm powered by Qwen 3 1.7B running locally "
            "through Ollama."
        )

    # ========================================================
    # AI
    # ========================================================

    else:

        set_status("Qwen is thinking...")

        response = ask_ai(command)

    # ========================================================
    # SHOW RESPONSE
    # ========================================================

    add_message(
        ASSISTANT_NAME,
        response,
        "assistant"
    )

    set_status("Ready")

    # Speak in background
    threading.Thread(
        target=speak,
        args=(response,),
        daemon=True
    ).start()



# TEXT INPUT


input_frame = tk.Frame(
    root,
    bg=BG_COLOR
)

input_frame.pack(
    fill=tk.X,
    padx=20,
    pady=(5, 10)
)


entry = tk.Entry(
    input_frame,
    font=("Arial", 13),
    bg=INPUT_BG,
    fg=TEXT_COLOR,
    insertbackground=TEXT_COLOR,
    relief=tk.FLAT
)

entry.pack(
    side=tk.LEFT,
    fill=tk.X,
    expand=True,
    ipady=10,
    padx=(0, 10)
)



# SEND MESSAGE


def send_message(event=None):

    message = entry.get().strip()

    if not message:
        return

    entry.delete(
        0,
        tk.END
    )

    threading.Thread(
        target=process_command,
        args=(message,),
        daemon=True
    ).start()


send_button = tk.Button(
    input_frame,
    text="SEND",
    command=send_message,
    font=("Arial", 11, "bold"),
    bg=BUTTON_COLOR,
    fg=TEXT_COLOR,
    activebackground="#333333",
    activeforeground=TEXT_COLOR,
    relief=tk.FLAT,
    padx=20,
    pady=8
)

send_button.pack(
    side=tk.RIGHT
)



# MICROPHONE


def listen_microphone():

    try:

        set_status("Listening...")

        with sr.Microphone() as source:

            # Small calibration for ambient noise
            recognizer.adjust_for_ambient_noise(
                source,
                duration=0.5
            )

            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=15
            )

        set_status("Recognizing...")

        try:

            text = recognizer.recognize_google(
                audio
            )

            print("You said:", text)

            process_command(text)

        except sr.UnknownValueError:

            add_message(
                ASSISTANT_NAME,
                "I couldn't understand what you said.",
                "assistant"
            )

            set_status("Ready")

        except sr.RequestError:

            add_message(
                ASSISTANT_NAME,
                "Speech recognition needs an internet connection.",
                "assistant"
            )

            set_status("Ready")

    except sr.WaitTimeoutError:

        add_message(
            ASSISTANT_NAME,
            "I didn't hear anything.",
            "assistant"
        )

        set_status("Ready")

    except Exception as e:

        print("Microphone error:", e)

        add_message(
            ASSISTANT_NAME,
            f"Microphone error: {e}",
            "assistant"
        )

        set_status("Ready")



# MICROPHONE BUTTON


mic_button = tk.Button(
    input_frame,
    text="🎤",
    command=lambda: threading.Thread(
        target=listen_microphone,
        daemon=True
    ).start(),
    font=("Arial", 15),
    bg=BUTTON_COLOR,
    fg=TEXT_COLOR,
    activebackground="#333333",
    activeforeground=TEXT_COLOR,
    relief=tk.FLAT,
    padx=15,
    pady=5
)

mic_button.pack(
    side=tk.RIGHT,
    padx=(0, 10)
)



# ENTER KEY


entry.bind(
    "<Return>",
    send_message
)



# STARTUP MESSAGE


startup_message = (
    "Hey Dead. I'm Nyx.\n\n"
    "I'm connected to Qwen 3 1.7B through Ollama. "
    "You can talk to me using the microphone or type a message.\n\n"
    "Try:\n"
    "• What is Python?\n"
    "• Explain recursion\n"
    "• Write a Python calculator\n"
    "• Open YouTube\n"
    "• What time is it?\n"
    "• Tell me a joke\n"
    "• Wikipedia Albert Einstein"
)

add_message(
    ASSISTANT_NAME,
    startup_message,
    "assistant"
)



# START GUI


entry.focus()

root.mainloop()
