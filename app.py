import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

st.set_page_config(layout='wide',page_title='Startup Analysis')

df= pd.read_csv('startup_funding_cleaned.csv')

df['Date']= pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')


def load_company_details(company):
    
    # Name of the company
    st.title(company)

    # Industry of the company
    industry_list= df[df['Company']==company]['Industry'].unique()[:5].tolist()

    col1, spacer, col2= st.columns([5,1,5])

    with col1:
        st.subheader(f"{company}'s Associated Industries")
        for industry in industry_list:
            st.markdown(f"- {industry}")

    # Sub-industry of the company
    subindustry_list= df[(df['Company']==company) & (df['Subvertical']!= 'Not unknown')]['Subvertical'].unique()[:5].tolist()

    with col2:
        st.subheader(f"{company}'s Associated Sub-Industries")
        for subindustry in subindustry_list:
            st.markdown(f"- {subindustry}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Location of the company
    company_city= df[df['Company']==company]['City'].unique().tolist()

    col1, spacer, col2= st.columns([5,1,5])

    with col1:
        st.subheader(f"{company}'s Location")
        for city in company_city:
            st.markdown(f"- {city}")

    # Investors of the company
    investor_list= df[df['Company']==company]['Investors'].unique()[:5]

    with col2:
        st.subheader(f"Investors of {company}")
        for investor in investor_list:
            st.markdown(f'- {investor}')

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Latest funding of the company
    latest_funding=df[df['Company']==company][['Date','Amount','Investors']].head()

    latest_funding.rename(columns={'Amount':'Amount (in Rs Cr)'},inplace=True)

    styled_html = latest_funding.style.set_table_styles(
    [{'selector': 'th', 'props': [('text-align', 'center')]},
     {'selector': 'td', 'props': [('text-align', 'center')]}]
    ).hide(axis='index').to_html()

    st.subheader(f"Latest funding details of {company}")
    st.markdown(styled_html, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Similar Companies
    temp_row= df[df['Company']==company]

    target_industry= str(temp_row.iloc[0]['Industry']).strip().lower()
    target_city= str(temp_row.iloc[0]['City']).strip().lower()

    temp=df
    temp['Industry']= temp['Industry'].astype(str)
    temp['City']= temp['City'].astype(str)

    similar = temp[
        (temp['Company'] != company) &
        (temp['Industry'].str.lower().str.contains(target_industry, na=False)) &
        (temp['City'].str.lower().str.contains(target_city, na=False))
    ]

    similar_company_list= similar['Company'].unique()[:5]

    st.subheader(f'Similar companies of {company} (This is just representation)')
    if len(similar_company_list)==0:
        st.markdown("None as per our database")

    for companies in similar_company_list:
            st.markdown(f'- {companies}')



def load_investor_details(investor):

    # Name of the investor
    st.title(investor)

    col1, col_spacer, col2=st.columns([2.5, 0.1, 1.5])


    # 5 recent investments made
    temp=df[df['Investors'].str.contains(investor, case=False, na=False)].sort_values(by='Date',ascending=False).head()

    temp= temp[['Date','Company','Industry','City','Amount']]
    temp.rename(columns={'Amount':'Amount (in Rs Cr)'},inplace=True)
    
    with col1:
        st.subheader(f"5 recent investments made by {investor}")
        st.dataframe(temp,use_container_width=False)


    # 3 biggest investments
    comapny_grp= df[df['Investors']==investor].groupby('Company')
    biggest_investment= comapny_grp['Amount'].sum().sort_values(ascending=False).head(3).to_frame().reset_index()

    biggest_investment.rename(columns={'Amount':'Amount (in Rs Cr)'}, inplace=True)

    with col2:
        st.subheader(f"Top 3 biggest investments of {investor}")
        st.dataframe(biggest_investment, use_container_width=False)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Investment sector
    industry_grp= df[df['Investors']==investor].groupby('Industry')
    investment_plot= industry_grp['Amount'].sum().sort_values(ascending=False).head(5)

    col1, col2= st.columns([1,1])

    with col1:
        fig1, ax1= plt.subplots(figsize=(7,7))
        ax1.pie(investment_plot, autopct='%0.1f%%', labels=investment_plot.index)
        ax1.set_title(f"Top 5 sector investment for {investor}")
        
        st.pyplot(fig1)

    # Investment city
    city_grp= df[df['Investors']==investor].groupby('City')
    city_plot= city_grp['Amount'].sum().sort_values(ascending=False).head(5)

    with col2:
        fig3, ax3= plt.subplots(figsize=(5,5))
        ax3.pie(city_plot, autopct='%0.1f%%', labels=city_plot.index)
        ax3.set_title(f"Top 5 cities for investment for {investor}")
        
        st.pyplot(fig3)



def load_overall_analysis():

    st.title("Indian Startup Funding Analysis")

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2= st.columns(2)

    # Total Amount Invested
    total_amt= df['Amount'].sum()

    with col1:
        st.metric(value=total_amt, label='Total funding in Indian Startups (in Rs Cr)')


    # Maximum Amount Invested
    max_amt= df['Amount'].max()

    with col2:
        st.metric(value=max_amt, label="Maximum funding in Indian startup (in Rs Cr)")

    col1, col2= st.columns(2)

    # Average Amount Invested
    avg_amt=np.round(df['Amount'].mean(),2)

    with col1:
        st.metric(value=avg_amt, label="Average funding in Indian Startups (in Rs Cr)")


    # Total funded companies
    total_company= df['Company'].nunique()

    with col2:
        st.metric(value=total_company, label="Total Indian Startup Companies")

    st.markdown("<br>", unsafe_allow_html=True)

    # Quarter on Quarter chart

    st.markdown("<h2 style='text-align: center'>Quarter on Quarter Analysis</h2>", unsafe_allow_html=True)
    col1, spacer, col2= st.columns([5,0.5,5])

    with col1:
        # No. of startups quarter by quarter
        quarter_grp= df.groupby(['Year','Quarter'])
        temp= quarter_grp['Company'].count().reset_index()
        temp['X_axis']= temp['Quarter'].astype('str') + '-' + temp['Year'].astype('str')

        temp= temp[['Company', 'X_axis']]

        fig1, ax1 = plt.subplots(figsize=(5, 4))
        ax1.plot(temp['X_axis'], temp['Company'], marker='o')
        ax1.set_title("No. of startups funded per Quarter")
        ax1.set_xlabel("Quarter-Year")
        ax1.set_ylabel("Number of Startups")
        ax1.tick_params(axis='x', rotation=45)
        plt.tight_layout()

        st.pyplot(fig1)

    with col2:
        # Funding in startups in each quarter
        temp1= quarter_grp['Amount'].sum().reset_index()
        temp1['X_axis']= temp1['Quarter'].astype('str') + '-' + temp1['Year'].astype('str')

        temp1= temp1[['Amount', 'X_axis']]

        fig2, ax2 = plt.subplots(figsize=(5, 4))
        ax2.plot(temp1['X_axis'], temp1['Amount'], marker='o')
        ax2.set_title("Funding in startups quarter by quarter")
        ax2.set_xlabel("Quarter-Year")
        ax2.set_ylabel("Funding of Startups")
        ax2.tick_params(axis='x', rotation=45)
        plt.tight_layout(pad=0.5)

        st.pyplot(fig2)

    st.markdown("<br>", unsafe_allow_html=True)


    # Sector Analysis
    
    st.markdown("<h2 style='text-align: center'>Sector Analysis</h2>", unsafe_allow_html=True)
    col1, spacer, col2= st.columns([5,0.5,5])

    with col1:
    # Top 5 sectors by no. of startups
        sector_plot1= df['Industry'].value_counts().head()

        fig3, ax3= plt.subplots(figsize=(5,5.5))
        sns.barplot(x=sector_plot1.index, y=sector_plot1.values, ax=ax3)
        ax3.set_title("Top 5 industry sectors for investment (by no. of startups)")
        ax3.set_xlabel("Industry Sector")
        ax3.set_ylabel("No. of Startups")
        ax3.tick_params(axis='x', rotation=45)
        

        st.pyplot(fig3)

    with col2:
        # Top 5 sectors by funding of startups
        sector_plot2= df.groupby(['Industry'])['Amount'].sum().sort_values(ascending=False).head()

        fig4, ax4= plt.subplots(figsize=(5,5))
        sns.barplot(x=sector_plot2.index, y=sector_plot2.values, ax=ax4)
        ax4.set_title("Top 5 industry sectors for investment (by funding of startups)")
        ax4.set_xlabel("Industry Sector")
        ax4.set_ylabel("Funding of Startups (in Rs Cr)")
        ax4.tick_params(axis='x', rotation=45)

        st.pyplot(fig4)

    st.markdown("<br>", unsafe_allow_html=True)


    # City for investment:

    st.markdown("<h2 style='text-align: center'>City Analysis</h2>", unsafe_allow_html=True)
    col1, spacer, col2= st.columns([5,0.5,5])

    with col1:
        # Top 5 cities by no. of companies
        city_plot1= df['City'].value_counts().head()

        fig1, ax1= plt.subplots(figsize=(5,5))
        ax1.pie(city_plot1, autopct='%0.1f%%', labels=city_plot1.index)
        ax1.set_title("Top 5 cities for investment (by no. of companies)")

        st.pyplot(fig1)

    with col2:
        # Top 5 cities by no. of companies
        city_plot2= df.groupby(['City'])['Amount'].sum().sort_values(ascending=False).head()

        fig2, ax2= plt.subplots(figsize=(5,5.8))
        ax2.pie(city_plot2, autopct='%0.1f%%', labels=city_plot2.index)
        ax2.set_title("Top 5 cities for investment (by funding of companies)")

        st.pyplot(fig2)




# Main Program


st.sidebar.title('Startup Funding Analysis')

option=st.sidebar.selectbox('Select One',['Overall Analysis','Startup Analysis','Investor Analysis'])

if option=='Overall Analysis':
    
    button0= st.sidebar.button("Click for overall analysis")

    if button0:
        load_overall_analysis()

elif option=='Startup Analysis':

    # Select the company
    company= st.sidebar.selectbox('Select Startup',sorted(df['Company'].unique()))

    button1= st.sidebar.button("Find compnay's details")

    if button1:
        load_company_details(company)

elif option=='Investor Analysis':
    
    # Select the investor
    investor= st.sidebar.selectbox('Select Investor',sorted(df['Investors'].unique()))

    button2= st.sidebar.button("Find Investor's details")

    if button2:
        load_investor_details(investor)
