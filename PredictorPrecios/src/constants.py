columns = {
    'postingId': 'posting_id',
    'priceOperationTypes[0].operationType.name': 'status',
    'priceOperationTypes[0].prices[0].formattedAmount': 'price',                        # Valor 
    'priceOperationTypes[0].prices[0].currency': 'currency_price',                      # Moneda
    'expenses.formattedAmount': 'expenses',                                             # Valor expensas
    'expenses.currency': 'currency_expenses',                                           # Modeda expensas
    'mainFeatures.1000019.value': 'disposition',                                        # Disposicion (Frente/Interno)
    'mainFeatures.CFT100.value': 'm2_total',                                            # m2 totales
    'mainFeatures.CFT101.value': 'm2_covered',                                          # m2 cubiertos
    'mainFeatures.CFT1.value': 'room',                                                  # Cant.Ambientes
    'mainFeatures.CFT2.value': 'bedroom',                                               # Cant.Dormitorio
    'mainFeatures.CFT3.value': 'bathroom',                                              # Cant.Baños
    'mainFeatures.CFT4.value': 'toilette',                                              # Cant.Toilettes
    'mainFeatures.CFT5.value': 'antiquity',                                             # Antiguedad
    'mainFeatures.CFT7.value': 'garage',                                                # Cant.Cocheras
    'publisher.publisherId': 'publisher_id',                                            # id publicacion
    'publisher.name': 'publisher_name',                                                 # Nombre Inmoviliaria
    'realEstateType.name': 'type',                                                      # Tipo (Depto/Casa/etc)
    'postingLocation.location.name':'barrio',                                           # Barrio
    'mainFeatures.1000029.value':'orientation',                                         # Orientacion(NE/NO/N/etc)
    'postingLocation.postingGeolocation.geolocation.latitude': 'geo_latitude',          # Latitud
    'postingLocation.postingGeolocation.geolocation.longitude': 'geo_longitude',        # Longitud
}
