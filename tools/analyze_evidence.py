#!/usr/bin/env python3
"""
Evidence Analysis Tool for iOS iCloud Backup Integrity Vulnerability

This tool analyzes iOS diagnostic data to detect corruption indicators
documented in the vulnerability report.

Usage:
    python analyze_evidence.py <path_to_diagnostics>
    python analyze_evidence.py --mock  # Use mock data for demonstration
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


class EvidenceAnalyzer:
    """Analyzes iOS diagnostic data for corruption indicators."""
    
    def __init__(self):
        self.findings: List[Dict[str, Any]] = []
        self.corruption_score = 0
    
    def analyze_keychain_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze PCS keychain status for corruption indicators."""
        result = {
            "name": "Keychain Status Analysis",
            "issues": [],
            "severity": "none"
        }
        
        status = data.get("status_keychain", {})
        circle_status = status.get("circle_status")
        
        # Check circle status
        if circle_status == "Error":
            result["issues"].append({
                "type": "circle_status_error",
                "description": "circle_status is 'Error' - indicates keychain sync failure",
                "severity": "high",
                "evidence": "CloudCompromise.md Finding 1, line 115"
            })
            self.corruption_score += 3
            result["severity"] = "high"
        
        # Check PCS views
        view_status = status.get("view_status", {})
        unknown_views = [view for view, state in view_status.items() if state == "unknown"]
        
        if unknown_views:
            result["issues"].append({
                "type": "unknown_pcs_views",
                "description": f"{len(unknown_views)} PCS views showing 'unknown' status",
                "affected_views": unknown_views,
                "severity": "high" if len(unknown_views) > 5 else "medium",
                "evidence": "CloudCompromise.md Finding 1, lines 117-127"
            })
            self.corruption_score += len(unknown_views)
            result["severity"] = "high"
        
        return result
    
    def analyze_timestamps(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check for invalid epoch timestamps."""
        result = {
            "name": "Timestamp Validation",
            "issues": [],
            "severity": "none"
        }
        
        epoch_items = []
        for item in data.get("keychain_items", []):
            created = item.get("creation_date", "")
            modified = item.get("modification_date", "")
            
            if "1970-01-01" in created or "1970-01-01" in modified:
                epoch_items.append({
                    "service": item.get("service"),
                    "account": item.get("account"),
                    "creation_date": created,
                    "modification_date": modified
                })
        
        if epoch_items:
            result["issues"].append({
                "type": "epoch_timestamps",
                "description": f"Found {len(epoch_items)} keychain items with epoch timestamps",
                "items": epoch_items,
                "severity": "high",
                "evidence": "CloudCompromise.md Finding 2, line 145"
            })
            self.corruption_score += len(epoch_items) * 2
            result["severity"] = "high"
        
        return result
    
    def analyze_backup_metadata(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if corrupted data is being backed up."""
        result = {
            "name": "Backup Activity Analysis",
            "issues": [],
            "severity": "none"
        }
        
        metadata = data.get("backup_metadata", {})
        integrity = data.get("integrity_checks", {})
        
        # Check if backup is active
        sync_active = metadata.get("SyncZoneFetched", False)
        last_backup = metadata.get("NilBackupDateFetchDate")
        
        if sync_active and last_backup:
            result["issues"].append({
                "type": "active_backup_without_validation",
                "description": "iCloud backup is active but no validation performed",
                "last_backup": last_backup,
                "validation_performed": integrity.get("keychain_validated", False),
                "severity": "high",
                "evidence": "CloudCompromise.md Finding 3, lines 159-167"
            })
            self.corruption_score += 2
            result["severity"] = "high"
        
        return result
    
    def analyze_all(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run all analyses and generate report."""
        self.findings = []
        self.corruption_score = 0
        
        # Run individual analyses
        self.findings.append(self.analyze_keychain_status(data))
        self.findings.append(self.analyze_timestamps(data))
        self.findings.append(self.analyze_backup_metadata(data))
        
        # Generate summary
        total_issues = sum(len(f["issues"]) for f in self.findings)
        high_severity = sum(1 for f in self.findings if f["severity"] == "high")
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_findings": len(self.findings),
                "total_issues": total_issues,
                "high_severity_findings": high_severity,
                "corruption_score": self.corruption_score,
                "assessment": self._assess_corruption_level()
            },
            "findings": self.findings,
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _assess_corruption_level(self) -> str:
        """Assess overall corruption level based on score."""
        if self.corruption_score >= 10:
            return "SEVERE - Multiple corruption indicators present"
        elif self.corruption_score >= 5:
            return "MODERATE - Significant corruption detected"
        elif self.corruption_score > 0:
            return "MILD - Some issues detected"
        else:
            return "CLEAN - No corruption indicators found"
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on findings."""
        recommendations = []
        
        if self.corruption_score > 0:
            recommendations.extend([
                "DO NOT restore from this backup to new devices",
                "Collect sysdiagnose for documentation",
                "Contact Apple Support with case reference",
                "Consider creating new clean backup after remediation"
            ])
        
        if self.corruption_score >= 10:
            recommendations.insert(0, 
                "URGENT: Severe corruption detected - avoid using this backup")
        
        return recommendations


def print_report(report: Dict[str, Any], verbose: bool = False):
    """Print analysis report in human-readable format."""
    print("\n" + "="*70)
    print("iOS iCloud Backup Integrity Analysis Report")
    print("="*70 + "\n")
    
    summary = report["summary"]
    print(f"Analysis Timestamp: {report['timestamp']}")
    print(f"Total Findings: {summary['total_findings']}")
    print(f"Total Issues: {summary['total_issues']}")
    print(f"High Severity: {summary['high_severity_findings']}")
    print(f"Corruption Score: {summary['corruption_score']}")
    print(f"\nAssessment: {summary['assessment']}")
    print("\n" + "-"*70 + "\n")
    
    # Print findings
    for finding in report["findings"]:
        print(f"📋 {finding['name']}")
        print(f"   Severity: {finding['severity'].upper()}")
        
        if finding["issues"]:
            print(f"   Issues Found: {len(finding['issues'])}")
            for issue in finding["issues"]:
                print(f"\n   ⚠️  {issue['description']}")
                if verbose:
                    print(f"      Type: {issue['type']}")
                    print(f"      Severity: {issue['severity']}")
                    print(f"      Evidence: {issue['evidence']}")
        else:
            print("   ✅ No issues detected")
        
        print()
    
    # Print recommendations
    if report["recommendations"]:
        print("-"*70)
        print("\n🔍 Recommendations:\n")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"   {i}. {rec}")
        print()
    
    print("="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze iOS diagnostics for iCloud backup corruption"
    )
    parser.add_argument(
        "path",
        nargs="?",
        help="Path to diagnostic data (JSON format)"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock corrupted data for demonstration"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output with full details"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output JSON report to file"
    )
    
    args = parser.parse_args()
    
    # Load data
    if args.mock:
        # Use mock corrupted data
        fixtures_path = Path(__file__).parent.parent / "tests" / "poc" / "fixtures"
        data_path = fixtures_path / "corrupted_keychain.json"
        
        if not data_path.exists():
            print(f"Error: Mock data not found at {data_path}")
            return 1
        
        with open(data_path) as f:
            data = json.load(f)
        
        # Add backup metadata
        metadata_path = fixtures_path / "backup_metadata.json"
        with open(metadata_path) as f:
            metadata = json.load(f)
        data.update(metadata)
        
        print("Using mock corrupted data for demonstration...")
    
    elif args.path:
        try:
            with open(args.path) as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error loading data from {args.path}: {e}")
            return 1
    else:
        parser.print_help()
        return 1
    
    # Run analysis
    analyzer = EvidenceAnalyzer()
    report = analyzer.analyze_all(data)
    
    # Print report
    print_report(report, verbose=args.verbose)
    
    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Report saved to {args.output}")
    
    # Return exit code based on severity
    return 1 if report["summary"]["corruption_score"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
