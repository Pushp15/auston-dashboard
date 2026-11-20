# 🛠️ Apex — Service Operations & CSAT Dashboard

A real-time field service operations, ticketing, and CSAT dashboard built with **Streamlit** that pulls live data from Google Sheets (`CUSTOMER ISSUES` & `VISITS` tabs).

---

## ✨ Features

- **4 Core Service KPIs**: Total Issues Logged, Open Issues, Resolution Rate (%), and Visits Completed.
- **Service Engineer Metrics**: Completed field visits, open tickets, and resolved tickets per engineer.
- **Issues by Priority Matrix**: Interactive severity chart (`Low`, `Medium`, `High`, `Critical`).
- **All Customer Issues Log**: Complete searchable and filterable customer issue ticket registry.
- **Real-Time Sync**: Auto-refresh interval slider + force sync button.
- **Dynamic Filters**: Filter all data by Engineer and Product.

---

## 🗂️ Google Sheet Tabs Used

This dashboard connects to:
- `CUSTOMER ISSUES`
- `VISITS`

---

## 🚀 Run Locally

```bash
pip install -r requirements.txt
streamlit run App.py
```
