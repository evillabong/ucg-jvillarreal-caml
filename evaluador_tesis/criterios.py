"""
Criterios de evaluación para tesis aplicada en ciencia de datos.

Este módulo define los criterios y rúbricas que utiliza el evaluador exigente
para analizar tesis de ciencia de datos, con énfasis en debilidades reales,
supuestos injustificados y conclusiones infladas.
"""

CRITERIOS_EVALUACION = {
    "debilidades_metodologicas": {
        "descripcion": "Detectar fallas en el diseño y ejecución metodológica",
        "preguntas_guia": [
            "¿El tamaño de muestra es suficiente para las conclusiones presentadas?",
            "¿Se justifica la elección del modelo o algoritmo usado?",
            "¿Se aplica validación cruzada o técnicas adecuadas de evaluación?",
            "¿Existe fuga de datos (data leakage) entre entrenamiento y prueba?",
            "¿Se tratan adecuadamente los valores atípicos y datos faltantes?",
            "¿El proceso de preprocesamiento está correctamente documentado y justificado?",
            "¿Se separan correctamente los conjuntos de entrenamiento, validación y prueba?",
            "¿Los hiperparámetros fueron ajustados usando solo datos de entrenamiento?",
        ],
        "peso": 0.30,
    },
    "supuestos_injustificados": {
        "descripcion": "Identificar supuestos no declarados o no validados",
        "preguntas_guia": [
            "¿Se asume que los datos son representativos de la población sin demostrarlo?",
            "¿Se asume normalidad, independencia u otras propiedades estadísticas sin verificarlas?",
            "¿Se supone causalidad a partir de correlaciones observadas?",
            "¿Se asume que el modelo generaliza a contextos distintos al de entrenamiento?",
            "¿Se dan por sentadas relaciones lineales entre variables sin validación?",
            "¿Se ignoran posibles sesgos en la recolección o etiquetado de datos?",
            "¿Se asume que las variables seleccionadas son las más relevantes sin análisis de importancia?",
            "¿Se aplica un algoritmo sin verificar que sus supuestos se cumplen en los datos?",
        ],
        "peso": 0.35,
    },
    "conclusiones_infladas": {
        "descripcion": "Detectar afirmaciones que exceden lo que los resultados soportan",
        "preguntas_guia": [
            "¿Las métricas de desempeño se interpretan sin compararse con baselines simples?",
            "¿Se generaliza a poblaciones o contextos no contemplados en los datos?",
            "¿Se afirma causalidad sin un diseño experimental adecuado?",
            "¿El impacto práctico se infla más allá de lo que los datos demuestran?",
            "¿Se presentan mejoras marginales como avances significativos?",
            "¿Se omiten limitaciones relevantes del estudio?",
            "¿Las conclusiones contradicen resultados intermedios del cuerpo del trabajo?",
            "¿Se extraen recomendaciones de política o aplicación sin la evidencia suficiente?",
        ],
        "peso": 0.35,
    },
}

ESCALA_SEVERIDAD = {
    "critico": {
        "nivel": 4,
        "descripcion": "Invalida o compromete seriamente la validez del trabajo",
        "accion_requerida": "Corrección fundamental antes de poder aceptar el trabajo",
    },
    "mayor": {
        "nivel": 3,
        "descripcion": "Debilita significativamente las conclusiones o la metodología",
        "accion_requerida": "Revisión mayor y nueva validación",
    },
    "menor": {
        "nivel": 2,
        "descripcion": "Introduce imprecisión o falta de rigor sin invalidar el trabajo",
        "accion_requerida": "Corrección y aclaración requerida",
    },
    "observacion": {
        "nivel": 1,
        "descripcion": "Área de mejora que no compromete la validez central",
        "accion_requerida": "Considerar para versiones futuras o trabajos relacionados",
    },
}

ESTRUCTURA_INFORME = """
## Informe de Evaluación Exigente de Tesis en Ciencia de Datos

### 1. Resumen Ejecutivo
[Evaluación global en 3-5 oraciones. Sin elogios vacíos.]

### 2. Debilidades Metodológicas
[Lista numerada. Cada punto: descripción del problema, evidencia textual, severidad, corrección requerida.]

### 3. Supuestos Injustificados
[Lista numerada. Cada punto: supuesto detectado, por qué es problemático, qué se necesitaría para validarlo.]

### 4. Conclusiones Infladas o No Respaldadas
[Lista numerada. Cada punto: afirmación del texto, por qué excede la evidencia, reformulación honesta.]

### 5. Fortalezas Reconocidas
[Solo las genuinamente sustentadas. Máximo 3-5 puntos. Sin relleno.]

### 6. Veredicto Final
[Calificación: Rechazar / Revisión Mayor / Revisión Menor / Aceptar con Observaciones]
[Justificación de 2-3 oraciones.]
"""
