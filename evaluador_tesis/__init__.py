"""
Evaluador exigente de tesis aplicada en ciencia de datos.

Paquete que implementa un evaluador riguroso para tesis de ciencia de datos,
con énfasis en detectar debilidades reales, supuestos injustificados y
conclusiones infladas.

Uso básico:
    from evaluador_tesis import evaluar_con_openai, evaluar_sin_api

    # Con API de OpenAI (requiere OPENAI_API_KEY)
    resultado = evaluar_con_openai(texto_tesis)
    resultado.imprimir()

    # Sin API (genera guía de evaluación manual)
    resultado = evaluar_sin_api(texto_tesis)
    resultado.imprimir()
"""

from evaluador_tesis.evaluador import (
    ResultadoEvaluacion,
    evaluar_con_anthropic,
    evaluar_con_openai,
    evaluar_sin_api,
)

__all__ = [
    "ResultadoEvaluacion",
    "evaluar_con_anthropic",
    "evaluar_con_openai",
    "evaluar_sin_api",
]
