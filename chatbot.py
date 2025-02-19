import os
import openai
import wikipediaapi
import requests
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import BaseModel
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.llms.openai import OpenAI
from bs4 import BeautifulSoup

import os
import openai

# Leer la API Key desde las variables de entorno
openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    raise ValueError("❌ No se encontró la API Key. Configúrala como variable de entorno.")

# Ruta absoluta a la carpeta de documentos OCR
CARPETA_OCR = r"C:\Users\Florencia\Downloads\chatbot-linguistica\materiales_clase_ocr"

# Verificación de la ruta y existencia de la carpeta
print(f"📂 Ruta a la carpeta OCR: {CARPETA_OCR}")
if not os.path.exists(CARPETA_OCR):
    raise FileNotFoundError(f"🚫 La carpeta {CARPETA_OCR} no existe. Verifica la ubicación.")

# Cargar documentos y crear índice
try:
    print("🔄 Cargando documentos...")
    documentos = SimpleDirectoryReader(input_dir=CARPETA_OCR).load_data()
    indice = VectorStoreIndex.from_documents(documentos)
    print("✅ Documentos cargados correctamente.")
except Exception as e:
    print(f"🚫 Error al cargar documentos: {e}")
    raise

# Configurar el modelo de IA (GPT-4o) con respuestas largas
llm = OpenAI(model="gpt-4o", max_tokens=2048, temperature=0.7)

# Crear API con FastAPI utilizando solo Swagger UI
app = FastAPI(
    title="Chatbot de Lingüística 📚💬",
    description="Asistente virtual con bibliografía priorizada y búsqueda web gratuita.",
    version="1.0.0",
    docs_url="/docs",    # Activa Swagger UI en /docs
    redoc_url=None        # Desactiva ReDoc
)

# Modelo para la solicitud POST
class PreguntaRequest(BaseModel):
    pregunta: str

# Función para buscar en Wikipedia
def buscar_en_wikipedia(query):
    try:
        wiki = wikipediaapi.Wikipedia('es')
        pagina = wiki.page(query)
        return pagina.summary if pagina.exists() else None
    except Exception as e:
        print(f"🚫 Error al buscar en Wikipedia: {e}")
        return None

# Función para buscar en la web usando DuckDuckGo (gratuito)
def buscar_en_duckduckgo(query):
    try:
        url = f"https://duckduckgo.com/html/?q={query}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        resultados = soup.find_all('a', class_='result__a')
        return resultados[0].text if resultados else None
    except Exception as e:
        print(f"🚫 Error al buscar en DuckDuckGo: {e}")
        return None

# Función para buscar en los documentos cargados (prioridad 1)
def buscar_en_documentos(pregunta):
    try:
        query_engine = indice.as_query_engine(llm=llm)
        respuesta = query_engine.query(pregunta)
        return respuesta.response.strip()
    except Exception as e:
        print(f"🚫 Error al buscar en documentos: {e}")
        return ""

@app.get("/")
def read_root():
    return {"message": "Chatbot listo: prioriza la bibliografía y usa fuentes web gratuitas si es necesario 🚀"}

@app.post("/preguntar/")
def preguntar(request: PreguntaRequest):
    pregunta = request.pregunta.strip()
    if not pregunta:
        return {"respuesta": "❌ La pregunta no puede estar vacía."}

    # 1️⃣ Buscar primero en la bibliografía cargada
    respuesta_documentos = buscar_en_documentos(pregunta)
    if len(respuesta_documentos) > 50:
        return {"respuesta": f"📄 Respuesta desde la bibliografía cargada: {respuesta_documentos}"}

    # 2️⃣ Si no hay respuesta suficiente, buscar en Wikipedia
    respuesta_wikipedia = buscar_en_wikipedia(pregunta)
    if respuesta_wikipedia:
        return {"respuesta": f"📚 Respuesta desde Wikipedia: {respuesta_wikipedia}"}

    # 3️⃣ Si tampoco se encuentra en Wikipedia, buscar en DuckDuckGo
    respuesta_web = buscar_en_duckduckgo(pregunta)
    if respuesta_web:
        return {"respuesta": f"🌐 Respuesta desde la web (DuckDuckGo): {respuesta_web}"}

    # 4️⃣ Si no se encuentra información en ninguna fuente
    return {"respuesta": "❌ No se encontró información en la bibliografía ni en fuentes web."}
