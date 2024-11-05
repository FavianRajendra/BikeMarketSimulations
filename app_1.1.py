import streamlit as st
import random
import pandas as pd
import time
import matplotlib.pyplot as plt
from negotiate import Shop, Buyer, negotiate_with_shops, simulate_market, generate_unique_names

# Add custom CSS for animations and styling
st.set_page_config(
    page_title="🚲 Bike Market Simulator",
    page_icon="🚲",
    layout="wide"
)

# Custom CSS for animations and styling
st.markdown("""
    <style>
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        .fade-in {
            animation: fadeIn 1s ease-in;
        }
        .stButton>button {
            background-color: #ff4b4b;
            color: white;
            border-radius: 10px;
            padding: 0.5rem 1rem;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .download-button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            margin: 10px 0;
            transition: all 0.3s ease;
        }
        .download-button:hover {
            background-color: #45a049;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }
    </style>
""", unsafe_allow_html=True)

BIKE_TYPES = ["Mountain Bike 🏔️", "Road Bike 🛣️", "Hybrid Bike 🚲", "City Bike 🌆", "BMX 🎪", "Electric Bike ⚡"]

def run_simulation(num_shops, num_buyers):
    shop_names = generate_unique_names(num_shops)
    buyer_names = generate_unique_names(num_buyers)
    shops = [Shop(name) for name in shop_names]
    
    for shop in shops:
        for bike_type in BIKE_TYPES:
            if random.random() < 0.7:
                shop.add_bike(bike_type, random.randint(200, 2000), random.randint(1, 10))

    buyers = [Buyer(name, random.randint(200, 2500), random.sample(BIKE_TYPES, random.randint(1, 3))) 
             for name in buyer_names]

    return simulate_market(shops, buyers)

def main():
    # Title with animation
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.title("🚲 Bike Market Simulation Dashboard")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Initialize session state
    if 'transactions_df' not in st.session_state:
        st.session_state.transactions_df = None
    if 'negotiation_history_df' not in st.session_state:
        st.session_state.negotiation_history_df = None
    
    # Sidebar with better styling
    with st.sidebar:
        st.markdown("### 🎮 Simulation Controls")
        st.markdown("---")
        num_shops = st.slider("🏪 Number of Shops", 10, 1000, 100, 
                            help="Slide to adjust the number of shops in the simulation")
        num_buyers = st.slider("👥 Number of Buyers", 50, 5000, 500,
                             help="Slide to adjust the number of buyers in the simulation")
        
        st.markdown("---")
        if st.button("🚀 Launch Simulation", help="Click to start the simulation"):
            with st.spinner("🔄 Running simulation... Please wait"):
                start_time = time.time()
                transactions, negotiation_history = run_simulation(num_shops, num_buyers)
                end_time = time.time()

            st.success(f"✨ Simulation completed in {end_time - start_time:.2f} seconds!")
            
            # Update session state
            st.session_state.transactions_df = pd.DataFrame(transactions)
            st.session_state.negotiation_history_df = pd.DataFrame(negotiation_history)
            st.rerun()

    # Main content area
    st.markdown("### 📊 Summary Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        if st.session_state.transactions_df is not None:
            st.metric("🤝 Total Transactions", f"{len(st.session_state.transactions_df):,}")
        else:
            st.metric("🤝 Total Transactions", "Run simulation")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        if st.session_state.negotiation_history_df is not None:
            st.metric("💬 Total Negotiations", f"{len(st.session_state.negotiation_history_df):,}")
        else:
            st.metric("💬 Total Negotiations", "Run simulation")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        if st.session_state.negotiation_history_df is not None:
            st.metric("✅ Success Rate", 
                     f"{st.session_state.negotiation_history_df['Accepted'].mean()*100:.1f}%")
        else:
            st.metric("✅ Success Rate", "Run simulation")
        st.markdown('</div>', unsafe_allow_html=True)

    # Visualizations
    st.markdown("### 📈 Market Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔝 Top Selling Bikes")
        if st.session_state.transactions_df is not None:
            st.bar_chart(st.session_state.transactions_df['Bike Type'].value_counts().head())
        else:
            st.info("Run simulation to see top selling bikes")
    
    with col2:
        st.markdown("#### 💰 Price Distribution")
        if st.session_state.transactions_df is not None:
            fig, ax = plt.subplots()
            st.session_state.transactions_df['Price'].hist(bins=30, ax=ax)
            st.pyplot(fig)
        else:
            st.info("Run simulation to see price distribution")

    # Price statistics
    st.markdown("### 💵 Price Statistics")
    if st.session_state.transactions_df is not None:
        price_stats = pd.DataFrame({
            'Metric': ['💰 Average Price', '⬇️ Minimum Price', '⬆️ Maximum Price'],
            'Value': [
                f"${st.session_state.transactions_df['Price'].mean():,.2f}",
                f"${st.session_state.transactions_df['Price'].min():,.2f}",
                f"${st.session_state.transactions_df['Price'].max():,.2f}"
            ]
        })
        st.table(price_stats)
    else :
        st.info(" Run simulation to see price statistics")

    # Download section
    if st.session_state.transactions_df is not None:
        st.markdown("### 📥 Download Results")
        col1, col2 = st.columns(2)
        
        with col1:
            transactions_csv = st.session_state.transactions_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Transactions CSV",
                data=transactions_csv,
                file_name="transactions.csv",
                mime="text/csv",
                key="download_transactions"
            )
        
        with col2:
            negotiation_csv = st.session_state.negotiation_history_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Negotiation History CSV",
                data=negotiation_csv,
                file_name="negotiation_history.csv",
                mime="text/csv",
                key="download_negotiation"
            )

if __name__ == "__main__":
    main()