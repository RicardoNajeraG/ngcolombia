from .gas_data_manager import ngDataManager as _ngDataManager

_APIKEY = 'c2JfcHVibGlzaGFibGVfb2xfYURBY25IeEZsZG5kU2lvS29QZ19KSFYyT0ZoSw=='

reporte_cromatografias = _ngDataManager(apikey=_APIKEY)

__all__ = ['reporte_cromatografias']
