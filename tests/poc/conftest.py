"""
Shared fixtures for iOS iCloud backup validation PoC tests.

This file provides mock data structures and fixtures based on actual iOS
diagnostic data from the vulnerability report.
"""

import json
import pytest
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def corrupted_keychain(fixtures_dir: Path) -> Dict[str, Any]:
    """Load corrupted keychain data fixture."""
    with open(fixtures_dir / "corrupted_keychain.json", "r") as f:
        return json.load(f)


@pytest.fixture
def valid_keychain(fixtures_dir: Path) -> Dict[str, Any]:
    """Load valid keychain data fixture."""
    with open(fixtures_dir / "valid_keychain.json", "r") as f:
        return json.load(f)


@pytest.fixture
def backup_metadata(fixtures_dir: Path) -> Dict[str, Any]:
    """Load backup metadata fixture."""
    with open(fixtures_dir / "backup_metadata.json", "r") as f:
        return json.load(f)


class MockiCloudBackupSystem:
    """
    Mock iCloud backup system that simulates the vulnerability.
    
    This class demonstrates the LACK of validation in the backup/restore flow.
    In a secure implementation, these methods would include validation checks.
    """
    
    def __init__(self):
        self.backups: Dict[str, Dict[str, Any]] = {}
        self.validation_performed = False
        self.warnings_shown = False
        
    def create_backup(self, device_id: str, keychain_data: Dict[str, Any], 
                      metadata: Dict[str, Any]) -> bool:
        """
        Create backup without validation (VULNERABILITY).
        
        A secure implementation would:
        1. Validate circle_status != "Error"
        2. Check PCS views != "unknown"
        3. Verify no epoch timestamps
        4. Validate data structure integrity
        """
        # VULNERABILITY: No validation performed
        self.backups[device_id] = {
            "keychain": keychain_data,
            "metadata": metadata,
            "created_at": datetime.utcnow().isoformat(),
            "validated": False  # Never validated
        }
        return True
    
    def restore_backup(self, device_id: str) -> Dict[str, Any]:
        """
        Restore backup without validation (VULNERABILITY).
        
        A secure implementation would:
        1. Validate backup integrity before restore
        2. Show warnings for corrupted data
        3. Offer option to skip keychain restore
        4. Log validation failures
        """
        # VULNERABILITY: No validation, no warnings
        if device_id not in self.backups:
            raise ValueError(f"No backup found for device {device_id}")
        
        backup = self.backups[device_id]
        # VULNERABILITY: Return corrupted data without checks
        return backup["keychain"]
    
    def validate_keychain(self, keychain_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validation method that SHOULD be called but ISN'T (VULNERABILITY).
        
        This demonstrates what proper validation would look like.
        """
        self.validation_performed = True
        
        issues = []
        status = keychain_data.get("status_keychain", {})
        
        # Check circle status
        if status.get("circle_status") == "Error":
            issues.append("circle_status is Error")
        
        # Check PCS views
        view_status = status.get("view_status", {})
        for view, state in view_status.items():
            if state == "unknown":
                issues.append(f"PCS view {view} is unknown")
        
        # Check for epoch timestamps
        for item in keychain_data.get("keychain_items", []):
            created = item.get("creation_date", "")
            if "1970-01-01" in created:
                issues.append(f"Epoch timestamp in {item.get('service')}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "validation_performed": True
        }
    
    def show_user_warning(self, issues: List[str]) -> None:
        """
        User warning that SHOULD be shown but ISN'T (VULNERABILITY).
        """
        self.warnings_shown = True
        # In real iOS, this would show a UI alert
        # VULNERABILITY: This method is never called


@pytest.fixture
def backup_system() -> MockiCloudBackupSystem:
    """Provide mock iCloud backup system."""
    return MockiCloudBackupSystem()


@pytest.fixture
def corruption_indicators() -> Dict[str, Any]:
    """Return corruption indicators from evidence."""
    return {
        "epoch_timestamp": "1970-01-01T00:00:00Z",
        "error_status": "Error",
        "unknown_pcs_view": "unknown",
        "corruption_date": "2024-11-14T12:06:28Z"
    }


def is_epoch_timestamp(timestamp_str: str) -> bool:
    """Check if timestamp is Unix epoch (1970-01-01)."""
    return "1970-01-01" in timestamp_str


def has_corruption_indicators(keychain_data: Dict[str, Any]) -> bool:
    """Check if keychain data has corruption indicators."""
    status = keychain_data.get("status_keychain", {})
    
    # Check for error status
    if status.get("circle_status") == "Error":
        return True
    
    # Check for unknown PCS views
    view_status = status.get("view_status", {})
    if any(state == "unknown" for state in view_status.values()):
        return True
    
    # Check for epoch timestamps
    for item in keychain_data.get("keychain_items", []):
        if is_epoch_timestamp(item.get("creation_date", "")):
            return True
    
    return False
