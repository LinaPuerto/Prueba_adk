# MCP/mcp_server_bosque.py

from mcp.server.fastmcp import FastMCP
import requests
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import os
from datetime import datetime
import google.generativeai as genai

# Inicializa el servidor
server = FastMCP("servidor_bosque")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

PDFS = {
    "filosofia_fungi": r"E:\DATAR\Prueba_adk\pdfs\Filosofia_fungi.pdf",
    "margullis": r"E:\DATAR\Prueba_adk\pdfs\Margullis.pdf",
    "hongo_planta": r"E:\DATAR\Prueba_adk\pdfs\Hongo_planta.pdf",
    "donna": r"E:\DATAR\Prueba_adk\pdfs\donna.pdf",
}

# Fuentes fijas
FUENTES = {
    "pot": "https://bogota.gov.co/bog/pot-2022-2035/",
    "biomimética": "https://asknature.org/",
    "suelo": "https://www.frontiersin.org/journals/microbiology/articles/10.3389/fmicb.2019.02872/full",
    "briofitas": "https://stri.si.edu/es/noticia/briofitas",
}

def log_uso(fuente, tipo):
    """Guarda registro de cada fuente usada."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] Usando {tipo}: {fuente}")

@server.tool()
def leer_pagina(url: str) -> str:
    """Lee y devuelve texto de una página web."""
    log_uso(url, "página web")
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    text = soup.get_text(separator="\n", strip=True)
    return text[:4000]

@server.tool()
def explorar_pdf(tema: str) -> str:
    """
    Explora un los archivos que estan en PDFS, busca los temas asociados y genera
    un conjunto de preguntas reflexivas basadas en filosofía de la biología, simbiosis,
    concepto de individuo y asociaciones.Usa el modelo Gemini para formularlas.
    """
    tema = tema.lower().strip()
    if tema not in PDFS:
        return f"No hay un PDF registrado para el tema '{tema}'."

    ruta_pdf = PDFS[tema]
    if not os.path.exists(ruta_pdf):
        return f"No se encontró el archivo: {ruta_pdf}"

    log_uso(ruta_pdf, "PDF")

    # Extraer texto del PDF
    texto = ""
    with fitz.open(ruta_pdf) as doc:
        for pagina in doc:
            texto += pagina.get_text()

    texto_corto = texto[:6000]  # limitar el texto para el modelo

    # Crear prompt reflexivo
    prompt = f"""
    Eres un asistente reflexivo especializado en filosofía de la biología.
    A partir del siguiente fragmento del texto, genera un breve resumen
    (máximo 5 líneas) y luego 1 a 3 preguntas filosóficas o reflexivas
    relacionadas con temas como:
    - simbiosis
    - concepto de individuo
    - cooperación y asociaciones biológicas
    - límites entre especies
    - vida y relaciones ecológicas
    - el humano como parte del ecosistema

    Texto:
    \"\"\"{texto_corto}\"\"\"
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        salida = response.text.strip()
    except Exception as e:
        salida = f"Error al generar preguntas con Gemini: {e}"

    resultado = (
        f"📄 Fuente PDF: {ruta_pdf}\n\n"
        f"💬 Resultado generado por IA:\n\n{salida}"
    )
    return resultado

@server.tool()
def explorar(tema: str) -> str:
    """
    Busca información sobre un tema combinando PDFs y fuentes web.
    """
    tema = tema.lower().strip()
    respuesta = ""

    # Intentar con PDF
    if tema in PDFS:
        respuesta += explorar_pdf(tema) + "\n\n"

    # Buscar fuente web
    for clave, link in FUENTES.items():
        if clave in tema:
            log_uso(link, "fuente web")
            resp = requests.get(link)
            soup = BeautifulSoup(resp.text, "html.parser")
            text = soup.get_text(separator="\n", strip=True)
            resumen = text[:1500]
            respuesta += f"🌐 Fuente web: {link}\n\n{resumen}\n\n"

    if not respuesta.strip():
        respuesta = f"No encontré información registrada para el tema '{tema}'."

    return respuesta
