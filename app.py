import streamlit as st
import os
import re
import pandas as pd
from docx import Document
import PyPDF2
import textract


def extract_text_from_docx(file_path):
    try:
        doc = Document(file_path)
        text = ''
        for paragraph in doc.paragraphs:
            text += paragraph.text + '\n'
        return text
    except Exception as e:
        st.error(f"Error extracting text from DOCX file: {e}")
        return ''

def extract_text_from_pdf(file_path):
    try:
        text = ''
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF file: {e}")
        return ''

def extract_text_from_other(file_path):
    try:
        return textract.process(file_path, method='tesseract', language='eng')
    except Exception as e:
        st.error(f"Error extracting text from file: {e}")
        return ''


def extract_emails_and_numbers(text):
    emails = re.findall(r'[\w\.-]+@[\w\.-]+', text)
    phone_numbers = re.findall(r'(\+?\d{1,3}[-\s]?\d{5}[-\s]?\d{5}|\d{11}|\d{5}[-\s]?\d{5}|\d{4}[-\s]?\d{6}|\+\d{2}[-\s]?\d{5}[-\s]?\d{5}|\d{2}[-\s]?\d{5}[-\s]?\d{5})', text)
    return emails, phone_numbers


def process_cv(file):
    filename = file.name

    # Save the uploaded file temporarily
    with open(filename, 'wb') as f:
        f.write(file.getvalue())

    if filename.endswith('.docx'):
        text = extract_text_from_docx(filename)
    elif filename.endswith('.pdf'):
        text = extract_text_from_pdf(filename)
    else:
        text = extract_text_from_other(filename)
    
    # Remove the temporary file
    os.remove(filename)
    
    # Print extracted text for debugging
    # st.write(f"Extracted text from {filename}:\n{text}")

    emails, phone_numbers = extract_emails_and_numbers(text)
    emails, phone_numbers = replace_null(emails, phone_numbers)

    return filename, ', '.join(emails), ', '.join(phone_numbers),text

def replace_null(emails, phone_numbers):
    if not emails:
        emails = ["(Not Found Or Not Properly Written)"]
    if not phone_numbers:
        phone_numbers = ["(Not Found Or Not Properly Written)"]
    return emails, phone_numbers


# The driver code :
st.title('CV Information Extractor')

uploaded_files = st.file_uploader("Upload CVs (docx, pdf)", type=["docx", "pdf"], accept_multiple_files=True)

if uploaded_files:
    st.write("CVs Uploaded:")
    for file in uploaded_files:
        st.write(f"- {file.name}")
    
    if st.button("Extract Information"):
        data = []
        for file in uploaded_files:
            filename, emails, phone_numbers, text = process_cv(file)
            data.append([filename, emails, phone_numbers, text])
        
        df = pd.DataFrame(data, columns=["Filename", "Email", "Phone Number", "Overall Text"])
        df.fillna("Not Found", inplace=True)
        st.write(df)

        # Allow downloading the extracted data as CSV
        csv_data = df.to_csv(index=False)
        st.download_button(label="Download Extracted Information", data=csv_data, file_name='cv-insights.csv', mime='text/csv')
