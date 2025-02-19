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
import json
import requests
import time

def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
runpod_key = os.getenv("Runpod_Key")
runpod_id = os.getenv("runpod_id")

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

def qven_response(input, emcoded_image, api_key, endpoint_id):
    endpoint = f"https://api.runpod.ai/v2/{endpoint_id}/run"

    header = {"Content-Type" : "application/json",
          "Authorization": f"Bearer {api_key}"}
    
    input = {"input" : {"prompt" :[{
        "role": "user",
        "content": [
            {
                "type": "image",
                "image": f"data:image;base64,{emcoded_image}"
            },
            {"type": "text", "text": "What is wirtten on the document. Structure it in JSON output."}
        ]
        }
    ]}}

    try:
        r= requests.post(url= endpoint, headers=header, data =json.dumps(input))
        request_id = r.json()['id']

        status = "IN_PROGRESS"
        while status != "COMPLETED":
            check_job_status = requests.post(url=f"https://api.runpod.ai/v2/{id}/status/{request_id}", headers=header)
            status = check_job_status.json()["status"]
            time.sleep(15)
        output = check_job_status.json()["output"]['output'][0]
 
        
    except TimeoutError:
        print("Job timed out.")

    return output

with st.sidebar:
    # st.header("Text as input")
    # text_input_prompt =st.text_input("Enter the prompt: ",key="input")
    # st.markdown("<h1 style='text-align: center;'>(or)</h1>", unsafe_allow_html=True)
    option = st.selectbox("Select llm model:",
                          ("gemini-1.5-flash", "qwen-vl [open_source]")),
    img_input_prompt =st.text_input("Enter the prompt: ",key="input1")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    image="" 
    if img_input_prompt=="":
                img_input_prompt = "What is wirtten on the document. Structure it in JSON output."
    submit=st.button("Generate response")


if submit:
    if uploaded_file:
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            im_file = BytesIO()
            image.save(im_file, format="png")
            im_bytes = im_file.getvalue()  # im_bytes: image in binary format.
            im_b64 = base64.b64encode(im_bytes)
            # print(base64.b64encode(uploaded_file).decode('utf-8'))
            st.image(image, caption="Uploaded Image.", use_column_width=True)
            st.subheader("Generated response:")
            print(option)
          
            if "gemini-1.5-flash" in option:
                response=get_gemini_response_image(img_input_prompt,image)
            else:
                response = qven_response(img_input_prompt, im_b64,runpod_key, runpod_id)

        st.write(response)
    else:
        st.write("Please upload a document")