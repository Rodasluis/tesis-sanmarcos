# Procedencia de los datos

Generado por `codigo/01_descarga.py`. No editar a mano.

- Descargado: 2026-10-05
- Fuente: API del Banco Mundial, `api.worldbank.org/v2`
- Licencia: CC BY 4.0 (World Bank Open Data)
- Países (17): PER, BOL, ECU, COL, CHL, BRA, ARG, URY, PRY, MEX, CRI, PAN, DOM, GTM, HND, SLV, NIC
- Periodo: 2010–2023

## Indicadores

| Código | Variable | Observaciones con valor |
|---|---|---|
| `SL.GDP.PCAP.EM.KD` | productividad | 238 de 238 |
| `IT.NET.USER.ZS` | internet | 238 de 238 |
| `SE.XPD.TOTL.GD.ZS` | gasto_educacion | 220 de 238 |
| `SL.UEM.TOTL.ZS` | desempleo | 238 de 238 |
| `NY.GDP.PCAP.KD` | pbi_per_capita | 238 de 238 |

## Cómo volver a bajarlos

```
uv run python codigo/01_descarga.py
```

El Banco Mundial revisa sus series hacia atrás sin avisar, así que una
descarga nueva puede no coincidir con esta. Por eso la fecha está arriba.
