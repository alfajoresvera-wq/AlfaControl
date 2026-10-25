import streamlit as st
import pandas as pd
from supabase_client import supabase
import os
import plotly.express as px

from datetime import datetime

from auth import login
import database


# LOGIN

if not login():
    st.stop()

# CONFIG

st.set_page_config(
    page_title="AlfaControl",
    page_icon="🍪",
    layout="centered"
)

# CREAR CARPETAS

os.makedirs(
    "imagenes",
    exist_ok=True
)

os.makedirs(
    "exports",
    exist_ok=True
)


# FUNCIONES

def clp(x):
    return f"${x:,.0f}".replace(",", ".")

def cargar_productos():
    respuesta = (
        supabase
        .table("productos")
        .select("*")
        .execute()
    )

    print(type(respuesta.data))
    print(respuesta.data)

    return pd.DataFrame(respuesta.data)
def cargar_ventas():
    respuesta = (
        supabase
        .table("ventas")
        .select("*")
        .execute()
    )

    return pd.DataFrame(respuesta.data)
# MENU

pagina = st.sidebar.radio(
    "Menú",
    [
        "🏠 Inicio",
        "🍪 Productos",
        "✏️ Editar",
        "🗑️ Eliminar",
        "📦 Stock",
        "💰 Ventas",
        "📊 Reportes"
    ]
)

# INICIO

if pagina == "🏠 Inicio":

    productos = cargar_productos()

    ventas = cargar_ventas()

    ganancia_total = (
        ventas["ganancia"].sum()
        if not ventas.empty
        else 0
    )

    stock_total = (
        productos["stock"].sum()
        if not productos.empty
        else 0
    )

    st.title("🍪 AlfaControl Pro")

    c1,c2 = st.columns(2)

    c1.metric(
        "Ganancia Total",
        clp(ganancia_total)
    )

    c2.metric(
        "Stock Total",
        stock_total
    )

# PRODUCTOS

elif pagina == "🍪 Productos":

    st.header("Nuevo Producto")

    nombre = st.text_input(
        "Nombre"
    )

    stock = st.number_input(
        "Stock",
        0
    )

    costo = st.number_input(
        "Costo",
        0.0
    )

    precio = st.number_input(
        "Precio Venta",
        0.0
    )

    stock_min = st.number_input(
        "Stock Mínimo",
        value=10
    )

    foto = st.file_uploader(
        "Foto",
        type=["png","jpg","jpeg"]
    )

    if st.button("Guardar"):

        ruta = ""

        if foto:

            ruta = os.path.join(
                "imagenes",
                foto.name
            )

            with open(
                ruta,
                "wb"
            ) as f:

                f.write(
                    foto.getbuffer()
                )

        supabase.table(
    "productos"
).insert(
    {
        "nombre": nombre,
        "stock": stock,
        "stock_minimo": stock_min,
        "costo": costo,
        "precio": precio,
        "foto": ruta,
        "vendidos": 0
    }
).execute()
        st.success(
            "Producto creado"
        )

# EDITAR

elif pagina == "✏️ Editar":

    productos = cargar_productos()

    if not productos.empty:

        producto = st.selectbox(
            "Producto",
            productos["nombre"]
        )

        fila = productos[
            productos["nombre"] == producto
        ].iloc[0]

        precio = st.number_input(
            "Precio",
            value=float(fila["precio"])
        )

        costo = st.number_input(
            "Costo",
            value=float(fila["costo"])
        )

        if st.button(
            "Actualizar"
        ):

            supabase.table(
                "productos"
            ).update(
                {
                    "precio": precio,
                    "costo": costo
                }
            ).eq(
                "nombre",
                producto
            ).execute()

            st.success(
                "Actualizado"
            )
# ELIMINAR

elif pagina == "🗑️ Eliminar":

    productos = cargar_productos()

    if not productos.empty:

        producto = st.selectbox(
            "Producto",
            productos["nombre"]
        )

        if st.button(
            "Eliminar Producto"
        ):

            supabase.table(
                "productos"
                ).delete().eq(
                "nombre",
                producto
            ).execute()

            conn.commit()

            st.success(
                "Producto eliminado"
            )

# STOCK

elif pagina == "📦 Stock":

    productos = cargar_productos()

    if not productos.empty:

        producto = st.selectbox(
            "Producto",
            productos["nombre"]
        )

        fila = productos[
            productos["nombre"] == producto
        ].iloc[0]

        cantidad =int( 
		st.number_input(
            		"Agregar",
            		min_value=1
        ))

        if st.button(
            "Añadir Stock"
        ):

            nuevo_stock = (
                int(fila["stock"]) + int(cantidad)
            )

            supabase.table(
                "productos"
            ).update(
                {
                    "stock": int(nuevo_stock)
                }
            ).eq(
                "id",
                int(fila["id"])
            ).execute()

            st.success(
                "Stock actualizado"
            )
# VENTAS

elif pagina == "💰 Ventas":

    productos = cargar_productos()

    if not productos.empty:

        producto = st.selectbox(
            "Producto",
            productos["nombre"]
        )

        fila = productos[
            productos["nombre"] == producto
        ].iloc[0]

        cantidad = st.number_input(
            "Cantidad",
            min_value=1
        )

        if st.button(
            "Registrar Venta"
        ):

            if cantidad > fila["stock"]:

                st.error(
                    "Stock insuficiente"
                )

            else:

                ingreso = (
                    fila["precio"]
                    * cantidad
                )

                ganancia = (
                    (
                        fila["precio"]
                        - fila["costo"]
                    )
                    * cantidad
                )
                supabase.table(
                    "productos"
                ).update(
                    {
                        "stock": int(fila["stock"]) - int(cantidad),
                        "vendidos": int(fila["vendidos"]) + int(cantidad)
                    }
                ).eq(
                    "id",
                    int(fila["id"])
                ).execute()

                supabase.table(
                    "ventas"
                ).insert(
                    {
                        "fecha": datetime.now().isoformat(),
                        "producto": str(producto),
                        "cantidad": int(cantidad),
                        "ingreso": float(ingreso),
                        "ganancia": float(ganancia)
                    }
                ).execute()

                st.success(
                    f"Ganancia {clp(ganancia)}"
                )
# REPORTES

elif pagina == "📊 Reportes":

    ventas = cargar_ventas()

    productos = cargar_productos()

    st.subheader(
        "Inventario"
    )

    st.dataframe(
        productos
    )

    st.subheader(
        "Ventas"
    )

    st.dataframe(
        ventas
    )

    if not ventas.empty:

        grafico = px.bar(
            ventas,
            x="producto",
            y="cantidad",
            color="producto"
        )

        st.plotly_chart(
            grafico,
            use_container_width=True
        )

        archivo = "exports/ventas.xlsx"

        ventas.to_excel(
            archivo,
            index=False
        )

        with open(
            archivo,
            "rb"
        ) as f:

            st.download_button(
                "📥 Descargar Excel",
                f,
                file_name="ventas.xlsx"
            )