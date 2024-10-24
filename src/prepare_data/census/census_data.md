# Census Data
This document will record the sources for the census data used for this tool. 
## Boundaries Files
- boundaries files by census tracts (CTs) 2021 available at: https://www12-statcan-gc-ca.myaccess.library.utoronto.ca/census-recensement/alternative_alternatif.cfm?l=eng&dispext=zip&teng=lct_000b21a_e.zip&k=%20%20%20%2013089&loc=//www12.statcan.gc.ca/census-recensement/2021/geo/sip-pis/boundary-limites/files-fichiers/lct_000b21a_e.zip 

- boundaries files also available in dissemination areas (DAs) or dissemination blocks (DBs) is needed
- the CTs for Toronto starts with 535, for now the filter is from 5350001 - 5350300 for the "Central Toronto" area
- centroid calculation is done by geopandas builtin: geopandas.geometry.centroid

## Census Data