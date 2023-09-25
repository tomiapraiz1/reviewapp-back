from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_apigateway as apigateway,
    aws_lambda as lambda_,
    aws_dynamodb as ddb,
    RemovalPolicy,
    aws_iam as iam,
    CfnOutput
)
from constructs import Construct

class BackStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ec2.Vpc(
            self,
            'mainVPC',
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    cidr_mask=24,
                    name="public-subnet",
                    subnet_type=ec2.SubnetType.PUBLIC
                )
            ]
        )
        
        api = apigateway.RestApi(
            self,
            "API",
            default_cors_preflight_options={
                "allow_origins": apigateway.Cors.ALL_ORIGINS,
                "allow_methods": apigateway.Cors.ALL_METHODS,
                "allow_headers": apigateway.Cors.DEFAULT_HEADERS
            },
            deploy=False
        )

        # dynamodb table for tasks
        review_table = ddb.Table(
            self,
            "Reviews",
            partition_key=ddb.Attribute(
                name="id",
                type=ddb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY
        )

        # secondary index for speed improvement when requests data
        review_table.add_global_secondary_index(
            index_name="user-index",
            partition_key=ddb.Attribute(
                name="user_id",
                type=ddb.AttributeType.STRING
            ),
            sort_key=ddb.Attribute(
                name="date",
                type=ddb.AttributeType.NUMBER
            )
        )

        # secondary index for speed improvement when requests data
        review_table.add_global_secondary_index(
            index_name="place-index",
            partition_key=ddb.Attribute(
                name="place_id",
                type=ddb.AttributeType.STRING
            ),
            sort_key=ddb.Attribute(
                name="date",
                type=ddb.AttributeType.NUMBER
            )
        )

        reviews_layer = lambda_.LayerVersion(
            self,
            "TableLayer",
            code=lambda_.Code.from_asset("./layers/"),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_11]
        )

        all_reviews_by_place_lambda = lambda_.Function(
            self,
            "All reviews by place lambda",
            runtime=lambda_.Runtime.PYTHON_3_11,
            code=lambda_.Code.from_asset("./api/"),
            handler="all_reviews_by_place.handler",
            environment={
                "REVIEWS_TABLE_NAME": review_table.table_name
            },
            layers=[
                reviews_layer
            ]
        )

        all_reviews_by_place_lambda_integration = apigateway.LambdaIntegration(
            all_reviews_by_place_lambda,
            request_parameters={
                "integration.request.querystring.place_id": "method.request.querystring.place_id"
            }
        )

        all_reviews_by_place_lambda.grant_invoke(iam.ServicePrincipal("apigateway.amazonaws.com"))
        review_table.grant_read_data(all_reviews_by_place_lambda)

        all_reviews_by_user_lambda = lambda_.Function(
            self,
            "All reviews by user lambda",
            runtime=lambda_.Runtime.PYTHON_3_11,
            code=lambda_.Code.from_asset("./api/"),
            handler="all_reviews_by_user.handler",
            environment={
                "REVIEWS_TABLE_NAME": review_table.table_name
            },
            layers=[
                reviews_layer
            ]
        )

        all_reviews_by_user_lambda_integration = apigateway.LambdaIntegration(
            all_reviews_by_user_lambda,
            request_parameters={
                "integration.request.querystring.user_id": "method.request.querystring.user_id"
            }
        )

        all_reviews_by_user_lambda.grant_invoke(iam.ServicePrincipal("apigateway.amazonaws.com"))
        review_table.grant_read_data(all_reviews_by_user_lambda)

        create_review_lambda = lambda_.Function(
            self,
            "Create review lambda",
            runtime=lambda_.Runtime.PYTHON_3_11,
            code=lambda_.Code.from_asset("./api/"),
            handler="create_review.handler",
            environment={
                "REVIEWS_TABLE_NAME": review_table.table_name
            },
            layers=[
                reviews_layer
            ]
        )

        create_review_lambda_integration = apigateway.LambdaIntegration(
            create_review_lambda
        )

        create_review_lambda.grant_invoke(iam.ServicePrincipal("apigateway.amazonaws.com"))
        review_table.grant_write_data(create_review_lambda)

        delete_review_lambda = lambda_.Function(
            self,
            "Delete review lambda",
            runtime=lambda_.Runtime.PYTHON_3_11,
            code=lambda_.Code.from_asset("./api/"),
            handler="delete_review.handler",
            environment={
                "REVIEWS_TABLE_NAME": review_table.table_name
            },
            layers=[
                reviews_layer
            ]
        )

        delete_review_lambda_integration = apigateway.LambdaIntegration(
            delete_review_lambda,
            request_parameters={
                "integration.request.querystring.id": "method.request.querystring.id"
            }
        )

        delete_review_lambda.grant_invoke(iam.ServicePrincipal("apigateway.amazonaws.com"))
        review_table.grant_read_write_data(delete_review_lambda)

        tasks_resource = api.root.add_resource("reviews")

        tasks_resource.add_method(
            "GET",
            all_reviews_by_user_lambda_integration,
            request_parameters={
                "method.request.querystring.user_id": True
            },
            method_responses=[
                {
                    "statusCode": "200",
                    "responseParameters": {
                        "method.response.header.Access-Control-Allow-Origin": True
                    }
                },
                {
                    "statusCode": "400",
                    "responseParameters": {
                        "method.response.header.Access-Control-Allow-Origin": True
                    }
                }
            ]
        )

        tasks_resource.add_method(
            "POST",
            create_review_lambda_integration,
            method_responses=[
                {
                    "statusCode": "201",
                    "responseParameters": {
                        "method.response.header.Access-Control-Allow-Origin": True
                    }
                },
                {
                    "statusCode": "400",
                    "responseParameters": {
                        "method.response.header.Access-Control-Allow-Origin": True
                    }
                }
            ]
        )

        tasks_resource.add_method(
            "DELETE",
            delete_review_lambda_integration,
            request_parameters={
                "method.request.querystring.id": True
            },
            method_responses=[
                {
                    "statusCode": "200",
                    "responseParameters": {
                        "method.response.header.Access-Control-Allow-Origin": True
                    }
                },
                {
                    "statusCode": "400",
                    "responseParameters": {
                        "method.response.header.Access-Control-Allow-Origin": True
                    }
                },
                {
                    "statusCode": "404",
                    "responseParameters": {
                        "method.response.header.Access-Control-Allow-Origin": True
                    }
                }
            ]
        )

        deployment = apigateway.Deployment(
            self,
            "Deployment",
            api=api
        )

        dev_stage = apigateway.Stage(
            self,
            "DevStage",
            deployment=deployment,
            stage_name="dev"
        )

        prod_stage = apigateway.Stage(
            self,
            "ProdStage",
            deployment=deployment,
            stage_name="prod"
        )

        api.deployment_stage = dev_stage

        CfnOutput(
            self,
            "DEV API URL",
            value=api.url
        )
