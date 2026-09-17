"""Consultas a Crossref, OpenAlex y PubMed, con caché en disco y freno de ritmo.

Tres decisiones de diseño, todas por la misma razón — que una verificación no
dependa de que una API esté de buen humor:

- **Caché en disco** (`registro/_cache_red/`). Una consulta ya hecha no se
  repite, así que volver a correr la verificación es instantáneo y offline.
- **Modo sin red** (`--sin-red`). Degrada a aviso en lugar de error. El CI lo usa
  siempre: un servicio caído no debe poner en rojo la tesis de nadie.
- **Nunca inventa.** Si no se puede comprobar algo, se dice "no se pudo
  comprobar", que es distinto de "está mal" y muy distinto de "está bien".
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import pathlib
import time
from dataclasses import dataclass
from typing import Any

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DIR_CACHE = RAIZ / "registro" / "_cache_red"

CROSSREF = "https://api.crossref.org/works/"
OPENALEX = "https://api.openalex.org/works"
PUBMED_BUSCAR = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_RESUMEN = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

#: Crossref y OpenAlex piden un correo de contacto para dar mejor servicio.
CONTACTO = "tesis-sanmarcos (repositorio académico UNMSM)"
UA = f"tesis-sanmarcos/0.1 ({CONTACTO})"

#: Segundos entre llamadas al mismo servicio. Conservador a propósito.
PAUSA = 0.35


@dataclass
class Respuesta:
    """Resultado de una consulta. `ok=False` no significa que la cita esté mal."""

    ok: bool
    datos: dict[str, Any] | None = None
    motivo: str = ""
    desde_cache: bool = False

    @property
    def sin_comprobar(self) -> bool:
        return not self.ok


class Cliente:
    def __init__(self, sin_red: bool = False, dir_cache: pathlib.Path | None = None,
                 pausa: float = PAUSA) -> None:
        self.sin_red = sin_red
        self.dir_cache = dir_cache or DIR_CACHE
        self.pausa = pausa
        self._ultimo: dict[str, float] = {}
        self.consultas = 0
        self.aciertos_cache = 0

    # -- caché -----------------------------------------------------------------

    def _ruta_cache(self, servicio: str, clave: str) -> pathlib.Path:
        h = hashlib.sha256(clave.encode("utf8")).hexdigest()[:24]
        return self.dir_cache / servicio / f"{h}.json"

    def _leer_cache(self, servicio: str, clave: str) -> dict[str, Any] | None:
        ruta = self._ruta_cache(servicio, clave)
        if not ruta.exists():
            return None
        try:
            return json.loads(ruta.read_text(encoding="utf8"))
        except (json.JSONDecodeError, OSError):
            return None

    def _guardar_cache(self, servicio: str, clave: str, datos: dict[str, Any]) -> None:
        ruta = self._ruta_cache(servicio, clave)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        # Que no se pueda escribir la caché no debe tumbar una verificación.
        with contextlib.suppress(OSError):
            ruta.write_text(json.dumps(datos, ensure_ascii=False), encoding="utf8")

    # -- transporte ------------------------------------------------------------

    def _frenar(self, servicio: str) -> None:
        ultimo = self._ultimo.get(servicio)
        if ultimo is not None:
            espera = self.pausa - (time.monotonic() - ultimo)
            if espera > 0:
                time.sleep(espera)
        self._ultimo[servicio] = time.monotonic()

    def _pedir(self, servicio: str, url: str, params: dict[str, Any] | None = None,
               intentos: int = 3) -> Respuesta:
        clave = url + "?" + json.dumps(params or {}, sort_keys=True)

        en_cache = self._leer_cache(servicio, clave)
        if en_cache is not None:
            self.aciertos_cache += 1
            return Respuesta(ok=en_cache.get("_ok", True), datos=en_cache.get("datos"),
                             motivo=en_cache.get("_motivo", ""), desde_cache=True)

        if self.sin_red:
            return Respuesta(False, motivo="modo sin red y no estaba en caché")

        try:
            import requests
        except ImportError:
            return Respuesta(False, motivo="falta la dependencia `requests`")

        for intento in range(intentos):
            self._frenar(servicio)
            try:
                self.consultas += 1
                r = requests.get(url, params=params, headers={"User-Agent": UA},
                                 timeout=20)
            except Exception as e:  # noqa: BLE001
                if intento == intentos - 1:
                    return Respuesta(False, motivo=f"no se pudo conectar: {type(e).__name__}")
                time.sleep(1.5 * (intento + 1))
                continue

            if r.status_code == 404:
                res = {"_ok": False, "_motivo": "no encontrado", "datos": None}
                self._guardar_cache(servicio, clave, res)
                return Respuesta(False, motivo="no encontrado")
            if r.status_code in (429, 500, 502, 503, 504):
                if intento == intentos - 1:
                    return Respuesta(False, motivo=f"el servicio respondió {r.status_code}")
                time.sleep(2.0 * (intento + 1))
                continue
            if r.status_code != 200:
                return Respuesta(False, motivo=f"respuesta {r.status_code}")

            try:
                datos = r.json()
            except ValueError:
                return Respuesta(False, motivo="la respuesta no era JSON")
            self._guardar_cache(servicio, clave, {"_ok": True, "datos": datos})
            return Respuesta(True, datos=datos)

        return Respuesta(False, motivo="agotados los reintentos")

    # -- servicios -------------------------------------------------------------

    def crossref(self, doi: str) -> Respuesta:
        if not doi:
            return Respuesta(False, motivo="sin DOI")
        r = self._pedir("crossref", CROSSREF + doi.strip())
        if not r.ok or not r.datos:
            return r
        msg = r.datos.get("message") or {}
        titulos = msg.get("title") or []
        fecha = (msg.get("issued") or {}).get("date-parts") or [[]]
        anio = str(fecha[0][0]) if fecha and fecha[0] else ""
        autores = msg.get("author") or []
        return Respuesta(True, datos={
            "titulo": titulos[0] if titulos else "",
            "anio": anio,
            "primer_autor": (autores[0].get("family") or "") if autores else "",
            "tipo": msg.get("type", ""),
            "retirado": bool(msg.get("update-to") and any(
                (u.get("type") or "").lower() == "retraction"
                for u in msg.get("update-to") or [])),
            "fuente": "crossref",
        }, desde_cache=r.desde_cache)

    def openalex(self, titulo: str, anio: str = "") -> Respuesta:
        if not titulo:
            return Respuesta(False, motivo="sin título para buscar")
        params = {"search": titulo[:250], "per-page": 5}
        r = self._pedir("openalex", OPENALEX, params)
        if not r.ok or not r.datos:
            return r
        resultados = r.datos.get("results") or []
        if not resultados:
            return Respuesta(False, motivo="OpenAlex no devolvió resultados")
        mejor = resultados[0]
        autoria = mejor.get("authorships") or []
        primer = ""
        if autoria:
            primer = ((autoria[0].get("author") or {}).get("display_name") or "").split()[-1:]
            primer = primer[0] if primer else ""
        return Respuesta(True, datos={
            "titulo": mejor.get("title") or mejor.get("display_name") or "",
            "anio": str(mejor.get("publication_year") or ""),
            "primer_autor": primer,
            "doi": (mejor.get("doi") or "").replace("https://doi.org/", ""),
            "retirado": bool(mejor.get("is_retracted")),
            "fuente": "openalex",
        }, desde_cache=r.desde_cache)

    def pubmed(self, titulo: str) -> Respuesta:
        """Busca por título y devuelve el PMID y los metadatos del primer acierto."""
        if not titulo:
            return Respuesta(False, motivo="sin título para buscar")
        buscar = self._pedir("pubmed", PUBMED_BUSCAR, {
            "db": "pubmed", "term": titulo[:250], "retmode": "json", "retmax": 1})
        if not buscar.ok or not buscar.datos:
            return buscar
        ids = ((buscar.datos.get("esearchresult") or {}).get("idlist") or [])
        if not ids:
            return Respuesta(False, motivo="PubMed no devolvió resultados")
        pmid = ids[0]
        resumen = self._pedir("pubmed", PUBMED_RESUMEN, {
            "db": "pubmed", "id": pmid, "retmode": "json"})
        if not resumen.ok or not resumen.datos:
            return Respuesta(True, datos={"pmid": pmid, "fuente": "pubmed"},
                             desde_cache=resumen.desde_cache)
        reg = (resumen.datos.get("result") or {}).get(pmid) or {}
        tipos = [t.lower() for t in (reg.get("pubtype") or [])]
        return Respuesta(True, datos={
            "pmid": pmid,
            "titulo": reg.get("title", ""),
            "anio": (reg.get("pubdate") or "")[:4],
            "retirado": any("retract" in t for t in tipos),
            "fuente": "pubmed",
        }, desde_cache=resumen.desde_cache)

    def estadisticas(self) -> dict[str, int]:
        return {"consultas_de_red": self.consultas, "aciertos_de_cache": self.aciertos_cache}


def parecido(a: str, b: str) -> float:
    """Similitud 0-1 entre dos títulos, tolerante a puntuación y mayúsculas."""
    if not a or not b:
        return 0.0
    try:
        from rapidfuzz import fuzz
        return fuzz.token_set_ratio(a.lower(), b.lower()) / 100.0
    except ImportError:
        import difflib
        return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()
