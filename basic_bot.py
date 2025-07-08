import logging
import time
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException

logging.basicConfig(level=logging.INFO)

class BasicBot:
    def __init__(self, api_key, api_secret, testnet=True):
        self.client = Client(api_key, api_secret, testnet=testnet)

        if testnet:
            self.client.FUTURES_URL = 'https://testnet.binancefuture.com/fapi'
            self.client.API_URL = self.client.FUTURES_URL

        try:
            server_time = self.client.get_server_time()['serverTime']
            local_time = int(time.time() * 1000)
            self.client.timestamp_offset = server_time - local_time
            logging.info("Time synced: offset = %d ms", self.client.timestamp_offset)
            
        except Exception as e:
            logging.error("Failed to sync time: %s", e)

        logging.info("Bot initialized with testnet = %s", testnet)

    def place_order(self, symbol, side, order_type, quantity, price=None):
        try:
            order_params = {
                'symbol': symbol,
                'side': SIDE_BUY if side.upper() == 'BUY' else SIDE_SELL,
                'type': order_type,
                'quantity': quantity
            }

            if order_type == ORDER_TYPE_LIMIT:
                if not price:
                    raise ValueError("Price required for limit order")
                order_params['price'] = price
                order_params['timeInForce'] = TIME_IN_FORCE_GTC

            order = self.client.futures_create_order(**order_params)
            logging.info("Order placed: %s", order)
            print("✅ Order placed successfully!")
            print("Order ID:", order['orderId'])
            print("Status:", order['status'])
            return order

        except BinanceAPIException as e:
            logging.error("API error: %s", e.message)
            print("❌ API Error:", e.message)

        except Exception as e:
            logging.error("Unexpected error: %s", str(e))
            print("❌ Unexpected Error:", str(e))

def main():
    print("=== Binance Futures Trading Bot ===")
    api_key = input("Enter your Binance API Key: ").strip()
    api_secret = input("Enter your Binance API Secret: ").strip()

    bot = BasicBot(api_key, api_secret)

    symbol = input("Enter symbol (e.g. BTCUSDT): ").upper()
    side = input("Buy or Sell [BUY/SELL]: ").upper()
    order_type = input("Order type [MARKET/LIMIT]: ").upper()
    quantity = float(input("Enter quantity: "))

    price = None
    if order_type == "LIMIT":
        price = float(input("Enter price: "))

    bot.place_order(symbol, side, order_type, quantity, price)

if __name__ == "__main__":
    main()