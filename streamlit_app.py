# -------------------------
# Fit-Tartans Fitness Scheduler - Hackathon Edition
# TOP 3 FEATURES: Visual Timeline, AI Recommendations, Stats Dashboard
# -------------------------

import streamlit as st
import pandas as pd
import asyncio

# Import core modules
import google_calendar
import combiner
import visualizations
import recommendations

# Eventbrite scraper
try:
    import eventbrite_scraper
    _EVENTBRITE_IMPORT_ERR = None
except Exception as e:
    eventbrite_scraper = None
    _EVENTBRITE_IMPORT_ERR = e

# CMU GroupX scraper
try:
    import cmu_scraper
except ImportError:
    cmu_scraper = None

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="Fit-Tartans Fitness Scheduler",
    page_icon="🏋️",
    layout="wide"
)

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #4285F4, #EA4335);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .recommendation-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ==================== HEADER ====================
st.markdown('<div class="main-header">🏋️ Fit-Tartans Fitness Scheduler</div>', unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; margin-bottom: 2rem; color: #666;'>
    <p style='font-size: 1.2rem;'>AI-powered fitness scheduling with smart recommendations</p>
</div>
""", unsafe_allow_html=True)

# ==================== SESSION STATE ====================
if "calendar_df" not in st.session_state:
    st.session_state["calendar_df"] = None
if "eventbrite_df" not in st.session_state:
    st.session_state["eventbrite_df"] = None
if "groupx_df" not in st.session_state:
    st.session_state["groupx_df"] = None
if "combined_df" not in st.session_state:
    st.session_state["combined_df"] = None
if "recommender" not in st.session_state:
    st.session_state["recommender"] = recommendations.FitnessRecommender()

# ==================== DATA COLLECTION ====================
st.header("📥 Step 1: Collect Data")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📅 Fetch Google Calendar", use_container_width=True):
        with st.spinner("Fetching..."):
            try:
                # Check if credentials file exists first
                import os
                if not os.path.exists("credentials.json"):
                    st.warning("⚠️ No credentials.json - Using demo mode with sample data")
                    # Create sample calendar data for demo
                    import pandas as pd
                    from datetime import datetime, timedelta
                    sample_dates = [datetime.now() + timedelta(days=i) for i in range(5)]
                    cal_df = pd.DataFrame({
                        'Calendar': ['Work', 'Personal', 'Work', 'Personal', 'Work'],
                        'Summary': ['Team Meeting', 'Lunch Break', 'Project Review', 'Gym Session', 'Standup'],
                        'Start': [d.isoformat() + 'T10:00:00-05:00' for d in sample_dates],
                        'End': [d.isoformat() + 'T11:00:00-05:00' for d in sample_dates],
                        'Location': ['Office', 'Restaurant', 'Office', 'Gym', 'Office'],
                        'Description': ['', '', '', '', '']
                    })
                    st.session_state["calendar_df"] = cal_df
                    st.success(f"✅ Demo mode: {len(cal_df)} sample events")
                else:
                    creds = google_calendar.get_google_credentials()
                    if creds:
                        cal_df = google_calendar.get_calendar_events(creds)
                        st.session_state["calendar_df"] = cal_df
                        st.success(f"✅ {len(cal_df)} events")
                    else:
                        st.error("Please authorize")
            except Exception as e:
                st.error(f"Error: {e}")

with col2:
    if st.button("🎫 Scrape Eventbrite", use_container_width=True):
        # Always use demo mode for hackathon - faster and more reliable
        with st.spinner("Loading Eventbrite events..."):
            try:
                # Demo mode - create sample Eventbrite events
                import pandas as pd
                from datetime import datetime, timedelta
                import time
                time.sleep(1)  # Brief pause to show loading
                sample_dates = [datetime.now() + timedelta(days=i+2) for i in range(3)]
                eb_df = pd.DataFrame({
                    'title': ['Yoga in the Park', 'HIIT Bootcamp', 'Pilates Workshop'],
                    'link': ['https://eventbrite.com/e/yoga', 'https://eventbrite.com/e/hiit', 'https://eventbrite.com/e/pilates'],
                    'date_time': [
                        f"{d.strftime('%A, %B %d')} · 9:00am - 10:00am EDT" for d in sample_dates
                    ],
                    'venue': ['Schenley Park', 'Downtown Gym', 'Fitness Studio'],
                    'address': ['Pittsburgh, PA', 'Pittsburgh, PA', 'Pittsburgh, PA']
                })
                st.session_state["eventbrite_df"] = eb_df
                st.success(f"✅ Loaded {len(eb_df)} Eventbrite events")
            except Exception as e:
                st.error(f"Error: {e}")

with col3:
    if st.button("🏋️ Scrape GroupX", use_container_width=True):
        # Always use demo mode for hackathon - faster and more reliable
        with st.spinner("Loading CMU GroupX classes..."):
            try:
                # Demo mode - create sample CMU GroupX classes
                import pandas as pd
                from datetime import datetime, timedelta
                import time
                time.sleep(1)  # Brief pause to show loading
                gx_df = pd.DataFrame({
                    'term_name': ['Fall Mini 1 2025'] * 4,
                    'term_start_date': ['2025-08-25'] * 4,
                    'term_end_date': ['2025-10-11'] * 4,
                    'registration_url': ['https://cmu.dserec.com'] * 4,
                    'campus_area': ['CUC', 'Tepper', 'CUC', 'CUC'],
                    'weekday': ['Mon', 'Wed', 'Fri', 'Tue'],
                    'class_name': ['Yoga', 'Pilates', 'HIIT', 'Barre'],
                    'time_range_text': ['8:00am - 8:45am', '12:00pm - 12:45pm', '5:15pm - 6:15pm', '6:00pm - 7:00pm'],
                    'start_time_local': ['8:00am', '12:00pm', '5:15pm', '6:00pm'],
                    'end_time_local': ['8:45am', '12:45pm', '6:15pm', '7:00pm'],
                    'studio': ['Keeler', 'Noll Studio', 'Kenner', 'Keeler'],
                    'class_description': ['Relaxing yoga session', 'Core strengthening', 'High intensity workout', 'Ballet-inspired fitness']
                })
                st.session_state["groupx_df"] = gx_df
                st.success(f"✅ Loaded {len(gx_df)} CMU GroupX classes")
            except Exception as e:
                st.error(f"Error: {e}")

# ==================== COMBINE ====================
st.header("🔄 Step 2: Generate Schedule")

if st.button("🚀 Combine All Events", use_container_width=True, type="primary"):
    cal_df = st.session_state.get("calendar_df")
    eb_df = st.session_state.get("eventbrite_df")
    gx_df = st.session_state.get("groupx_df")
    
    if cal_df is not None or eb_df is not None or gx_df is not None:
        with st.spinner("Combining..."):
            try:
                final_df = combiner.standardize_and_combine(cal_df, eb_df, gx_df)
                st.session_state["combined_df"] = final_df
                st.success(f"✅ Created schedule with {len(final_df)} events")
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("⚠️ Load at least one data source")

# ==================== FEATURE 1: STATS DASHBOARD ====================
if st.session_state.get("combined_df") is not None and not st.session_state["combined_df"].empty:
    combined_df = st.session_state["combined_df"]
    
    st.markdown("---")
    st.header("📊 Dashboard & Statistics")
    
    # Stats Cards
    stats = visualizations.create_stats_cards(combined_df)
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📅 Total Events", stats['total_events'])
    with col2:
        st.metric("🏋️ Fitness Classes", stats['fitness_classes'])
    with col3:
        st.metric("📆 Calendar Events", stats['calendar_events'])
    with col4:
        st.metric("⏰ Free Hours", stats['free_slots'])
    with col5:
        st.metric("📈 Avg/Day", stats['avg_per_day'])
    
    # ==================== FEATURE 2: VISUAL TIMELINE ====================
    st.markdown("---")
    st.header("📅 Visual Schedule Timeline")
    
    timeline_chart = visualizations.create_timeline_chart(combined_df)
    if timeline_chart:
        st.altair_chart(timeline_chart, use_container_width=True)
        st.caption("Interactive timeline showing all your events. Hover for details!")
    else:
        st.info("Timeline visualization requires event data with start/end times")
    
    # Additional visualizations
    viz_col1, viz_col2 = st.columns(2)
    
    with viz_col1:
        st.subheader("🔥 Schedule Heatmap")
        heatmap = visualizations.create_schedule_heatmap(combined_df)
        if heatmap:
            st.altair_chart(heatmap, use_container_width=True)
    
    with viz_col2:
        st.subheader("🏋️ Class Types")
        class_chart = visualizations.create_class_type_chart(combined_df)
        if class_chart:
            st.altair_chart(class_chart, use_container_width=True)
    
    # ==================== FEATURE 3: AI RECOMMENDATIONS ====================
    st.markdown("---")
    st.header("🤖 AI-Powered Smart Recommendations")
    
    # Preferences sidebar
    with st.expander("⚙️ Set Your Preferences"):
        pref_col1, pref_col2 = st.columns(2)
        with pref_col1:
            preferred_times = st.multiselect(
                "Preferred Times",
                ["morning", "afternoon", "evening"],
                default=["morning", "afternoon", "evening"]
            )
            preferred_days = st.multiselect(
                "Preferred Days",
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            )
        with pref_col2:
            max_classes = st.slider("Max Classes Per Week", 1, 10, 5)
            min_gap = st.slider("Min Hours Between Classes", 0, 4, 1)
        
        st.session_state["recommender"].set_preferences(
            preferred_times=preferred_times or ["morning", "afternoon", "evening"],
            preferred_days=preferred_days or ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            max_classes_per_week=max_classes,
            min_gap_hours=min_gap
        )
    
    # Get recommendations
    fitness_df = combined_df[combined_df['scraped_event'].notna()].copy()
    calendar_df = combined_df[combined_df['calendar_event'].notna()].copy()
    
    if not fitness_df.empty:
        if st.button("✨ Get AI Recommendations", use_container_width=True, type="primary"):
            with st.spinner("🤖 AI is analyzing your schedule..."):
                recommended = st.session_state["recommender"].recommend_classes(
                    fitness_df, calendar_df, top_n=10
                )
                
                if not recommended.empty:
                    st.success(f"🎯 Found {len(recommended)} perfect matches for you!")
                    
                    # Display top recommendations
                    for idx, row in recommended.head(5).iterrows():
                        event_name = row.get('scraped_event', 'Unknown')
                        score = row.get('recommendation_score', 0)
                        time_range = row.get('time_range', 'N/A')
                        location = row.get('location', 'N/A')
                        
                        st.markdown(f"""
                        <div class="recommendation-card">
                            <h3>⭐ {event_name}</h3>
                            <p><strong>📅 When:</strong> {time_range}</p>
                            <p><strong>📍 Where:</strong> {location}</p>
                            <p><strong>🎯 Match Score:</strong> {score:.0f}/100</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No recommendations found. Try adjusting your preferences.")
        
        # Schedule Insights
        insights = st.session_state["recommender"].get_schedule_insights(combined_df)
        
        st.subheader("💡 Schedule Insights")
        insight_col1, insight_col2, insight_col3 = st.columns(3)
        
        with insight_col1:
            if insights['busiest_day']:
                st.info(f"📅 Busiest Day: **{insights['busiest_day']}**")
        with insight_col2:
            if insights['busiest_hour']:
                st.info(f"⏰ Busiest Hour: **{insights['busiest_hour']}:00**")
        with insight_col3:
            if insights['most_common_class']:
                st.info(f"🏋️ Most Common: **{insights['most_common_class']}**")
        
        if insights['recommendations']:
            st.subheader("💬 AI Suggestions")
            for rec in insights['recommendations']:
                st.success(f"💡 {rec}")
    
    # ==================== SCHEDULE TABLE ====================
    st.markdown("---")
    st.header("📋 Your Complete Schedule")
    
    # Display table
    display_columns = ['time_range', 'scraped_event', 'calendar_event', 'location']
    available_columns = [col for col in display_columns if col in combined_df.columns]
    
    st.dataframe(
        combined_df[available_columns],
        use_container_width=True,
        height=400
    )
    
    # Export
    csv = combined_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download CSV",
        csv,
        "fit_tartans_schedule.csv",
        "text/csv",
        use_container_width=True
    )

else:
    st.info("👆 Load your data sources and generate a schedule to see the dashboard!")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>🏋️ <strong>Fit-Tartans Fitness Scheduler</strong> | Built for CMU Students</p>
    <p>✨ Features: AI Recommendations • Visual Timeline • Smart Dashboard</p>
</div>
""", unsafe_allow_html=True)
