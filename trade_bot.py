import time
from pybit import HTTP  # Bybit için doğru kütüphane
from dotenv import load_dotenv
import os

# Çevresel değişkenleri yükle
load_dotenv()

# Bybit Testnet API anahtarlarını al
API_KEY = 'u2L28P2FAqa1pghQrv'
API_SECRET = 'Xj8jAP5Hy5t510SPcoaTSoH1YmPcntsivgGP'

# Bybit Testnet URL'si üzerinden bağlanma
client = bybit(test=True, api_key=API_KEY, api_secret=API_SECRET)  # Testnet kullanıyoruz

# İşlem yapılacak sembol
SYMBOL = 'BTCUSDT'

# Pozisyon büyüklüğü (örneğin 50 USDT'lik pozisyon için)
TRADE_QUANTITY_USDT = 50

# 10x kaldıraç ayarla
client.LinearPositions.LinearPositions_saveLeverage(symbol=SYMBOL, buy_leverage=10, sell_leverage=10)

# Kar ve zarar oranları
TAKE_PROFIT_PERCENTAGE = 0.20  # %20 kar
STOP_LOSS_PERCENTAGE = 0.10  # %10 zarar

# Yüksek ve düşük fiyatlar (Fibonacci hesaplaması için)
MAX_PRICE = 70079.99
MIN_PRICE = 48949.38

# Fibonacci seviyelerini hesapla
fib_23_6 = MAX_PRICE - 0.236 * (MAX_PRICE - MIN_PRICE)
fib_38_2 = MAX_PRICE - 0.382 * (MAX_PRICE - MIN_PRICE)
fib_50 = MAX_PRICE - 0.5 * (MAX_PRICE - MIN_PRICE)
fib_61_8 = MAX_PRICE - 0.618 * (MAX_PRICE - MIN_PRICE)

# 50 USDT değerinde BTC miktarını hesapla
def calculate_quantity():
    price = float(client.Market.Market_symbolInfo(symbol=SYMBOL)['result'][0]['last_price'])  # Güncel fiyatı al
    quantity = TRADE_QUANTITY_USDT / price
    return round(quantity, 3)

# Alım işlemi
def buy_order():
    quantity = calculate_quantity()
    try:
        order = client.LinearOrder.LinearOrder_new(
            symbol=SYMBOL,
            side="Buy",
            order_type="Market",
            qty=quantity,
            time_in_force="GoodTillCancel"
        )
        print(f"Alım emri başarıyla oluşturuldu: {order}")
        return order
    except Exception as e:
        print(f"Alım emri başarısız: {e}")
        return None

# Satım işlemi
def sell_order():
    quantity = calculate_quantity()
    try:
        order = client.LinearOrder.LinearOrder_new(
            symbol=SYMBOL,
            side="Sell",
            order_type="Market",
            qty=quantity,
            time_in_force="GoodTillCancel"
        )
        print(f"Satış emri başarıyla oluşturuldu: {order}")
        return order
    except Exception as e:
        print(f"Satış emri başarısız: {e}")
        return None

# Pozisyonu izleyip kar veya zarar durumunda kapatma
def monitor_position(buy_price):
    while True:
        # Güncel fiyatı al
        price = float(client.Market.Market_symbolInfo(symbol=SYMBOL)['result'][0]['last_price'])
        print(f"Güncel fiyat: {price}")

        # Hedef kâr ve stop-loss fiyatlarını hesapla
        take_profit_price = buy_price * (1 + TAKE_PROFIT_PERCENTAGE)
        stop_loss_price = buy_price * (1 - STOP_LOSS_PERCENTAGE)

        print(f"Hedef kâr fiyatı: {take_profit_price}, Stop-loss fiyatı: {stop_loss_price}")

        # Kârda mıyız?
        if price >= take_profit_price:
            print(f"%20 kâr elde edildi. Pozisyon kapatılıyor...")
            sell_order()
            break
        # Zararda mıyız?
        elif price <= stop_loss_price:
            print(f"%10 zarara ulaşıldı. Pozisyon kapatılıyor...")
            sell_order()
            break

        time.sleep(1)

# Fibonacci seviyelerine göre işlem açma
def trade_on_fibonacci_levels():
    while True:
        # Güncel fiyatı al
        price = float(client.Market.Market_symbolInfo(symbol=SYMBOL)['result'][0]['last_price'])
        print(f"Güncel fiyat: {price}")

        # Fiyat Fibonacci seviyelerine gelirse alım/satım yap
        if price <= fib_61_8:  # Destek seviyesi, alım işlemi
            print("Fiyat 61.8% Fibonacci seviyesine ulaştı. Alım yapılıyor...")
            buy_order()
            monitor_position(price)
            break
        elif price >= fib_23_6:  # Direnç seviyesi, satış işlemi
            print("Fiyat 23.6% Fibonacci seviyesine ulaştı. Satış yapılıyor...")
            sell_order()
            monitor_position(price)
            break

        # Her döngüden sonra biraz bekle (örneğin 1 saniye)
        time.sleep(1)

# Ana işlem fonksiyonu
if __name__ == "__main__":
    trade_on_fibonacci_levels()
