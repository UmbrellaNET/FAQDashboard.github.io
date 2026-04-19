import traceback
import requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

# ------------------------------------------------
# 🔑 WhatsApp Cloud API credentials

WHATSAPP_TOKEN = "EAARXw3STgtMBPc3ZCOBukJUSor36yXhTzOqkfLgy4y20nZCUmkFVpszm3N0TEZBkXZBzZBh9c4x6gYJcf0di3oWIDogZCcAul3mHmQJBsJqIe7Yet5HgOsVyR27XJF1jcDjc0DnzNZA0gFedmuOUDA3JRFkeuWvE5L6LmvaEPFJlAVrU322PHZADK1sKZBZAZAAdsZAgqQZDZD"
PHONE_NUMBER_ID = "810217165499672"  # from Meta dashboard
VERIFY_TOKEN = "BOT"  
# ------------------------------------------------


# Serve chats.html when opening http://127.0.0.1:5000/
@app.route('/')
def index():
    return send_from_directory('.', 'chats.html')


# 🔹 WhatsApp webhook (GET = verify, POST = incoming messages)
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Verify webhook
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return 'Forbidden', 403

    elif request.method == 'POST':
        try:
            data = request.get_json()
            print(f"Incoming webhook data: {data}")

            if data.get('object') == 'whatsapp_business_account':
                for entry in data.get('entry', []):
                    for change in entry.get('changes', []):
                        if change.get('field') == 'messages':
                            value = change.get('value')
                            if value:
                                message = value.get('messages', [{}])[0]
                                sender = message.get('from')
                                msg_type = message.get('type')
                                text = None

                                if msg_type == 'text':
                                    text = message.get('text', {}).get('body', '')

                                elif msg_type == 'interactive':
                                    interactive = message.get('interactive', {})
                                    if interactive.get('type') == 'button_reply':
                                        text = interactive['button_reply'].get('title')
                                    elif interactive.get('type') == 'list_reply':
                                        text = interactive['list_reply'].get('title')

                                elif msg_type == 'image':
                                    text = f"IMAGE ID: {message['image'].get('id')}"

                                print(f"📩 Message from {sender}: {text}")

            return jsonify({'status': 'success'}), 200

        except Exception as e:
            print(f"Error processing webhook: {e}")
            print(traceback.format_exc())
            return jsonify({'status': 'error', 'message': str(e)}), 500

    return jsonify({'status': 'bad_request'}), 400


# 🔹 Endpoint to send outbound WhatsApp messages
@app.route('/sendWhatsApp', methods=['POST'])
def send_whatsapp():
    try:
        data = request.get_json()
        recipient = data.get("to")
        message = data.get("message")

        url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "text",
            "text": {"body": message}
        }

        r = requests.post(url, headers=headers, json=payload)

        # Debug log
        print("WhatsApp API response:", r.status_code, r.text)

        if r.status_code >= 400:
            return jsonify({"status": "error", "response": r.json()}), r.status_code

        return jsonify({"status": "sent", "response": r.json()}), 200
    except Exception as e:
        print("Error sending message:", e)
        print(traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)
