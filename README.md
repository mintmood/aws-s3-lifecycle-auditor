# aws-s3-lifecycle-auditor

Small CLI to audit S3 buckets for missing lifecycle rules (`AbortIncompleteMultipartUpload` and `NoncurrentVersionExpiration`).

## Usage

```bash
pip install -r requirements.txt
python3 audit_s3.py --only-missing --json
python3 audit_s3.py --prefix prod-
```
