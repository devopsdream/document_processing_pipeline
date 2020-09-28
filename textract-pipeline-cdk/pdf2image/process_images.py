import os
from pdf2image import convert_from_bytes
import boto3
import logging
from io import BytesIO
import json
from pathlib import Path
from urllib.parse import unquote_plus

#set logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


s3 = boto3.resource('s3')

def convert_doc_to_png(bucket_name, object_name):
    bucket_name  = bucket_name
    object_name = object_name
    obj = s3.Object(bucket_name, object_name)
    infile = obj.get()['Body'].read()
    poppler_path = "/opt/python/poppler-utils-0.26.5-42.20.amzn1.x86_64/usr/bin"
    images = convert_from_bytes(infile,
                                dpi=300,
                                fmt="png",
                                poppler_path=poppler_path)

    processed_images = []
    for page_num, image in enumerate(images):
        # The directory is: <name of the pdf>-num_pages-<number of pages in the pdf>
        directory = object_name.split('.')[0]
        logger.info("The directory to save the file %s", directory)
        # Then save the image and name it: <name of the pdf>-page<page number>.FMT
        location = directory + "/" + object_name.split('.')[0] + "-page" + str(page_num) + '.' + "png"
        logger.info("The name of the file %s", location)
        #buffer the bytes into memory
        buffer = BytesIO()
        image.save(buffer, "png".upper())
        buffer.seek(0)
        s3.Object(
            bucket_name,
            location
        ).put(
            Body=buffer,
            Metadata={
                'ORIGINAL_DOCUMENT_BUCKET': bucket_name,
                'ORIGINAL_DOCUMENT_KEY': object_name,
                'PAGE_NUMBER': str(page_num),
                'PAGE_COUNT': str(len(images))
            }
        )
        ##append to array
        file_name = {"bucket_name": bucket_name, "file_name": location}
        processed_images.append(file_name)
        processed_output = {"files": processed_images}

    return  processed_output



def  lambda_handler(event,context):
    # check the opt directories directories = os.popen("find /opt/* -type d -maxdepth 4").read().split("\n")
    # check LD_LIBRARY_PATh os.popen("echo $LD_LIBRARY_PATH").read()
    logger.info(event)
    bucket_name = event['bucket_name']
    object_name = unquote_plus(event['object_name'])
    logger.info("Bucket Name: %s", bucket_name)
    logger.info("Object Name %s", object_name)
    output = convert_doc_to_png(bucket_name=bucket_name, object_name=object_name)

    return output