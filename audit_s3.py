#!/usr/bin/env python3
import argparse
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


def main():
    p = argparse.ArgumentParser(description="Audit S3 buckets for lifecycle & multipart cleanup rules")
    p.add_argument("--prefix", default="", help="Filter bucket names by prefix")
    args = p.parse_args()
    s3 = boto3.client("s3")
    for b in s3.list_buckets().get("Buckets", []):
        name = b["Name"]
        if args.prefix and not name.startswith(args.prefix):
            continue
        rules = get_lifecycle_rules(s3, name)
        print(f"{name}\trules={len(rules)}\tabort_mpu={has_abort_multipart(rules)}")


if __name__ == "__main__":
    main()
