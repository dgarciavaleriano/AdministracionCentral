import os
import requests
from datetime import datetime
from typing import List, Optional
from xml.etree import ElementTree as ET
import logging

# Configuración básica de logging
logger = logging.getLogger(__name__)

class BOEClient:
    """
    Cliente para descargar PDFs del BOE a partir del sumario diario.
    Documentación oficial: https://www.boe.es/datosabiertos/api/api.php
    """
    BASE_URL = "https://www.boe.es/datosabiertos/api"

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()
        # El BOE no requiere autenticación, pero es buena práctica identificar el cliente.
        self.session.headers.update({
            "User-Agent": "AdministracionCentral/1.0 (RAG-PDF-Downloader)"
        })

    def _get_sumario_xml(self, fecha: str) -> Optional[ET.Element]:
        """
        Obtiene el sumario del BOE para una fecha (formato YYYYMMDD o YYYY-MM-DD).
        Devuelve el nodo raíz del XML o None si hay error.
        """
        fecha_limpia = fecha.replace("-", "")
        url = f"{self.BASE_URL}/boe/sumario/{fecha_limpia}"
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            # La API devuelve XML por defecto. Si se quisiera JSON, añadir header Accept: application/json
            return ET.fromstring(response.content)
        except requests.RequestException as e:
            logger.error(f"Error al obtener sumario del {fecha}: {e}")
            return None
        except ET.ParseError as e:
            logger.error(f"Error al parsear XML del sumario del {fecha}: {e}")
            return None

    def obtener_urls_pdf(self, fecha: str) -> List[str]:
        """
        Extrae todas las URLs de PDF del sumario de una fecha.
        """
        root = self._get_sumario_xml(fecha)
        if root is None:
            return []

        # Buscamos todas las etiquetas <url_pdf> en el XML (pueden estar en diferentes niveles)
        urls = []
        for elem in root.iter():
            if elem.tag == "url_pdf" and elem.text:
                urls.append(elem.text.strip())
        
        logger.info(f"Encontrados {len(urls)} PDFs en el sumario del {fecha}")
        return urls

    def descargar_pdf(self, url: str, directorio_destino: str = "data/pdfs") -> Optional[str]:
        """
        Descarga un PDF desde una URL y lo guarda en el directorio especificado.
        Devuelve la ruta del archivo guardado o None si falla.
        """
        os.makedirs(directorio_destino, exist_ok=True)
        nombre_archivo = url.split("/")[-1]
        ruta_completa = os.path.join(directorio_destino, nombre_archivo)

        # Si el archivo ya existe, no lo descargamos de nuevo (útil para RAG incremental)
        if os.path.exists(ruta_completa):
            logger.debug(f"El archivo {nombre_archivo} ya existe. Saltando descarga.")
            return ruta_completa

        try:
            response = self.session.get(url, timeout=self.timeout, stream=True)
            response.raise_for_status()
            with open(ruta_completa, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger.info(f"Descargado: {nombre_archivo}")
            return ruta_completa
        except requests.RequestException as e:
            logger.error(f"Error al descargar {url}: {e}")
            return None

    def descargar_sumario_completo(self, fecha: str, directorio_destino: str = "data/pdfs") -> List[str]:
        """
        Método de conveniencia: obtiene todas las URLs del sumario y descarga cada PDF.
        Devuelve la lista de rutas de archivos descargados.
        """
        urls = self.obtener_urls_pdf(fecha)
        rutas_descargadas = []
        for url in urls:
            ruta = self.descargar_pdf(url, directorio_destino)
            if ruta:
                rutas_descargadas.append(ruta)
        return rutas_descargadas


# --- Ejemplo de uso ---
#if __name__ == "__main__":
    # Configurar logging para ver el progreso
    #logging.basicConfig(level=logging.INFO)
    
    #cliente = BOEClient()
    # Descargar todos los PDFs del 13 de noviembre de 2026 (ejemplo)
    #fecha_ejemplo = "2026-11-13"
    #archivos = cliente.descargar_sumario_completo(fecha_ejemplo, directorio_destino="data/pdfs")
    
    #print(f"Se descargaron {len(archivos)} archivos en 'data/pdfs'.")