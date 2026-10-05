"""Anota en `registro/registro_ia.jsonl` cada acción de Claude que toca la tesis.

Es el único hook del repositorio y está escrito para no estorbar nunca:

- **Siempre termina con código 0.** Pase lo que pase. La documentación de hooks
  dice que solo el código 2 bloquea, así que este archivo no contiene ningún
  camino que devuelva 2. Si algo falla aquí, se pierde una línea del registro;
  no se pierde el trabajo del tesista.
- **Se dispara en `PostToolUse`**, que por definición no puede bloquear: la
  herramienta ya se ejecutó cuando este script arranca.
- **Importa lo mínimo** porque corre en cada escritura, edición y comando. Nada
  de pandas ni de yaml aquí.

De este archivo sale la declaración de uso de IA que genera `entregar.py`. Por
eso registra qué se hizo y sobre qué, no el contenido: el contenido ya está en
el repositorio y en el historial de git.
"""
import datetime
import json
import os
import pathlib
import sys

#: Cosas que no deben acabar escritas en un registro que se va a compartir.
SOSPECHOSO = ("api_key", "api-key", "token", "password", "passwd", "secret",
              "authorization", "bearer ", "apikey")

LIMITE_RESUMEN = 220


def raiz() -> pathlib.Path:
    """Raíz del proyecto: la variable del entorno, o dos niveles sobre este archivo."""
    desde_entorno = os.environ.get("CLAUDE_PROJECT_DIR")
    if desde_entorno:
        return pathlib.Path(desde_entorno)
    return pathlib.Path(__file__).resolve().parent.parent.parent


def etapa_actual(base: pathlib.Path) -> str:
    """Etapa que las skills dejan anotada en `registro/.etapa`."""
    marca = base / "registro" / ".etapa"
    try:
        return marca.read_text(encoding="utf8").strip() or "sin etapa"
    except OSError:
        return "sin etapa"


def _relativa(ruta: str, base: pathlib.Path) -> str:
    """Ruta relativa a la raíz, siempre con barras normales.

    El registro puede leerse en otra máquina o acabar en la declaración de uso
    de IA, así que no debe arrastrar separadores de Windows.
    """
    if not ruta:
        return ""
    try:
        rel = str(pathlib.Path(ruta).resolve().relative_to(base.resolve()))
    except (ValueError, OSError):
        rel = ruta
    return rel.replace("\\", "/")


def _redactar(texto: str) -> str:
    bajo = texto.lower()
    if any(s in bajo for s in SOSPECHOSO):
        return "[omitido: el comando parecía contener una credencial]"
    return texto


def resumir(herramienta: str, entrada: dict, base: pathlib.Path) -> tuple[str, str]:
    """Devuelve (archivo, resumen) para una llamada de herramienta."""
    archivo = _relativa(str(entrada.get("file_path") or entrada.get("notebook_path") or ""), base)

    if herramienta in ("Write", "NotebookEdit"):
        contenido = entrada.get("content") or entrada.get("file_text") or ""
        lineas = len(contenido.splitlines())
        return archivo, f"escribió {lineas} líneas"

    if herramienta in ("Edit", "MultiEdit"):
        cambios = entrada.get("edits")
        if isinstance(cambios, list) and cambios:
            return archivo, f"aplicó {len(cambios)} ediciones"
        viejo = entrada.get("old_string") or ""
        return archivo, f"reemplazó un fragmento de {len(viejo)} caracteres"

    if herramienta == "Bash":
        comando = str(entrada.get("command") or "").replace("\n", " ")
        comando = _redactar(comando)
        if len(comando) > LIMITE_RESUMEN:
            comando = comando[:LIMITE_RESUMEN] + "…"
        return "", f"ejecutó: {comando}"

    return archivo, f"usó {herramienta}"


def main() -> int:
    try:
        crudo = sys.stdin.read()
        datos = json.loads(crudo) if crudo.strip() else {}
    except Exception:
        return 0

    try:
        herramienta = str(datos.get("tool_name") or "")
        if not herramienta:
            return 0

        base = raiz()
        entrada = datos.get("tool_input") or {}
        archivo, resumen = resumir(herramienta, entrada, base)

        # No se registra lo que el propio registro escribe: sería ruido circular.
        if archivo.replace("\\", "/").startswith("registro/"):
            return 0

        linea = {
            "momento": datetime.datetime.now().isoformat(timespec="seconds"),
            "etapa": etapa_actual(base),
            "herramienta": herramienta,
            "archivo": archivo,
            "resumen": resumen,
            "sesion": str(datos.get("session_id") or "")[:8],
            "tool_use_id": str(datos.get("tool_use_id") or ""),
        }

        destino = base / "registro" / "registro_ia.jsonl"
        destino.parent.mkdir(parents=True, exist_ok=True)
        with open(destino, "a", encoding="utf8") as f:
            f.write(json.dumps(linea, ensure_ascii=False) + "\n")
    except Exception:
        # Un registro incompleto es un problema menor; una sesión rota no lo es.
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
