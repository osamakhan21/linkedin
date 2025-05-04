import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

# Page config
st.set_page_config(page_title='LinkedIn Job Dashboard', layout='wide')

# Load dataset
df = pd.read_csv('data/linkdin_Job_data_cleaned.csv')

# Apply dark theme styling
st.markdown("""
    <style>
    body { background-color: #0f0f1a; color: #ffffff; }
    .stApp { background-color: #0f0f1a; color: white; }
    .css-1d391kg, .css-1cpxqw2 { background-color: #1e1e2f; }
    .stButton>button { background-color: #5f4bb6; color: white; }
    .sidebar .sidebar-content { background-color: #1e1e2f; color: white; 
    }
    /* Sidebar full dark styling */
    .css-6qob1r, .css-1d391kg, .css-1cpxqw2, .st-eb {
        background-color: #1e1e2f !important;
        color: white !important;
    }

    /* Multiselect pill styling */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #5f4bb6 !important;
        color: white !important;
        border-radius: 8px !important;
        max-width: 120px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    /* Filter label spacing */
    .stSidebar .st-expander > summary {
        margin-bottom: 8px;
    }

    /* Filter section spacing */
    .stSidebar .st-expander {
        margin-bottom: 15px;
    }

    /* Reduce padding in sidebar widgets */
    .css-1v3fvcr {
        padding: 0.25rem 0.5rem;
    }
    .stMultiSelect [data-baseweb="tag"] {
    padding-top: 2px;
    padding-bottom: 2px;
    font-size: 0.8rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }
    .stMultiSelect [data-baseweb="tag"] {
    position: relative;
}
.stMultiSelect [data-baseweb="tag"]::after {
    content: attr(title);
    position: absolute;
    left: 0;
    bottom: 100%;
    background: #222;
    color: white;
    padding: 3px 6px;
    font-size: 10px;
    white-space: nowrap;
    opacity: 0;
    transition: opacity 0.3s ease-in-out;
    pointer-events: none;
}
.stMultiSelect [data-baseweb="tag"]:hover::after {
    opacity: 1;
}


    </style>
    """, unsafe_allow_html=True)

# Sidebar with logo and filters
st.sidebar.image("linkedin-logo-linkedin-icon-transparent-free-png.webp", use_container_width=True)
st.sidebar.title(" Dashboard Filters")
with st.sidebar.expander(" Text Filters", expanded=True):
    job_filter = st.text_input("Job Title Search")
    location_filter = st.text_input("Location Search")

    if job_filter:
        df = df[df['job'].str.contains(job_filter, case=False, na=False)]
    if location_filter:
        df = df[df['location'].str.contains(location_filter, case=False, na=False)]

with st.sidebar.expander(" Categorical Filters", expanded=True):
    work_type_options = sorted(df['work_type'].dropna().unique())
    selected_work_types = st.multiselect(
        "Work Type",
        options=work_type_options,
        default=work_type_options,
        key="work_type_filter"
    )

    industry_options = sorted(df['industry'].dropna().unique())
    selected_industries = st.multiselect(
        " Industry",
        options=industry_options,
        default=industry_options,
        key="industry_filter"
    )

    # Apply categorical filters
    df = df[df['work_type'].isin(selected_work_types)]
    df = df[df['industry'].isin(selected_industries)]

with st.sidebar.expander(" Company Filter (Dynamic)", expanded=True):
    df_filtered_for_company = df[df['industry'].isin(selected_industries)]
    company_options = sorted(df_filtered_for_company['company_name'].dropna().unique())

    selected_companies = st.multiselect(
        "Company (filtered by industry)", 
        options=company_options,
        default=company_options,
        key="company_filter"
    )

    df = df[df['company_name'].isin(selected_companies)]

with st.sidebar.expander(" Job Age Filter", expanded=True):
    if 'posted_hours_ago' in df.columns and not df['posted_hours_ago'].isnull().all():
        df['posted_hours_ago'] = pd.to_numeric(df['posted_hours_ago'], errors='coerce')
        max_hours = int(df['posted_hours_ago'].max())
        posted_within = st.slider(
            "Posted within last (hours)", 
            1, 
            max_hours, 
            max_hours,
            key="posted_within_slider"
        )
        df = df[df['posted_hours_ago'] <= posted_within]

# Top header
st.title(" LinkedIn Job Analytics Dashboard")

# Top KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Jobs", len(df))
col2.metric("Remote Jobs", df[df['work_type'].str.contains("Remote", na=False)].shape[0])
col3.metric("Industries", df['industry'].nunique())
col4.metric("Companies", df['company_name'].nunique())

# Visualizations row
st.markdown("---")
st.subheader(" Key Visualizations")

chart_col1, chart_col2, chart_col3, chart_col4 = st.columns(4)
with chart_col1:
    top_companies = df['company_name'].value_counts().head(5).reset_index()
    top_companies.columns = ['Company', 'Job Count']
    fig1 = px.bar(top_companies, x='Company', y='Job Count', color='Job Count',
                  color_continuous_scale='plasma', template='plotly_dark')
    fig1.update_layout(
        paper_bgcolor='#0f0f1a',
        plot_bgcolor='#0f0f1a',
        autosize=True
    )
    st.plotly_chart(fig1, use_container_width=True)

with chart_col2:
    work_type_counts = df['work_type'].value_counts().reset_index()
    work_type_counts.columns = ['Work Type', 'Count']
    fig2 = px.pie(work_type_counts, names='Work Type', values='Count', template='plotly_dark')
    fig2.update_layout(
        paper_bgcolor='#0f0f1a',
        autosize=True
    )
    st.plotly_chart(fig2, use_container_width=True)

with chart_col3:
    if 'posted_hours_ago' in df.columns:
        df['posted_hours_ago'] = pd.to_numeric(df['posted_hours_ago'], errors='coerce')
        hourly_jobs = df.groupby('posted_hours_ago').size().reset_index(name='Job Count')
        fig3 = px.area(hourly_jobs.sort_values('posted_hours_ago'), x='posted_hours_ago', y='Job Count',
                       title='Jobs Posted Over Time', template='plotly_dark', line_shape='spline')
        fig3.update_layout(
            paper_bgcolor='#0f0f1a',
            plot_bgcolor='#0f0f1a',
            autosize=True
        )
        st.plotly_chart(fig3, use_container_width=True)

with chart_col4:
    loc_counts = df['location'].value_counts().head(5).reset_index()
    loc_counts.columns = ['Location', 'Jobs']
    fig4 = px.bar(loc_counts, x='Location', y='Jobs', color='Jobs',
                  color_continuous_scale='viridis', template='plotly_dark')
    fig4.update_layout(
        paper_bgcolor='#0f0f1a',
        plot_bgcolor='#0f0f1a',
        autosize=True
    )
    st.plotly_chart(fig4, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("🔗 **Built with Streamlit** | Styled to match your design | © 2025 LinkedIn Job Insights")
