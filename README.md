# 📈 Apex — Sales Performance Dashboard

A real-time sales operations and pipeline intelligence dashboard built with **Streamlit** that pulls live data from Google Sheets (`ENQUIRIES` & `ORDERS` tabs).

---

## ✨ Features

- **6 Real-Time KPIs**: Total Enquiries, Open Enquiries, Quotes Sent, Expected Orders, Orders Received, and Overdue Follow-ups.
- **Sales Engineer Activity**: Enquiries logged vs. orders closed per engineer.
- **Product Sales Distribution**: Lead and order breakdown by product.
- **Sales Update Chart**: Dynamic stage-by-stage pipeline velocity breakdown.
- **Recent Enquiries & Follow-up Tracker**: Interactive, searchable table of all leads and next action dates.
- **Auto-Sync & Manual Refresh**: Configurable auto-reload interval + force sync button.
- **Dynamic Filters**: Filter all charts and metrics by Engineer and Product.

---

## 🗂️ Google Sheet Tabs Used

This dashboard connects to:
- `ENQUIRIES`
- `ORDERS`

---

## 🚀 Run Locally

```bash
pip install -r requirements.txt
streamlit run App.py
```
