import streamlit as st
import mysql.connector
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta

# MySQL database connection details
db_config = {
    'host': 'localhost',  # Replace with your MySQL server hostname
    'user': 'root',
    'password': 'sql123',
    'database': 'otp'  # Changed to the 'otp' database
}

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

def get_otp_from_sequence():
    cursor.execute("SELECT @otp_seq := @otp_seq + 1 FROM (SELECT @otp_seq := 0) AS init")
    otp = cursor.fetchone()[0]
    return otp

def send_email(to_email, otp):
    from_email = "minatoooo2002@gmail.com"  #https://www.tempmail.us.com/
    password = "tmaa ylwu ycby bskv" #"Anup09@gmail"
    
    subject = "Your OTP Code"
    body = f"Your OTP code is {otp}. It will expire in 5 minutes."
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(from_email, password)
            server.send_message(msg)
    except smtplib.SMTPException as e:
        st.error(f"SMTP error: {e}")

def store_otp(email, otp):
    timestamp = datetime.now() + timedelta(minutes=5)
    cursor.execute("""
        INSERT INTO otp_table (email, otp, timestamp)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE otp = %s, timestamp = %s
        """,
        (email, otp, timestamp, otp, timestamp)
    )
    conn.commit()

def verify_otp(email, otp):
    cursor.execute("SELECT otp, timestamp FROM otp_table WHERE email = %s", (email,))
    result = cursor.fetchone()
    if result:
        stored_otp, timestamp = result
        if stored_otp == otp and datetime.now() <= timestamp:
            return True
        else:
            return False
    else:
        return False

# Streamlit UI
st.title("OTP Verification System")

menu = ["Generate OTP", "Verify OTP"]
choice = st.sidebar.selectbox("Select Option", menu)

if choice == "Generate OTP":
    email = st.text_input("Enter your email address:")
    if st.button("Generate OTP"):
        if email:
            otp = get_otp_from_sequence()
            send_email(email, otp)
            store_otp(email, otp)
            st.success("OTP has been sent to your email!")
        else:
            st.error("Please enter an email address.")
    
elif choice == "Verify OTP":
    email = st.text_input("Enter your email address:")
    otp = st.text_input("Enter the OTP:")
    if st.button("Verify OTP"):
        if email and otp:
            if verify_otp(email, otp):
                st.success("OTP verified successfully!")
            else:
                st.error("Invalid or expired OTP.")
        else:
            st.error("Please enter both email address and OTP.")

# Close database connection
cursor.close()
conn.close()
