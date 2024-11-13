import streamlit as st
from openai import OpenAI
import time
from io import BytesIO
import qrcode

# Page config
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

# Background images from GitHub
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
    1: {
        "name": "name",
        "label": "სახელი",
        "type": "text",
        "placeholder": "შეიყვანეთ თქვენი სახელი..."
    },
    2: {
        "name": "gender",
        "label": "სქესი",
        "type": "text",
        "placeholder": "შეიყვანეთ თქვენი სქესი..."
    },
    3: {
        "name": "age",
        "label": "ასაკი",
        "type": "number",
        "placeholder": "შეიყვანეთ თქვენი ასაკი..."
    },
    4: {
        "name": "profession",
        "label": "პროფესია",
        "type": "text",
        "placeholder": "შეიყვანეთ თქვენი პროფესია..."
    },
    5: {
        "name": "hobby",
        "label": "ჰობი",
        "type": "text",
        "placeholder": "შეიყვანეთ თქვენი ჰობი..."
    },
    6: {
        "name": "style",
        "label": "სტილი",
        "type": "text",
        "placeholder": "შეიყვანეთ სასურველი სტილი..."
    }
}

def set_background(step):
    """Set the background image for the current step"""
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url({BACKGROUNDS[step]});
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Custom styling
st.markdown("""
    <style>
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Form container */
    .form-container {
        padding: 2rem;
        max-width: 600px;
        margin: 4rem auto;
    }

    /* Progress line */
    .progress-line {
        height: 2px;
        background: rgba(255, 255, 255, 0.1);
        margin-bottom: 3rem;
        position: relative;
    }

    .progress-line-fill {
        position: absolute;
        height: 100%;
        background: linear-gradient(90deg, #FF9A9E, #FAD0C4);
        transition: width 0.3s ease;
    }

    /* Input field */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        background-color: rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
        border-radius: 8px;
        padding: 1rem;
        font-size: 1rem;
        width: 100%;
    }

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: rgba(255, 154, 158, 0.5);
        box-shadow: none;
    }

    /* Custom button container */
    .button-container {
        display: grid;
        grid-template-columns: 1fr auto 1fr;
        gap: 1rem;
        align-items: center;
        margin-top: 2rem;
    }

    /* Back and Next buttons (with frame) */
    .framed-button {
        background: linear-gradient(45deg, #FF9A9E, #FAD0C4);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        width: 100%;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    /* Skip button (without frame) */
    .skip-button {
        background: transparent;
        color: #FF9A9E;
        border: none;
        padding: 0.75rem 2rem;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
    }

    /* Step indicator */
    .step-text {
        color: white;
        font-size: 1.5rem;
        margin-bottom: 1.5rem;
        font-weight: 500;
    }

    /* Label */
    .field-label {
        color: white;
        font-size: 1.25rem;
        margin-bottom: 1rem;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

def display_form_step():
    """Display the current form step with three-button layout"""
    current_step = st.session_state.current_step
    field = FORM_FIELDS[current_step]
    
    # Set background for current step
    set_background(current_step)
    
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    
    # Progress line
    progress_width = (current_step - 1) / 5 * 100
    st.markdown(f"""
        <div class="progress-line">
            <div class="progress-line-fill" style="width: {progress_width}%"></div>
        </div>
    """, unsafe_allow_html=True)
    
    # Step indicator and label
    st.markdown(f'<div class="step-text">Step {current_step}/6</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="field-label">{field["label"]}</div>', unsafe_allow_html=True)
    
    # Input field
    if field["type"] == "number":
        value = st.number_input(
            field["label"],
            min_value=0,
            max_value=120,
            label_visibility="collapsed",
            placeholder=field["placeholder"]
        )
    else:
        value = st.text_input(
            field["label"],
            label_visibility="collapsed",
            placeholder=field["placeholder"]
        )
    
    # Custom button layout using HTML/CSS
    st.markdown("""
        <div class="button-container">
            <button onclick="goBack()" class="framed-button">Back</button>
            <button onclick="skipStep()" class="skip-button">Skip</button>
            <button onclick="goNext()" class="framed-button">Next</button>
        </div>
    """, unsafe_allow_html=True)

    # Hidden buttons for Streamlit state management
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if current_step > 1 and st.button("Back", key="back_button", use_container_width=True):
            st.session_state.current_step -= 1
            st.experimental_rerun()
    
    with col2:
        if st.button("Skip", key="skip_button", use_container_width=True):
            if current_step < 6:
                st.session_state.current_step += 1
                st.experimental_rerun()
    
    with col3:
        if st.button("Next", key="next_button", use_container_width=True):
            if value:
                st.session_state.user_data[field["name"]] = value
            if current_step < 6:
                st.session_state.current_step += 1
                st.experimental_rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

    # JavaScript for button interactions
    st.markdown("""
        <script>
        function goBack() {
            document.querySelector('button[key="back_button"]').click();
        }
        
        function skipStep() {
            document.querySelector('button[key="skip_button"]').click();
        }
        
        function goNext() {
            document.querySelector('button[key="next_button"]').click();
        }
        </script>
    """, unsafe_allow_html=True)

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
