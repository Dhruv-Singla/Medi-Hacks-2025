# 🩺 Smart AI Triage & Appointment System

**A project for the Medi-Hacks 2025 Hackathon.**

This intelligent web application streamlines the patient triage process by using AI to conduct a guided self-examination, assess urgency, and provide an instant, actionable recommendation for both the patient and medical staff.

---

## 🚀 The Problem

In busy healthcare environments, the initial patient triage process is often time-consuming and relies heavily on the availability of medical staff. This can lead to delays in identifying critical cases, inefficient allocation of specialists, and a stressful experience for patients. The key challenge is to quickly and accurately gather relevant information to prioritize care effectively.

## ✨ Our Solution

This AI-powered system acts as a "digital front door" to the triage process. It empowers patients to provide more accurate information through a guided, interactive examination and delivers an immediate, AI-driven analysis.

This tool saves valuable time for doctors and nurses, helps in the early detection of critical conditions, and directs patients to the right specialist, improving overall hospital workflow and patient outcomes.

---

## 🌟 Key Features

* **🤖 AI-Guided Examination:** The system doesn't just ask for symptoms; it provides simple, physical instructions to help patients describe their condition more accurately.
* **🚨 Critical Alert System:** The AI assesses the urgency of each case. If a situation is deemed "Critical," the UI displays a prominent alert, ensuring immediate attention is drawn to high-priority patients.
* **🧑‍⚕️ Smart Doctor Recommendations:** Using an internal directory of specialists, the system recommends a specific, named doctor to the patient for non-critical cases, closing the loop from triage to appointment.
* **📄 Dual-Summary Output:** The AI generates two distinct reports: a simple, reassuring summary for the patient and a detailed, technical report for the doctor, hidden in an expander to avoid overwhelming the user.
* **🧠 Context-Aware Analysis:** The AI is specifically prompted to prioritize a patient's current symptoms over their past medical history, preventing confirmation bias and leading to more accurate initial assessments.

---

## 🛠️ Technology Stack

* **Backend:** Python
* **Frontend:** Streamlit
* **AI/LLM:** Groq API with Llama 3
* **Data Handling:** Pandas

---

## ⚙️ Setup and Installation

To run this project locally, please follow these steps:

**1. Clone the Repository**
```bash
git clone [https://github.com/YourUsername/Medi-Hacks-2025.git](https://github.com/YourUsername/Medi-Hacks-2025.git)
cd Medi-Hacks-2025# Medi-Hacks-2025
