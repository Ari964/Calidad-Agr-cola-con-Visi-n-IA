from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Dict, List, Optional
import numpy as np
import cv2
import base64
from io import BytesIO
from PIL import Image
import uvicorn
import json
from datetime import datetime

app = FastAPI(
    title="Agricultural Computer Vision API",
    description="API para análisis de calidad de productos agrícolas usando visión artificial",
    version="1.0.0"
)

class ImageAnalysisRequest(BaseModel):
    image_data: str  # base64
    product_type: str
    analysis_id: str

class ImageAnalysisResponse(BaseModel):
    analysis_id: str
    defects: List[Dict]
    size_measurements: Dict
    color_analysis: Dict
    confidence_score: float
    processing_time: float
    total_area: float

# Simulador de modelo de visión artificial
class AgriculturalVisionAI:
    def __init__(self):
        self.defect_categories = {
            'Manzana': ['Punto Negro', 'Golpe', 'Podredumbre', 'Corte', 'Mancha'],
            'Naranja': ['Mancha', 'Piel Dañada', 'Podredumbre', 'Golpe'],
            'Tomate': ['Rajadura', 'Golpe', 'Podredumbre', 'Mancha'],
            'Papa': ['Ojo Profundo', 'Verde', 'Daño Mecánico', 'Mancha']
        }
        
        # Simular umbrales de confianza por tipo de defecto
        self.defect_confidence_thresholds = {
            'Punto Negro': 0.7,
            'Golpe': 0.75,
            'Podredumbre': 0.8,
            'Corte': 0.85,
            'Mancha': 0.7,
            'Piel Dañada': 0.75,
            'Rajadura': 0.8,
            'Ojo Profundo': 0.7,
            'Verde': 0.85,
            'Daño Mecánico': 0.8,
            'Defecto General': 0.6
        }

    def preprocess_image(self, image_data: str) -> np.ndarray:
        """Preprocesar imagen base64 para análisis"""
        try:
            # Decodificar base64
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
            
            # Convertir a numpy array
            img_array = np.array(image)
            
            # Convertir BGR a RGB si es necesario
            if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            return img_array
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error procesando imagen: {str(e)}")

    def simulate_defect_detection(self, image: np.ndarray, product_type: str) -> List[Dict]:
        """Simular detección de defectos basada en características de la imagen"""
        possible_defects = self.defect_categories.get(product_type, ['Defecto General'])
        
        # Simular detección basada en características de la imagen
        height, width = image.shape[:2]
        
        # Número de defectos basado en complejidad de la imagen
        if len(image.shape) == 3:
            # Imagen a color - analizar variaciones
            std_dev = np.std(image)
            num_defects = min(5, max(0, int(std_dev / 10)))  # 0-5 defectos basado en variación
        else:
            # Imagen escala de grises
            num_defects = np.random.randint(0, 3)
        
        defects = []
        for i in range(num_defects):
            defect_type = np.random.choice(possible_defects)
            
            # Simular coordenadas de bounding box (evitar bordes)
            margin = 50
            x = np.random.randint(margin, width - margin - 50)
            y = np.random.randint(margin, height - margin - 50)
            w = np.random.randint(20, min(100, width - x - 10))
            h = np.random.randint(20, min(100, height - y - 10))
            
            # Calcular área
            area = w * h
            total_area = width * height
            area_percentage = (area / total_area) * 100
            
            # Confianza basada en tipo de defecto
            base_confidence = self.defect_confidence_thresholds.get(defect_type, 0.7)
            confidence = np.random.uniform(base_confidence, 0.95)
            
            # Severidad basada en área y tipo
            if area_percentage > 5 or defect_type in ['Podredumbre', 'Daño Severo']:
                severity = 'severe'
            elif area_percentage > 2:
                severity = 'moderate'
            else:
                severity = 'minor'
            
            defects.append({
                'type': defect_type,
                'bbox': [int(x), int(y), int(w), int(h)],
                'area': int(area),
                'confidence': float(confidence),
                'severity': severity,
                'description': f'{defect_type} detectado en posición ({x},{y}) con área {area_percentage:.1f}%'
            })
        
        return defects

    def measure_size(self, image: np.ndarray) -> Dict:
        """Medir tamaño del producto en la imagen"""
        height, width = image.shape[:2]
        
        # Simular detección del producto (en producción usaría segmentación)
        # Asumimos que el producto ocupa aproximadamente el 60-80% del área
        product_ratio = np.random.uniform(0.6, 0.8)
        diameter_pixels = min(height, width) * product_ratio
        
        # Convertir a mm (factores de conversión por tipo de producto)
        conversion_factors = {
            'Manzana': 0.15,  # mm por pixel
            'Naranja': 0.18,
            'Tomate': 0.12,
            'Papa': 0.20
        }
        
        # Factor de conversión simulado
        pixel_to_mm = conversion_factors.get('Manzana', 0.15)
        diameter_mm = diameter_pixels * pixel_to_mm
        
        return {
            'diameter_pixels': float(diameter_pixels),
            'diameter_mm': float(diameter_mm),
            'width_pixels': int(width),
            'height_pixels': int(height),
            'total_area_pixels': int(height * width),
            'product_area_ratio': float(product_ratio)
        }

    def analyze_color(self, image: np.ndarray) -> Dict:
        """Analizar distribución de colores del producto"""
        if len(image.shape) != 3:
            # Imagen en escala de grises
            return {
                'dominant_hue': 0,
                'average_saturation': 0,
                'average_value': float(np.mean(image)),
                'color_uniformity': 0.8,
                'color_variance': float(np.var(image)),
                'is_grayscale': True
            }
        
        try:
            # Convertir a HSV para mejor análisis de color
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Calcular histogramas
            h_hist = cv2.calcHist([hsv], [0], None, [180], [0, 180])
            s_hist = cv2.calcHist([hsv], [1], None, [256], [0, 256])
            v_hist = cv2.calcHist([hsv], [2], None, [256], [0, 256])
            
            # Encontrar colores dominantes
            dominant_hue = int(np.argmax(h_hist))
            avg_saturation = float(np.mean(s_hist))
            avg_value = float(np.mean(v_hist))
            
            # Calcular uniformidad del color (inversa de la varianza)
            hue_variance = float(np.var(h_hist))
            color_uniformity = max(0.1, 1.0 - (hue_variance / 1000))
            
            # Determinar madurez basada en color (simulación)
            if dominant_hue < 30:  # Rojos/Naranjas
                maturity = "Maduro"
            elif dominant_hue < 90:  # Verdes
                maturity = "Inmaduro"
            else:
                maturity = "Variable"
            
            return {
                'dominant_hue': dominant_hue,
                'average_saturation': avg_saturation,
                'average_value': avg_value,
                'color_uniformity': float(color_uniformity),
                'color_variance': float(hue_variance),
                'maturity_indicator': maturity,
                'is_grayscale': False
            }
        except Exception as e:
            # Fallback si hay error en el análisis de color
            return {
                'dominant_hue': 0,
                'average_saturation': 0,
                'average_value': float(np.mean(image)),
                'color_uniformity': 0.7,
                'color_variance': 0,
                'maturity_indicator': 'No determinado',
                'is_grayscale': True
            }

    def analyze_texture(self, image: np.ndarray) -> Dict:
        """Analizar textura del producto (simulación)"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Calcular características de textura simples
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Simular análisis de textura
        if laplacian_var < 100:
            texture = "Lisa"
        elif laplacian_var < 500:
            texture = "Media"
        else:
            texture = "Rugosa"
        
        return {
            'texture_type': texture,
            'smoothness_score': max(0.1, min(1.0, 1.0 - (laplacian_var / 1000))),
            'laplacian_variance': float(laplacian_var)
        }

    def analyze_image(self, image_data: str, product_type: str, analysis_id: str) -> Dict:
        """Analizar imagen completa"""
        start_time = datetime.now()
        
        try:
            # Preprocesar imagen
            image = self.preprocess_image(image_data)
            
            # Realizar análisis
            defects = self.simulate_defect_detection(image, product_type)
            size_measurements = self.measure_size(image)
            color_analysis = self.analyze_color(image)
            texture_analysis = self.analyze_texture(image)
            
            # Calcular confianza general basada en los análisis
            base_confidence = 0.85
            if defects:
                # Ajustar confianza basada en defectos detectados
                avg_defect_confidence = np.mean([d['confidence'] for d in defects])
                base_confidence = (base_confidence + avg_defect_confidence) / 2
            
            # Calcular tiempo de procesamiento
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                'analysis_id': analysis_id,
                'defects': defects,
                'size_measurements': size_measurements,
                'color_analysis': color_analysis,
                'texture_analysis': texture_analysis,
                'confidence_score': float(base_confidence),
                'processing_time': float(processing_time),
                'total_area': size_measurements['total_area_pixels'],
                'image_dimensions': {
                    'width': size_measurements['width_pixels'],
                    'height': size_measurements['height_pixels']
                },
                'product_type': product_type,
                'analysis_timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error en análisis de imagen: {str(e)}")

# Instancia global del analizador
vision_ai = AgriculturalVisionAI()

@app.post("/analyze-image", response_model=ImageAnalysisResponse)
async def analyze_image(request: ImageAnalysisRequest):
    """
    Analizar una imagen de producto agrícola para control de calidad
    
    - **image_data**: Imagen en formato base64
    - **product_type**: Tipo de producto (Manzana, Naranja, Tomate, Papa)
    - **analysis_id**: ID único para el análisis
    """
    try:
        print(f"🔍 Iniciando análisis para {request.product_type} - ID: {request.analysis_id}")
        
        result = vision_ai.analyze_image(
            request.image_data,
            request.product_type,
            request.analysis_id
        )
        
        print(f"✅ Análisis completado: {len(result['defects'])} defectos encontrados")
        return ImageAnalysisResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error en análisis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en análisis de imagen: {str(e)}")

@app.post("/analyze-batch")
async def analyze_batch(images: List[UploadFile] = File(...)):
    """Endpoint para análisis por lote de múltiples imágenes"""
    results = []
    
    try:
        for i, image in enumerate(images):
            print(f"📦 Procesando imagen {i+1}/{len(images)}")
            
            # Convertir imagen a base64
            image_data = base64.b64encode(await image.read()).decode("utf-8")
            
            # Analizar cada imagen
            result = vision_ai.analyze_image(
                image_data,
                "Manzana",  # Tipo por defecto para batch
                f"batch_{datetime.now().timestamp()}_{i}"
            )
            results.append(result)
        
        return {
            "batch_id": f"batch_{datetime.now().timestamp()}",
            "total_images": len(images),
            "results": results,
            "summary": {
                "total_defects": sum(len(r['defects']) for r in results),
                "average_confidence": np.mean([r['confidence_score'] for r in results]),
                "processing_time_total": sum(r['processing_time'] for r in results)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en análisis por lote: {str(e)}")

@app.get("/")
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "Agricultural Computer Vision API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "analyze-image": "POST /analyze-image - Analizar imagen individual",
            "analyze-batch": "POST /analyze-batch - Analizar lote de imágenes",
            "docs": "GET /docs - Documentación interactiva"
        }
    }

@app.get("/health")
async def health_check():
    """Endpoint de verificación de salud"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "agricultural-vision-api"
    }

@app.get("/supported-products")
async def get_supported_products():
    """Obtener lista de productos soportados"""
    return {
        "supported_products": list(vision_ai.defect_categories.keys()),
        "defect_categories": vision_ai.defect_categories
    }

if __name__ == "__main__":
    print("🚀 Iniciando Servidor de Computer Vision...")
    print("📚 Documentación disponible en: http://localhost:8004/docs")
    print("🌱 Productos soportados:", list(vision_ai.defect_categories.keys()))
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8004,
        log_level="info"
    )