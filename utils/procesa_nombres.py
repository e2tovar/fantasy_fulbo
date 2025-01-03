from typing import List, Dict
import re


def pre_procesa_nombres(excel_names: List, db_names: Dict):
    # Nombres a minúscula y quitamos acentos. Al excel y al db
    excel_names = [
        name.lower().replace('á', 'a').replace('ã', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
        for name in excel_names]
    db_names = {
        name.lower().replace('á', 'a').replace('ã', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u'): id
        for name, id in db_names.items()}
    # Eliminamos los nombres comunes del grupo para que el peso recaiga en el apellido/apodo
    comunes = ['andres', 'gabriel']

    posibles_mapeos = {
        'danielito': 'daniel',
        'francisco': 'frank',
        'roymer': 'roy',
        'arturo suarez': 'chino'
    }

    # aplica mapeos con replace
    for key, value in posibles_mapeos.items():
        excel_names = [name.replace(key, value) for name in excel_names]
        db_names = {name.replace(key, value): id for name, id in db_names.items()}

    for comun in comunes:
        excel_names = [name.replace(comun, '') for name in excel_names]
        db_names = {name.replace(comun, ''): id for name, id in db_names.items()}

    # Eliminamos articulos
    excel_names = [name.replace('de ', '') for name in excel_names]
    db_names = {name.replace('de ', ''): id for name, id in db_names.items()}

    # Eliminamos iniciales. Nos quedamos con la primera palabra del resultado
    excel_names = [re.sub(r'^[a-z]\.', '', name).split()[0] for name in excel_names]
    db_names = {re.sub(r'^[a-z]\.', '', name).split()[0]: id for name, id in db_names.items()}


    return excel_names, db_names
