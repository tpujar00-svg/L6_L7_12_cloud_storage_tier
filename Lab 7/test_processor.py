from hypothesis import given, strategies as st
from processor import parse_storage_quota, compute_compression_ratio, lookup_bandwidth_tier_rate


@given(st.text() | st.none())
def test_parse_storage_quota_no_crash(s):
    try:
        parse_storage_quota(s)
    except Exception as e:
        assert False, f"Unexpected exception in parse_storage_quota: {e}"


@given(st.text() | st.none())
def test_compute_compression_ratio_safe(s):
    try:
        compute_compression_ratio(s)
    except Exception as e:
        assert False, f"Unexpected exception in compute_compression_ratio: {e}"


@given(st.text() | st.none())
def test_lookup_bandwidth_tier_rate_safe(s):
    try:
        lookup_bandwidth_tier_rate(s)
    except Exception as e:
        assert False, f"Unexpected exception in lookup_bandwidth_tier_rate: {e}"
