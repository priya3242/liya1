import quickfix as fix
import quickfix44 as fix44
import random
import csv
from datetime import datetime
import time

# Generate a unique order ID
def gen_order_id():
    return str(random.randint(100000, 999999))

class MarketMaker(fix.Application):
    def __init__(self):
        super().__init__()
        self.session_id = None
        try:
            self.csv_file = open('market_maker_messages.csv', 'w', newline='')
            self.csv_writer = csv.writer(self.csv_file)
            # Log FIX messages into the CSV file
            self.csv_writer.writerow(['Date', 'Time', 'MsgType', 'Symbol', 'Side', 'OrderQty', 'Price', 'OrderID', 'ExecType', 'OrdStatus'])
            print("Market Maker CSV file opened successfully.")
        except Exception as e:
            print(f"Failed to open Market Maker CSV file: {e}")
            sys.exit(1)

    # Callback when session is created
    def onCreate(self, session_id):
        self.session_id = session_id
        print(f"Session created - {session_id}")

    # Callback on successful logon
    def onLogon(self, session_id):
        print(f"Logon successful for session {session_id}")

    # Callback on logout
    def onLogout(self, session_id):
        print(f"Logout - {session_id}")

    # ToAdmin is called when sending admin messages
    def toAdmin(self, message, session_id):
        print(f"Market Maker To Admin: {message}")

    # FromAdmin is called when receiving admin messages
    def fromAdmin(self, message, session_id):
        print(f"Market Maker From Admin: {message}")

    # ToApp is called before sending an application message
    def toApp(self, message, session_id):
        print(f"Market Maker Sending message: {message}")

    # FromApp is called when receiving an application message
    def fromApp(self, message, session_id):
        print(f"Market Maker Received message: {message}")
        self.process_message(message)

    # Process received FIX messages
    def process_message(self, message):
        try:
            msg_type = self.get_field_value(message, fix.MsgType())
            symbol = self.get_field_value(message, fix.Symbol())
            side = self.get_field_value(message, fix.Side())
            order_qty = self.get_field_value(message, fix.OrderQty())
            price = self.get_field_value(message, fix.Price())
            cl_ord_id = self.get_field_value(message, fix.ClOrdID())

            now = datetime.now()
            date = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M:%S.%f")[:-3]

            self.csv_writer.writerow([date, time_str, msg_type, symbol, side, order_qty, price, cl_ord_id, '', ''])
            self.csv_file.flush()
            print("Message logged to Market Maker CSV.")

            if msg_type == fix.MsgType_NewOrderSingle:
                # Print order details
                print(f"Order Received: ClOrdID={cl_ord_id}, Symbol={symbol}, Side={side}, Quantity={order_qty}, Price={price}")

                # Respond with Execution Report (ExecType = 0 = New, OrdStatus = 0 = New)
                exec_report = fix44.ExecutionReport()
                exec_report.setField(fix.OrderID(gen_order_id()))
                exec_report.setField(fix.ClOrdID(cl_ord_id))
                exec_report.setField(fix.ExecID(gen_order_id()))
                exec_report.setField(fix.ExecType(fix.ExecType_NEW))
                exec_report.setField(fix.OrdStatus(fix.OrdStatus_NEW))
                exec_report.setField(fix.Symbol(symbol))
                exec_report.setField(fix.Side(side))
                exec_report.setField(fix.OrderQty(order_qty))
                exec_report.setField(fix.Price(price))
                exec_report.setField(fix.LastShares(order_qty))
                exec_report.setField(fix.LastPx(price))
                exec_report.setField(fix.TransactTime())

                fix.Session.sendToTarget(exec_report, self.session_id)
                print("Execution Report sent.")

        except Exception as e:
            print(f"Error processing message: {e}")

    # Helper method to extract field values from FIX messages
    def get_field_value(self, message, field):
        try:
            message.getField(field)
            return field.getString()
        except fix.FieldNotFound:
            return ''

    def close(self):
        try:
            self.csv_file.close()
            print("Market Maker CSV file closed.")
        except Exception as e:
            print(f"Error closing Market Maker CSV file: {e}")

def main():
    try:
        settings = fix.SessionSettings("Server.cfg")  # Ensure correct path
        application = MarketMaker()
        store_factory = fix.FileStoreFactory(settings)
        log_factory = fix.ScreenLogFactory(settings)
        acceptor = fix.SocketAcceptor(application, store_factory, settings, log_factory)

        # Start the FIX server
        acceptor.start()
        print("Market Maker has started... Press CTRL+C to quit.")

        # Keep the server running
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Shutting down Market Maker...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        application.close()
        acceptor.stop()
        print("Market Maker stopped.")

if __name__ == "__main__":
    main()
