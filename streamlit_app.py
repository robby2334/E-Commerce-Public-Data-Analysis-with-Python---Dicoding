import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

#membuat helper funtions
def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        'order_id':'nunique',
        'price': 'sum'
    })

    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        'order_id':'order_count',
        'price':'revenue'
    },inplace=True)

    return daily_orders_df

def create_sum_order_df(df):
    sum_order_items_df=df.groupby('product_category_name').order_item_id.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df


def create_review_score_df(df):
    review_score_df=df.groupby(by=['review_score','product_category_name']).agg({
        'order_id':'nunique',
        'review_score':'sum',
    },inplace=True).sort_values(by='order_id',ascending=False)
    review_score_df.head()
    return review_score_df

def create_bystate_df(df):
    bystate_df=df.groupby(by='customer_state').customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        'customer_id':'customer_count'
    },inplace=True)


    return bystate_df


def create_bycity_df(df):
    bycity_df=df.groupby(by='customer_city').customer_id.nunique().reset_index()
    bycity_df.rename(columns={
        'customer_id':'customer_count'
    },inplace=True)


    return bycity_df


def create_rfm_df(df):
    rfm_df=df.groupby(by='customer_state', as_index=False).agg({
        'order_purchase_timestamp':'max',
        'order_id':'nunique',
        'price':'sum'
    })

    rfm_df.columns=['customer_state','max_order_timestamp','frequency','monetary']

    # menghitung kapan terakhir pelanggan melakukan transaksi (hari)
    rfm_df['max_order_timestamp'] = rfm_df['max_order_timestamp'].dt.date
    recent_date = df['order_purchase_timestamp'].dt.date.max()
    rfm_df['recency'] = rfm_df['max_order_timestamp'].apply(lambda x:(recent_date-x).days)


    rfm_df.drop('max_order_timestamp', axis=1, inplace=True)
    rfm_df.head()

    return rfm_df

#menyiapkan data set
all_df = pd.read_csv("all_data.csv")

datetime_columns=['order_purchase_timestamp','order_estimated_delivery_date']
all_df.sort_values(by='order_purchase_timestamp', inplace=True)
all_df.reset_index(inplace=True)


for columns in datetime_columns:
    all_df[columns] = pd.to_datetime(all_df[columns])



#membuat komponen filter
min_date = all_df['order_purchase_timestamp'].min()
max_date = all_df['order_purchase_timestamp'].max()

with st.sidebar:
    #menambahkan logo perusahaan
    st.image("https://images.datacamp.com/image/upload/v1640050215/image27_frqkzv.png")

    #Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# membuat variable untuk menampung data yang telah difilter
main_df=all_df[(all_df['order_purchase_timestamp']>= str(start_date))&(all_df['order_purchase_timestamp']<= str(end_date))]

# memanggil helper funtions 


daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_df(main_df)
review_score_df = create_review_score_df(main_df)
bystate_df = create_bystate_df(main_df)
rfm_df = create_rfm_df(main_df)

bycity_df = create_bycity_df(main_df)

st.header('E-Commerce Public :sparkles:')


st.subheader('Daily Orders')

col1, col2 =st.columns(2)


with col1:
    total_orders = daily_orders_df.order_count.sum()

    st.metric('Total orders', value=total_orders)

with col2:
    total_revenue=format_currency(daily_orders_df.revenue.sum(), 'BRL', locale='es_BR')
    st.metric('Total revenue', value=total_revenue)

fig, ax = plt.subplots(figsize=(16,8))

ax.plot(
    daily_orders_df['order_purchase_timestamp'],
    daily_orders_df['order_count'],
    marker='.',
    linewidth=2,
    color="#90CAF9"

)

ax.tick_params(axis='y', labelsize=25)
ax.tick_params(axis='x', labelsize=20, rotation=45)


st.pyplot(fig)

# 5 produk paling laris dan paling sedikit

st.subheader("Best & Worst Performing Product")
 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
 
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
 
sns.barplot(x="order_item_id", y="product_category_name", data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].set_title("Best Performing Product", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)
 
sns.barplot(x="order_item_id", y="product_category_name", data=sum_order_items_df.sort_values(by="order_item_id", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
 
st.pyplot(fig)




# Demografi pelanggan berdasarkan states dan city menggunakan Tabs
st.title('Customer Demographics')

tab1,tab2=st.tabs(['by state','by City'])

with tab1:
    fig, ax =plt.subplots(figsize=(35, 15))
    colors_ = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
    sns.barplot(
        x="customer_count", 
        y="customer_state",      
        data=bystate_df.sort_values(by="customer_count", ascending=False).head(10),
        palette=colors_,
        ax=ax
)
    ax.set_title("Number of Customer by States", loc="center", fontsize=30)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='y', labelsize=25)
    ax.tick_params(axis='x', labelsize=25)
    st.pyplot(fig)


with tab2:
    fig, ax =plt.subplots(figsize=(35, 15))
    colors_ = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
    sns.barplot(
        x="customer_count", 
        y="customer_city",
        data=bycity_df.sort_values(by="customer_count", ascending=False).head(10),
        palette=colors_,
        ax=ax
)
    ax.set_title("Number of Customer by City", loc="center", fontsize=30)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='y', labelsize=25)
    ax.tick_params(axis='x', labelsize=25)
    st.pyplot(fig)
   


st.subheader('Best Customer Regions Based on RFM Parameters')


col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "BRL", locale='es_BR') 
    st.metric("Average Monetary", value=avg_frequency)
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]
 
sns.barplot(y="recency", x="customer_state", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_state", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)
 
sns.barplot(y="frequency", x="customer_state", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_state", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)
 
sns.barplot(y="monetary", x="customer_state", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_state", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)
 
st.pyplot(fig)
 
st.caption('Robbie Christhover (c) Dicoding 2024')
