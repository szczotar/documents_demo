from dotenv import load_dotenv

load_dotenv()

import streamlit as st
import os
import pathlib
import textwrap
from PIL import Image
import google.generativeai as genai
import base64
from io import BytesIO

def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def get_gemini_response(question):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(question)
    return response.text

def get_gemini_response_image(input,image):
    model = genai.GenerativeModel('gemini-1.5-flash')
    if input!="":
       response = model.generate_content([input,image])
    else:
       response = model.generate_content(image)
    return response.text

with st.sidebar:
    st.header("Text as input")
    text_input_prompt =st.text_input("Enter the prompt: ",key="input")
    st.markdown("<h1 style='text-align: center;'>(or)</h1>", unsafe_allow_html=True)
    img_input_prompt =st.text_input("Enter the prompt: ",key="input1")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    image="" 
    submit=st.button("Generate response")


if submit:
    if text_input_prompt:
        response=get_gemini_response(text_input_prompt)
        st.subheader("Generated response:")
        st.write(response)
    elif uploaded_file:
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            im_file = BytesIO()
            image.save(im_file, format="png")
            im_bytes = im_file.getvalue()  # im_bytes: image in binary format.
            im_b64 = base64.b64encode(im_bytes)
            print(im_b64)
            # print(base64.b64encode(uploaded_file).decode('utf-8'))
            st.image(image, caption="Uploaded Image.", use_column_width=True)
        st.subheader("Generated response:")
        response=get_gemini_response_image(img_input_prompt,image)
        st.write(response)