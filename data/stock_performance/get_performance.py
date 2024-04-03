import pandas as pd
import matplotlib.pyplot as plt

def analyze_stock_performance(open_price, close_price, high_price, low_price):
    if close_price > open_price:
        return "increased"
    elif close_price < open_price:
        return "decreased"
    else:
        if high_price > open_price or high_price > close_price:
            return "increased"
        elif low_price < open_price or low_price < close_price:
            return "decreased"
        else:
            return "neutral"

def plot_price_for_day(open_price, close_price, high_price, low_price):
    plt.plot([1, 2, 3, 4], [open_price, low_price, high_price, close_price], marker='o', linestyle='-')
    plt.xticks([1, 2, 3, 4], ['Open', 'Low', 'High', 'Close'])
    plt.title('Stock Prices For A Day')
    plt.xlabel('Price Type')
    plt.ylabel('Price')
    plt.grid(True)
    plt.show()
if __name__ == '__main__':
    #### ADD PERFORMANCE LABEL TO STOCK DATA ####
    # stock_data = pd.read_csv('test_stock_data.csv')
    # stock_data['Performance'] = stock_data.apply(lambda row: analyze_stock_performance(row['Open'], row['Close'], row['High'], row['Low']), axis=1)
    # stock_data.to_csv('stockdata_with_performance.csv', index=False)
    # print("Stock performance analysis completed and saved to 'stockdata_with_performance.csv'.")

    #### VISUALIZE ####
    open_price, close_price, high_price, low_price = 45.32,43.78,46.11,42.98    # values from test_stock_data.csv or stockdata_with_performance.csv
    plot_price_for_day(open_price, close_price, high_price, low_price)
