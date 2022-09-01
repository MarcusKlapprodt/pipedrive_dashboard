import pandas as pd
import requests
import json
import datetime
import os
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
import datetime
from plotly import graph_objects as go

# Sync API Key
api_key = ''

with open('.key.json') as json_file:
    data = json.load(json_file)
    api_key = data['api_key']
    

# Setup Activities Table
activities = ['sc_anruf', 'online_demo','meeting','task','onboarding__user_training','mapping_telco__test','email','sc_anruf_nicht_erreicht','chat','call', 'anruf_nicht_erreicht','online_demo_vereinbart','ib_anruf_entscheider','ib_anruf_nicht_erreicht','ib_online_demo_vereinbart','anruf','anruf_nicht_erreicht1','xing'] 

# Get Users
with open('keys/users.json') as users: 
    user_id = json.load(users)
print(user_id)

#CS Activities

def getCS(SuccessManager, start_date, end_date):
    request_url = 'https://api.pipedrive.com/v1/activities?user_id=' + user_id[SuccessManager] + '&limit=200&start=0&start_date=' + start_date + '&end_date=' + end_date + '&done=1&api_token=' + api_key
    data = json.loads(requests.get(request_url).content)
    if data['data'] == None:
        d = {'due_date': [start_date,end_date], 'type': ['sc_anruf','user_training'], 'org_name': [0,0], 'person_name': [0,0], 'deal_title': [0,0],'note': [0,0],'done':[0,0], 'sc_anruf':[0,0],'user_training':[0,0],'meeting':[0,0],'mapping':[0,0],'task':[0,0],'nicht_erreicht':[0,0]}
        cs_df  = pd.DataFrame(data=d)
    else:        
        cs_df = pd.json_normalize(data['data'])[['due_date', 'type', 'org_name', 'person_name', 'deal_title', 'note', 'done']]
        # split 'type' into different columns
        cs_df['sc_anruf'] = cs_df.apply(lambda x: 1 if x.type=='sc_anruf' and x.done ==True else 0, axis=1)
        cs_df['user_training'] = cs_df.apply(lambda x: 1 if x.type=='onboarding__user_training' and x.done ==True else 0, axis=1)
        cs_df['meeting'] = cs_df.apply(lambda x: 1 if x.type=='meeting' and x.done ==True else 0, axis=1)
        cs_df['mapping'] = cs_df.apply(lambda x: 1 if x.type=='mapping_telco__test' and x.done ==True else 0, axis=1)
        cs_df['task'] = cs_df.apply(lambda x: 1 if x.type=='task' and x.done ==True else 0, axis=1)
        cs_df['nicht_erreicht'] = cs_df.apply(lambda x: 1 if x.type=='anruf_nicht_erreicht1' and x.done ==True else 0, axis=1)
    
    return cs_df

def getSumCS(SuccessManager, start_date, end_date):
    csSumDf = getCS(SuccessManager, start_date, end_date).groupby('due_date').sum().reset_index()
    csSumDf.loc[:, 'date'] = pd.to_datetime(csSumDf['due_date'], format='%Y-%m-%d')
    
    # Drop second Date column
    csSumDf.drop('due_date', axis=1, inplace=True)
     
    # Set date as first column
    col_name="date"
    first_col = csSumDf.pop(col_name)
    csSumDf.insert(0, col_name, first_col)
    csSumDf.loc[:, 'date']= csSumDf['date'].dt.strftime('%d/%m/%Y')
    
    # get cumulated Sums
    csSumDf['a_sc_anruf'] = csSumDf['sc_anruf'].cumsum()
    csSumDf['a_training'] = csSumDf['user_training'].cumsum()
    csSumDf['a_meeting'] = csSumDf['meeting'].cumsum()
    csSumDf['a_mapping'] = csSumDf['mapping'].cumsum()
    csSumDf['a_task'] = csSumDf['task'].cumsum()
    csSumDf['a_nicht_erreicht'] = csSumDf['nicht_erreicht'].cumsum()
    
    # Render all numbers to int except date
    intCols = csSumDf.columns[1:]
    csSumDf[intCols] = csSumDf[intCols].astype(int)
    
    return csSumDf   
 

def mChurns(month): 
    chosenMonth = month

    excelFile = "/mnt/c/Users/MarcusKlapprodt/snapADDY GmbH/snapADDY Intranet - 02_Customer Success/05_Business_Intelligence/Churn Rate_Recurring.xlsm"
    excelDf = pd.read_excel(excelFile, sheet_name='DQ Kündigungen')
    churns = excelDf.loc[(excelDf['Monat'] == chosenMonth) & ((excelDf['Kündigungsart'] == 'Buchungskündigung') | (excelDf['Kündigungsart'] == 'Kündigung')) ]
    churns = churns[['Firmenname', 'Gekündigt am','Gekündigt zum','Nettobetrag','CS Manager','Kündigungsart','Kündigungsgrund','Produktkategorie']].sort_values('Nettobetrag', ascending=False)
    churns['Nettobetrag'] = churns['Nettobetrag'].astype('int32')
    
    totalChurn = '{:20,.2f}'.format(churns['Nettobetrag'].sum(skipna = True))

    MonthlyChurns = churns.style.set_caption('Churns in {} - Gesamtsumme = {}'.format(chosenMonth, totalChurn))\
                .hide_index()\
                .bar(subset=['Nettobetrag'], color='#FE6C36')\
                .apply(lambda x: ['color: #9da600 ; font-weight: bold' if v ==  'Buchungskündigung' else "" for v in x], axis = 1)
    
    #MonthlyChurns.format({'Nettobetrag':'{:.2}'})
    
    return MonthlyChurns


# Bigger Chart for all four activities

def csKpiTotal(dataFrame, minOne, minTwo, minThree, minFour):
    fig = go.Figure()
    fig = make_subplots(rows=2, cols=2, subplot_titles=('Success Calls', 'Metings', 'Onboardings','Mappings'))
    
    # Success Calls
    fig.add_trace(
        go.Scatter(
            x=dataFrame.date,
            y=dataFrame['a_sc_anruf'],
            name='Success Calls',
            line={'color':'red'}
        ),row=1, col=1)

    fig.add_trace(
        go.Scatter(
            x=dataFrame.date,
            y=[minOne,minOne,minOne,minOne,minOne,minOne,minOne], 
            name='SC-Calls Breakline', 
            line={'color':'lightpink'}
        ),row=1, col=1)

    # Meetings
    fig.add_trace(
        go.Scatter(
            x=dataFrame.date,
            y=dataFrame['a_meeting'],
            name='Metings',
            line={'color':'blue'}
        ),row=1, col=2)

    fig.add_trace(
        go.Scatter(
            x=dataFrame.date,
            y=[minTwo,minTwo,minTwo,minTwo,minTwo,minTwo,minTwo], 
            name='Meetings Breakline', 
            line={'color':'lightblue'}
        ),row=1, col=2)
    
        # Onboardings
    fig.add_trace(
        go.Scatter(
            x=dataFrame.date,
            y=dataFrame['a_training'],
            name='Onb./ Trainigs',
            line={'color':'green'}
        ),row=2, col=1)

    fig.add_trace(
        go.Scatter(
            x=dataFrame.date,
            y=[minThree,minThree,minThree,minThree,minThree,minThree,minThree], 
            name='Onboardings Breakline', 
            line={'color':'lightgreen'}
        ),row=2, col=1)
    
            # Mappings
    fig.add_trace(
        go.Scatter(
            x=dataFrame.date,
            y=dataFrame['a_mapping'],
            name='Onb./ Trainigs',
            line={'color':'yellow'}
        ),row=2, col=2)

    fig.add_trace(
        go.Scatter(
            x=dataFrame.date,
            y=[minFour,minFour,minFour,minFour,minFour,minFour,minFour], 
            name='Meetings Breakline', 
            line={'color':'lightgoldenrodyellow'}
        ),row=2, col=2)

    fig.update_layout(template='plotly_dark', legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1),height=600, showlegend=False)
    return fig


def getUsers():
    request_url = 'https://api.pipedrive.com/v1/users?&api_token=' + api_key
    data = json.loads(requests.get(request_url).content)
    return data

## Test
# def scatter(dataFrame, activity, plotname, color, rownum, colnum): 
#     string = 'go.Scatter(x={}.date,y={}[\'{}\'],name=\'{}\',line={{\'color\':\'{}\'}}),row={}, col={})'.format(dataFrame, dataFrame, activity, plotname, color, colnum, colnum)
#     return string
