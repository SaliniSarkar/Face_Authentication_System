import streamlit as st
from PIL import Image

from database import (
    create_tables,
    register_user,
    get_users,
    save_login,
    save_logout,
    has_active_login,
    get_attendance,
    get_user_count,
)
from face_utils import (
    create_face_encoding,
    recognize_face,
    find_duplicate_face,
)
from validators import validate_registration


st.set_page_config(
    page_title="Face Authentication System",
    page_icon="👤",
    layout="wide",
)

create_tables()

st.title("👤 Face Authentication & Attendance System")
st.caption("Register with your face, then use face matching to login/logout.")

menu = st.sidebar.radio(
    "Menu",
    ["Register", "Login", "Logout", "Attendance Dashboard"],
)

st.sidebar.metric("Registered Users", get_user_count())


def load_camera_image(key):
    image_file = st.camera_input("Take a photo", key=key)
    if image_file is None:
        return None
    try:
        return Image.open(image_file).convert("RGB")
    except Exception as exc:
        st.error(f"Could not read the image: {exc}")
        return None


if menu == "Register":
    st.header("📝 Register New User")

    name = st.text_input("Full Name")
    email = st.text_input("Email")
    employee_id = st.text_input("Employee ID")

    image = load_camera_image("register_camera")

    if image is not None:
        st.image(image, caption="Registration photo", width=300)

        if st.button("Register User", type="primary"):
            error = validate_registration(name, email, employee_id)
            if error:
                st.error(error)
                st.stop()

            with st.spinner("Creating face encoding..."):
                try:
                    encoding = create_face_encoding(image)
                except Exception as exc:
                    st.error(f"Face processing failed: {exc}")
                    st.stop()

            if encoding is None:
                st.error("No face was detected. Please take another photo.")
                st.stop()

            if isinstance(encoding, str) and encoding == "multiple":
                st.error("Multiple faces detected. Only one face is allowed.")
                st.stop()

            users = get_users()

            duplicate = find_duplicate_face(
                encoding,
                users,
                tolerance=0.5,
            )

            if duplicate:
                st.error("This face is already registered.")
                st.info(
                    f"Existing account: {duplicate['name']} "
                    f"(Employee ID: {duplicate['employee_id']})"
                )
                st.stop()

            try:
                register_user(
                    name=name.strip(),
                    email=email.strip(),
                    employee_id=employee_id.strip(),
                    face_encoding=encoding,
                )
                st.success(
                    f"Registration successful. Welcome, {name.strip()}!"
                )
            except Exception as exc:
                st.error(f"Registration failed: {exc}")


elif menu == "Login":
    st.header("🔐 Face Login")
    image = load_camera_image("login_camera")

    if image is not None:
        st.image(image, caption="Login photo", width=300)

        if st.button("Recognize & Login", type="primary"):
            users = get_users()

            if not users:
                st.warning("No registered users exist.")
                st.stop()

            with st.spinner("Matching face..."):
                try:
                    result = recognize_face(
                        image,
                        users,
                        tolerance=0.5,
                    )
                except Exception as exc:
                    st.error(f"Face recognition failed: {exc}")
                    st.stop()

            if result == "multiple":
                st.error("Multiple faces detected. Please show only your face.")
            elif result is None:
                st.error("Face not recognized.")
            else:
                st.success(f"Face matched: {result['name']}")
                st.write(f"**Employee ID:** {result['employee_id']}")
                st.write(f"**Email:** {result['email']}")
                st.write(f"**Face distance:** {result['distance']:.4f}")

                if has_active_login(result["id"]):
                    st.warning("You are already logged in.")
                else:
                    if save_login(result["id"]):
                        st.success("Login time saved successfully.")
                    else:
                        st.error("Could not save login time.")


elif menu == "Logout":
    st.header("🚪 Face Logout")
    image = load_camera_image("logout_camera")

    if image is not None:
        st.image(image, caption="Logout photo", width=300)

        if st.button("Recognize & Logout", type="primary"):
            users = get_users()

            if not users:
                st.warning("No registered users exist.")
                st.stop()

            with st.spinner("Matching face..."):
                try:
                    result = recognize_face(
                        image,
                        users,
                        tolerance=0.5,
                    )
                except Exception as exc:
                    st.error(f"Face recognition failed: {exc}")
                    st.stop()

            if result == "multiple":
                st.error("Multiple faces detected. Please show only your face.")
            elif result is None:
                st.error("Face not recognized.")
            else:
                st.success(f"Face matched: {result['name']}")
                st.write(f"**Employee ID:** {result['employee_id']}")
                st.write(f"**Face distance:** {result['distance']:.4f}")

                if not has_active_login(result["id"]):
                    st.warning("This user does not have an active login.")
                elif save_logout(result["id"]):
                    st.success("Logout time saved successfully.")
                else:
                    st.error("Could not save logout time.")


elif menu == "Attendance Dashboard":
    st.header("📊 Attendance Dashboard")

    df = get_attendance()

    if df.empty:
        st.info("No attendance records yet.")
    else:
        total = len(df)
        active = int(df["Logout_Time"].isna().sum())
        completed = int(df["Logout_Time"].notna().sum())

        c1, c2, c3 = st.columns(3)
        c1.metric("Attendance Records", total)
        c2.metric("Currently Logged In", active)
        c3.metric("Completed Sessions", completed)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )
