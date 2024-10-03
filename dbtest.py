import mysql.connector
import streamlit as st


# Database connection setup
def create_connection():
    connection = mysql.connector.connect(
        host="localhost",      # Host where the database is running
        user="root",           # Your MySQL username
        password="toor", # Your MySQL password
        database="shms"        # Your database name
    )
    return connection

# Login page
def login_page():
    st.title("Smart Healthcare Management System")
    st.subheader("Login")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user_type = authenticate_user(username, password)
        if user_type:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.user_type = user_type
            st.success(f"Welcome {user_type.capitalize()}, {username}!")
        else:
            st.error("Invalid username or password")

# Function to authenticate user (basic example)
def authenticate_user(username, password):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Check in the admin_users table
    cursor.execute("SELECT * FROM admin_users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    if user:
        return 'admin'
    
    # Check in the patients table
    cursor.execute("SELECT * FROM patients WHERE email = %s AND medical_history = %s", (username, password)) # Assuming password is stored in medical_history for now
    user = cursor.fetchone()
    if user:
        return 'patient'
    
    # Check in the doctors table
    cursor.execute("SELECT * FROM doctors WHERE name = %s", (username,))
    user = cursor.fetchone()
    if user:
        return 'doctor'
    
    return None

# Patient Dashboard
def patient_dashboard():
    st.title(f"Patient Dashboard - {st.session_state.username}")
    st.write("Here you can view your medical history and book appointments.")

    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Display medical history
    cursor.execute("SELECT medical_history FROM patients WHERE email = %s", (st.session_state.username,))
    medical_history = cursor.fetchone()
    
    if medical_history:
        st.write(f"Your Medical History: {medical_history['medical_history']}")
    
    # Appointment booking section (simplified)
    st.subheader("Book an Appointment")
    doctor = st.selectbox("Select Doctor", ["Dr. Smith", "Dr. Adams"])  # Example doctors
    date = st.date_input("Select Date")
    time = st.time_input("Select Time")
    
    if st.button("Book Appointment"):
        appointment_datetime = f"{date} {time}"
        cursor.execute("INSERT INTO appointments (patient_id, doctor_id, appointment_datetime, status) VALUES (%s, %s, %s, %s)", 
                        (1, 1, appointment_datetime, 'Scheduled'))  # Replace 1 with actual patient/doctor IDs
        conn.commit()
        st.success("Appointment booked successfully!")

# Doctor Dashboard
def doctor_dashboard():
    st.title(f"Doctor Dashboard - {st.session_state.username}")
    
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Display doctor's upcoming appointments
    cursor.execute("SELECT * FROM appointments WHERE doctor_id = (SELECT id FROM doctors WHERE name = %s)", (st.session_state.username,))
    appointments = cursor.fetchall()
    
    st.write("Upcoming Appointments:")
    for appointment in appointments:
        st.write(f"Appointment ID: {appointment['id']}, Date: {appointment['appointment_datetime']}, Status: {appointment['status']}")

# Admin Dashboard
def admin_dashboard():
    st.title(f"Admin Dashboard - {st.session_state.username}")
    
    # Add a patient section
    st.subheader("Add a New Patient")
    new_patient_name = st.text_input("Patient Name")
    new_patient_email = st.text_input("Patient Email")
    new_patient_medical_history = st.text_area("Patient Medical History")
    
    if st.button("Add Patient"):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO patients (name, email, medical_history) VALUES (%s, %s, %s)", 
                        (new_patient_name, new_patient_email, new_patient_medical_history))
        conn.commit()
        st.success("Patient added successfully!")

    # Remove a patient section
    st.subheader("Remove a Patient")
    remove_patient_email = st.text_input("Enter Patient Email to Remove")
    if st.button("Remove Patient"):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM patients WHERE email = %s", (remove_patient_email,))
        conn.commit()
        st.success("Patient removed successfully!")

# Main function to handle the dashboards
def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login_page()
    else:
        user_type = st.session_state.user_type
        if user_type == 'patient':
            patient_dashboard()
        elif user_type == 'doctor':
            doctor_dashboard()
        elif user_type == 'admin':
            admin_dashboard()

if __name__ == "__main__":
    main()
