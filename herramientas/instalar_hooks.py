"""Instala el hook del registro de IA y el hook de git, en esta máquina.

Por qué hace falta un instalador en lugar de dejarlo todo en
`.claude/settings.json`: un hook necesita saber **con qué intérprete arrancar**,
y eso cambia en cada equipo. En Windows, además, `python` suele ser el atajo a la
Microsoft Store, que no ejecuta nada. Si el hook apuntara a un intérprete que no
existe, fallaría en silencio —que es su diseño, no bloquear— y el registro de IA
se quedaría vacío sin que nadie lo notara.

Por eso el intérprete se resuelve aquí, en la máquina donde se va a usar, y se
escribe en `.claude/settings.local.json`, que no se versiona.

Lo que instala:

1. **Un hook de Claude Code**, `PostToolUse`, que anota cada escritura, edición
   y comando en `registro/registro_ia.jsonl`. Siempre termina con código 0, así
   que no puede bloquear la sesión.
2. **Un hook de git**, `pre-commit`, que impide subir datos personales. Vive
   fuera de la sesión de Claude: bloquear un commit no interrumpe nada.

Uso:
    uv run python -m herramientas.instalar_hooks
    uv run python -m herramientas.instalar_hooks --comprobar
    uv run python -m herramientas.instalar_hooks --desinstalar
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import stat
import subprocess
import sys
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent

#: Herramientas cuyo uso vale la pena registrar. Leer o buscar no cambia la
#: tesis; escribir, editar y ejecutar código, sí.
MATCHER = "Write|Edit|MultiEdit|NotebookEdit|Bash"

MARCA = "tesis-sanmarcos:registro_ia"


def interprete() -> pathlib.Path:
    """El intérprete con el que se está ejecutando esto.

    Es la elección más fiable que existe: si está corriendo este archivo,
    arranca. Y si vino por `uv run`, apunta al Python del entorno del proyecto,
    que arranca directo y rápido, sin pagar la resolución de uv en cada llamada.
    """
    return pathlib.Path(sys.executable)


def _hook_config(raiz: pathlib.Path) -> dict:
    script = raiz / ".claude" / "hooks" / "registrar_ia.py"
    return {
        "matcher": MATCHER,
        "hooks": [
            {
                "type": "command",
                "command": str(interprete()),
                "args": [str(script)],
                "timeout": 10,
                "statusMessage": MARCA,
            }
        ],
    }


def _leer_json(ruta: pathlib.Path) -> dict:
    if not ruta.exists():
        return {}
    try:
        datos = json.loads(ruta.read_text(encoding="utf8"))
        return datos if isinstance(datos, dict) else {}
    except json.JSONDecodeError:
        return {}


def _es_nuestro(entrada: dict) -> bool:
    for h in entrada.get("hooks") or []:
        if h.get("statusMessage") == MARCA:
            return True
        args = h.get("args") or []
        if any("registrar_ia.py" in str(a) for a in args):
            return True
    return False


def instalar_hook_claude(raiz: pathlib.Path = RAIZ) -> tuple[pathlib.Path, bool]:
    """Escribe el hook en settings.local.json. Devuelve (ruta, si cambió)."""
    destino = raiz / ".claude" / "settings.local.json"
    destino.parent.mkdir(parents=True, exist_ok=True)

    ajustes = _leer_json(destino)
    hooks = ajustes.setdefault("hooks", {})
    post = hooks.setdefault("PostToolUse", [])
    nuevo = _hook_config(raiz)

    # Se reemplaza el nuestro si ya estaba; no se tocan los de nadie más.
    anterior = None
    for i, entrada in enumerate(post):
        if _es_nuestro(entrada):
            anterior = post[i]
            post[i] = nuevo
            break
    else:
        post.append(nuevo)

    if anterior == nuevo:
        return destino, False

    ajustes["$comentario"] = (
        "Archivo local, no se versiona. Lo genera "
        "`uv run python -m herramientas.instalar_hooks`, que resuelve el "
        "intérprete de esta máquina. Si cambias de equipo o de entorno, vuelve a "
        "ejecutarlo."
    )
    destino.write_text(json.dumps(ajustes, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf8")
    return destino, True


def desinstalar_hook_claude(raiz: pathlib.Path = RAIZ) -> bool:
    destino = raiz / ".claude" / "settings.local.json"
    ajustes = _leer_json(destino)
    post = (ajustes.get("hooks") or {}).get("PostToolUse") or []
    quedan = [e for e in post if not _es_nuestro(e)]
    if len(quedan) == len(post):
        return False
    if quedan:
        ajustes["hooks"]["PostToolUse"] = quedan
    else:
        ajustes["hooks"].pop("PostToolUse", None)
        if not ajustes["hooks"]:
            ajustes.pop("hooks", None)
    destino.write_text(json.dumps(ajustes, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf8")
    return True


def instalar_hook_git(raiz: pathlib.Path = RAIZ) -> tuple[bool, str]:
    """Apunta git a `.githooks/`. Devuelve (ok, detalle)."""
    carpeta = raiz / ".githooks"
    if not (carpeta / "pre-commit").exists():
        return False, "falta .githooks/pre-commit"

    # En POSIX el hook tiene que ser ejecutable.
    if os.name != "nt":
        archivo = carpeta / "pre-commit"
        archivo.chmod(archivo.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    try:
        r = subprocess.run(["git", "config", "core.hooksPath", ".githooks"],
                           cwd=str(raiz), capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError) as e:
        return False, f"no se pudo configurar git: {e}"
    if r.returncode != 0:
        return False, (r.stderr or "git config falló").strip()
    return True, "git usará .githooks/"


def comprobar(raiz: pathlib.Path = RAIZ) -> list[tuple[str, bool, str]]:
    """Comprueba de verdad que el hook arranca y escribe. Devuelve filas."""
    filas: list[tuple[str, bool, str]] = []

    script = raiz / ".claude" / "hooks" / "registrar_ia.py"
    filas.append(("script del hook", script.exists(), str(script.relative_to(raiz))))

    ajustes = _leer_json(raiz / ".claude" / "settings.local.json")
    post = (ajustes.get("hooks") or {}).get("PostToolUse") or []
    registrado = any(_es_nuestro(e) for e in post)
    filas.append(("hook registrado en settings.local.json", registrado,
                  "sí" if registrado else "falta: corre el instalador"))

    exe = None
    for entrada in post:
        if _es_nuestro(entrada):
            exe = (entrada.get("hooks") or [{}])[0].get("command")
            break
    if exe:
        existe = pathlib.Path(exe).exists()
        filas.append(("el intérprete configurado existe", existe, str(exe)))
    else:
        filas.append(("el intérprete configurado existe", False, "sin configurar"))

    # La prueba que importa: ¿arranca y escribe una línea?
    if script.exists() and exe and pathlib.Path(exe).exists():
        with tempfile.TemporaryDirectory() as tmp:
            falso = pathlib.Path(tmp)
            (falso / "registro").mkdir(parents=True, exist_ok=True)
            carga = json.dumps({
                "tool_name": "Write",
                "tool_input": {"file_path": str(falso / "capitulos" / "prueba.qmd"),
                               "content": "una línea\n"},
                "session_id": "comprobacion",
            })
            entorno = dict(os.environ, CLAUDE_PROJECT_DIR=str(falso))
            try:
                r = subprocess.run([exe, str(script)], input=carga, text=True,
                                   capture_output=True, timeout=20, env=entorno)
                escrito = (falso / "registro" / "registro_ia.jsonl").exists()
                filas.append(("el hook arranca y escribe", escrito and r.returncode == 0,
                              f"código de salida {r.returncode}"))
            except (OSError, subprocess.SubprocessError) as e:
                filas.append(("el hook arranca y escribe", False, str(e)))
    else:
        filas.append(("el hook arranca y escribe", False, "no se pudo probar"))

    # git
    try:
        r = subprocess.run(["git", "config", "--get", "core.hooksPath"],
                           cwd=str(raiz), capture_output=True, text=True, timeout=20)
        valor = r.stdout.strip()
        filas.append(("git apunta a .githooks", valor == ".githooks",
                      valor or "sin configurar"))
    except (OSError, subprocess.SubprocessError) as e:
        filas.append(("git apunta a .githooks", False, str(e)))

    return filas


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--comprobar", action="store_true",
                    help="no instala nada: comprueba que lo instalado funciona")
    ap.add_argument("--desinstalar", action="store_true")
    args = ap.parse_args(argv)

    if args.comprobar:
        print("Comprobación de los hooks")
        print("=" * 48)
        todo_bien = True
        for nombre, ok, detalle in comprobar():
            print(f"  [{'ok' if ok else '  '}] {nombre}: {detalle}")
            todo_bien = todo_bien and ok
        print()
        if todo_bien:
            print("Todo en orden. Cada escritura, edición y comando queda registrado.")
            return 0
        print("Falta algo. Corre: uv run python -m herramientas.instalar_hooks")
        return 1

    if args.desinstalar:
        quitado = desinstalar_hook_claude()
        subprocess.run(["git", "config", "--unset", "core.hooksPath"],
                       cwd=str(RAIZ), capture_output=True, text=True)
        print("Hook de Claude quitado." if quitado else "No había hook de Claude instalado.")
        print("git vuelve a usar sus hooks por defecto.")
        return 0

    destino, cambio = instalar_hook_claude()
    print(f"OK  hook de Claude {'instalado' if cambio else 'ya estaba al día'}")
    print(f"    {destino.relative_to(RAIZ)}")
    print(f"    intérprete: {interprete()}")

    ok, detalle = instalar_hook_git()
    print(f"{'OK ' if ok else 'ERR'} hook de git: {detalle}")

    print()
    print("El hook anota en registro/registro_ia.jsonl lo que Claude escribe,")
    print("edita y ejecuta. De ahí sale la declaración de uso de IA.")
    print("Nunca bloquea: si falla, se pierde una línea del registro, nada más.")
    print()
    print("Compruébalo con: uv run python -m herramientas.instalar_hooks --comprobar")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
