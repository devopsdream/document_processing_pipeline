import json
from helper import FileHelper, S3Helper
from trp import Document
import boto3

class OutputGenerator:
    def __init__(self, response, bucketName, objectName, tables, metadata):
        self.response = response
        self.bucketName = bucketName
        self.objectName = objectName
        self.tables = tables
        self.metadata = metadata

        self.outputPath = "{}-analysis/".format(objectName, objectName)

        self.document = Document(self.response)

    def _outputText(self, page, p):
        page_number = self.metadata['page_number']
        text = page.text
        opath = "{}page-{}-text.txt".format(self.outputPath, page_number)
        S3Helper.writeToS3(text, self.bucketName, opath)
        textInReadingOrder = page.getTextInReadingOrder()
        opath = "{}page-{}-text-inreadingorder.txt".format(self.outputPath, page_number)
        S3Helper.writeToS3(textInReadingOrder, self.bucketName, opath)

        return opath


    def _outputTable(self, page, p):
        page_number = self.metadata['page_number']
        csvData = []
        for table in page.tables:
            csvRow = []
            csvRow.append("Table")
            csvData.append(csvRow)
            for row in table.rows:
                csvRow  = []
                for cell in row.cells:
                    csvRow.append(cell.text)
                csvData.append(csvRow)
            csvData.append([])
            csvData.append([])

        opath = "{}page-{}-tables.csv".format(self.outputPath, page_number)
        S3Helper.writeCSVRaw(csvData, self.bucketName, opath)

        return opath

    def run(self):

        if(not self.document.pages):
            return

        opath = "{}response.json".format(self.outputPath)
        S3Helper.writeToS3(json.dumps(self.response), self.bucketName, opath)

        print("Total Pages in Document: {}".format(len(self.document.pages)))

        docText = ""

        p = 1
        for page in self.document.pages:
            opath = "{}page-{}-response.json".format(self.outputPath, self.metadata['page_number'])
            S3Helper.writeToS3(json.dumps(page.blocks), self.bucketName, opath)

            text_file = self._outputText(page, p)

            docText = docText + page.text + "\n"

            if(self.tables):
                csv_file = self._outputTable(page, p)

            p = p + 1
        return {"csv": csv_file, "text_file": text_file}
        