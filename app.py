
import pandas as pd
import streamlit as st
import datetime
import os
import openai
from helpers import openai_call
from streamlit_ws_localstorage import injectWebsocketCode, getOrCreateUID
from streamlit_timeline import timeline
# from streamlit_card import card
from constants import EXAMPLE_PROFILE, EXAMPLE_TIMELINE
st.set_page_config(
    '&.ai',
    layout='wide',
    page_icon="&.ai"
)

@st.cache_data
def setup():
    conn = injectWebsocketCode(hostPort='linode.liquidco.in', uid=getOrCreateUID())
    return conn.getLocalStorageVal(key='k1')


def main():
    col1, _ = st.columns([1,6])

    col1.title(':blue[_&_].', anchor='&.')

    current_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    # Main call to the api, returns a communication object
    ret = setup()
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
            conn = injectWebsocketCode(hostPort='linode.liquidco.in', uid=getOrCreateUID())
            ret1 = conn.setLocalStorageVal(key='k1', val=user_nom)
            # st.warning(ret1)
            if 'success' not in str(ret1):
                st.warning('failed to create user')     
            else:  
                needs_to_create_user_account = False     
            is_clicked = False
    else:
        wow1, wow2 = st.columns([5,1])
        wow1.success('Welcome back '+ ret+'! 🎬📝', icon='💡')
        is_signedout = wow2.button('sign out')
        if is_signedout:
            conn = injectWebsocketCode(hostPort='linode.liquidco.in', uid=getOrCreateUID())
            ret1 = conn.setLocalStorageVal(key='k1', val='')
            needs_to_create_user_account = True 
            user_nom = ""
        user_nom = str(ret)


    # st.title('A title with _italics_ :blue[colors] and emojis :sunglasses:')
    # col2.write('')
    # col2.write('')
    # col2.write('')
    # col2.write(current_time)
    if not needs_to_create_user_account:
        modes = ['ms.j', 'mr.k', 'mr.z']
        mode = modes[0]
        # col3.write('')
        # col3.write('')
        with st.expander('settings'):
            col22, col3 = st.columns([1,1])
            mode = col3.radio('mode:', modes)
            OPENAI_API_KEY = col22.text_input('OPENAI_API_KEY', '')
            if OPENAI_API_KEY!='' and len(OPENAI_API_KEY) > 4:
                os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
                openai.api_key = OPENAI_API_KEY

        tabs = st.tabs(['chat', 'history', 'outline', 'profiles'])
        database_df = pd.DataFrame()
        with tabs[0]:
            if os.environ.get('OPENAI_API_KEY', None):
                openai_call(user_nom, mode)
            else:
                st.warning('please update `OPENAI_API_KEY` in the settings')

            if os.path.exists(user_nom+'_database.csv'):
                database_df = pd.read_csv(user_nom+'_database.csv', header=None)
                database_df.columns = ['prompt', 'mode', 'unix_timestamp', '&.ai']
                database_df.index = pd.to_datetime(database_df['unix_timestamp']*1e9)
                database_df_to_download = database_df.to_csv().encode('utf-8')
                col22.download_button(
                    label="download database [bytes="+str(len(database_df))+"]",
                    data=database_df_to_download,
                    file_name='database.csv',
                    mime='text/csv',
                )

        with tabs[1]:
            st.dataframe(database_df)
        with tabs[2]:
            do_update1 = st.button('update',key='outline-update')
            timeline_file = user_nom+'_timeline.json'
            data = None
            if os.path.exists(timeline_file):
                # load data
                with open(timeline_file, "r") as f:
                    data = f.read()
                # render timeline
            else:
               data =  EXAMPLE_TIMELINE
            timeline(data, height=800)

        with tabs[3]:
            do_update2 = st.button('update',key='profile-update')

            profiles = EXAMPLE_PROFILE
            col1, _, col2 = st.columns([4,1,4])
            for i,x in enumerate(profiles['characters']):
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

            # if do_update2:



if __name__ == '__main__':
    main()