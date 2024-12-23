# AWS S3

# S3 stands for Simple Storage Service.
# S3 is versatile object storage service that enables users to store and retrieve any amount of data from
# anywhere on the web. i.e. Media streaming platform like Netflix uses S3.


import boto3

s3_client = boto3.client(
    "s3",
    region_name="",
    aws_access_key_id="",
    aws_secret_access_key=""
)

# NOTE: If the file name is exist and still we upload file then it will replace completely
# until we not enable versioning for bucket. If enabled, then after upload it will return VersionId in response.

# 1. FOR STORE IN S3

# upload_file : Uploads a file from the local filesystem to an S3 bucket.
# Recommended for large files as it handles multipart uploads.
s3_client.upload_file(
    "<Full File Path>",
    "<Bucket Name>",
    "File Name"
)

# put_object : Uploads raw binary data or strings directly to an S3 bucket.
# Suitable for small files or simple data uploads.
s3_client.put_object(
    Bucket="<S3 bucket name>",
    Key="<File name in the bucket>",
    Body="Raw Data",
)

# upload_fileobj : Uploads a file-like object (e.g., io.BytesIO) to an S3 bucket.
# Useful for uploading in-memory data or streaming uploads.
s3_client.upload_fileobj(
    Fileobj="<In-memory file object>",
    Bucket='<S3 bucket name>',
    Key='<File Name in the bucket>'
)

# 2. TO RETRIEVE FROM S3

# Using Pre-Signed URL
s3_client.generate_presigned_url(
    'get_object', Params={'Bucket': "", 'Key': "<File Name>"}, ExpiresIn="<Int value of time in seconds>"
)

# Using get_object
s3_client.get_object(
    Bucket='<S3 bucket name>',
    Key='<File Name in the bucket>'
)

# Using download file
s3_client.download_file(
    Bucket='<S3 bucket name>',
    Key='<File Name in the bucket>',
    Filename='<Local file path to download>'
)

# Check if file exists or not
response = s3_client.list_objects_v2(
    Bucket="<S3 bucket name>", Prefix='<File Name in the bucket>'
)
file_exists = True if 'Contents' in response else False


# EC2

# EC2 stands for Elastic Compute Cloud, that offer resizable compute capacity in the cloud,
# allowing users to scale up or down based on demand.
# EC2 allows you to rent virtual servers, known as instances, to run/host you application.


# AWS Lambda
