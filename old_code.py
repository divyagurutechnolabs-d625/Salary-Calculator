import streamlit as st
from decimal import Decimal, ROUND_HALF_UP


st.set_page_config(layout="wide")
st.markdown(
    "<h3 style='text-align:center; margin:0;'>SALARY CALCULATOR</h3>",
    unsafe_allow_html=True,
)


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
        # total_working_hours=st.number_input(
        #     "Total Working Hours (Month)",
        #     value=195.5
        # )
        # st.write("")

        paid_hours_per_day = st.number_input("Paid Hours Per Day", value=8.5)
        st.write("")

    with col2:
        compulsory_hour = st.number_input("Compulsory Working Hours", value=187.0)
        st.write("")

        days_in_month = st.number_input("Days in Month", value=31, step=1)
        st.write("")


left_col, right_col = st.columns(2)  # from and summary


##reset function
def reset_form():
    st.session_state["salary_input"] = 0
    st.session_state["worked_hours_input"] = 187.0
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
            # salary filed
            salary = st.number_input(
                "Enter Employee Salary", min_value=0, step=1, key="salary_input"
            )
            st.write("")

            # working hours filed
            worked_hours = st.number_input(
                "Enter Employee Working Hours",
                min_value=0.0,
                value=187.0,
                key="worked_hours_input",
            )
            st.write("")

        with colB:
            ##drop down for late comming
            late_opetion = st.selectbox(
                "Late Coming",
                [
                    "No Late",
                    "3 Times Late (Half Day Cut)",
                    "6 Times Late (Full Day Cut)",
                ],
                key="late_option_input",
            )

            late_comming_count = {
                "No Late": 0,
                "3 Times Late (Half Day Cut)": 3,
                "6 Times Late (Full Day Cut)": 6,
            }[late_opetion]

            st.write("")

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

        ## -------------------- Rates -------------------- ##
        hours_rate = salary / days_in_month / paid_hours_per_day
        day_salary = salary / days_in_month

        ## ----------------------------------------------- ##

        ## -------------- AUTO RESERVED HOURS ------------------##
        # Extra hours worked beyond compulsory
        reserved_hours = max(worked_hours - compulsory_hour, 0)

        # Shortage if worked hours less than compulsory
        shortage = max(compulsory_hour - worked_hours, 0)

        # Use reserved hours ONLY to fill shortage (if any)
        used_reserved = min(reserved_hours, shortage)

        final_working_hours = worked_hours + used_reserved
        remaining_reserved = reserved_hours - used_reserved

        # -------------------- Salary Deduction for Shortage --------------------#
        # If shortage remains after using reserved hours → salary cut
        uncovered_shortage = max(shortage - used_reserved, 0)
        hour_cut_amount = uncovered_shortage * hours_rate

        ## -------------------------------------------------- ##

        ## --------- Late Comming Deductions --------- ##
        late_deduction = 0
        late_text = "No Deduction"

        if late_comming_count >= 6:
            late_deduction = day_salary
            late_text = "Full day salary cut"

        elif late_comming_count >= 3:
            late_deduction = day_salary / 2
            late_text = "Half day salary cut"

        ## ----------------------------------------------- ##

        ## ---------------------- Total salary -------------------- ##
        salary_d = Decimal(str(salary))
        late_deduction_d = Decimal(str(late_deduction))
        hour_cut_d = Decimal(str(hour_cut_amount))

        total_salary = salary_d - late_deduction_d - hour_cut_d

        if total_salary < 0:
            total_salary = Decimal("0")

        total_salary = total_salary.quantize(Decimal("1"), rounding=ROUND_HALF_UP)

        ## ---------------------------------------------------------- ##

        # -------------------------
        # Centered Salary Summary
        # -------------------------

        st.markdown(
            f"<h3 style='text-align: center; color: green;'>Total Salary: ₹{total_salary:,}</h3>",
            unsafe_allow_html=True,
        )

        st.subheader("Salary Summary")
        st.write(f"💰 Total Salary: ₹{total_salary:,}")
        st.write(f"✅ **Final Working Hours:** {final_working_hours:.2f}")
        st.write(f"⏱ **Reserved Hours (Extra Worked):** {reserved_hours:.2f}")
        st.write(f"📦 **Reserved Hours Used:** {used_reserved:.2f}")
        st.write(f"📦 **Remaining Reserved Hours:** {remaining_reserved:.2f}")
        st.write(f"⏰ **Late Coming:** {late_opetion}")
        st.write(f"📉 **Late Deduction:** ₹{int(late_deduction)}")

        st.markdown("</div>", unsafe_allow_html=True)
