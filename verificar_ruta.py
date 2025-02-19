import os

# Verificación de ruta absoluta
current_dir = os.path.dirname(os.path.abspath(__file__))
CARPETA_OCR = os.path.join(current_dir, "materiales_clase_ocr")

# Mostrar las rutas para depuración
print(f"📂 Ruta actual del script: {current_dir}")
print(f"📂 Ruta construida para OCR: {CARPETA_OCR}")
print(f"✅ ¿Existe la carpeta OCR?: {os.path.exists(CARPETA_OCR)}")

# Lanzar error si la carpeta no existe
if not os.path.exists(CARPETA_OCR):
    raise FileNotFoundError(f"🚫 La carpeta {CARPETA_OCR} no existe. Verifica la ubicación.")
