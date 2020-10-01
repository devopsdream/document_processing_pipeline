import os
import json
import logging
import boto3
from botocore.exceptions import ClientError

log = logging.getLogger()
log.setLevel(logging.INFO)

sqs = boto3.client('sqs')

QUEUE_URL = os.getenv('QueueUrl')
def delete_message_from_queue(receipt_handle):
    try:
        response = sqs.delete_message(
            QueueUrl=QUEUE_URL,
            ReceiptHandle=str(receipt_handle)
        )
    except ClientError as error:
        raise error
    else:
        return response
    
def handler(event,context):
    log.info(json.dumps(json.dumps(event)))
    receipt_handle = event["message_id"]
    delete_message_from_queue(receipt_handle=receipt_handle)
    return {"status": "complete"}