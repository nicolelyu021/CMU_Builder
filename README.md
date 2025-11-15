# 🏋️ Fit-Tartans Fitness Scheduler

**AI-powered fitness scheduling assistant for CMU students**

Combine your Google Calendar with fitness classes from Eventbrite and CMU GroupX to create the perfect workout schedule.

---

## ✨ Features

### 🤖 AI-Powered Recommendations
- Smart algorithm scores fitness classes based on your preferences
- Conflict detection with existing calendar events
- Personalized recommendations with match scores (0-100)
- Schedule insights (busiest day, busiest hour, most common class)

### 📅 Visual Timeline
- Interactive Gantt chart showing all events
- Color-coded by source (Calendar vs Fitness Classes)
- Schedule heatmap showing density by day/hour
- Class type distribution charts
- Hover tooltips for event details

### 📊 Stats Dashboard
- Real-time metrics: Total Events, Fitness Classes, Calendar Events
- Free hours calculation
- Average events per day
- Beautiful metric cards

### 🔄 Data Integration
- **Google Calendar**: Fetch your existing calendar events
- **Eventbrite**: Scrape fitness events from Pittsburgh area
- **CMU GroupX**: Scrape CMU recreation class schedules
- Automatic conflict detection and removal
- Unified schedule view

---

## 🚀 Quick Start

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/nicolelyu021/CMU_Builder.git
   cd CMU_Builder
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers** (for web scraping)
   ```bash
   playwright install chromium
   ```

4. **Run the app**
   ```bash
   streamlit run streamlit_app.py
   ```

5. **Open in browser**
   - The app will automatically open at `http://localhost:8501`
   - Or manually navigate to that URL

---

## 📖 How to Use

### Step 1: Collect Data

Click the three buttons to load data from different sources:

1. **📅 Fetch Google Calendar**
   - Connects to your Google Calendar (requires `credentials.json`)
   - Or uses demo mode with sample data if credentials not available
   - Fetches events for the next 14 days

2. **🎫 Scrape Eventbrite**
   - Scrapes fitness events from Eventbrite (Pittsburgh area)
   - Or uses demo mode with sample events

3. **🏋️ Scrape GroupX**
   - Scrapes CMU GroupX class schedules
   - Or uses demo mode with sample classes

### Step 2: Generate Schedule

Click the **🚀 Combine All Events** button to:
- Merge all data sources into one unified schedule
- Remove overlapping events (prioritizes calendar events)
- Standardize timezones and formats
- Generate the dashboard

### Step 3: Explore Features

After combining, you'll see:

- **📊 Dashboard**: Stats and metrics at a glance
- **📅 Visual Timeline**: Interactive Gantt chart of all events
- **🤖 AI Recommendations**: Click "Get AI Recommendations" for personalized suggestions
- **📋 Schedule Table**: Complete list of all events

---

## 🎯 Demo Mode

The app includes **demo mode** for all data sources, so you can:
- Test the app without setting up credentials
- Show a live demo during presentations
- Use sample data that works instantly

**Demo mode activates automatically when:**
- Google Calendar: No `credentials.json` file
- Eventbrite: Scraper unavailable or fails
- GroupX: Scraper unavailable or fails

---

## 🔧 Setup (Optional)

### Google Calendar Integration

To use real Google Calendar data:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Google Calendar API**
4. Create **OAuth 2.0 credentials**
5. Download `credentials.json` and place it in the project directory
6. The app will guide you through OAuth flow on first use

### Real Web Scraping

The app can scrape real data from:
- **Eventbrite**: Requires Playwright (already installed)
- **CMU GroupX**: Requires Selenium and Chrome (may need login)

For hackathon demos, demo mode is recommended for speed and reliability.

---

## 📁 Project Structure

```
CMU_Builder/
├── streamlit_app.py          # Main Streamlit application
├── google_calendar.py         # Google Calendar integration
├── eventbrite_scraper.py     # Eventbrite web scraper
├── cmu_scraper.py            # CMU GroupX web scraper
├── combiner.py               # Data combination and processing
├── visualizations.py         # Charts and timeline visualizations
├── recommendations.py        # AI recommendation engine
├── calendar_export.py        # Calendar export functionality
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── DEMO_FEATURES.md          # Detailed demo guide
└── QUICK_DEMO_GUIDE.md       # Quick reference
```

---

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Visualizations**: Altair
- **Data Processing**: Pandas, NumPy
- **Web Scraping**: Playwright, Selenium
- **APIs**: Google Calendar API
- **Authentication**: OAuth2

---

## 🎤 Hackathon Presentation Tips

1. **Start with demo mode** - It's faster and more reliable
2. **Show the 3 main features**:
   - Stats Dashboard (metrics at a glance)
   - Visual Timeline (interactive Gantt chart)
   - AI Recommendations (smart suggestions)
3. **Emphasize the AI** - Mention the scoring algorithm and personalization
4. **Highlight the visuals** - The timeline makes scheduling intuitive

See `DEMO_FEATURES.md` for detailed presentation script.

---

## 📝 Requirements

- Python 3.8+
- Google Chrome (for Selenium scraping)
- Internet connection (for web scraping and Google Calendar API)

---

## 🤝 Contributing

This is a hackathon project. Feel free to fork and improve!

---

## 📄 License

This project is open source and available for educational purposes.

---

## 🙏 Acknowledgments

- Built for CMU students
- Uses Google Calendar API
- Scrapes data from Eventbrite and CMU GroupX
- Powered by Streamlit and AI recommendations

---

**Built with ❤️ for the CMU community**
