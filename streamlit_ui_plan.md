
# Streamlit UI Plan - Student Enrollment App

## Purpose

This plan describes the Streamlit UI for the Module 8 Session 2 student enrollment app. The goal is to build a student-facing two-page app that connects to the Session 1 backend. The UI should let a simulated logged-in student view enrolled classes, enter an enrollment key, go to a selected class page, and soft-unenroll from a class.

The UI should act as the presentation layer. It should call the existing backend/service functions and should not place SQL directly inside the Streamlit file.

---

## Simulated User

The app assumes the user is already logged in.

Simulated/current student:

- Name: Maya Patel
- User ID: u100
- Email: maya.patel@example.edu
- Role: student

The app should not create login, registration, password handling, account creation, or a new authentication system.

---

## Files

### New UI File

- `streamlit_app.py`
- Layer: UI / presentation layer
- Purpose: Handles Streamlit layout, routing, session state, buttons, forms, feedback messages, and page display.

### Existing Backend File

- `enrollment_starter.py`
- Layer: backend/service/database layer
- Purpose: Provides the existing student enrollment behavior, database setup, enrollment key handling, student summary, and soft-unenrollment functions.

The UI should import and use existing backend functions instead of rewriting database logic.

---

## Backend Functions the UI Should Use

The Streamlit UI should use backend functions such as:

- `create_tables()`
- `seed_sample_data()`
- `get_student_enrollments(user_id)`
- `get_student_enrollment_history(user_id)`
- `get_student_summary(user_id)`
- `enroll_with_key(user_id, email, enrollment_key)`
- `soft_unenroll_student(user_id, course_id)`

The UI should avoid writing direct SQL. SQL should remain in the backend/database layer.

---

## Session State Plan

The app should use `st.session_state` to manage routing, role checking, selected class information, and feedback messages.

Suggested session state values:

| Session State Key | Purpose |
|---|---|
| `role` | Stores the current user's role, which should be `"student"` |
| `page` | Stores the current page, either `"dashboard"` or `"class_detail"` |
| `selected_class` | Stores the selected class/course record |
| `selected_course_id` | Stores the selected course ID |
| `feedback_message` | Stores a short message after an action |
| `feedback_type` | Stores the type of message, such as success, warning, or error |

The app should start on the dashboard page. When a student clicks **Go to Class** or successfully enrolls in a class, the app should update `st.session_state` and navigate to the selected class page.

---

## Routing Plan

The app should have two pages:

1. Student Dashboard
2. Selected Class Page

Routing should be handled with `st.session_state["page"]`.

Suggested page values:

- `"dashboard"`
- `"class_detail"`

The app should not use a complex routing system. It can use simple conditional logic based on `st.session_state["page"]`.

---

## Role Check

The app should check that the current simulated user has the student role.

If `st.session_state["role"]` is not `"student"`, the app should show an error message and stop the student dashboard from displaying.

Because this session assumes the student is already logged in, the role check should be simple and should not become a login system.

---

## Page 1: Student Dashboard

The dashboard should be the main page students see when they open the app.

### Dashboard Goals

The student should be able to:

- See their name and email
- View summary metrics
- See currently enrolled classes
- Enter an enrollment key
- Enroll or re-enroll in a class
- Select a class
- Go to a selected class page
- Soft-unenroll from a class

### Streamlit Elements

The dashboard should use:

- `st.title` for the dashboard title
- `st.caption` for the student information
- `st.metric` for summary counts
- `st.columns` for organizing layout
- `st.divider` for separating sections
- `st.dataframe` to show enrolled classes and enrollment history
- `st.form` for enrollment key entry
- `st.text_input` for the enrollment key
- `st.form_submit_button` for submitting the key
- `st.selectbox` for selecting a class
- `st.button` for Go to Class and Unenroll
- `st.success`, `st.warning`, and `st.error` for feedback messages

### Dashboard Layout

The dashboard should include:

1. A page title: Student Enrollment Dashboard
2. A caption showing the simulated student name and email
3. Summary metrics:
   - Total records
   - Currently enrolled records
   - Unenrolled records
4. A table or dataframe of currently enrolled classes
5. A form to enter an enrollment key
6. A class action section with:
   - Select class
   - Go to Class button
   - Unenroll button
7. An optional enrollment history section

---

## Enrollment Key Behavior

The student should enter an enrollment key into a text input.

Valid example:

```text
DATA210-SPRING