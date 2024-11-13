import streamlit as st
from openai import OpenAI
import time
from io import BytesIO
import qrcode
import requests
from PIL import Image

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
if 'generated_image' not in st.session_state:
    st.session_state.generated_image = None

# Background images from GitHub
BACKGROUNDS = {
    1: "https://github.com/ketipotova/dalle-generator/blob/main/1.png?raw=true",
    2: "https://github.com/ketipotova/dalle-generator/blob/main/2.png?raw=true",
    3: "https://github.com/ketipotova/dalle-generator/blob/main/3.png?raw=true",
    4: "https://github.com/ketipotova/dalle-generator/blob/main/5.png?raw=true",
    5: "https://github.com/ketipotova/dalle-generator/blob/main/6.png?raw=true",
    6: "https://github.com/ketipotova/dalle-generator/blob/main/6915f1b7-b2e3-4f12-8dde-18b09a0869fd.png?raw=true"
}

# Frame image URL
FRAME_URL = "https://github.com/ketipotova/dalle-generator/blob/main/frame.jpeg?raw=true"

# Form fields configuration
FORM_FIELDS = {
    1: {"name": "name", "label": "სახელი", "type": "text"},
    2: {"name": "gender", "label": "სქესი", "type": "text"},
    3: {"name": "age", "label": "ასაკი", "type": "number"},
    4: {"name": "profession", "label": "პროფესია", "type": "text"},
    5: {"name": "hobby", "label": "ჰობი", "type": "text"},
    6: {"name": "style", "label": "სტილი", "type": "text"}
}

def create_dalle_prompt(user_data):
    """Create a detailed prompt for DALL-E using GPT-4"""
    client = OpenAI(api_key=st.session_state.api_key)
    
    prompt_request = f"""
    Create a detailed image generation prompt based on this information:
    - Name: {user_data.get('name', '')}
    - Gender: {user_data.get('gender', '')}
    - Age: {user_data.get('age', '')}
    - Profession: {user_data.get('profession', '')}
    - Hobby: {user_data.get('hobby', '')}
    - Preferred style: {user_data.get('style', '')}

    Requirements:
    1. Create a cinematic, visually striking scene
    2. The image should be optimized for 9:16 aspect ratio (portrait orientation)
    3. Include dramatic lighting and atmospheric elements
    4. Make it personal and specific to the individual
    5. Focus on high-quality, detailed visuals
    6. Keep it family-friendly and appropriate
    7. Leave space around the edges for a frame

    Return only the prompt text, no explanations.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert at crafting detailed image generation prompts."},
                {"role": "user", "content": prompt_request}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error generating prompt: {str(e)}")
        return None

def generate_image(prompt):
    """Generate image using DALL-E 3"""
    try:
        client = OpenAI(api_key=st.session_state.api_key)
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1792",  # 9:16 ratio
            quality="hd",
            n=1
        )
        return response.data[0].url
    except Exception as e:
        st.error(f"Error generating image: {str(e)}")
        return None

def add_frame_to_image(image_url):
    """Add frame to the generated image"""
    try:
        # Download the generated image
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        
        # Download the frame
        frame_response = requests.get(FRAME_URL)
        frame = Image.open(BytesIO(frame_response.content))
        
        # Resize frame to match the image dimensions
        frame = frame.resize(img.size)
        
        # Create a new image with the same size and mode
        final_image = Image.new('RGBA', img.size)
        
        # Paste the original image
        final_image.paste(img, (0, 0))
        
        # Paste the frame on top
        final_image.paste(frame, (0, 0), frame if frame.mode == 'RGBA' else None)
        
        # Save to BytesIO
        buffered = BytesIO()
        final_image.save(buffered, format="PNG")
        return buffered.getvalue()
    except Exception as e:
        st.error(f"Error adding frame: {str(e)}")
        return None

def create_qr_code(url):
    """Create a QR code for the given URL"""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        qr_image.save(buffered, format="PNG")
        return buffered.getvalue()
    except Exception as e:
        st.error(f"QR კოდის შექმნის შეცდომა: {str(e)}")
        return None

# Custom CSS
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
    }

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

    /* Input fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        background-color: rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
        border-radius: 8px;
        padding: 1rem;
        font-size: 1rem;
    }

    /* Button styles */
    .stButton > button {
        width: 100%;
        border: none;
        padding: 0.75rem 2rem;
        cursor: pointer;
        font-weight: 500;
        border-radius: 8px;
    }

    /* Back and Next buttons */
    .back-button > button,
    .next-button > button {
        background: linear-gradient(45deg, #FF9A9E, #FAD0C4) !important;
        color: white !important;
    }

    /* Skip button */
    .skip-button > button {
        background: transparent !important;
        color: #FF9A9E !important;
    }

    /* Text styles */
    .step-text {
        color: white;
        font-size: 1.5rem;
        margin-bottom: 1.5rem;
        font-weight: 500;
    }

    .field-label {
        color: white;
        font-size: 1.25rem;
        margin-bottom: 1rem;
        font-weight: 500;
    }

    /* Generated image container */
    .generated-image {
        padding: 20px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        margin: 2rem auto;
        max-width: 90%;
    }

    /* QR container */
    .qr-container {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem auto;
        max-width: 200px;
        text-align: center;
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

def display_form_step():
    """Display the current form step"""
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
            key=f"input_{current_step}"
        )
    else:
        value = st.text_input(
            field["label"],
            label_visibility="collapsed",
            key=f"input_{current_step}"
        )

    # Button layout with proper styling
    cols = st.columns([1, 0.7, 1])
    
    # Back button
    with cols[0]:
        if current_step > 1:
            back = st.button("Back", key="back", use_container_width=True)
            if back:
                st.session_state.current_step -= 1
                st.rerun()
    
    # Skip button
    with cols[1]:
        skip = st.button("Skip", key="skip", use_container_width=True)
        if skip and current_step < 6:
            st.session_state.current_step += 1
            st.rerun()
    
    # Next button
    with cols[2]:
        next = st.button("Next", key="next", use_container_width=True)
        if next:
            if value:
                st.session_state.user_data[field["name"]] = value
            if current_step < 6:
                st.session_state.current_step += 1
                st.rerun()
            elif current_step == 6:
                # Generate image on final step
                prompt = create_dalle_prompt(st.session_state.user_data)
                if prompt:
                    image_url = generate_image(prompt)
                    if image_url:
                        # Add frame to the image
                        framed_image = add_frame_to_image(image_url)
                        if framed_image:
                            st.markdown('<div class="generated-image">', unsafe_allow_html=True)
                            st.image(framed_image, caption="Your AI-generated image")
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # QR Code
                            qr_code = create_qr_code(image_url)
                            if qr_code:
                                st.markdown('<div class="qr-container">', unsafe_allow_html=True)
                                st.image(qr_code, caption="Scan to download")
                                st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main application function"""
    if not st.session_state.api_key:
        st.title("შეიყვანეთ თქვენი OpenAI API გასაღები")
        api_key_input = st.text_input("API გასაღები", type="password")
        if api_key_input:
            st.session_state.api_key = api_key_input
            st.rerun()
    else:
        display_form_step()

if __name__ == "__main__":
    main()
