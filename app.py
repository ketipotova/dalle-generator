import streamlit as st
from openai import OpenAI
import time
from io import BytesIO
import qrcode

# Must be the first Streamlit command
st.set_page_config(
    page_title="AI სურათების გენერატორი",
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'api_key' not in st.session_state:
    st.session_state.api_key = ''
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'history' not in st.session_state:
    st.session_state.history = []

# Background images for each step
BACKGROUNDS = {
    1: "https://github.com/ketipotova/dalle-generator/blob/main/1.png?raw=true",
    2: "https://github.com/ketipotova/dalle-generator/blob/main/2.png?raw=true",
    3: "https://github.com/ketipotova/dalle-generator/blob/main/3.png?raw=true",
    4: "https://github.com/ketipotova/dalle-generator/blob/main/5.png?raw=true",
    5: "https://github.com/ketipotova/dalle-generator/blob/main/6.png?raw=true",
    6: "https://github.com/ketipotova/dalle-generator/blob/main/6915f1b7-b2e3-4f12-8dde-18b09a0869fd.png?raw=true"
}

# Form fields configuration
FORM_FIELDS = {
    1: {"name": "name", "label": "სახელი", "type": "text"},
    2: {"name": "gender", "label": "სქესი", "type": "text"},
    3: {"name": "age", "label": "ასაკი", "type": "number"},
    4: {"name": "profession", "label": "პროფესია", "type": "text"},
    5: {"name": "hobby", "label": "ჰობი", "type": "text"},
    6: {"name": "style", "label": "სტილი", "type": "text"}
}

# Custom styling
st.markdown("""
    <style>
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Base theme */
    .stApp {
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        min-height: 100vh;
    }

    /* Form container */
    .form-container {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        max-width: 500px;
        margin: 2rem auto;
    }

    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(45deg, #FF9A9E, #FAD0C4);
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #FF9A9E, #FAD0C4);
        color: #1a1a2e;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 10px;
        font-weight: bold;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(255, 154, 158, 0.4);
    }

    /* Input styling */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.1);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        padding: 0.75rem 1rem;
    }

    .stNumberInput > div > div > input {
        background: rgba(255, 255, 255, 0.1);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        padding: 0.75rem 1rem;
    }
    </style>
""", unsafe_allow_html=True)

def set_background(step):
    """Set the background image for the current step"""
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url({BACKGROUNDS[step]});
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def next_step():
    """Advance to the next step"""
    if st.session_state.current_step < 6:
        st.session_state.current_step += 1

def skip_step():
    """Skip the current step"""
    if st.session_state.current_step < 6:
        st.session_state.current_step += 1

def display_form_step():
    """Display the current form step"""
    current_step = st.session_state.current_step
    field = FORM_FIELDS[current_step]
    
    # Set background for current step
    set_background(current_step)
    
    # Display progress
    progress = current_step / 6
    st.progress(progress)
    
    st.markdown(f'<div class="form-container">', unsafe_allow_html=True)
    
    # Title
    st.title(f"Step {current_step}/6")
    st.subheader(field["label"])
    
    # Input field
    if field["type"] == "number":
        value = st.number_input(
            field["label"],
            min_value=0,
            max_value=120,
            label_visibility="collapsed"
        )
    else:
        value = st.text_input(
            field["label"],
            label_visibility="collapsed"
        )
    
    # Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Next", use_container_width=True):
            if value:  # Save value if provided
                st.session_state.user_data[field["name"]] = value
            next_step()
            st.experimental_rerun()
    
    with col2:
        if st.button("Skip", use_container_width=True):
            skip_step()
            st.experimental_rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main application function"""
    if not st.session_state.api_key:
        st.title("შეიყვანეთ თქვენი OpenAI API გასაღები")
        api_key_input = st.text_input("API გასაღები", type="password")
        if api_key_input:
            st.session_state.api_key = api_key_input
            st.experimental_rerun()
    else:
        display_form_step()

if __name__ == "__main__":
    main()
