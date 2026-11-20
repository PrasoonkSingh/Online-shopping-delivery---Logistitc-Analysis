# Project 23: Online Shopping Delivery & Logistics Analysis

## Overview

This project analyses an online-shopping delivery dataset to understand
shipment performance, delivery delays, shipping methods, delivery
partners, and monthly trends.

**Tools:** Python, Pandas, NumPy, Matplotlib\
**Dataset:** `23_delivery_performance.csv`\
**Main program:** `project_23_delivery_analysis.py`

## Project Objectives

-   Inspect the dataset structure, columns, data types, and missing
    values.
-   Identify and remove duplicate `Shipment_ID` records.
-   Handle missing delivery dates and shipping costs using documented
    methods.
-   Calculate delivery duration and overall delivery success.
-   Compare shipping methods and delivery partners.
-   Identify the ten longest deliveries.
-   Classify shipments by delivery duration.
-   Calculate statistical measures and detect IQR outliers.
-   Compare delivery performance by month.
-   Generate five recommendations to improve logistics performance.

## Files Required

Keep these files in the same folder:

``` text
Project-23/
├── project_23_delivery_analysis.py
├── 23_delivery_performance.csv
└── README.md
```

> **Important:** The Python program expects the dataset to be named
> exactly `23_delivery_performance.csv`. If your downloaded file is
> named `23_delivery_performance(1).csv`, rename it to
> `23_delivery_performance.csv` before running the program.

## Requirements

Use Python 3.x and install the required libraries:

``` bash
pip install pandas numpy matplotlib
```

## How to Run

### Option 1: Run using VS Code or Terminal

1.  Place the Python file and CSV dataset in the same folder.
2.  Open that folder in VS Code or a terminal.
3.  Install the required libraries using the command above.
4.  Run:

``` bash
python project_23_delivery_analysis.py
```

### Option 2: Run using Jupyter Notebook

1.  Open Jupyter Notebook.
2.  Keep the Python file and CSV dataset in the same working folder.
3.  Run the Python script from a notebook cell:

``` python
%run project_23_delivery_analysis.py
```

### Option 3: Run using Google Colab

1.  Upload `project_23_delivery_analysis.py` to Colab.
2.  Upload the dataset when prompted, if it is not already available.
3.  Run the script.

## Analysis Tasks Covered

  -----------------------------------------------------------------------
  Task                                Description
  ----------------------------------- -----------------------------------
  1                                   Load the dataset and inspect its
                                      shape, columns, and data types

  2                                   Find missing values and duplicate
                                      shipment IDs

  3                                   Handle missing delivery dates and
                                      shipping costs

  4                                   Convert order and delivery dates to
                                      datetime

  5                                   Calculate `Delivery_Days`

  6                                   Calculate total shipments,
                                      delivered shipments, and success
                                      percentage

  7                                   Find average delivery duration by
                                      shipping method

  8                                   Rank delivery partners by shipment
                                      count and average delivery duration

  9                                   Compare delivery success rates by
                                      shipping method

  10                                  Display the ten shipments with the
                                      longest delivery duration

  11                                  Use a dictionary for status counts
                                      and a set for unique delivery
                                      partners

  12                                  Classify shipments by delivery
                                      duration

  13                                  Calculate mean, median, and
                                      standard deviation using NumPy

  14                                  Detect IQR outliers and compare
                                      monthly performance

  15                                  Create a `Shipment` class and
                                      provide five recommendations
  -----------------------------------------------------------------------

## Data Cleaning and Business Rules

-   Text values in `Shipment_ID`, `Shipping_Method`, `Delivery_Partner`,
    and `Order_Status` are stripped of extra spaces. Shipment IDs are
    converted to uppercase.
-   Duplicate `Shipment_ID` rows are removed, keeping the first
    occurrence.
-   `Order_Date` and `Delivery_Date` are converted to datetime. Invalid
    date values become missing values.
-   Rows with a delivery date earlier than the order date are removed.
-   Rows without a valid order date are removed.
-   Missing delivery dates for `Cancelled` and `In Transit` shipments
    are left blank because those shipments have not been delivered.
-   For records marked `Delivered` or `Delayed` with a missing delivery
    date, the program estimates a date using the median delivery
    duration for the same shipping method. The `Date_Estimated` column
    marks estimated dates.
-   Missing `Shipping_Cost` values are filled using the median shipping
    cost for the same shipping method.
-   Only records whose `Order_Status` is exactly `Delivered` count as
    successful deliveries.

## Delivery Classification

The program uses these day limits:

  Delivery duration           Classification
  --------------------------- ------------------
  0--3 days                   On-Time
  4--6 days                   Slightly Delayed
  7 days or more              Highly Delayed
  Missing delivery duration   Not Delivered

These thresholds are defined in the Python program and can be changed in
the `classify_shipment()` function.

## Statistical Analysis

The program calculates: - Mean delivery duration - Median delivery
duration - Population standard deviation - First quartile (Q1), third
quartile (Q3), and interquartile range (IQR) - IQR lower and upper
boundaries - Shipments outside the IQR boundaries - Monthly shipment
counts, average delivery days, and delivery success percentage

The usual IQR boundaries used are:

``` text
Lower boundary = Q1 - 1.5 × IQR
Upper boundary = Q3 + 1.5 × IQR
```

## Expected Outputs

When the program runs successfully, it displays: - Dataset inspection
and data-quality information - Overall delivery performance summary -
Shipping-method comparison - Delivery-partner rankings - Top ten longest
deliveries - Shipment status counts and unique partners - Delivery
classification counts - Statistical summary and IQR outliers - Monthly
performance summary - Matplotlib charts - Five logistics recommendations

## Troubleshooting

**Error: `FileNotFoundError`** - Check that the CSV is in the same
folder as the Python file. - Check that the filename is exactly
`23_delivery_performance.csv`.

**Error: `ModuleNotFoundError`** - Install the missing library. For
example:

``` bash
pip install pandas numpy matplotlib
```

**Charts are not appearing** - If using a notebook, make sure the cell
is executed. - If using a local Python environment, ensure Matplotlib is
installed and your environment supports displaying plot windows.

## Limitations

-   The project analyses the supplied historical dataset; it does not
    track live shipments.
-   Estimated delivery dates are calculated values, not original
    recorded dates. Check the `Date_Estimated` column before
    interpreting results.
-   Delivery success is based on the exact status text `Delivered`.
-   Delivery classification depends on the stated 0--3, 4--6, and 7+ day
    thresholds.

## Author

**Project 23 -- Online Shopping Delivery & Logistics Analysis**
