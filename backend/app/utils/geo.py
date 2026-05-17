"""Helpers geoespaciais — offset de privacidade e geometrias PostGIS.

Algoritmo de offset:
- Sorteia bearing uniforme em [0, 360°) e distância em [min, min*1.3].
- Aplica deslocamento na coordenada original via geopy.distance.
- Persistido UMA VEZ (lat_pub/lng_pub no model) — não recalcular a cada leitura.
"""

from __future__ import annotations

import math
import random
from typing import Literal

from geopy.distance import distance as geopy_distance
from sqlalchemy import func
from sqlalchemy.sql.elements import ColumnElement

from app.core.config import settings


Territorio = Literal["urbano", "rural"]


def offset_minimo_m(territorio: Territorio) -> int:
    return (
        settings.GEO_OFFSET_URBANO_M
        if territorio == "urbano"
        else settings.GEO_OFFSET_RURAL_M
    )


def aplicar_offset_privacidade(
    lat: float,
    lng: float,
    *,
    territorio: Territorio,
) -> tuple[float, float, float]:
    """Retorna (lat_pub, lng_pub, offset_metros_aplicados).

    Distância sorteada entre [min, min*1.3] para evitar que o ponto público
    fique sempre exatamente no mesmo anel — dificultando reverter o offset.
    """
    base = offset_minimo_m(territorio)
    distancia_m = random.uniform(base, base * 1.3)
    bearing_deg = random.uniform(0, 360)

    destino = geopy_distance(meters=distancia_m).destination(
        point=(lat, lng), bearing=bearing_deg
    )
    return destino.latitude, destino.longitude, distancia_m


def make_point_wkt(lat: float, lng: float, *, srid: int | None = None) -> str:
    """WKT POINT no formato `SRID=4326;POINT(lng lat)`."""
    s = srid or settings.GEO_DEFAULT_SRID
    return f"SRID={s};POINT({lng} {lat})"


def st_dwithin_geography(
    geom_column: ColumnElement,
    lat: float,
    lng: float,
    raio_km: float,
) -> ColumnElement:
    """Cláusula PostGIS para buscar pontos dentro de `raio_km` em metros geodésicos."""
    raio_m = raio_km * 1000
    ponto = func.ST_SetSRID(func.ST_MakePoint(lng, lat), settings.GEO_DEFAULT_SRID)
    return func.ST_DWithin(
        func.ST_Transform(geom_column, 4326).cast(_GEOGRAPHY),
        ponto.cast(_GEOGRAPHY),
        raio_m,
    )


# Sentinela para cast — evita import circular do tipo Geography
from sqlalchemy.types import UserDefinedType


class _GeographyType(UserDefinedType):
    cache_ok = True

    def get_col_spec(self, **_kw) -> str:
        return "geography"


_GEOGRAPHY = _GeographyType()


def distancia_haversine_km(
    lat1: float, lng1: float, lat2: float, lng2: float
) -> float:
    """Distância em km entre dois pontos via fórmula de Haversine."""
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def territorio_de(cidade: str, uf: str) -> Territorio:
    """Classifica território cidade/UF como urbano ou rural.

    No MVP: tudo o que cair em capital ou cidade > 100k habitantes é urbano.
    A tabela IBGE é injetada/configurada em produção; aqui assume urbano por padrão
    para evitar exposição (offset maior é mais conservador).
    """
    _ = (cidade, uf)
    return "urbano"
