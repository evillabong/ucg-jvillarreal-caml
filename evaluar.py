#!/usr/bin/env python3
"""
CLI para el evaluador exigente de tesis en ciencia de datos.

Uso:
    python evaluar.py --texto mi_tesis.txt
    python evaluar.py --texto mi_tesis.txt --proveedor openai --modelo gpt-4o
    python evaluar.py --texto mi_tesis.txt --proveedor anthropic
    python evaluar.py --texto mi_tesis.txt --proveedor manual
"""

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluador exigente de tesis en ciencia de datos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--texto",
        required=True,
        metavar="ARCHIVO",
        help="Ruta al archivo de texto con la tesis a evaluar (.txt, .md)",
    )
    parser.add_argument(
        "--proveedor",
        choices=["openai", "anthropic", "manual"],
        default="manual",
        help="Proveedor de LLM a usar (por defecto: manual)",
    )
    parser.add_argument(
        "--modelo",
        default=None,
        help="Nombre del modelo a usar (opcional, usa el predeterminado del proveedor)",
    )
    parser.add_argument(
        "--salida",
        metavar="ARCHIVO",
        default=None,
        help="Guardar la evaluación en un archivo en lugar de imprimir en pantalla",
    )

    args = parser.parse_args()

    archivo = Path(args.texto)
    if not archivo.exists():
        print(f"Error: No se encontró el archivo '{archivo}'", file=sys.stderr)
        return 1

    texto_tesis = archivo.read_text(encoding="utf-8")
    if not texto_tesis.strip():
        print(f"Error: El archivo '{archivo}' está vacío", file=sys.stderr)
        return 1

    from evaluador_tesis import (
        evaluar_con_anthropic,
        evaluar_con_openai,
        evaluar_sin_api,
    )

    try:
        if args.proveedor == "openai":
            kwargs = {}
            if args.modelo:
                kwargs["modelo"] = args.modelo
            resultado = evaluar_con_openai(texto_tesis, **kwargs)
        elif args.proveedor == "anthropic":
            kwargs = {}
            if args.modelo:
                kwargs["modelo"] = args.modelo
            resultado = evaluar_con_anthropic(texto_tesis, **kwargs)
        else:
            resultado = evaluar_sin_api(texto_tesis)
    except (ImportError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if args.salida:
        Path(args.salida).write_text(resultado.texto_evaluacion, encoding="utf-8")
        print(f"Evaluación guardada en: {args.salida}")
    else:
        resultado.imprimir()

    return 0


if __name__ == "__main__":
    sys.exit(main())
