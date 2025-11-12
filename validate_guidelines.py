#!/usr/bin/env python3
"""
Guidelines Adherence Validation Script
Ensures PROJECT_GUIDELINES.md compliance across the codebase
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Tuple

class GuidelinesValidator:
    def __init__(self, project_root: str = "/workspaces/mydemerzel-project"):
        self.project_root = Path(project_root)
        self.guidelines_path = self.project_root / "PROJECT_GUIDELINES.md"
        self.violations = []
        
    def load_guidelines(self) -> str:
        """Load PROJECT_GUIDELINES.md content"""
        if not self.guidelines_path.exists():
            raise FileNotFoundError("PROJECT_GUIDELINES.md not found!")
        return self.guidelines_path.read_text()
    
    def check_file_structure(self) -> List[str]:
        """Validate proper file organization"""
        violations = []
        
        # Check for old guidelines files that should be deleted
        old_guidelines = [
            "DEVELOPER_QUICK_REFERENCE.md",
            "ENHANCED_FORMATTING_GUIDE.md", 
            "FORMATTING_IMPLEMENTATION_SUMMARY.md",
            "INTERFACE_UPDATES.md",
            "LAYOUT_FIX_SUMMARY.md"
        ]
        
        for old_file in old_guidelines:
            if (self.project_root / old_file).exists():
                violations.append(f"Old guidelines file still exists: {old_file}")
        
        return violations
    
    def check_python_imports(self) -> List[str]:
        """Check Python files for proper import structure"""
        violations = []
        python_files = [f for f in list(self.project_root.glob("*.py")) if f.name != "validate_guidelines.py"]
        
        for py_file in python_files:
            content = py_file.read_text()
            lines = content.split('\n')
            
            # Check for proper Flask import structure
            if 'from flask import' in content:
                flask_imports = [line for line in lines if 'from flask import' in line]
                if len(flask_imports) > 1:
                    violations.append(f"{py_file.name}: Multiple Flask import lines (should be consolidated)")
        
        return violations
    
    def check_ttrpg_structure(self) -> List[str]:
        """Validate TTRPG system structure"""
        violations = []
        ttrpg_config_path = self.project_root / "ttrpg-config.json"
        
        if not ttrpg_config_path.exists():
            violations.append("ttrpg-config.json missing")
            return violations
        
        config = json.loads(ttrpg_config_path.read_text())
        required_ttrpgs = [
            "dune",
            "mouse-guard",
            "the-witcher",
            "zweihander",
            "cyberpunk",
            "pendragon",
            "master-template",
        ]
        
        for ttrpg in required_ttrpgs:
            if ttrpg not in config.get("systems", {}):
                violations.append(f"TTRPG system missing from config: {ttrpg}")
        
        return violations
    
    def check_embedding_files(self) -> List[str]:
        """Validate embedding system files"""
        violations = []
        required_embedding_files = [
            "generate_optimized_embeddings.py",
            "memory_optimized_embeddings.py", 
            "optimized_embedding_search.py"
        ]
        
        for req_file in required_embedding_files:
            if not (self.project_root / req_file).exists():
                violations.append(f"Required embedding file missing: {req_file}")
        
        return violations
    
    def check_deployment_readiness(self) -> List[str]:
        """Check deployment configuration"""
        violations = []
        
        required_files = [
            "requirements.txt",
            "requirements-prod.txt", 
            "gunicorn.conf.py",
            "app.py"
        ]
        
        for req_file in required_files:
            if not (self.project_root / req_file).exists():
                violations.append(f"Deployment file missing: {req_file}")
        
        return violations
    
    def run_validation(self) -> bool:
        """Run complete validation suite"""
        print("🔍 Validating PROJECT_GUIDELINES.md adherence...")
        
        # Load guidelines first
        try:
            guidelines_content = self.load_guidelines()
            print(f"✅ PROJECT_GUIDELINES.md loaded ({len(guidelines_content)} chars)")
        except FileNotFoundError as e:
            print(f"❌ {e}")
            return False
        
        # Run all checks
        checks = [
            ("File Structure", self.check_file_structure),
            ("Python Imports", self.check_python_imports),
            ("TTRPG Structure", self.check_ttrpg_structure),
            ("Embedding Files", self.check_embedding_files),
            ("Deployment Readiness", self.check_deployment_readiness)
        ]
        
        all_violations = []
        for check_name, check_func in checks:
            violations = check_func()
            all_violations.extend(violations)
            
            if violations:
                print(f"⚠️  {check_name}: {len(violations)} violations")
                for violation in violations:
                    print(f"   - {violation}")
            else:
                print(f"✅ {check_name}: No violations")
        
        # Summary
        if all_violations:
            print(f"\n❌ Validation failed: {len(all_violations)} total violations")
            print("\n📋 ADHERENCE ACTION REQUIRED:")
            print("1. Review PROJECT_GUIDELINES.md")
            print("2. Fix violations listed above")
            print("3. Re-run validation")
            return False
        else:
            print("\n✅ All guidelines validation checks passed!")
            print("📋 PROJECT_GUIDELINES.md adherence: CONFIRMED")
            return True

def main():
    """Main execution"""
    validator = GuidelinesValidator()
    success = validator.run_validation()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
