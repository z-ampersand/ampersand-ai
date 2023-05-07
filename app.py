
import pandas as pd
import streamlit as st
import datetime
import os
import openai
from helpers import openai_call, openai_idea_clusters, openai_character_profiles, openai_movie_timeline
from streamlit_ws_localstorage import injectWebsocketCode, getOrCreateUID
from streamlit_timeline import timeline
from glob import glob
import json
# from streamlit_card import card
from constants import EXAMPLE_PROFILE, EXAMPLE_TIMELINE
st.set_page_config(
    '&.ai',
    layout='wide',
    page_icon="&.ai"
)
import plotly.express as px
# from streamlit_plotly_events import plotly_events

conn = injectWebsocketCode(hostPort='linode.liquidco.in', uid=getOrCreateUID())

# @st.cache_data
# def setup():
#     conn = injectWebsocketCode(hostPort='linode.liquidco.in', uid=getOrCreateUID())
#     return conn.getLocalStorageVal(key='k1')

def login_logic():
    ret = conn.getLocalStorageVal(key='k1')
    needs_to_create_user_account = len(str(ret))==0
    if needs_to_create_user_account:
        col1, col2 = st.columns([4,1])
        user_nom = col1.text_input('select your user name:')
        col2.write('\n\n')
        col2.write('\n\n')
        is_clicked = col2.button('submit', key='account-create-submit')  
        if is_clicked and len(user_nom):
            # if os.path.exists(user_nom+'_database.csv'):
            #     st.warning('USER NAME "'+str(user_nom)+'" IS ALREADY TAKEN.')
            # else:        
            # st.warning('setting into localStorage')
            ret1 = conn.setLocalStorageVal(key='k1', val=user_nom)
            # st.warning(ret1)
            if 'success' not in str(ret1):
                st.warning('failed to create user')     
            else:  
                needs_to_create_user_account = False     
            is_clicked = False
        elif is_clicked and len(user_nom) == 0:
            st.warning('must add user name above')
    else:
        wow1, wow2 = st.columns([5,1])
        wow1.success('Welcome back '+ ret+'! 🎬📝', icon='💡')
        is_signedout = wow2.button('sign out')
        if is_signedout:
            # conn = injectWebsocketCode(hostPort='linode.liquidco.in', uid=getOrCreateUID())
            ret1 = conn.setLocalStorageVal(key='k1', val='')
            needs_to_create_user_account = True 
            user_nom = ""
        user_nom = str(ret)
    return user_nom, needs_to_create_user_account

def make_sidebar():
    user_nom = ''
    st.sidebar.title("&. Settings")
    if 'model_name' not in st.session_state:
        st.session_state['model_name'] = []
    if 'cost' not in st.session_state:
        st.session_state['cost'] = []
    if 'total_tokens' not in st.session_state:
        st.session_state['total_tokens'] = []
    if 'total_cost' not in st.session_state:
        st.session_state['total_cost'] = 0.0

    model_name = st.sidebar.radio("Choose a model:", ("GPT-3.5", "GPT-4"), horizontal=True)
    counter_placeholder = st.sidebar.empty()
    counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")
    # clear_button = st.sidebar.button("Clear Conversation", key="clear")
    modes = ['ms.j', 'mr.k', 'mr.z']
    mode = modes[0]
    # col3.write('')
    # col3.write('')
    doveride = st.sidebar.radio('user name override:', [True, False], index=1, horizontal=True)
    if doveride:
        ffs = [x.split('_')[0] for x in glob('*_database.csv')]
        user_nom = st.sidebar.selectbox('dataset:', ffs)
    with st.sidebar.expander('settings'):
        col22, col3 = st.columns([1,1])
        mode = col3.radio('mode:', modes)
        OPENAI_API_KEY = col22.text_input('OPENAI_API_KEY', '')
        if OPENAI_API_KEY!='' and len(OPENAI_API_KEY) > 4:
            os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
            openai.api_key = OPENAI_API_KEY

    return mode, user_nom

def load_dataframe_json_from_csv(ff):
    df = pd.read_csv(ff, header=None)
    df.columns = ['prompt', 'unix_timestamp', 'result'] 
    most_recent_ideamap = df['result'].values[-1]
    most_recent_ideamap = str(most_recent_ideamap)
    flipped = most_recent_ideamap[::-1]
    x = most_recent_ideamap.index('[')
    xend = -(flipped.index(']'))
    # st.write(x, xend)
    if xend != 0:
        st.sidebar.write('ideamap indexes:', x, xend)
        most_recent_ideamap = most_recent_ideamap[x:xend]
    try:
        dd = json.loads(most_recent_ideamap)
    except:
        st.warning(ff + ' json decode failed!')
        dd = {} 
    return df, dd

def main():
    mode, user_nom = make_sidebar()
    col1, _ = st.columns([1,6])
    col1.title(':blue[_&_].', anchor='&.')

    current_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    # Main call to the api, returns a communication object
    # ret = setup()
    needs_to_create_user_account = False
    if user_nom == '':
        user_nom, needs_to_create_user_account = login_logic()



    # st.title('A title with _italics_ :blue[colors] and emojis :sunglasses:')
    # col2.write('')
    # col2.write('')
    # col2.write('')
    # col2.write(current_time)
    if not needs_to_create_user_account:


        tabs = st.tabs(['chat', 'history', 'ideation', 'outline', 'profiles'])
        database_df = pd.DataFrame()
        with tabs[0]:
            if os.path.exists(user_nom+'_database.csv'):
                database_df = pd.read_csv(user_nom+'_database.csv', header=None)
                database_df.columns = ['prompt', 'mode', 'unix_timestamp', '&.ai']
                database_df.index = pd.to_datetime(database_df['unix_timestamp']*1e9)
                database_df_to_download = database_df.to_csv().encode('utf-8')
                st.sidebar.download_button(
                    label="download database [bytes="+str(len(database_df))+"]",
                    data=database_df_to_download,
                    file_name='database.csv',
                    mime='text/csv',
                )
            if os.environ.get('OPENAI_API_KEY', None):
                openai_call(user_nom, mode, database_df)
            else:
                st.warning('please update `OPENAI_API_KEY` in the settings')

        with tabs[1]:
            st.dataframe(database_df)
            # hist_json = database_df[['prompt', '&.ai']].T.to_json()
            # st.json(hist_json)
        
        idea_file = user_nom+'_ideation.csv'
        idea_df = None
        with tabs[2]:
            do_update1 = st.button('update',key='idea-update')
            if do_update1:
                    dat = database_df[['prompt', '&.ai']].T.to_json()
                    openai_idea_clusters(user_nom, dat)
                    do_update1 = False
            if os.path.exists(idea_file):
                df, dd = load_dataframe_json_from_csv(idea_file)
            tabs2 = st.tabs(['summary', 'chart'])
            idea_df = pd.DataFrame()

            with tabs2[0]:
                if dd:
                    idea_df = pd.concat([pd.DataFrame(x) for x in dd])
                    idea_df = pd.concat([pd.DataFrame(x) for x in dd])
                    idea_df['promptLevel'] = idea_df['prompts'].apply(lambda x: sum(x)/len(x))
                    idea_df['promptTime'] = pd.to_datetime(idea_df['promptLevel']*1e6)
                    idea_df['y'] = idea_df['heat_score']**2
                    for x in idea_df['information'].values:
                        st.write('> ' + x)
            with tabs2[1]:
                plotly_st, = st.columns(1)
                with st.expander('raw data'):
                    st.dataframe(df)
                    st.json(dd, expanded=False)
                    st.dataframe(idea_df)
                if dd:
                    fig = px.scatter(idea_df, x="promptTime", y="y",
                    size="heat_score", color="heat_score",
                        hover_name="information", 
                        #  log_x=True,
                        size_max=60)
                        # selected_points = plotly_events(fig)
                    plotly_st.plotly_chart(fig, True)
                # if len(selected_points):
                #     st.dataframe(pd.concat([pd.DataFrame.from_dict(a,orient='index') for a in selected_points]))


        with tabs[3]:
            if os.path.exists(idea_file):
                do_update1 = st.button('update',key='outline-update')
                if do_update1:
                    dat = '. '.join(idea_df['information'].values.tolist())
                    openai_movie_timeline(user_nom, dat)
                    do_update1 = False
                timeline_file = user_nom+'_timeline.csv'
                data = None
                if os.path.exists(timeline_file):
                    df, data = load_dataframe_json_from_csv(timeline_file)
                    st.json(data, expanded=False)
                    # load data
                    # with open(timeline_file, "r") as f:
                    #     data = f.read()
                    # render timeline
                else:
                    data =  EXAMPLE_TIMELINE

                if isinstance(data, list) or data.get('events', None):
                    data = {'events': data}
                timeline(data, height=800)

        with tabs[4]:
            profiles_file = user_nom+'_profiles.csv'
            if os.path.exists(idea_file):
                do_update2 = st.button('update',key='profile-update')
                if do_update2:
                    dat = '. '.join(idea_df['information'].values.tolist())
                    openai_character_profiles(user_nom, dat)
                    do_update2 = False
                profiles = None
                if os.path.exists(profiles_file):
                    # profiles = EXAMPLE_PROFILE['characters']
                    df, dd = load_dataframe_json_from_csv(profiles_file)
                    profiles = dd
                st.json(profiles, expanded=False)
                if profiles is not None:
                    col1, _, col2 = st.columns([4,1,4])
                    for i,x in enumerate(profiles):
                        if i % 2 == 0:
                            col1.header(x['name'])
                            col1.slider('fluidity', key='char-'+str(i), value=5, min_value=0, max_value=10)
                            col1.write(x['description'])
                            col1.write(' ')
                        else:
                            col2.header(x['name'])
                            col2.slider('fluidity', key='char-'+str(i), value=9, min_value=0, max_value=10)
                            col2.write(x['description'])
                            col2.write(' ')
                else:
                    st.write('click update to build profiles')
            # if do_update2:



if __name__ == '__main__':
    main()