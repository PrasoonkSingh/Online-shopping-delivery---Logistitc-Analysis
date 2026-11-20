# ==========================================================
# Project 23: Online Shopping Delivery & Logistics Analysis
# Tools: Python, Pandas, NumPy, Matplotlib
# Dataset: 23_delivery_performance.csv
# ==========================================================
# HOW TO RUN
#  - Jupyter: keep the CSV in the same folder as the notebook.
#  - Google Colab: run the cell; if the CSV is not found,
#    you will be asked to upload it.
# ==========================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

pd.set_option("display.width", 150)
pd.set_option("display.max_columns", 20)

CSV_PATH = "23_delivery_performance.csv"


def heading(text):
    """Print a clear section heading."""
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70)


# ----------------------------------------------------------
# TASK 1: Load the dataset and inspect shape, columns, dtypes
# ----------------------------------------------------------
heading("TASK 1: Load and inspect the dataset")

import os
if not os.path.exists(CSV_PATH):
    try:                                   # works only in Google Colab
        from google.colab import files
        print("CSV not found. Please upload 23_delivery_performance.csv")
        files.upload()
    except ImportError:
        raise FileNotFoundError(f"Put {CSV_PATH} in the same folder as this script.")

df = pd.read_csv(CSV_PATH)

print("Shape (rows, columns):", df.shape)
print("\nColumns:", list(df.columns))
print("\nData types:")
print(df.dtypes)
print("\nFirst 5 rows:")
print(df.head())

# ----------------------------------------------------------
# TASK 2: Missing values and duplicate Shipment_ID records
# ----------------------------------------------------------
heading("TASK 2: Missing values and duplicate Shipment_IDs")

print("Missing values per column:")
print(df.isnull().sum())

# Clean text columns first so ' sh1005 ' and 'SH1005' are treated as the same ID
for col in ["Shipment_ID", "Shipping_Method", "Delivery_Partner", "Order_Status"]:
    df[col] = df[col].astype(str).str.strip()
df["Shipment_ID"] = df["Shipment_ID"].str.upper()

dup_rows = df[df["Shipment_ID"].duplicated(keep=False)]
print("\nNumber of repeated Shipment_ID records:", df["Shipment_ID"].duplicated().sum())
print("Rows that share a Shipment_ID:")
print(dup_rows)

# Where is Delivery_Date missing? (useful for Task 3)
print("\nOrder_Status of rows with missing Delivery_Date:")
print(df[df["Delivery_Date"].isnull()]["Order_Status"].value_counts())

# Remove duplicates: keep the FIRST record of each Shipment_ID
rows_before = len(df)
df = df.drop_duplicates(subset="Shipment_ID", keep="first").reset_index(drop=True)
print(f"\nRows before: {rows_before} | Rows after removing duplicate IDs: {len(df)}")

# ----------------------------------------------------------
# TASK 4 (done before Task 3): Convert dates to datetime
# ----------------------------------------------------------
# errors="coerce" turns invalid / unreadable dates into NaT instead of crashing.
heading("TASK 4: Convert Order_Date and Delivery_Date to datetime")

df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")
df["Delivery_Date"] = pd.to_datetime(df["Delivery_Date"], errors="coerce")

print(df[["Order_Date", "Delivery_Date"]].dtypes)
print("Invalid/missing Order_Date :", df["Order_Date"].isnull().sum())
print("Missing Delivery_Date      :", df["Delivery_Date"].isnull().sum())

# Invalid-date check: delivery must not be before the order
bad = df[df["Delivery_Date"] < df["Order_Date"]]
print("Rows where Delivery_Date is before Order_Date:", len(bad))
df = df[~df.index.isin(bad.index)].copy()      # drop impossible records

# Rows without a valid Order_Date cannot be analysed
df = df.dropna(subset=["Order_Date"]).copy()

# ----------------------------------------------------------
# TASK 3: Handle missing Delivery_Date and Shipping_Cost
# ----------------------------------------------------------
heading("TASK 3: Handle missing Delivery_Date and Shipping_Cost")

# --- Delivery_Date ---
# Cancelled / In Transit orders have no delivery date because they have NOT
# been delivered yet. Filling these would create fake data, so we leave them empty.
# Only rows marked Delivered/Delayed but with NO date are a real data problem.
# For those we estimate: Order_Date + median delivery days of the same
# shipping method (median is not affected by extreme values).
df["Date_Estimated"] = False
real_days = (df["Delivery_Date"] - df["Order_Date"]).dt.days
median_days_by_method = real_days.groupby(df["Shipping_Method"]).median()
print("Median delivery days by method (used for estimates):")
print(median_days_by_method)

need_fix = df["Delivery_Date"].isnull() & df["Order_Status"].isin(["Delivered", "Delayed"])
print("\nDelivered/Delayed rows with missing Delivery_Date:", need_fix.sum())
for idx in df[need_fix].index:
    days = median_days_by_method[df.loc[idx, "Shipping_Method"]]
    df.loc[idx, "Delivery_Date"] = df.loc[idx, "Order_Date"] + pd.Timedelta(days=days)
    df.loc[idx, "Date_Estimated"] = True
print("Dates estimated and flagged in 'Date_Estimated':", df["Date_Estimated"].sum())
print("Delivery_Date left empty (not delivered yet / cancelled):",
      df["Delivery_Date"].isnull().sum())

# --- Shipping_Cost ---
# Fill with the MEDIAN cost of the same shipping method. Median is safer than
# mean when a few very high/low costs exist, and grouping by method keeps
# the estimate realistic.
print("\nMissing Shipping_Cost before:", df["Shipping_Cost"].isnull().sum())
df["Shipping_Cost"] = df["Shipping_Cost"].fillna(
    df.groupby("Shipping_Method")["Shipping_Cost"].transform("median"))
print("Missing Shipping_Cost after :", df["Shipping_Cost"].isnull().sum())

# ----------------------------------------------------------
# TASK 5: Delivery_Days = Delivery_Date - Order_Date
# ----------------------------------------------------------
heading("TASK 5: Calculate Delivery_Days")

df["Delivery_Days"] = (df["Delivery_Date"] - df["Order_Date"]).dt.days
print(df[["Shipment_ID", "Order_Date", "Delivery_Date", "Delivery_Days"]].head(8))
print("\nRows with a Delivery_Days value:", df["Delivery_Days"].notnull().sum())

# ----------------------------------------------------------
# TASK 6: Total, delivered shipments and success percentage
# ----------------------------------------------------------
heading("TASK 6: Overall delivery success")

# Success = Order_Status is exactly "Delivered".
# ("Delayed" shipments are not counted as successful.)
total_shipments = len(df)
delivered_shipments = (df["Order_Status"] == "Delivered").sum()
success_pct = delivered_shipments / total_shipments * 100

print("Total shipments    :", total_shipments)
print("Delivered shipments:", delivered_shipments)
print(f"Delivery success % : {success_pct:.2f}%")

# ----------------------------------------------------------
# TASK 7: Average delivery duration by shipping method
# ----------------------------------------------------------
heading("TASK 7: Average delivery days by shipping method")

avg_by_method = df.groupby("Shipping_Method")["Delivery_Days"].mean().round(2).sort_values()
print(avg_by_method)

plt.figure(figsize=(6, 4))
plt.bar(avg_by_method.index, avg_by_method.values, color="steelblue")
plt.title("Average Delivery Days by Shipping Method")
plt.xlabel("Shipping Method")
plt.ylabel("Average Delivery Days")
for i, v in enumerate(avg_by_method.values):
    plt.text(i, v + 0.05, f"{v:.2f}", ha="center")
plt.tight_layout()
plt.show()

# ----------------------------------------------------------
# TASK 8: Rank delivery partners
# ----------------------------------------------------------
heading("TASK 8: Rank delivery partners")

partner = df.groupby("Delivery_Partner").agg(
    Shipments=("Shipment_ID", "count"),
    Avg_Delivery_Days=("Delivery_Days", "mean")).round(2)

# Rank 1 = most shipments; Rank 1 = fastest (lowest) average days
partner["Volume_Rank"] = partner["Shipments"].rank(ascending=False, method="min").astype(int)
partner["Speed_Rank"] = partner["Avg_Delivery_Days"].rank(ascending=True, method="min").astype(int)
partner = partner.sort_values(["Volume_Rank", "Speed_Rank"])
print(partner)

fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ax[0].bar(partner.index, partner["Shipments"], color="seagreen")
ax[0].set_title("Shipments per Partner")
ax[0].set_ylabel("Number of Shipments")
ax[0].tick_params(axis="x", rotation=30)
ax[1].bar(partner.index, partner["Avg_Delivery_Days"], color="darkorange")
ax[1].set_title("Average Delivery Days per Partner")
ax[1].set_ylabel("Days")
ax[1].tick_params(axis="x", rotation=30)
plt.tight_layout()
plt.show()

# ----------------------------------------------------------
# TASK 9: Delivery success rate by shipping method
# ----------------------------------------------------------
heading("TASK 9: Success rate by shipping method")

method_stats = df.groupby("Shipping_Method").agg(
    Total=("Shipment_ID", "count"),
    Delivered=("Order_Status", lambda s: (s == "Delivered").sum()))
method_stats["Success_%"] = (method_stats["Delivered"] / method_stats["Total"] * 100).round(2)
print(method_stats.sort_values("Success_%", ascending=False))

plt.figure(figsize=(6, 4))
plt.bar(method_stats.index, method_stats["Success_%"], color="mediumpurple")
plt.title("Delivery Success Rate by Shipping Method")
plt.xlabel("Shipping Method")
plt.ylabel("Success Rate (%)")
plt.ylim(0, 100)
for i, v in enumerate(method_stats["Success_%"]):
    plt.text(i, v + 1, f"{v:.1f}%", ha="center")
plt.tight_layout()
plt.show()

# ----------------------------------------------------------
# TASK 10: 10 shipments with the longest delivery duration
# ----------------------------------------------------------
heading("TASK 10: Top 10 longest deliveries")

longest = df.dropna(subset=["Delivery_Days"]).sort_values(
    ["Delivery_Days", "Shipment_ID"], ascending=[False, True]).head(10)
print(longest[["Shipment_ID", "Delivery_Partner", "Shipping_Method",
               "Order_Status", "Delivery_Days"]].to_string(index=False))
print("\nNote: several shipments tie at the same number of days; ties are")
print("ordered by Shipment_ID, so a few tied shipments may fall outside the top 10.")

# ----------------------------------------------------------
# TASK 11: Dictionary of status counts and set of partners
# ----------------------------------------------------------
heading("TASK 11: Dictionary and set")

status_counts = {}                       # dictionary: status -> count
for status in df["Order_Status"]:
    status_counts[status] = status_counts.get(status, 0) + 1
print("Delivery counts by status (dictionary):")
print(status_counts)

unique_partners = set(df["Delivery_Partner"])    # set: only unique values
print("\nUnique delivery partners (set):", unique_partners)
print("Number of unique partners:", len(unique_partners))

plt.figure(figsize=(6, 4))
plt.bar(status_counts.keys(), status_counts.values(), color="indianred")
plt.title("Shipments by Order Status")
plt.ylabel("Number of Shipments")
plt.tight_layout()
plt.show()

# ----------------------------------------------------------
# TASK 12: Classification function
# ----------------------------------------------------------
heading("TASK 12: Classify shipments")

# Day limits (stated clearly):
#   On-Time          : 0 to 3 days
#   Slightly Delayed : 4 to 6 days
#   Highly Delayed   : 7 days or more
#   Not Delivered    : no delivery date (cancelled / in transit)
def classify_shipment(days):
    if pd.isnull(days):
        return "Not Delivered"
    elif days <= 3:
        return "On-Time"
    elif days <= 6:
        return "Slightly Delayed"
    else:
        return "Highly Delayed"

df["Delivery_Class"] = df["Delivery_Days"].apply(classify_shipment)
class_counts = df["Delivery_Class"].value_counts()
print(class_counts)
print("\nPercentage of delivered shipments in each class:")
delivered_only = df[df["Delivery_Class"] != "Not Delivered"]
print((delivered_only["Delivery_Class"].value_counts(normalize=True) * 100).round(2))

plt.figure(figsize=(6, 4))
plt.bar(class_counts.index, class_counts.values,
        color=["seagreen", "goldenrod", "indianred", "grey"][:len(class_counts)])
plt.title("Shipment Delivery Classification")
plt.ylabel("Number of Shipments")
plt.xticks(rotation=15)
plt.tight_layout()
plt.show()

# ----------------------------------------------------------
# TASK 13: NumPy statistics of Delivery_Days
# ----------------------------------------------------------
heading("TASK 13: NumPy statistics")

days_array = df["Delivery_Days"].dropna().to_numpy()
mean_days = np.mean(days_array)
median_days = np.median(days_array)
std_days = np.std(days_array)             # population std (NumPy default)
print(f"Mean delivery days  : {mean_days:.2f}")
print(f"Median delivery days: {median_days:.2f}")
print(f"Standard deviation  : {std_days:.2f}")

# ----------------------------------------------------------
# TASK 14: IQR outliers and monthly comparison
# ----------------------------------------------------------
heading("TASK 14: IQR outliers and monthly performance")

q1 = np.percentile(days_array, 25)
q3 = np.percentile(days_array, 75)
iqr = q3 - q1
lower_limit = q1 - 1.5 * iqr
upper_limit = q3 + 1.5 * iqr
print(f"Q1 = {q1}, Q3 = {q3}, IQR = {iqr}")
print(f"Normal range: {lower_limit} to {upper_limit} days")

outliers = df[(df["Delivery_Days"] < lower_limit) | (df["Delivery_Days"] > upper_limit)]
print("Number of unusually long/short deliveries:", len(outliers))
if len(outliers) > 0:
    print(outliers[["Shipment_ID", "Delivery_Partner", "Delivery_Days"]])
else:
    print("No outliers found: every delivery is inside the IQR range.")

plt.figure(figsize=(7, 4))
plt.hist(days_array, bins=range(0, int(days_array.max()) + 2),
         color="steelblue", edgecolor="black", align="left")
plt.axvline(upper_limit, color="red", linestyle="--", label=f"IQR upper limit = {upper_limit:.0f}")
plt.title("Distribution of Delivery Days")
plt.xlabel("Delivery Days")
plt.ylabel("Number of Shipments")
plt.legend()
plt.tight_layout()
plt.show()

# --- Monthly comparison (by Order_Date month) ---
df["Order_Month"] = df["Order_Date"].dt.month
monthly = df.groupby("Order_Month").agg(
    Shipments=("Shipment_ID", "count"),
    Avg_Delivery_Days=("Delivery_Days", "mean"),
    Delivered=("Order_Status", lambda s: (s == "Delivered").sum()))
monthly["Success_%"] = (monthly["Delivered"] / monthly["Shipments"] * 100).round(2)
monthly["Avg_Delivery_Days"] = monthly["Avg_Delivery_Days"].round(2)
month_names = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
               7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}
monthly.index = [month_names[m] for m in monthly.index]
print("\nMonthly performance:")
print(monthly)

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
ax[0].bar(monthly.index, monthly["Avg_Delivery_Days"], color="teal")
ax[0].set_title("Average Delivery Days by Month")
ax[0].set_ylabel("Days")
ax[1].plot(monthly.index, monthly["Success_%"], marker="o", color="crimson")
ax[1].set_title("Delivery Success Rate by Month")
ax[1].set_ylabel("Success (%)")
ax[1].set_ylim(0, 105)
plt.tight_layout()
plt.show()

# ----------------------------------------------------------
# TASK 15: Shipment class and recommendations
# ----------------------------------------------------------
heading("TASK 15: Shipment class")

class Shipment:
    """A simple class to store one shipment."""

    def __init__(self, shipment_id, partner, delivery_days):
        self.shipment_id = shipment_id
        self.partner = partner
        self.delivery_days = delivery_days

    def describe(self):
        if pd.isnull(self.delivery_days):
            return f"{self.shipment_id} | {self.partner} | not delivered yet"
        return (f"{self.shipment_id} | {self.partner} | "
                f"{int(self.delivery_days)} days | {classify_shipment(self.delivery_days)}")

# Create objects for the first 5 shipments in the cleaned data
shipment_objects = [Shipment(r.Shipment_ID, r.Delivery_Partner, r.Delivery_Days)
                    for r in df.head(5).itertuples()]
for s in shipment_objects:
    print(s.describe())

# ----------------------------------------------------------
# FIVE RECOMMENDATIONS (values come from the results above)
# ----------------------------------------------------------
heading("FIVE PRACTICAL RECOMMENDATIONS")

slowest_partner = partner["Avg_Delivery_Days"].idxmax()
fastest_partner = partner["Avg_Delivery_Days"].idxmin()
slowest_method = avg_by_method.idxmax()
worst_month = monthly["Avg_Delivery_Days"].idxmax()
best_month = monthly["Avg_Delivery_Days"].idxmin()
lowest_success_method = method_stats["Success_%"].idxmin()
high_delay_pct = (delivered_only["Delivery_Class"] == "Highly Delayed").mean() * 100

print(f"1. Review {slowest_partner} (slowest partner: "
      f"{partner.loc[slowest_partner, 'Avg_Delivery_Days']} avg days). Set a delivery-time "
      f"target in the contract and move more orders to {fastest_partner} "
      f"({partner.loc[fastest_partner, 'Avg_Delivery_Days']} avg days).")
print(f"2. Fix the {slowest_method} method (slowest: {avg_by_method[slowest_method]} avg days) "
      f"and the weakest success rate ({lowest_success_method}: "
      f"{method_stats.loc[lowest_success_method, 'Success_%']}%). Check whether "
      f"promised delivery times are realistic.")
print(f"3. Plan extra capacity for {worst_month}, the month with the slowest "
      f"deliveries ({monthly.loc[worst_month, 'Avg_Delivery_Days']} days), and learn "
      f"from {best_month} ({monthly.loc[best_month, 'Avg_Delivery_Days']} days).")
print(f"4. Reduce Highly Delayed shipments ({high_delay_pct:.1f}% of delivered orders, "
      f"7+ days) by sending an alert when a shipment passes day 4 and "
      f"re-routing it.")
print("5. Improve data quality: validate that every Delivered order has a "
      "Delivery_Date and Shipping_Cost, and block duplicate Shipment_IDs at entry.")

print("\nProject completed successfully.")
