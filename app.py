
import streamlit as st
import data_library as dl

st.set_page_config(page_title='UAE Deposit Products Dashboard', layout='wide')
st.title('🇦🇪 Deposit Products Dashboard')

st.sidebar.header('Controls')
if st.sidebar.button('🔄 Refresh live data'):
    data = dl.refresh_data()
    st.sidebar.success('Data refreshed!')
else:
    data = dl.load_data()

providers = st.sidebar.multiselect('Filter providers', sorted(data['provider'].unique()))
if providers:
    data = data[data['provider'].isin(providers)]

st.subheader('Product Catalogue')
st.dataframe(data, use_container_width=True)

sel = st.selectbox('Select a product for detail view', options=data['product_name'].unique())
st.subheader(f'Details – {sel}')
st.write(data[data['product_name'] == sel].T)
