import json
import boto3
from  helper import AwsHelper, S3Helper
from og import OutputGenerator
def callTextract(bucket_name, object_name, detectText, detectTables ):

    textract = AwsHelper().getClient('textract')
    if(not detectTables):
        response = textract.detect_document_text(
             Document={
                 'S3Object': {
                     'Bucket': bucket_name,
                     'Name': object_name
                 }
             }
        )
    else:
        features  = []
        if(detectTables):
            features.append("TABLES")
        if(detectForms):
            features.append("FORMS")
        response = textract.analyze_document(
            Document={
                'S3Object': {
                    'Bucket': bucket_name,
                    'Name': object_name
                }
            },
            FeatureTypes=features
        )

    return response






    return 
def processImage(features, bucket_name, object_name):

    detectTables = "Tables" in features
    detectText = "Text" in features

    response = callTextract(bucket_name, object_name, detectText, detectTables)

    print("Generating output for DocumentId: {}".format(object_name))

    opg = OutputGenerator(response, bucketName=bucket_name, objectName=object_name, tables=detectTables)

    #opg.run()

    #print("DocumentId: {}".format(object_name))





    
def processRequest(request):
    bucket_name = request['bucketName']
    object_name = request["objectName"]
    features = request['features']
    print("processing bucket: {}".format(bucket_name))
    print("Processing file: {}".format(object_name))

    if object_name and  features:
        processImage(features=features, bucket_name=bucket_name, object_name=object_name)

    output = "features: {}, Object: {}/{} processed.".format(features, bucket_name, object_name)

    return {
        'statusCode': 200,
        'body': output
    }


def lambda_handler(event, context):
    print("event: {}".format(event))
    request = {}
    request["bucketName"] = 'tonouma-266014969233-docs'
    request["objectName"] = event
    request["features"] = ['detectText', 'detectTables']    

    return processRequest(request)