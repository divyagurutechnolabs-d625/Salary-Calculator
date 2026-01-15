import streamlit as st
from decimal import Decimal, ROUND_HALF_UP


##set title
st.set_page_config(layout="wide")
st.markdown(
    "<h3 style='text-align:center; margin:0;'>SALARY CALCULATOR</h3>",
    unsafe_allow_html=True,
)


## set height and width
st.markdown(
    """
<style>
.full-box {
    min-height: 80vh;
    padding: 25;
    border-radius: 14px;
    background-color: #f5f7fa;
}
</style>
""",
    unsafe_allow_html=True,
)


# -------------------------
# COMPANY RULES (Editable)
# -------------------------
with st.expander("Company Rules"):
    col1, col2 = st.columns(2)

    with col1:

        ##--------set hours per day---------##
        paid_hours_per_day = st.number_input("Paid Hours Per Day", value=8.5)
        st.write("")

        ##------Months-----##
        months = st.selectbox(
            "Months",
            [
                "January",
                "February",
                "March",
                "April",
                "May",
                "June",
                "July",
                "August",
                "September",
                "October",
                "November",
                "December",
            ],
        )

        days_in_month = {
            "January": 31,
            "February": 28,
            "March": 31,
            "April": 30,
            "May": 31,
            "June": 30,
            "July": 31,
            "August": 31,
            "September": 30,
            "October": 31,
            "November": 30,
            "December": 31,
        }[months]

        st.write("")
        ##-----------------##

    with col2:

        ##-----set company hour per months-----##
        compulsory_hour = st.number_input("Total Working Hours (Month)", value=195.0)
        st.write("")


##-----set from and smmary parts------##
left_col, right_col = st.columns(2)  # from and summary


##-----reset function-----##
def reset_form():
    st.session_state["salary_input"] = 0
    st.session_state["worked_hours_input"] = 186.50
    st.session_state["reserved_level_hours"] = 0
    st.session_state["late_option_input"] = "No Late"
    st.session_state["submit_clicked"] = False


if "submit_clicked" not in st.session_state:
    st.session_state["submit_clicked"] = False


# -------------------------
# ADMIN INPUT (Form)
# -------------------------
with left_col:
    with st.form("salary_form"):
        colA, colB = st.columns(2)

        with colA:
            ## salary filed of employee
            salary = st.number_input(
                "Enter Employee Salary", min_value=0, step=1, key="salary_input"
            )
            st.write("")

            ## working hours filed of employee
            worked_hours = st.number_input(
                "Enter Employee Working Hours",
                ## min_value=0.0,
                value=186.50,
                key="worked_hours_input",
            )
            st.write("")

        with colB:

            ##drop down for late comming filed
            late_opetion = st.selectbox(
                "Late Coming",
                [
                    "No Late",
                    "3 Times Late (Half Day Cut)",
                    "6 Times Late (1 Day Cut)",
                    "9 Times Late (1.5 Day Cut)",
                    "12 Times Late (2 Day Cut)",
                    "15 Times Late (2.5 Day Cut)",
                    "18 Times Late (3 Day Cut)",
                    "21 Times Late (3.5 Day Cut)",
                    "24 Times Late (4 Day Cut)",
                    "27 Times Late (4.5 Day Cut)",
                    "30 Times Late (5 Day Cut)",
                ],
                key="late_option_input",
            )

            late_comming_count = {
                "No Late": 0,
                "3 Times Late (Half Day Cut)": 3,
                "6 Times Late (1 Day Cut)": 6,
                "9 Times Late (1.5 Day Cut)": 9,
                "12 Times Late (2 Day Cut)": 12,
                "15 Times Late (2.5 Day Cut)": 15,
                "18 Times Late (3 Day Cut)": 18,
                "21 Times Late (3.5 Day Cut)": 21,
                "24 Times Late  (4 Day Cut)": 24,
                "27 Times Late (4.5 Day Cut)": 27,
                "30 Times Late (5 Day Cut)": 30,
            }[late_opetion]

            st.write("")

            ## Reserved Level Hours of employee
            Reserved_level_hours = st.number_input(
                "Enter Reserved Level Hours", min_value=0.0, key="reserved_level_hours"
            )

        st.write("")

        submit_col, reset_col = st.columns(2)

        ## Form submit button
        with submit_col:
            submit = st.form_submit_button("Calculate")
            if submit:
                st.session_state["submit_clicked"] = True

        ## reset button
        with reset_col:
            reset = st.form_submit_button("Reset", on_click=reset_form)


# -------------------------
# CALCULATION Logic of salary
# -------------------------
if submit:

    with right_col:

        # days_in_month = 31

        ## -------------------- Rates -------------------- ##
        hours_rate = salary / days_in_month / paid_hours_per_day  ## hours base
        day_salary = salary / days_in_month  ## salary base
        ## ----------------------------------------------- ##

        # -------------- AUTO RESERVED HOURS ------------------#
        ## calculate paid hours of employee
        auto_reserved_level = max(compulsory_hour - worked_hours, 0)
        auto_reserved_level = min(auto_reserved_level, paid_hours_per_day)

        ## Calculate shortage WITHOUT counting manual reserved hours
        worked_hours = (
            worked_hours + Reserved_level_hours
        )  ## add employee Reserved level hours to employee work hours

        final_working_hours_for_cut = worked_hours + auto_reserved_level
        uncovered_shortage = max(compulsory_hour - final_working_hours_for_cut, 0)
        hour_cut_amount = Decimal(str(uncovered_shortage)) * Decimal(str(hours_rate))

        ## --------------------------------------------------------- ##

        ## --------- Late Comming Deductions --------- ##
        if late_comming_count == 0:
            late_days = Decimal("0")

        else:
            ## Every 3 late = 0.5 day salary cut
            late_days = Decimal(late_comming_count) / Decimal("3") * Decimal("0.5")

        late_deduction = late_days * Decimal(str(day_salary))

        late_text = f"{late_days} Day Salary Cut"

        ## ----------------------------------------------- ##

        ## ---------------------- Total salary -------------------- ##
        salary_d = Decimal(str(salary))
        late_deduction_d = Decimal(str(late_deduction))
        hour_cut_d = Decimal(str(hour_cut_amount))
        total_salary = salary_d - late_deduction_d - hour_cut_amount

        if total_salary < 0:
            total_salary = Decimal("0")

        total_salary = total_salary.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        ## ---------------------------------------------------------- ##

        # -------------------------
        # Centered Salary Summary
        # -------------------------

        st.write("")

        st.markdown(
            f"<h2 style='text-align: center; color: green;'>Total Salary: ₹{total_salary:,}</h2>",
            unsafe_allow_html=True,
        )

        st.subheader("**Salary Summary**")
        st.write(f"💰 **Total Salary:**  ₹{total_salary:,}")
        st.write(f"✅ **Company Working Hours:** {compulsory_hour:.2f}")
        st.write(f"✅ **Employee Working Hours:**  {worked_hours:.2f}")
        st.write(f"📦 **Reserved Level Hours:** {auto_reserved_level:.2f}")
        st.write(f"⏰ **Late Coming:**  {late_opetion}")
        st.write(f"📉 **Late Deduction:**  ₹{int(late_deduction)}")

        st.markdown("</div>", unsafe_allow_html=True)
