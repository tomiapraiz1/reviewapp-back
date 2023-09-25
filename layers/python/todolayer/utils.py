import json
from decimal import Decimal

# Función para convertir objetos Decimal a tipos nativos de Python
def decimal_default(obj):
    if isinstance(obj, Decimal):
        return int(obj)
    raise TypeError

# Decorador para manejar la serialización Decimal en respuesta
def handle_decimal_serialization(handler_function):
    def wrapper(event, context):
        result = handler_function(event, context)
        if "body" in result:
            result["body"] = json.dumps(result["body"], default=decimal_default)
        return result
    return wrapper