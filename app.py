import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# Page configuration
st.set_page_config(
    page_title="CoachBot AI - Your Virtual Sports Coach",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .feature-box {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin: 1rem 0;
    }
    .output-box {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #e8f4f8;
        border-left: 5px solid #1E88E5;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'api_configured' not in st.session_state:
    st.session_state.api_configured = False
if 'history' not in st.session_state:
    st.session_state.history = []

# Configure API key from Streamlit secrets
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    st.session_state.api_configured = True
except Exception as e:
    st.session_state.api_configured = False
    st.error(f"⚠️ API Key Configuration Error: {str(e)}")
    st.info("Please make sure GEMINI_API_KEY is set in Streamlit secrets.")

# Header
st.markdown('<div class="main-header">⚽ CoachBot AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Your Personal AI Sports Coach - Empowering Youth Athletes</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("ℹ️ About CoachBot")
    st.info("""
    CoachBot AI provides:
    - 🏋️ Personalized workout plans
    - 🩺 Injury-safe training
    - 🎯 Tactical advice
    - 🥗 Nutrition guidance
    - 🧠 Mental preparation
    """)
    
    st.markdown("---")
    st.header("📊 Settings")
    temperature = st.slider("Creativity Level", 0.1, 1.0, 0.5, 0.1, 
                           help="Lower = Conservative, Higher = Creative")
    
    st.markdown("---")
    if st.session_state.api_configured:
        st.success("✅ API Configured")
    else:
        st.error("❌ API Not Configured")

# Main content
if not st.session_state.api_configured:
    st.error("⚠️ API Key is not configured properly!")
    st.info("""
    ### For administrators:
    Configure the API key in Streamlit Cloud:
    1. Go to your app settings in Streamlit Cloud
    2. Click on "Secrets"
    3. Add your Gemini API key as:
    GEMINI_API_KEY = "your-api-key-here"
""")
else:
    # Feature Selection
    st.header("🎯 Select Your Coaching Feature")
    
    features = {
        "1️⃣ Position-Based Workout Plan": "workout_plan",
        "2️⃣ Injury Recovery Training": "injury_recovery",
        "3️⃣ Tactical Coaching Tips": "tactical_tips",
        "4️⃣ Nutrition Guide": "nutrition_guide",
        "5️⃣ Warm-up & Cool-down Routine": "warmup_cooldown",
        "6️⃣ Mental Focus & Tournament Prep": "mental_prep",
        "7️⃣ Hydration & Electrolyte Strategy": "hydration",
        "8️⃣ Pre-Match Visualization": "visualization",
        "9️⃣ Position-Specific Drills": "position_drills",
        "🔟 Post-Injury Mobility Workout": "mobility_workout"
    }
    
    selected_feature = st.selectbox("Choose a coaching feature:", list(features.keys()))
    feature_code = features[selected_feature]
    
    st.markdown("---")
    
    # Common inputs
    col1, col2 = st.columns(2)
    
    with col1:
        sport = st.selectbox("Sport", [
            "Football/Soccer", "Cricket", "Basketball", "Athletics", 
            "Volleyball", "Tennis", "Badminton", "Swimming", "Hockey"
        ])
        
        age = st.number_input("Age", min_value=10, max_value=25, value=15)
        
        gender = st.selectbox("Gender", ["Male", "Female", "Prefer not to say"])
    
    with col2:
        if sport == "Football/Soccer":
            positions = ["Goalkeeper", "Defender", "Midfielder", "Forward/Striker", "Winger"]
        elif sport == "Cricket":
            positions = ["Batsman", "Bowler (Fast)", "Bowler (Spin)", "All-rounder", "Wicket-keeper"]
        elif sport == "Basketball":
            positions = ["Point Guard", "Shooting Guard", "Small Forward", "Power Forward", "Center"]
        elif sport == "Athletics":
            positions = ["Sprinter", "Middle Distance", "Long Distance", "Jumper", "Thrower"]
        else:
            positions = ["General Player", "Attacker", "Defender", "All-rounder"]
        
        position = st.selectbox("Position/Specialization", positions)
        
        experience_level = st.selectbox("Experience Level", [
            "Beginner (0-1 years)",
            "Intermediate (1-3 years)",
            "Advanced (3-5 years)",
            "Elite (5+ years)"
        ])
    
    # Feature-specific inputs
    st.markdown("### 📝 Specific Requirements")
    
    if feature_code in ["injury_recovery", "mobility_workout"]:
        injury_history = st.text_area("Injury History (describe any past or current injuries)", 
                                      placeholder="e.g., Knee sprain 3 months ago, recovering from ankle strain")
        injury_severity = st.select_slider("Current Injury Status", 
                                          ["Fully Recovered", "Mild Discomfort", "Moderate Pain", "Recovering", "Recent Injury"])
    
    if feature_code in ["workout_plan", "injury_recovery", "mobility_workout", "position_drills"]:
        col1, col2 = st.columns(2)
        with col1:
            training_days = st.number_input("Training Days per Week", 1, 7, 4)
            session_duration = st.slider("Session Duration (minutes)", 30, 120, 60, 15)
        with col2:
            intensity = st.select_slider("Preferred Intensity", 
                                        ["Low", "Moderate", "High", "Very High"])
            equipment = st.multiselect("Available Equipment", 
                                      ["Gym", "Resistance Bands", "Dumbbells", "Bodyweight Only", 
                                       "Pool", "Track", "Sports Field", "Home Setup"])
    
    if feature_code in ["nutrition_guide"]:
        col1, col2 = st.columns(2)
        with col1:
            diet_type = st.selectbox("Diet Preference", 
                                    ["Vegetarian", "Non-Vegetarian", "Vegan", "Pescatarian", "No Preference"])
            allergies = st.text_input("Food Allergies/Restrictions", 
                                     placeholder="e.g., lactose intolerant, nut allergy")
        with col2:
            calorie_goal = st.selectbox("Calorie Goal", 
                                       ["Weight Loss", "Maintenance", "Muscle Gain", "Athletic Performance"])
            meal_count = st.slider("Meals per Day", 3, 6, 4)
    
    if feature_code == "tactical_tips":
        skill_focus = st.text_input("Skill to Improve", 
                                   placeholder="e.g., passing accuracy, shooting power, defensive positioning")
        tactical_goal = st.text_area("Specific Tactical Goal", 
                                    placeholder="e.g., improve decision-making in final third, better positioning on corners")
    
    if feature_code == "mental_prep":
        event_type = st.selectbox("Upcoming Event", 
                                 ["School Tournament", "Regional Competition", "State Championship", 
                                  "National Event", "Regular Match", "Trials/Selection"])
        days_until = st.number_input("Days Until Event", 1, 90, 7)
        mental_challenges = st.multiselect("Mental Challenges", 
                                          ["Performance Anxiety", "Lack of Focus", "Pressure Handling", 
                                           "Confidence Issues", "Motivation", "Pre-game Nerves"])
    
    general_goal = st.text_area("Your Primary Goal", 
                               placeholder="e.g., build stamina for full match, recover from injury, prepare for tournament")
    
    # Generate button
    if st.button("🚀 Generate Personalized Coaching Plan", type="primary", use_container_width=True):
        with st.spinner("🤖 CoachBot is analyzing your requirements..."):
            try:
                # Initialize Gemini model
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Construct prompt based on feature
                prompt = f"""You are CoachBot AI, an expert sports coach specializing in youth athlete development. 
You are working with a {age}-year-old {gender} {sport} player who plays as a {position}.
Experience level: {experience_level}

"""
                
                if feature_code == "workout_plan":
                    prompt += f"""Generate a comprehensive {training_days}-day per week workout plan.
Each session should be approximately {session_duration} minutes.
Intensity level: {intensity}
Available equipment: {', '.join(equipment) if equipment else 'Bodyweight only'}

Goal: {general_goal}

Provide:
1. Weekly training schedule with specific exercises
2. Sets, reps, and rest periods
3. Progressive overload strategy
4. Position-specific conditioning exercises
5. Recovery recommendations

Format the response with clear sections and be specific about exercises."""

                elif feature_code == "injury_recovery":
                    prompt += f"""Create a safe recovery training plan considering:
Injury History: {injury_history}
Current Status: {injury_severity}
Training availability: {training_days} days/week, {session_duration} min sessions
Intensity: {intensity}
Equipment: {', '.join(equipment) if equipment else 'Bodyweight only'}

Goal: {general_goal}

Provide:
1. Phase-by-phase recovery plan
2. Exercises to avoid and safe alternatives
3. Gradual progression timeline
4. Strengthening exercises for injury prevention
5. Signs to watch for (when to rest)
6. Return-to-play guidelines

Be extremely cautious about injury safety."""

                elif feature_code == "tactical_tips":
                    prompt += f"""Provide tactical coaching advice to improve:
Skill Focus: {skill_focus if 'skill_focus' in locals() else 'overall game'}
Tactical Goal: {tactical_goal if 'tactical_goal' in locals() else general_goal}

Provide:
1. Key tactical concepts for the position
2. Decision-making frameworks
3. Position-specific situations and solutions
4. Game reading skills
5. Practice drills to improve tactical awareness
6. Video analysis tips (what to watch)

Make it practical and applicable to youth level."""

                elif feature_code == "nutrition_guide":
                    prompt += f"""Create a {meal_count}-meal per day nutrition plan for:
Diet Type: {diet_type}
Allergies/Restrictions: {allergies if allergies else 'None'}
Goal: {calorie_goal}
Overall objective: {general_goal}

Provide:
1. Daily meal plan with specific foods and portions
2. Pre-training and post-training nutrition
3. Hydration guidelines
4. Snack recommendations
5. Supplement suggestions (if appropriate for youth)
6. Match-day nutrition strategy
7. Weekly grocery list

Focus on whole foods, age-appropriate portions, and athletic performance."""

                elif feature_code == "warmup_cooldown":
                    prompt += f"""Design a complete warm-up and cool-down routine for:
Session type: {intensity} intensity training
Duration: {session_duration} minutes session
Goal: {general_goal}

Provide:
1. 10-15 minute dynamic warm-up (position-specific)
2. Sport-specific activation exercises
3. 10-15 minute cool-down routine
4. Static stretching protocol
5. Foam rolling recommendations
6. Breathing exercises

Make it specific to {sport} and {position}."""

                elif feature_code == "mental_prep":
                    prompt += f"""Create a mental preparation program for:
Event: {event_type if 'event_type' in locals() else 'upcoming competition'}
Days until event: {days_until if 'days_until' in locals() else 7}
Challenges: {', '.join(mental_challenges) if 'mental_challenges' in locals() else 'general preparation'}
Goal: {general_goal}

Provide:
1. Daily mental training exercises (countdown to event)
2. Visualization techniques
3. Breathing and relaxation methods
4. Pre-game routine
5. Focus techniques during competition
6. Positive self-talk strategies
7. Performance anxiety management

Keep it age-appropriate and practical."""

                elif feature_code == "hydration":
                    prompt += f"""Develop a hydration and electrolyte strategy for:
Training schedule: {training_days if 'training_days' in locals() else 4} days/week
Session duration: {session_duration if 'session_duration' in locals() else 60} minutes
Intensity: {intensity if 'intensity' in locals() else 'Moderate'}
Goal: {general_goal}

Provide:
1. Daily water intake targets
2. Pre, during, and post-training hydration
3. Electrolyte replacement strategies
4. Signs of dehydration to watch for
5. Sports drink recommendations (when needed)
6. Hydration for different weather conditions
7. Match-day hydration schedule

Be specific with amounts and timing."""

                elif feature_code == "visualization":
                    prompt += f"""Create pre-match visualization techniques for:
Position: {position}
Goal: {general_goal}

Provide:
1. Step-by-step visualization exercises
2. Position-specific scenarios to visualize
3. Success imagery techniques
4. Opponent analysis mental preparation
5. Confidence-building visualizations
6. 5-minute pre-game visualization routine
7. Recovery from mistakes mental strategy

Make it practical for a {age}-year-old athlete."""

                elif feature_code == "position_drills":
                    prompt += f"""Design position-specific training drills for:
Training days: {training_days if 'training_days' in locals() else 4}/week
Session length: {session_duration if 'session_duration' in locals() else 60} minutes
Equipment: {', '.join(equipment) if 'equipment' in locals() and equipment else 'Basic equipment'}
Goal: {general_goal}

Provide:
1. 5-7 position-specific drills
2. Clear instructions and diagrams (text description)
3. Progression methods
4. Common mistakes to avoid
5. Skill benchmarks
6. Competition drills
7. Solo practice variations

Focus on technical and tactical development."""

                elif feature_code == "mobility_workout":
                    prompt += f"""Create a post-injury mobility and flexibility program:
Injury history: {injury_history if 'injury_history' in locals() else 'General recovery'}
Current status: {injury_severity if 'injury_severity' in locals() else 'Maintenance'}
Goal: {general_goal}

Provide:
1. Daily mobility routine (15-20 minutes)
2. Joint-specific exercises
3. Flexibility progressions
4. Myofascial release techniques
5. Movement quality assessments
6. Long-term injury prevention exercises
7. When to progress to full training

Focus on safe, gradual progression."""

                # Generate response
                generation_config = genai.types.GenerationConfig(
                    temperature=temperature,
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=2048,
                )
                
                response = model.generate_content(prompt, generation_config=generation_config)
                
                # Display results
                st.success("✅ Your personalized coaching plan is ready!")
                
                # Output box
                st.markdown('<div class="output-box">', unsafe_allow_html=True)
                st.markdown(response.text)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Save to history
                st.session_state.history.append({
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'feature': selected_feature,
                    'sport': sport,
                    'position': position,
                    'response': response.text
                })
                
                # Download option
                st.download_button(
                    label="📥 Download Coaching Plan",
                    data=response.text,
                    file_name=f"coachbot_{feature_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
                
                # Feedback
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("👍 Helpful"):
                        st.success("Thank you for your feedback!")
                with col2:
                    if st.button("👎 Not Helpful"):
                        st.info("We'll work on improving!")
                with col3:
                    if st.button("🔄 Generate Again"):
                        st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error generating coaching plan: {str(e)}")
                st.info("Please check your API key configuration and try again.")
    
    # History section
    if st.session_state.history:
        st.markdown("---")
        with st.expander("📚 View Coaching History"):
            for idx, item in enumerate(reversed(st.session_state.history)):
                st.markdown(f"**{item['timestamp']}** - {item['feature']}")
                st.markdown(f"*{item['sport']} - {item['position']}*")
                with st.container():
                    st.text(item['response'][:200] + "..." if len(item['response']) > 200 else item['response'])
                st.markdown("---")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p><strong>CoachBot AI</strong> - Empowering Youth Athletes with AI-Driven Coaching</p>
    <p>🏆 NextGen Sports Lab | Bridging the Coaching Gap with Technology</p>
    <p style='font-size: 0.9rem;'>⚠️ Always consult with a qualified coach or healthcare provider before starting any new training program.</p>
</div>
""", unsafe_allow_html=True)
