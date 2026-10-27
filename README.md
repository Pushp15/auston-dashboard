# 🤖 Auston Robot — Sales & Service Operations Dashboard

A real-time business intelligence dashboard built with **Streamlit** that pulls live data from a Google Sheet to monitor sales pipelines, service operations, and engineer performance for Auston Robot.

---

## 📸 Overview

The dashboard is split into two tabs:

| Tab | Purpose |
|-----|---------|
| 📈 **Sales Dashboard** | Track enquiries, quotations, expected orders, and pipeline stages |
| 🛠️ **Service Dashboard** | Monitor customer issues, resolution rates, visit completions, and priority breakdown |

---

## ✨ Features

### Sales Dashboard
- **6 KPI Metrics** — Total Enquiries, Open Enquiries, Quotes Sent, Expected Orders, Orders Received, and Overdue Follow-Ups
- **Sales Engineer Activity Table** — Enquiries logged and orders closed per engineer
- **Product Sales Distribution** — Enquiries and orders broken down by product
- **Pipeline Stage Breakdown** — Bar chart across all deal stages (New → Won/Lost)
- **Enquiry & Follow-Up Tracker** — Full filterable data table

### Service Dashboard
- **4 KPI Metrics** — Total Issues Logged, Open Issues, Resolution Rate (%), Visits Completed
- **Service Engineer Metrics** — Visits completed, open issues, and resolved issues per engineer
- **Issues by Priority Matrix** — Colour-coded Altair bar chart (Low / Medium / High / Critical)
- **Customer Issues Log** — Full filterable data table

### Global Controls
- **Real-Time Live Sync** toggle — enables zero-TTL cache for instant data refresh
- **Force Sync Data** button — clears cache and reruns the app on demand
- **Filter by Engineer** — scopes all metrics to a specific sales/service engineer
- **Filter by Product** — scopes all metrics to a specific product

---

## 🗂️ Google Sheet Structure

The app reads from a single public Google Spreadsheet with **four tabs**:

| Sheet Tab | Key Columns |
|-----------|-------------|
| `ENQUIRIES` | `ENGINEER`, `PRODUCT`, `ENQUIRY STATUS`, `QUOTATION STATUS`, `EXPECTED ORDER`, `NEXT FOLLOW-UP` |
| `CUSTOMER ISSUES` | `ENGINEER`, `PRODUCT`, `CURRENT STATUS`, `PRIORITY` |
| `VISITS` | `ENGINEER`, `PRODUCT`, `VISIT STATUS` |
| `ORDERS` | `ENGINEER`, `PRODUCT` |

> **Important:** The Google Sheet must be shared with **"Anyone with the link can view"** for the data fetch to work.

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd Sales_Dashboard_KPIs
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Your Google Sheet

Open `App.py` and update the `SPREADSHEET_ID` variable with your own spreadsheet ID:

```python
# Line 41 in App.py
SPREADSHEET_ID = "your-google-spreadsheet-id-here"
```

You can find the ID in your sheet's URL:
```
https://docs.google.com/spreadsheets/d/<SPREADSHEET_ID>/edit
```

### 4. Run the App

```bash
streamlit run App.py
```

The dashboard will open at `http://localhost:8501`.

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `streamlit` | Web app framework and UI components |
| `pandas` | Data loading, cleaning, and filtering |
| `altair` | Interactive charts (Priority Matrix) |
| `xlsxwriter` | Excel export support |

Install all dependencies with:

```bash
pip install -r requirements.txt
```

---

## 📁 Project Structure

```
Sales_Dashboard_KPIs/
├── App.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

---

## 🔧 Configuration Notes

- **Date Columns**: Any column with `DATE` or `FOLLOW-UP` in its name is automatically parsed as a datetime.
- **Overdue Follow-Ups**: Calculated by comparing `NEXT FOLLOW-UP` dates against today's date.
- **Dynamic Filters**: Engineers and products are extracted automatically from all four sheets — no hardcoding needed.
- **Empty Data Handling**: If all four sheets fail to load, the app shows an error and stops gracefully.

---

## 📄 License

This project is proprietary to **Auston Robot**. All rights reserved.