import json
import pytest

from aws_cdk import core
from textract-pipeline-cdk.textract_pipeline_cdk_stack import TextractPipelineCdkStack


def get_template():
    app = core.App()
    TextractPipelineCdkStack(app, "textract-pipeline-cdk")
    return json.dumps(app.synth().get_stack("textract-pipeline-cdk").template)


def test_sqs_queue_created():
    assert("AWS::SQS::Queue" in get_template())


def test_sns_topic_created():
    assert("AWS::SNS::Topic" in get_template())
