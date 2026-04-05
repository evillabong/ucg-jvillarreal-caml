"""
Tests para el evaluador exigente de tesis en ciencia de datos.
"""

import pytest
from evaluador_tesis.criterios import (
    CRITERIOS_EVALUACION,
    ESCALA_SEVERIDAD,
    ESTRUCTURA_INFORME,
)
from evaluador_tesis.prompt import PROMPT_EVALUACION, SYSTEM_PROMPT
from evaluador_tesis.evaluador import ResultadoEvaluacion, evaluar_sin_api


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

TESIS_CORTA = "El modelo predice con 95% de accuracy. Los resultados son excelentes."

TESIS_EJEMPLO = """
## Predicción de abandono escolar mediante machine learning

### Resumen
Este trabajo aplica un modelo de Random Forest para predecir el abandono escolar
en una muestra de 200 estudiantes de una sola institución educativa. Se obtuvo
un accuracy del 93% en el conjunto de prueba, lo que demuestra que el modelo
puede ser implementado en cualquier institución del país para reducir el abandono
escolar en un 50%. No se aplicó validación cruzada. Los datos fueron preprocesados
eliminando todos los valores nulos sin mayor análisis. La variable objetivo
representa únicamente el 8% de los casos (clases desbalanceadas). Se concluye
que el modelo es superior a todos los enfoques previos y está listo para producción.
"""


# ---------------------------------------------------------------------------
# Tests de criterios
# ---------------------------------------------------------------------------

class TestCriterios:
    def test_existen_tres_dimensiones(self):
        assert "debilidades_metodologicas" in CRITERIOS_EVALUACION
        assert "supuestos_injustificados" in CRITERIOS_EVALUACION
        assert "conclusiones_infladas" in CRITERIOS_EVALUACION

    def test_pesos_suman_uno(self):
        total = sum(v["peso"] for v in CRITERIOS_EVALUACION.values())
        assert abs(total - 1.0) < 1e-9, f"Los pesos deben sumar 1.0, suman {total}"

    def test_cada_criterio_tiene_preguntas(self):
        for nombre, datos in CRITERIOS_EVALUACION.items():
            assert len(datos["preguntas_guia"]) >= 5, (
                f"'{nombre}' debe tener al menos 5 preguntas guía"
            )

    def test_escala_severidad_tiene_cuatro_niveles(self):
        assert set(ESCALA_SEVERIDAD.keys()) == {"critico", "mayor", "menor", "observacion"}

    def test_estructura_informe_contiene_secciones_clave(self):
        secciones = [
            "Resumen Ejecutivo",
            "Debilidades Metodológicas",
            "Supuestos Injustificados",
            "Conclusiones Infladas",
            "Fortalezas",
            "Veredicto Final",
        ]
        for seccion in secciones:
            assert seccion in ESTRUCTURA_INFORME, f"Falta sección '{seccion}' en la plantilla"


# ---------------------------------------------------------------------------
# Tests del prompt
# ---------------------------------------------------------------------------

class TestPrompt:
    def test_system_prompt_no_vacio(self):
        assert len(SYSTEM_PROMPT) > 100

    def test_system_prompt_menciona_debilidades(self):
        assert "debilidades" in SYSTEM_PROMPT.lower() or "weaknesses" in SYSTEM_PROMPT.lower()

    def test_system_prompt_menciona_supuestos(self):
        assert "supuesto" in SYSTEM_PROMPT.lower() or "assumption" in SYSTEM_PROMPT.lower()

    def test_system_prompt_menciona_conclusiones(self):
        assert "conclusi" in SYSTEM_PROMPT.lower()

    def test_system_prompt_menciona_severidad(self):
        assert "critico" in SYSTEM_PROMPT.lower() or "crítico" in SYSTEM_PROMPT.lower()

    def test_prompt_evaluacion_tiene_placeholder(self):
        assert "{texto_tesis}" in PROMPT_EVALUACION

    def test_prompt_evaluacion_puede_formatearse(self):
        resultado = PROMPT_EVALUACION.format(texto_tesis="texto de prueba")
        assert "texto de prueba" in resultado
        assert "{texto_tesis}" not in resultado


# ---------------------------------------------------------------------------
# Tests del evaluador sin API
# ---------------------------------------------------------------------------

class TestEvaluarSinApi:
    def test_retorna_resultado_evaluacion(self):
        resultado = evaluar_sin_api(TESIS_EJEMPLO)
        assert isinstance(resultado, ResultadoEvaluacion)

    def test_modelo_es_manual(self):
        resultado = evaluar_sin_api(TESIS_EJEMPLO)
        assert "manual" in resultado.modelo_usado.lower()

    def test_evaluacion_contiene_preguntas_guia(self):
        resultado = evaluar_sin_api(TESIS_EJEMPLO)
        # Debe contener al menos algunas preguntas de evaluación
        assert "?" in resultado.texto_evaluacion

    def test_evaluacion_contiene_las_tres_dimensiones(self):
        resultado = evaluar_sin_api(TESIS_EJEMPLO)
        texto = resultado.texto_evaluacion.upper()
        assert "METODOL" in texto
        assert "SUPUESTO" in texto or "INJUSTIFICADO" in texto
        assert "CONCLUSI" in texto or "INFLAD" in texto

    def test_advertencia_texto_corto(self):
        resultado = evaluar_sin_api(TESIS_CORTA)
        assert len(resultado.advertencias) > 0
        assert any("corto" in adv.lower() or "palabras" in adv.lower()
                   for adv in resultado.advertencias)

    def test_sin_advertencias_texto_largo(self):
        texto_largo = TESIS_EJEMPLO * 5  # Multiplicar para superar 500 palabras
        resultado = evaluar_sin_api(texto_largo)
        assert len(resultado.advertencias) == 0

    def test_imprimir_no_lanza_error(self, capsys):
        resultado = evaluar_sin_api(TESIS_EJEMPLO)
        resultado.imprimir()
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_resultado_tiene_escala_severidad(self):
        resultado = evaluar_sin_api(TESIS_EJEMPLO)
        assert "SEVERIDAD" in resultado.texto_evaluacion.upper()


# ---------------------------------------------------------------------------
# Tests del dataclass ResultadoEvaluacion
# ---------------------------------------------------------------------------

class TestResultadoEvaluacion:
    def test_creacion_basica(self):
        r = ResultadoEvaluacion(texto_evaluacion="Evaluación", modelo_usado="test-model")
        assert r.texto_evaluacion == "Evaluación"
        assert r.modelo_usado == "test-model"
        assert r.tokens_usados is None
        assert r.advertencias == []

    def test_creacion_con_todos_los_campos(self):
        r = ResultadoEvaluacion(
            texto_evaluacion="Evaluación completa",
            modelo_usado="gpt-4o",
            tokens_usados=1500,
            advertencias=["Advertencia de prueba"],
        )
        assert r.tokens_usados == 1500
        assert len(r.advertencias) == 1
