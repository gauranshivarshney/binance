import streamlit as st
import logging
from binance.client import Client
from binance.enums import SIDE_BUY, SIDE_SELL, ORDER_TYPE_MARKET, ORDER_TYPE_LIMIT, TIME_IN_FORCE_GTC
from binance.exceptions import BinanceAPIException

ORDER_TYPE_STOP_MARKET = 'STOP_MARKET'
ORDER_TYPE_OCO = 'OCO'
ORDER_TYPE_STOP_LOSS_LIMIT = 'STOP_LOSS_LIMIT'

logging.basicConfig(level=logging.INFO)

class BasicBot:
    def __init__(self, api_key, api_secret, testnet=True):
        self.client = Client(api_key, api_secret)
        
        if testnet:
            self.client.FUTURES_URL = 'https://testnet.binancefuture.com/fapi'
            self.client.API_URL = self.client.FUTURES_URL
            self.client.FUTURES_ACCOUNT = 'https://testnet.binancefuture.com/fapi/v2/account'
            self.client.FUTURES_ACCOUNT_BALANCE = 'https://testnet.binancefuture.com/fapi/v2/balance'

        try:
            server_time = self.client.get_server_time()['serverTime']
            local_time = int(time.time() * 1000)
            self.client.timestamp_offset = server_time - local_time
            logging.info("Time synced: offset = %d ms", self.client.timestamp_offset)
        except Exception as e:
            logging.error("Failed to sync time: %s", e)

        logging.info("Bot initialized with testnet = %s", testnet)

    def place_order(self, symbol, side, order_type, quantity, price=None, stop_price=None):
        try:
            order_params = {
                'symbol': symbol,
                'side': SIDE_BUY if side == 'BUY' else SIDE_SELL,
                'type': order_type,
                'quantity': quantity
            }

            if order_type == ORDER_TYPE_LIMIT:
                order_params['price'] = price
                order_params['timeInForce'] = TIME_IN_FORCE_GTC

            if order_type == ORDER_TYPE_STOP_MARKET:
                order_params['stopPrice'] = stop_price
                order_params['timeInForce'] = TIME_IN_FORCE_GTC

            order = self.client.futures_create_order(**order_params)
            logging.info("Order placed: %s", order)
            return {"status": "success", "order": order}

        except BinanceAPIException as e:
            logging.error("API error: %s", e.message)
            return {"status": "error", "message": e.message}
        
        except Exception as e:
            logging.error("Unexpected error: %s", str(e))
            return {"status": "error", "message": str(e)}

def main():
    st.set_page_config(page_title="Binance Futures Bot", page_icon="⚙️")
    st.title("📊 Binance Futures Trading Bot")

    with st.sidebar:
        st.header("🔐 API Credentials")
        api_key = st.text_input("API Key", type="password")
        api_secret = st.text_input("API Secret", type="password")
        testnet = st.checkbox("Use Testnet (Recommended)", value=True)

    if api_key and api_secret:
        bot = BasicBot(api_key, api_secret, testnet)

        st.subheader("📈 Order Settings")
        symbol = st.text_input("Trading Pair (e.g. BTCUSDT)", value="BTCUSDT").upper()
        side = st.selectbox("Side", ["BUY", "SELL"])
        order_type = st.selectbox("Order Type", ["MARKET", "LIMIT", "STOP_MARKET"])
        quantity = st.number_input("Quantity", min_value=0.001, step=0.001)

        price = None
        stop_price = None

        if order_type == "LIMIT":
            price = st.number_input("Limit Price", min_value=0.0)
        if order_type == "STOP_MARKET":
            stop_price = st.number_input("Stop Price", min_value=0.0)

        if st.button("📤 Place Order"):
            with st.spinner("Placing order..."):
                result = bot.place_order(symbol, side, order_type, quantity, price, stop_price)
                if result["status"] == "success":
                    st.success("✅ Order Placed Successfully!")
                    st.json(result["order"])
                else:
                    st.error(f"❌ {result['message']}")
    else:
        st.warning("Enter your API credentials to start trading.")

if __name__ == "__main__":
    main()