"""Unit tests for the knowledge base loader module."""

import pytest

from src.knowledge_base.loader import (
    clear_cache,
    get_all_frameworks,
    get_framework,
    get_industry_context,
    get_technology_db,
)


@pytest.fixture(autouse=True)
def _clear_cache():
    clear_cache()
    yield
    clear_cache()


class TestGetFramework:
    def test_load_eu_ai_act(self):
        data = get_framework("eu_ai_act")
        assert data["framework_id"] == "eu_ai_act"
        assert data["display_name"] == "EU AI Act"
        assert "risk_tiers" in data
        assert "key_obligations" in data

    def test_load_all_seven_frameworks(self):
        framework_ids = [
            "eu_ai_act", "singapore_maigf", "us_nist_ai_rmf",
            "uk_ai_regulation", "canada_aida", "australia_ai_ethics", "iso_42001",
        ]
        for fid in framework_ids:
            data = get_framework(fid)
            assert data["framework_id"] == fid

    def test_missing_framework_raises_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            get_framework("nonexistent_framework")

    def test_caching_returns_same_object(self):
        data1 = get_framework("eu_ai_act")
        data2 = get_framework("eu_ai_act")
        assert data1 is data2


class TestGetAllFrameworks:
    def test_returns_all_seven_frameworks(self):
        frameworks = get_all_frameworks()
        assert len(frameworks) == 7

    def test_each_framework_has_required_fields(self):
        frameworks = get_all_frameworks()
        required = ["framework_id", "display_name", "country_or_region", "summary",
                    "last_updated", "version", "risk_tiers", "key_obligations"]
        for fw in frameworks:
            for field in required:
                assert field in fw

    def test_caching_returns_same_list(self):
        f1 = get_all_frameworks()
        f2 = get_all_frameworks()
        assert f1 is f2


class TestGetTechnologyDb:
    def test_returns_all_three_categories(self):
        tech_db = get_technology_db()
        assert "platforms" in tech_db
        assert "orchestration" in tech_db
        assert "models" in tech_db

    def test_platforms_has_entries(self):
        tech_db = get_technology_db()
        assert len(tech_db["platforms"]) >= 1

    def test_each_entry_has_required_fields(self):
        tech_db = get_technology_db()
        required = ["category", "name", "provider", "description",
                    "key_capabilities", "pros", "cons", "compliance_notes"]
        for category, entries in tech_db.items():
            for entry in entries:
                for field in required:
                    assert field in entry

    def test_caching_returns_same_object(self):
        db1 = get_technology_db()
        db2 = get_technology_db()
        assert db1 is db2


class TestGetIndustryContext:
    def test_load_banking(self):
        data = get_industry_context("banking")
        assert data["sector"] == "banking"
        assert "regulatory_context" in data
        assert "common_ai_use_cases" in data
        assert "best_practices" in data

    def test_load_all_nine_sectors(self):
        sectors = ["banking", "insurance", "health", "retail", "technology",
                   "government", "education", "manufacturing", "telecommunications"]
        for sector in sectors:
            data = get_industry_context(sector)
            assert data["sector"] == sector

    def test_missing_sector_raises_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            get_industry_context("nonexistent_sector")

    def test_caching_returns_same_object(self):
        data1 = get_industry_context("banking")
        data2 = get_industry_context("banking")
        assert data1 is data2
