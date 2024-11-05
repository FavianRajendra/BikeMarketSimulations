import random
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import openpyxl
import names
import time
from tqdm import tqdm

# Generate a large number of unique shop and buyer names
def generate_unique_names(count):
    name_set = set()
    while len(name_set) < count:
        name_set.add(names.get_full_name())
    return list(name_set)

# Constants
NUM_SHOPS = 1000
NUM_BUYERS = 5000
BIKE_TYPES = ["Mountain Bike", "Road Bike", "Hybrid Bike", "City Bike", "BMX", "Electric Bike"]

class Shop:
    def __init__(self, name):
        self.name = name
        self.inventory = {}

    def add_bike(self, bike_type, price, stock):
        self.inventory[bike_type] = {'price': price, 'stock': stock}

    def negotiate(self, bike_type, buyer_offer):
        if bike_type in self.inventory and self.inventory[bike_type]['stock'] > 0:
            price = self.inventory[bike_type]['price']
            if buyer_offer >= price * 0.9:
                return price, True
            else:
                counter_offer = max(price * 0.95, buyer_offer + 10)
                return counter_offer, False
        return None, False

    def sell_bike(self, bike_type):
        if bike_type in self.inventory and self.inventory[bike_type]['stock'] > 0:
            self.inventory[bike_type]['stock'] -= 1
            return True
        return False

class Buyer:
    def __init__(self, name, budget, desired_bikes):
        self.name = name
        self.budget = budget
        self.desired_bikes = desired_bikes

    def make_offer(self, price):
        return min(price * 0.9, self.budget)

def negotiate_with_shops(buyer, shops):
    transactions = []
    negotiation_history = []
    for bike_type in buyer.desired_bikes:
        for shop in random.sample(shops, min(10, len(shops))):  # Negotiate with up to 10 random shops
            if bike_type in shop.inventory and shop.inventory[bike_type]['stock'] > 0:
                shop_price = shop.inventory[bike_type]['price']
                buyer_offer = buyer.make_offer(shop_price)
                final_price, accepted = shop.negotiate(bike_type, buyer_offer)
                
                negotiation_history.append({
                    "Buyer": buyer.name,
                    "Shop": shop.name,
                    "Bike Type": bike_type,
                    "Buyer Offer": buyer_offer,
                    "Shop Price": final_price,
                    "Accepted": accepted
                })

                if accepted and shop.sell_bike(bike_type):
                    transactions.append({
                        "Buyer": buyer.name,
                        "Shop": shop.name,
                        "Bike Type": bike_type,
                        "Price": final_price
                    })
                    break  # Buyer got the bike, move to next desired bike

    return transactions, negotiation_history

def simulate_market(shops, buyers):
    all_transactions = []
    all_negotiation_history = []
    with ThreadPoolExecutor(max_workers=50) as executor:
        future_to_buyer = {executor.submit(negotiate_with_shops, buyer, shops): buyer for buyer in buyers}
        for future in tqdm(as_completed(future_to_buyer), total=len(buyers), desc="Processing buyers"):
            transactions, negotiation_history = future.result()
            all_transactions.extend(transactions)
            all_negotiation_history.extend(negotiation_history)
    return all_transactions, all_negotiation_history

# Generate unique names for shops and buyers
shop_names = generate_unique_names(NUM_SHOPS)
buyer_names = generate_unique_names(NUM_BUYERS)

# Create shops
shops = [Shop(name) for name in shop_names]

# Add bikes to shops
for shop in shops:
    for bike_type in BIKE_TYPES:
        if random.random() < 0.7:  # 70% chance of having each bike type
            shop.add_bike(bike_type, random.randint(200, 2000), random.randint(1, 10))

# Create buyers
buyers = [Buyer(name, random.randint(200, 2500), random.sample(BIKE_TYPES, random.randint(1, 3))) for name in buyer_names]

# Simulate the market
print("Starting market simulation...")
start_time = time.time()
transactions, negotiation_history = simulate_market(shops, buyers)
end_time = time.time()

print(f"Simulation completed in {end_time - start_time:.2f} seconds")

# Create DataFrames
transactions_df = pd.DataFrame(transactions)
negotiation_history_df = pd.DataFrame(negotiation_history)

# Replace the existing Excel saving code with this:
try:
    with pd.ExcelWriter('large_scale_negotiation_results.xlsx', engine='openpyxl') as writer:
        # Save main data
        transactions_df.to_excel(writer, sheet_name='Transactions', index=False)
        negotiation_history_df.to_excel(writer, sheet_name='Negotiation History', index=False)
        
        # Create summary statistics DataFrames
        bike_type_summary = transactions_df['Bike Type'].value_counts().reset_index()
        bike_type_summary.columns = ['Bike Type', 'Number of Sales']
        
        price_summary = pd.DataFrame({
            'Metric': ['Average Transaction Price', 'Minimum Price', 'Maximum Price'],
            'Value': [
                transactions_df['Price'].mean(),
                transactions_df['Price'].min(),
                transactions_df['Price'].max()
            ]
        })
        
        general_stats = pd.DataFrame({
            'Metric': [
                'Total Transactions',
                'Total Negotiations',
                'Acceptance Rate (%)'
            ],
            'Value': [
                len(transactions_df),
                len(negotiation_history_df),
                negotiation_history_df['Accepted'].mean() * 100
            ]
        })
        
        # Save summary statistics to separate sheets
        bike_type_summary.to_excel(writer, sheet_name='Bike Sales Summary', index=False)
        price_summary.to_excel(writer, sheet_name='Price Statistics', index=False)
        general_stats.to_excel(writer, sheet_name='General Statistics', index=False)
        
    print("Results saved to 'large_scale_negotiation_results.xlsx'")
except Exception as e:
    print(f"Error saving to Excel: {e}")
    # Fallback to CSV if Excel saving fails
    transactions_df.to_csv('large_scale_transactions.csv', index=False)
    negotiation_history_df.to_csv('large_scale_negotiation_history.csv', index=False)
    print("Results saved to CSV files due to Excel saving error")

# Display summary statistics (keep this part as is)
print("\n--- Summary Statistics ---")
print(f"Total Transactions: {len(transactions_df)}")
print(f"Total Negotiations: {len(negotiation_history_df)}")
print("\nTop 5 Most Sold Bike Types:")
print(transactions_df['Bike Type'].value_counts().head())
print("\nAverage Transaction Price: ${:.2f}".format(transactions_df['Price'].mean()))
print("Acceptance Rate: {:.2f}%".format(negotiation_history_df['Accepted'].mean() * 100))