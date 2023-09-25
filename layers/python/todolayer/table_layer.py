import os, boto3
from uuid import uuid4

class Review(object):
    def __init__(self, user_id, place_id, rating, price, review, date):
        self.id = str(uuid4())
        self.user_id = user_id
        self.place_id = place_id
        self.rating = rating
        self.price = price
        self.review = review
        self.date = date

def get_table():
    table_name = os.environ.get("REVIEWS_TABLE_NAME")
    return boto3.resource("dynamodb").Table(table_name)