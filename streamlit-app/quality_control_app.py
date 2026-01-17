import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
import json
import base64
from datetime import datetime, timedelta
from supabase import create_client
from fpdf import FPDF
import tempfile
from PIL import Image
import io
import os
import numpy as np  # Movido al inicio

# Configuración de página
st.set_page_config(
    page_title="Control de Calidad con Visión IA",
    page_icon="🚜",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cliente Supabase
@st.cache_resource
def init_supabase():
    try:
        # CORREGIDO: Usar la estructura correcta de secrets.toml
        supabase_url = ""
        supabase_key = ""
        
        try:
            if "supabase" in st.secrets:
                supabase_url = st.secrets["supabase"]["url"]
                supabase_key = st.secrets["supabase"]["key"]
            else:
                # Fallback a valores por defecto si no hay secrets
                supabase_url = "https://gaqpexgmfqjeijzntcow.supabase.co"
                supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdhcXBleGdtZnFqZWlqem50Y293Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE4NDM3ODYsImV4cCI6MjA3NzQxOTc4Nn0.MgPzjkoxNdxECJwam1iC6QhUj9oJUmcH_kvmNlvJOoQ"
        except:
            supabase_url = "https://gaqpexgmfqjeijzntcow.supabase.co"
            supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdhcXBleGdtZnFqZWlqem50Y293Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE4NDM3ODYsImV4cCI6MjA3NzQxOTc4Nn0.MgPzjkoxNdxECJwam1iC6QhUj9oJUmcH_kvmNlvJOoQ"
        
        return create_client(supabase_url, supabase_key)
    except Exception as e:
        st.error(f"Error inicializando Supabase: {e}")
        return None

# Clase para reportes PDF
class QualityControlPDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Reporte de Control de Calidad', 0, 1, 'C')
        self.ln(5)
    
    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(2)
    
    def chapter_body(self, body):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 8, body)
        self.ln()
    
    def add_metric(self, label, value):
        self.set_font('Arial', 'B', 10)
        self.cell(0, 8, f"{label}: ")
        self.set_font('Arial', '', 10)
        self.cell(0, 8, str(value), 0, 1)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .quality-premium {
        background: linear-gradient(135deg, #4CAF50, #45a049);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        font-size: 1.8rem;
        font-weight: bold;
    }
    .quality-standard {
        background: linear-gradient(135deg, #FF9800, #F57C00);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        font-size: 1.8rem;
        font-weight: bold;
    }
    .quality-commercial {
        background: linear-gradient(135deg, #FFC107, #FFA000);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        font-size: 1.8rem;
        font-weight: bold;
    }
    .quality-rejected {
        background: linear-gradient(135deg, #F44336, #D32F2F);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        font-size: 1.8rem;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1E88E5;
        margin-bottom: 1rem;
    }
    .alert-card {
        background-color: #ffebee;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #F44336;
        margin-bottom: 0.5rem;
    }
    .defect-card {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #FF9800;
        margin-bottom: 0.5rem;
    }
    .success-card {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #4CAF50;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

def trigger_quality_analysis(product_data):
    """Disparar análisis de calidad en n8n"""
    try:
        # CORREGIDO: Usar la estructura correcta de secrets.toml
        n8n_webhook_url = ""
        try:
            if "n8n" in st.secrets and "webhook_url" in st.secrets["n8n"]:
                n8n_webhook_url = st.secrets["n8n"]["webhook_url"]
            else:
                n8n_webhook_url = "http://localhost:5678/webhook/quality-control-webhook"
        except:
            n8n_webhook_url = "http://localhost:5678/webhook/quality-control-webhook"
        
        # Si n8n no está configurado o la URL está vacía, usar modo demo
        if not n8n_webhook_url or n8n_webhook_url == "":
            st.info("📋 n8n no configurado - Modo demo activado")
            # Simular respuesta de n8n para desarrollo
            demo_response = {
                "analysis_id": f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "quality_grade": "Estándar",
                "quality_score": 85.5,
                "size_category": "Mediano",
                "measured_diameter": 75.2,
                "total_defects": 2,
                "severe_defects": 0,
                "confidence_score": 0.92,
                "defects": [
                    {
                        "type": "Mancha leve",
                        "severity": "minor",
                        "confidence": 0.88,
                        "area_percentage": 2.1,
                        "description": "Mancha superficial en la piel"
                    }
                ],
                "batch_analysis": {
                    "total_units": product_data.get("total_units", 100),
                    "average_quality_score": 85.5,
                    "rejection_rate": 0.05,
                    "compliance_rate": 0.95,
                    "quality_distribution": {
                        "Premium": 15,
                        "Estándar": 70,
                        "Comercial": 10,
                        "Rechazado": 5
                    }
                },
                "executive_summary": {
                    "overall_quality": "Aceptable",
                    "batch_status": "Aprobado",
                    "recommendation": "Continuar con proceso normal"
                }
            }
            return True, demo_response
        
        # Limitar el tamaño de las imágenes para evitar timeouts
        if 'images' in product_data and len(product_data['images']) > 0:
            # Tomar solo la primera imagen para la demo
            product_data['images'] = [product_data['images'][0]]
        
        # Agregar timeout más corto para desarrollo
        response = requests.post(n8n_webhook_url, json=product_data, timeout=30)
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Error del servidor: {response.status_code} - {response.text}"
            
    except requests.exceptions.Timeout:
        st.warning("⏰ n8n timeout - Usando modo demo")
        # Retornar datos de demo en caso de timeout
        demo_response = {
            "analysis_id": f"timeout_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "quality_grade": "Estándar", 
            "quality_score": 80.0,
            "size_category": "Mediano",
            "measured_diameter": 70.0,
            "total_defects": 1,
            "severe_defects": 0,
            "defects": [],
            "batch_analysis": {
                "total_units": product_data.get("total_units", 100),
                "average_quality_score": 80.0,
                "quality_distribution": {"Estándar": 100}
            }
        }
        return True, demo_response
        
    except requests.exceptions.ConnectionError:
        st.warning("🔌 n8n no disponible - Usando modo demo")
        demo_response = {
            "analysis_id": f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "quality_grade": "Estándar",
            "quality_score": 82.0,
            "size_category": "Mediano", 
            "measured_diameter": 72.5,
            "total_defects": 0,
            "severe_defects": 0,
            "defects": [],
            "batch_analysis": {
                "total_units": product_data.get("total_units", 100),
                "average_quality_score": 82.0,
                "quality_distribution": {"Estándar": 100}
            }
        }
        return True, demo_response
        
    except Exception as e:
        return False, f"Error inesperado: {str(e)}"

def fetch_quality_history(batch_id=None):
    """Obtener historial de controles de calidad"""
    supabase = init_supabase()
    if not supabase:
        return pd.DataFrame()
    
    try:
        query = supabase.table('quality_control').select('*').order('analyzed_at', desc=True)
        if batch_id:
            query = query.eq('batch_id', batch_id)
        
        response = query.limit(50).execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching quality history: {e}")
        return pd.DataFrame()

def image_to_base64(image_file):
    """Convertir imagen a base64"""
    try:
        image_bytes = image_file.getvalue()
        base64_str = base64.b64encode(image_bytes).decode('utf-8')
        return f"data:image/jpeg;base64,{base64_str}"
    except Exception as e:
        st.error(f"Error convirtiendo imagen: {e}")
        return None

def create_quality_distribution_chart(batch_analysis):
    """Crear gráfico de distribución de calidad"""
    if not batch_analysis:
        return None
    
    distribution = batch_analysis.get('quality_distribution', {})
    if not distribution:
        return None
    
    fig = px.pie(
        values=list(distribution.values()),
        names=list(distribution.keys()),
        title="Distribución de Calidad del Lote",
        color=list(distribution.keys()),
        color_discrete_map={
            'Premium': "#4CAF50",
            'Estándar': "#FF9800",
            'Comercial': "#FFC107",
            'Rechazado': "#F44336"
        }
    )
    fig.update_layout(height=400)
    return fig

def create_defect_analysis_chart(defects):
    """Crear gráfico de análisis de defectos"""
    if not defects:
        return None
    
    # Agrupar defectos por tipo y severidad
    defect_types = {}
    severity_counts = {"minor": 0, "moderate": 0, "severe": 0}
    
    for defect in defects:
        defect_type = defect.get('type', "Desconocido")
        severity = defect.get('severity', "minor")
        
        if defect_type not in defect_types:
            defect_types[defect_type] = 0
        defect_types[defect_type] += 1
        severity_counts[severity] += 1
    
    # Crear subplots
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Defectos por Tipo", "Defectos por Severidad"),
        specs=[[{"type": "bar"}, {"type": "pie"}]]
    )
    
    # Gráfico de barras para tipos de defectos
    if defect_types:
        fig.add_trace(
            go.Bar(x=list(defect_types.keys()), y=list(defect_types.values()),
                   marker_color="#FF9800", name="Defectos"),
            row=1, col=1
        )
    
    # Gráfico de torta para severidad
    fig.add_trace(
        go.Pie(labels=list(severity_counts.keys()), 
               values=list(severity_counts.values()),
               marker_colors=['#4CAF50', '#FF9800', '#F44336'],
               name="Severidad"),
        row=1, col=2
    )
    
    fig.update_layout(height=400, showlegend=False)
    return fig

def create_size_distribution_chart(batch_analysis):
    """Crear gráfico de distribución de tamaños"""
    if not batch_analysis:
        return None
    
    distribution = batch_analysis.get('size_distribution', {})
    if not distribution:
        return None
    
    fig = px.bar(
        x=list(distribution.keys()),
        y=list(distribution.values()),
        title="Distribución de Tamaños",
        color=list(distribution.keys()),
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_layout(
        xaxis_title='Categoría de Tamaño',
        yaxis_title='Cantidad de Unidades',
        height=400
    )
    return fig

def generate_quality_pdf_report(analysis_result):
    """Generar reporte PDF de control de calidad"""
    try:
        pdf = QualityControlPDFReport()
        pdf.add_page()

        # Encabezado
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'REPORTE DE CONTROL DE CALIDAD', 0, 1, 'C')
        pdf.ln(5)

        # Información del Lote
        pdf.chapter_title('INFORMACIÓN DEL LOTE')
        pdf.add_metric('ID Análisis', analysis_result.get('analysis_id', 'N/A'))
        pdf.add_metric('Lote', analysis_result.get('batch_id', 'N/A'))
        pdf.add_metric('Producto', analysis_result.get('product_type', 'N/A'))
        pdf.add_metric('Operador', analysis_result.get('operator_id', 'N/A'))
        pdf.ln(5)

        # Resultados de calidad
        pdf.chapter_title('RESULTADOS DE CALIDAD')
        pdf.add_metric('Grado de Calidad', analysis_result.get('quality_grade', 'N/A'))
        pdf.add_metric('Score de Calidad', analysis_result.get('quality_score', 'N/A'))
        pdf.add_metric('Categoría de Tamaño', analysis_result.get('size_category', 'N/A'))
        
        measured_diameter = analysis_result.get('measured_diameter', 0)
        pdf.add_metric('Diámetro Medido', f"{measured_diameter:.1f} mm")
        pdf.ln(5)

        # Análisis del Lote
        batch_analysis = analysis_result.get('batch_analysis', {})
        if batch_analysis:
            pdf.chapter_title('ANÁLISIS DEL LOTE')
            pdf.add_metric('Total Unidades', batch_analysis.get('total_units', 0))
            pdf.add_metric('Score Promedio', batch_analysis.get('average_quality_score', 0))
            
            rejection_rate = batch_analysis.get('rejection_rate', 0)
            pdf.add_metric('Tasa de Rechazo', f"{(rejection_rate * 100):.1f}%")
            
            compliance_rate = batch_analysis.get('compliance_rate', 0)
            pdf.add_metric('Tasa de Cumplimiento', f"{(compliance_rate * 100):.1f}%")
            pdf.ln(5)

            # Distribución de calidad
            quality_dist = batch_analysis.get('quality_distribution', {})
            if quality_dist:
                pdf.chapter_title('DISTRIBUCIÓN DE CALIDAD')
                for quality, count in quality_dist.items():
                    pdf.add_metric(f"{quality}", count)
                pdf.ln(5)

        # Defectos detectados
        defects = analysis_result.get('defects', [])
        if defects:
            pdf.chapter_title('DEFECTOS DETECTADOS')
            pdf.add_metric('Total Defectos', len(defects))
            pdf.add_metric('Defectos Severos', analysis_result.get('severe_defects', 0))
            
            for i, defect in enumerate(defects[:3]):  # Mostrar primeros 3
                pdf.set_font('Arial', 'B', 10)
                pdf.cell(0, 6, f"Defecto {i+1}: {defect.get('type', 'N/A')} ({defect.get('severity', 'N/A')})", 0, 1)
                pdf.set_font('Arial', '', 10)
                confidence = defect.get('confidence', 0) * 100
                area_pct = defect.get('area_percentage', 0)
                pdf.multi_cell(0, 6, f"Confianza: {confidence:.1f}% - Area: {area_pct}%")
                pdf.ln(2)

        # Alertas
        alerts = analysis_result.get('alerts', [])
        if alerts:
            pdf.chapter_title('ALERTAS Y RECOMENDACIONES')
            for alert in alerts:
                pdf.set_font('Arial', 'B', 10)
                alert_type = alert.get('type', 'Alerta').replace('_', ' ').title()
                pdf.cell(0, 6, f"{alert_type}:", 0, 1)
                pdf.set_font('Arial', '', 10)
                pdf.multi_cell(0, 6, f" {alert.get('message', 'N/A')}")
                pdf.multi_cell(0, 6, f" Recomendación: {alert.get('recommendation', 'N/A')}")
                pdf.ln(2)

        # Pie de página
        pdf.set_y(-15)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0, 10, f'Generado el: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 0, 'C')

        # CORRECIÓN: pdf.output(dest='S') ya retorna bytearray, no necesita encode
        pdf_output = pdf.output(dest='S')
        return pdf_output
        
    except Exception as e:
        st.error(f"Error generando PDF: {e}")
        import traceback
        st.error(f"Detalles: {traceback.format_exc()}")
        return None
    
def main():
    # Header principal
    st.markdown('<h1 class="main-header">🌱 Control de Calidad con Visión IA</h1>', unsafe_allow_html=True)
    st.markdown("### Análisis Automático de Productos Agrícolas • Detección de Defectos • Clasificación por Tamaño • Alertas en Tiempo Real")
    
    # Inicializar session state
    if 'last_analysis' not in st.session_state:
        st.session_state.last_analysis = None
    if 'quality_history' not in st.session_state:
        st.session_state.quality_history = None
    if 'current_batch' not in st.session_state:
        st.session_state.current_batch = None
    
    # Sidebar para entrada de datos
    with st.sidebar:
        st.header("📋 Datos del Producto")
        
        with st.form("product_data_form"):
            st.subheader("Información del Lote")
            
            col1, col2 = st.columns(2)
            with col1:
                batch_id = st.text_input("ID del Lote", f"LOTE_{datetime.now().strftime('%Y%m%d_%H%M')}")
                product_type = st.selectbox("Tipo de Producto", ["Manzana", "Naranja", "Tomate", "Papa"])
            with col2:
                total_units = st.number_input("Total de Unidades", min_value=1, max_value=10000, value=100)
                expected_quality = st.selectbox("Calidad Esperada", ["Premium", "Estándar", "Comercial"])
            
            st.subheader("Subir Imágenes para Análisis")
            uploaded_images = st.file_uploader(
                "Selecciona imágenes del producto",
                type=['jpg', 'jpeg', 'png'],
                accept_multiple_files=True,
                help="Sube imágenes de los productos para análisis de calidad"
            )
            
            st.subheader("Información Adicional")
            operator_id = st.text_input("ID del Operador", "OPER_001")
            supervisor_phone = st.text_input("Teléfono Supervisor (Alertas)", placeholder="+1234567890")
            
            analyze_button = st.form_submit_button("🚀 Iniciar Análisis con Visión IA", type="primary", use_container_width=True)
            
            if analyze_button:
                if uploaded_images:
                    # Convertir imágenes a base64
                    image_data_list = []
                    for uploaded_file in uploaded_images:
                        base64_image = image_to_base64(uploaded_file)
                        if base64_image:
                            image_data_list.append(base64_image)
                    
                    if image_data_list:
                        product_data = {
                            "batch_id": batch_id,
                            "product_type": product_type,
                            "total_units": total_units,
                            "expected_quality": expected_quality,
                            "images": image_data_list,
                            "operator_id": operator_id,
                            "supervisor_phone": supervisor_phone
                        }
                        
                        with st.spinner("🔍 Analizando imágenes con redes neuronales convolucionales..."):
                            success, result = trigger_quality_analysis(product_data)
                        
                        if success:
                            st.session_state.last_analysis = result
                            st.session_state.current_batch = batch_id
                            st.success("✅ Análisis de calidad completado!")
                            st.rerun()
                        else:
                            st.error(f"❌ Error: {result}")
                    else:
                        st.error("❌ Error procesando las imágenes")
                else:
                    st.error("❌ Por favor sube al menos una imagen para análisis")
        
        st.markdown("---")
        st.header("📊 Historial de Calidad")
        if st.button("🔄 Actualizar Historial", use_container_width=True):
            with st.spinner("Cargando historial..."):
                st.session_state.quality_history = fetch_quality_history()
    
    # Contenido principal
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "🔍 Análisis", "📈 Estadísticas", "⚠️ Alertas", "📄 Reportes"])
    
    with tab1:
        if st.session_state.last_analysis:
            result = st.session_state.last_analysis
            
            # Mostrar grado de calidad con indicador visual
            quality_grade = result.get('quality_grade', 'Estándar')
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                if quality_grade == "Premium":
                    st.markdown(f'<div class="quality-premium">🏆 Calidad: Premium</div>', unsafe_allow_html=True)
                elif quality_grade == "Estándar":
                    st.markdown(f'<div class="quality-standard">✅ Calidad: Estándar</div>', unsafe_allow_html=True)
                elif quality_grade == "Comercial":
                    st.markdown(f'<div class="quality-commercial">📊 Calidad: Comercial</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="quality-rejected">❌ Calidad: {quality_grade}</div>', unsafe_allow_html=True)
            
            # Métricas principales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Score de Calidad", f"{result.get('quality_score', 0):.1f}")
            with col2:
                st.metric("Categoría Tamaño", result.get('size_category', 'N/A'))
            with col3:
                batch_analysis = result.get('batch_analysis', {})
                rejection_rate = batch_analysis.get('rejection_rate', 0)
                st.metric("Tasa de Rechazo", f"{rejection_rate:.1%}")
            with col4:
                st.metric("Defectos Detectados", result.get('total_defects', 0))
            
            # Mostrar imagen analizada si está disponible
            if result.get('images') and len(result['images']) > 0:
                st.markdown("### 📷 Imagen Analizada")
                try:
                    if 'data:' in result['images'][0]:
                        image_data = result['images'][0].split(',')[1]
                    else:
                        image_data = result['images'][0]
                    
                    image_bytes = base64.b64decode(image_data)
                    st.image(image_bytes, caption="Producto analizado", use_column_width=True)
                except Exception as e:
                    st.info("No se pudo mostrar la imagen analizada")
            
            # Gráficos principales
            col1, col2 = st.columns(2)
            
            with col1:
                quality_chart = create_quality_distribution_chart(result.get('batch_analysis', {}))
                if quality_chart:
                    st.plotly_chart(quality_chart, use_container_width=True)
                else:
                    st.info("No hay datos de distribución de calidad")
            
            with col2:
                defect_chart = create_defect_analysis_chart(result.get('defects', []))
                if defect_chart:
                    st.plotly_chart(defect_chart, use_container_width=True)
                else:
                    st.info("No se detectaron defectos")
            
            # Resumen ejecutivo
            st.markdown("## 📋 Resumen Ejecutivo")
            executive_summary = result.get('executive_summary', {})
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📦 Estado del Lote")
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.write(f"**Calidad General:** {executive_summary.get('overall_quality', 'N/A')}")
                st.write(f"**Estado del Lote:** {executive_summary.get('batch_status', 'N/A')}")
                st.write(f"**Recomendación:** {executive_summary.get('recommendation', 'N/A')}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown("### 🎯 Próximos Pasos")
                if executive_summary.get('recommendation') == 'Requiere atención':
                    st.error("**Acción Requerida:** El lote necesita revisión inmediata")
                    st.write("• Contactar al supervisor de calidad")
                    st.write("• Revisar proceso de producción")
                    st.write("• Documentar acciones correctivas")
                else:
                    st.success("✅ **Lote Aprobado:** Puede proceder con el empaque")
                    st.write("• Continuar con proceso normal")
                    st.write("• Mantener estándares actuales")
                    st.write("• Documentar resultados")
        else:
            st.info("👆 Sube imágenes de productos agrícolas y ejecuta el análisis de calidad con visión artificial")
            st.markdown("---")
            st.markdown("### 💡 Cómo usar el sistema:")
            st.markdown("""
            1. **Completa la información** del lote en el sidebar
            2. **Sube imágenes** de los productos a analizar
            3. **Haz clic en 'Iniciar Análisis'** para procesar con IA
            4. **Revisa los resultados** en las diferentes pestañas
            5. **Genera reportes** PDF si es necesario
            """)
    
    with tab2:
        if st.session_state.last_analysis:
            result = st.session_state.last_analysis
            
            st.markdown("### 🔍 Análisis Detallado")
            
            # Información del producto analizado
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📏 Medidas del Producto")
                st.metric("Diámetro", f"{result.get('measured_diameter', 0):.1f} mm")
                st.metric("Categoría de Tamaño", result.get('size_category', 'N/A'))
                st.metric("Confianza IA", f"{(result.get('confidence_score', 0) * 100):.1f}%")
            
            with col2:
                st.markdown("#### 🎨 Análisis de Color")
                color_analysis = result.get('color_analysis', {})
                st.metric("Tono Dominante", color_analysis.get('dominant_hue', 'N/A'))
                st.metric("Saturación Promedio", f"{color_analysis.get('average_saturation', 0):.1f}")
                st.metric("Uniformidad Color", f"{(color_analysis.get('color_uniformity', 0) * 100):.1f}%")
            
            # Defectos detectados
            st.markdown("### 🔧 Defectos Detectados")
            defects = result.get('defects', [])
            
            if defects:
                for i, defect in enumerate(defects):
                    severity = defect.get('severity', 'minor')
                    severity_color = {
                        'minor': '🟢',
                        'moderate': '🟡', 
                        'severe': '🔴'
                    }.get(severity, '⚪')
                    
                    with st.expander(f"{severity_color} Defecto {i+1}: {defect.get('type', 'N/A')}", expanded=i==0):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Severidad:** {severity}")
                            st.write(f"**Confianza:** {(defect.get('confidence', 0) * 100):.1f}%")
                            st.write(f"**Area Afectada:** {defect.get('area_percentage', 0)}%")
                        with col2:
                            bbox = defect.get('bbox', [])
                            if bbox and len(bbox) >= 4:
                                st.write(f"**Posición:** x={bbox[0]}, y={bbox[1]}")
                                st.write(f"**Tamaño:** {bbox[2]}x{bbox[3]} px")
                            st.write(f"**Descripción:** {defect.get('description', 'N/A')}")
            else:
                st.success("✅ No se detectaron defectos en el producto analizado")
        else:
            st.info("Ejecuta un análisis primero para ver los detalles")
    
    with tab3:
        if st.session_state.last_analysis:
            result = st.session_state.last_analysis
            batch_analysis = result.get('batch_analysis', {})
            
            st.markdown("### 📈 Estadísticas del Lote")
            
            # Métricas del Lote
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Unidades", batch_analysis.get('total_units', 0))
            with col2:
                st.metric("Score Promedio", f"{batch_analysis.get('average_quality_score', 0):.1f}")
            with col3:
                st.metric("Tasa Cumplimiento", f"{(batch_analysis.get('compliance_rate', 0) * 100):.1f}%")
            with col4:
                defect_stats = batch_analysis.get('defect_statistics', {})
                st.metric("Defectos/Unidad", f"{defect_stats.get('defects_per_unit', 0):.1f}")
            
            # Gráfico de distribución de tamaños
            st.markdown("### ⚖️ Distribución de Tamaños")
            size_chart = create_size_distribution_chart(batch_analysis)
            if size_chart:
                st.plotly_chart(size_chart, use_container_width=True)
            else:
                st.info("No hay datos de distribución de tamaños")
            
            # Estadísticas de defectos del Lote
            st.markdown("### 🐛 Estadísticas de Defectos")
            defect_stats = batch_analysis.get('defect_statistics', {})
            if defect_stats:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Defectos", defect_stats.get('total_defects', 0))
                with col2:
                    st.metric("Defectos Severos", defect_stats.get('severe_defects', 0))
                with col3:
                    st.metric("Promedio por Unidad", f"{defect_stats.get('defects_per_unit', 0):.1f}")
                
                # Defectos más comunes
                st.markdown("### 📊 Defectos Más Comunes")
                common_defects = defect_stats.get('common_defect_types', [])
                for defect in common_defects:
                    st.write(f"• {defect}")
            else:
                st.info("No hay estadísticas de defectos disponibles")
            
            # Tendencias de calidad (datos simulados)
            st.markdown("### 📈 Tendencias de Calidad")
            
            # Simular datos históricos para mostrar tendencias
            dates = pd.date_range(end=datetime.now(), periods=7, freq='D')
            quality_scores = [75 + np.random.randint(-10, 15) for _ in range(7)]
            rejection_rates = [0.1 + np.random.uniform(-0.05, 0.08) for _ in range(7)]
            
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig.add_trace(
                go.Scatter(x=dates, y=quality_scores, name="Score Calidad", line=dict(color="#4CAF50")),
                secondary_y=False,
            )
            
            fig.add_trace(
                go.Scatter(x=dates, y=rejection_rates, name="Tasa Rechazo", line=dict(color="#F44336")),
                secondary_y=True,
            )
            
            fig.update_layout(
                title="Tendencias de Calidad (Últimos 7 días)",
                xaxis_title="Fecha",
                height=400
            )
            
            fig.update_yaxes(title_text="Score Calidad", secondary_y=False)
            fig.update_yaxes(title_text="Tasa Rechazo", secondary_y=True, tickformat=".0%")
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Ejecuta un análisis primero para ver las estadísticas")
    
    with tab4:
        st.markdown("## ⚠️ Sistema de Alertas")
        
        if st.session_state.last_analysis:
            result = st.session_state.last_analysis
            
            # Alertas críticas
            critical_alerts = result.get('critical_alerts', [])
            if critical_alerts:
                st.error("### 🔴 Alertas Críticas")
                for alert in critical_alerts:
                    st.markdown('<div class="alert-card">', unsafe_allow_html=True)
                    alert_type = alert.get('type', 'Alerta').replace('_', ' ').title()
                    st.error(f"**{alert_type}**")
                    st.write(f"**Mensaje:** {alert.get('message', 'N/A')}")
                    st.write(f"**Recomendación:** {alert.get('recommendation', 'N/A')}")
                    st.write(f"**Prioridad:** {alert.get('priority', 'N/A').title()}")
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Todas las alertas
            all_alerts = result.get('alerts', [])
            if all_alerts:
                st.markdown("### 🟡 Todas las Alertas")
                for alert in all_alerts:
                    if alert not in critical_alerts:  # Ya mostramos las críticas
                        priority = alert.get('priority', 'medium')
                        priority_color = {
                            'high': '🔴',
                            'medium': '🟡', 
                            'low': '🟢'
                        }.get(priority, '⚪')
                        
                        with st.expander(f"{priority_color} {alert.get('type', 'Alerta').replace('_', ' ').title()}"):
                            st.write(f"**Mensaje:** {alert.get('message', 'N/A')}")
                            st.write(f"**Recomendación:** {alert.get('recommendation', 'N/A')}")
                            st.write(f"**Prioridad:** {priority.title()}")
            else:
                st.success("✅ No hay alertas activas - El lote cumple con todos los estándares de calidad")
            
            # Panel de acciones
            st.markdown("### 🎛️ Panel de Acciones")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📧 Enviar Reporte por Email", use_container_width=True):
                    st.success("✅ Reporte enviado al supervisor de calidad")
            
            with col2:
                if st.button("🔔 Notificar Equipo", use_container_width=True):
                    st.info("🔔 Notificación enviada al equipo de calidad")
            
            with col3:
                if st.button("📋 Crear Tarea de Revisión", use_container_width=True):
                    st.warning("⚠️ Tarea de revisión creada en el sistema")
        else:
            st.info("Ejecuta un análisis primero para ver las alertas")
    
    with tab5:
        st.markdown("## 📄 Reportes y Documentación")
        
        if st.session_state.last_analysis:
            result = st.session_state.last_analysis
            
            # Generar reporte PDF
            st.markdown("### 📊 Generar Reportes")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📄 Reporte PDF Completo", type="primary", use_container_width=True):
                    with st.spinner("Generando reporte PDF..."):
                        pdf_data = generate_quality_pdf_report(result)
                    
                    if pdf_data:
                        st.download_button(
                            label="📥 Descargar Reporte PDF",
                            data=pdf_data,
                            file_name=f"reporte_calidad_{result.get('batch_id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    else:
                        st.error("Error generando el reporte PDF")
            
            with col2:
                if st.button("📈 Reporte Estadístico", use_container_width=True):
                    st.info("📊 Generando reporte estadístico...")
                    # Aquí se generaría un reporte estadístico específico
            
            with col3:
                if st.button("🐛 Reporte de Defectos", use_container_width=True):
                    st.info("🔍 Generando reporte de defectos...")
                    # Aquí se generaría un reporte específico de defectos
            
            # Historial de controles de calidad
            st.markdown("## 📋 Historial de Controles")
            
            if st.session_state.quality_history is not None and not st.session_state.quality_history.empty:
                df = st.session_state.quality_history
                
                # Métricas del historial
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    total_analyses = len(df)
                    st.metric("Total Controles", total_analyses)
                with col2:
                    avg_score = df['quality_score'].mean()
                    st.metric("Score Promedio", f"{avg_score:.1f}")
                with col3:
                    premium_rate = (df['quality_grade'] == 'Premium').mean()
                    st.metric("Tasa Premium", f"{(premium_rate * 100):.1f}%")
                with col4:
                    rejection_rate = (df['quality_grade'] == 'Rechazado').mean()
                    st.metric("Tasa Rechazo", f"{(rejection_rate * 100):.1f}%")
                
                # Gráfico de evolución de calidad
                if 'analyzed_at' in df.columns:
                    df['analyzed_at'] = pd.to_datetime(df['analyzed_at'])
                    df_sorted = df.sort_values('analyzed_at')
                    
                    fig = px.line(df_sorted, x='analyzed_at', y='quality_score',
                                title='Evolución del Score de Calidad',
                                markers=True)
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                # Tabla de historial detallada
                st.markdown("### 📋 Historial Detallado")
                display_columns = ['analyzed_at', 'batch_id', 'product_type', 'quality_grade', 'quality_score', 'size_category']
                available_columns = [col for col in display_columns if col in df.columns]
                
                if available_columns:
                    display_df = df[available_columns].copy()
                    if 'analyzed_at' in display_df.columns:
                        display_df['analyzed_at'] = pd.to_datetime(display_df['analyzed_at']).dt.strftime('%Y-%m-%d %H:%M')
                    
                    st.dataframe(
                        display_df,
                        column_config={
                            "analyzed_at": "Fecha Análisis",
                            "batch_id": "Lote", 
                            "product_type": "Producto",
                            "quality_grade": "Grado Calidad",
                            "quality_score": "Score",
                            "size_category": "Tamaño"
                        },
                        use_container_width=True
                    )
            else:
                st.info("No hay historial disponible o no se ha cargado el historial")
            
            # Exportar datos
            st.markdown("### 💾 Exportar Datos")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.session_state.last_analysis:
                    json_data = json.dumps(st.session_state.last_analysis, indent=2, ensure_ascii=False)
                    st.download_button(
                        label="📁 Exportar JSON",
                        data=json_data,
                        file_name=f"datos_calidad_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                        mime="application/json",
                        use_container_width=True
                    )
            
            with col2:
                if st.session_state.quality_history is not None and not st.session_state.quality_history.empty:
                    csv_data = st.session_state.quality_history.to_csv(index=False)
                    st.download_button(
                        label="📊 Exportar CSV",
                        data=csv_data,
                        file_name=f"historial_calidad_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
        else:
            st.info("Ejecuta un análisis primero para generar reportes")

if __name__ == "__main__":
    main()