from aws_cdk import (
    aws_iam as iam,
    aws_sqs as sqs,
    core,
)
from cdk_chalice import Chalice
import os
from aws_cdk import aws_lambda_python as _function
from aws_cdk import aws_lambda as lambda_
from aws_cdk import  aws_lambda_event_sources as source
from aws_cdk import aws_s3 as s3
import aws_cdk.aws_stepfunctions as sfn
import aws_cdk.aws_stepfunctions_tasks as tasks


class TextractPipelineCdkStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        #from existing bucket
        docs_bucket = s3.Bucket.from_bucket_attributes(
            self,
            "DocBucket",
            bucket_name="tonouma-266014969233-docs")

        #define the queue
        queue = sqs.Queue(
            self, "TextractPipelineCdkQueue",
            visibility_timeout=core.Duration.seconds(300),
            
        )

        #lamba policy
        pdf2imageStatement = iam.PolicyStatement(
            actions=["s3:*"],
            effect=iam.Effect.ALLOW,
            resources=["*"]

        )
        callTextractStatement = iam.PolicyStatement(
            actions=[
                "textract:*",
                "s3:*"
                ],
            effect=iam.Effect.ALLOW,
            resources=["*"]
        )

        

        #set the lambda code paths
        code_dir = os.path.join(os.path.dirname(__file__),
                                          os.pardir, 'pdf2image')
        layer_files = os.path.join(os.path.dirname(__file__),
        os.pardir, 'vendor')

        #define a layer for libraries
        poppler_layer = lambda_.LayerVersion(self, "poppler_layer", 
            code=lambda_.Code.from_asset(path=layer_files),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_7],
            description="Poppler Lambda Layer"
        
        )
        #define functions
        #get message from sqs
        get_messages_from_sqs = _function.PythonFunction(
            self,
            id="GetSQSMessage",
            entry='./process_sqs',
            index='process_sqs.py',
            handler='lambda_handler',
            runtime=lambda_.Runtime.PYTHON_3_7,
            tracing=lambda_.Tracing.ACTIVE,
            events=[source.SqsEventSource(queue=queue)]
        )
        #process pdf
        pdf2image = _function.PythonFunction(self, "Pdf2Image",
            entry=code_dir,
            index='process_images.py',
            handler='lambda_handler',
            runtime=lambda_.Runtime.PYTHON_3_7,
            layers=[poppler_layer],
            tracing=lambda_.Tracing.ACTIVE,
            memory_size=1028,
            timeout=core.Duration.seconds(300)
        ).add_to_role_policy(
            statement=pdf2imageStatement
        )

        #call texract
        callTextract = _function.PythonFunction(self, "CallTextract",
            entry='./calltextract',
            index='calltextract.py',
            handler='lambda_handler',
            runtime=lambda_.Runtime.PYTHON_3_7,
            layers=[poppler_layer],
            tracing=lambda_.Tracing.ACTIVE,
            memory_size=1028,
            timeout=core.Duration.seconds(300)
        ).add_to_role_policy(
            statement=callTextractStatement
        )







    





