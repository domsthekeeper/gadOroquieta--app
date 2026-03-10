import streamlit as st
from overall import display as display_overall
from city_mayor import display as display_city_mayor
from sangguniang_panlungsod import display as display_sangguniang_panlungsod
from accounting import display as display_accounting
from administrator import display as display_administrator
from assessors import display as display_assessors
from agriculture import display as display_agriculture
from budget import display as display_budget
from disaster import display as display_disaster
from economic import display as display_economic
from engineers import display as display_engineers
from health import display as display_health
from legal import display as display_legal
from social import display as display_social
from treasurers import display as display_treasurers
from general_services import display as display_general_services
from human_resource import display as display_human_resource
from local_registrar import display as display_local_registrar
from public_service import display as display_public_service
from building_official import display as display_building_official
from city_planning import display as display_city_planning
from sds import display as display_sds
from city_vice_mayor import display as display_city_vice_mayor

# Title for the page
st.set_page_config(page_title="Gad Database", page_icon=":bar_chart:", layout="wide")

# Display the logo in the sidebar
st.sidebar.image("oroquietalogo.png", use_container_width=True)

# Sidebar navigation
st.sidebar.title("Gender and Development Database")
page = st.sidebar.selectbox("Select Office", ["All", "City Mayor Office", "City Vice Mayor Office", "Sangguniang Panglungsod",
                                              "City Accounting Office", "Office of the Administrator", "City Assessors Office",
                                              "City Agriculture & Fisheries Office", "City Budget Office", "City Disaster Risk Reduction Management Office",
                                              "City Economic Enterprise & Development Office", "City Engineer’s Office",
                                              "City Health Office", "City Legal Office", "City Social Welfare & Development Office", "City Treasurer’s Office",
                                              "City General Services Office", "Human Resource Management Office", "Local Civil Registrar’s Office",
                                              "Office of the City Public Service", "Office of the Building Official", "Office of the City Planning and Development Coordinator",
                                              "Office of the Schools Division Superintendent"])

# Admin access restriction for City Mayor Office
if page == "City Mayor Office":
    # password = st.text_input("Enter Admin Password:", type="password")
    # if password == "admin123":  # Change this to a secure password
    #     st.success("Access Granted!")
    #     display_city_mayor()
    # elif password:
    #     st.error("Access Denied!")
# Display the selected page 
    display_city_mayor()
elif page == "All":
    display_overall()
elif page == "City Vice Mayor Office":
    display_city_vice_mayor()
elif page == "Sangguniang Panglungsod":
    display_sangguniang_panlungsod()
elif page == "City Accounting Office":
    display_accounting()
elif page == "Office of the Administrator":
    display_administrator()
elif page == "City Assessors Office":
    display_assessors()
elif page == "City Agriculture & Fisheries Office":
    display_agriculture()
elif page == "City Budget Office":
    display_budget()
elif page == "City Disaster Risk Reduction Management Office":
    display_disaster()
elif page == "City Economic Enterprise & Development Office":
    display_economic()
elif page == "City Engineer’s Office":
    display_engineers()
elif page == "City Health Office":
    display_health()
elif page == "City Legal Office":
    display_legal()
elif page == "City Social Welfare & Development Office":
    display_social()
elif page == "City Treasurer’s Office":
    display_treasurers()
elif page == "City General Services Office":
    display_general_services()
elif page == "Human Resource Management Office":
    display_human_resource()
elif page == "Local Civil Registrar’s Office":
    display_local_registrar()
elif page == "Office of the City Public Service":
    display_public_service()
elif page == "Office of the Building Official":
    display_building_official()
elif page == "Office of the City Planning and Development Coordinator":
    display_city_planning()
elif page == "Office of the Schools Division Superintendent":
    display_sds()
