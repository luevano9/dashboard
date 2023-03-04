import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# Set the theme

df = pd.read_csv('MOCK_DATA.csv')
st.sidebar.title('Choose your parameter')
week = sorted(df['Week'].unique().tolist())
week.insert(0,'Overall')

options = st.sidebar.radio('Select an Option',('Overall','Site','Ops','QA'))
week_num = st.sidebar.selectbox("Select the week", week)

if week_num == "Overall":
    data = df
else:
    data = df[df['Week']==week_num]

gm = data['Manager'].unique().tolist()
gm.append('All')
ops =  data['Operations'].unique()
site = data['Site'].unique().tolist()
qa = data['QA login'].unique().tolist()
qa.append('All')


if options == 'Overall':
    st.write("<h1 style='text-align: center;'>Overall Analysis</h1>", unsafe_allow_html=True)
    col1, col2, col3= st.columns(3)
    with col1:
        st.header("Contacts Audited")
        st.header(data.shape[0])
    with col2:
        st.header('Policy Adherence')
        a = (data[data['Policy Adherence'] == 'Adhered'].shape[0] / data.shape[0])
        percentage = "{:.2%}".format(a)
        st.header(percentage)
    with col3:
        st.header('Policy Deviated')
        a = (data[data['Policy Adherence'] == 'Deviated'].shape[0] / data.shape[0])
        percentage = "{:.2%}".format(a)
        st.header(percentage)

    col4, col5 = st.columns(2)
    with col4:
        df2 = data['Policy Adherence']
        df2 = pd.DataFrame(df2)
        yes_percent = df2[df2['Policy Adherence'] == 'Adhered'].count() / len(df2)
        # Create the pie chart using plotly express
        fig = px.pie(df2, values=[yes_percent[0], 1 - yes_percent[0]], names=['Adhered', 'Deviated'],
                     color_discrete_sequence=['green', 'lightblue'])
        fig.update_traces(hole=0.6, textinfo='none', hovertemplate='%{label}: %{value:.0%}')
        fig.add_annotation(x=0.5, y=0.5, text='Adherence: {:.0%}'.format(yes_percent[0]), showarrow=False,
                           font=dict(size=19, color='white'))
        # Add title and labels
        fig.update_layout(title='Adherence Percentage', font_size=16)
        fig.update_traces(rotation=0, direction='clockwise', textposition='inside')
        st.plotly_chart(fig,use_container_width=True,width=300, height=100)

    with col5:
        counts2 = data.groupby(["Site", "Policy Adherence"]).size().reset_index(name="Count")
        total_counts = counts2.groupby("Site")["Count"].transform("sum")
        counts2["Percent"] = counts2["Count"] / total_counts * 100
        color_map = {"Adhered": "green", "Deviated": "red"}
        # Create a Sunburst chart with plotly.express

        fig2 = px.sunburst(counts2, path=["Site", "Policy Adherence"], values="Count", color="Policy Adherence",
                           color_discrete_map=color_map)
        fig2.update_layout(title="SiteWise Adherence Distribution", font_size=16)
        st.plotly_chart(fig2, use_container_width=False, width=300, height=100)

    if week_num == "Overall":
        percentage = df
    elif (int(week_num) <= 4) & (int(week_num)>1):
        percentage = df[df['Week'] <= int(week_num)]
    else:
        percentage = df[df['Week'] > int(week_num) - 4]

    st.title("Past Week bps")
    total_contacts = percentage.pivot_table(index='Site', columns='Week', values='Contact id', aggfunc='count')
# Calculate number of deviated contacts for each site and week
    deviated_contacts = percentage[percentage['Policy Adherence'] == "Deviated"].pivot_table(index='Site', columns='Week',
                                                                                 values='Contact id', aggfunc='count')
# Calculate percentage of deviated contacts out of total contacts for each site and week
    deviation_percentage = round((deviated_contacts / total_contacts) * 100, 2)
# Add a new column for the mean of all weeks
    deviation_percentage['Mean'] = deviation_percentage.mean(axis=1)
# Add a new column for the difference between last week and second last week
    deviation_percentage['Bps'] = round((deviation_percentage.iloc[:, -2] - deviation_percentage.iloc[:, -3]) * 100,2)
# Rename the columns to remove the multi-level indexing
    deviation_percentage.columns = list(deviation_percentage.columns[:-2]) + ['Average', 'Bps']
    deviation_percentage = deviation_percentage.reset_index()
# Print the resulting pivot table
    st.table(deviation_percentage)

    try:
        # Plot percentage on a line chart
        st.title('Past Weeks Adherence Trend')
        percentage = df.groupby('Week')['Policy Adherence'].apply(lambda x: (x == 'Adhered').mean() * 100).reset_index()
        if week_num == "Overall":
            pass
        elif int(week_num) <= 4:
            percentage = percentage[percentage['Week'] < int(week_num) + 1]
        else:
            percentage = percentage[percentage['Week'] > int(week_num) - 4]

        percentage['Policy Adherence'] = round(percentage['Policy Adherence'], 2)

        fig = px.line(percentage, x='Week', y='Policy Adherence', title='Percentage of "Yes" Responses by Week', width=300)
        fig.update_traces(mode='lines+markers', marker=dict(color='yellow'))
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(gridcolor='lightgray'),
            yaxis=dict(gridcolor='lightgray'),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Plot Annotations on a line chart
        st.title('Past Weeks Invalid Annotations Trends')
        percentage = df.groupby('Week')['Annotations'].apply(lambda x: (x == 'Valid').mean() * 100).reset_index()
        if week_num == "Overall":
            pass
        elif int(week_num) <= 4:
            percentage = percentage[percentage['Week'] < int(week_num) + 1]
        else:
            percentage = percentage[percentage['Week'] > int(week_num) - 4]
        percentage['Annotations'] = round(percentage['Annotations'], 2)

        fig = px.line(percentage, x='Week', y='Annotations', title='Percentage of "Yes" Responses by Week')
        fig.update_traces(mode='lines+markers', marker=dict(color='yellow'))
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(gridcolor='lightgray'),
            yaxis=dict(gridcolor='lightgray'),
        )
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.write("Due to some error, unable to show the data")

elif options == 'Site':
    st.title('Sitewise Analysis')
    selected_site = st.selectbox('Select the site', sorted(site))
    data = data[data['Site'] == selected_site]
    col1, col2 = st.columns(2)
    with col1:
        st.header("Contacts Audited")
        st.header(data.shape[0])
    with col2:
        st.header('Policy Adherence')
        a = (data[data['Policy Adherence'] == 'Adhered'].shape[0] / data.shape[0])
        percentage = "{:.2%}".format(a)
        st.header(percentage)

    col3, col4 = st.columns(2)
    with col3:
        counts = data["Policy Adherence"].value_counts()

        # Create a Pie chart with plotly.express
        fig = px.pie(data, values=counts, names=counts.index, title="Policy Adherence")
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.header('Impact Table')
        tabs = data[data['Site'] == selected_site]['impact'].value_counts().reset_index(name='count')
        st.table(tabs)

    if week_num == "Overall":
        percentage = df
    elif (int(week_num) <= 4) & (int(week_num) > 1):
        percentage = df[df['Week'] <= int(week_num)]
    else:
        percentage = df[df['Week'] > int(week_num) - 4]

    percentage = percentage[percentage['Site'] == selected_site]
    st.title("Past Weeks bps")
    total_contacts = percentage.pivot_table(index='Site', columns='Week', values='Contact id', aggfunc='count')
    # Calculate number of deviated contacts for each site and week
    deviated_contacts = percentage[percentage['Policy Adherence'] == "Deviated"].pivot_table(index='Site',
                                                                                             columns='Week',
                                                                                             values='Contact id',
                                                                                             aggfunc='count')
    # Calculate percentage of deviated contacts out of total contacts for each site and week
    deviation_percentage = round((deviated_contacts / total_contacts) * 100, 2)
    # Add a new column for the mean of all weeks
    deviation_percentage['Mean'] = deviation_percentage.mean(axis=1)
    # Add a new column for the difference between last week and second last week
    deviation_percentage['Bps'] = round((deviation_percentage.iloc[:, -2] - deviation_percentage.iloc[:, -3]) * 100,
                                        2)
    # Rename the columns to remove the multi-level indexing
    deviation_percentage.columns = list(deviation_percentage.columns[:-2]) + ['Average', 'Bps']
    deviation_percentage = deviation_percentage.reset_index()
    # Print the resulting pivot table
    st.table(deviation_percentage)

#Policy fails Line chart
    st.title('Past Weeks Policy Adherence Trends')
    percentage = df[df['Site'] == selected_site].groupby('Week')['Policy Adherence'].apply(
        lambda x: (x == 'Adhered').mean() * 100).reset_index()
    if week_num == "Overall":
        pass
    elif int(week_num) <= 4:
        percentage = percentage[percentage['Week'] < int(week_num) + 1]
    else:
        percentage = percentage[percentage['Week'] > int(week_num) - 4]

    percentage['Policy Adherence'] = round(percentage['Policy Adherence'], 2)
        # Plot percentage on a line chart
    fig = px.line(percentage, x='Week', y='Policy Adherence', title='Percentage of "Yes" Responses by Week')
    fig.update_traces(mode='lines+markers', marker=dict(color='yellow'))
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor='lightgray'),
        yaxis=dict(gridcolor='lightgray'),
    )
    st.plotly_chart(fig,use_container_width=True)
# Annotations
    st.title('Past Weeks Invalid Annotations trends')
    percentage = df[df['Site'] == selected_site].groupby('Week')['Annotations'].apply(lambda x: (x == 'Valid').mean() * 100).reset_index()
    if week_num == "Overall":
        pass
    elif int(week_num) <= 4:
        percentage = percentage[percentage['Week'] < int(week_num) + 1]
    else:
        percentage = percentage[percentage['Week'] > int(week_num) - 4]
    percentage['Annotations'] = round(percentage['Annotations'], 2)
    fig = px.line(percentage, x='Week', y='Annotations', title='Percentage of "Yes" Responses by Week')
    fig.update_traces(mode='lines+markers', marker=dict(color='yellow'))
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor='lightgray'),
        yaxis=dict(gridcolor='lightgray'),
    )
    st.plotly_chart(fig, use_container_width=True)

elif options == 'Ops':
    st.title('Ops Analysis')
    selected_ops = st.selectbox('Select the Ops Name', sorted(ops))

    data = data[data['Operations'] == selected_ops]
    col1, col2 = st.columns(2)
    with col1:
        st.header("Contacts Audited")
        st.header(data.shape[0])
    with col2:
        st.header('Policy Adherence')
        a = (data[data['Policy Adherence'] == 'Adhered'].shape[0] / data.shape[0])
        percentage = "{:.2%}".format(a)
        st.header(percentage)

    col3, col4 = st.columns(2)
    with col3:
        counts = data["Policy Adherence"].value_counts()

        # Create a Pie chart with plotly.express
        fig = px.pie(data, values=counts, names=counts.index, title="Policy Adherence Distribution")
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        counts2 = data.groupby(["Site", "Policy Adherence"]).size().reset_index(name="Count")
        total_counts = counts2.groupby("Site")["Count"].transform("sum")
        counts2["Percent"] = counts2["Count"] / total_counts * 100
        color_map = {"Adhered": "green", "Deviated": "red"}
        # Create a Sunburst chart with plotly.express

        fig2 = px.sunburst(counts2, path=["Site", "Policy Adherence"], values="Count", color="Policy Adherence",
                           color_discrete_map=color_map, title="SiteWise Policy Adherence Distribution")
        st.plotly_chart(fig2, use_container_width=True)

# Plot percentage on a line chart
    st.title('Past 4 week')
    percentage = df[df['Operations'] == selected_ops].groupby('Week')['Policy Adherence'].apply(
        lambda x: (x == 'Adhered').mean() * 100).reset_index()
    if week_num == "Overall":
        pass
    elif int(week_num) <= 4:
        percentage = percentage[percentage['Week'] < int(week_num) +1]
    else:
        percentage = percentage[percentage['Week'] > int(week_num) - 4]
    percentage['Policy Adherence'] = round(percentage['Policy Adherence'], 2)

    fig = px.line(percentage, x='Week', y='Policy Adherence', title='Percentage of "Yes" Responses by Week')
    fig.update_traces(mode='lines+markers', marker=dict(color='yellow'))
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor='lightgray'),
        yaxis=dict(gridcolor='lightgray'),
    )
    st.plotly_chart(fig, use_container_width=True)

#Display Fails contact details
    tm = data['Manager'].unique().tolist()
    tm = sorted(tm)
    tm.insert(0,'Overall')
    impact = data[data['Policy Adherence'] == "Deviated" ]['impact'].unique().tolist()
    impact.append('Overall')

    tm_selected = st.selectbox("Enter the Manager", tm)
    impact_selected = st.selectbox("Enter the Impact", impact)

    if tm_selected == 'Overall' and impact_selected == 'Overall':
        tabs = data[(data['Policy Adherence'] == 'Deviated')][
            ['Contact id', 'first_name', 'Manager',
            'impact', 'opportunity']]
        st.table(tabs)
    elif tm_selected != 'Overall' and impact_selected == 'Overall':
        tabs = data[(data['Policy Adherence'] == 'Deviated') & (data['Manager'] == tm_selected)][
            ['Contact id', 'first_name', 'Manager',
             'impact', 'opportunity']]
        st.table(tabs)
    elif tm_selected == 'Overall' and impact_selected != 'Overall':
        tabs = data[(data['Policy Adherence'] == 'Deviated') & (data['impact'] == impact_selected)][
            ['Contact id', 'first_name', 'Manager',
             'impact', 'opportunity']]
        st.table(tabs)
    else:
        tabs = data[(data['Policy Adherence'] == 'Deviated') & (data['impact'] == impact_selected)& (data['Manager'] == tm_selected)][
            ['Contact id', 'first_name', 'Manager',
             'impact', 'opportunity']]
        st.table(tabs)

else:
    st.title('QA Analysis')
    selected_qa = st.selectbox('Select the QA Name', sorted(qa))

    if week_num == "Overall":
        data = df
    else:
        data = df[df['Week'] == week_num]

    if selected_qa == "All":
        main = data['QA login'].value_counts().sort_index().reset_index()
        main['pass_count'] = data[data['Policy Adherence'] == 'Adhered']['QA login'].value_counts().sort_index().values
        main['fail_count'] = data[data['Policy Adherence'] == 'Deviated']['QA login'].value_counts().sort_index().values
        main.rename(columns={'index': 'QA', 'QA login':'Total Contacts Audited', 'pass_count':'Contacts Passed',
                             'fail_count': 'Contacts Failed'}, inplace=True)
        main = main.sort_values('Contacts Failed', ascending=False)
        st.table(main)

    else:
        col1,col2,col3 = st.columns(3)

        with col1:
            st.title('Total Contacts Audited')
            st.header(data[data['QA login']==selected_qa].shape[0])
        with col2:
            st.title('Total Contacts Passed')
            st.header(data[(data['QA login']==selected_qa) & (data['Policy Adherence']=='Adhered')].shape[0])
        with col3:
            st.title('Total Contacts Failed')
            st.header(data[(data['QA login']==selected_qa) & (data['Policy Adherence']=='Deviated')].shape[0])

        a = data[data['QA login'] == selected_qa]['opportunity'].value_counts() / data['opportunity'].value_counts()
        a = a.reset_index().dropna().reset_index().rename(
            columns={'index': 'use case', 'opportunity': 'Percent of total'})
        a['Percent of total'] = round(a['Percent of total'], 2)
        a = a.sort_values('Percent of total')
        a.drop('level_0', axis=1, inplace=True)
        st.header("Use Case fails")
        st.table(a)
