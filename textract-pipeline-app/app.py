from chalice import Chalice

app = Chalice(app_name='textract-pipeline-app')

@app.lambda_function(name='pdf2image')
def pdf2image_lambda_function(event, context):
    # Anything you want here.
    return {}
