
import openai
import streamlit as st
import os
import csv

def call_openai_gpt(user_prompt, mode='ms.j', history=None):
    user_prompt = str(user_prompt)
    context = ""
    if '?' not in user_prompt:
        user_prompt+='?'

    if mode=='ms.j':
        preamble = 'You are an inspiring writing partner for a high quality MOVIE trying to extract creativity with probing questions. Answer and ask questions back in a helpful, encouraging style.' 
    elif mode=='mr.k':
        preamble = 'You are a creative writing partner for a high quality MOVIE  trying to extract creativity with probing questions. Answer and ask questions back in an artistic, high brow style.' 
    elif mode=='mr.z':
        preamble = 'You are an intelligent writing partner for a high quality MOVIE trying to extract creativity with probing questions. Answer and ask questions back in dry wit, cryptic, and skeptical style.' 

    # user_prompt = preamble + user_prompt

    all_messages = [
        {
        "role": "system", "content": preamble
        },
        
        ]
    if history is not None and len(history): # assume pd.DataFrame
        for key, x in history.T.to_dict().items():
            print(x)
            all_messages.append({"role": "user", "content": x['prompt']})
            all_messages.append({"role": "assistant", "content": x['&.ai']})
    
    all_messages.append({"role": "user", "content": context + user_prompt})
    print(all_messages)
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo", 
    messages= all_messages
    )
    calc_cost(completion.get("usage"))

    return completion

def calc_cost(usage: dict) -> None:
    total_tokens = usage.get("total_tokens")
    prompt_tokens = usage.get("prompt_tokens")
    completion_tokens = usage.get("completion_tokens")
    st.session_state.total_tokens.append(total_tokens)
    # pricing logic: https://openai.com/pricing#language-models
    if st.session_state.model_name == "gpt-3.5-turbo":
        cost = total_tokens * 0.002 / 1000
    else:
        cost = (prompt_tokens * 0.03 + completion_tokens * 0.06) / 1000
    st.session_state['total_cost'] += cost

def openai_data_call(outfile, the_ask, data):
    all_messages = []
    og_user_prompt = str(data) + ' \n ' + the_ask
    all_messages.append({'role':'system', 'content': 'Only response in JSON format / copyable code.'})
    all_messages.append({"role": "user", "content": og_user_prompt})
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo", 
    messages= all_messages
    )

    response = completion.choices[0].message.content
    calc_cost(completion.get("usage"))
    # st.swrite(str(response))
    st.sidebar.code('OpenAI response:')
    st.sidebar.json(completion, expanded=False)
    with open(outfile,'a', newline='') as f:
        writer = csv.writer(f)
        cont = str(completion.choices[0].message.content)
        createtime = (completion.created)
        writer.writerow([og_user_prompt, createtime, cont]) 

def openai_idea_clusters(user_nom, data):
    the_ask = 'summarize above ideas. create N clusters of M pieces of information here, each with annotated heat scores. format it in python array like [[{"heat_score": 0-100, "information":"str", "prompts":[1683401273000, ...]}, ...], [], ...]'
    outfile = user_nom+'_ideation.csv'
    openai_data_call(outfile, data, the_ask)


def openai_movie_timeline(user_nom, data):
    the_ask =   """write a timeline for a movie using the information above, mimicking this formating scheme:
      {    
    "events": [
      {
        "media": {
          "url": "",
          "caption": ""
        },
        "start_date": {
          "year": "2023"
        },
        "text": {
          "headline": "",
          "text": ""
        }
      },
      ...
      ]
      } 
    """
    outfile = user_nom+'_timeline.csv'
    openai_data_call(outfile, data, the_ask)

def openai_character_profiles(user_nom, data):
    the_ask =   """  you are a creative writing partner for a new movie. using the above information (be loose with the designs and maximize dramatic effect), build character profiles in JSON format like this:  {
    "characters": [
        {
        "name": "",
        "description": "",
        "picture_url": ""
        },
    ]}
    """
    outfile = user_nom+'_profiles.csv'
    openai_data_call(outfile, data, the_ask)



def openai_call(user_nom, mode, history=None): 
    response  = ""
    with st.container():
        chatconvo, yourconvo  = st.columns(2)

    if 'something' not in st.session_state:
        st.session_state.something = ''

    def submit():
        st.session_state.something = st.session_state.widget
        st.session_state.widget = ''
        og_user_prompt = str(st.session_state.something)
        yourconvo.write(og_user_prompt)
        chatconvo.write(' '*len(og_user_prompt)+'\n')
        # st.warning(st.session_state.something)
        if len(og_user_prompt):
            completion = call_openai_gpt(st.session_state.something, mode, history)
            response = completion.choices[0].message.content
            chatconvo.write(str(response))
            yourconvo.write(' '*len(response)+'\n')
            st.sidebar.json(completion, expanded=False)
            with open(user_nom+'_database.csv','a', newline='') as f:
                writer = csv.writer(f)
                cont = str(completion.choices[0].message.content)
                createtime = (completion.created)
                writer.writerow([og_user_prompt, mode, createtime, cont]) 
    col1,_ = st.columns([10,1])
    col1.text_area('', height=2, key='widget', on_change=submit)
        


