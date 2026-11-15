import streamlit as st
import pandas as pd


st.markdown("""
<style>
div[data-testid="stMetric"] {
    background-color: #EAF5F2;
    border: 1px solid #A8DCD2;
    border-radius: 16px;
    padding: 18px;
    min-height: 130px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
}
div[data-testid="stMetricLabel"],
div[data-testid="stMetricValue"] {
    width: 100%;
    justify-content: center;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)


sheet_id = "12ViJCURtLCJ1PFl6wodONac_qeoXOXMBILujjfwwvC4"
def load_sheet(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    return pd.read_csv(url)

org_df = load_sheet("Organizations")
scholarship_df = load_sheet("Scholarships")
internship_df = load_sheet("Internships")

if st.session_state.get("show_results", False):
    st.image("MatchesBanner.png", use_container_width=True)

    if st.button("← Back to search"):
        st.session_state.show_results = False
        st.rerun()

    choices = st.session_state["choices"]
    def includes(cell, answer):
        options = [item.strip().lower() for item in str(cell).split(",")]
        return answer.lower() in options

    student_major = choices["major"]
    student_standing = choices["standing"].replace("Graduate student", "Graduate")

    wanted_org_majors = choices["org_majors"] or [student_major]
    org_matches = org_df[
        org_df["Major"].apply(
            lambda value: includes(value, "Any")
            or any(includes(value, major) for major in wanted_org_majors)
        )
    ]

    if choices["org_interests"]:
        org_matches = org_matches[
            org_matches["Interests"].isin(choices["org_interests"])
        ]

    scholarship_matches = scholarship_df[
        scholarship_df["Major"].apply(lambda value: includes(value, student_major))
        & scholarship_df["Class Standing"].apply(
            lambda value: includes(value, student_standing)
        )
    ]

    internship_matches = internship_df[
        internship_df["Major"].apply(lambda value: includes(value, student_major))
        & internship_df["Class Standing"].apply(
            lambda value: includes(value, student_standing)
        )
    ]

    if choices["locations"]:
        locations = [
            "Onsite" if location == "On-site" else location
            for location in choices["locations"]
        ]
        internship_matches = internship_matches[
            internship_matches["Location"].isin(locations)
        ]

    if choices["work_types"]:
        internship_matches = internship_matches[
            internship_matches["Work Type"].isin(choices["work_types"])
        ]

    if choices["paid_only"]:
        internship_matches = internship_matches[
            internship_matches["Paid"].astype(str).str.lower() == "true"
        ]

    selected = []
    if choices["organizations"]:
        selected.append(("Organizations", org_matches, "Student Org"))
    if choices["scholarships"]:
        selected.append(("Scholarships", scholarship_matches, "Scholarship Name"))
    if choices["internships"]:
        selected.append(("Internships", internship_matches, "Internship Name"))

    st.write(f"**{choices['standing']} · {choices['major']}**")

    # Summary cards at the top of the dashboard
    card_count = len(selected) + (1 if choices["scholarships"] else 0)
    metric_columns = st.columns(card_count)

    for column, (label, data, _) in zip(metric_columns, selected):
        column.metric(label, len(data), border=True)

    if choices["scholarships"]:
        amounts = pd.to_numeric(
            scholarship_matches["Money"].astype(str)
            .str.replace(",", "")
            .str.replace("$", "", regex=False),
            errors="coerce"
        )
        metric_columns[-1].metric(
            "Total Awards",
            f"${amounts.sum() / 1000:,.1f}K".replace(".0K", "K"),
            border=True
        )

    tabs = st.tabs([item[0] for item in selected])

    for tab, (label, data, name_column) in zip(tabs, selected):
        with tab:
            st.subheader(f"Potential {label.lower()}")

            if data.empty:
                st.info("No listings match this search. Try changing a preference.")
            else:
                for _, row in data.iterrows():
                    with st.container(border=True):
                        st.write(f"**{row[name_column]}**")

                        if label == "Organizations":
                            st.caption(f"{row['Interests']} · {row['Major']}")

                        elif label == "Scholarships":
                            st.caption(f"{row['Major']} · {row['Class Standing']}")
                            if pd.notna(row["Money"]):
                                st.write(f"Award: ${row['Money']}")

                        elif label == "Internships":
                            st.caption(
                                f"{row['Company']} · {row['Location']} · "
                                f"{row['Work Type']}"
                            )
                            st.write(
                                "Paid" if str(row["Paid"]).lower() == "true"
                                else "Unpaid"
                            )

                        link = row.get("URL")
                        if pd.notna(link) and str(link).strip().startswith(
                            ("https://", "http://")
                        ):
                            st.link_button("View opportunity ↗", str(link).strip())

    st.stop()

left, center, right = st.columns([1, 3, 1])
with center:
    st.image("spotUNITYbig.png", use_container_width=True)

st.markdown(
    "<h3 style='text-align:center; color:#102d50;'>"
    "Find your people. Fund your future. Build your path."
    "</h3>",
    unsafe_allow_html=True,
)


standing = st.selectbox(
   "What is your class standing?",
   ["Select class standing", "Freshman", "Sophomore", "Junior", "Senior", "Graduate student"]
)
major = st.selectbox(
   "What is your major?",
   ["Select a Major", "Computer Science", "Mechanical Engineering", "Electrical Engineering", "Business", "Public Health"]
)



st.write("What are you looking for?")
col1, col2, col3 = st.columns(3)

with col1:
    org_box = st.checkbox("Organizations")

    if org_box:
        _, org_options = st.columns([1, 9])

        with org_options:
            academic_org = st.checkbox("Academic", key="org_academic")

            if academic_org:
                _, major_options = st.columns([1, 9])

                with major_options:
                    cs_acd = st.checkbox("Computer Science", key="cs_acd")
                    me_acd = st.checkbox("Mechanical Engineering", key="me_acd")
                    ee_acd = st.checkbox("Electrical Engineering", key="ee_acd")
                    bus_acd = st.checkbox("Business", key="bus_acd")
                    pubh_acd = st.checkbox("Public Health", key="pubh_acd")

            social_org = st.checkbox("Social", key="org_social")
 
with col2:
    scholarship_box = st.checkbox("Scholarships")

with col3:
   internship_box = st.checkbox("Internships")
   if internship_box:
       location_box = st.multiselect("Preferred Location", ["Remote", "On-site", "Hybrid"], key="internship_location")
       parttime_box = st.checkbox("Part-time", key="internship_parttime")
       fulltime_box = st.checkbox("Full-time", key="internship_fulltime")
       paid_box = st.checkbox("Paid", key="internship_paid")

if st.button("Find My Opportunities!"):
    if standing == "Select class standing":
        st.warning("Please select your class standing.")
    elif major == "Select a Major":
        st.warning("Please select your major.")
    elif not (org_box or scholarship_box or internship_box):
        st.warning("Choose at least one type of opportunity.")
    else:
        st.session_state["choices"] = {
            "standing": standing,
            "major": major,
            "organizations": org_box,
            "scholarships": scholarship_box,
            "internships": internship_box,

            "org_interests": [
    label for label, key in [
        ("Academic", "org_academic"),
        ("Social", "org_social"),
    ]
    if st.session_state.get(key, False)
],

"org_majors": [
    label for label, key in [
        ("Computer Science", "cs_acd"),
        ("Mechanical Engineering", "me_acd"),
        ("Electrical Engineering", "ee_acd"),
        ("Business", "bus_acd"),
        ("Public Health", "pubh_acd"),
    ]
    if st.session_state.get(key, False)
],

"locations": st.session_state.get("internship_location", []),
"work_types": [
    label for label, key in [
        ("Part-time", "internship_parttime"),
        ("Full-time", "internship_fulltime"),
    ]
    if st.session_state.get(key, False)
],
"paid_only": st.session_state.get("internship_paid", False),
        }
        st.session_state.show_results = True
        st.rerun()