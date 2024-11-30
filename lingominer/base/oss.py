import boto3
import os


def download_file(bucket: str, key: str, fp: str):
    s3 = boto3.client(
        service_name="s3",
        endpoint_url=os.getenv("R2_ENDPOINT_URL"),
    )
    with open(fp, "wb") as f:
        s3.download_fileobj(bucket, key, f)


def upload_file(bucket: str, key: str, fp: str):
    s3 = boto3.client(
        service_name="s3",
        endpoint_url=os.getenv("R2_ENDPOINT_URL"),
    )
    with open(fp, "rb") as f:
        s3.upload_fileobj(f, bucket, key)
