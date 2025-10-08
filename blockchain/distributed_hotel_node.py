from flask import Flask, render_template_string, request, redirect
import hashlib
import json
import time
import webbrowser
import os

app = Flask(__name__)

# --------------------
# Blockchain Classes
# --------------------
class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'data': self.data,
            'previous_hash': self.previous_hash
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []

    def create_genesis_block(self):
        return Block(0, time.time(), "Genesis Block", "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_transaction(self, transaction):
        self.pending_transactions.append(transaction)

    def mine_block(self):
        if not self.pending_transactions:
            return None
        new_block = Block(
            len(self.chain),
            time.time(),
            self.pending_transactions,
            self.get_latest_block().hash
        )
        self.chain.append(new_block)
        self.pending_transactions = []
        return new_block

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            if current.hash != current.calculate_hash():
                return False
            if current.previous_hash != previous.hash:
                return False
        return True


# --------------------
# Initialize Blockchain
# --------------------
blockchain = Blockchain()

# --------------------
# HTML Template
# --------------------
HTML_TEMPLATE = """  
<!DOCTYPE html>
<html>
<head>
    <title>Hotel Booking Blockchain</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f0f4f8; margin: 0; padding: 20px; }
        h1 { color: #1a73e8; text-align: center; margin-bottom: 20px; }
        .dashboard { display: flex; justify-content: space-around; margin-bottom: 30px; flex-wrap: wrap; }
        .card { background: #ffffff; padding: 20px 25px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center; width: 180px; margin: 10px; }
        .card h2 { color: #1a73e8; margin: 0 0 10px 0; }
        .form-container, .mine-container { background: #ffffff; padding: 25px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); max-width: 500px; margin: 20px auto; }
        label { display: block; margin-top: 15px; font-weight: bold; }
        input { width: 100%; padding: 10px; margin-top: 5px; border-radius: 5px; border: 1px solid #ccc; box-sizing: border-box; }
        button { margin-top: 20px; padding: 12px 25px; background-color: #1a73e8; color: white; font-size: 16px; border: none; border-radius: 6px; cursor: pointer; transition: background 0.3s ease; }
        button:hover { background-color: #155ab6; }
        .status { text-align: center; margin-top: 15px; font-size: 18px; }
        .valid { color: green; font-weight: bold; }
        .invalid { color: red; font-weight: bold; }
        table { border-collapse: collapse; width: 100%; margin-top: 30px; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
        th, td { padding: 12px; text-align: left; }
        th { background-color: #1a73e8; color: white; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        ul { padding-left: 18px; margin: 0; }
    </style>
</head>
<body>
    <h1>Hotel Booking Blockchain</h1>

    <div class="dashboard">
        <div class="card">
            <h2>{{ blockchain|length }}</h2>
            <p>Total Blocks</p>
        </div>
        <div class="card">
            <h2>{{ total_bookings }}</h2>
            <p>Total Confirmed Bookings</p>
        </div>
        <div class="card">
            <h2>{{ pending_transactions|length }}</h2>
            <p>Pending Transactions</p>
        </div>
    </div>

    <div class="form-container">
        <form action="/add_transaction" method="post">
            <label>Customer Name:</label>
            <input type="text" name="customer_name" required>
            <label>Room Number:</label>
            <input type="text" name="room_number" required>
            <label>Check-in Date:</label>
            <input type="date" name="check_in" required>
            <label>Check-out Date:</label>
            <input type="date" name="check_out" required>
            <label>Amount (₹):</label>
            <input type="number" name="amount" required>
            <button type="submit">Add Booking</button>
        </form>
    </div>

    <div class="mine-container">
        <form action="/mine_block" method="post">
            <button type="submit">Mine Block</button>
        </form>
    </div>

    <div class="status">
        Blockchain Status:
        {% if is_valid %}
            <span class="valid">✅ Valid</span>
        {% else %}
            <span class="invalid">❌ Compromised</span>
        {% endif %}
    </div>

    <table>
        <tr>
            <th>Index</th>
            <th>Timestamp</th>
            <th>Transactions</th>
            <th>Hash</th>
            <th>Previous Hash</th>
        </tr>
        {% for block in blockchain %}
        <tr>
            <td>{{ block.index }}</td>
            <td>{{ format_time(block.timestamp) }}</td>
            <td>
                {% if block.index == 0 %}
                    Genesis Block
                {% else %}
                    <ul>
                    {% for tx in block.data %}
                        <li>{{ tx.customer_name }} | Room {{ tx.room_number }} | {{ tx.check_in }} → {{ tx.check_out }} | ₹{{ tx.amount }}</li>
                    {% endfor %}
                    </ul>
                {% endif %}
            </td>
            <td>{{ block.hash }}</td>
            <td>{{ block.previous_hash }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

# --------------------
# Flask Routes
# --------------------
@app.route('/')
def index():
    total_bookings = sum(len(block.data) for block in blockchain.chain if block.index != 0)
    return render_template_string(
        HTML_TEMPLATE,
        blockchain=blockchain.chain,
        pending_transactions=blockchain.pending_transactions,
        total_bookings=total_bookings,
        is_valid=blockchain.is_chain_valid(),
        format_time=lambda ts: time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))
    )

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    transaction = {
        "customer_name": request.form.get('customer_name'),
        "room_number": request.form.get('room_number'),
        "check_in": request.form.get('check_in'),
        "check_out": request.form.get('check_out'),
        "amount": request.form.get('amount')
    }
    blockchain.add_transaction(transaction)
    return redirect('/')

@app.route('/mine_block', methods=['POST'])
def mine_block():
    blockchain.mine_block()
    return redirect('/')

# --------------------
# Run the App
# --------------------
def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

