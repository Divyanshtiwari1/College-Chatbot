const chatbotToggler = document.querySelector(".chatbot-toggler");
const closeBtn = document.querySelector(".close-btn");
const chatbox = document.querySelector(".chatbox");
const chatInput = document.querySelector(".chat-input textarea");
const sendChatBtn = document.querySelector(".chat-input span");
const languageSelect = document.getElementById("language-select");

let userMessage = null;
let language = "en-US"; // Default Web Speech API language
let recognition;

// Initialize Web Speech API
function initializeSpeechRecognition() {
    if (!('webkitSpeechRecognition' in window)) {
        alert("Sorry, your browser doesn't support speech recognition.");
        return;
    }
    
    recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = language;
    
    recognition.onresult = (event) => {
        let transcript = Array.from(event.results)
            .map(result => result[0].transcript)
            .join('');
        chatInput.value = transcript;
    };
    
    recognition.onerror = (event) => {
        console.error("Speech recognition error:", event.error);
    };
    
    recognition.onend = () => {
        console.log("Speech recognition ended.");
    };
}

// Update the language for Web Speech API based on selection
languageSelect.addEventListener("change", function () {
    const selectedLanguage = languageSelect.value;
    switch (selectedLanguage) {
        case "Hindi":
            language = "hi-IN";
            break;
        case "Telugu":
            language = "te-IN";
            break;
        case "Marathi":
            language = "mr-IN";
            break;
        case "English":
        default:
            language = "en-US";
    }
    if (recognition) recognition.lang = language;
});

// Function to start speech recognition
function startRecognition() {
    if (recognition) {
        chatInput.value = ""; // Clear input before starting new recognition
        recognition.start();
    }
}

// Trigger speech recognition on microphone icon click
document.querySelector(".microphone-btn").addEventListener("click", startRecognition);

const createChatLi = (message, className) => {
    const chatLi = document.createElement("li");
    chatLi.classList.add("chat", `${className}`);
    let chatContent =
        className === "outgoing"
            ? `<p></p>`
            : `<span class="material-symbols-outlined">smart_toy</span><p></p>`;
    chatLi.innerHTML = chatContent;
    chatLi.querySelector("p").innerHTML = message;
    return chatLi;
};
const generateResponse = (chatElement) => {
    const messageElement = chatElement.querySelector("p");

    const requestOptions = {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            query: userMessage,
            college_name: "iiitn", // Hardcoded value for college
            lang: language
        }),
    };

    fetch("http://localhost:8000/ask_query", requestOptions)
        .then((res) => res.json())
        .then((data) => {
            console.log(data);
            messageElement.innerHTML = data
        })
        .catch(() => {
            messageElement.classList.add("error");
            messageElement.textContent =
                "Oops! Something went wrong. Please try again.";
        })
        .finally(() => chatbox.scrollTo(0, chatbox.scrollHeight));
};


const handleChat = () => {
    userMessage = chatInput.value.trim();
    if (!userMessage) return;

    chatInput.value = "";   
    chatbox.appendChild(createChatLi(userMessage, "outgoing"));
    chatbox.scrollTo(0, chatbox.scrollHeight);

    setTimeout(() => {
        const incomingChatLi = createChatLi("Thinking...", "incoming");
        chatbox.appendChild(incomingChatLi);
        chatbox.scrollTo(0, chatbox.scrollHeight);
        generateResponse(incomingChatLi);
        
    }, 600);
};

// Send message on "Enter" key press
chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault(); // Prevent newline on Enter
        handleChat();
    }
});

sendChatBtn.addEventListener("click", handleChat);
closeBtn.addEventListener("click", () =>
    document.body.classList.remove("show-chatbot")
);
chatbotToggler.addEventListener("click", () =>
    document.body.classList.toggle("show-chatbot")
);

initializeSpeechRecognition();
