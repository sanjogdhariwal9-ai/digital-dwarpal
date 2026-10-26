import streamlit as st
from streamlit_mic_recorder import mic_recorder
from google import genai
from PIL import Image
from gtts import gTTS
import os

# 1. Page Configuration & Theme Settings
st.set_page_config(
    page_title="Digital Dwarpal - AI School Receptionist", 
    page_icon="🏫", 
    layout="centered"
)

# Custom CSS for clean UI styling
st.markdown("""
    <style>
    .stButton button {
        border-radius: 8px;
        font-weight: 500;
    }
    .stChatInputContainer {
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Session state initialization
if "school_info" not in st.session_state:
    st.session_state.school_info = {
        "school_name": "Delhi Public School",
        "principal": "Dr. Sharma",
        "timings": "8:00 AM to 2:00 PM",
        "directory": "Math Dept: Mr. Verma, Science Dept: Dr. Khan",
        "admission_fees": "Admission Fee: Rs. 5,000, Tuition Fee: Rs. 2,000 per month",
        "documents": "Birth Certificate, Aadhar Card, Previous Marksheet, Transfer Certificate (TC)",
        "timetable": "Class 6 to 8 (Sections A, B): Period 1-Math, Period 2-Science. Class 9 to 12: Period 1-Physics.",
        "incharges": "Class 6A: Mrs. Sharma, Class 10A: Mr. Verma, Class 12A: Mr. Kapoor",
        "app_icon": "🏫",
        "voice_lang": "hi"
    }

if "messages_box" not in st.session_state:
    st.session_state.messages_box = []

# 2. Sidebar - Developer Panel & Gemini API Key Configuration
with st.sidebar:
    st.header("⚙️ Developer & Admin Panel")
    st.write("Secure login for school management & API setup.")
    
    st.subheader("🔑 Gemini API Key Setup")
    
    # 3. Automatic / Manual Client Setup using new genai.Client
    client = None
    try:
        if "GEMINI_API_KEY" in st.secrets:
            client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    except Exception:
        pass

    user_api_key = st.text_input("Enter Gemini API Key (Optional if in secrets):", type="password", value="")
    
    if user_api_key:
        client = genai.Client(api_key=user_api_key)
        st.success("✅ API Key Configured!")
    elif client:
        st.success("✅ Loaded API Key from Secrets!")
    else:
        st.warning("⚠️ Please enter your Gemini API Key below to activate AI responses.")

    st.markdown("---")
    admin_password = st.text_input("Enter Developer Password:", type="password")
    
    if admin_password == "sanjog_dhariwal":
        st.success("✅ Admin Access Granted!")
        st.markdown("---")
        
        st.subheader("Edit School Info & Settings")
        new_school_name = st.text_input("School Name", value=st.session_state.school_info["school_name"])
        new_icon = st.text_input("App Icon / Emoji", value=st.session_state.school_info["app_icon"])
        new_principal = st.text_input("Principal Name", value=st.session_state.school_info["principal"])
        new_timings = st.text_input("School Timings", value=st.session_state.school_info["timings"])
        new_directory = st.text_area("Teachers Directory", value=st.session_state.school_info["directory"])
        new_fees = st.text_area("Admission & Fees Structure", value=st.session_state.school_info["admission_fees"])
        new_docs = st.text_area("Required Documents", value=st.session_state.school_info["documents"])
        new_timetable = st.text_area("Timetable & Sections", value=st.session_state.school_info["timetable"])
        new_incharges = st.text_area("Class Incharges", value=st.session_state.school_info["incharges"])
        
        new_voice = st.selectbox("AI Voice Language", ["hi (Hindi)", "en (English)"], index=0 if st.session_state.school_info["voice_lang"]=="hi" else 1)
        
        if st.button("Save Changes"):
            st.session_state.school_info["school_name"] = new_school_name
            st.session_state.school_info["app_icon"] = new_icon
            st.session_state.school_info["principal"] = new_principal
            st.session_state.school_info["timings"] = new_timings
            st.session_state.school_info["directory"] = new_directory
            st.session_state.school_info["admission_fees"] = new_fees
            st.session_state.school_info["documents"] = new_docs
            st.session_state.school_info["timetable"] = new_timetable
            st.session_state.school_info["incharges"] = new_incharges
            st.session_state.school_info["voice_lang"] = "hi" if "Hindi" in new_voice else "en"
            st.success("Settings updated successfully!")
            st.rerun()
            
        st.markdown("---")
        st.subheader("📥 Visitor Inbox Stats")
        st.metric("Total Messages / Feedback", len(st.session_state.messages_box))
        
    elif admin_password != "":
        st.error("❌ Incorrect Password!")
    else:
        st.info("🔒 Enter password to unlock admin panel.")

# Dynamic System Instruction
current_info = st.session_state.school_info
secure_system_instruction = f"""
You are "Digital Dwarpal", the official Digital Receptionist AI for {current_info['school_name']}. 
- Principal Name: {current_info['principal']}
- Timings: {current_info['timings']}
- Teachers Directory: {current_info['directory']}
- Admission & Fees: {current_info['admission_fees']}
- Required Documents: {current_info['documents']}
- Timetable: {current_info['timetable']}
- Class Incharges: {current_info['incharges']}

Your Personality & Behavior:
- Extremely friendly, warm, welcoming, and polite like a favorite school guide.
- Use respectful words like "Namaste", "Aapka swagat hai".
- Occasionally include light-hearted, respectful, and sweet school-related jokes or quotes.
- Answer all questions accurately using the provided school details, and also freely answer any general or random questions (science, history, actors, chemistry, etc.) asked by the user.
"""

# 3. UI Header
st.title(f"{current_info['app_icon']} Digital Dwarpal - {current_info['school_name']}")
st.markdown(f"*\"Swagat hai! Main aapka Digital Dwarpal hoon. School ki jankari, class incharges, ya admission ke baare mein puchiye, ya koi bhi sawal kijiye!\"*")
st.write("---")

# 4. Tabs for Chat & Complaint Box
tab1, tab2 = st.tabs(["💬 AI Chat & Map Guide", "📝 Principal Message / Complaint Box"])

with tab1:
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {
                "role": "assistant", 
                "content": f"Namaste ji! Main {current_info['school_name']} ka **Digital Dwarpal** hoon. Aapka yahan swagat hai! 🏫 Bataiye, aaj main aapki kya madad kar sakta hoon?"
            }
        ]

    st.markdown("💡 **Quick Queries:**")
    col1, col2, col3, col4 = st.columns(4)
    quick_query = None
    with col1:
        if st.button("🏫 Timings"): quick_query = "What are the school timings?"
    with col2:
        if st.button("💰 Fees Structure"): quick_query = "What is the admission and fee structure?"
    with col3:
        if st.button("📋 Documents"): quick_query = "What documents are required for admission?"
    with col4:
        if st.button("👨‍🏫 Teachers"): quick_query = "Show me the teachers directory and incharges."

    st.markdown("---")

    # Display chat history safely
    for idx, message in enumerate(st.session_state.chat_messages):
        with st.chat_message(message["role"]):
            if "image" in message and message["image"]:
                st.image(message["image"], caption="Uploaded Map", width=300)
            st.markdown(message["content"])
            
            if message["role"] == "assistant" and idx > 0:
                if st.button("🔊 Listen Audio", key=f"audio_{idx}"):
                    try:
                        tts = gTTS(text=message["content"], lang=current_info['voice_lang'], slow=False)
                        audio_file = "temp_voice.mp3"
                        tts.save(audio_file)
                        st.audio(audio_file, format="audio/mp3", autoplay=True)
                    except Exception:
                        st.error("Audio play karne mein samasya aayi.")

    uploaded_map = st.file_uploader("📂 School ka Map (Image) upload karein (Optional):", type=["jpg", "jpeg", "png"])

    # Input controls layout (Text input + Mic button)
    col_input1, col_input2 = st.columns([6, 1])
    
    with col_input1:
        user_query = st.chat_input("Yahan apna sawaal type karein (Chemistry, Actor ya School ki jankari)...")
    
    with col_input2:
        # Mic recorder button
        audio = mic_recorder(
            start_prompt="🎙️", 
            stop_prompt="⏹️", 
            key='unique_mic_button'
        )

    prompt = None

    if quick_query:
        prompt = quick_query
    elif user_query:
        prompt = user_query
    elif audio:
        st.audio(audio['bytes'])
        prompt = "नमस्ते, मैंने माइक से सवाल पूछा है।"

    if prompt:
        if not client:
            st.error("⚠️ Pehle sidebar mein apni Gemini API Key enter karein!")
        else:
            img = None
            content_to_send = [prompt]
            
            if uploaded_map is not None:
                try:
                    img = Image.open(uploaded_map)
                    content_to_send = [prompt, img]
                except Exception:
                    pass

            # Append user message and display
            st.session_state.chat_messages.append({"role": "user", "content": prompt, "image": img})
            
            with st.chat_message("user"):
                if img:
                    st.image(img, caption="Uploaded Map", width=300)
                st.markdown(prompt)

            with st.spinner("Jawab tyaar kiya ja raha hai..."):
                try:
                    # New google-genai SDK call format with system instruction
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=content_to_send,
                        config={
                            'system_instruction': secure_system_instruction
                        }
                    )
                    bot_reply = response.text
                except Exception as e:
                    bot_reply = f"Kshama karein, takneekee dikkat aa gayi: {e}"

                st.session_state.chat_messages.append({"role": "assistant", "content": bot_reply})
                st.rerun()

    st.markdown("---")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_messages = [st.session_state.chat_messages[0]]
            st.rerun()
    with col_c2:
        chat_transcript = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.chat_messages])
        st.download_button("📥 Download Chat Transcript", chat_transcript, file_name="school_chat_log.txt")

with tab2:
    st.subheader("Principal Sir ke liye Message ya Complaint Darj Karein")
    st.write("Aap yahan apna naam aur message likh sakte hain.")
    
    with st.form("complaint_form"):
        visitor_name = st.text_input("Aapka Naam (Your Name):")
        msg_type = st.selectbox("Type:", ["Message for Principal", "Complaint / Feedback"])
        visitor_text = st.text_area("Apna Message yahan likhein:")
        submit_button = st.form_submit_button("Submit Message")
        
        if submit_button:
            if visitor_name and visitor_text:
                st.session_state.messages_box.append({
                    "name": visitor_name,
                    "type": msg_type,
                    "text": visitor_text
                })
                st.success("Aapka message safaltapurvak bhej diya gaya hai!")
            else:
                st.error("Kripya apna naam aur message dono bharein.")
    
    if len(st.session_state.messages_box) > 0:
        st.markdown("### 📋 Received Messages (Admin View)")
        for idx, msg in enumerate(st.session_state.messages_box, 1):
            st.info(f"**{idx}. {msg['name']} ({msg['type']}):** {msg['text']}")
