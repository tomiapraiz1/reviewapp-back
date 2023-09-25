from todolayer.table_layer import Review
from todolayer.table_layer import get_table
import time, json

def handler(event, _):
    try:
        item = json.loads(event["body"])

        review = Review(
            user_id=str(item["user_id"]),
            place_id=str(item["place_id"]),
            rating=int(item["rating"]),
            price=str(item["price"]),
            review=str(item["review"]),
            date=int(time.time())
        )
    except (TypeError, KeyError):
        return {
            "statusCode": 400,
            "body": "user_id, place_id, rating, price, and review are required"
        }
    
    print(vars(review))

    table = get_table()
    table.put_item(
        Item=vars(review)
    )

    return {
        "statusCode": 201,
        "headers": {
            "Access-Control-Allow-Origin" : "*",
            "Access-Control-Allow-Credentials" : "true",
            "Content-Type": "application/json"
        },
        "body": "task created"
    }