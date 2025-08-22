import streamlit as st
import pandas as pd
from openai import OpenAI
import re

st.set_page_config(page_title="AI Patient Triage System", layout="wide")

try:
    client = OpenAI(
        api_key=st.secrets["GROQ_API_KEY"],
        base_url="https://api.groq.com/openai/v1",
    )
except (FileNotFoundError, KeyError):
    st.error("ERROR: API key not found")
    st.stop()
    
@st.cache_data
def load_patient_data():
    """Loads patient data from the CSV file."""
    try:
        return pd.read_csv('patients.csv')
    except FileNotFoundError:
        st.error("ERROR: patients.csv not found.")
        return None

@st.cache_data
def load_doctor_data():
    """Loads doctor and department data from the CSV file."""
    try:
        return pd.read_csv('doctors.csv')
    except FileNotFoundError:
        st.error("ERROR: doctors.csv not found.")
        return None

def generate_clarifying_questions(patient_history, current_symptoms):
    """AI asks smarter, guided questions for self-examination."""
    prompt = f"""
    You are a Medical AI Triage Assistant. Your primary goal is to create a set of guided self-examination questions for a patient based on their *current* symptoms.

**CRITICAL INSTRUCTION:** Your entire focus must be on the `{current_symptoms}`. **Do not** ask about the `{patient_history}` unless a current symptom is a clear continuation of a known past condition. Create 3-4 simple, instructional questions.

**Patient History:** {patient_history}, consider history only if symptoms match it is not always due to past patient history
**Initial Symptoms:** {current_symptoms}

**Instructions:**
- Example 1 (Pain): "Gently press on the upper right side of your stomach. Is the pain sharp or dull?"
- Example 2 (Breathing): "Take a deep breath. Does the pain in your chest get worse?"
- Example 3 (Dizziness): "From a sitting position, stand up slowly. Does the room feel like it's spinning?"
- Output only the questions, numbered. Do not add any conversational text or introductions.

    """
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}]
        )
        questions = response.choices[0].message.content.strip().split('\n')
        return [q.strip() for q in questions if q.strip()]
    except Exception as e:
        st.error(f"An error occurred while generating questions: {e}")
        return []

def generate_doctor_report(patient_history, current_symptoms, question_answers, doctors_list_str):
    """AI generates a detailed doctor report AND a simple patient summary with refined logic."""
    qa_summary = "\n".join([f"- {qa['question']} {qa['answer']}" for qa in question_answers])
    prompt = f"""
    You are an expert Medical AI. Your task is to perform a triage analysis and generate two separate summaries.
    **CRITICAL INSTRUCTION: Prioritize the patient's current symptoms and their answers to the guided questions above all else.** Only use the patient's history for context if it is directly and obviously relevant. If the history is not relevant, you must ignore it.

    **Available Doctors & Departments:**
    {doctors_list_str}

    **Patient Information:**
    - History: {patient_history}
    - Initial Symptoms: {current_symptoms}
    - Guided Examination Answers: {qa_summary}

    **Your Task:**
    Generate two distinct parts separated by "---".

    **Part 1: [DOCTOR REPORT]**
    Generate a report with SIX sections based on the new priority instruction.
    1. Symptom Summary
    2. Relevant History (if any)
    3. Potential Diagnoses (Ranked)
    4. Specialist Recommendation
    5. Urgency Assessment (Low, Medium, High, or Critical)
    6. Actionable Recommendation

    ---

    **Part 2: [PATIENT SUMMARY]**
    Generate a simple summary for the patient.
    1. Acknowledge their information has been analyzed.
    2. If urgency is "Critical", instruct them to seek immediate medical attention.
    3. If not critical, you **must** recommend a specific doctor by name from the **Available Doctors** list. For example: "We recommend you see Dr. Kenji Tanaka (General Practitioner)."
    """
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {e}"

# --- 4. FRONTEND USER INTERFACE ---
st.title("🩺 Smart AI Triage & Appointment System")
st.markdown("This tool guides patients through self-examination and provides an instant recommendation.")

patient_df = load_patient_data()
doctor_df = load_doctor_data()

if 'stage' not in st.session_state:
    st.session_state.stage = 'initial_input'

if patient_df is not None and doctor_df is not None:
    left_column, right_column = st.columns((1, 1.2))

    with left_column:
        st.header("Patient Input")
        patient_name = st.selectbox("Select Patient:", patient_df['patient_name'])
        selected_patient = patient_df[patient_df['patient_name'] == patient_name].iloc[0]

        st.subheader("Existing Medical History")
        st.info(selected_patient['medical_history'])

        if st.session_state.stage == 'initial_input':
            symptoms_input = st.text_area("Enter Your Main Symptoms:", height=100)
            if st.button("Start Guided Examination", type="primary"):
                if symptoms_input:
                    st.session_state.patient_history = selected_patient['medical_history']
                    st.session_state.initial_symptoms = symptoms_input
                    with st.spinner("AI is preparing guided questions..."):
                        st.session_state.questions = generate_clarifying_questions(st.session_state.patient_history, st.session_state.initial_symptoms)
                    st.session_state.stage = 'clarifying_questions'
                    st.rerun()

        if st.session_state.stage == 'clarifying_questions':
            st.subheader("AI Guided Examination")
            st.markdown("Please provide answers to the AI's questions below to help with the analysis.")
            answers = {}
            for i, question in enumerate(st.session_state.questions):
                clean_question = re.sub(r'^\d+\.\s*', '', question)
                answers[i] = st.text_input(clean_question, key=f"ans_{i}")

            if st.button("Analyze My Case", type="primary"):
                qa_list = [{"question": q, "answer": answers[i]} for i, q in enumerate(st.session_state.questions)]
                doctors_list_str = doctor_df.to_markdown(index=False)
                with st.spinner("AI is analyzing your case and finding a specialist..."):
                    full_report = generate_doctor_report(st.session_state.patient_history, st.session_state.initial_symptoms, qa_list, doctors_list_str)
                st.session_state.full_report = full_report
                st.session_state.stage = 'show_report'
                st.rerun()

    with right_column:
        st.header("Your Triage Result")
        if st.session_state.stage == 'show_report':
            full_report = st.session_state.full_report
            
            try:
                doctor_report, patient_summary = full_report.split("---", 1)
                patient_summary = patient_summary.replace("[PATIENT SUMMARY]", "").strip()
                doctor_report = doctor_report.replace("[DOCTOR REPORT]", "").strip()
            except (ValueError, AttributeError):
                doctor_report = "Could not parse the AI's full report. The AI may be overloaded."
                patient_summary = "There was an issue generating the patient summary. Please try again."

            if "Critical" in doctor_report:
                st.error("🚨 URGENT: CRITICAL HEALTH ALERT")
                st.markdown(f"**Based on your symptoms, the AI analysis indicates a critical situation.**")
                st.warning(patient_summary)
            else:
                st.success("Analysis Complete")
                st.markdown("**Here is your recommendation:**")
                st.info(patient_summary)

            with st.expander("Show Detailed Doctor's Report (For Medical Staff)"):
                st.markdown(doctor_report)
            
            if st.button("Start New Triage"):
                st.session_state.stage = 'initial_input'
                st.rerun()
        else:
            st.info("Your analysis and doctor recommendation will appear here.")