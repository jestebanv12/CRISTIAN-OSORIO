import streamlit as st
import pandas as pd
import utilidades as util
import streamlit as st
from PIL import Image 
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt


st.set_page_config(
    page_title="TPM Equipos",
    page_icon="Logo.png",
    layout="wide"
)

def main():
    st.title("Informe de Ventas 2025")
if __name__=="__main__":
    main()



def generar_menu():
    # Agregar una imagen en la parte superior del menú (sin contorno blanco)
    st.sidebar.image("TPM.png", use_container_width=True)  

    st.sidebar.title("📌 Menú Principal")

    # Opciones del menú con emojis o iconos
    opciones = {
        "🏠 Inicio": "inicio",
        "👩‍🏭 Vendedores": "Vendedores",
        "ℹ️ Cliente": "clientes",
        "⚙️ Referencias":"Referencias",
        "💯TPM":"TPM"
    }

    # Crear botones en la barra lateral
    for nombre, clave in opciones.items():
        if st.sidebar.button(nombre):
            st.session_state["pagina"] = clave

    # Si no hay página seleccionada, establecer "inicio" por defecto
    if "pagina" not in st.session_state:
        st.session_state["pagina"] = "inicio"

    return st.session_state["pagina"]

# Uso en la aplicación
pagina = generar_menu()

if pagina == "inicio":
    @st.cache_data
    def cargar_datos():
        df = pd.read_csv("Informe ventas.csv", sep=None, engine="python")
        df.columns = df.columns.str.strip()
        return df

    df = cargar_datos()
    
    df.columns = df.columns.str.strip()

    #Convertir TOTAL V a número (por si viene como texto)
    df["TOTAL V"] = pd.to_numeric(df["TOTAL V"], errors="coerce")

    # Verificar columnas necesarias
    columnas_requeridas = {"AÑO", "MES", "DIA", "TOTAL V", "GRUPO TRES"}
    if not columnas_requeridas.issubset(df.columns):
        st.error(f"Faltan columnas requeridas: {columnas_requeridas - set(df.columns)}")
        st.stop()

    # Limpieza inicial
    df["AÑO"] = df["AÑO"].astype(int)
    df["MES"] = df["MES"].astype(str).str.upper().str.strip()

    # Segmentador de año
    años_disponibles = sorted(df["AÑO"].unique(), reverse=True)
    año_seleccionado = st.selectbox("Selecciona un año:", ["Todos"] + list(map(str, años_disponibles)))

# ---------------------
# VENTAS ANUALES
# ---------------------
    if año_seleccionado == "Todos":
        df_filtrado = df.groupby("AÑO").agg({"TOTAL V": "sum"}).reset_index()
        df_filtrado["Crecimiento (%)"] = df_filtrado["TOTAL V"].pct_change() * 100
        df_filtrado["Crecimiento (%)"] = df_filtrado["Crecimiento (%)"].round(2)
        eje_x = "AÑO"
        titulo_grafica = "Ventas Anuales con Crecimiento (%)"

        # Top 10 total
        df_top10 = df.groupby("GRUPO TRES").agg({"TOTAL V": "sum"}).reset_index()

# ---------------------
# VENTAS MENSUALES
# ---------------------
    else:
        año_int = int(año_seleccionado)
        df_año = df[df["AÑO"] == año_int].copy()

        orden_meses = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", 
                   "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
        df_año["MES"] = pd.Categorical(df_año["MES"], categories=orden_meses, ordered=True)

        df_filtrado = df_año.groupby("MES").agg({"TOTAL V": "sum"}).reset_index()
        df_filtrado["Crecimiento (%)"] = df_filtrado["TOTAL V"].pct_change() * 100
        df_filtrado["Crecimiento (%)"] = df_filtrado["Crecimiento (%)"].round(2)
        eje_x = "MES"
        titulo_grafica = f"Ventas Mensuales en {año_int} con Crecimiento (%)"

        # Top 10 de ese año
        df_top10 = df_año.groupby("GRUPO TRES").agg({"TOTAL V": "sum"}).reset_index()

# ---------------------
# GRÁFICO DE BARRAS
# ---------------------
    fig = px.bar(
        df_filtrado, 
        x=eje_x, 
        y="TOTAL V",
        text_auto="$,.0f",
        labels={"TOTAL V": "Total Ventas ($)", eje_x: eje_x},
        title=titulo_grafica,
        color="Crecimiento (%)",
        color_continuous_scale="Oranges"
    )
    fig.update_traces(textposition="outside")

    # Formato de eje X para valores enteros (cuando son años)
    if eje_x == "AÑO":
        fig.update_xaxes(tickformat="d", type="category")  # Formato entero y tratarlo como categoría

    st.plotly_chart(fig, use_container_width=True)

# ---------------------
# TOP 10 GRUPO TRES
# ---------------------
    df_top10 = df_top10.sort_values(by="TOTAL V", ascending=False).head(10)
    df_top10["TOTAL V"] = df_top10["TOTAL V"].apply(lambda x: f"${x:,.2f}")

    st.write(f"### Top 10 'GRUPO TRES' por Ventas en {año_seleccionado}")
    st.dataframe(df_top10[["GRUPO TRES", "TOTAL V"]], hide_index=True)
    
elif pagina == "Vendedores":
    st.title("👩‍🏭 Ventas por vendedor")
    @st.cache_data
    def cargar_datos():
        df = pd.read_csv("Informe ventas.csv", sep=None, engine="python")
        df.columns = df.columns.str.strip()
        df["TOTAL V"] = pd.to_numeric(df["TOTAL V"], errors="coerce")
        df["AÑO"] = pd.to_numeric(df["AÑO"], errors="coerce")
        return df

    df = cargar_datos()
    df["MES"] = df["MES"].astype(str).str.strip().str.upper()
    # Validar columnas necesarias
    columnas_requeridas = {"AÑO", "MES", "DIA", "TOTAL V", "GRUPO TRES"}
    if not columnas_requeridas.issubset(df.columns):
        st.error(f"Faltan columnas requeridas: {columnas_requeridas - set(df.columns)}")
        st.stop()

    # Filtros
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        vendedor_seleccionado = st.selectbox("Vendedor", ["Todos"] + sorted(df["VENDEDOR"].dropna().unique()))

    with col2:
        años_disponibles = sorted(df["AÑO"].dropna().unique())
        año_seleccionado = st.selectbox("Año", ["Todos"] + list(map(str, años_disponibles)))

    with col3:
        dpto_seleccionado = st.selectbox("Departamento", ["Todos"] + sorted(df["DPTO"].dropna().unique()))

    with col4:
        ciudades_disponibles = (
            df[df["DPTO"] == dpto_seleccionado]["CIUDAD"].dropna().unique().tolist()
            if dpto_seleccionado != "Todos"
            else sorted(df["CIUDAD"].dropna().unique().tolist())
        )
        ciudad_seleccionada = st.selectbox("Ciudad", ["Todos"] + sorted(ciudades_disponibles))

    df["VENDEDOR"] = df["VENDEDOR"].str.strip()
    df["AÑO"] = pd.to_numeric(df["AÑO"], errors="coerce")
    df["TOTAL V"] = pd.to_numeric(df["TOTAL V"], errors="coerce")

    
    # Aplicar filtros
    df_filtrado = df.copy()

    if vendedor_seleccionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["VENDEDOR"].str.strip() == vendedor_seleccionado.strip()]


    if año_seleccionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["AÑO"] == int(año_seleccionado)]

    if dpto_seleccionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["DPTO"] == dpto_seleccionado]

    if ciudad_seleccionada != "Todos":
        df_filtrado = df_filtrado[df_filtrado["CIUDAD"] == ciudad_seleccionada]
    
    
        
    
    else:
        # Agrupación para la gráfica
        if vendedor_seleccionado == "Todos" or año_seleccionado == "Todos":
            df_agrupado = df_filtrado.groupby("AÑO")["TOTAL V"].sum().reset_index()
            eje_x = "AÑO"
            titulo_grafica = "Ventas Totales de la Empresa" if vendedor_seleccionado == "Todos" else f"Ventas de {vendedor_seleccionado} por Año"
        else:
            orden_meses = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
            df_filtrado["MES"] = pd.Categorical(df_filtrado["MES"], categories=orden_meses, ordered=True)
            df_agrupado = df_filtrado.groupby("MES")["TOTAL V"].sum().reset_index()
            eje_x = "MES"
            titulo_grafica = f"Ventas de {vendedor_seleccionado} en {año_seleccionado}"

        # Mostrar gráfico
        # Formatear los valores como moneda
        df_agrupado["TOTAL V"] = pd.to_numeric(df_agrupado["TOTAL V"], errors="coerce")  # Asegurar que es numérico

        fig = px.bar(
            df_agrupado, 
            x=eje_x, 
            y="TOTAL V", 
            title=titulo_grafica, 
            text_auto=True
)

        # Formato de moneda en las etiquetas
        fig.update_traces(texttemplate="$%{y:,.2f} ", textposition="outside")

        # Formato de moneda en el eje Y
        fig.update_layout(yaxis_tickprefix="$", yaxis_tickformat=",", xaxis_title=eje_x, yaxis_title="Ventas ($)")
        # Corregir formato del eje X cuando se trata de años
        if eje_x == "AÑO":
            fig.update_xaxes(type="category")  # Tratar los años como categorías discretas

        st.plotly_chart(fig, use_container_width=True)

        # Tablas Top 10
        col5, col6 = st.columns(2, gap="large")

        def estilo_dataframe(df):
            return df.style.set_properties(**{
                "text-align": "left",
                "white-space": "nowrap"
            }).format({"TOTAL V": "$ {:,.2f}"})

        with col5:
            st.subheader("🏆 Top 10 por Ubicación")
            if dpto_seleccionado == "Todos":
                top = df_filtrado.groupby("DPTO")["TOTAL V"].sum().reset_index().sort_values(by="TOTAL V", ascending=False).head(10)
            else:
                top = df_filtrado.groupby("CIUDAD")["TOTAL V"].sum().reset_index().sort_values(by="TOTAL V", ascending=False).head(10)
            st.dataframe(estilo_dataframe(top), use_container_width=True, hide_index=True)

        with col6:
            st.subheader("🏆 Top 10 REFERENCIA")
            top_ref = df_filtrado.groupby("REFERENCIA")["TOTAL V"].sum().reset_index().sort_values(by="TOTAL V", ascending=False).head(10)
            st.dataframe(estilo_dataframe(top_ref.set_index("REFERENCIA")), use_container_width=True)

        st.markdown("<h3 style='text-align: center;'>🏆 Top 10 RAZON SOCIAL</h3>", unsafe_allow_html=True)
        top_razon = df_filtrado.groupby("RAZON SOCIAL")["TOTAL V"].sum().reset_index().sort_values(by="TOTAL V", ascending=False).head(10)
        st.dataframe(estilo_dataframe(top_razon.set_index("RAZON SOCIAL")), use_container_width=True)
elif pagina == "clientes":
    st.title("ℹClientes")    
    @st.cache_data
    def cargar_datos():
        df = pd.read_csv("Informe ventas.csv", sep=None, engine="python")
        df.columns = df.columns.str.strip()
        df["TOTAL V"] = pd.to_numeric(df["TOTAL V"], errors="coerce")
        df["AÑO"] = pd.to_numeric(df["AÑO"], errors="coerce")
        return df

    df = cargar_datos()
    df["MES"] = df["MES"].astype(str).str.strip().str.upper()
    # Validar columnas necesarias
    columnas_requeridas = {"AÑO", "MES", "DIA", "TOTAL V", "GRUPO TRES"}
    if not columnas_requeridas.issubset(df.columns):
        st.error(f"Faltan columnas requeridas: {columnas_requeridas - set(df.columns)}")
        st.stop()
    # Verificar que el archivo CSV tenga las columnas correctas
    columnas_requeridas = {"AÑO", "MES", "DIA", "TOTAL V", "RAZON SOCIAL", "REFERENCIA"}
    if not columnas_requeridas.issubset(set(df.columns)):
        st.error(f"El archivo CSV debe contener las columnas exactas: {columnas_requeridas}")
    else:
        st.subheader("📊 Informe de Ventas", divider="blue")
    
        col1, col2 = st.columns([2,1])
        with col1:
            razon_social_seleccionada = st.selectbox("Buscar Razón Social", [""] + sorted(df["RAZON SOCIAL"].unique()), index=0)
        with col2:
            año_seleccionado = st.selectbox("Año", ["Todos"] + sorted(df["AÑO"].unique()))
    
        # Filtrar datos según selección
        df_filtrado = df.copy()
    
        if razon_social_seleccionada:
            df_filtrado = df_filtrado[df_filtrado["RAZON SOCIAL"].str.contains(razon_social_seleccionada, case=False, na=False)]
    
        if año_seleccionado != "Todos":
            df_filtrado = df_filtrado[df_filtrado["AÑO"] == año_seleccionado]
    
        # Mostrar Top 10 de Referencias
        st.subheader("🏆 Top 10 REFERENCIA")
        df_top_referencia = df_filtrado.groupby("REFERENCIA").agg({"TOTAL V": "sum"}).reset_index().sort_values(by="TOTAL V", ascending=False).head(10)
        df_top_referencia["TOTAL V"] = df_top_referencia["TOTAL V"].apply(lambda x: f"${x:,.2f}")
        st.dataframe(df_top_referencia.set_index("REFERENCIA"), use_container_width=True)
    
        # Mostrar Gráficos si se selecciona Razón Social
    if razon_social_seleccionada:
        st.subheader("📈 Ventas de la Razón Social")

    if df_filtrado.empty:
        st.warning("No hay datos para mostrar en la gráfica.")
    else:
        if año_seleccionado == "Todos":
            df_grafico = df_filtrado.groupby("AÑO").agg({"TOTAL V": "sum"}).reset_index()
            df_grafico["AÑO"] = df_grafico["AÑO"].astype(str)
            x_axis = "AÑO"
        else:
            # Ordenar meses
            orden_meses = [
                "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
                "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"
            ]
            # Normalizar nombres de meses
            df_filtrado["MES"] = df_filtrado["MES"].str.strip().str.upper()
            df_filtrado["MES"] = pd.Categorical(df_filtrado["MES"], categories=orden_meses, ordered=True)

            df_grafico = df_filtrado.groupby("MES").agg({"TOTAL V": "sum"}).reset_index()
            x_axis = "MES"

        # Verificamos si hay datos reales para graficar
        if df_grafico["TOTAL V"].sum() == 0:
            st.warning("No hay ventas registradas para esta selección.")
        else:
            fig_bar = px.bar(
                df_grafico,
                x=x_axis,
                y="TOTAL V",
                title="Ventas por Periodo",
                text_auto=True,
                color_discrete_sequence=["yellow"]
            )
            fig_bar.update_traces(texttemplate="$%{y:,.2f}", textposition="outside")
            fig_bar.update_layout(yaxis_tickprefix="$", yaxis_tickformat=",")
          


            # Asegurar que el eje X de los años no tenga valores intermedios
        if x_axis == "AÑO":
                fig_bar.update_xaxes(type="category")  # Forzar eje X como categórico
    
                st.plotly_chart(fig_bar, use_container_width=True)
if pagina == "Referencias":
    st.title("⚙️ Referencias")
    @st.cache_data
    def cargar_datos():
        df = pd.read_csv("Informe ventas.csv", sep=None, engine="python")
        df.columns = df.columns.str.strip()
        df["TOTAL V"] = pd.to_numeric(df["TOTAL V"], errors="coerce")
        df["AÑO"] = pd.to_numeric(df["AÑO"], errors="coerce")
        return df

    df = cargar_datos()
    df["MES"] = df["MES"].astype(str).str.strip().str.upper()
    # Validar columnas necesarias
    columnas_requeridas = {"AÑO", "MES", "DIA", "TOTAL V", "RAZON SOCIAL", "REFERENCIA"}
    if not columnas_requeridas.issubset(df.columns):
        st.error(f"Faltan columnas requeridas: {columnas_requeridas - set(df.columns)}")
        st.stop()
    else:
        st.subheader("📊 Informe de Ventas", divider="blue")
    
        col1, col2, col3 = st.columns([2,2,1])
        with col1:
            referencia_seleccionada = st.selectbox("Buscar Referencia", [""] + sorted(df["REFERENCIA"].unique()), index=0)
        with col2:
            razon_social_seleccionada = st.selectbox("Buscar Razón Social", [""] + sorted(df["RAZON SOCIAL"].unique()), index=0)
        with col3:
            año_seleccionado = st.selectbox("Año", ["Todos"] + sorted(df["AÑO"].astype(int).unique()))
    
        # Filtrar datos según selección
        df_filtrado = df.copy()
    
        if referencia_seleccionada:
            df_filtrado = df_filtrado[df_filtrado["REFERENCIA"].str.contains(referencia_seleccionada, case=False, na=False)]
    
        if razon_social_seleccionada:
            df_filtrado = df_filtrado[df_filtrado["RAZON SOCIAL"].str.contains(razon_social_seleccionada, case=False, na=False)]
    
        if año_seleccionado != "Todos":
            df_filtrado = df_filtrado[df_filtrado["AÑO"].astype(int) == int(año_seleccionado)]
    
        # Si se selecciona una referencia y un año, mostrar tabla
        if referencia_seleccionada and año_seleccionado != "Todos":
            st.subheader("📊 Ventas de la Referencia en el Año")
            df_ref_año = df_filtrado.groupby(["AÑO", "MES"]).agg({"TOTAL V": "sum"}).reset_index()
            df_ref_año["TOTAL V"] = df_ref_año["TOTAL V"].apply(lambda x: f"${x:,.2f}")
            st.dataframe(df_ref_año, use_container_width=True)
    
        # Si no se selecciona referencia, mostrar Top 10
        else:
            st.subheader("🏆 Top 10 REFERENCIA")
            df_top_referencia = df_filtrado.groupby("REFERENCIA").agg({"TOTAL V": "sum"}).reset_index().sort_values(by="TOTAL V", ascending=False).head(10)
            df_top_referencia["TOTAL V"] = df_top_referencia["TOTAL V"].apply(lambda x: f"${x:,.2f}")
            st.dataframe(df_top_referencia.set_index("REFERENCIA"), use_container_width=True)
    
        # Mostrar gráficos si se selecciona Razón Social
        if razon_social_seleccionada:
            st.subheader("📊 Ventas de la Razón Social")
            df_filtrado["AÑO"] = df_filtrado["AÑO"].astype(int)
            df_grafico = df_filtrado.groupby("AÑO" if año_seleccionado == "Todos" else "MES").agg({"TOTAL V": "sum"}).reset_index()
            x_axis = "AÑO" if año_seleccionado == "Todos" else "MES"
    
            # Convert to string to treat as category
            df_grafico[x_axis] = df_grafico[x_axis].astype(str)
    
            fig = px.bar(df_grafico, x=x_axis, y="TOTAL V", color_discrete_sequence=['#6F42C1'])
    
            # Force categorical axis
            fig.update_xaxes(type='category')
    
            st.plotly_chart(fig, use_container_width=True)