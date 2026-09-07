JARVIS - AI Desktop Assistant

> Final Year Project (FYP) - A voice and text based intelligent virtual assistant for Windows.

JARVIS is designed to interact with users through voice and text commands and perform various tasks such as opening applications, searching the web, sending emails, generating AI responses, and providing voice output. It features a modern desktop interface built with PyQt5.

---

##  Features

| Feature | Description |
|---------|-------------|
|  Voice Commands | Interact using speech recognition |
|  Text Commands | Type commands in the interface |
|  Web Searching | Search Google, YouTube, and Wikipedia |
|  App Launcher | Open system applications |
|  Email Sending | Send emails via voice/text |
|  AI Responses | OpenAI API powered replies |
|  Speech Output | Text-to-speech responses |
|  Memory | Stores previous commands |
|  Desktop UI | Modern PyQt5 interface |
|  Task Automation | Basic automation tasks |

---

##  Technologies Used



  Python 3.x
├── PyQt5              (Desktop UI)
├── SpeechRecognition  (Voice input)
├── pyttsx3            (Text-to-speech)
├── OpenAI API         (AI responses)
├── pywhatkit          (Web/Youtube search)
├── wikipedia-api      (Wikipedia queries)
├── smtplib            (Email sending)
└── Various APIs       (External services)



---

##  Project Structure



UOJ_JARVIS Final/
│
├── ai/                 # AI-related functionality
├── automation/         # Automation and system control
├── core/               # Core application logic
├── memory/             # Memory and stored information
├── nlp/                # Natural language processing
├── system/             # System-related functions
├── ui/                 # User interface (PyQt5)
├── voice/              # Speech recognition & output
├── assets/             # Images and application resources
│
├── main.py             # Entry point of application
├── requirements.txt    # Python dependencies
├── .gitignore          # Files ignored by Git
└── README.md           # Project documentation



---

##  How It Works

1. User provides a *voice command* or *types text* in the interface
2. JARVIS processes the command
3. Identifies the required action (web search, app open, AI response, etc.)
4. Executes the action
5. Displays result on screen and speaks it back

---

##  Installation & Setup

### 1️⃣ Clone the repository
bash
git clone https://github.com/hamnarubab103-max/JARVIS_AI_DESKTOP_ASSISTANT.git
cd JARVIS_AI_DESKTOP_ASSISTANT


2️⃣ Install dependencies

bash
pip install -r requirements.txt


3️⃣ Set up OpenAI API Key (if using AI features)

· Get your API key from OpenAI
· Create a .env file and add:


OPENAI_API_KEY=your_api_key_here


4: Run the application

bash
python main.py


---

 Example Commands

Command Action
"Hello JARVIS" Wakes up the assistant
"Search YouTube for Python" Opens YouTube with search
"What's the time?" Tells current time
"Open Notepad" Launches Notepad
"Send email to John" Opens email composer
"Tell me a joke" AI generates a joke
"Wikipedia AI" Searches Wikipedia
"Close" Exits the application


---

 Troubleshooting

Issue Solution
 Microphone not working Check Windows microphone permissions
 No voice output Install pyaudio: pip install pyaudio
 Email sending fails Enable "Less secure app access" in Google
 API Key error Verify OpenAI API key in .env

---

 Future Enhancements

☐ Add Gemini/Claude AI integration
☐ Mobile app version
☐ Multi-language support
☐ Custom wake word detection
☐ IoT device control
☐ Calendar/reminder integration

---

 Author

Hamna Rubab
    Final Year Project (FYP)
    hamnarubab103@gmail.com
    github.com/hamnarubab103-max

---

 Acknowledgments

· University supervisors for guidance
· Open source community for libraries
· OpenAI for API support

---

 License

This project is for educational purposes as part of a Final Year Project.
All rights reserved.

---

 Support

If this project helped you, please give it a ⭐ on GitHub!

---

Made  by Hamna Rubub