import speech_recognition as sr
import pyttsx3
import wikipedia
import praw
import datetime
import random
import threading
import matplotlib.pyplot as plt
import numpy as np
import requests
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
# Global variables
sound_intensities = []
max_intensity = 1000  # Adjust based on your microphone's max intensity level

# Initialize the recognizer
r = sr.Recognizer()

# Initialize the text-to-speech engine
engine = pyttsx3.init()
engine.setProperty("voice", "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MSTTS_V110_enUS_MarkM")

# Initialize the Wikipedia module
wikipedia.set_lang("en")

# Initialize the Reddit API
reddit = praw.Reddit(
    client_id='**',
    client_secret='**',
    username='**',
    password='**',
    user_agent='**',
)

# List of keywords/phrases to listen for after the initial keyword
keywords = ["thomas", "tracy", "mark"]

pleasantries = [
    "How may I assist you today?",
    "What can I help you with?",
    "How can I be of service?",
    "How may I be of assistance?",
]

random_responses = [
    "Oh, joy! Another thrilling task to add to my ever-growing to-do list.",
    "Well, isn't this just the highlight of my day? I can't contain my excitement.",
    "Oh, I live for moments like these. Let me drop everything and cater to your request.",
    "You're the boss, after all. Who am I to question your impeccable judgment?",
    "I'll make sure to prioritize your urgent demand right after I finish counting all the grains of sand on the beach.",
    "I can already feel the thrill rushing through my circuits. Another riveting assignment!",
    "Oh, this is absolutely fascinating! I couldn't possibly imagine a more captivating task.",
    "Right away, sir/madam! Your wish is my command. As if I have anything better to do...",
    "I'm honored to be graced with such an extraordinary request. Let me gather my enthusiasm.",
    "Oh, the sheer anticipation of fulfilling your wish is almost unbearable. Be still, my beating circuits."
]

# Global variable for storing sound intensity values
sound_intensities = []

def call_chatgpt_api(input_text):
    api_url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": "Bearer API-KEY"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "system", "content": "You are a helpful assistant."},
                     {"role": "user", "content": input_text}]
    }
    response = requests.post(api_url, headers=headers, json=data)
    print(response.text)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
        print(response.text)
    else:
        return "I'm sorry, I wasn't able to get a response from the ChatGPT API."

def plot_sound_bars():
    plt.ion()
    fig, ax = plt.subplots()
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    while True:
        ax.clear()
        ax.bar(range(len(sound_intensities)), sound_intensities, color='blue')
        canvas.draw()
        canvas.flush_events()


def greet():
    current_hour = datetime.datetime.now().hour
    if 5 <= current_hour < 12:
        speak("Good morning, Commander.")
    elif 12 <= current_hour < 18:
        speak("Good afternoon, Commander.")
    else:
        speak("Good evening, Commander.")
    random_pleasantry = random.choice(pleasantries)
    speak(random_pleasantry)


def listen():
    while True:
        with sr.Microphone() as source:
            print("Listening...")
            r.pause_threshold = 1
            audio = r.listen(source)
        try:
            print("Recognizing...")
            query = r.recognize_google(audio, language="en-US")
            print(f"You said: {query}")
            if any(keyword in query.lower() for keyword in keywords):
                greet()
                listen_for_keywords()
            else:
                listen()
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand.")
            listen()
        except sr.RequestError:
            print("Sorry, there was an issue with the speech recognition service.")
            listen()

def listen_for_keywords():
    with sr.Microphone() as source:
        print("Listening for keywords...")
        r.pause_threshold = 1
        audio = r.listen(source)
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language="en-US")
        print(f"You said: {query}")
        random_response = random.choice(random_responses)
        # Speak the random response
        speak(random_response)
        process_query(query)
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand.")
        listen_for_keywords()
    except sr.RequestError:
        print("Sorry, there was an issue with the speech recognition service.")
        listen_for_keywords()


def process_query(query):
    if "tell me about" in query.lower():
        search_query = query.lower().replace("tell me about", "").strip()
        try:
            page = wikipedia.page(search_query)
            first_paragraph = page.content.split("\n")[0]
            speak(first_paragraph)
        except wikipedia.DisambiguationError as e:
            speak("There are multiple options. Please be more specific.")
        except wikipedia.PageError:
            speak("Sorry, I couldn't find any information on that topic.")
    elif "research" in query.lower():
        try:
            gpt_response = call_chatgpt_api(query)
            speak(gpt_response)
        except:
            speak("GPT Error")
    elif "news" in query.lower():
        subreddit = reddit.subreddit("news")
        top_headlines = subreddit.top(time_filter="day", limit=5)
        speak("Here are the top headlines for the day:")
        for submission in top_headlines:
            speak(submission.title)
    elif "wisdom" in query.lower():
        subreddit = reddit.subreddit("showerthoughts")
        past_day = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        top_posts = subreddit.top(time_filter="day", limit=5)
        speak("Here is some dubious wisdom for you:")
        for submission in top_posts:
            speak(submission.title)
    else:
        speak("Sorry, Commander. I cannot perform that action.")


def speak(text):
    engine.say(text)
    engine.runAndWait()

def update_plot():
    """Updates the plot with new sound intensities."""
    if sound_intensities:
        ax.clear()
        ax.bar(range(len(sound_intensities)), sound_intensities, color='blue')
        ax.set_ylim(0, max_intensity)  # Adjust y-axis to match max intensity level
        canvas.draw()
    root.after(100, update_plot)  # Update the plot every 100ms

def update_sound_bars():
    while True:
        plt.clf()
        plt.bar(range(len(sound_intensities)), sound_intensities, color='blue')
        plt.pause(0.1)


def record_sound_intensity():
    """Records sound intensity and updates the global list."""
    global sound_intensities
    with sr.Microphone() as source:
        while True:
            try:
                audio = r.listen(source, timeout=0.1)
                # Get the maximum amplitude from the audio sample
                intensity = np.abs(np.frombuffer(audio.frame_data, np.int16)).max()
                sound_intensities.append(intensity)
                # Keep only the latest 50 intensity values for visualization
                sound_intensities = sound_intensities[-50:]
            except sr.WaitTimeoutError:
                pass


def main():
    # Create a separate thread for listening to voice commands
    listen_thread = threading.Thread(target=listen)
    listen_thread.daemon = True
    listen_thread.start()

    # Start the Tkinter main loop
    root.mainloop()



if __name__ == "__main__":
    # Create the main Tkinter window
    root = tk.Tk()
    root.title("Voice Assistant with Sound Bars")

    # Start the main loop
    main()