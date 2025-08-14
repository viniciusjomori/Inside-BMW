import aws_cdk as cdk

from inside_bmw.inside_bmw_stack import InsideBmwStack

app = cdk.App()
InsideBmwStack(app, "InsideBmwStack")

app.synth()