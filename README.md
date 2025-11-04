# 🌍 TravelWise

**TravelWise** is an all-in-one travel management and budgeting app built with **Streamlit**.  
It helps users plan their trips efficiently — manage expenses, convert currencies, set travel budgets, and even chat with an AI travel assistant — all in one place.

🔗 **Live App:** [https://travelwise-app.streamlit.app/](https://travelwise-app.streamlit.app/)

---

## 🚀 Features

- **✈️ Budget Planner** — Keep track of your travel expenses and set spending goals.
- **💱 Currency Converter** — Convert between different currencies in real time.
- **📊 Dashboard** — Get insights into your travel spending habits.
- **🧠 AI Chatbot** — Ask travel-related questions or get itinerary suggestions.
- **⚙️ Account Settings** — Manage your user profile and data securely.

---

## 🧩 Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io/)
- **Backend:** Python (with SQLite for database)
- **Libraries Used:**
  - `pandas`
  - `sqlite3`
  - `streamlit`
  - `requests` (for currency APIs)
  - `dotenv` (for managing environment variables)

---

## 📁 Folder Structure

```
travelwise/
│
├── assets/ # Static assets (images, icons, etc.)
├── database/
│ ├── chathistory.db
│ └── users.db
├── pages/ # Streamlit pages
│ ├── 1_Account Settings.py
│ ├── 2_Budget_Planner.py
│ ├── 3_Currency_Converter.py
│ ├── 4_Dashboard.py
│ ├── 5_AI Chatbot.py
│ └── 6_Chat History.py
├── utils/ # Helper functions
├── venv/ # Virtual environment
├── Home.py # Main Streamlit entry point
├── requirements.txt # Dependencies
└── README.md # Project documentation
```
