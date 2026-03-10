import streamlit as st
import plotly.express as px
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# -------------------- CACHE DATA LOADING --------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("gadDATABASE.xlsx", sheet_name="overall")
        return df
    except FileNotFoundError:
        st.error("File 'gadDATABASE.xlsx' not found. Please ensure it's in the app directory.")
        return None
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def display():
    st.set_page_config(page_title="LGU Departments Dashboard", layout="wide")
    st.title(":bar_chart: LGU Departments")

    # Load data
    df = load_data()
    if df is None:
        st.stop()

    # -------------------- FILTERS (placed in main area) --------------------
    st.subheader("Filter Options")

    # Check if YEAR column exists; if not, assume single year and create dummy
    if 'YEAR' not in df.columns:
        df['YEAR'] = 2024
        available_years = [2024]
    else:
        available_years = sorted(df['YEAR'].unique())

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        selected_years = st.multiselect(
            "Select Year(s)",
            available_years,
            default=available_years[:2] if len(available_years) >= 2 else available_years
        )

    if not selected_years:
        st.warning("Please select at least one year.")
        st.stop()

    # Filter data by selected years
    df_filtered = df[df['YEAR'].isin(selected_years)].copy()

    # Optional: select specific indicators/offices if column exists
    if 'INDICATOR' in df_filtered.columns:
        with col_f2:
            offices = st.multiselect(
                "Select Offices",
                df_filtered['INDICATOR'].unique(),
                default=df_filtered['INDICATOR'].unique()
            )
        if offices:
            df_filtered = df_filtered[df_filtered['INDICATOR'].isin(offices)]

    st.divider()

    # -------------------- KPI CARDS --------------------
    total_male = df_filtered['MALE'].sum()
    total_female = df_filtered['FEMALE'].sum()
    total_employees = df_filtered['TOTAL'].sum() if 'TOTAL' in df_filtered.columns else total_male + total_female

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Male", f"{total_male:,}")
    col2.metric("Total Female", f"{total_female:,}")
    col3.metric("Total Employees", f"{total_employees:,}")

    st.divider()

    # -------------------- DATA VIEW WITH STYLING --------------------
    with st.expander("View Filtered Data", expanded=False):
        # Style the dataframe with a gradient
        styled_df = df_filtered.style.background_gradient(cmap='cool', subset=['MALE', 'FEMALE'])\
                                     .format({'MALE': '{:,.0f}', 'FEMALE': '{:,.0f}'})
        st.dataframe(styled_df, use_container_width=True)

    # -------------------- MAIN CHARTS --------------------
    # Prepare long format for plotting
    id_vars = ['INDICATOR']
    if 'YEAR' in df_filtered.columns:
        id_vars.append('YEAR')
    df_long = df_filtered.melt(
        id_vars=id_vars,
        value_vars=['MALE', 'FEMALE'],
        var_name='Gender',
        value_name='Count'
    )
    df_long['Gender'] = df_long['Gender'].replace({'MALE': 'Male', 'FEMALE': 'Female'})

    custom_colors = {'Male': '#347dc1', 'Female': '#e6a6c7'}

    # Row 1: Bar chart + Total pie
    col_left, col_right = st.columns(2)

    with col_left:
        # Grouped bar chart
        if 'YEAR' in df_long.columns and len(selected_years) > 1:
            # Multiple years: group by year and gender
            fig_bar = px.bar(
                df_long,
                x='INDICATOR',
                y='Count',
                color='Gender',
                barmode='group',
                facet_col='YEAR',
                title="Male vs Female by Office and Year",
                text='Count',
                color_discrete_map=custom_colors
            )
            fig_bar.update_traces(texttemplate='%{text}', textposition='inside')
        else:
            # Single year
            fig_bar = px.bar(
                df_long,
                x='INDICATOR',
                y='Count',
                color='Gender',
                barmode='group',
                title=f"Male vs Female by Office ({', '.join(map(str, selected_years))})",
                text='Count',
                color_discrete_map=custom_colors
            )
            fig_bar.update_traces(texttemplate='%{text}', textposition='inside')
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        # Total percentage pie (all selected data)
        total_gender = df_filtered[['MALE', 'FEMALE']].sum().reset_index()
        total_gender.columns = ['Gender', 'Total']
        total_gender['Gender'] = total_gender['Gender'].replace({'MALE': 'Male', 'FEMALE': 'Female'})

        fig_pie_total = px.pie(
            total_gender,
            values='Total',
            names='Gender',
            title=f"Overall Male vs Female ({', '.join(map(str, selected_years))})",
            hole=0.3,
            color='Gender',
            color_discrete_map=custom_colors
        )
        st.plotly_chart(fig_pie_total, use_container_width=True)

    # Row 2: Office pie chart + Trend line (if multiple years)
    col_left2, col_right2 = st.columns(2)

    with col_left2:
        # Percentage per office (using all selected data)
        # Aggregate by office
        office_totals = df_filtered.groupby('INDICATOR')[['MALE', 'FEMALE']].sum().reset_index()
        office_totals['Total'] = office_totals['MALE'] + office_totals['FEMALE']

        # Create a color map for offices
        unique_offices = office_totals['INDICATOR'].unique()
        office_colors = px.colors.qualitative.Set3
        color_map = {office: office_colors[i % len(office_colors)] for i, office in enumerate(unique_offices)}

        fig_pie_office = px.pie(
            office_totals,
            values='Total',
            names='INDICATOR',
            title=f"Employee Distribution by Office ({', '.join(map(str, selected_years))})",
            hole=0.3,
            color='INDICATOR',
            color_discrete_map=color_map
        )
        st.plotly_chart(fig_pie_office, use_container_width=True)

    with col_right2:
        # If multiple years, show a line chart for trends
        if 'YEAR' in df_filtered.columns and len(selected_years) > 1:
            yearly_totals = df_filtered.groupby('YEAR')[['MALE', 'FEMALE', 'TOTAL']].sum().reset_index()\
                                        .melt(id_vars='YEAR', value_vars=['MALE', 'FEMALE'],
                                              var_name='Gender', value_name='Count')
            yearly_totals['Gender'] = yearly_totals['Gender'].replace({'MALE': 'Male', 'FEMALE': 'Female'})

            fig_line = px.line(
                yearly_totals,
                x='YEAR',
                y='Count',
                color='Gender',
                markers=True,
                title="Gender Trends Over Years",
                color_discrete_map=custom_colors
            )
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            # Placeholder or show total by office horizontal bar
            office_sum = df_filtered.groupby('INDICATOR')[['MALE', 'FEMALE']].sum().reset_index()
            office_sum['Total'] = office_sum['MALE'] + office_sum['FEMALE']
            office_sum = office_sum.sort_values('Total', ascending=True)

            fig_hbar = px.bar(
                office_sum,
                y='INDICATOR',
                x='Total',
                orientation='h',
                title="Total Employees by Office",
                text='Total'
            )
            fig_hbar.update_traces(textposition='outside')
            st.plotly_chart(fig_hbar, use_container_width=True)

    # -------------------- YEAR-OVER-YEAR TABLE (if multiple years) --------------------
    if 'YEAR' in df_filtered.columns and len(selected_years) > 1:
        st.divider()
        st.subheader("📊 Year-over-Year Summary")
        yearly_summary = df_filtered.groupby('YEAR')[['MALE', 'FEMALE', 'TOTAL']].sum().reset_index()
        yearly_summary['Change'] = yearly_summary['TOTAL'].diff().fillna(0).astype(int)
        yearly_summary['Change %'] = yearly_summary['TOTAL'].pct_change().fillna(0).map('{:.1%}'.format)
        st.dataframe(yearly_summary, use_container_width=True)

# Entry point (if running directly)
if __name__ == "__main__":
    display()