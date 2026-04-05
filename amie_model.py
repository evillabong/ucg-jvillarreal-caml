"""
amie_model.py
=============
Modelo de dominio para el dataset AMIE del Ministerio de Educación del Ecuador.

Contiene:
  - 12 clases Enum que reemplazan strings categóricos
  - Funciones normalizadoras para valores compuestos (Modalidad, Jornada, Nivel)
  - Dataclass InstitucionEducativa con tipado fuerte
  - Método from_row()    → construye una instancia desde una fila de DataFrame
  - Property features_ml → retorna dict numérico listo para sklearn
  - Método validar()     → detecta inconsistencias en los datos

Uso:
    from amie_model import InstitucionEducativa, build_dataset
    instituciones = build_dataset(df_inicio, df_fin, anio)
    X = [inst.features_ml for inst in instituciones]
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import pandas as pd
import numpy as np


# ══════════════════════════════════════════════════════════════════════════════
# 1. ENUMERADOS
# ══════════════════════════════════════════════════════════════════════════════

class Sostenimiento(Enum):
    """Tipo de financiamiento de la institución educativa."""
    FISCAL          = 1
    PARTICULAR      = 2
    FISCOMISIONAL   = 3
    MUNICIPAL       = 4
    DESCONOCIDO     = 0

    @classmethod
    def from_str(cls, valor: str) -> "Sostenimiento":
        mapa = {
            "fiscal":        cls.FISCAL,
            "particular":    cls.PARTICULAR,
            "fiscomisional": cls.FISCOMISIONAL,
            "municipal":     cls.MUNICIPAL,
        }
        return mapa.get(str(valor).strip().lower(), cls.DESCONOCIDO)


class Area(Enum):
    """Ubicación geográfica de la institución."""
    URBANA      = 1
    RURAL       = 2
    DESCONOCIDO = 0

    @classmethod
    def from_str(cls, valor: str) -> "Area":
        mapa = {
            "urbana": cls.URBANA,
            "rural":  cls.RURAL,
        }
        return mapa.get(str(valor).strip().lower(), cls.DESCONOCIDO)


class Regimen(Enum):
    """Régimen escolar según zona geográfica del Ecuador."""
    COSTA    = 1
    SIERRA   = 2
    AMAZONIA = 3   # puede aparecer en períodos anteriores
    INSULAR  = 4
    DESCONOCIDO = 0

    @classmethod
    def from_str(cls, valor: str) -> "Regimen":
        mapa = {
            "costa":    cls.COSTA,
            "sierra":   cls.SIERRA,
            "amazonia": cls.AMAZONIA,
            "amazónica":cls.AMAZONIA,
            "insular":  cls.INSULAR,
        }
        return mapa.get(str(valor).strip().lower(), cls.DESCONOCIDO)


class Jurisdiccion(Enum):
    """Jurisdicción educativa (lengua de instrucción)."""
    INTERCULTURAL          = 1
    INTERCULTURAL_BILINGUE = 2
    DESCONOCIDO            = 0

    @classmethod
    def from_str(cls, valor: str) -> "Jurisdiccion":
        v = str(valor).strip().lower()
        if "bilingü" in v or "bilingue" in v:
            return cls.INTERCULTURAL_BILINGUE
        if "intercultural" in v:
            return cls.INTERCULTURAL
        return cls.DESCONOCIDO


class ModalidadPrimaria(Enum):
    """
    Modalidad de enseñanza principal.
    Cuando el campo contiene combinaciones (ej. 'Presencial y A Distancia'),
    se toma la primera modalidad listada como primaria.
    """
    PRESENCIAL     = 1
    SEMIPRESENCIAL = 2
    DISTANCIA      = 3
    VIRTUAL        = 4
    RADIOFONICA    = 5
    EN_CASA        = 6
    OTRO           = 0

    @classmethod
    def from_str(cls, valor: str) -> "ModalidadPrimaria":
        v = str(valor).strip().lower()
        # Orden de prioridad: tomar la primera modalidad mencionada
        if v.startswith("presencial"):
            return cls.PRESENCIAL
        if v.startswith("semipresencial"):
            return cls.SEMIPRESENCIAL
        if "radiofónica" in v or "radiofonica" in v:
            return cls.RADIOFONICA
        if "en casa" in v or "educación en casa" in v:
            return cls.EN_CASA
        if "a distancia" in v:
            return cls.DISTANCIA
        if "virtual" in v or "en línea" in v or "en linea" in v:
            return cls.VIRTUAL
        if "red virtual" in v:
            return cls.VIRTUAL
        return cls.OTRO


class JornadaPrimaria(Enum):
    """
    Jornada escolar principal.
    Cuando el campo contiene combinaciones (ej. 'Matutina y Nocturna'),
    se toma la primera jornada listada como primaria.
    """
    MATUTINA   = 1
    VESPERTINA = 2
    NOCTURNA   = 3
    COMPLETA   = 4   # jornada extendida / todo el día
    DESCONOCIDO = 0

    @classmethod
    def from_str(cls, valor: str) -> "JornadaPrimaria":
        v = str(valor).strip().lower()
        if v.startswith("matutina"):
            return cls.MATUTINA
        if v.startswith("vespertina"):
            return cls.VESPERTINA
        if v.startswith("nocturna"):
            return cls.NOCTURNA
        if "completa" in v or "doble" in v:
            return cls.COMPLETA
        return cls.DESCONOCIDO


class NivelEducacion(Enum):
    """
    Nivel educativo principal de la institución.
    Valores combinados se agrupan en la categoría más alta presente.
    """
    INICIAL       = 1
    BASICA        = 2
    BACHILLERATO  = 3
    MULTI_NIVEL   = 4   # combina dos o más niveles
    OTRO          = 0   # Alfabetización, Artesanal, etc.

    @classmethod
    def from_str(cls, valor: str) -> "NivelEducacion":
        v = str(valor).strip().lower()
        tiene_bach  = "bachillerato" in v or "bach" in v
        tiene_egb   = "básica" in v or "basica" in v or "egb" in v
        tiene_ini   = "inicial" in v
        tiene_otro  = "alfabetización" in v or "alfabetizacion" in v \
                      or "artesanal" in v or "artesanal" in v

        combinados = sum([tiene_bach, tiene_egb, tiene_ini, tiene_otro])

        if combinados > 1:
            return cls.MULTI_NIVEL
        if tiene_bach:
            return cls.BACHILLERATO
        if tiene_egb:
            return cls.BASICA
        if tiene_ini:
            return cls.INICIAL
        return cls.OTRO


class TipoEducacion(Enum):
    """Tipo de oferta educativa."""
    ORDINARIA              = 1
    ESPECIAL               = 2
    ESCOLARIDAD_INCONCLUSA = 3
    DESCONOCIDO            = 0

    @classmethod
    def from_str(cls, valor: str) -> "TipoEducacion":
        v = str(valor).strip().lower()
        if "ordinaria" in v:
            return cls.ORDINARIA
        if "especial" in v:
            return cls.ESPECIAL
        if "inconclusa" in v:
            return cls.ESCOLARIDAD_INCONCLUSA
        return cls.DESCONOCIDO


class TenenciaEdificio(Enum):
    """
    Situación legal del inmueble donde funciona la institución.
    Agrupado en tres categorías para reducir dispersión.
    """
    PROPIO      = 1   # "Propio"
    NO_PROPIO   = 2   # Arriendo, Prestado, Comodato, Cesión de derechos
    DESCONOCIDO = 0   # No conoce, Invasión, o nulo

    @classmethod
    def from_str(cls, valor: str) -> "TenenciaEdificio":
        v = str(valor).strip().lower()
        if v == "propio":
            return cls.PROPIO
        if v in ("arriendo", "prestado", "comodato",
                 "cesión de derechos", "cesion de derechos"):
            return cls.NO_PROPIO
        return cls.DESCONOCIDO


class AccesoEdificio(Enum):
    """Tipo de vía de acceso a la institución."""
    TERRESTRE   = 1
    FLUVIAL     = 2
    AEREA       = 3
    DESCONOCIDO = 0

    @classmethod
    def from_str(cls, valor: str) -> "AccesoEdificio":
        mapa = {
            "terrestre": cls.TERRESTRE,
            "fluvial":   cls.FLUVIAL,
            "aérea":     cls.AEREA,
            "aerea":     cls.AEREA,
        }
        return mapa.get(str(valor).strip().lower(), cls.DESCONOCIDO)


class ZonaAdministrativa(Enum):
    """
    Zona de planificación administrativa del Ecuador (SENPLADES).
    El valor entero del Enum se usa directamente como feature numérica.
    Zona en Estudio = 0 (sin zona asignada aún).
    """
    ZONA_EN_ESTUDIO = 0
    ZONA_1 = 1   # Esmeraldas, Carchi, Imbabura, Sucumbíos
    ZONA_2 = 2   # Pichincha (excl. Quito), Napo, Orellana
    ZONA_3 = 3   # Cotopaxi, Tungurahua, Chimborazo, Pastaza
    ZONA_4 = 4   # Manabí, Santo Domingo de los Tsáchilas
    ZONA_5 = 5   # Santa Elena, Guayas (excl. Guayaquil), Bolívar, Los Ríos, Galápagos
    ZONA_6 = 6   # Azuay, Cañar, Morona Santiago
    ZONA_7 = 7   # El Oro, Loja, Zamora Chinchipe
    ZONA_8 = 8   # Guayaquil, Samborondón, Durán
    ZONA_9 = 9   # Quito (Distrito Metropolitano)

    @classmethod
    def from_str(cls, valor: str) -> "ZonaAdministrativa":
        v = str(valor).strip().lower().replace(" ", "_")
        mapa = {
            "zona_1": cls.ZONA_1, "zona_2": cls.ZONA_2,
            "zona_3": cls.ZONA_3, "zona_4": cls.ZONA_4,
            "zona_5": cls.ZONA_5, "zona_6": cls.ZONA_6,
            "zona_7": cls.ZONA_7, "zona_8": cls.ZONA_8,
            "zona_9": cls.ZONA_9,
            "zona_en_estudio": cls.ZONA_EN_ESTUDIO,
        }
        return mapa.get(v, cls.ZONA_EN_ESTUDIO)


class NivelDesercion(Enum):
    """Variable objetivo del modelo de clasificación."""
    BAJO  = 0   # tasa < 5%
    MEDIO = 1   # 5% <= tasa <= 15%
    ALTO  = 2   # tasa > 15%

    @classmethod
    def from_tasa(cls, tasa: float) -> "NivelDesercion":
        if tasa < 0.05:
            return cls.BAJO
        if tasa <= 0.15:
            return cls.MEDIO
        return cls.ALTO

    def label(self) -> str:
        return self.name.capitalize()


# ══════════════════════════════════════════════════════════════════════════════
# 2. DATACLASS — MODELO DE DOMINIO
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class InstitucionEducativa:
    """
    Representa una institución educativa en un año lectivo específico.
    Combina datos del archivo Inicio y Fin del AMIE.

    Atributos de identificación (no usados en ML):
        amie, anio_lectivo, provincia

    Atributos categóricos (Enum → valor entero en features_ml):
        zona, sostenimiento, area, regimen, jurisdiccion,
        modalidad, jornada, nivel_educacion, tipo_educacion,
        acceso_edificio, tenencia_edificio

    Atributos numéricos:
        total_docentes, total_administrativos,
        est_inicio, est_fin,
        ratio_doc_est, ratio_genero_est

    Atributos derivados (target):
        tasa_desercion, nivel_desercion
    """

    # ── Identificación ────────────────────────────────────────────────────────
    amie:            str
    anio_lectivo:    str
    provincia:       str

    # ── Categóricos tipados ───────────────────────────────────────────────────
    zona:             ZonaAdministrativa
    sostenimiento:    Sostenimiento
    area:             Area
    regimen:          Regimen
    jurisdiccion:     Jurisdiccion
    modalidad:        ModalidadPrimaria
    jornada:          JornadaPrimaria
    nivel_educacion:  NivelEducacion
    tipo_educacion:   TipoEducacion
    acceso_edificio:  AccesoEdificio
    tenencia_edificio: TenenciaEdificio

    # ── Numéricos ─────────────────────────────────────────────────────────────
    total_docentes:       float
    total_administrativos: float
    est_inicio:           float
    est_fin:              float
    ratio_doc_est:        float   # docentes por estudiante
    ratio_genero_est:     float   # femenino / total (0–1)

    # ── Target ───────────────────────────────────────────────────────────────
    tasa_desercion:  float
    nivel_desercion: NivelDesercion

    # ── Propiedades ───────────────────────────────────────────────────────────

    @property
    def features_ml(self) -> dict:
        """
        Retorna un diccionario con todas las features en formato numérico,
        listo para construir un DataFrame de entrada a sklearn.
        Los Enums se representan por su valor entero (.value).
        """
        return {
            # Categóricas (valor entero del Enum)
            "zona":              self.zona.value,
            "sostenimiento":     self.sostenimiento.value,
            "area":              self.area.value,
            "regimen":           self.regimen.value,
            "jurisdiccion":      self.jurisdiccion.value,
            "modalidad":         self.modalidad.value,
            "jornada":           self.jornada.value,
            "nivel_educacion":   self.nivel_educacion.value,
            "tipo_educacion":    self.tipo_educacion.value,
            "acceso_edificio":   self.acceso_edificio.value,
            "tenencia_edificio": self.tenencia_edificio.value,
            # Numéricas
            "total_docentes":        self.total_docentes,
            "total_administrativos": self.total_administrativos,
            "est_inicio":            self.est_inicio,
            "ratio_doc_est":         self.ratio_doc_est,
            "ratio_genero_est":      self.ratio_genero_est,
        }

    @property
    def target_ml(self) -> int:
        """Valor entero del nivel de deserción (para sklearn)."""
        return self.nivel_desercion.value

    @property
    def target_label(self) -> str:
        """Etiqueta de texto del nivel de deserción."""
        return self.nivel_desercion.label()

    # ── Validación ────────────────────────────────────────────────────────────

    def validar(self) -> list[str]:
        """
        Detecta inconsistencias en los datos.
        Retorna lista de mensajes de error (vacía si todo está OK).
        """
        errores = []

        if self.est_inicio <= 0:
            errores.append(f"[{self.amie}] est_inicio <= 0")

        if self.est_fin < 0:
            errores.append(f"[{self.amie}] est_fin negativo")

        if not (0.0 <= self.tasa_desercion <= 1.0):
            errores.append(f"[{self.amie}] tasa_desercion fuera de [0,1]: {self.tasa_desercion:.4f}")

        if self.total_docentes < 0:
            errores.append(f"[{self.amie}] total_docentes negativo")

        if self.zona == ZonaAdministrativa.ZONA_EN_ESTUDIO:
            errores.append(f"[{self.amie}] zona no asignada (Zona en Estudio)")

        if self.sostenimiento == Sostenimiento.DESCONOCIDO:
            errores.append(f"[{self.amie}] sostenimiento desconocido")

        return errores

    # ── Constructor desde fila de DataFrame ──────────────────────────────────

    @classmethod
    def from_row(
        cls,
        row_inicio: pd.Series,
        est_fin: float,
        anio_lectivo: str,
    ) -> Optional["InstitucionEducativa"]:
        """
        Construye una InstitucionEducativa desde una fila del DataFrame Inicio
        y el total de estudiantes al Fin de año.

        Retorna None si los datos mínimos no están disponibles.
        """
        def get(campo: str, default="") -> str:
            """Obtiene el valor de una columna de forma segura."""
            val = row_inicio.get(campo, default)
            return "" if pd.isna(val) else str(val).strip()

        def get_num(campo: str, default: float = 0.0) -> float:
            """Obtiene un valor numérico de forma segura."""
            val = row_inicio.get(campo, default)
            try:
                return float(val)
            except (ValueError, TypeError):
                return default

        # Datos mínimos necesarios
        amie      = get("AMIE")
        est_inicio = get_num("Total Estudiantes")

        if not amie or est_inicio < 5:
            return None

        # Tasa de deserción
        est_fin_val    = max(0.0, float(est_fin)) if not pd.isna(est_fin) else 0.0
        tasa           = max(0.0, min(1.0, (est_inicio - est_fin_val) / est_inicio))
        nivel_des      = NivelDesercion.from_tasa(tasa)

        # Ratio docente / estudiante
        docentes = get_num("Total Docentes")
        ratio_doc = docentes / est_inicio if est_inicio > 0 else 0.0

        # Ratio de género estudiantes
        fem = get_num("Estudiantes Femenino")
        total = est_inicio if est_inicio > 0 else 1.0
        ratio_gen = fem / total

        return cls(
            amie             = amie,
            anio_lectivo     = anio_lectivo,
            provincia        = get("Provincia").upper(),

            zona             = ZonaAdministrativa.from_str(get("Zona")),
            sostenimiento    = Sostenimiento.from_str(get("Sostenimiento")),
            area             = Area.from_str(get("Área") or get("Area")),
            regimen          = Regimen.from_str(get("Régimen Escolar") or get("Regimen Escolar")),
            jurisdiccion     = Jurisdiccion.from_str(get("Jurisdicción") or get("Jurisdiccion")),
            modalidad        = ModalidadPrimaria.from_str(get("Modalidad")),
            jornada          = JornadaPrimaria.from_str(get("Jornada")),
            nivel_educacion  = NivelEducacion.from_str(get("Nivel Educación") or get("Nivel Educacion")),
            tipo_educacion   = TipoEducacion.from_str(get("Tipo Educación") or get("Tipo Educacion")),
            acceso_edificio  = AccesoEdificio.from_str(get("Acceso Edificio")),
            tenencia_edificio= TenenciaEdificio.from_str(get("Tenencia Inmueble Edificio")),

            total_docentes        = docentes,
            total_administrativos = get_num("Total Administrativos"),
            est_inicio            = est_inicio,
            est_fin               = est_fin_val,
            ratio_doc_est         = ratio_doc,
            ratio_genero_est      = ratio_gen,

            tasa_desercion   = tasa,
            nivel_desercion  = nivel_des,
        )

    def __repr__(self) -> str:
        return (
            f"InstitucionEducativa("
            f"amie={self.amie!r}, anio={self.anio_lectivo!r}, "
            f"provincia={self.provincia!r}, "
            f"area={self.area.name}, sostenimiento={self.sostenimiento.name}, "
            f"tasa={self.tasa_desercion:.2%}, nivel={self.nivel_desercion.name})"
        )


# ══════════════════════════════════════════════════════════════════════════════
# 3. FUNCIÓN DE CONSTRUCCIÓN DEL DATASET
# ══════════════════════════════════════════════════════════════════════════════

def build_dataset(
    df_inicio: pd.DataFrame,
    df_fin: pd.DataFrame,
    anio_lectivo: str,
    col_est: str = "Total Estudiantes",
) -> list[InstitucionEducativa]:
    """
    Construye una lista de InstitucionEducativa combinando Inicio y Fin.

    Args:
        df_inicio:    DataFrame del archivo Inicio del año lectivo
        df_fin:       DataFrame del archivo Fin del año lectivo
        anio_lectivo: Etiqueta del año (ej. '2023-2024')
        col_est:      Nombre de la columna Total Estudiantes

    Returns:
        Lista de InstitucionEducativa válidas (sin nulos críticos)
    """
    # Normalizar columnas
    df_inicio = df_inicio.copy()
    df_fin    = df_fin.copy()
    df_inicio.columns = df_inicio.columns.str.strip()
    df_fin.columns    = df_fin.columns.str.strip()

    # Buscar columna de estudiantes si difiere del nombre esperado
    def encontrar_col_est(df: pd.DataFrame) -> str:
        if col_est in df.columns:
            return col_est
        candidatos = [c for c in df.columns
                      if "total" in c.lower() and "estud" in c.lower()]
        return candidatos[0] if candidatos else col_est

    col_i = encontrar_col_est(df_inicio)
    col_f = encontrar_col_est(df_fin)

    # Preparar lookup AMIE → Est_Fin
    df_fin["AMIE"] = df_fin["AMIE"].astype(str).str.strip()
    fin_lookup = df_fin.set_index("AMIE")[col_f].to_dict()

    # Construir instancias
    instituciones: list[InstitucionEducativa] = []
    errores_total: list[str] = []

    for _, row in df_inicio.iterrows():
        amie    = str(row.get("AMIE", "")).strip()
        est_fin = fin_lookup.get(amie, np.nan)

        inst = InstitucionEducativa.from_row(row, est_fin, anio_lectivo)
        if inst is None:
            continue

        errores = inst.validar()
        if errores:
            errores_total.extend(errores)
            continue   # descartar instancias inválidas

        instituciones.append(inst)

    if errores_total:
        print(f"  [validación] {len(errores_total)} advertencias descartadas en {anio_lectivo}")

    return instituciones


def instituciones_to_dataframe(instituciones: list[InstitucionEducativa]) -> pd.DataFrame:
    """
    Convierte una lista de InstitucionEducativa en un DataFrame con:
      - Columnas de features_ml (numéricas, listas para sklearn)
      - Columna 'target'       (int: NivelDesercion.value)
      - Columna 'target_label' (str: 'Bajo'/'Medio'/'Alto')
      - Columnas de identificación (amie, anio_lectivo, provincia)
    """
    registros = []
    for inst in instituciones:
        r = inst.features_ml
        r["amie"]         = inst.amie
        r["anio_lectivo"] = inst.anio_lectivo
        r["provincia"]    = inst.provincia
        r["tasa_desercion"]  = inst.tasa_desercion
        r["target"]          = inst.target_ml
        r["target_label"]    = inst.target_label
        registros.append(r)

    return pd.DataFrame(registros)
