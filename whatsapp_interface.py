from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Twilio credentials from environment variables
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')

# Initialize Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def get_chatgpt_response(message):
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are PasalMate, a helpful store assistant. You help with inventory management, sales updates, and general store queries. Keep responses concise and helpful."},
                {"role": "user", "content": message}
            ],
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error: {str(e)}")
        return f"Sorry, I encountered an error: {str(e)}"

def send_whatsapp_message(to_number, message):
    try:
        message = twilio_client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=message,
            to=f'whatsapp:{to_number}'
        )
        return message.sid
    except Exception as e:
        print(f"Error sending message: {str(e)}")
        return None

app = Flask(__name__)

@app.route("/whatsapp", methods=["POST"])
def reply():
    incoming_msg = request.form.get("Body")
    sender_number = request.form.get("From").replace("whatsapp:", "")
    
    # Get response from ChatGPT
    chatgpt_response = get_chatgpt_response(incoming_msg)
    
    # Send response through Twilio
    message_sid = send_whatsapp_message(sender_number, chatgpt_response)
    
    if message_sid:
        return "Message sent successfully", 200
    else:
        return "Error sending message", 500

if __name__ == "__main__":
    app.run(debug=True)