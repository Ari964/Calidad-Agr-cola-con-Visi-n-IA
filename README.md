# 🍎 Sistema de Control de Calidad Agrícola con Visión Artificial

Este proyecto implementa un **sistema integral de control de calidad agrícola** basado en **visión artificial**, automatización de procesos y visualización interactiva de resultados.
La arquitectura combina **n8n** como motor de workflows (backend), un **servidor Python con FastAPI** para análisis de imágenes, **Supabase** como base de datos y **Streamlit** como aplicación frontend.

---

## 📌 Objetivo del Sistema

Automatizar el **análisis de calidad de productos agrícolas** (manzana, naranja, tomate y papa) mediante:

* Detección automática de defectos
* Clasificación por tamaño
* Cálculo de score y grado de calidad
* Análisis por lote
* Generación de alertas críticas
* Persistencia de resultados
* Visualización y generación de reportes PDF

---

## 🏗️ Arquitectura General

El sistema sigue una **arquitectura desacoplada y orientada a eventos**:

```
Streamlit (Frontend)
        │
        ▼
n8n Webhook (Backend de Orquestación)
        │
        ▼
FastAPI – Visión Artificial
        │
        ▼
Procesamiento de Calidad y Lote
        │
        ▼
Supabase (Base de Datos)
        │
        ├── Alertas (Twilio)
        └── Reportes PDF
```

---

## 🧩 Componentes del Sistema

### 1️⃣ Frontend – Streamlit (`quality_control_app.py`)

Aplicación web interactiva que permite:

* Cargar imágenes de productos agrícolas
* Definir datos del lote y operador
* Disparar el análisis automático
* Visualizar resultados en tiempo real:

  * Score de calidad
  * Distribución de tamaños
  * Defectos detectados
  * Alertas
* Consultar historial almacenado en Supabase
* Generar y descargar reportes PDF
* Exportar datos en JSON y CSV

---

### 2️⃣ Backend de Orquestación – n8n

Workflow completamente automatizado que:

1. Recibe datos desde Streamlit mediante **Webhook**
2. Valida información del producto e imágenes
3. Aplica estándares de calidad según tipo de producto
4. Envía imágenes al servidor de visión artificial
5. Procesa:

   * Defectos
   * Tamaño
   * Score de calidad
6. Ejecuta análisis por lote
7. Genera alertas críticas
8. Guarda resultados en Supabase
9. Envía notificaciones SMS (Twilio)
10. Prepara datos para reportes PDF

---

### 3️⃣ Servidor de Visión Artificial – FastAPI (`computer_vision_server.py`)

Servicio independiente encargado del análisis de imágenes:

* Recepción de imágenes en formato Base64
* Preprocesamiento de imágenes
* Simulación de:

  * Detección de defectos
  * Medición de tamaño
  * Análisis de color
* Cálculo de métricas:

  * Área afectada
  * Confianza del modelo
  * Tiempo de procesamiento

> ⚠️ Nota: El modelo es **simulado**, pero la arquitectura está preparada para integrar modelos reales (YOLO, CNN, TensorFlow, PyTorch).

---

### 4️⃣ Base de Datos – Supabase

Almacena de forma persistente:

* Resultados individuales de análisis
* Información de lotes
* Defectos detectados
* Alertas generadas
* Resúmenes ejecutivos
* Fechas y métricas clave

Tabla principal: `quality_control`

---

## 🚨 Sistema de Alertas

El sistema genera alertas automáticas cuando:

* La tasa de rechazo supera el umbral definido
* Existen demasiados defectos severos
* El score promedio de calidad es bajo

Tipos de alertas:

* 🔴 Críticas
* 🟡 Medias
* 🟢 Informativas

Las alertas críticas se notifican vía **SMS (Twilio)**.

---

## 📄 Reportes

Se generan reportes en formato **PDF** que incluyen:

* Información del lote
* Métricas de calidad
* Distribución de tamaños
* Defectos detectados
* Alertas y recomendaciones
* Resumen ejecutivo

También se permite la exportación de:

* JSON (resultado completo)
* CSV (historial de calidad)

---

## ⚙️ Requisitos del Sistema

### Software

* Python 3.9+
* n8n
* Supabase
* Node.js (para n8n)

### Librerías Python

```bash
pip install fastapi uvicorn opencv-python pillow numpy tensorflow
pip install streamlit supabase plotly fpdf requests
```

---

## 🚀 Ejecución del Sistema

### 1️⃣ Iniciar servidor de Visión Artificial

```bash
python computer_vision_server.py
```

### 2️⃣ Levantar n8n

```bash
n8n start
```

Importar el workflow JSON incluido en el proyecto.

### 3️⃣ Ejecutar aplicación Streamlit

```bash
streamlit run quality_control_app.py
```

---

## 🔐 Variables de Entorno

Configurar en `Streamlit Secrets` y n8n:

* `SUPABASE_URL`
* `SUPABASE_KEY`
* `N8N_WEBHOOK_URL`
* `TWILIO_ACCOUNT_SID`
* `TWILIO_PHONE_NUMBER`

---

## 📈 Escalabilidad y Mejoras Futuras

* Integración de modelos reales de Deep Learning
* Análisis batch real con múltiples imágenes
* Segmentación avanzada de productos
* Dashboard empresarial multiusuario
* Control de roles y permisos
* Integración con sistemas ERP agrícolas

---

## 👨‍💻 Autor

Proyecto desarrollado como **sistema completo de automatización agrícola con visión artificial**, integrando backend, frontend, IA y bases de datos modernas.

---

## 📜 Licencia

Proyecto con fines **educativos y demostrativos**.
Uso libre para investigación y aprendizaje.

---

🍏 **Sistema de Control de Calidad Agrícola con Visión IA – Automatización Inteligente de la Calidad**
