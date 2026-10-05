"""Herramientas de tesis-sanmarcos.

Todo lo que imprimen estas herramientas está en español y lo lee un tesista en
su terminal. En Windows la consola suele usar una página de códigos antigua, y
sin forzar UTF-8 los acentos salen rotos justo en los mensajes que importan: el
que dice por qué se detuvo un commit, el que explica qué cita no se pudo
verificar.

Por eso la salida se reconfigura aquí, al importar el paquete, en lugar de
repetirlo en cada `main()`. Si el flujo no admite reconfiguración —pytest lo
sustituye por el suyo— se deja como está y no pasa nada.
"""
import contextlib
import sys


def _salida_en_utf8() -> None:
    for flujo in (sys.stdout, sys.stderr):
        with contextlib.suppress(AttributeError, ValueError, OSError):
            flujo.reconfigure(encoding="utf-8", errors="replace")


_salida_en_utf8()
