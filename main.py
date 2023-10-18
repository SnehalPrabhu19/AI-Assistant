from datetime import datetime
import speech_recognition as sr
import pyttsx3  # text to speech
import webbrowser
import wikipedia
import wolframalpha

# Initialize Text to Speech engine object
engine = pyttsx3.init()
voices = engine.getProperty('voices')

# Speech rate (words per minute)
# engine.setProperty('rate', 150)  
# Volume (from 0.0 to 1.0)
# engine.setProperty('volume', 0.9) 
# Change the voice 
# engine.setProperty('voice', 'english-us')  

engine.setProperty('voice', voices[1].id)

activationWord = 'june'

# Configure browser by setting the path
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
webbrowser.register("chrome", None, webbrowser.BackgroundBrowser(chrome_path))

# wolfram alpha init
app_id = "YQXAW9-ETRQGL8Q9L"
wolframClient = wolframalpha.Client(app_id)

# convert text to speech
def speak(text, rate = 150):
    engine.setProperty('rate', rate)
    engine.say(text)
    engine.runAndWait()

# listen for commands
def parseCommand():
    listener = sr.Recognizer()
    print("Listening for a command..")

    with sr.Microphone() as source:
        listener.pause_threshold = 2
        audio_input = listener.listen(source)

    try: 
        print("Recognizing speech..")
        query = listener.recognize_google(audio_input, language='en_gb')
        print(f"The input speech was: {query}")

    except Exception as exception:
        print("I did not understand that")
        speak("I did not understand that")
        print(exception)
        return None

    return query

# search on wikipedia
def search_wiki(query=""):
    searchresult=wikipedia.search(query)
    if not searchresult:
        print("No wikipedia result found")
        return "No wikipedia result found"
    try:
        wikipage = wikipedia.page(searchresult[0])
    except wikipage.DisambiguationError as error:
        wikipage = wikipage.page(error.options[0])
    
    print(wikipage.title)
    wikisummary = str(wikipage.summary)
    return wikisummary    

def listOrdict(s):
    if isinstance(s,list):
        return s[0]["plaintext"]
    else:
        return s["plaintext"]     

# compute on wolfram alpha
def search_wolfram(query=""):
    response = wolframClient.query(query)

    if response["@success"] == False:
        return "Cound not compute"

    else:
        result=""
        # question
        pod0 = response["pod"][0]
        pod1 = response["pod"][1]
        # may contain the answer with the highest confidence value
        if (("result") in pod1["@title"].lower()) or (pod1.get("@primary","false")=="true") or ("definition" in pod1["@title"].lower()):
            result = listOrdict(pod1["subpod"])
            return result.split("(")[0]
        else:
            question = listOrdict(pod0["subpod"])
            return question.split("(")[0]
            # failed with wolfram so look into wiki
            speak("Computation failed. Now, quering the universal database.")
            search_wiki(question)


# main loop
if __name__ == "__main__":
    speak("All systems ready.")
    while True:
        # listen for activation word
        query = parseCommand().lower().split()
        if query[0]==activationWord:
            query.pop(0)

            # greetings 
            if query[0]=="say":
                if "hello" in query:
                    speak("Greetings, all.")
                else:
                    query.pop(0)
                    speech = " ".join(query)
                    speak(speech)

            # navigate to a webpage
            if query[0]=="go" and query[1]=="to":
                speak("Opening..")
                query = " ".join(query[2:])
                webbrowser.get("chrome").open_new(query)

            # access wikipedia
            if query[0]== "wikipedia":
                query=" ".join(query[1:])
                speak("Quesrying the universal databank.") 
                speak(search_wiki(query))

            # wolfram Alpha
            if query[0]=="compute" or query[0]=="computer":
                query = " ".join(query[1:])
                speak("Computing")
                try:
                    result = search_wolfram(query)
                    speak(result)
                except:
                    speak("Unable to compute.")    

            # Take notes
            if query[0]=="log":
                speak("Ready to record your notes.")
                note = parseCommand().lower()
                now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                with open("note_%s.txt" % now, w) as newfile:
                    newfile.write(note)
                speak("Note written")    

            # exit
            if query[0]=="exit":
                speak("Goodbye.")  
                break
