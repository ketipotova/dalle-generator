import streamlit as st
from openai import OpenAI
import time
import qrcode
from io import BytesIO
import base64
from PIL import Image
import requests

# Must be the first Streamlit command
st.set_page_config(
    page_title="AI სურათების გენერატორი",
    page_icon="🎨",
    layout="centered",  # Using centered layout
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'api_key' not in st.session_state:
    st.session_state.api_key = ''
if 'page' not in st.session_state:
    st.session_state.page = 'input'
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'history' not in st.session_state:
    st.session_state.history = []

# API Key input
if not st.session_state.api_key:
    st.title("შეიყვანეთ თქვენი OpenAI API გასაღები")
    st.write("გთხოვთ, შეიყვანეთ თქვენი OpenAI API გასაღები პროგრამის გასაგრძელებლად.")
    api_key_input = st.text_input("API გასაღები", type="password")
    if api_key_input:
        st.session_state.api_key = api_key_input
        st.experimental_rerun()
else:
    # Initialize OpenAI client with the provided API key
    client = OpenAI(
        api_key=st.session_state.api_key
    )

    # Custom styling
    st.markdown("""
        <style>
        /* Hide Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Control width and padding */
        .block-container {
            max-width: 1000px !important;
            padding-top: 1rem !important;
            padding-bottom: 0rem !important;
        }

        /* Base theme */
        .stApp {
            background: linear-gradient(150deg, #1a1a2e 0%, #16213e 100%);
            color: white;
        }

        /* Container styling */
        .input-container, .generation-container {
            background: rgba(255, 255, 255, 0.05);
            padding: 2rem;
            border-radius: 20px;
            backdrop-filter: blur(10px);
            margin: 1rem auto;
            max-width: 900px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        /* Feature container */
        .feature-container {
            background: rgba(255, 255, 255, 0.08);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
        }

        /* Input styling */
        .stTextInput > div > div > input {
            background: rgba(255, 255, 255, 0.07);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 0.75rem 1rem;
        }

        /* Select box styling */
        .stSelectbox > div > div {
            background: rgba(255, 255, 255, 0.07);
            border-radius: 10px;
            color: white !important;
        }

        /* Button styling */
        .stButton > button {
            background: linear-gradient(45deg, #FF9A9E, #FAD0C4);
            color: #1a1a2e;
            border: none;
            padding: 0.75rem 2rem;
            border-radius: 10px;
            font-weight: bold;
            width: 100%;
            transition: all 0.3s ease;
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(255, 154, 158, 0.4);
        }

        /* QR container */
        .qr-container {
            background: white;
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            margin: 1rem auto;
            max-width: 250px;
        }

        /* Instructions container */
        .instructions-container {
            background: rgba(255, 255, 255, 0.08);
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1rem auto;
        }

        /* Progress bar */
        .stProgress > div > div > div {
            background: linear-gradient(45deg, #FF9A9E, #FAD0C4);
        }

        /* Responsive images */
        img {
            max-width: 100%;
            height: auto;
        }

        /* Header styling */
        .header {
            text-align: center;
            margin-bottom: 2rem;
        }

        /* Make columns more compact */
        .stColumn {
            padding: 0 0.5rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # Data structures
    hobbies = {
        "სპორტი": {
            "ფეხბურთი": "football",
            "კალათბურთი": "basketball",
            "ჭადრაკი": "chess",
            "ცურვა": "swimming",
            "იოგა": "yoga",
            "ჩოგბურთი": "tennis",
            "სირბილი": "running"
        },
        "ხელოვნება": {
            "ხატვა": "painting",
            "მუსიკა": "music",
            "ცეკვა": "dancing",
            "ფოტოგრაფია": "photography",
            "კერამიკა": "ceramics",
            "ქარგვა": "embroidery"
        },
        "ტექნოლოგია": {
            "პროგრამირება": "programming",
            "გეიმინგი": "gaming",
            "რობოტიკა": "robotics",
            "3D მოდელირება": "3D modeling",
            "AI": "artificial intelligence"
        },
        "ბუნება": {
            "მებაღეობა": "gardening",
            "ლაშქრობა": "hiking",
            "კემპინგი": "camping",
            "ალპინიზმი": "mountain climbing"
        }
    }

    colors = {
        "წითელი": "red",
        "ლურჯი": "blue",
        "მწვანე": "green",
        "ყვითელი": "yellow",
        "იისფერი": "purple",
        "ოქროსფერი": "gold",
        "ვერცხლისფერი": "silver",
        "ცისფერი": "light blue"
    }

    styles = {
        "რეალისტური": "realistic",
        "ფანტასტიკური": "fantastic",
        "მულტიპლიკაციური": "cartoon",
        "ანიმე": "anime",
        "იმპრესიონისტული": "impressionistic"
    }

    moods = {
        "მხიარული": "cheerful",
        "მშვიდი": "peaceful",
        "ენერგიული": "energetic",
        "რომანტიული": "romantic",
        "სათავგადასავლო": "adventurous",
        "ნოსტალგიური": "nostalgic"
    }

    filters = {
        "ბუნებრივი": "natural",
        "რეტრო": "retro",
        "დრამატული": "dramatic",
        "ნათელი": "bright",
        "კონტრასტული": "high contrast"
    }

    # Helper Functions
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

    def translate_user_data(user_data):
        """Translate Georgian user data to English"""
        return {
            "name": user_data['name'],
            "age": user_data['age'],
            "hobby": hobbies[user_data['hobby_category']][user_data['hobby']],
            "color": colors[user_data['color']],
            "style": styles[user_data['style']],
            "mood": moods[user_data['mood']],
            "filter": filters[user_data['filter']]
        }

    def create_personalized_prompt(user_data):
        """Create a personalized English prompt based on translated user information"""
        try:
            eng_data = translate_user_data(user_data)

            prompt_request = f"""
            Create a detailed image prompt for a {eng_data['age']}-year-old named {eng_data['name']} 
            who loves {eng_data['hobby']}. 

            Key elements to incorporate:
            - Favorite color: {eng_data['color']}
            - Visual style: {eng_data['style']}
            - Mood: {eng_data['mood']}
            - Filter effect: {eng_data['filter']}

            Create a personalized, artistic scene that captures their interests and personality.
            Focus on cinematic composition, dramatic lighting, and high-quality details.
            Make it engaging and suitable for an expo demonstration.
            Ensure the image is family-friendly and appropriate for all ages.
            """

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system",
                     "content": "You are an expert at crafting detailed image generation prompts. Focus on creating vivid, specific descriptions that work well with DALL-E 3."},
                    {"role": "user", "content": prompt_request}
                ],
                temperature=0.7
            )

            english_prompt = response.choices[0].message.content

            georgian_summary = f"""🎨 რას ვქმნით: 
            პერსონალიზებული სურათი {user_data['name']}-სთვის
            • ჰობი: {user_data['hobby']}
            • სტილი: {user_data['style']}
            • განწყობა: {user_data['mood']}
            • ფილტრი: {user_data['filter']}
            """

            return english_prompt, georgian_summary

        except Exception as e:
            st.error(f"შეცდომა პრომპტის შექმნისას: {str(e)}")
            return None, None

    def generate_dalle_image(prompt):
        """Generate image using DALL-E 3"""
        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1792x1024",
                quality="hd",
                style="vivid",
                n=1
            )
            return response.data[0].url
        except Exception as e:
            st.error(f"შეცდომა სურათის გენერაციისას: {str(e)}")
            return None

    def add_to_history(image_url, prompt):
        """Add generated image to history"""
        if len(st.session_state.history) >= 5:
            st.session_state.history.pop(0)

        st.session_state.history.append({
            'url': image_url,
            'prompt': prompt,
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
        })

    def show_error_message(error):
        """Display error message with retry option"""
        st.error(f"შეცდომა: {str(error)}")
        if st.button("🔄 ხელახლა ცდა"):
            st.rerun()

    def validate_inputs(user_data):
        """Validate user inputs before processing"""
        if not user_data.get('name'):
            return False, "გთხოვთ შეიყვანოთ სახელი"
        if not user_data.get('hobby'):
            return False, "გთხოვთ აირჩიოთ ჰობი"
        return True, ""

    def show_history():
        """Display history of generated images"""
        if st.session_state.history:
            with st.expander("🕒 წინა სურათები"):
                for item in reversed(st.session_state.history):
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(item['url'], width=200)
                    with col2:
                        st.markdown(f"**დრო:** {item['timestamp']}")
                        st.markdown(f"**აღწერა:** {item['prompt'][:100]}...")
                    st.markdown("---")

    def display_input_page():
        """Display the input form page"""
        st.markdown('<div class="input-container">', unsafe_allow_html=True)

        # Create two rows with four columns each
        row1_col1, row1_col2, row1_col3, row1_col4 = st.columns(4)
        row2_col1, row2_col2, row2_col3, row2_col4 = st.columns(4)

        with row1_col1:
            st.markdown('<div class="feature-container">', unsafe_allow_html=True)
            st.markdown('<p class="feature-label">👤 სახელი</p>', unsafe_allow_html=True)
            name = st.text_input("", placeholder="მაგ: გიორგი", label_visibility="collapsed", key="name_input")
            st.markdown('</div>', unsafe_allow_html=True)

        with row1_col2:
            st.markdown('<div class="feature-container">', unsafe_allow_html=True)
            st.markdown('<p class="feature-label">🎂 ასაკი</p>', unsafe_allow_html=True)
            age = st.number_input("", min_value=5, max_value=100, value=25, label_visibility="collapsed", key="age_input")
            st.markdown('</div>', unsafe_allow_html=True)

        with row1_col3:
            st.markdown('<div class="feature-container">', unsafe_allow_html=True)
            st.markdown('<p class="feature-label">🎯 კატეგორია</p>', unsafe_allow_html=True)
            hobby_category = st.selectbox("", list(hobbies.keys()), label_visibility="collapsed", key="category_input")
            st.markdown('</div>', unsafe_allow_html=True)

        with row1_col4:
            st.markdown('<div class="feature-container">', unsafe_allow_html=True)
            st.markdown('<p class="feature-label">🎨 ჰობი</p>', unsafe_allow_html=True)
            hobby = st.selectbox("", list(hobbies[hobby_category].keys()), label_visibility="collapsed", key="hobby_input")
            st.markdown('</div>', unsafe_allow_html=True)

        with row2_col1:
            st.markdown('<div class="feature-container">', unsafe_allow_html=True)
            st.markdown('<p class="feature-label">🎨 ფერი</p>', unsafe_allow_html=True)
            color = st.selectbox("", list(colors.keys()), label_visibility="collapsed", key="color_input")
            st.markdown('</div>', unsafe_allow_html=True)

        with row2_col2:
            st.markdown('<div class="feature-container">', unsafe_allow_html=True)
            st.markdown('<p class="feature-label">🖼️ სტილი</p>', unsafe_allow_html=True)
            style = st.selectbox("", list(styles.keys()), label_visibility="collapsed", key="style_input")
            st.markdown('</div>', unsafe_allow_html=True)

        with row2_col3:
            st.markdown('<div class="feature-container">', unsafe_allow_html=True)
            st.markdown('<p class="feature-label">😊 განწყობა</p>', unsafe_allow_html=True)
            mood = st.selectbox("", list(moods.keys()), label_visibility="collapsed", key="mood_input")
            st.markdown('</div>', unsafe_allow_html=True)

        with row2_col4:
            st.markdown('<div class="feature-container">', unsafe_allow_html=True)
            st.markdown('<p class="feature-label">🌈 ფილტრი</p>', unsafe_allow_html=True)
            filter_effect = st.selectbox("", list(filters.keys()), label_visibility="collapsed", key="filter_input")
            st.markdown('</div>', unsafe_allow_html=True)

        # Generate button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("✨ შექმენი სურათი", use_container_width=True):
                if not name:
                    st.error("გთხოვთ შეიყვანოთ სახელი")
                    return

                st.session_state.user_data = {
                    "name": name,
                    "age": age,
                    "hobby_category": hobby_category,
                    "hobby": hobby,
                    "color": color,
                    "style": style,
                    "mood": mood,
                    "filter": filter_effect
                }
                st.session_state.page = 'generate'
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    def display_generation_page():
        """Display the image generation and result page"""
        st.markdown('<div class="generation-container">', unsafe_allow_html=True)

        with st.spinner("🎨 ვქმნით შენთვის უნიკალურ სურათს..."):
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)

            english_prompt, georgian_summary = create_personalized_prompt(st.session_state.user_data)
            if english_prompt and georgian_summary:
                st.markdown("#### 🔮 სურათის დეტალები:")
                st.markdown(georgian_summary)

                with st.expander("🔍 სრული აღწერა"):
                    st.markdown(f"*{english_prompt}*")

                image_url = generate_dalle_image(english_prompt)
                if image_url:
                    add_to_history(image_url, english_prompt)

                    st.success("✨ თქვენი სურათი მზადაა!")
                    st.image(image_url, caption="შენი პერსონალური AI სურათი", use_column_width=True)

                    qr_col1, qr_col2 = st.columns([1, 2])
                    with qr_col1:
                        st.markdown('<div class="qr-container">', unsafe_allow_html=True)
                        qr_code = create_qr_code(image_url)
                        if qr_code:
                            st.image(qr_code, width=200)
                            st.markdown("📱 დაასკანერე QR კოდი")
                        st.markdown('</div>', unsafe_allow_html=True)

                    with qr_col2:
                        st.markdown('<div class="instructions-container">', unsafe_allow_html=True)
                        st.markdown("""
                            ### 📱 როგორ გადმოვწერო:
                            1. გახსენი ტელეფონის კამერა
                            2. დაასკანერე QR კოდი
                            3. გადმოწერე სურათი
                        """)
                        st.markdown('</div>', unsafe_allow_html=True)

                    # Download and new image buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(
                            f'<a href="{image_url}" download="ai_image.png" '
                            f'target="_blank"><button style="width:100%">📥 გადმოწერა</button></a>',
                            unsafe_allow_html=True
                        )
                    with col2:
                        if st.button("🔄 ახალი სურათი"):
                            st.session_state.page = 'input'
                            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    def main():
        """Main application function"""
        try:
            # Display header with minimal padding
            st.markdown(
                '<div class="header" style="padding: 1rem 0;">',
                unsafe_allow_html=True
            )
            # Title and subtitle
            st.title("🎨 AI სურათების გენერატორი")
            st.markdown("### შექმენი შენი უნიკალური სურათი")
            st.markdown('</div>', unsafe_allow_html=True)

            # Display appropriate page based on state
            if st.session_state.page == 'input':
                display_input_page()
                show_history()
            else:
                display_generation_page()

            # Add minimal footer
            st.markdown(
                """
                <div style='text-align: center; color: rgba(255,255,255,0.5); 
                     padding: 1rem 0; font-size: 0.8rem; margin-top: 2rem;'>
                შექმნილია ❤️-ით DALL-E 3-ის გამოყენებით
                </div>
                """,
                unsafe_allow_html=True
            )

        except Exception as e:
            show_error_message(e)

    # Main execution
    if __name__ == "__main__":
        main()
