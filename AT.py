from flask import Flask, request, jsonify
import sqlite3
import africastalking
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables
load_dotenv()
AT_USERNAME = os.getenv("AT_USERNAME")
AT_API_KEY = os.getenv("AT_API_KEY")

# Initialize Africa's Talking SDK
africastalking.initialize(AT_USERNAME, AT_API_KEY)
sms = africastalking.SMS

# Database setup
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            phone_number TEXT PRIMARY KEY,
            travel_mode INTEGER DEFAULT 0
        )
    """)

    # Fraud alerts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fraud_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT,
            alert TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

init_db()

def ussd_callback():
    session_id = request.form.get("sessionId")
    phone_number = request.form.get("phoneNumber")
    text = request.form.get("text", "")

    user_inputs = text.split("*")

    # Menu Options
    if text == "":
        travel_mode_status = check_travel_mode(phone_number)
        travel_mode_text = "ON" if travel_mode_status else "OFF"
        response = (
            f"CON Welcome to SafiriGuard.\n"
            f"Travel Mode: {travel_mode_text}\n"
            "1. Activate Travel Mode\n"
            "2. Deactivate Travel Mode\n"
            "3. Check Fraud Alerts\n"
            "4. Report Fraud\n"
            "99. Exit"
        )
    
    elif text == "1":
        response = activate_travel_mode(phone_number)

    elif text == "2":
        response = deactivate_travel_mode(phone_number)

    elif text == "3":
        response = get_fraud_alerts(phone_number)

    elif text.startswith("4*"):
        report_text = text[2:]  # Extract the report message
        save_fraud_report(phone_number, report_text)
        response = "END Thank you! Your fraud report has been submitted."

    elif text == "99":
        response = "END Thank you for using SafiriGuard. Stay safe!"
    
    else:
        response = "CON Invalid input. Try again.\n0. Back"

    # Return the response as plain text (important for USSD gateways)
    return Response(response, mimetype="text/plain")

# Function to check Travel Mode status
def check_travel_mode(phone_number):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT travel_mode FROM users WHERE phone_number = ?", (phone_number,))
    result = cursor.fetchone()
    conn.close()
    return result[0] == 1 if result else False

# Function to activate Travel Mode & send SMS
def activate_travel_mode(phone_number):
    if check_travel_mode(phone_number):
        return "CON Travel Mode is already ON.\n0. Back"
    else:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (phone_number, travel_mode) VALUES (?, ?) ON CONFLICT(phone_number) DO UPDATE SET travel_mode=1", (phone_number, 1))
        conn.commit()
        conn.close()

        send_sms(phone_number, "🚨 Travel Mode ACTIVATED! Transactions will require extra security. Stay safe with SafiriGuard.")

        return "CON Travel Mode Activated! You'll receive an SMS confirmation.\n0. Back"

# Function to deactivate Travel Mode & send SMS
def deactivate_travel_mode(phone_number):
    if not check_travel_mode(phone_number):
        return "CON Travel Mode is already OFF.\n0. Back"
    else:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET travel_mode=0 WHERE phone_number=?", (phone_number,))
        conn.commit()
        conn.close()

        send_sms(phone_number, "🚨 Travel Mode DEACTIVATED. Normal transactions will resume. Stay safe!")

        return "CON Travel Mode Deactivated! You'll receive an SMS confirmation.\n0. Back"

# Function to send SMS
def send_sms(phone_number, message):
    try:
        sms.send(message, [phone_number])
    except Exception as e:
        print(f"SMS sending failed: {e}")

# Fraud detection function
def detect_fraud(phone_number, transaction_amount):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Check if recent SIM swap exists
    cursor.execute("SELECT COUNT(*) FROM sim_swaps WHERE phone_number = ? AND timestamp >= datetime('now', '-1 day')", (phone_number,))
    recent_sim_swaps = cursor.fetchone()[0]

    # Check if transaction amount is unusually high (e.g., over 50,000 KES)
    high_value_transaction = int(transaction_amount) > 50000

    if recent_sim_swaps > 0 or high_value_transaction:
        # Store fraud alert in the database
        alert_message = f"🚨 Fraud Alert: Suspicious transaction of KES {transaction_amount} detected!"
        print(alert_message)
        cursor.execute("INSERT INTO fraud_alerts (phone_number, alert) VALUES (?, ?)", (str(phone_number), alert_message))
        conn.commit()

        # Send SMS alert
        sms.send(alert_message, [f"+254{phone_number}"])

        print(f"Fraud alert triggered for {phone_number}")  

    conn.close()

# Simulate a transaction endpoint
@app.route("/transaction", methods=["POST"])
def transaction():
    try:
        phone_number = request.form.get("phoneNumber")
        amount = request.form.get("amount")
        
        print(f"Received transaction request: phone={phone_number}, amount={amount}")

        detect_fraud(phone_number, amount)  # This function may be causing the issue

        return jsonify({"status": "Transaction processed"})
    
    except Exception as e:
        print("Error processing transaction:", str(e))
        return jsonify({"error": "Internal Server Error"}), 500


# Function to get fraud alerts from the database
def get_fraud_alerts(phone_number):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT alert FROM fraud_alerts WHERE phone_number = ? ORDER BY timestamp DESC LIMIT 3", (phone_number,))
    alerts = cursor.fetchall()
    conn.close()

    print("Fetched Alerts:", alerts) 

    if alerts:
        alert_messages = "\n".join([f"- {alert[0]}" for alert in alerts])
        return f"CON Fraud Alerts:\n{alert_messages}\n0. Back"
    
    
    else:
        return "CON No fraud alerts found. Stay safe!\n0. Back"

# Function to save fraud reports (Simulating fraud detection)
def save_fraud_report(phone_number, report):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO fraud_alerts (phone_number, alert) VALUES (?, ?)", (phone_number, report))
    conn.commit()
    conn.close()

    send_sms(phone_number, f"🚨 Fraud Report Received! '{report}' has been logged for investigation.")

if __name__ == '__main__':
    app.run(port=5000)



# from flask import Flask, request, jsonify
# import sqlite3
# import africastalking
# import os
# from dotenv import load_dotenv

# app = Flask(__name__)

# # Load environment variables
# load_dotenv()
# AT_USERNAME = os.getenv("AT_USERNAME")
# AT_API_KEY = os.getenv("AT_API_KEY")

# # Initialize Africa's Talking SDK
# africastalking.initialize(AT_USERNAME, AT_API_KEY)
# sms = africastalking.SMS

# # Database setup
# def init_db():
#     conn = sqlite3.connect("database.db")
#     cursor = conn.cursor()
    
#     # Users table
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS users (
#             phone_number TEXT PRIMARY KEY,
#             travel_mode INTEGER DEFAULT 0
#         )
#     """)

#     # Fraud alerts table
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS fraud_alerts (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             phone_number TEXT,
#             alert TEXT,
#             timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
#         )
#     """)
    
#     conn.commit()
#     conn.close()

# init_db()

# @app.route('/ussd', methods=['POST'])
# def ussd_callback():
#     session_id = request.form.get("sessionId")
#     phone_number = request.form.get("phoneNumber")
#     text = request.form.get("text", "")

#     user_inputs = text.split("*")

#     if text == "":
#         travel_mode_status = check_travel_mode(phone_number)
#         travel_mode_text = "ON" if travel_mode_status else "OFF"
#         response = f"CON Welcome to SafiriGuard.\nTravel Mode: {travel_mode_text}\n1. Activate Travel Mode\n2. Deactivate Travel Mode\n3. Check Fraud Alerts\n4. Report Fraud\n99. Exit"
    
#     elif text == "1":
#         response = activate_travel_mode(phone_number)

#     elif text == "2":
#         response = deactivate_travel_mode(phone_number)

#     elif text == "3":
#         response = get_fraud_alerts(f"+254{phone_number}")

#     # elif text == "3":  # View Fraud Alerts
#     #     alerts = get_fraud_alerts('+254715025259')
#     #     if not alerts:
#     #         response = "END No fraud alerts found."
#     #     else:
#     #         response = "END Recent Fraud Alerts:\n"
#     #         for alert in alerts:
#     #             response += f"- {alert[1]} ({alert[2]})\n"  # Adjust indexing based on your table structure


#     elif text.startswith("4*"):
#         report_text = text[2:]
#         save_fraud_report(phone_number, report_text)
#         response = "END Thank you! Your fraud report has been submitted."

#     elif text == "99":
#         response = "END Thank you for using SafiriGuard. Stay safe!"
    
#     else:
#         response = "CON Invalid input. Try again.\n0. Back"

#     return response

# # Function to check Travel Mode status
# def check_travel_mode(phone_number):
#     conn = sqlite3.connect("database.db")
#     cursor = conn.cursor()
#     cursor.execute("SELECT travel_mode FROM users WHERE phone_number = ?", (phone_number,))
#     result = cursor.fetchone()
#     conn.close()
#     return result[0] == 1 if result else False

# # Function to activate Travel Mode & send SMS
# def activate_travel_mode(phone_number):
#     if check_travel_mode(phone_number):
#         return "CON Travel Mode is already ON.\n0. Back"
#     else:
#         conn = sqlite3.connect("database.db")
#         cursor = conn.cursor()
#         cursor.execute("INSERT INTO users (phone_number, travel_mode) VALUES (?, ?) ON CONFLICT(phone_number) DO UPDATE SET travel_mode=1", (phone_number, 1))
#         conn.commit()
#         conn.close()

#         send_sms(phone_number, "🚨 Travel Mode ACTIVATED! Transactions will require extra security. Stay safe with SafiriGuard.")

#         return "CON Travel Mode Activated! You'll receive an SMS confirmation.\n0. Back"

# # Function to deactivate Travel Mode & send SMS
# def deactivate_travel_mode(phone_number):
#     if not check_travel_mode(phone_number):
#         return "CON Travel Mode is already OFF.\n0. Back"
#     else:
#         conn = sqlite3.connect("database.db")
#         cursor = conn.cursor()
#         cursor.execute("UPDATE users SET travel_mode=0 WHERE phone_number=?", (phone_number,))
#         conn.commit()
#         conn.close()

#         send_sms(phone_number, "🚨 Travel Mode DEACTIVATED. Normal transactions will resume. Stay safe!")

#         return "CON Travel Mode Deactivated! You'll receive an SMS confirmation.\n0. Back"

# # Function to send SMS
# def send_sms(phone_number, message):
#     try:
#         sms.send(message, [phone_number])
#     except Exception as e:
#         print(f"SMS sending failed: {e}")

# # Fraud detection function
# def detect_fraud(phone_number, transaction_amount):
#     conn = sqlite3.connect("database.db")
#     cursor = conn.cursor()

#     # Check if recent SIM swap exists
#     cursor.execute("SELECT COUNT(*) FROM sim_swaps WHERE phone_number = ? AND timestamp >= datetime('now', '-1 day')", (phone_number,))
#     recent_sim_swaps = cursor.fetchone()[0]

#     # Check if transaction amount is unusually high (e.g., over 50,000 KES)
#     high_value_transaction = int(transaction_amount) > 50000

#     if recent_sim_swaps > 0 or high_value_transaction:
#         # Store fraud alert in the database
#         alert_message = f"🚨 Fraud Alert: Suspicious transaction of KES {transaction_amount} detected!"
#         print(alert_message)
#         cursor.execute("INSERT INTO fraud_alerts (phone_number, alert) VALUES (?, ?)", (str(phone_number), alert_message))
#         conn.commit()

#         # Send SMS alert
#         sms.send(alert_message, [f"+254{phone_number}"])

#         print(f"Fraud alert triggered for {phone_number}")  

#     conn.close()

# # Simulate a transaction endpoint
# @app.route("/transaction", methods=["POST"])
# def transaction():
#     try:
#         phone_number = request.form.get("phoneNumber")
#         amount = request.form.get("amount")
        
#         print(f"Received transaction request: phone={phone_number}, amount={amount}")

#         detect_fraud(phone_number, amount)  # This function may be causing the issue

#         return jsonify({"status": "Transaction processed"})
    
#     except Exception as e:
#         print("Error processing transaction:", str(e))
#         return jsonify({"error": "Internal Server Error"}), 500


# # Function to get fraud alerts from the database
# def get_fraud_alerts(phone_number):
#     conn = sqlite3.connect("database.db")
#     cursor = conn.cursor()
#     cursor.execute("SELECT alert FROM fraud_alerts WHERE phone_number = ? ORDER BY timestamp DESC LIMIT 3", (phone_number,))
#     alerts = cursor.fetchall()
#     conn.close()

#     print("Fetched Alerts:", alerts) 

#     if alerts:
#         alert_messages = "\n".join([f"- {alert[0]}" for alert in alerts])
#         return f"CON Fraud Alerts:\n{alert_messages}\n0. Back"
    
    
#     else:
#         return "CON No fraud alerts found. Stay safe!\n0. Back"

# # Function to save fraud reports (Simulating fraud detection)
# def save_fraud_report(phone_number, report):
#     conn = sqlite3.connect("database.db")
#     cursor = conn.cursor()
#     cursor.execute("INSERT INTO fraud_alerts (phone_number, alert) VALUES (?, ?)", (phone_number, report))
#     conn.commit()
#     conn.close()

#     send_sms(phone_number, f"🚨 Fraud Report Received! '{report}' has been logged for investigation.")

# if __name__ == '__main__':
#     app.run(port=5000)
