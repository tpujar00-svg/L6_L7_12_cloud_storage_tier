import pytest
from cloud_storage_tier import process_storage_tenants, monitor_replication_latency


def test_invalid_tenants():
    with pytest.raises(ValueError):
        process_storage_tenants("invalid", 10)


def test_negative_support_fee():
    with pytest.raises(ValueError):
        process_storage_tenants([], -1)


def test_inactive_tenant():
    result = process_storage_tenants(
        [{"account_active": False, "buckets": []}], 10
    )
    assert result["status"] == "ZERO_USAGE"


def test_all_storage_tiers_and_large_buckets():
    tenants = [
        {
            "account_active": True,
            "tier": "hot",
            "has_backup_vault": True,
            "buckets": [{"size_gb": 600, "egress_gb": 150}]
        },
        {
            "account_active": True,
            "tier": "cool",
            "buckets": [{"size_gb": 100, "egress_gb": 100}]
        },
        {
            "account_active": True,
            "tier": "archive",
            "buckets": [{"size_gb": 100}]
        }
    ]
    result = process_storage_tenants(tenants, 10)
    assert result == {"total_billed": 29.5, "status": "BILLED"}


def test_invalid_tier():
    result = process_storage_tenants(
        [{"account_active": True, "tier": "unknown"}], 10
    )
    assert result["status"] == "ZERO_USAGE"


def test_invalid_bucket_size():
    result = process_storage_tenants(
        [{"account_active": True, "tier": "hot",
          "buckets": [{"size_gb": 0}]}], 10
    )
    assert result["status"] == "ZERO_USAGE"


def test_corrupted_non_archive_bucket():
    result = process_storage_tenants(
        [{"account_active": True, "tier": "hot",
          "buckets": [
              {"size_gb": 100, "corrupted": True, "egress_gb": 150}
          ]}], 10
    )
    assert result == {"total_billed": 4.0, "status": "BILLED"}


def test_corrupted_archive_bucket():
    result = process_storage_tenants(
        [{"account_active": True, "tier": "archive",
          "has_backup_vault": True,
          "buckets": [
              {"size_gb": 100, "corrupted": True},
              {"size_gb": 200}
          ]}], 10
    )
    assert result == {"total_billed": 10.0, "status": "BILLED"}


def test_audit_flagged():
    buckets = [{"size_gb": 0} for _ in range(5)]
    result = process_storage_tenants(
        [{"account_active": True, "tier": "hot",
          "buckets": buckets}], 10
    )
    assert result["status"] == "AUDIT_FLAGGED"


def test_zero_usage():
    result = process_storage_tenants([], 10)
    assert result == {"total_billed": 0.0, "status": "ZERO_USAGE"}


def test_empty_replication_data():
    assert monitor_replication_latency([]) == "NO_DATA"


def test_consecutive_high_latency():
    assert monitor_replication_latency([[250, 300]]) == "SYNC_LAG_ALERT"


def test_latency_reset():
    assert monitor_replication_latency([[250, 100, 260]]) == "SYNCED"


def test_single_high_latency():
    assert monitor_replication_latency([[250]]) == "SYNCED"


def test_empty_node_logs():
    assert monitor_replication_latency([[]]) == "SYNCED"
