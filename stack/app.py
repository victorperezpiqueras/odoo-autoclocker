import json

import aws_cdk as cdk
from aws_cdk import (
    aws_events as events,
)
from aws_cdk import (
    aws_events_targets as targets,
)
from aws_cdk import (
    aws_lambda as _lambda,
)
from aws_cdk import (
    aws_lambda_python_alpha,
)
from constructs import Construct


class CronLambdaStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        with open(".env.json") as file:
            lambda_env = json.load(file)

        lambda_layer = aws_lambda_python_alpha.PythonLayerVersion(
            self,
            "AutoClockerScheduledLambdaLayer",
            layer_version_name="AutoClockerScheduledLambdaLayer",
            entry="app",
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_12],
        )

        # Create the Lambda function using the specified handler
        scheduled_lambda = aws_lambda_python_alpha.PythonFunction(
            self,
            "ScheduledLambda",
            function_name="AutoClockerScheduledLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            entry="app",
            index="handler.py",
            handler="check_attendance",
            layers=[lambda_layer],
            timeout=cdk.Duration.minutes(5),
            memory_size=512,
            environment=lambda_env,
        )

        # Create a rule to trigger at 7:00 AM every day (UTC) -> 8/9 AM in CET/CEST
        morning_rule = events.Rule(
            self,
            "MorningScheduleRule",
            schedule=events.Schedule.cron(
                minute="0",
                hour="7",
                month="*",
                week_day="MON-FRI",
                year="*",
            ),
        )

        # Create a rule to trigger at 5:00 PM every day (UTC) -> 6/7 PM in CET/CEST
        evening_rule = events.Rule(
            self,
            "EveningScheduleRule",
            schedule=events.Schedule.cron(
                minute="0",
                hour="17",
                month="*",
                week_day="MON-FRI",
                year="*",
            ),
        )

        # Add the Lambda function as a target for both rules
        morning_rule.add_target(targets.LambdaFunction(scheduled_lambda))
        evening_rule.add_target(targets.LambdaFunction(scheduled_lambda))


app = cdk.App()
CronLambdaStack(app, "autoclocker-cron-lambda-stack")
app.synth()
