from boto3.dynamodb.conditions import Key
from todolayer.table_layer import get_table
from todolayer.utils import handle_decimal_serialization

@handle_decimal_serialization
def handler(event, _):
    try:
        place_id = event["queryStringParameters"]["place_id"]
        if not place_id:
            raise TypeError()
    except TypeError:
        return {
            "statusCode": 400,
            "body": "place_id is required"
        }
    
    table = get_table()
    response = table.query(
        IndexName="place-index",
        KeyConditionExpression=(
            Key("place_id").eq(place_id)
        )
    )

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin" : "*",
            "Access-Control-Allow-Credentials" : "true",
            "Content-Type": "application/json"
        },
        "body": response.get("Items", [])
    }