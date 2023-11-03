import streamlit as st

from matplotlib import pyplot as plt


import plotly.express as px
import pandas as pd
import os 
import warnings 
warnings.filterwarnings('ignore')


st.set_page_config(page_title = 'Superstore  ' , page_icon=":bar_chart" , layout="wide")
st.title(":bar_chart: Super Store EDA ")

st.markdown('<style>div.block-container{padding-top:1rem;}</style>' , unsafe_allow_html=True)

fl = st.file_uploader(":file_folder: Upload a File " , type = ["csv" , "txt", "xslx" , "xls"])
if fl is not None:
    filename = fl.name
    st.write(filename)

    df = pd.read_csv(filename ,encoding="ANSI")
else:
    os.chdir(r"c:\Users\xsinghsh\Downloads\react")
    df = pd.read_csv("Superstore.csv" , encoding="ANSI")

col1 , col2 = st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"])

startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()


with col1:
    date1 = pd.to_datetime(st.date_input("Start Date" , startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date" , endDate))


    df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()
    
    st.sidebar.header("Choose your Header")
    reigon = st.sidebar.multiselect("Pick Your Reigon" , df["Region"].unique())
     
    if not reigon:
        df2 = df.copy()
    else:
        df2 = df[df["Region"].isin(reigon)]
    
    state = st.sidebar.multiselect("Pick Your State" , df2["State"].unique())
    if not state:
        df3 = df2.copy()
    else:
        df3 = df2[df2["State"].isin(state)]

    city = st.sidebar.multiselect("Pick the City" , df3["City"].unique())
    
    if not reigon and not state and not city:
        filter_df = df
    elif not state and not city:
        filter_df = df[df["Region"].isin(reigon)]
    elif not reigon and not city:
        filter_df = df[df["State"].isin(state)]
    elif state and city:
        filter_df = df3[df["State"].isin(state) & df3["City"].isin(city)]
    elif reigon and city:
        filter_df = df3[df["Region"].isin(reigon) & df3["City"].isin(city)]
    elif reigon and state:
        filter_df = df3[df["Region"].isin(reigon) & df3["State"].isin(state)]
    elif city:
        filter_df = df3[df3["City"].isin(city)]
    else:
        filter_df = df3[df3["Region"].isin(reigon) and df3["State"].isin(state) and df3["City"].isin(city)]
    

    category = filter_df.groupby(by = ["Category"] , as_index = False)["Sales"].sum()

    with col1:
        st.subheader("Category wise Sales")
        fig = px.bar(category , x = "Category" , y = "Sales" , text = ['${:,.2f}'.format(x) for x in category["Sales"]] , 
                     template="seaborn")
        st.plotly_chart(fig , use_container_width=True , height = 200)
    with col2:
        st.subheader("Reigon wise Sales")
        fig = px.pie(filter_df , values = "Sales" , names = "Region" , hole=0.5)
        fig.update_traces(text = filter_df["Region"] , textposition = "outside")
        st.plotly_chart(fig , use_container_width=True)
    
cl1 , cl2 = st.columns(2)

with cl1:
    with st.expander("Category_ViewDataa"):
         st.write(category.style.background_gradient(cmap = "Blues"))
         csv = category.to_csv(index = False).encode('utf-8')
         st.download_button("Download Data" , data = csv , file_name = "Category.csv" , mime = "text/csv",
                           help = 'Click here to Download the data as a CSV file ')
    
    with cl2:
        with st.expander("Category_ViewDataa"):
         reigon = filter_df.groupby(by = "Region" , as_index = False)["Sales"].sum()
         st.write(reigon.style.background_gradient(cmap = "Oranges"))
         csv = reigon.to_csv(index = False).encode('utf-8')
         st.download_button("Download Data" , data = csv , file_name = "Reigon.csv" , mime = "text/csv",
                           help = 'Click here to Download the data as a CSV file ')

    


filter_df["month_year"] = filter_df["Order Date"].dt.to_period("M")
st.subheader('Time Series Analysis')
linechart = pd.DataFrame(filter_df.groupby(filter_df["month_year"].dt.strftime("%Y :%b"))["Sales"].sum()).reset_index()
fig2 =  px.line(linechart , x = "month_year" , y = "Sales" , labels = {"Sales":"Amount"} , height=500 , width = 1000 , template = "gridon")
st.plotly_chart(fig2 , use_container_width=True)

with st.expander("View Data of Time Series:"):
    st.write(linechart.T.style.background_gradient(cmap = "Blues"))
    csv = linechart.to_csv(index = False).encode("utf-8")
    st.download_button('Download' , data = csv , file_name = "TimeSeries.csv" , mime = "text/csv")


st.subheader("Hierarchial view of sales using tree map")
fig3 = px.treemap(filter_df , path = ["Region" , "Category" , "Sub-Category"] , values = "Sales" , hover_data=["Sales"],
                  color = "Sub-Category")

fig3.update_layout(width = 800 , height = 650)
st.plotly_chart(fig3 , use_container_width=True)


chart1 , chart2 = st.columns(2)

with chart1:
    st.subheader('Segment wise Sales')
    fig = px.pie(filter_df , values = "Sales" , names="Segment" , template="plotly_dark")
    fig.update_traces(text = filter_df["Segment"] , textposition = "inside")
    st.plotly_chart(fig , use_container_width=True)

with chart2:
    st.subheader('Category wise Sales')
    fig = px.pie(filter_df , values = "Sales" , names="Segment" , template="gridon")
    fig.update_traces(text = filter_df["Category"] , textposition = "inside")
    st.plotly_chart(fig , use_container_width=True)


import plotly.figure_factory as ff


st.subheader(" Month wise Sub-Category Sales Summary")
with st.expander("Summary_Table"):
    df_sample =  df[0:5][["Region" , "State" , "City" , "Category" , "Sales" , "Profit" , "Quantity"]]
    fig = ff.create_table (df_sample , colorscale="Cividis")
    st.plotly_chart(fig , use_container_width=True)

    st.markdown("Month wise Sub-Category Table")
    filter_df["month"] = filter_df["Order Date"].dt.month_name()
    sub_category_year = pd.pivot_table(data = filter_df , values = "Sales" , index = ["Sub-Category"] , columns = "month")
     
    st.write(sub_category_year.style.background_gradient(cmap = "Blues"))


data1 = px.scatter(filter_df , x = "Sales" , y = "Profit" , size = "Quantity")
data1['layout'].update(title = "Relationship netween Sales and profits using scatter plot ",
                       titlefont = dict(size = 20) , xaxis = dict(title = "Sales" , titlefont = dict(size = 19)),
                       yaxis = dict(title = "Profit" , titlefont = dict(size = 19)))


st.plotly_chart(data1 , use_container_width=True)


with st.expander("View Data"):
  st.write(filter_df.iloc[:500,1:20:2].style.background_gradient(cmap = "Oranges"))