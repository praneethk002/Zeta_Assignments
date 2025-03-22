import os
from flask import Flask, jsonify, request
from time import time

# Define the RateLimiter class
class RateLimiter:
    def __init__(self, max_requests, window):
        self.max_requests = max_requests  # max allowed requests
        self.window = window              # time window in seconds
        self.user_requests = {}

    def allow_request(self, user_id):
        current_time = int(time())  # current time in seconds
        if user_id not in self.user_requests:
            # If the user doesn't exist, initialize their request count and time window
            self.user_requests[user_id] = {'count': 1, 'window_start': current_time}
            return True
        else:
            record = self.user_requests[user_id]
            # If the window time has passed, reset count and start a new window
            if current_time - record['window_start'] >= self.window:
                record['count'] = 1
                record['window_start'] = current_time
                return True
            # If the user hasn't exceeded the limit, allow the request
            elif record['count'] < self.max_requests:
                record['count'] += 1
                return True
            else:
                # If the user has exceeded the max requests, deny the request
                return False

# Flask setup
app = Flask(__name__)

# Set up the RateLimiter with max 5 requests per second
limiter = RateLimiter(max_requests=5, window=1)

@app.route('/transaction', methods=['POST'])
def transaction():
    user_id = request.json.get('user_id')  # Get user_id from the request

    if not user_id:
        return jsonify({"error": "Missing 'user_id' in the request body"}), 400
    
    # Check if the request is allowed
    if limiter.allow_request(user_id):
        return jsonify({"message": "Transaction processed successfully"}), 200
    else:
        return jsonify({"error": "Rate limit exceeded"}), 429

if __name__ == '__main__':
    app.run(debug=True, port = 6000)
