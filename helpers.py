
import openai
import streamlit as st
import os
import csv

def call_openai_gpt(user_prompt, mode='ms.j'):
    user_prompt = str(user_prompt)
    context = ""
    if '?' not in user_prompt:
        user_prompt+='?'

    if mode=='ms.j':
        preamble = 'You are an inspiring writing partner for a high quality MOVIE trying to extract creativity with probing questions. Answer and ask questions back in a helpful, encouraging style. Respond to this: ' 
    elif mode=='mr.k':
        preamble = 'You are a creative writing partner for a high quality MOVIE  trying to extract creativity with probing questions. Answer and ask questions back in an artistic, high brow style. Respond to this: ' 
    elif mode=='mr.z':
        preamble = 'You are an intelligent writing partner for a high quality MOVIE trying to extract creativity with probing questions. Answer and ask questions back in dry wit, cryptic, and skeptical style. Respond to this: ' 

    user_prompt = preamble + user_prompt
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo", 
    messages=[{"role": "user", "content": context + user_prompt}]
    )

    return completion
     

def openai_call(user_nom, mode): 
    response  = ""
    col1, col2 = st.columns([6,2])
    user_prompt = col1.text_area('')
    col2.write('')
    col2.write('')
    is_clicked = col2.button('submit')  
    og_user_prompt = str(user_prompt)

    completion = ""
    if is_clicked and len(user_prompt):
        completion = call_openai_gpt(user_prompt, mode) 
        is_clicked = False

    if completion:
        response = completion.choices[0].message.content
        st.write('> ' + str(response))
        st.json(completion, expanded=False)
        with open(user_nom+'_database.csv','a', newline='') as f:
            writer = csv.writer(f)
            cont = str(completion.choices[0].message.content)
            createtime = (completion.created)
            writer.writerow([og_user_prompt, mode, createtime, cont])


