# Analysis Tools

This directory contains tools for analyzing iOS diagnostic data to detect corruption indicators related to the iCloud backup integrity vulnerability.

## Tools Available

### analyze_evidence.py

Automated evidence analysis tool that scans iOS diagnostic data for corruption indicators.

**Features**:
- Detects circle_status errors
- Identifies unknown PCS views
- Finds epoch timestamps (1970-01-01)
- Checks backup validation status
- Calculates corruption severity score
- Generates recommendations

**Usage**:

```bash
# Analyze mock corrupted data (demonstration)
python tools/analyze_evidence.py --mock --verbose

# Analyze actual iOS diagnostics
python tools/analyze_evidence.py path/to/diagnostic.json --verbose

# Generate JSON report
python tools/analyze_evidence.py --mock --output report.json

# Get help
python tools/analyze_evidence.py --help
```

**Input Format**:

The tool expects JSON data in this structure:

```json
{
  "status_keychain": {
    "circle_status": "Error" | "In Circle",
    "view_status": {
      "PCS-Backup": "unknown" | "enabled",
      "PCS-CloudKit": "unknown" | "enabled",
      ...
    }
  },
  "keychain_items": [
    {
      "service": "ServiceName",
      "account": "AccountName",
      "creation_date": "ISO-8601 timestamp",
      "modification_date": "ISO-8601 timestamp"
    }
  ],
  "backup_metadata": {
    "NilBackupDateFetchDate": "ISO-8601 timestamp",
    "SyncZoneFetched": true | false,
    "LastBackupStatus": "Completed" | "Failed"
  }
}
```

**Output**:

```
======================================================================
iOS iCloud Backup Integrity Analysis Report
======================================================================

Analysis Timestamp: 2025-12-10T19:45:18+00:00
Total Findings: 3
Total Issues: 4
High Severity: 3
Corruption Score: 20

Assessment: SEVERE - Multiple corruption indicators present

----------------------------------------------------------------------

📋 Keychain Status Analysis
   Severity: HIGH
   Issues Found: 2

   ⚠️  circle_status is 'Error' - indicates keychain sync failure
   ⚠️  11 PCS views showing 'unknown' status

📋 Timestamp Validation
   Severity: HIGH
   Issues Found: 1

   ⚠️  Found 2 keychain items with epoch timestamps

📋 Backup Activity Analysis
   Severity: HIGH
   Issues Found: 1

   ⚠️  iCloud backup is active but no validation performed

----------------------------------------------------------------------

🔍 Recommendations:

   1. URGENT: Severe corruption detected - avoid using this backup
   2. DO NOT restore from this backup to new devices
   3. Collect sysdiagnose for documentation
   4. Contact Apple Support with case reference
   5. Consider creating new clean backup after remediation

======================================================================
```

**Corruption Score Interpretation**:

- **0**: CLEAN - No corruption indicators found
- **1-4**: MILD - Some issues detected
- **5-9**: MODERATE - Significant corruption detected
- **10+**: SEVERE - Multiple corruption indicators present

## Collecting iOS Diagnostics

To use this tool with actual iOS data, you need to collect a sysdiagnose:

### On iOS Device

1. Settings > Privacy & Security > Analytics & Improvements
2. Analytics Data > Find "sysdiagnose_*" files
3. Tap and share via AirDrop or email

### Via Xcode (Mac)

1. Window > Devices and Simulators
2. Select your device
3. View Device Logs
4. Click "sysdiagnose" button

### Extract Files

```bash
# Extract the archive
tar -xzf sysdiagnose_*.tar.gz
cd sysdiagnose_*/

# Key files to examine:
# - logs/PCS/pcsstatus.txt
# - logs/Security/security-sysdiagnose.txt
# - com_apple_MobileBackup.plist
# - SystemVersion.plist
```

## Creating JSON Input

You'll need to manually structure the diagnostic data as JSON. See the fixtures in `tests/poc/fixtures/` for examples.

Example extraction:

```bash
# Convert plist to JSON
plutil -convert json com_apple_MobileBackup.plist -o backup.json

# Extract PCS status (manual process)
cat logs/PCS/pcsstatus.txt | grep -A50 "status_keychain"
# Then manually structure as JSON
```

## Security Note

⚠️ **Important**: Do not share raw iOS diagnostics publicly as they may contain sensitive information:

- User identifiers
- Device serial numbers
- Network information
- App usage data

Always redact sensitive information before sharing analysis results.

## See Also

- `tests/poc/README.md` - PoC test documentation
- `VERIFICATION_REPORT.md` - Full verification report
- `ANALYSIS_SUMMARY.md` - Quick reference guide
