import streamlit as st
import streamlit.components.v1 as components

from streamlit_drawable_canvas import st_canvas
import networkx as nx
import matplotlib.pyplot as plt

import json

import gspread
from google.oauth2.service_account import Credentials

import datetime

def render_gcf_factorization(item):
    st.write(item["text"])

    gcf_key = f"{item['id']}_gcf"

    def first_two_factors(n):
        factors = []
        for i in range(1, n + 1):
            if n % i == 0:
                factors.append(i)
            if len(factors) == 2:
                break
        return factors

    factors_n1 = first_two_factors(item["num1"])
    factors_n2 = first_two_factors(item["num2"])
    
    st.text_input(f"Factors of {item['num1']} (comma separated):", key=f"{item['id']}_factors_n1", placeholder=f"e.g., {', '.join(map(str, factors_n1))}...")
    st.text_input(f"Factors of {item['num2']} (comma separated):", key=f"{item['id']}_factors_n2", placeholder=f"e.g., {', '.join(map(str, factors_n2))}...")

    st.text_input("GCF:", placeholder="Enter a number (e.g., 2)", key=gcf_key)

def render_gcf_subtraction(item):
    st.write(item["text"])

    steps_key = f"{item['id']}_steps"
    input_key = f"{item['id']}_input"
    error_key = f"{item['id']}_error"
    gcf_key = f"{item['id']}_gcf"

    bigger = max(item["num1"], item["num2"])
    smaller = min(item["num1"], item["num2"])

    # Init session state
    if steps_key not in st.session_state:
        st.session_state[steps_key] = []

    if error_key not in st.session_state:
        st.session_state[error_key] = ""

    def add_step():
        raw = st.session_state[input_key].strip()
        try:
            num, den = map(int, raw.split("-"))
            st.session_state[steps_key].append(f"{num} - {den} = {num - den}")
            st.session_state[input_key] = ""
            st.session_state[error_key] = ""
        except:
            st.session_state[error_key] = f"❌ Invalid format. Use e.g., {bigger}-{smaller}"

    def remove_step():
        if st.session_state[steps_key]:
            st.session_state[steps_key].pop()

    # Show current steps
    for step in st.session_state[steps_key]:
        st.text(step)

    st.text_input(f"Type a subtraction step (e.g., {bigger}-{smaller})", key=input_key)
    if st.session_state[error_key]:
        st.warning(st.session_state[error_key])

    cols = st.columns([1.5, 6])
    with cols[0]:
        st.button("Add subtraction step", on_click=add_step, key=f"{item['id']}_add_btn")
    with cols[1]:
        st.button("Remove last step", on_click=remove_step, key=f"{item['id']}_remove_btn")

    st.text_input("GCF:", placeholder="Enter a number (e.g., 2)", key=gcf_key)

def render_gcf_division(item):
    st.write(item["text"])

    steps_key = f"{item['id']}_steps"
    input_key = f"{item['id']}_input"
    error_key = f"{item['id']}_error"
    gcf_key = f"{item['id']}_gcf"

    bigger = max(item["num1"], item["num2"])
    smaller = min(item["num1"], item["num2"])

    if steps_key not in st.session_state:
        st.session_state[steps_key] = []
    if error_key not in st.session_state:
        st.session_state[error_key] = ""

    def add_step():
        raw = st.session_state[input_key].strip()
        try:
            num, den = map(int, raw.split("/"))
            if den == 0:
                st.session_state[error_key] = "❌ Division by zero is not allowed."
                return
            quotient = num // den
            remainder = num % den
            st.session_state[steps_key].append(f"{num} ÷ {den} = {quotient} R {remainder}")
            st.session_state[input_key] = ""
            st.session_state[error_key] = ""
        except:
            st.session_state[error_key] = f"❌ Invalid format. Use e.g., {bigger}/{smaller}"

    def remove_step():
        if st.session_state[steps_key]:
            st.session_state[steps_key].pop()

    # Show steps
    for step in st.session_state[steps_key]:
        st.text(step)

    st.text_input("Type a division step (e.g., 150/100)", key=input_key)
    if st.session_state[error_key]:
        st.warning(st.session_state[error_key])

    cols = st.columns([1.5, 6])
    with cols[0]:
        st.button("Add division step", on_click=add_step, key=f"{item['id']}_add_btn")
    with cols[1]:
        st.button("Remove last step", on_click=remove_step, key=f"{item['id']}_remove_btn")

    st.text_input("GCF:", placeholder="Enter a number (e.g., 2)", key=gcf_key)

def render_instruction(item):
    st.write(f"**Instruction**: {item["text"]}")
    if "image" in item:
        st.image(item["image"])

def render_mcq(item):
    question_text = item["text"]
    options = [f"{chr(97 + i)}. {opt}" for i, opt in enumerate(item["options"])]
    
    st.write(question_text)
    if "image" in item:
        st.image(item["image"])

    st.radio(
        f"**{question_text}**",
        options=options,
        key=item["id"],
        label_visibility="collapsed"
    )

# def render_short_answer(item):
#     st.write(item["text"])
#     st.text_input(label=item["text"], key=item["id"], label_visibility="collapsed")
#     st.write("")

def render_custom_component(item, components):
    st.write(item["text"])
    component_name = item["component"]
    
    if component_name in components:
        component = components[component_name]
        component(key=item["id"])
    else:
        st.warning(f"Unknown component: {component_name}")

def render_drawing(item):
    st.write(f"**Instruction**: {item["text"]}")
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 1)",  # White background
        stroke_width=3,
        stroke_color="black",
        background_color="white",
        height=600,
        width=700,
        drawing_mode="freedraw",  # or "line", "rect", "circle", "transform"
        key="canvas",
    )

    


def render_item(item, components=None):
    match item["type"]:
        case "mcq":
            render_mcq(item)
        # case "short_answer":
        #     render_short_answer(item)
        case "instruction":
            render_instruction(item)
        case "sudoku":
            render_custom_component(item, components)
        case "gcf_factorization":
            render_gcf_factorization(item)
        case "gcf_subtraction":
            render_gcf_subtraction(item)
        case "gcf_division":
            render_gcf_division(item)
        case "drawing":
            render_drawing(item)
        case _:
            st.warning(f"Unknown item type: {item['type']}")

    st.write("")  # Spacer
    st.write("")  # One more

def render_section(section, components=None):
    st.subheader(section["title"])
    
    if "instruction" in section:
        st.write(f"**Instruction**: {section["instruction"]}")
    if "image" in section:
        st.image(section["image"])
    
    for item in section.get("items", []):
        render_item(item, components)

def render_exam(exam_data, components=None):
    st.title(exam_data.get("title", "Exam"))

    for section in exam_data.get("sections", []):
        render_section(section, components)



st.set_page_config(page_title="Final Exam", layout="centered")
st.title("Final Exam")
st.header("Student Information")

# Student Info
class_options = ["3/11", "3/12"]
selected_class = st.selectbox("Select your class:", class_options)
nickname = st.text_input("Nickname")
roll_number = st.text_input("Roll Number")

# puzzle = st.secrets["sudoku"]["puzzle"]
# solution = st.secrets["sudoku"]["solution"]

# Load your JSON
with open("exam.json") as f:
    exam_data = json.load(f)

# Declare components
sudoku = components.declare_component("sudoku", path="components/sudoku")
custom_components = {
    "sudoku": sudoku
}

# Render everything
render_exam(exam_data, components=custom_components)















if st.button("Submit Test"):
    if not nickname or not student_number:
        st.error("Please fill in your nickname and student number.")
    else:
        
        

        # Set up creds and open your sheet
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        
        # Load credentials from Streamlit secrets
        service_account_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
        
        client = gspread.authorize(creds)
        
        
        # Timestamp for filenames and sheets
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename_ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        
        json_path = f'{selected_class.replace("/", "-")}_{nickname}_{student_number}_{filename_ts}.json'
        with open(json_path, "w") as f:
            json.dump(submission, f, indent=2)
            
        

        try:
            sheet = client.open("Final").worksheet(selected_class)
        except gspread.WorksheetNotFound:
            st.error(f"Worksheet '{selected_class}' not found. Please check your Google Sheet.")

        row = [
            submission["roll_number"],
            submission["nickname"],
            submission["scores"]["part1_sudoku"],
            submission["scores"]["part2"],
            submission["scores"]["part3"],
            submission["scores"]["part4"],
            submission["scores"]["part5"],
            submission["scores"]["total"],
            timestamp
        ]

        sheet.append_row(row)
        st.success(f"Submission received! ✅ Total Score: {round(total)}/20")
        
        with open(json_path, "rb") as f:
            st.download_button(
            "Download answers",
                data=f,
                file_name=os.path.basename(json_path),
                mime="application/json"
            )

