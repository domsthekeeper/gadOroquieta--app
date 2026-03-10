import streamlit as st
import plotly.express as px
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# -------------------- CACHE DATA LOADING --------------------
@st.cache_data
def load_data(sheet_name="sangguniang_panglungsod"):
    try:
        df = pd.read_excel("gadDATABASE.xlsx", sheet_name=sheet_name)
        return df
    except FileNotFoundError:
        st.error("File 'gadDATABASE.xlsx' not found. Please ensure it's in the app directory.")
        return None
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def display():
    st.set_page_config(page_title="Sangguniang Panglungsod Dashboard", layout="wide")
    st.title(":bar_chart: Sangguniang Panglungsod ")

    # Load data
    df = load_data("sangguniang_panglungsod")
    if df is None:
        st.stop()

    # Get all unique indicators
    indicators = sorted(df['INDICATOR'].unique())

    # Define custom gender colors (used throughout)
    custom_colors = {'Male': '#347dc1', 'Female': '#e6a6c7'}

    # -------------------- CREATE A SEPARATE EXPANDER FOR EACH INDICATOR --------------------
    for indicator in indicators:
        df_ind = df[df['INDICATOR'] == indicator].copy()
        if df_ind.empty:
            continue

        with st.expander(f"View {indicator} Data", expanded=False):
            st.subheader(f"{indicator} Employees")

            # Year filter (specific to this indicator)
            ind_years = sorted(df_ind["YEAR"].unique())
            ind_selected_years = st.multiselect(
                f"Select Year(s) for {indicator}",
                ind_years,
                default=ind_years[:2] if len(ind_years) >= 2 else ind_years,
                key=f"{indicator}_years"
            )
            if not ind_selected_years:
                st.warning(f"Please select at least one year for {indicator}.")
                continue  # skip this indicator if no years selected
            df_ind_filtered = df_ind[df_ind["YEAR"].isin(ind_selected_years)]

            # KPIs for latest year
            if not df_ind_filtered.empty:
                ind_yearly = df_ind_filtered.groupby("YEAR")[["MALE", "FEMALE", "TOTAL"]].sum().reset_index()
                ind_yearly = ind_yearly.sort_values("YEAR")
                ind_latest = ind_yearly.iloc[-1]

                ind_male = ind_latest["MALE"]
                ind_female = ind_latest["FEMALE"]
                ind_total = ind_latest["TOTAL"]
                ind_delta_male = ind_male - ind_yearly.iloc[-2]["MALE"] if len(ind_yearly) > 1 else 0
                ind_delta_female = ind_female - ind_yearly.iloc[-2]["FEMALE"] if len(ind_yearly) > 1 else 0
                ind_delta_total = ind_total - ind_yearly.iloc[-2]["TOTAL"] if len(ind_yearly) > 1 else 0
            else:
                ind_male = ind_female = ind_total = 0
                ind_delta_male = ind_delta_female = ind_delta_total = 0
                ind_latest = {"YEAR": "N/A"}

            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric(f"Total Male ({ind_latest['YEAR']})", f"{ind_male:,}", f"{ind_delta_male:+,}" if ind_delta_male != 0 else None)
            kpi2.metric(f"Total Female ({ind_latest['YEAR']})", f"{ind_female:,}", f"{ind_delta_female:+,}" if ind_delta_female != 0 else None)
            kpi3.metric(f"Total Employees ({ind_latest['YEAR']})", f"{ind_total:,}", f"{ind_delta_total:+,}" if ind_delta_total != 0 else None)

            # Data table with styling
            with st.expander(f"View {indicator} Data Table", expanded=False):
                styled_ind = df_ind_filtered.style.background_gradient(cmap='cool', subset=['MALE', 'FEMALE'])\
                                               .format({'MALE': '{:,.0f}', 'FEMALE': '{:,.0f}'})
                st.dataframe(styled_ind, use_container_width=True)
                csv_ind = df_ind_filtered.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=f"📥 Download {indicator} Data",
                    data=csv_ind,
                    file_name=f"{indicator}_{'_'.join(map(str, ind_selected_years))}.csv",
                    mime="text/csv"
                )

            # Prepare long format for charts
            df_ind_long = df_ind_filtered.melt(
                id_vars=['YEAR'],
                value_vars=['MALE', 'FEMALE'],
                var_name='Gender',
                value_name='Count'
            )
            df_ind_long['Gender'] = df_ind_long['Gender'].replace({'MALE': 'Male', 'FEMALE': 'Female'})

            # Row 1: Bar + Donut
            col1, col2 = st.columns(2)
            with col1:
                fig_bar = px.bar(
                    df_ind_long,
                    x='YEAR',
                    y='Count',
                    color='Gender',
                    barmode='group',
                    text='Count',
                    title=f"{indicator}: Male vs Female by Year",
                    color_discrete_map=custom_colors
                )
                fig_bar.update_traces(textposition='inside')
                st.plotly_chart(fig_bar, use_container_width=True)

            with col2:
                ind_total_gender = df_ind_filtered[['MALE', 'FEMALE']].sum().reset_index()
                ind_total_gender.columns = ['Gender', 'Total']
                ind_total_gender['Gender'] = ind_total_gender['Gender'].replace({'MALE': 'Male', 'FEMALE': 'Female'})
                fig_donut = px.pie(
                    ind_total_gender,
                    values='Total',
                    names='Gender',
                    hole=0.5,
                    color='Gender',
                    color_discrete_map=custom_colors,
                    title=f"{indicator}: Overall Gender Distribution"
                )
                st.plotly_chart(fig_donut, use_container_width=True)

            # Row 2: Line + Area
            col3, col4 = st.columns(2)
            with col3:
                fig_line = px.line(
                    df_ind_long,
                    x='YEAR',
                    y='Count',
                    color='Gender',
                    markers=True,
                    title=f"{indicator}: Gender Trends",
                    color_discrete_map=custom_colors
                )
                st.plotly_chart(fig_line, use_container_width=True)

            with col4:
                ind_pivot = df_ind_filtered.groupby('YEAR')[['MALE', 'FEMALE']].sum().reset_index()
                ind_pivot_long = ind_pivot.melt(id_vars='YEAR', var_name='Gender', value_name='Count')
                ind_pivot_long['Gender'] = ind_pivot_long['Gender'].replace({'MALE': 'Male', 'FEMALE': 'Female'})
                fig_area = px.area(
                    ind_pivot_long,
                    x='YEAR',
                    y='Count',
                    color='Gender',
                    title=f"{indicator}: Composition Over Time",
                    color_discrete_map=custom_colors
                )
                st.plotly_chart(fig_area, use_container_width=True)

            # YoY table (if multiple years)
            if len(ind_selected_years) > 1:
                ind_yoy = df_ind_filtered.groupby("YEAR")[["MALE", "FEMALE", "TOTAL"]].sum().reset_index()
                ind_yoy = ind_yoy.sort_values("YEAR")
                ind_yoy["CHANGE"] = ind_yoy["TOTAL"].diff().fillna(0).astype(int)
                ind_yoy["CHANGE_%"] = ind_yoy["TOTAL"].pct_change().fillna(0).map("{:.1%}".format)

                # Style change column
                def color_change(val):
                    color = 'green' if val > 0 else 'red' if val < 0 else 'black'
                    return f'color: {color}'

                styled_yoy = ind_yoy.style.applymap(color_change, subset=['CHANGE'])
                st.dataframe(styled_yoy, use_container_width=True)

# Entry point
if __name__ == "__main__":
    display()