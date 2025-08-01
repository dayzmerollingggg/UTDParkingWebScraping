from flask import Flask, render_template_string, request, jsonify
import datetime

# --- Flask Application Setup ---
app = Flask(__name__)

# --- Mock Data for AI Analysis ---
# In a real-world scenario, you would fetch this data from an API or a database.
# Here, we simulate a college events calendar and class schedule data.
mock_campus_calendar = {
    'holidays': [
        datetime.date(2025, 12, 24), # Christmas Eve
        datetime.date(2025, 12, 25), # Christmas Day
        datetime.date(2026, 1, 1),   # New Year's Day
    ],
    'exam_week_start': datetime.date(2025, 12, 8),
    'exam_week_end': datetime.date(2025, 12, 19),
    'class_schedule': {
        'Monday': ['9 AM - 11 AM', '1 PM - 3 PM'],
        'Tuesday': ['10 AM - 12 PM', '2 PM - 4 PM'],
        'Wednesday': ['9 AM - 11 AM', '1 PM - 3 PM'],
        'Thursday': ['10 AM - 12 PM', '2 PM - 4 PM'],
        'Friday': ['9 AM - 11 AM', '1 PM - 2 PM']
    }
}

# --- The Front-End HTML (served by Flask) ---
# This is a single-page app containing the graphs and the chatbot interface.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>College Parking Assistant</title>
    <style>
        body { font-family: sans-serif; margin: 20px; }
        .container { max-width: 900px; margin: auto; }
        .chat-container { border: 1px solid #ccc; padding: 10px; border-radius: 8px; margin-top: 20px; }
        .chat-messages { height: 200px; overflow-y: scroll; border-bottom: 1px solid #ccc; padding: 10px; }
        .user-message, .bot-message { margin: 5px 0; }
        .user-message { text-align: right; color: blue; }
        .bot-message { text-align: left; color: green; }
        .chat-input { display: flex; margin-top: 10px; }
        .chat-input input { flex-grow: 1; padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
        .chat-input button { padding: 8px 12px; margin-left: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h1>College Campus Parking Assistant</h1>

        <!-- Placeholder for the graphs -->
        <p>This is where your dynamically generated graphs will go. You can embed them as images here.</p>
        <img src="https://placehold.co/800x400?text=Parking+Spaces+Graph" alt="Parking spaces graph placeholder" style="max-width: 100%; height: auto;">

        <div class="chat-container">
            <h2>AI Parking Chatbot</h2>
            <div class="chat-messages" id="chat-messages">
                <div class="bot-message">Hello! I'm here to help you find the best time to park. Tell me your estimated arrival time and date (e.g., '3 PM on Friday, December 12th').</div>
            </div>
            <div class="chat-input">
                <input type="text" id="user-input" placeholder="Enter your time and date..." onkeydown="if(event.keyCode === 13) sendMessage()">
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>
    </div>

    <script>
        // Function to send user message and get a response from the backend
        async function sendMessage() {
            const userInput = document.getElementById('user-input');
            const userMessage = userInput.value;
            if (userMessage.trim() === '') return;

            const chatMessages = document.getElementById('chat-messages');
            
            // Display user message
            const userDiv = document.createElement('div');
            userDiv.className = 'user-message';
            userDiv.textContent = userMessage;
            chatMessages.appendChild(userDiv);
            userInput.value = '';

            // Scroll to the bottom
            chatMessages.scrollTop = chatMessages.scrollHeight;

            // Show a loading indicator while waiting for the bot
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'bot-message';
            loadingDiv.textContent = 'Assistant is thinking...';
            chatMessages.appendChild(loadingDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;

            try {
                // Send the message to the Flask API
                const response = await fetch('/chatbot', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: userMessage }),
                });

                const data = await response.json();
                
                // Remove loading indicator
                chatMessages.removeChild(loadingDiv);

                // Display bot's response
                const botDiv = document.createElement('div');
                botDiv.className = 'bot-message';
                botDiv.textContent = data.response;
                chatMessages.appendChild(botDiv);

                // Scroll to the bottom again
                chatMessages.scrollTop = chatMessages.scrollHeight;

            } catch (error) {
                console.error('Error fetching chatbot response:', error);
                chatMessages.removeChild(loadingDiv);
                const errorDiv = document.createElement('div');
                errorDiv.className = 'bot-message';
                errorDiv.textContent = 'Oops! Something went wrong. Please try again.';
                chatMessages.appendChild(errorDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        }
    </script>
</body>
</html>
"""

# --- Chatbot Logic Implementation ---
def get_parking_recommendation(user_message):
    """
    Analyzes user's request and provides a parking recommendation.
    This is the core "AI" logic.
    """
    # 1. Parse the user's message to extract time and date
    # This is a very simple parser. A real one would be more robust.
    user_message_lower = user_message.lower()
    
    # Try to parse a date
    # In a real app, you would use a library like 'dateutil' for this.
    today = datetime.date.today()
    try:
        if 'today' in user_message_lower:
            target_date = today
        elif 'tomorrow' in user_message_lower:
            target_date = today + datetime.timedelta(days=1)
        # Add more parsing for specific dates like 'December 12th' if needed
        else:
            return "Sorry, I couldn't understand the date. Please try 'today' or 'tomorrow'."
    except ValueError:
        return "Sorry, I couldn't understand the date format. Please try again."

    # 2. Analyze the date against the mock calendar
    if target_date in mock_campus_calendar['holidays']:
        return "That day is a holiday! Garages should be very empty. You can park anytime."

    if mock_campus_calendar['exam_week_start'] <= target_date <= mock_campus_calendar['exam_week_end']:
        return "That date falls during exam week. Garages are likely to be busy all day, especially in the mornings."

    # 3. Analyze the time against the class schedule
    weekday = target_date.strftime('%A')
    busy_times = mock_campus_calendar['class_schedule'].get(weekday)

    if not busy_times:
        return f"That's a {weekday}. I don't have class schedule data for that day. Parking might be okay."
    
    # Simple rule-based logic
    message_to_user = f"Based on the class schedule for {weekday}: "
    if 'morning' in user_message_lower:
        message_to_user += f"Morning hours might be busy, especially during {busy_times[0]}. Try to arrive earlier or later."
    elif 'afternoon' in user_message_lower:
        message_to_user += f"Afternoon hours might be busy, especially during {busy_times[1]}. Consider arriving outside of those times."
    else:
        message_to_user += "I see that there are classes scheduled. To find a time with the least amount of traffic, I recommend avoiding peak class times."

    return message_to_user


# --- Flask Routes ---
@app.route('/')
def home():
    """
    Serves the main web page.
    """
    return render_template_string(HTML_TEMPLATE)

@app.route('/chatbot', methods=['POST'])
def chatbot_api():
    """
    API endpoint for the chatbot.
    Receives user message and returns a recommendation.
    """
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'response': 'Please provide a message.'})
    
    recommendation = get_parking_recommendation(user_message)
    return jsonify({'response': recommendation})

# --- Main execution block ---
if __name__ == '__main__':
    # Setting debug=True is good for development, but should be False in production.
    app.run(debug=True)

