import boto3
from botocore.exceptions import ClientError


def get_lifecycle_rules(s3, bucket: str) -> list:
    try:
        return s3.get_bucket_lifecycle_configuration(Bucket=bucket).get("Rules", [])
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchLifecycleConfiguration":
            return []
        raise


def has_abort_multipart(rules: list) -> bool:
    return any(r.get("Status") == "Enabled" and "AbortIncompleteMultipartUpload" in r for r in rules)
