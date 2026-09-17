"""Lector de `referencias.bib` sin dependencias externas.

Solo necesitamos leer lo que exporta Better BibTeX, no soportar BibTeX entero.
Aun así conviene ser tolerante: un `.bib` real trae llaves anidadas, comillas,
comentarios, entradas `@string` y campos repetidos.
"""
from __future__ import annotations

import pathlib
import re
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

#: Campos mínimos por tipo de entrada, según el estilo de citas del perfil.
CAMPOS_MINIMOS: dict[str, dict[str, tuple[str, ...]]] = {
    "apa7": {
        "article": ("author", "title", "journal", "year"),
        "book": ("author", "title", "publisher", "year"),
        "incollection": ("author", "title", "booktitle", "publisher", "year"),
        "inproceedings": ("author", "title", "booktitle", "year"),
        "phdthesis": ("author", "title", "school", "year"),
        "mastersthesis": ("author", "title", "school", "year"),
        "techreport": ("author", "title", "institution", "year"),
        "misc": ("author", "title", "year"),
        "online": ("title", "year", "url"),
    },
    "vancouver": {
        "article": ("author", "title", "journal", "year"),
        "book": ("author", "title", "publisher", "year"),
        "incollection": ("author", "title", "booktitle", "publisher", "year"),
        "inproceedings": ("author", "title", "booktitle", "year"),
        "phdthesis": ("author", "title", "school", "year"),
        "mastersthesis": ("author", "title", "school", "year"),
        "techreport": ("author", "title", "institution", "year"),
        "misc": ("author", "title", "year"),
        "online": ("title", "year", "url"),
    },
}

#: Tipos que, además, deberían traer paginación para poder citar con página.
TIPOS_CON_PAGINAS = {"article", "incollection", "inproceedings"}

RE_ENTRADA = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", re.I)


@dataclass
class Entrada:
    clave: str
    tipo: str
    campos: dict[str, str] = field(default_factory=dict)
    linea: int = 0

    def get(self, nombre: str, defecto: str = "") -> str:
        return self.campos.get(nombre.lower(), defecto)

    @property
    def doi(self) -> str:
        d = self.get("doi").strip()
        d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d, flags=re.I)
        return d

    @property
    def anio(self) -> str:
        for clave in ("year", "date"):
            v = self.get(clave)
            m = re.search(r"\b(1\d{3}|20\d{2})\b", v)
            if m:
                return m.group(1)
        return ""

    @property
    def titulo_limpio(self) -> str:
        t = re.sub(r"[{}]", "", self.get("title"))
        return re.sub(r"\s+", " ", t).strip()

    @property
    def primer_autor(self) -> str:
        autores = self.get("author")
        if not autores:
            return ""
        primero = re.split(r"\s+and\s+", autores, maxsplit=1)[0]
        primero = re.sub(r"[{}]", "", primero)
        if "," in primero:
            return primero.split(",", 1)[0].strip()
        return primero.strip().split()[-1] if primero.strip() else ""

    def campos_faltantes(self, estilo: str) -> list[str]:
        reglas = CAMPOS_MINIMOS.get(estilo) or CAMPOS_MINIMOS["apa7"]
        exigidos = reglas.get(self.tipo.lower())
        if exigidos is None:
            exigidos = ("author", "title", "year")
        return [c for c in exigidos if not self.get(c).strip()]


def _desenvolver(valor: str) -> str:
    v = valor.strip()
    while len(v) >= 2 and ((v[0] == "{" and v[-1] == "}") or (v[0] == '"' and v[-1] == '"')):
        v = v[1:-1].strip()
    return re.sub(r"\s+", " ", v)


def _partir_campos(cuerpo: str) -> Iterator[tuple[str, str]]:
    """Recorre `campo = valor` respetando llaves y comillas anidadas."""
    i, n = 0, len(cuerpo)
    while i < n:
        m = re.compile(r"([A-Za-z_][\w\-]*)\s*=\s*").match(cuerpo, i)
        if not m:
            i += 1
            continue
        nombre = m.group(1).lower()
        i = m.end()
        if i >= n:
            break
        if cuerpo[i] == "{":
            nivel, inicio = 0, i
            while i < n:
                if cuerpo[i] == "{":
                    nivel += 1
                elif cuerpo[i] == "}":
                    nivel -= 1
                    if nivel == 0:
                        i += 1
                        break
                i += 1
            valor = cuerpo[inicio:i]
        elif cuerpo[i] == '"':
            inicio = i
            i += 1
            while i < n and cuerpo[i] != '"':
                i += 2 if cuerpo[i] == "\\" else 1
            i += 1
            valor = cuerpo[inicio:i]
        else:
            inicio = i
            while i < n and cuerpo[i] != ",":
                i += 1
            valor = cuerpo[inicio:i]
        yield nombre, _desenvolver(valor)
        while i < n and cuerpo[i] in ", \n\r\t":
            i += 1


def parsear(texto: str) -> list[Entrada]:
    """Devuelve las entradas del .bib, en orden de aparición."""
    entradas: list[Entrada] = []
    for m in RE_ENTRADA.finditer(texto):
        tipo, clave = m.group(1).lower(), m.group(2)
        if tipo in {"comment", "preamble", "string"}:
            continue
        # cuerpo hasta la llave de cierre equilibrada
        i = texto.index("{", m.start())
        nivel, j = 0, i
        while j < len(texto):
            if texto[j] == "{":
                nivel += 1
            elif texto[j] == "}":
                nivel -= 1
                if nivel == 0:
                    break
            j += 1
        cuerpo = texto[m.end():j]
        campos = dict(_partir_campos(cuerpo))
        linea = texto.count("\n", 0, m.start()) + 1
        entradas.append(Entrada(clave=clave, tipo=tipo, campos=campos, linea=linea))
    return entradas


def cargar(ruta: pathlib.Path) -> list[Entrada]:
    if not ruta.exists():
        return []
    return parsear(ruta.read_text(encoding="utf8", errors="replace"))


def indexar(entradas: list[Entrada]) -> dict[str, Entrada]:
    return {e.clave: e for e in entradas}


def duplicados(entradas: list[Entrada]) -> dict[str, list[Entrada]]:
    """Agrupa entradas que parecen la misma obra, por DOI o por título+año."""
    por_firma: dict[str, list[Entrada]] = {}
    for e in entradas:
        doi = e.doi.lower()
        if doi:
            firma = f"doi:{doi}"
        else:
            t = re.sub(r"[^a-z0-9]+", "", e.titulo_limpio.lower())[:60]
            if not t:
                continue
            firma = f"ty:{t}:{e.anio}"
        por_firma.setdefault(firma, []).append(e)
    return {f: g for f, g in por_firma.items() if len(g) > 1}


def claves_repetidas(entradas: list[Entrada]) -> dict[str, int]:
    cuenta: dict[str, int] = {}
    for e in entradas:
        cuenta[e.clave] = cuenta.get(e.clave, 0) + 1
    return {k: v for k, v in cuenta.items() if v > 1}


def resumen(entradas: list[Entrada]) -> dict[str, Any]:
    tipos: dict[str, int] = {}
    for e in entradas:
        tipos[e.tipo] = tipos.get(e.tipo, 0) + 1
    return {
        "entradas": len(entradas),
        "con_doi": sum(1 for e in entradas if e.doi),
        "tipos": dict(sorted(tipos.items(), key=lambda kv: -kv[1])),
    }
