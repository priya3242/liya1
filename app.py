from flask import Flask, request, jsonify, render_template
import quickfix as fix
import quickfix44 as fix44
import random
import threading

app = Flask(__name__)

class Client(fix.Application):
    def __init__(self):
        super().__init__()
        self.session_id = None
        self.order_statuses = {}  # Dictionary to store order statuses

    def onCreate(self, session_id):
        self.session_id = session_id
        print(f"Session created - {session_id}")

    def onLogon(self, session_id):
        print(f"Logon successful for session {session_id}")

    def onLogout(self, session_id):
        print(f"Logout - {session_id}")

    def toAdmin(self, message, session_id):
        pass

    def fromAdmin(self, message, session_id):
        pass

    def toApp(self, message, session_id):
        print(f"Sending message: {message}")

    def fromApp(self, message, session_id):
        print(f"Received message: {message}")
        
        # Handle the response messages for status updates
        if message.getHeader().getField(fix.MsgType()) == fix.MsgType_ORDER_EXECUTION_REPORT:
            cl_ord_id = message.getField(fix.ClOrdID())
            status = message.getField(fix.OrdStatus())
            self.order_statuses[cl_ord_id] = status
            print(f"Order execution report received: {cl_ord_id} - Status={status}")

    def _place_order(self, side, symbol, quantity):
        if self.session_id is None:
            print("Cannot place order: session not established.")
            return None
        
        # Create New Order Single message
        order = fix44.NewOrderSingle()
        order_id = gen_order_id()
        order.setField(fix.ClOrdID(order_id))
        order.setField(fix.Symbol(symbol))
        order.setField(fix.Side(side))  # 1 for Buy, 2 for Sell
        order.setField(fix.OrderQty(quantity))
        order.setField(fix.OrdType(fix.OrdType_MARKET))
        order.setField(fix.TransactTime())

        # Send the message to the server
        fix.Session.sendToTarget(order, self.session_id)
        print(f"Order sent: Side={side}, Symbol={symbol}, Quantity={quantity}")
        return order_id  # Return the order ID

    def place_order(self, side, symbol, quantity):
        if side == 'buy':
            return self._place_order(fix.Side_BUY, symbol, quantity)
        elif side == 'sell':
            return self._place_order(fix.Side_SELL, symbol, quantity)
        else:
            print("Invalid order side. Must be 'buy' or 'sell'.")
            return None

    def get_order_status(self, cl_ord_id):
        return self.order_statuses.get(cl_ord_id, "Order status not found")

def gen_order_id():
    return str(random.randint(100000, 999999))

client = Client()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/order', methods=['POST'])
def place_order():
    data = request.json
    side = data.get('side')
    symbol = data.get('symbol')
    quantity = data.get('quantity')

    if side not in ['buy', 'sell']:
        return jsonify({'error': 'Invalid order side. Must be "buy" or "sell".'}), 400
    if not symbol or not isinstance(quantity, int) or quantity <= 0:
        return jsonify({'error': 'Invalid symbol or quantity.'}), 400

    order_id = client.place_order(side, symbol, quantity)
    if order_id:
        return jsonify({'status': 'Order placed successfully.', 'order_id': order_id})
    else:
        return jsonify({'error': 'Failed to place order.'}), 500

@app.route('/order_status/<cl_ord_id>', methods=['GET'])
def check_order_status(cl_ord_id):
    status = client.get_order_status(cl_ord_id)
    return jsonify({"status": status})

def start_flask_app():
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    threading.Thread(target=start_flask_app).start()

    settings = fix.SessionSettings("Client.cfg")
    store_factory = fix.FileStoreFactory(settings)
    log_factory = fix.ScreenLogFactory(settings)
    initiator = fix.SocketInitiator(client, store_factory, settings, log_factory)
    initiator.start()
    print("FIX client started.")
