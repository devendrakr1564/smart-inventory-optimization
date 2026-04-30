import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

# Page config
st.set_page_config(layout="wide")

# -----------------------------
# Load dataset
# -----------------------------
df = pd.read_csv("inventory_data_multi_product_updated.csv")
df['date'] = pd.to_datetime(df['date'], dayfirst=True)

data_A = df[df['product_id'] == 'A'].copy()

# -----------------------------

# -----------------------------
D_default = 79438.021   # Demand per year
S_default = 50          # Ordering cost
unit_cost_default = 350 # Purchasing cost

# -----------------------------
# CREATE COLUMNS
# -----------------------------
col1, col2 = st.columns([1, 2])

# =============================
# LEFT PANEL
# =============================
with col1:
    st.markdown("## EOQ")

    D = st.number_input("Demand per year:", value=D_default)
    S = st.number_input("Fixed order cost:", value=S_default)

    holding_percent = st.number_input("Annual inventory holding cost (%):", value=2)
    unit_cost = st.number_input("Purchasing cost:", value=unit_cost_default)

    robustness = st.slider("Robustness of EOQ model", 0.1, 5.0, 1.0)

    # Holding cost
    H = (holding_percent / 100) * unit_cost

# =============================
# CALCULATIONS
# =============================
EOQ = math.sqrt((2 * D * S) / H)

lead_time = data_A['lead_time'].iloc[0]
std_dev = np.std(data_A['demand'])
Z = 1.65

safety_stock = Z * std_dev * (lead_time ** 0.5)
daily_demand = D / 365
ROP = (daily_demand * lead_time) + safety_stock

current_Q = EOQ * robustness

# Costs
ordering_cost_EOQ = (D / EOQ) * S
holding_cost_EOQ = (EOQ / 2) * H
total_cost_EOQ = ordering_cost_EOQ + holding_cost_EOQ

ordering_cost_current = (D / current_Q) * S
holding_cost_current = (current_Q / 2) * H
total_cost_current = ordering_cost_current + holding_cost_current

# =============================
# RIGHT PANEL
# =============================
with col2:
    st.markdown("## Functions of the order quantity")

    Q = np.linspace(EOQ * 0.1, EOQ * 2, 200)

    ordering_cost_curve = (D / Q) * S
    holding_cost_curve = (Q / 2) * H
    total_cost = ordering_cost_curve + holding_cost_curve

    fig, ax = plt.subplots(figsize=(6, 4))

    ax.plot(Q, total_cost, label="Total cost")
    ax.plot(Q, ordering_cost_curve, linestyle='--', label="Fixed order cost")
    ax.plot(Q, holding_cost_curve, linestyle='--', label="Inventory-holding cost")

    # EOQ line
    ax.axvline(EOQ, linestyle='--')
    ax.text(EOQ, max(total_cost) * 0.6, "EOQ", ha='center')

    # Current Q point
    ax.scatter(current_Q, total_cost_current)
    ax.text(current_Q, total_cost_current, "real Q")

    ax.set_xlabel("Quantity")
    ax.set_ylabel("Cost")
    ax.legend()

    plt.tight_layout()

    st.pyplot(fig, use_container_width=False)

    # =============================
    # RESULTS
    # =============================
    st.write(f"Optimal quantity: {round(EOQ,2)}")
    st.write(f"Reorder interval: {round(EOQ / daily_demand,2)} days")
    st.write(f"Total costs: {round(total_cost_EOQ,2)}")
    st.write(f"Current costs: {round(total_cost_current,2)}")

    ratio_q = (current_Q / EOQ) * 100
    ratio_cost = (total_cost_current / total_cost_EOQ) * 100

    st.write(f"If ratio of quantity: {round(ratio_q,1)}% then ratio of costs: {round(ratio_cost,1)}%")
