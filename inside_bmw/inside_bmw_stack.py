from aws_cdk import (
    Stack,
    CfnOutput,
    aws_apprunner as apprunner,
    aws_ecr_assets as ecr,
    aws_iam as iam,
)
from constructs import Construct

class InsideBmwStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        app_role = iam.Role(self, "AppRole",
            assumed_by=iam.ServicePrincipal("build.apprunner.amazonaws.com")
        )

        app_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryReadOnly")
        )

        image = ecr.DockerImageAsset(self, 'DockerImage', directory='image')
        dockerApp = apprunner.CfnService(
            self, "DockerApp",
            source_configuration={
                'authenticationConfiguration': {
                    'accessRoleArn': app_role.role_arn
                },
                'imageRepository': {
                    'imageIdentifier': image.image_uri,
                    'imageRepositoryType': 'ECR',
                    'imageConfiguration': {
                        'port': '5000'
                    }
                },
                'autoDeploymentsEnabled': True
            },
        )

        CfnOutput(self, "AppRunnerServiceUrl", value=dockerApp.attr_service_url)