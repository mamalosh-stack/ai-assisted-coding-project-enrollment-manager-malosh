
import streamlit as st

from enrollment_starter import (
    CURRENT_STUDENT,
    STATUS_ENROLLED,
    STATUS_UNENROLLED,
    create_tables,
    seed_sample_data,
    get_student_enrollments,
    get_student_enrollment_history,
    get_student_summary,
    enroll_with_key,
    soft_unenroll_student,
)


# ---------- Setup ----------

st.set_page_config(
    page_title="Student Enrollment Dashboard",
    page_icon="🎓",
    layout="wide",
)


def setup_database() -> None:
    """Prepare the local database for the app."""
    create_tables()
    seed_sample_data()


def initialize_session_state() -> None:
    """Initialize values needed for routing and feedback."""
    if "role" not in st.session_state:
        st.session_state.role = "student"

    if "page" not in st.session_state:
        st.session_state.page = "dashboard"

    if "selected_class" not in st.session_state:
        st.session_state.selected_class = None

    if "selected_course_id" not in st.session_state:
        st.session_state.selected_course_id = None

    if "feedback_message" not in st.session_state:
        st.session_state.feedback_message = ""

    if "feedback_type" not in st.session_state:
        st.session_state.feedback_type = ""


def show_feedback() -> None:
    """Show a short success, warning, or error message."""
    message = st.session_state.get("feedback_message", "")
    feedback_type = st.session_state.get("feedback_type", "")

    if not message:
        return

    if feedback_type == "success":
        st.success(message)
    elif feedback_type == "warning":
        st.warning(message)
    elif feedback_type == "error":
        st.error(message)
    else:
        st.info(message)

    st.session_state.feedback_message = ""
    st.session_state.feedback_type = ""


def set_feedback(message: str, feedback_type: str) -> None:
    """Store a feedback message in session state."""
    st.session_state.feedback_message = message
    st.session_state.feedback_type = feedback_type


def go_to_dashboard() -> None:
    """Navigate back to the dashboard."""
    st.session_state.page = "dashboard"
    st.session_state.selected_class = None
    st.session_state.selected_course_id = None
    st.rerun()


def go_to_class(course_record: dict) -> None:
    """Navigate to the selected class page."""
    st.session_state.selected_class = course_record
    st.session_state.selected_course_id = course_record.get("course_id")
    st.session_state.page = "class_detail"
    st.rerun()


def find_class_by_course_id(course_id: str) -> dict | None:
    """Find a class record from the student's full enrollment history."""
    history = get_student_enrollment_history(CURRENT_STUDENT["user_id"])

    for record in history:
        if record.get("course_id") == course_id:
            return record

    return None


def handle_unenroll(course_id: str) -> None:
    """Soft-unenroll the current student from a course."""
    if not course_id:
        set_feedback("Please select a class before unenrolling.", "warning")
        st.rerun()

    success = soft_unenroll_student(CURRENT_STUDENT["user_id"], course_id)

    if success:
        set_feedback(f"You have been unenrolled from {course_id}.", "success")
    else:
        set_feedback("The selected class could not be unenrolled.", "error")

    st.session_state.page = "dashboard"
    st.session_state.selected_class = None
    st.session_state.selected_course_id = None
    st.rerun()


# ---------- Page 1: Student Dashboard ----------

def show_dashboard() -> None:
    """Show the student dashboard page."""
    student = CURRENT_STUDENT
    user_id = student["user_id"]
    email = student["email"]

    st.title("Student Enrollment Dashboard")
    st.caption(f"Logged in as {student['name']} | {email}")

    show_feedback()

    summary = get_student_summary(user_id)
    enrolled_classes = get_student_enrollments(user_id)
    history = get_student_enrollment_history(user_id)

    metric_col1, metric_col2, metric_col3 = st.columns(3)
    metric_col1.metric("Total Records", summary.get("total_records", 0))
    metric_col2.metric("Currently Enrolled", summary.get(STATUS_ENROLLED, 0))
    metric_col3.metric("Unenrolled Records", summary.get(STATUS_UNENROLLED, 0))

    st.divider()

    left_col, right_col = st.columns([2, 1])

    with left_col:
        st.subheader("My Enrolled Classes")

        if enrolled_classes:
            st.dataframe(
                enrolled_classes,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.warning("You are not currently enrolled in any classes.")

        st.subheader("Class Actions")

        if enrolled_classes:
            course_options = {
                f"{record['course_id']} - {record['course_name']}": record
                for record in enrolled_classes
            }

            selected_label = st.selectbox(
                "Select a class",
                list(course_options.keys()),
            )

            selected_record = course_options[selected_label]

            action_col1, action_col2 = st.columns(2)

            with action_col1:
                if st.button("Go to Class", use_container_width=True):
                    go_to_class(selected_record)

            with action_col2:
                if st.button("Unenroll", use_container_width=True):
                    handle_unenroll(selected_record["course_id"])
        else:
            st.info("Enroll in a class first to use class actions.")

    with right_col:
        st.subheader("Join a Class")

        with st.form("enrollment_key_form"):
            enrollment_key = st.text_input(
                "Enrollment Key",
                placeholder="Example: DATA210-SPRING",
            )

            submitted = st.form_submit_button(
                "Enroll / Re-Enroll",
                use_container_width=True,
            )

        if submitted:
            clean_key = enrollment_key.strip().upper()

            if not clean_key:
                set_feedback("Please enter an enrollment key.", "warning")
                st.rerun()

            result = enroll_with_key(
                user_id=user_id,
                email=email,
                enrollment_key=clean_key,
            )

            if result:
                set_feedback(
                    f"Successfully enrolled in {result['course_id']}.",
                    "success",
                )
                go_to_class(result)
            else:
                set_feedback(
                    "Invalid enrollment key. Please check the key and try again.",
                    "error",
                )
                st.rerun()

        st.divider()

        with st.expander("Enrollment History"):
            if history:
                st.dataframe(
                    history,
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("No enrollment history found.")


# ---------- Page 2: Selected Class Page ----------

def show_class_detail() -> None:
    """Show the selected class detail page."""
    selected_course_id = st.session_state.get("selected_course_id")

    if not selected_course_id:
        set_feedback("No class was selected.", "warning")
        go_to_dashboard()

    class_record = find_class_by_course_id(selected_course_id)

    if not class_record:
        set_feedback("The selected class could not be found.", "error")
        go_to_dashboard()

    st.title(class_record["course_name"])
    st.caption(f"Course ID: {class_record['course_id']}")

    show_feedback()

    st.divider()

    detail_col1, detail_col2 = st.columns(2)

    with detail_col1:
        st.subheader("Class Information")
        st.write(f"**Course ID:** {class_record['course_id']}")
        st.write(f"**Course Name:** {class_record['course_name']}")
        st.write(f"**Instructor:** {class_record['instructor']}")

    with detail_col2:
        st.subheader("Enrollment Information")
        st.write(f"**Status:** {class_record['status']}")
        st.write(f"**Enrolled At:** {class_record['enrolled_at']}")
        st.metric("Enrollment ID", class_record["enrollment_id"])

    st.divider()

    action_col1, action_col2 = st.columns(2)

    with action_col1:
        if st.button("Back to Dashboard", use_container_width=True):
            go_to_dashboard()

    with action_col2:
        if class_record["status"] == STATUS_ENROLLED:
            if st.button("Unenroll from This Class", use_container_width=True):
                handle_unenroll(class_record["course_id"])
        else:
            st.warning("You are currently unenrolled from this class.")


# ---------- App Runner ----------

def main() -> None:
    setup_database()
    initialize_session_state()

    if st.session_state.role != "student":
        st.error("This app is only available for student users.")
        return

    if st.session_state.page == "dashboard":
        show_dashboard()
    elif st.session_state.page == "class_detail":
        show_class_detail()
    else:
        st.session_state.page = "dashboard"
        st.rerun()


if __name__ == "__main__":
    main()