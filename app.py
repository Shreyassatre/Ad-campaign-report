import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

data = pd.read_csv('Data Analyst _ Sample Data _HDM.csv')

# campaign performance report
def generate_campaign_performance_report(advertiser_filter):
    total_calls = data['Call Id'].nunique()
    unique_leads = data['Lead Id'].nunique()

    # Assuming 'completed' and 'in-progress' represent connected calls
    connected_call_statuses = ['completed', 'in-progress']
    calls_connected = data[data['Call Status'].isin(connected_call_statuses)]['Call Id'].count()
    unique_calls_connected = data[data['Call Status'].isin(connected_call_statuses)]['Lead Id'].nunique()

    leads_converted = data[data['Lead Status'] == 'Interested']['Call Id'].count()
    qualified_leads = data[(data['Lead Status'] == 'Interested') & (data['Advertiser Id'] == advertiser_filter)]['Call Id'].count()
    leads_lost = data[data['Lead Status'] == 'Not Interested']['Call Id'].count()
    avg_agent_duration = data['Agent Duration(seconds)'].mean()
    avg_customer_duration = data['Customer Duration(seconds)'].mean()

    #Metric
    report_data = {
        'Metric': ['Total calls', 'Unique leads', 'Calls connected', 'Unique calls connected',
                   'Leads converted', 'Qualified leads', 'Leads lost',
                   'Average agent call duration (seconds)', 'Average customer call duration (seconds)'],
        'Value': [total_calls, unique_leads, calls_connected, unique_calls_connected,
                  leads_converted, qualified_leads, leads_lost,
                  avg_agent_duration, avg_customer_duration]
    }
    report_df = pd.DataFrame(report_data)

    return report_df

# lead disposition report
def generate_lead_disposition_report():
    lead_status_distribution = data['Lead Status'].value_counts().reset_index()
    lead_status_distribution.columns = ['Lead Status', 'Count']
    return lead_status_distribution

# agent performance report
def generate_agent_performance_report():
    agent_performance = data.groupby('Agent Id')[['Call Id', 'Call Status', 'Lead Status', 'Agent Duration(seconds)', 'Customer Duration(seconds)']].agg({
        'Call Id': 'count',
        'Call Status': lambda x: ((x == 'completed') | (x == 'in-progress')).astype(int).sum(),
        'Lead Status': lambda x: (x == 'Interested').sum(),
        'Agent Duration(seconds)': 'mean',
        'Customer Duration(seconds)': 'mean'
    }).reset_index()
    agent_performance.columns = ['Agent Id', 'Calls Made', 'Calls Connected', 'Leads Converted', 'Avg Agent Duration', 'Avg Customer Duration']
    return agent_performance

def generate_additional_report():
    if selected_visualization == 'Call Status Distribution':
        call_status_dist = data['Call Status'].value_counts().reset_index()
        call_status_dist.columns = ['Call Status', 'Count']
        fig, ax = plt.subplots()
        ax = sns.barplot(x='Call Status', y='Count', data=call_status_dist)
        ax.set_title('Call Status Distribution')
        ax.set_xlabel('Call Status')
        ax.set_ylabel('Count')
        st.pyplot(fig)

    elif selected_visualization == 'Lead Status Distribution':
        lead_status_dist = data['Lead Status'].value_counts().reset_index()
        lead_status_dist.columns = ['Lead Status', 'Count']
        fig, ax = plt.subplots(figsize=(8, 6))
        colors = sns.color_palette("pastel")
        ax.pie(lead_status_dist['Count'], colors=colors, autopct='')
        ax.axis('equal')  
        ax.set_title('Lead Status Distribution')

        label_template = "{0} ({1:.0f})"
        labels = [label_template.format(row[0], row[1]) for row in lead_status_dist.values]
        ax.legend(labels, loc='center right', bbox_to_anchor=(1.4, 0.5), fontsize=10, labels=lead_status_dist['Lead Status'])
        st.pyplot(fig)

    elif selected_visualization == 'Agent Performance':
        agent_performance = data.groupby('Agent Id')[['Call Id', 'Call Status', 'Lead Status', 'Agent Duration(seconds)', 'Customer Duration(seconds)']].agg({
            'Call Id': 'count',
            'Call Status': lambda x: ((x == 'completed') | (x == 'in-progress')).astype(int).sum(),
            'Lead Status': lambda x: (x == 'Interested').sum(),
            'Agent Duration(seconds)': 'mean',
            'Customer Duration(seconds)': 'mean'
        }).reset_index()
        agent_performance.columns = ['Agent Id', 'Calls Made', 'Calls Connected', 'Leads Converted', 'Avg Agent Duration', 'Avg Customer Duration']
        selected_metric = st.selectbox('Select Metric', ['Calls Made', 'Calls Connected', 'Leads Converted', 'Avg Agent Duration', 'Avg Customer Duration'])
        
        fig = plt.figure(figsize=(10, 8))
        sns.barplot(x=selected_metric, y='Agent Id', data=agent_performance, palette='viridis',orient='h')

        plt.xlabel(selected_metric)
        plt.ylabel('Agent Id')
        plt.title('Agent Performance by {}'.format(selected_metric))

        st.pyplot(fig)


st.title('Advertisement Campaign Reports')

report_option = st.sidebar.selectbox('Select Report', ['Campaign Performance', 'Lead Disposition', 'Agent Performance', 'Additional Reports'])
advertiser_filter = st.sidebar.selectbox('Select Advertiser', options=data['Advertiser Id'].unique().tolist())

if report_option == 'Campaign Performance':
    st.subheader('Campaign Performance Report')
    st.write(generate_campaign_performance_report(advertiser_filter))
elif report_option == 'Lead Disposition':
    st.subheader('Lead Disposition Report')
    st.write(generate_lead_disposition_report())
elif report_option == 'Agent Performance':
    st.subheader('Agent Performance Report')
    st.write(generate_agent_performance_report())
else:
    st.subheader('Additional Reports')
    selected_visualization = st.selectbox('Select Visualization', ['Call Status Distribution', 'Lead Status Distribution', 'Agent Performance'])
    generate_additional_report()