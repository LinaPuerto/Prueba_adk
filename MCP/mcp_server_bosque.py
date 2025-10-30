# MCP/mcp_server_bosque.py

from mcp.server.fastmcp import FastMCP
import requests
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import os
from datetime import datetime

# Inicializa el servidor
server = FastMCP("servidor_bosque")

PDFS = {
    "Filosofia_fungi": r"E:\DATAR\pdfs\Filosofia_fungi.pdf",
    "Margullis": r"E:\DATAR\pdfs\Margullis.pdf",
    "Hongo_planta" : r"E:\DATAR\pdfs\Hongo_planta.pdf",
    "donna": r"E:\DATAR\pdfs\donna.pdf",
}

# Fuentes fijas 
FUENTES = {
    "POT": "https://bogota.gov.co/bog/pot-2022-2035/",
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
    log_uso(url, "página web")
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    text = soup.get_text(separator="\n", strip=True)
    return text[:8000]

@server.tool()
def explorar_pdf(tema: str) -> str:
    """
    Devuelve texto resumido de un PDF asociado al tema.
    """
    tema = tema.lower().strip()
    if tema not in PDFS:
        return f"No hay un PDF registrado para el tema '{tema}'."

    ruta_pdf = PDFS[tema]
    if not os.path.exists(ruta_pdf):
        return f"No se encontró el archivo: {ruta_pdf}"

    log_uso(ruta_pdf, "PDF")

    texto = ""
    with fitz.open(ruta_pdf) as doc:
        for pagina in doc:
            texto += pagina.get_text()

    resumen = texto[:4000]
    return f"📄 Fuente PDF: {ruta_pdf}\n\n{resumen}"

@server.tool()
def explorar(tema: str) -> str:
    """
    Busca información sobre un tema combinando PDFs y fuentes web.
    """
    tema = tema.lower().strip()
    respuesta = ""

    #  Intentar con PDF
    if tema in PDFS:
        respuesta += explorar_pdf(tema) + "\n\n"

    #  Buscar fuente web
    for clave, link in FUENTES.items():
        if clave in tema:
            log_uso(link, "fuente web")
            resp = requests.get(link)
            soup = BeautifulSoup(resp.text, "html.parser")
            text = soup.get_text(separator="\n", strip=True)
            resumen = text[:1500]
            respuesta += f"🌐 Fuente web: {link}\n\n{resumen}\n\n"

    #  Verificar si se encontró algo
    if not respuesta.strip():
        respuesta = f"No encontré información registrada para el tema '{tema}'."

    return respuesta
