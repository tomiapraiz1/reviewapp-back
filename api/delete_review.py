from todolayer.table_layer import get_table
from todolayer.utils import handle_decimal_serialization

@handle_decimal_serialization
def handler(event, _):
    try:
        id = event["queryStringParameters"]["id"]
        if not id:
            raise TypeError()
    except TypeError:
        return {
            "statusCode": 400,
            "body": "id is required"
        }
    
    table = get_table()
    
    item = table.get_item(
        Key={
            "id": id
        }
    )
    if not item.get("Item"):
        return {
            "statusCode": 404,
            "body": "Review not found"
        }

    table.delete_item(
        Key={
            "id": id
        }
    )

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin" : "*",
            "Access-Control-Allow-Credentials" : "true",
            "Content-Type": "application/json"
        },
        "body": "task deleted"
    }