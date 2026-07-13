import pytest

from design_traffic import calculate_design_traffic


# ============================================================
# TEST 1: BASELINE DESIGN TRAFFIC CALCULATION
# ============================================================

def test_baseline_design_traffic():

    results = calculate_design_traffic(
        traffic_at_last_count=2355.14,
        growth_rate=0.05,
        design_period=20,
        years_to_completion=0,
        vdf=3.0,
        distribution_factor=0.50
    )

    assert results["traffic_at_last_count"] == pytest.approx(
        2355.14
    )

    assert results["opening_traffic"] == pytest.approx(
        2355.14
    )

    assert results["design_traffic_msa"] == pytest.approx(
        42.64,
        abs=0.02
    )


# ============================================================
# TEST 2: DESIGN TRAFFIC INCREASES WITH GROWTH RATE
# ============================================================

def test_design_traffic_increases_with_growth_rate():

    lower_growth = calculate_design_traffic(
        traffic_at_last_count=2355.14,
        growth_rate=0.05,
        design_period=20,
        years_to_completion=0,
        vdf=3.0,
        distribution_factor=0.50
    )

    higher_growth = calculate_design_traffic(
        traffic_at_last_count=2355.14,
        growth_rate=0.07,
        design_period=20,
        years_to_completion=0,
        vdf=3.0,
        distribution_factor=0.50
    )

    assert (
        higher_growth["design_traffic_msa"]
        > lower_growth["design_traffic_msa"]
    )


# ============================================================
# TEST 3: DESIGN TRAFFIC INCREASES WITH VDF
# ============================================================

def test_design_traffic_increases_with_vdf():

    lower_vdf = calculate_design_traffic(
        traffic_at_last_count=2355.14,
        growth_rate=0.05,
        design_period=20,
        years_to_completion=0,
        vdf=3.0,
        distribution_factor=0.50
    )

    higher_vdf = calculate_design_traffic(
        traffic_at_last_count=2355.14,
        growth_rate=0.05,
        design_period=20,
        years_to_completion=0,
        vdf=4.0,
        distribution_factor=0.50
    )

    assert (
        higher_vdf["design_traffic_msa"]
        > lower_vdf["design_traffic_msa"]
    )


# ============================================================
# TEST 4: ZERO GROWTH RATE CASE
# ============================================================

def test_zero_growth_rate():

    results = calculate_design_traffic(
        traffic_at_last_count=1000,
        growth_rate=0.0,
        design_period=10,
        years_to_completion=0,
        vdf=3.0,
        distribution_factor=0.50
    )

    expected_standard_axles = (
        365
        * 1000
        * 10
        * 3.0
        * 0.50
    )

    expected_msa = expected_standard_axles / 1_000_000

    assert results["growth_factor"] == pytest.approx(10.0)

    assert results["design_traffic_msa"] == pytest.approx(
        expected_msa
    )


# ============================================================
# TEST 5: ROAD-OPENING DELAY INCREASES DESIGN TRAFFIC
# ============================================================

def test_road_opening_delay_increases_design_traffic():

    no_delay = calculate_design_traffic(
        traffic_at_last_count=2355.14,
        growth_rate=0.05,
        design_period=20,
        years_to_completion=0,
        vdf=3.0,
        distribution_factor=0.50
    )

    delayed_opening = calculate_design_traffic(
        traffic_at_last_count=2355.14,
        growth_rate=0.05,
        design_period=20,
        years_to_completion=3,
        vdf=3.0,
        distribution_factor=0.50
    )

    assert (
        delayed_opening["opening_traffic"]
        > no_delay["opening_traffic"]
    )

    assert (
        delayed_opening["design_traffic_msa"]
        > no_delay["design_traffic_msa"]
    )