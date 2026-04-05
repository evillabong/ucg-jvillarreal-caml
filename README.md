# Evaluador Exigente de Tesis en Ciencia de Datos

Herramienta para evaluar tesis aplicadas en ciencia de datos con criterio riguroso,
priorizando la detección de **debilidades reales**, **supuestos injustificados** y
**conclusiones infladas**.

Proyecto de Conceptos y Aplicaciones de Machine Learning (CAML).

---

## ¿Qué hace este evaluador?

El evaluador aplica tres dimensiones críticas con sus respectivos pesos:

| Dimensión | Peso | Descripción |
|-----------|------|-------------|
| **Debilidades metodológicas** | 30% | Fallas en diseño, preprocesamiento, validación de modelos |
| **Supuestos injustificados** | 35% | Supuestos no declarados o no validados sobre datos y modelos |
| **Conclusiones infladas** | 35% | Afirmaciones que exceden lo que los datos demuestran |

### Escala de severidad

- **Crítico**: Invalida o compromete seriamente la validez del trabajo
- **Mayor**: Debilita significativamente las conclusiones o la metodología
- **Menor**: Introduce imprecisión o falta de rigor sin invalidar el trabajo
- **Observación**: Área de mejora que no compromete la validez central

---

## Estructura del proyecto

```
evaluador_tesis/
├── __init__.py       # API pública del paquete
├── criterios.py      # Criterios, pesos y plantilla de informe
├── prompt.py         # System prompt y plantilla de usuario para LLM
└── evaluador.py      # Funciones de evaluación (OpenAI, Anthropic, manual)

tests/
└── test_evaluador.py # Suite de pruebas unitarias

evaluar.py            # CLI para ejecutar evaluaciones desde la línea de comandos
requirements.txt      # Dependencias opcionales del proyecto
```

---

## Uso

### Modo manual (sin API externa)

Genera una guía de evaluación estructurada con todas las preguntas críticas:

```bash
python evaluar.py --texto mi_tesis.txt --proveedor manual
```

### Con OpenAI GPT-4o

```bash
export OPENAI_API_KEY="tu-api-key"
python evaluar.py --texto mi_tesis.txt --proveedor openai
```

### Con Anthropic Claude

```bash
export ANTHROPIC_API_KEY="tu-api-key"
python evaluar.py --texto mi_tesis.txt --proveedor anthropic
```

### Guardar la evaluación en un archivo

```bash
python evaluar.py --texto mi_tesis.txt --salida evaluacion.md
```

### Uso programático

```python
from evaluador_tesis import evaluar_con_openai, evaluar_sin_api

# Sin API: obtén la guía de evaluación manual
resultado = evaluar_sin_api(texto_tesis)
resultado.imprimir()

# Con OpenAI (requiere OPENAI_API_KEY en el entorno)
resultado = evaluar_con_openai(texto_tesis, modelo="gpt-4o")
resultado.imprimir()
```

---

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/evillabong/ucg-jvillarreal-caml.git
cd ucg-jvillarreal-caml

# Instalar dependencias opcionales para uso con LLM
pip install -r requirements.txt
```

---

## Ejecutar las pruebas

```bash
pip install pytest
python -m pytest tests/ -v
```

---

## Ejemplo de debilidades que detecta

El evaluador está diseñado para detectar problemas comunes en tesis de ciencia de datos:

- **Data leakage**: uso de datos de prueba durante el entrenamiento
- **Accuracy en clases desbalanceadas**: reportar accuracy como métrica principal cuando la clase positiva es rara
- **Overfitting no detectado**: alta métrica en prueba sin validación cruzada
- **Causalidad a partir de correlación**: "el modelo X *causa* Y"
- **Generalización injustificada**: resultados de una ciudad/hospital/empresa presentados como universales
- **Ausencia de baselines**: no comparar con modelos simples (regresión logística, media, etc.)
- **Hiperparámetros ajustados con datos de prueba**: inflación artificial del desempeño reportado
