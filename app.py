import streamlit as st
import random
import os
import csv
import base64
from PIL import Image

# =========================================================
# 1. DOSYA YOLLARI VE KESİNLİKLE İLK ÇALIŞMASI GEREKEN AYARLAR
# =========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DATASET_PATH = os.path.join(BASE_DIR, "mps.csv")
icon_path = os.path.join(ASSETS_DIR, "demokratiksolparti.png")

# İkon dosyasını güvenli bir şekilde kontrol et ve yükle
if os.path.exists(icon_path):
    try:
        page_icon_image = Image.open(icon_path)
    except Exception:
        page_icon_image = "🏛️"  # Resim açılırken hata verirse emojiye dön
else:
    page_icon_image = "🏛️"  # Dosya bulunamazsa varsayılan emojiye dön

# ÇÖKME OLMAMASI İÇİN STREAMLIT'TE İLK BU KOMUT ÇALIŞMALIDIR!
st.set_page_config(
    page_title="Turkish 1990s Parliament Match", 
    page_icon=page_icon_image, 
    layout="centered"
)

# 2. Define the Dataset (Load portrait metadata from mps.csv and normalize party names)

def normalize_party_name(party_name):
    if party_name is None:
        return ""

    normalized = party_name.strip()
    if not normalized:
        return ""

    alias_map = {
        "fp": "Fazilet",
        "fazilet": "Fazilet",
        "fazilet partisi": "Fazilet",
        "dyp": "True Path",
        "true path": "True Path",
        "true path party": "True Path",
        "doğru yol": "True Path",
        "doğru yol partisi": "True Path",
        "mhp": "MHP",
        "dsp": "DSP",
        "anap": "ANAP",
    }
    return alias_map.get(normalized.lower(), normalized)


if "dataset" not in st.session_state:
    dataset = []
    if os.path.exists(DATASET_PATH):
        with open(DATASET_PATH, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                name = row.get("name", "").strip()
                party = row.get("party", "").strip()
                img = row.get("img", "").strip()
                if name and party and img:
                    dataset.append({
                        "name": name,
                        "party": normalize_party_name(party),
                        "img": img,
                    })

    if not dataset:
        dataset = [
            {"name": "Bülent Ecevit", "party": "DSP", "img": "ecevit.jpg"},
            {"name": "Ahmet Mesut Yılmaz", "party": "ANAP", "img": "mesut yılmaz.jpg"},
            {"name": "Recai Kutan", "party": "Fazilet", "img": "kutan.jpg"},
            {"name": "Tansu Çiller", "party": "True Path", "img": "ciller.jpg"},
            {"name": "Devlet Bahçeli", "party": "MHP", "img": "bahceli.jpg"}
        ]

    random.shuffle(dataset)
    st.session_state.dataset = dataset

# 3. Initialize Game Variables (Keeps track of state across browser refreshes)
if "index" not in st.session_state: st.session_state.index = 0
if "score" not in st.session_state: st.session_state.score = 0
if "trials" not in st.session_state: st.session_state.trials = 0  # Yeni eklenen soru sayacı
if "answered" not in st.session_state: st.session_state.answered = False
if "feedback" not in st.session_state: st.session_state.feedback = ""
if "is_correct" not in st.session_state: st.session_state.is_correct = False
if "recent_guesses" not in st.session_state: st.session_state.recent_guesses = []

# =========================================================
# 3. GÖRSEL VINTAGE CSS TASARIMI VE BAŞLIKLAR
# =========================================================
st.markdown(
    """
    <style>
        .stApp,
        [data-testid="stAppViewContainer"] {
            background-color: #f5f0e6 !important;
        }
        [data-testid="stHeader"] {
            background-color: transparent !important;
        }
        .stMarkdown [data-testid="stMarkdownContainer"] {
            font-family: 'Georgia', 'Times New Roman', serif !important;
        }
        .top-text-wrapper {margin-top: -60px; margin-bottom: 4px; padding-bottom: 0;}
       
        .top-text-wrapper h1 {
            margin-bottom: 0.15rem;
            font-family: 'Cinzel', 'Times New Roman', serif;
            text-transform: uppercase;
            text-align: center;
        }
       
        .top-text-wrapper p {
            margin-top: 0.15rem;
            margin-bottom: 0.15rem;
            font-family: 'Georgia', 'Times New Roman', serif;
            text-align: center;
        }
       
        .button-spacer {margin-top: 24px;}
        [data-testid="stHorizontalBlock"] [data-testid="stButton"] button {
            height: 64px !important;
            min-height: 64px !important;
            padding: 12px 10px !important;
            line-height: 1.2 !important;
            box-sizing: border-box !important;
            font-family: 'Georgia', 'Times New Roman', serif !important;
        }
        [data-testid="stHorizontalBlock"] [data-testid="stButton"] button,
        [data-testid="stHorizontalBlock"] [data-testid="stButton"] button p,
        [data-testid="stHorizontalBlock"] [data-testid="stButton"] button span {
            font-family: 'Georgia', 'Times New Roman', serif !important;
            font-size: 21px !important;
        }
        [data-testid="stAlert"] {
            min-height: 84px !important;
            padding: 1.25rem 1.5rem !important;
            box-sizing: border-box !important;
        }
        [data-testid="stAlert"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stAlert"]:is(:hover, :focus, :focus-within, :active) [data-testid="stMarkdownContainer"] p,
        [data-testid="stAlert"] [data-testid="stMarkdownContainer"]:is(:hover, :focus, :focus-within, :active) p,
        [data-testid="stAlert"] [data-testid="stMarkdownContainer"] p:is(:hover, :focus, :focus-within, :active),
        [data-testid="stAlert"] [data-testid="stMarkdownContainer"] p *,
        [data-testid="stAlert"]:is(:hover, :focus, :focus-within, :active) [data-testid="stMarkdownContainer"] p *,
        [data-testid="stAlert"] [data-testid="stMarkdownContainer"]:is(:hover, :focus, :focus-within, :active) p *,
        [data-testid="stAlert"] [data-testid="stMarkdownContainer"] p *:is(:hover, :focus, :focus-within, :active) {
            font-family: 'Georgia', 'Times New Roman', serif !important;
            color: #2C3E50 !important;
        }
        [data-testid="stAlert"] [data-testid="stMarkdownContainer"] p {
            font-family: 'Georgia', 'Times New Roman', serif !important;
            font-size: 1.2rem !important;
            line-height: 1.5 !important;
        }
        .title {
            font-family: 'Cinzel', 'Times New Roman', serif;
            text-transform: uppercase;
        }
        .menu-item {
            font-family: 'Georgia', 'Times New Roman', serif;
        }
        .counter-text {
            text-align: center;
            color: #566573;
            font-size: 1.1rem;
            margin-bottom: 15px;
            font-weight: bold;
        }
        .end-screen {
            background-color: #FFFFFF;
            padding: 30px;
            border-radius: 8px;
            border: 1px solid #D5F5E3;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
            text-align: center;
            margin-top: 20px;
        }
    </style>
    <div class="top-text-wrapper">
      <h1> 1990s Turkish Parliament Party Match</h1>
      <p>Which party does this MP represent?</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# 4. Main Game Loop (20 Soru sınırına göre çalışır)
if st.session_state.trials < 20 and st.session_state.index < len(st.session_state.dataset):
    current_mp = st.session_state.dataset[st.session_state.index]

    # Kaçıncı soruda olduğunu gösteren canlı sayaç
    st.markdown(f'<div class="counter-text"> {st.session_state.trials + 1} / 20</div>', unsafe_allow_html=True)

    # Render portrait image centered
    img_path = os.path.join(ASSETS_DIR, current_mp["img"])
    if os.path.exists(img_path):
        left_space, middle_col, right_space = st.columns([1, 2, 1])
        with middle_col:
            with open(img_path, "rb") as image_file:
                image_bytes = image_file.read()
            encoded_image = base64.b64encode(image_bytes).decode()
            mime_type = "image/png" if img_path.lower().endswith(".png") else "image/jpeg"
            st.markdown(
                f"""
                <div style="width:240px; height:320px; margin:auto; padding:6px; background:#f0f0f0; border:1px solid #b3b3b3; box-sizing: border-box; overflow:hidden;">
                    <img src="data:{mime_type};base64,{encoded_image}"
                        style="width:100%; height:100%; object-fit:cover; display:block;" />
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.error(f"Image asset missing in your folder: {os.path.relpath(img_path, BASE_DIR)}")
        st.info("Make sure your images are saved in an 'assets' folder and named exactly like the dataset!")

    st.markdown("<div class='button-spacer'></div>", unsafe_allow_html=True)

    # Multi-choice buttons layout
    col1, col2, col3, col4, col5 = st.columns(5)
    parties = ["MHP", "DSP", "Fazilet", "ANAP", "True Path"]
   
    # Check button clicks (disabled once an answer is chosen)
    with col1: MHP_btn = st.button(parties[0], disabled=st.session_state.answered, use_container_width=True)
    with col2: DSP_btn = st.button(parties[1], disabled=st.session_state.answered, use_container_width=True)
    with col3: Fazilet_btn = st.button(parties[2], disabled=st.session_state.answered, use_container_width=True)
    with col4: ANAP_btn = st.button(parties[3], disabled=st.session_state.answered, use_container_width=True)
    with col5: TruePath_btn = st.button(parties[4], disabled=st.session_state.answered, use_container_width=True)

    # Detect which button was clicked
    selected_guess = None
    if MHP_btn: selected_guess = "MHP"
    if DSP_btn: selected_guess = "DSP"
    if Fazilet_btn: selected_guess = "Fazilet"
    if ANAP_btn: selected_guess = "ANAP"
    if TruePath_btn: selected_guess = "True Path"

    # Process the guess
    if selected_guess and not st.session_state.answered:
        st.session_state.answered = True
        st.session_state.trials += 1  # Kullanıcı cevap verdiğinde deneme sayısını 1 artırıyoruz
        if selected_guess == current_mp["party"]:
            st.session_state.score += 1
            st.session_state.is_correct = True
            st.session_state.feedback = f"Correct! That is **{current_mp['name']}**."
        else:
            st.session_state.is_correct = False
            st.session_state.feedback = f"Incorrect. That is **{current_mp['name']}**, who represented the **{current_mp['party']}**."
        
        # record recent guess
        st.session_state.recent_guesses.insert(0, {
            "name": current_mp["name"],
            "guessed": selected_guess,
            "correct": st.session_state.is_correct,
            "actual": current_mp["party"],
            "img": current_mp["img"],
        })
        st.session_state.recent_guesses = st.session_state.recent_guesses[:5]
        st.rerun()

    # Show the result of the guess and the "Next" button
    if st.session_state.answered:
        if st.session_state.is_correct:
            st.success(st.session_state.feedback)
        else:
            st.error(st.session_state.feedback)
           
        if st.button("Next", type="primary"):
            st.session_state.index += 1
            st.session_state.answered = False
            st.rerun()

    # Scoreboard banner at the bottom
    st.write("---")
    st.write(f" **Current Score:** {st.session_state.score} / {st.session_state.trials}")

    # Recent guesses
    if st.session_state.recent_guesses:
        st.subheader("Recent guesses")
        for g in st.session_state.recent_guesses:
            icon = "✅" if g.get("correct") else "❌"
            col_img, col_text, col_actual = st.columns([0.15, 0.6, 0.25])
            img_file = os.path.join(ASSETS_DIR, g.get("img")) if g.get("img") else None
            if img_file and os.path.exists(img_file):
                try:
                    col_img.image(Image.open(img_file), width=48)
                except Exception:
                    col_img.write("")
            else:
                col_img.write("")
            col_text.markdown(f"{icon} **{g.get('name')}** — guessed **{g.get('guessed')}**")
            col_actual.markdown(f"Actual: **{g.get('actual')}**")

# 5. Game Over Screen (20 Soru Tamamlandığında Burası Çalışır)
else:
    st.write("---")
    st.markdown(
        f"""
        <div class="end-screen">
            <h2 style='color: #2C3E50; font-family: "Cinzel", serif;'>🏛️ SESSION COMPLETED</h2>
            <p style='font-size: 1.2rem; margin-top: 10px;'>Your performance in matching 1990s political factions:</p>
            <h1 style='color: #27AE60; font-size: 3.5rem; margin: 15px 0;'>{st.session_state.score} / 20</h1>
        </div>
        """, 
        unsafe_allow_html=True
    )

    if st.session_state.score >= 14:
        st.balloons()
        st.success("Outstanding! You have an incredible elite-level grasp on linking physical traits to political orientation.")
    elif st.session_state.score >= 9:
        st.info("Solid result!")
    else:
        st.warning("You might want to revisit the archives! ")

    st.write("")
    if st.button("Play Again", type="primary"):
        st.session_state.index = 0
        st.session_state.score = 0
        st.session_state.trials = 0  # Yeni oyunda sayacı sıfırlıyoruz
        st.session_state.answered = False
        st.session_state.recent_guesses = []
        random.shuffle(st.session_state.dataset)
        st.rerun()

# 6. Party Library - collapsible reference for users
st.write("---")
with st.expander("Party Library - Learn about the parties"):
    st.markdown("""
    #### Turkish Political Parties in the game
   
    **MHP - Nationalist Movement Party**
    - Full name: Milliyetçi Hareket Partisi
   
  The MHP is a far-right, nationalist party in Turkey. It was founded in 1969 by Alparslan Türkeş and has been a significant force in Turkish politics, particularly among nationalist voters. The party's ideology is based on Turkish nationalism and conservatism, and it has often been associated with the paramilitary "Grey Wolves" youth organisation. The MHP has participated in various coalition governments and has been influential in shaping Turkey's political landscape, especially on issues related to national identity and security. Its members are known to wear crescent-shaped moustaches, which is a distinctive cultural trait.
   
    **DSP - Democratic Left Party**
    - Full name: Demokratik Sol Parti
               
    The DSP is a center-left political party in Turkey, founded in 1985 by Bülent Ecevit. The party's ideology is based on social democracy and democratic socialism, and it has traditionally been associated with the working class and labor unions. The DSP has been a significant player in Turkish politics, particularly during the late 1990s and early 2000s, when it was part of coalition governments. The party's platform focuses on social justice, workers' rights, and economic equality. Bülent Ecevit, the party's founder and long-time leader, served as Prime Minister of Turkey multiple times and was known for his charismatic leadership style. Its members of parliament are typically clean-shaven.
   
    **Fazilet Party**
    - Full name: Fazilet Partisi
               
    The Fazilet Party was an Islamist political party in Turkey, founded in 1997 as a successor to the Welfare Party (Refah Partisi). The party's ideology was based on political Islam and conservatism, and it aimed to promote Islamic values in Turkish society. The Fazilet Party was led by Recai Kutan and had a significant following among conservative and religious voters. However, the party faced legal challenges and was eventually banned by the Turkish Constitutional Court in 2001 for violating the secular principles of the Turkish state. After its dissolution, many of its members went on to form the Justice and Development Party (AKP), which has been a dominant force in Turkish politics since the early 2000s. Its members of parliament often had substantial facial hair, reflecting their conservative and religious orientation.
   
    **ANAP - Motherland Party**
    - Full name: Anavatan Partisi
               
    The ANAP is a center-right political party in Turkey, founded in 1983 by Turgut Özal. The ANAP played a significant role in Turkish politics during the 1980s and early 1990s, with Turgut Özal serving as Prime Minister and later as President of Turkey. The party's platform focused on economic liberalization, privatisation, and reducing the role of the state in the economy. The ANAP was known for its pro-Western stance and efforts to integrate Turkey into the global economy. However, the party's influence waned in the late 1990s, and it eventually merged with other parties to form the True Path Party (DYP). Its members of parliament typically had a more polished and business-like appearance, often with Özal's exceptionally large glasses.
   
    **True Path - True Path Party**
    - Full name: Doğru Yol Partisi
               
    The True Path Party (DYP) is a center-right political party in Turkey, founded in 1983 as a successor to the Justice Party (Adalet Partisi). The DYP's ideology is based on conservatism and economic liberalism, and it has traditionally been associated with rural voters and the business community. The party has been a significant player in Turkish politics, particularly during the 1990s, when it was part of several coalition governments. The DYP's platform focuses on economic development, privatisation, and maintaining traditional social values. Tansu Çiller, the party's most prominent leader, served as Turkey's first and only female Prime Minister from 1993 to 1996. Its members of parliament often had a more polished and business-like appearance, with many wearing suits and ties, reflecting their conservative and pro-business orientation.
    """)

with st.expander("About the Project"):
    st.markdown("""
    This project was created solely as an experimental endeavour. The game challenges its players to guess the party allegiance of Turkish members of parliament based on their physical aspects, such as facial hair styles and dress codes. By matching the portraits of these MPs to their respective parties, players can gain a deeper understanding of how political polarisation impacts physical outlook and preferences of fashion.
    """)
