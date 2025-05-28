import boto3
import os


def download_file(bucket: str, key: str, fp: str):
    s3 = boto3.client(
        service_name="s3",
        endpoint_url=f"https://{os.getenv('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com",
        aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY"),
    )
    with open(fp, "wb") as f:
        s3.download_fileobj(bucket, key, f)


def upload_file(bucket: str, key: str, fp: str):
    s3 = boto3.client(
        service_name="s3",
        endpoint_url=f"https://{os.getenv('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com",
        aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY"),
    )
    with open(fp, "rb") as f:
        s3.upload_fileobj(f, bucket, key)
