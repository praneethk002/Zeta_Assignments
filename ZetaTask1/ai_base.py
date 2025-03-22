import os
from flask import Flask, jsonify, request
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Fetch the API key from the environment variable
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise Exception("GOOGLE_API_KEY environment variable not set")

# Configure the Gemini API
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash-8b')

# Dummy customer history (for demonstration purposes)
customer_history = {
    "customer_1": {"disputes": 2, "high_risk": 1},
    "customer_2": {"disputes": 5, "high_risk": 3},
}

@app.route('/classify', methods=['POST'])
def classify():
    try:
        req_body = request.get_json()
        content = req_body.get("dispute_text")
        customer_id = req_body.get("customer_id")
        amount = req_body.get("amount")

        if not content or not customer_id:
            return jsonify({"error": "Missing 'dispute_text' or 'customer_id' in the request body"}), 400

        # Use Gemini API to classify the dispute
        prompt = f"""
        Dispute Description: {content}
        Customer's Past Disputes: {customer_history.get(customer_id, {'disputes': 0})['disputes']} past disputes
        Disputed Amount: {amount}
        Classify the dispute and provide:
        1. The dispute type (e.g., Fraud, Duplicate Charge).
        2. The risk level (e.g., High, Medium, Low).
        3. A short recommended action (e.g., "Review for Fraud", "Issue Refund", "Block Account").
        Please format the response as:
        - Dispute Type: <type>
        - Risk Level: <level>
        - Recommended Action: <action>
        Avoid additional explanation or text.
        """
        
        response = model.generate_content(prompt)

        # Check if the response contains the expected lines
        lines = response.text.strip().split("\n")

        if len(lines) >= 3:
            dispute_type = lines[0].split(":")[1].strip()
            risk_level = lines[1].split(":")[1].strip()
            recommended_action = lines[2].split(":")[1].strip()
        else:
            # Handle the case where the response is not as expected
            dispute_type = "Unknown"
            risk_level = "Low"
            recommended_action = "Review the dispute"

        priority = assign_priority(customer_id, dispute_type)

        result = {
            "dispute_type": dispute_type,
            "disputed_amount": amount,
            "risk_level": risk_level,
            "recommended_action": recommended_action
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def assign_priority(customer_id, classification):
    # Fetch customer history (dummy data for now)
    history = customer_history.get(customer_id, {"disputes": 0, "high_risk": 0})

    # Assign priority based on classification and history
    if classification == "Fraud":
        return "High"
    elif classification == "Duplicate Charge" and history["high_risk"] > 2:
        return "High"
    elif history["disputes"] > 3:
        return "Medium"
    else:
        return "Low"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
