import streamlit as st

st.set_page_config(
    page_title="Product Experimentation Platform",
    layout="wide"
)

st.title("Product Experimentation Platform")

st.write(
    "Google-style product analytics and experimentation dashboard."
)

col1, col2, col3 = st.columns(3)

col1.metric(
    label="Daily Active Users",
    value="24,521",
    delta="+12.4%"
)

col2.metric(
    label="Conversion Rate",
    value="8.7%",
    delta="+1.3%"
)

col3.metric(
    label="Retention Rate",
    value="41.2%",
    delta="-0.8%"
)