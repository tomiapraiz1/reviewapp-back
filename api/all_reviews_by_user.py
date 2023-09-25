from boto3.dynamodb.conditions import Key
from todolayer.table_layer import get_table
from todolayer.utils import handle_decimal_serialization

@handle_decimal_serialization
def handler(event, _):
    try:
        user_id = event["queryStringParameters"]["user_id"]
        if not user_id:
            raise TypeError()
    except TypeError:
        return {
            "statusCode": 400,
            "body": "user_id is required"
        }
    
    table = get_table()
    response = table.query(
        IndexName="user-index",
        KeyConditionExpression=(
            Key("user_id").eq(user_id)
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