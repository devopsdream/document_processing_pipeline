import boto3
import json
import logging
import os
from botocore.exceptions import ClientError
from urllib.parse import unquote_plus
log = logging.getLogger()
log.setLevel(logging.INFO)

sqs = boto3.client('sqs')
step_functions = boto3.client('stepfunctions')

QUEUE_URL = os.getenv('QueueUrl')
ACCOUNT_ID = os.getenv('ACCOUNT_ID')
MAX_DOCUMENTS = 1
LONG_POLL  = 20

def start_document_processing(messages):
    payload = messages
    input = {}
    if "Messages" in payload:
        message = {}
        message_handle = payload['Messages'][0]['ReceiptHandle']
        message["body"] = json.loads(payload['Messages'][0]['Body'])
        bucket_name = message["body"]["Records"][0]['s3']['bucket']['name']
        object_name = unquote_plus(message["body"]["Records"][0]['s3']['object']['key'])
        input = {
            "input": {
                "bucket_name": bucket_name, 
                "object_name": object_name, 
                "message_id": str(message_handle)
            },
            "output": {}
        }     
    else:
        log.info("No messages to retrieve")
        return []

    try:
        log.info("Starting  Stepfunction with input: {}".format(json.dumps(input)))
        response = step_functions.start_execution(
            stateMachineArn="arn:aws:states:us-east-1:{}:stateMachine:document_processing_state_machine".format(ACCOUNT_ID),
            input=json.dumps(input)
        )
    except ClientError as error:
        raise error
    else:
        return response

def recieve_messages(queue, max_number, wait_time):
    try:
        messages = sqs.receive_message(
            QueueUrl=queue,
            MaxNumberOfMessages=max_number,
            WaitTimeSeconds=wait_time,
            MessageAttributeNames=['All']
        )
        log.info("Messages retrived is: {}".format(messages))
    except ClientError as error:
        log.exception("Send messages failed to queue: %s", queue)
        raise error
    else:
        start_document_processing(messages=messages)
def handler(event, context):
    log.info(event)
    messages = recieve_messages(queue=QUEUE_URL, max_number=MAX_DOCUMENTS,  wait_time=LONG_POLL)
    log.info(messages)
    return event