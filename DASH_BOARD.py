import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Dashboard de Gestión Empresarial", layout="wide")

# Función para cargar datos simulados
def cargar_datos():
    productos = pd.DataFrame({
        "id_producto": [1, 2, 3],
        "nombre_producto": ["Dr Pepper Original", "Dr Pepper Cherry", "Dr Pepper Zero Sugar"],
        "costo_producción": [0.50, 0.60, 0.55],
        "precio_unitario": [1.50, 1.70, 1.60],
        "cantidad": [200, 150, 300]
    })

    segmentos = pd.DataFrame({
        "id_segmento": [1, 2, 3],
        "nombre_segmento": ["Retail", "Food Service", "Exportaciones"],
        "total_facturado": [5000, 8000, 6000]
    })

    cuentas_por_cobrar = pd.DataFrame({
        "id_cxc": [1, 2, 3],
        "id_segmento": [1, 2, 3],
        "total_cuentas_cobrar": [50000, 30000, 20000],
        "promedio_dias_cobro": [30, 45, 60],
        "cuentas_incobrables": [2.5, 1.8, 3.0],
        "fecha_registro": [datetime(2024, 12, 1), datetime(2024, 12, 2), datetime(2024, 12, 3)]
    })

    cuentas_por_pagar = pd.DataFrame({
        "id_cxp": [1, 2, 3],
        "id_proveedor": [101, 102, 103],
        "total_cuentas_pagar": [40000, 25000, 15000],
        "promedio_dias_pago": [35, 50, 40],
        "fecha_registro": [datetime(2024, 12, 1), datetime(2024, 12, 2), datetime(2024, 12, 3)]
    })

    facturacion = pd.DataFrame({
        "id_factura": [1, 2, 3],
        "id_producto": [1, 2, 3],
        "id_segmento": [1, 2, 1],
        "cantidad_vendida": [5, 10, 3],
        "total_facturado": [250, 800, 90],
        "fecha": [datetime(2024, 12, 1), datetime(2024, 12, 2), datetime(2024, 12, 3)]
    })

    return productos, segmentos, cuentas_por_cobrar, cuentas_por_pagar, facturacion

# Carga de datos simulados
productos, segmentos, cuentas_por_cobrar, cuentas_por_pagar, facturacion = cargar_datos()

# Encabezado
st.title("Dashboard de Gestión Empresarial")
st.markdown("""
Este dashboard permite supervisar métricas clave relacionadas con la rentabilidad, la gestión del capital de trabajo y el análisis de ventas.
""")

# Sección: Métricas Clave
st.header("Métricas Clave")
col1, col2, col3 = st.columns(3)
rotacion_activos = np.mean([8.0, 10.0, 7.5])  # Rotación de inventarios ficticia
indice_liquidez = np.sum(cuentas_por_cobrar["total_cuentas_cobrar"]) / np.sum(cuentas_por_pagar["total_cuentas_pagar"])
indice_endeudamiento = np.sum(cuentas_por_pagar["total_cuentas_pagar"]) / (np.sum(cuentas_por_cobrar["total_cuentas_cobrar"]) + np.sum(cuentas_por_pagar["total_cuentas_pagar"]))

col1.metric("Rotación de Activos", f"{rotacion_activos:.2f}")
col2.metric("Índice de Liquidez", f"{indice_liquidez:.2f}")
col3.metric("Índice de Endeudamiento", f"{indice_endeudamiento:.2%}")

# Sección: Facturación Filtrada
st.subheader("Facturación Filtrada")
fecha_inicio = st.sidebar.date_input("Fecha de inicio", value=datetime(2024, 12, 1))
fecha_fin = st.sidebar.date_input("Fecha de fin", value=datetime(2024, 12, 31))

# Filtrar datos de facturación según las fechas seleccionadas
facturacion_filtrada = facturacion[
    (facturacion["fecha"] >= pd.Timestamp(fecha_inicio)) & (facturacion["fecha"] <= pd.Timestamp(fecha_fin))
]
st.dataframe(facturacion_filtrada)

# Gráfico de ventas por producto
st.subheader("Análisis de Ventas por Producto")
ventas_por_producto = facturacion.groupby("id_producto")["total_facturado"].sum().reset_index()
ventas_por_producto = ventas_por_producto.merge(productos[["id_producto", "nombre_producto"]], on="id_producto")
fig_ventas_producto = px.bar(ventas_por_producto, x="nombre_producto", y="total_facturado", title="Ventas por Producto")
st.plotly_chart(fig_ventas_producto, use_container_width=True)

# Gráfico de tendencia de ventas
st.subheader("Tendencia de Ventas")
ventas_por_fecha = facturacion.groupby(facturacion["fecha"].dt.date)["total_facturado"].sum().reset_index()
fig_tendencia = px.line(ventas_por_fecha, x="fecha", y="total_facturado", title="Tendencia de Facturación")
st.plotly_chart(fig_tendencia, use_container_width=True)

# Rentabilidad por Producto
st.subheader("Rentabilidad por Producto")
productos["margen_utilidad"] = (productos["precio_unitario"] - productos["costo_producción"]) / productos["precio_unitario"] * 100
st.dataframe(productos[["nombre_producto", "margen_utilidad"]])

# Alertas Automáticas
st.header("Alertas Automáticas")
alertas = []
if np.mean(cuentas_por_cobrar["promedio_dias_cobro"]) > 45:
    alertas.append("⚠️ El promedio de días de cobro supera el límite de 45 días.")
if rotacion_activos < 8.0:
    alertas.append("⚠️ La rotación de activos está por debajo del valor ideal.")
if np.sum(cuentas_por_cobrar["total_cuentas_cobrar"]) > np.sum(cuentas_por_pagar["total_cuentas_pagar"]):
    alertas.append("⚠️ Las cuentas por cobrar superan las cuentas por pagar.")

if alertas:
    for alerta in alertas:
        st.warning(alerta)
else:
    st.success("No hay alertas críticas en este momento.")

# Entrada de nuevos datos
st.sidebar.header("Entrada de Datos")
opcion_tabla = st.sidebar.selectbox("Selecciona la tabla para agregar datos", ["Productos", "Facturación"])

if opcion_tabla == "Productos":
    nombre = st.sidebar.text_input("Nombre del Producto")
    costo = st.sidebar.number_input("Costo de Producción", min_value=0.0, format="%.2f")
    precio = st.sidebar.number_input("Precio Unitario", min_value=0.0, format="%.2f")
    cantidad = st.sidebar.number_input("Cantidad", min_value=0, step=1)
    if st.sidebar.button("Agregar Producto"):
        nuevo_producto = pd.DataFrame({
            "id_producto": [productos["id_producto"].max() + 1],
            "nombre_producto": [nombre],
            "costo_producción": [costo],
            "precio_unitario": [precio],
            "cantidad": [cantidad]
        })
        productos = pd.concat([productos, nuevo_producto], ignore_index=True)
        st.sidebar.success("Producto agregado exitosamente.")

if opcion_tabla == "Facturación":
    st.sidebar.subheader("Registrar Facturación")
    producto_id = st.sidebar.selectbox("Selecciona Producto", productos["id_producto"])
    segmento_id = st.sidebar.selectbox("Selecciona Segmento", segmentos["id_segmento"])
    cantidad = st.sidebar.number_input("Cantidad Vendida", min_value=0, step=1)
    if st.sidebar.button("Registrar Facturación"):
        precio_unitario = productos.loc[productos["id_producto"] == producto_id, "precio_unitario"].values[0]
        total_facturado = cantidad * precio_unitario

        nuevo_registro = pd.DataFrame({
            "id_factura": [facturacion["id_factura"].max() + 1 if not facturacion.empty else 1],
            "id_producto": [producto_id],
            "id_segmento": [segmento_id],
            "cantidad_vendida": [cantidad],
            "total_facturado": [total_facturado],
            "fecha": [datetime.now()]
        })

        facturacion = pd.concat([facturacion, nuevo_registro], ignore_index=True)
        st.sidebar.success("Facturación registrada exitosamente.")
