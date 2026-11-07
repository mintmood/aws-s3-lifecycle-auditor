#!/usr/bin/env python3
import argparse
import json
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


def has_noncurrent_expiration(rules: list) -> bool:
    return any(r.get("Status") == "Enabled" and "NoncurrentVersionExpiration" in r for r in rules)


def main():
    p = argparse.ArgumentParser(description="Audit S3 buckets for lifecycle & multipart cleanup rules")
    p.add_argument("--prefix", default="", help="Filter bucket names by prefix")
    p.add_argument("--only-missing", action="store_true", help="Show only buckets missing abort-mpu")
    p.add_argument("--json", action="store_true", help="Output JSON")
    args = p.parse_args()
    s3 = boto3.client("s3")
    results = []
    for b in s3.list_buckets().get("Buckets", []):
        name = b["Name"]
        if args.prefix and not name.startswith(args.prefix):
            continue
        rules = get_lifecycle_rules(s3, name)
        abort_mpu = has_abort_multipart(rules)
        if args.only_missing and abort_mpu:
            continue
        results.append({
            "bucket": name,
            "rules": len(rules),
            "abort_mpu": abort_mpu,
            "noncurrent_expire": has_noncurrent_expiration(rules),
        })
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            print(f"{r['bucket']}\trules={r['rules']}\tabort_mpu={r['abort_mpu']}\tnoncurrent_expire={r['noncurrent_expire']}")


if __name__ == "__main__":
    main()
