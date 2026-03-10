import streamlit as st
import plotly.express as px
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# -------------------- CACHE DATA LOADING --------------------
@st.cache_data
def load_data(sheet_name="social"):
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
    st.set_page_config(page_title="Social Welfare & Development Office Dashboard", layout="wide")
    st.title(":bar_chart: City Social Welfare & Development Office")

    # Global contact info (preserved from original)
    st.info("For more details, please contact: CSWD Office - 123-456-7890")

    # Load data
    df = load_data("social")
    if df is None:
        st.stop()

    # Define custom gender colors (used throughout)
    custom_colors = {'Male': '#347dc1', 'Female': '#e6a6c7'}

    # -------------------- REGULAR INDICATOR --------------------
    df_regular = df[df['INDICATOR'] == 'REGULAR'].copy()
    if not df_regular.empty:
        with st.expander("View REGULAR EMPLOYEE Data", expanded=False):
            st.subheader("REGULAR Employees")

            # Year filter (specific to this indicator)
            reg_years = sorted(df_regular["YEAR"].unique())
            reg_selected_years = st.multiselect(
                "Select Year(s) for REGULAR",
                reg_years,
                default=reg_years[:2] if len(reg_years) >= 2 else reg_years,
                key="reg_years"
            )
            if not reg_selected_years:
                st.warning("Please select at least one year for REGULAR.")
                st.stop()
            df_reg_filtered = df_regular[df_regular["YEAR"].isin(reg_selected_years)]

            # KPIs for latest year
            if not df_reg_filtered.empty:
                reg_yearly = df_reg_filtered.groupby("YEAR")[["MALE", "FEMALE", "TOTAL"]].sum().reset_index()
                reg_yearly = reg_yearly.sort_values("YEAR")
                reg_latest = reg_yearly.iloc[-1]

                reg_male = reg_latest["MALE"]
                reg_female = reg_latest["FEMALE"]
                reg_total = reg_latest["TOTAL"]
                reg_delta_male = reg_male - reg_yearly.iloc[-2]["MALE"] if len(reg_yearly) > 1 else 0
                reg_delta_female = reg_female - reg_yearly.iloc[-2]["FEMALE"] if len(reg_yearly) > 1 else 0
                reg_delta_total = reg_total - reg_yearly.iloc[-2]["TOTAL"] if len(reg_yearly) > 1 else 0
            else:
                reg_male = reg_female = reg_total = reg_delta_male = reg_delta_female = reg_delta_total = 0
                reg_latest = {"YEAR": "N/A"}

            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric(f"Total Male ({reg_latest['YEAR']})", f"{reg_male:,}", f"{reg_delta_male:+,}" if reg_delta_male != 0 else None)
            kpi2.metric(f"Total Female ({reg_latest['YEAR']})", f"{reg_female:,}", f"{reg_delta_female:+,}" if reg_delta_female != 0 else None)
            kpi3.metric(f"Total Employees ({reg_latest['YEAR']})", f"{reg_total:,}", f"{reg_delta_total:+,}" if reg_delta_total != 0 else None)

            # Data table with styling
            with st.expander("View REGULAR Data Table", expanded=False):
                styled_reg = df_reg_filtered.style.background_gradient(cmap='cool', subset=['MALE', 'FEMALE'])\
                                               .format({'MALE': '{:,.0f}', 'FEMALE': '{:,.0f}'})
                st.dataframe(styled_reg, use_container_width=True)
                csv_reg = df_reg_filtered.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download REGULAR Data", data=csv_reg,
                                   file_name=f"regular_{'_'.join(map(str, reg_selected_years))}.csv", mime="text/csv")

            # Prepare long format for charts
            df_reg_long = df_reg_filtered.melt(id_vars=['YEAR'], value_vars=['MALE', 'FEMALE'],
                                               var_name='Gender', value_name='Count')
            df_reg_long['Gender'] = df_reg_long['Gender'].replace({'MALE': 'Male', 'FEMALE': 'Female'})

            # Row 1: Bar + Donut
            col1, col2 = st.columns(2)
            with col1:
                fig_bar = px.bar(df_reg_long, x='YEAR', y='Count', color='Gender', barmode='group',
                                 text='Count', title="REGULAR: Male vs Female by Year",
                                 color_discrete_map=custom_colors)
                fig_bar.update_traces(textposition='inside')
                st.plotly_chart(fig_bar, use_container_width=True)
            with col2:
                reg_total_gender = df_reg_filtered[['MALE', 'FEMALE']].sum().reset_index()
                reg_total_gender.columns = ['Gender', 'Total']
                reg_total_gender['Gender'] = reg_total_gender['Gender'].replace({'MALE': 'Male', 'FEMALE': 'Female'})
                fig_donut = px.pie(reg_total_gender, values='Total', names='Gender', hole=0.5,
                                   color='Gender', color_discrete_map=custom_colors,
                                   title=f"REGULAR: Overall Gender Distribution")
                st.plotly_chart(fig_donut, use_container_width=True)

            # Row 2: Line + Area
            col3, col4 = st.columns(2)
            with col3:
                fig_line = px.line(df_reg_long, x='YEAR', y='Count', color='Gender', markers=True,
                                   title="REGULAR: Gender Trends", color_discrete_map=custom_colors)
                st.plotly_chart(fig_line, use_container_width=True)
            with col4:
                reg_pivot = df_reg_filtered.groupby('YEAR')[['MALE', 'FEMALE']].sum().reset_index()
                reg_pivot_long = reg_pivot.melt(id_vars='YEAR', var_name='Gender', value_name='Count')
                reg_pivot_long['Gender'] = reg_pivot_long['Gender'].replace({'MALE': 'Male', 'FEMALE': 'Female'})
                fig_area = px.area(reg_pivot_long, x='YEAR', y='Count', color='Gender',
                                   title="REGULAR: Composition Over Time", color_discrete_map=custom_colors)
                st.plotly_chart(fig_area, use_container_width=True)

            # YoY table
            if len(reg_selected_years) > 1:
                reg_yoy = df_reg_filtered.groupby("YEAR")[["MALE", "FEMALE", "TOTAL"]].sum().reset_index()
                reg_yoy = reg_yoy.sort_values("YEAR")
                reg_yoy["CHANGE"] = reg_yoy["TOTAL"].diff().fillna(0).astype(int)
                reg_yoy["CHANGE_%"] = reg_yoy["TOTAL"].pct_change().fillna(0).map("{:.1%}".format)
                styled_yoy = reg_yoy.style.applymap(lambda v: 'color: green' if v > 0 else ('color: red' if v < 0 else 'color: black'), subset=['CHANGE'])
                st.dataframe(styled_yoy, use_container_width=True)

    # -------------------- PWD REGULAR EMPLOYEE INDICATOR --------------------
    df_pwd_reg = df[df['INDICATOR'] == 'PWD REGULAR EMPLOYEE'].copy()
    if not df_pwd_reg.empty:
        with st.expander("View PWD LGU Regular Employee Data", expanded=False):
            st.subheader("PWD REGULAR EMPLOYEES")

            pwd_reg_years = sorted(df_pwd_reg["YEAR"].unique())
            pwd_reg_selected = st.multiselect("Select Year(s) for PWD REGULAR", pwd_reg_years,
                                              default=pwd_reg_years[:2] if len(pwd_reg_years) >= 2 else pwd_reg_years,
                                              key="pwd_reg_years")
            if not pwd_reg_selected:
                st.warning("Please select at least one year for PWD REGULAR.")
                st.stop()
            df_pwd_reg_filtered = df_pwd_reg[df_pwd_reg["YEAR"].isin(pwd_reg_selected)]

            # KPIs
            if not df_pwd_reg_filtered.empty:
                pwd_reg_yearly = df_pwd_reg_filtered.groupby("YEAR")[["MALE", "FEMALE", "TOTAL"]].sum().reset_index()
                pwd_reg_yearly = pwd_reg_yearly.sort_values("YEAR")
                pwd_reg_latest = pwd_reg_yearly.iloc[-1]
                pwd_reg_male = pwd_reg_latest["MALE"]
                pwd_reg_female = pwd_reg_latest["FEMALE"]
                pwd_reg_total = pwd_reg_latest["TOTAL"]
                pwd_reg_delta_male = pwd_reg_male - pwd_reg_yearly.iloc[-2]["MALE"] if len(pwd_reg_yearly) > 1 else 0
                pwd_reg_delta_female = pwd_reg_female - pwd_reg_yearly.iloc[-2]["FEMALE"] if len(pwd_reg_yearly) > 1 else 0
                pwd_reg_delta_total = pwd_reg_total - pwd_reg_yearly.iloc[-2]["TOTAL"] if len(pwd_reg_yearly) > 1 else 0
            else:
                pwd_reg_male = pwd_reg_female = pwd_reg_total = 0
                pwd_reg_delta_male = pwd_reg_delta_female = pwd_reg_delta_total = 0
                pwd_reg_latest = {"YEAR": "N/A"}

            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric(f"Total Male ({pwd_reg_latest['YEAR']})", f"{pwd_reg_male:,}", f"{pwd_reg_delta_male:+,}" if pwd_reg_delta_male != 0 else None)
            kpi2.metric(f"Total Female ({pwd_reg_latest['YEAR']})", f"{pwd_reg_female:,}", f"{pwd_reg_delta_female:+,}" if pwd_reg_delta_female != 0 else None)
            kpi3.metric(f"Total Employees ({pwd_reg_latest['YEAR']})", f"{pwd_reg_total:,}", f"{pwd_reg_delta_total:+,}" if pwd_reg_delta_total != 0 else None)

            # Data table (use 'Purples' colormap as in original)
            with st.expander("View PWD REGULAR Data Table", expanded=False):
                styled_pwd_reg = df_pwd_reg_filtered.style.background_gradient(cmap='Purples', subset=['MALE', 'FEMALE'])\
                                                      .format({'MALE': '{:,.0f}', 'FEMALE': '{:,.0f}'})
                st.dataframe(styled_pwd_reg, use_container_width=True)
                csv_pwd_reg = df_pwd_reg_filtered.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download PWD REGULAR Data", data=csv_pwd_reg,
                                   file_name=f"pwd_reg_{'_'.join(map(str, pwd_reg_selected))}.csv", mime="text/csv")

            # Prepare long format
            df_pwd_reg_long = df_pwd_reg_filtered.melt(id_vars=['YEAR'], value_vars=['MALE', 'FEMALE'],
                                                       var_name='Gender', value_name='Count')
            df_pwd_reg_long['Gender'] = df_pwd_reg_long['Gender'].replace({'MALE': 'Male', 'FEMALE': 'Female'})

            # Row 1: Bar + Donut
            col1, col2 = st.columns(2)
            with col1:
                fig_bar = px.bar(df_pwd_reg_long, x='YEAR', y='Count', color='Gender', barmode='group',
                                 text='Count', title="PWD REGULAR: Male vs Female by Year",
                                 color_discrete_map=custom_colors)
                fig_bar.update_traces(textposition='inside')
                st.plotly_chart(fig_bar, use_container_width=True)
            with col2:
                pwd_reg_total_gender = df_pwd_reg_filtered[['MALE', 'FEMALE']].sum().reset_index()
                pwd_reg_total_gender.columns = ['Gender', 'Total']
                pwd_reg_total_gender['Gender'] = pwd_reg_total_gender['Gender'].replace({'MALE': 'Male', 'FEMALE': 'Female'})
                fig_donut = px.pie(pwd_reg_total_gender, values='Total', names='Gender', hole=0.5,
                                   color='Gender', color_discrete_map=custom_colors,
                                   title="PWD REGULAR: Overall Gender Distribution")
                st.plotly_chart(fig_donut, use_container_width=True)

            # Row 2: Line + Area
            col3, col4 = st.columns(2)
            with col3:
                fig_line = px.line(df_pwd_reg_long, x='YEAR', y='Count', color='Gender', markers=True,
                                   title="PWD REGULAR: Gender Trends", color_discrete_map=custom_colors)
                st.plotly_chart(fig_line, use_container_width=True)
            with col4:
                pwd_reg_pivot = df_pwd_reg_filtered.groupby('YEAR')[['MALE', 'FEMALE']].sum().reset_index()
                pwd_reg_pivot_long = pwd_reg_pivot.melt(id_vars='YEAR', var_name='Gender', value_name='Count')
                pwd_reg_pivot_long['Gender'] = pwd_reg_pivot_long['Gender'].replace({'MALE': 'Male', 'FEMALE': 'Female'})
                fig_area = px.area(pwd_reg_pivot_long, x='YEAR', y='Count', color='Gender',
                                   title="PWD REGULAR: Composition Over Time", color_discrete_map=custom_colors)
                st.plotly_chart(fig_area, use_container_width=True)

            # YoY table
            if len(pwd_reg_selected) > 1:
                pwd_reg_yoy = df_pwd_reg_filtered.groupby("YEAR")[["MALE", "FEMALE", "TOTAL"]].sum().reset_index()
                pwd_reg_yoy = pwd_reg_yoy.sort_values("YEAR")
                pwd_reg_yoy["CHANGE"] = pwd_reg_yoy["TOTAL"].diff().fillna(0).astype(int)
                pwd_reg_yoy["CHANGE_%"] = pwd_reg_yoy["TOTAL"].pct_change().fillna(0).map("{:.1%}".format)
                styled_yoy = pwd_reg_yoy.style.applymap(lambda v: 'color: green' if v > 0 else ('color: red' if v < 0 else 'color: black'), subset=['CHANGE'])
                st.dataframe(styled_yoy, use_container_width=True)

    # -------------------- PWD CHILDREN INDICATOR --------------------
    df_pwd_child = df[df['INDICATOR'] == 'PWD CHILDREN'].copy()
    if not df_pwd_child.empty:
        with st.expander("View CHILDREN PWD Data", expanded=False):
            st.subheader("CHILDREN PWD")

            pwd_child_years = sorted(df_pwd_child["YEAR"].unique())
            pwd_child_selected = st.multiselect("Select Year(s) for CHILDREN PWD", pwd_child_years,
                                                default=pwd_child_years[:2] if len(pwd_child_years) >= 2 else pwd_child_years,
                                                key="pwd_child_years")
            if not pwd_child_selected:
                st.warning("Please select at least one year for CHILDREN PWD.")
                st.stop()
            df_pwd_child_filtered = df_pwd_child[df_pwd_child["YEAR"].isin(pwd_child_selected)]

            # KPIs
            if not df_pwd_child_filtered.empty:
                pwd_child_yearly = df_pwd_child_filtered.groupby("YEAR")[["MALE", "FEMALE", "TOTAL"]].sum().reset_index()
                pwd_child_yearly = pwd_child_yearly.sort_values("YEAR")
                pwd_child_latest = pwd_child_yearly.iloc[-1]
                pwd_child_male = pwd_child_latest["MALE"]
                pwd_child_female = pwd_child_latest["FEMALE"]
                pwd_child_total = pwd_child_latest["TOTAL"]
                pwd_child_delta_male = pwd_child_male - pwd_child_yearly.iloc[-2]["MALE"] if len(pwd_child_yearly) > 1 else 0
                pwd_child_delta_female = pwd_child_female - pwd_child_yearly.iloc[-2]["FEMALE"] if len(pwd_child_yearly) > 1 else 0
                pwd_child_delta_total = pwd_child_total - pwd_child_yearly.iloc[-2]["TOTAL"] if len(pwd_child_yearly) > 1 else 0
            else:
                pwd_child_male = pwd_child_female = pwd_child_total = 0
                pwd_child_delta_male = pwd_child_delta_female = pwd_child_delta_total = 0
                pwd_child_latest = {"YEAR": "N/A"}

            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric(f"Total Male ({pwd_child_latest['YEAR']})", f"{pwd_child_male:,}", f"{pwd_child_delta_male:+,}" if pwd_child_delta_male != 0 else None)
            kpi2.metric(f"Total Female ({pwd_child_latest['YEAR']})", f"{pwd_child_female:,}", f"{pwd_child_delta_female:+,}" if pwd_child_delta_female != 0 else None)
            kpi3.metric(f"Total Children ({pwd_child_latest['YEAR']})", f"{pwd_child_total:,}", f"{pwd_child_delta_total:+,}" if pwd_child_delta_total != 0 else None)

            # Data table (use 'Purples')
            with st.expander("View CHILDREN PWD Data Table", expanded=False):
                styled_pwd_child = df_pwd_child_filtered.style.background_gradient(cmap='Purples', subset=['MALE', 'FEMALE'])\
                                                          .format({'MALE': '{:,.0f}', 'FEMALE': '{:,.0f}'})
                st.dataframe(styled_pwd_child, use_container_width=True)
                csv_pwd_child = df_pwd_child_filtered.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download CHILDREN PWD Data", data=csv_pwd_child,
                                   file_name=f"pwd_child_{'_'.join(map(str, pwd_child_selected))}.csv", mime="text/csv")

            # Prepare long format
            df_pwd_child_long = df_pwd_child_filtered.melt(id_vars=['YEAR'], value_vars=['MALE', 'FEMALE'],
                                                           var_name='Gender', value_name='Count')
            df_pwd_child_long['Gender'] = df_pwd_child_long['Gender'].replace({'MALE': 'Male', 'FEMALE': 'Female'})

            # Row 1: Bar + Donut
            col1, col2 = st.columns(2)
            with col1:
                fig_bar = px.bar(df_pwd_child_long, x='YEAR', y='Count', color='Gender', barmode='group',
                                 text='Count', title="CHILDREN PWD: Male vs Female by Year",
                                 color_discrete_map=custom_colors)
                fig_bar.update_traces(textposition='inside')
                st.plotly_chart(fig_bar, use_container_width=True)
            with col2:
                pwd_child_total_gender = df_pwd_child_filtered[['MALE', 'FEMALE']].sum().reset_index()
                pwd_child_total_gender.columns = ['Gender', 'Total']
                pwd_child_total_gender['Gender'] = pwd_child_total_gender['Gender'].replace({'MALE': 'Male', 'FEMALE': 'Female'})
                fig_donut = px.pie(pwd_child_total_gender, values='Total', names='Gender', hole=0.5,
                                   color='Gender', color_discrete_map=custom_colors,
                                   title="CHILDREN PWD: Overall Gender Distribution")
                st.plotly_chart(fig_donut, use_container_width=True)

            # Row 2: Line + Area
            col3, col4 = st.columns(2)
            with col3:
                fig_line = px.line(df_pwd_child_long, x='YEAR', y='Count', color='Gender', markers=True,
                                   title="CHILDREN PWD: Gender Trends", color_discrete_map=custom_colors)
                st.plotly_chart(fig_line, use_container_width=True)
            with col4:
                pwd_child_pivot = df_pwd_child_filtered.groupby('YEAR')[['MALE', 'FEMALE']].sum().reset_index()
                pwd_child_pivot_long = pwd_child_pivot.melt(id_vars='YEAR', var_name='Gender', value_name='Count')
                pwd_child_pivot_long['Gender'] = pwd_child_pivot_long['Gender'].replace({'MALE': 'Male', 'FEMALE': 'Female'})
                fig_area = px.area(pwd_child_pivot_long, x='YEAR', y='Count', color='Gender',
                                   title="CHILDREN PWD: Composition Over Time", color_discrete_map=custom_colors)
                st.plotly_chart(fig_area, use_container_width=True)

            # YoY table
            if len(pwd_child_selected) > 1:
                pwd_child_yoy = df_pwd_child_filtered.groupby("YEAR")[["MALE", "FEMALE", "TOTAL"]].sum().reset_index()
                pwd_child_yoy = pwd_child_yoy.sort_values("YEAR")
                pwd_child_yoy["CHANGE"] = pwd_child_yoy["TOTAL"].diff().fillna(0).astype(int)
                pwd_child_yoy["CHANGE_%"] = pwd_child_yoy["TOTAL"].pct_change().fillna(0).map("{:.1%}".format)
                styled_yoy = pwd_child_yoy.style.applymap(lambda v: 'color: green' if v > 0 else ('color: red' if v < 0 else 'color: black'), subset=['CHANGE'])
                st.dataframe(styled_yoy, use_container_width=True)

# Entry point
if __name__ == "__main__":
    display()