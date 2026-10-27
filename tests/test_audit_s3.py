import unittest
from unittest.mock import MagicMock
from botocore.exceptions import ClientError
import audit_s3


class TestAuditS3(unittest.TestCase):
    def test_missing_lifecycle_returns_empty(self):
        s3 = MagicMock()
        s3.get_bucket_lifecycle_configuration.side_effect = ClientError(
            {"Error": {"Code": "NoSuchLifecycleConfiguration", "Message": "none"}},
            "GetBucketLifecycleConfiguration",
        )
        self.assertEqual(audit_s3.get_lifecycle_rules(s3, "my-bucket"), [])

    def test_has_abort_multipart(self):
        self.assertTrue(audit_s3.has_abort_multipart([{"Status": "Enabled", "AbortIncompleteMultipartUpload": {"DaysAfterInitiation": 7}}]))
        self.assertFalse(audit_s3.has_abort_multipart([{"Status": "Disabled", "AbortIncompleteMultipartUpload": {"DaysAfterInitiation": 7}}]))

    def test_has_noncurrent_expiration(self):
        self.assertTrue(audit_s3.has_noncurrent_expiration([{"Status": "Enabled", "NoncurrentVersionExpiration": {"NoncurrentDays": 90}}]))
        self.assertFalse(audit_s3.has_noncurrent_expiration([]))
