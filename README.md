# 🌾 Chhattisgarh Mausam Analytics Engine

An advanced, micro-regional telemetry platform designed to track, simulate, and analyze atmospheric conditions across various district clusters in Chhattisgarh, India. This application merges real-time weather observations with customized analytical interpolations inside a modern, high-end dark glassmorphic user interface.

---

## 🚀 Core Features

*   **Secure Access Portal:** Built-in cryptographic node operator framework with automated local persistent profile synchronization (`users.json`).
*   **Micro-Regional Telemetry Matrix:** Precision geographical dictionary matching sub-locales (e.g., Civic Centre, Mainpat Ridge, Chitrakote Belt) across Chhattisgarh's key urban and ecological hubs.
*   **Decoupled Interactive Visualization Engine:** Spline-smoothed data graph built on a dual-axis interactive Plotly workspace, completely separated from its metrics legend card to ensure maximum readability and layout cleanliness.
*   **Predictive Boundary Analysis:** Advanced mathematical interpolation layer (`scipy.interpolate.make_interp_spline`) simulating atmospheric pressure, moisture retention, and localized heat indices.

---

## 🛠️ Stack Architecture

*   **Frontend Interface:** Streamlit (Custom HTML5/CSS3 Injections)
*   **Data Layout & Analytics:** Pandas, NumPy, SciPy (Cubic Splines)
*   **Interactive Visualizations:** Plotly Graphing Objects (`go.Figure`)
*   **Data Ingestion API:** OpenWeather API Ecosystem

---

## 📦 Installation & Setup

To run this telemetry dashboard locally, open your **Command Prompt** (Windows) or **Terminal** (Mac) and follow these steps:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Shunjal-24/chhattisgarh-mausam-analytics.git](https://github.com/Shunjal-24/chhattisgarh-mausam-analytics.git)
   cd chhattisgarh-mausam-analytics

2. **Install the required dependencies:**
   ```bash
   pip install streamlit pandas numpy scipy plotly requests

3.**Launch the application:**
  ```bash
  streamlit run weather.py
