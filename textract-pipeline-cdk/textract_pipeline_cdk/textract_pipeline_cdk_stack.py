from aws_cdk import (
    aws_iam as iam,
    aws_sqs as sqs,
    core
)
from cdk_chalice import Chalice
import os


class TextractPipelineCdkStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        queue = sqs.Queue(
            self, "TextractPipelineCdkQueue",
            visibility_timeout=core.Duration.seconds(300),
        )
        #get the chalice application
        web_api_source_dir = os.path.join(os.path.dirname(__file__), os.pardir,
                                          os.pardir, 'textract-pipeline-app')
        
        #chalice stage  configuration
        chalice_stage_config = self._create_chalice_stage_config()

        #define the chalice application
        self.chalice = Chalice(self, 'textract-pipeline-app', source_dir=web_api_source_dir,
                               stage_config=chalice_stage_config)


    ##define chalice stage configuration
    def _create_chalice_stage_config(self):
        chalice_stage_config = {

        }
        return chalice_stage_config


