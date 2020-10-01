from aws_cdk import (
    aws_iam as iam,
    aws_sqs as sqs,
    aws_events as events,
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
import aws_cdk.aws_events_targets as targets


class TextractPipelineCdkStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        #IAM Roles
        sqs_lambda_poller_role = iam.Role(
            self,
            id="SQSPollerRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaSQSQueueExecutionRole")

            ]
            )
        sqs_lambda_poller_role.add_to_policy( iam.PolicyStatement(
            actions=[
                "sqs:*",
                "states:*"
            ],
            effect=iam.Effect.ALLOW,
            resources=["*"]
        )
        )
        sqs_delete_role =  iam.Role(
            self,
            id="RemoveMessageFromQueueRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
                ]
        )

        sqs_delete_role.add_to_policy(
            iam.PolicyStatement(
            actions=[
                "sqs:*"
            ],
            effect=iam.Effect.ALLOW,
            resources=["*"]
        )

        )
        #define the queue
        queue = sqs.Queue(
            self, "TextractPipelineCdkQueue",
            visibility_timeout=core.Duration.seconds(300),
            
        )
        queue.grant_consume_messages(sqs_lambda_poller_role)

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

        callSQSstatement = iam.PolicyStatement(
            actions=[
                "sqs:*",
                "states:*"
            ],
            effect=iam.Effect.ALLOW,
            resources=["*"]
        )

        
        #set the lambda code paths
        layer_files = os.path.join(os.path.dirname(__file__),
        os.pardir, 'vendor')

        #define a layer for libraries
        poppler_layer = lambda_.LayerVersion(self, "poppler_layer", 
            code=lambda_.Code.from_asset(path='layers/poppler_layer'),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_7],
            description="Poppler Lambda Layer"
        
        )
        #helper layers
        textract_processor_layer = lambda_.LayerVersion(
            self,
            "HelperLayer",
            code=lambda_.Code.from_asset(path='layers/helpers'),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_7],
            description="Helper Layers"
        )
        #define functions
            
     
        #get message from sqs
        poll_sqs_queue = lambda_.Function(self, "PollSQS",
                                          runtime=lambda_.Runtime.PYTHON_3_7,
                                          handler="process_sqs.handler",
                                          code=lambda_.Code.from_asset("lambda_funcs/process_sqs"),
                                          timeout=core.Duration.seconds(300),
                                          tracing=lambda_.Tracing.ACTIVE,
                                          role=sqs_lambda_poller_role,
                                          environment={
                                            "QueueUrl": queue.queue_url,
                                            "ACCOUNT_ID": core.Aws.ACCOUNT_ID
                                          },
                                          )
           #cron to trigger lambda
        polling_rule = events.Rule(
            self, "PollSQSRule",
            schedule=events.Schedule.rate(
                core.Duration.minutes(3)
            )
        )
        
        polling_rule.add_target(target=targets.LambdaFunction(poll_sqs_queue))
        
        #process pdf
        pdf2image = _function.PythonFunction(self, "Pdf2Image",
            entry='lambda_funcs/pdf2image',
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
            entry='lambda_funcs/calltextract',
            index='calltextract.py',
            handler='lambda_handler',
            runtime=lambda_.Runtime.PYTHON_3_7,
            layers=[textract_processor_layer],
            tracing=lambda_.Tracing.ACTIVE,
            memory_size=1028,
            timeout=core.Duration.seconds(300)
        ).add_to_role_policy(
            statement=callTextractStatement
        )

        #Remove message from queue
        remove_message_from_queue = lambda_.Function(
            self,
            id="RemoveMessageFromQueue",
            handler="remove_message.handler",
            code=lambda_.Code.from_asset("lambda_funcs/remove_msg_func"),
            runtime=lambda_.Runtime.PYTHON_3_7,
            tracing=lambda_.Tracing.ACTIVE,
            timeout=core.Duration.seconds(300),
            role=sqs_delete_role,
            environment={
                "QueueUrl": queue.queue_url
            }
        )
    






    





