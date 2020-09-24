#!/usr/bin/env python3

from aws_cdk import core

from textract_pipeline_cdk.textract_pipeline_cdk_stack import TextractPipelineCdkStack


app = core.App()
TextractPipelineCdkStack(app, "textract-pipeline-cdk", env={'region': 'us-east-1'})

app.synth()
