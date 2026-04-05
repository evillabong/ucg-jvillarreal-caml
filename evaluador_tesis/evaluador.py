"""
Evaluador exigente de tesis aplicada en ciencia de datos.

Módulo principal que orquesta la evaluación usando el LLM configurado
con el system prompt del evaluador exigente.
"""

from __future__ import annotations

import os
import textwrap
from dataclasses import dataclass, field
from typing import Optional

from evaluador_tesis.criterios import (
    CRITERIOS_EVALUACION,
    ESCALA_SEVERIDAD,
    ESTRUCTURA_INFORME,
)
from evaluador_tesis.prompt import PROMPT_EVALUACION, SYSTEM_PROMPT


@dataclass
class ResultadoEvaluacion:
    """Resultado estructurado de una evaluación de tesis."""

    texto_evaluacion: str
    modelo_usado: str
    tokens_usados: Optional[int] = None
    advertencias: list[str] = field(default_factory=list)

    def imprimir(self) -> None:
        """Imprime la evaluación formateada en la consola."""
        separador = "=" * 80
        print(separador)
        print("EVALUACIÓN EXIGENTE DE TESIS EN CIENCIA DE DATOS")
        print(f"Modelo: {self.modelo_usado}")
        if self.tokens_usados:
            print(f"Tokens utilizados: {self.tokens_usados}")
        print(separador)
        if self.advertencias:
            print("\n⚠️  ADVERTENCIAS:")
            for adv in self.advertencias:
                print(f"  - {adv}")
            print()
        print(self.texto_evaluacion)
        print(separador)


def evaluar_con_openai(
    texto_tesis: str,
    modelo: str = "gpt-4o",
    api_key: Optional[str] = None,
) -> ResultadoEvaluacion:
    """
    Evalúa una tesis usando la API de OpenAI con el evaluador exigente.

    Args:
        texto_tesis: Texto completo o extracto de la tesis a evaluar.
        modelo: Modelo de OpenAI a usar (por defecto 'gpt-4o').
        api_key: API key de OpenAI. Si es None, usa la variable de entorno OPENAI_API_KEY.

    Returns:
        ResultadoEvaluacion con el texto de evaluación y metadatos.

    Raises:
        ImportError: Si el paquete 'openai' no está instalado.
        ValueError: Si no se encuentra la API key.
    """
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise ImportError(
            "El paquete 'openai' es necesario. Instálalo con: pip install openai"
        ) from exc

    key = api_key or os.environ.get("OPENAI_API_KEY")
    if not key:
        raise ValueError(
            "Se requiere una API key de OpenAI. "
            "Proporciona 'api_key' o define la variable de entorno OPENAI_API_KEY."
        )

    client = OpenAI(api_key=key)
    prompt_usuario = PROMPT_EVALUACION.format(texto_tesis=texto_tesis)

    respuesta = client.chat.completions.create(
        model=modelo,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt_usuario},
        ],
        temperature=0.2,
    )

    texto_evaluacion = respuesta.choices[0].message.content or ""
    tokens = respuesta.usage.total_tokens if respuesta.usage else None

    return ResultadoEvaluacion(
        texto_evaluacion=texto_evaluacion,
        modelo_usado=modelo,
        tokens_usados=tokens,
    )


def evaluar_con_anthropic(
    texto_tesis: str,
    modelo: str = "claude-opus-4-5",
    api_key: Optional[str] = None,
) -> ResultadoEvaluacion:
    """
    Evalúa una tesis usando la API de Anthropic (Claude) con el evaluador exigente.

    Args:
        texto_tesis: Texto completo o extracto de la tesis a evaluar.
        modelo: Modelo de Anthropic a usar (por defecto 'claude-opus-4-5').
        api_key: API key de Anthropic. Si es None, usa la variable ANTHROPIC_API_KEY.

    Returns:
        ResultadoEvaluacion con el texto de evaluación y metadatos.

    Raises:
        ImportError: Si el paquete 'anthropic' no está instalado.
        ValueError: Si no se encuentra la API key.
    """
    try:
        import anthropic
    except ImportError as exc:
        raise ImportError(
            "El paquete 'anthropic' es necesario. Instálalo con: pip install anthropic"
        ) from exc

    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise ValueError(
            "Se requiere una API key de Anthropic. "
            "Proporciona 'api_key' o define la variable de entorno ANTHROPIC_API_KEY."
        )

    client = anthropic.Anthropic(api_key=key)
    prompt_usuario = PROMPT_EVALUACION.format(texto_tesis=texto_tesis)

    respuesta = client.messages.create(
        model=modelo,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt_usuario}],
        temperature=0.2,
    )

    texto_evaluacion = respuesta.content[0].text if respuesta.content else ""
    tokens = (
        respuesta.usage.input_tokens + respuesta.usage.output_tokens
        if respuesta.usage
        else None
    )

    return ResultadoEvaluacion(
        texto_evaluacion=texto_evaluacion,
        modelo_usado=modelo,
        tokens_usados=tokens,
    )


def evaluar_sin_api(texto_tesis: str) -> ResultadoEvaluacion:
    """
    Genera una lista de preguntas de evaluación sin requerir una API externa.

    Útil para evaluación manual guiada o para verificar los criterios aplicables
    antes de usar un LLM.

    Args:
        texto_tesis: Texto de la tesis (se usa para calcular métricas básicas).

    Returns:
        ResultadoEvaluacion con las preguntas guía y plantilla de informe.
    """
    lineas = []
    lineas.append("# GUÍA DE EVALUACIÓN EXIGENTE - MODO MANUAL")
    lineas.append("")
    lineas.append(
        "Aplica las siguientes preguntas al texto de la tesis. "
        "Documenta cada hallazgo con la referencia textual exacta.\n"
    )

    for categoria, datos in CRITERIOS_EVALUACION.items():
        titulo = categoria.replace("_", " ").upper()
        lineas.append(f"## {titulo}")
        lineas.append(f"*{datos['descripcion']}* (peso: {datos['peso']:.0%})\n")
        for i, pregunta in enumerate(datos["preguntas_guia"], 1):
            lineas.append(f"  {i}. {pregunta}")
        lineas.append("")

    lineas.append("## ESCALA DE SEVERIDAD")
    for nivel, info in ESCALA_SEVERIDAD.items():
        lineas.append(f"- **{nivel.upper()}** (nivel {info['nivel']}): {info['descripcion']}")
        lineas.append(f"  → {info['accion_requerida']}")
    lineas.append("")

    lineas.append("## PLANTILLA DE INFORME")
    lineas.append(textwrap.dedent(ESTRUCTURA_INFORME))

    palabras = len(texto_tesis.split())
    advertencias = []
    if palabras < 500:
        advertencias.append(
            f"El texto proporcionado es muy corto ({palabras} palabras). "
            "Una evaluación completa requiere el documento íntegro."
        )

    return ResultadoEvaluacion(
        texto_evaluacion="\n".join(lineas),
        modelo_usado="manual (sin API)",
        advertencias=advertencias,
    )
