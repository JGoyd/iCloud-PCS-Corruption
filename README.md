# iCloud-PCS-Corruption
CVE Pending - Apple iOS iCloud Backup Lacks PCS Keychain Integrity Validation

**CVE:** Pending Assignment  
**CVSS:** 8.1 (HIGH)  
**Discoverer:** Joseph Goydish II  
**Discovery Date:** November 27, 2025  


---

## Summary

Apple's iCloud backup system does not validate the integrity of Protected Cloud Storage (PCS) keychain data during backup creation or restoration. This allows corrupted keychain entries to persist indefinitely in user backups and restore silently to devices without detection or user warning.

## Impact

- Affects all iOS/iPadOS users with iCloud backup enabled
- Enables indefinite persistence of keychain corruption across devices
- Bypasses security patches through backup restoration
- Affects ALL past iOS vulnerabilities (not just recent exploits)
- No user remediation tools available

## Discovery

This vulnerability was discovered on November 27, 2025 through diagnostic analysis of an iOS 26.1 device showing:
- Corrupted keychain state (`circle_status: "Error"`)
- All PCS views showing `"unknown"` status
- Invalid epoch timestamps (1970-01-01) in keychain entries
- Active iCloud backup syncing corrupted data without validation

## Disclosure Status

- **Vendor Notification:** November 28, 2025
  - Apple Product Security (Tracking: OE01004512688207)
- **US-CERT:** November 28, 2025
  - CISA VINCE portal submission (Tracking: VRF#25-11-SQRSK)
- **JPCERT/CC:** December 1, 2025 (TN: JPCERT#98937191)

 **CVE Assignment:** Pending


---

**Copyright © 2025 Joseph Goydish II. All rights reserved.**

This research may be freely shared for educational and security purposes with proper attribution.
EOF

