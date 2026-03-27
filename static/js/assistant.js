/**
 * CampusBot - Advanced AI Assistant for CampusGig
 * 
 * Features:
 * - Dual Mode: Chat & Voice (Parity with DocuDigitize-v4)
 * - Quick Assist: Dynamic suggestion pills for fast interaction
 * - Contextual Intelligence: Specialized knowledge about CampusGig platform
 * - Speech Synthesis & Recognition: Full accessibility support
 */

document.addEventListener('DOMContentLoaded', () => {
    // --- Configuration & Knowledge Base ---
    
    // Quick Assist Suggestions (Initial state)
    const INITIAL_SUGGESTIONS = [
        "Browse Gigs", 
        "How to hire?", 
        "Post a Gig", 
        "Show Dashboard"
    ];

    // Comprehensive Knowledge Base for "Proper Replies"
    const KNOWLEDGE_BASE = {
        "pricing": "Joining CampusGig is free! Platform fees vary based on the project size, typically between 5-10% to support the community matching.",
        "trust": "Your safety is our priority. We use a secure escrow system for payments and a verified student-only registration process.",
        "categories": "We currently support: Web Development, Graphic Design, Content Writing, Marketing, and Tutoring.",
        "mission": "CampusBot's goal is to empower students by connecting their unique talents with real-world opportunities right on campus.",
        "contact": "You can reach our human support team at support@campusgig.edu or visit the help center in your dashboard.",
        "payment": "We support credit cards, PayPal, and campus-specific payment credits. Funds are held in escrow until you approve the work."
    };

    // Predefined Conversational Responses
    const RESPONSES = {
        "hello": "Hi there! I'm CampusBot, your personal assistant. How can I help you with your student freelancing journey today?",
        "hi": "Hello! Ready to discover amazing student talent or start your own gig?",
        "how are you": "I'm functioning at 100%! Ready to help you navigate the platform and find the best opportunities.",
        "what is campusgig": "CampusGig is a revolutionary platform where students can showcase their skills and find freelance opportunities within their own university community.",
        "how to hire": "Hiring is easy! Browse the 'Gigs' page, select a student profile you like, and click 'Hire Now'. We'll guide you through the secure booking.",
        "how to work": "Students can earn by creating a 'Gig' from their dashboard. Showcase your portfolio, set your price, and start getting hired by peers!",
        "thank you": "You're very welcome! Is there anything else I can assist you with today?",
        "thanks": "Anytime! I'm here to help.",
        "help": "I can assist with navigation, platform rules, or technical issues. Try asking about 'pricing', 'security', or 'how to post a gig'."
    };

    // Navigation Commands mapping to site URLs
    const COMMANDS = {
        "go to gigs": CAMPUSGIG_URLS.gigs,
        "browse gigs": CAMPUSGIG_URLS.gigs,
        "find gigs": CAMPUSGIG_URLS.gigs,
        "go to dashboard": CAMPUSGIG_URLS.dashboard,
        "show dashboard": CAMPUSGIG_URLS.dashboard,
        "go to home": CAMPUSGIG_URLS.home,
        "go to login": CAMPUSGIG_URLS.login,
        "sign in": CAMPUSGIG_URLS.login,
        "go to register": CAMPUSGIG_URLS.register,
        "join": CAMPUSGIG_URLS.register,
        "go to cart": CAMPUSGIG_URLS.cart,
        "show cart": CAMPUSGIG_URLS.cart,
        "logout": CAMPUSGIG_URLS.logout,
        "sign out": CAMPUSGIG_URLS.logout,
        "post a gig": CAMPUSGIG_URLS.dashboard // Usually where posting happens
    };

    // --- DOM Elements ---
    const navToggle = document.getElementById('assistant-nav-toggle');
    const navToggleIcon = document.getElementById('nav-toggle-icon');
    const assistantTrigger = document.getElementById('assistant-trigger');
    const triggerIcon = document.getElementById('trigger-icon');
    const assistantWindow = document.getElementById('assistant-window');
    const assistantClose = document.getElementById('assistant-close');
    const assistantMessages = document.getElementById('assistant-messages');
    const assistantInput = document.getElementById('assistant-input-field');
    const assistantSend = document.getElementById('assistant-send');
    const assistantLoading = document.getElementById('assistant-loading');
    const assistantSuggestions = document.getElementById('assistant-suggestions');
    
    // Voice elements
    const voiceOverlay = document.getElementById('voice-overlay');
    const voiceTranscript = document.getElementById('voice-transcript');
    const voiceResponse = document.getElementById('voice-response');

    // --- State Management ---
    let assistantMode = localStorage.getItem('assistantMode') || 'chat'; 
    let isVoiceActive = false;
    let recognition;
    let transcriptTimeout;

    /**
     * Initialize Assistant UI and Logic
     */
    const init = () => {
        updateModeUI();
        addMessage("Hello! I'm your CampusBot. How can I help you navigate CampusGig today? I can help you find work or hire talent!", 'assistant');
        renderSuggestions(INITIAL_SUGGESTIONS);
        
        // --- Web Speech API Setup ---
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = true;
            recognition.lang = 'en-US';

            recognition.onstart = () => {
                isVoiceActive = true;
                voiceTranscript.textContent = "Listening...";
                voiceResponse.textContent = "";
                voiceOverlay.style.display = 'block';
                triggerIcon.className = "fas fa-microphone animate-pulse";
                triggerIcon.style.color = "#ef4444";
            };

            recognition.onresult = (event) => {
                const transcript = Array.from(event.results)
                    .map(result => result[0].transcript)
                    .join('');
                voiceTranscript.textContent = transcript;
                
                if (event.results[0].isFinal) {
                    processInput(transcript);
                }
            };

            recognition.onerror = (event) => {
                console.error("Speech Recognition Error:", event.error);
                stopVoice();
                voiceTranscript.textContent = "Error: " + event.error;
            };

            recognition.onend = () => {
                isVoiceActive = false;
                triggerIcon.style.color = "white";
                triggerIcon.classList.remove('animate-pulse');
                
                clearTimeout(transcriptTimeout);
                transcriptTimeout = setTimeout(() => {
                    if (!isVoiceActive) voiceOverlay.style.display = 'none';
                }, 5000);
            };
        }
    };

    /**
     * Update UI based on current mode (Chat vs Voice)
     */
    const updateModeUI = () => {
        assistantWindow.style.display = 'none';
        voiceOverlay.style.display = 'none';
        
        if (assistantMode === 'chat') {
            navToggleIcon.className = "fas fa-comment-dots";
            triggerIcon.className = "fas fa-comments"; // Upgraded from robot to chat icon
            navToggle.title = "Switch to Voice Assistant";
        } else {
            navToggleIcon.className = "fas fa-microphone";
            triggerIcon.className = "fas fa-microphone";
            navToggle.title = "Switch to Chat Assistant";
        }
    };

    /**
     * Render Quick Assist suggestion pills
     */
    const renderSuggestions = (suggestions) => {
        assistantSuggestions.innerHTML = '';
        suggestions.forEach(text => {
            const pill = document.createElement('div');
            pill.className = 'suggestion-pill';
            pill.textContent = text;
            pill.addEventListener('click', () => {
                assistantInput.value = text;
                processInput(text);
            });
            assistantSuggestions.appendChild(pill);
        });
    };

    /**
     * Main Logic: Process user message and determine best response
     */
    const processInput = (text) => {
        const input = text.trim().toLowerCase();
        if (!input) return;

        // Visual feedback for processing
        if (assistantMode === 'chat') {
            addMessage(text, 'user');
            assistantLoading.style.display = 'block';
            assistantInput.value = '';
        }

        // Delay to simulate "thinking" / AI processing
        setTimeout(() => {
            let response = null;
            let navigateTo = null;

            // 1. Check for high-priority Navigation Commands
            for (const [cmd, url] of Object.entries(COMMANDS)) {
                if (input.includes(cmd)) {
                    response = `Perfect! Taking you to the ${cmd.replace('go to ', '')} page now.`;
                    navigateTo = url;
                    break;
                }
            }

            // 2. Check for Specific Knowledge Base entries
            if (!response) {
                for (const [key, val] of Object.entries(KNOWLEDGE_BASE)) {
                    if (input.includes(key)) {
                        response = val;
                        break;
                    }
                }
            }

            // 3. Check for standard Conversational Responses
            if (!response) {
                for (const [key, val] of Object.entries(RESPONSES)) {
                    if (input.includes(key)) {
                        response = val;
                        break;
                    }
                }
            }

            // 4. Fallback for unknown queries
            if (!response) {
                response = "I'm still learning about that! You can try asking about our 'categories', 'security', or 'how to hire' students.";
            }

            // Handle display based on mode
            if (assistantMode === 'chat') {
                assistantLoading.style.display = 'none';
                addMessage(response, 'assistant');
                // Potentially update suggestions based on context
                if (input.includes("hire")) renderSuggestions(["Pricing", "Security", "Browse Gigs"]);
                else if (input.includes("work")) renderSuggestions(["Categories", "Post a Gig", "Dashboard"]);
            } else {
                voiceResponse.textContent = response;
            }

            // Speak response if enabled
            speak(response);

            // Execute navigation if applicable
            if (navigateTo) {
                setTimeout(() => { window.location.href = navigateTo; }, 2000);
            }
        }, 1000);
    };

    const addMessage = (text, sender) => {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}`;
        msgDiv.textContent = text;
        assistantMessages.appendChild(msgDiv);
        assistantMessages.scrollTop = assistantMessages.scrollHeight;
    };

    const speak = (text) => {
        if (!window.speechSynthesis) return;
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.1; // Slightly faster for natural feel
        window.speechSynthesis.speak(utterance);
    };

    const switchMode = () => {
        assistantMode = assistantMode === 'chat' ? 'voice' : 'chat';
        localStorage.setItem('assistantMode', assistantMode);
        updateModeUI();
    };

    const toggleAssistant = () => {
        if (assistantMode === 'chat') {
            assistantWindow.style.display = assistantWindow.style.display === 'none' ? 'flex' : 'none';
            if (assistantWindow.style.display === 'flex') assistantInput.focus();
        } else {
            if (isVoiceActive) stopVoice();
            else startVoice();
        }
    };

    const startVoice = () => recognition ? recognition.start() : alert("Voice not supported.");
    const stopVoice = () => recognition && recognition.stop();

    // --- Global Event Listeners ---
    navToggle.addEventListener('click', switchMode);
    assistantTrigger.addEventListener('click', toggleAssistant);
    assistantClose.addEventListener('click', () => { assistantWindow.style.display = 'none'; });
    
    assistantSend.addEventListener('click', () => processInput(assistantInput.value));
    assistantInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') processInput(assistantInput.value);
    });

    // Special Helper for the Login Page
    if (window.location.pathname.includes('/login/')) {
        setTimeout(() => {
            if (assistantMode === 'chat' && assistantWindow.style.display === 'none') {
                toggleAssistant();
                addMessage("Welcome back! Remember, you can use the test credentials if you're just exploring the platform.", 'assistant');
            }
        }, 3000);
    }

    init();
});
