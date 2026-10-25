import streamlit as st

USUARIO = "admin"
PASSWORD = "1234"

def login():

    if "login" not in st.session_state:
        st.session_state.login = False

    if st.session_state.login:
        return True

    st.title("🍪 AlfaControl")

    usuario = st.text_input(
        "Usuario"
    )

    password = st.text_input(
        "Contraseña",
        type="password"
    )

    if st.button("Ingresar"):

        if (
            usuario == USUARIO and
            password == PASSWORD
        ):

            st.session_state.login = True
            st.rerun()

        else:

            st.error(
                "Usuario o contraseña incorrectos"
            )

    return False