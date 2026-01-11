"""
Code Validator Service
======================

Validates code quality, security compliance, and tracks placeholders.
Enforces best practices and OWASP Top 10 compliance.
"""

import json
import logging
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# File extensions to scan
CODE_EXTENSIONS = {
    '.js', '.jsx', '.ts', '.tsx', '.vue', '.svelte',
    '.py', '.rb', '.php', '.go', '.java', '.cs',
    '.html', '.css', '.scss', '.sass', '.less',
}

# Directories to skip
SKIP_DIRS = {
    'node_modules', '.git', 'dist', 'build', '.next', '.nuxt',
    '__pycache__', 'venv', '.venv', 'env', '.env',
    'coverage', '.pytest_cache', '.mypy_cache',
    # Backup and test directories
    'backup', 'backups', 'ui-react-backup', 'old', 'archive',
    'test-results', 'playwright-report',
}

# Files to skip (validator shouldn't flag itself)
SKIP_FILES = {
    'code_validator.py',  # This file contains patterns as data
    'security.py',  # Security rules file
    '.env.example',  # Example env files have placeholder patterns
    'PLACEHOLDERS.md',  # Generated placeholder docs
}


@dataclass
class CodeIssue:
    """Represents a code quality or security issue."""
    severity: str  # critical, high, medium, low, info
    category: str  # mock_data, placeholder, security, todo, best_practice
    file_path: str
    line_number: int
    line_content: str
    message: str
    owasp_category: Optional[str] = None  # e.g., "A01:2021 - Broken Access Control"


@dataclass
class Placeholder:
    """Represents a legitimate placeholder that needs to be replaced."""
    file_path: str
    line_number: int
    placeholder_type: str  # api_key, secret, url, credential, config
    current_value: str
    description: str
    required_action: str


# =============================================================================
# Pattern Definitions
# =============================================================================

# Mock/Fake Data Patterns (FORBIDDEN)
MOCK_DATA_PATTERNS = [
    (r'\bmockData\b', 'Mock data variable detected'),
    (r'\bfakeData\b', 'Fake data variable detected'),
    (r'\bsampleData\b', 'Sample data variable detected'),
    (r'\bdummyData\b', 'Dummy data variable detected'),
    (r'\btestData\b(?!\s*=\s*\{)', 'Test data variable detected (use fixtures instead)'),
    (r'\bplaceholderData\b', 'Placeholder data variable detected'),
    (r'\bMOCK_', 'Mock constant detected'),
    (r'\bFAKE_', 'Fake constant detected'),
    (r'\/\*\s*mock\s*\*\/', 'Mock comment block detected'),
    (r'#\s*mock\s+data', 'Mock data comment detected'),
    (r'\bgetMockData\b', 'getMockData function detected'),
    (r'\bcreateMockData\b', 'createMockData function detected'),
    (r'\bgenerateFakeData\b', 'generateFakeData function detected'),
    (r'faker\.(name|address|lorem|internet)', 'Faker library mock data detected'),
    (r'\[\s*["\']Mock\s+Item', 'Hardcoded mock item in array'),
    (r'["\']Lorem ipsum', 'Lorem ipsum placeholder text detected'),
    (r'["\']John\s+Doe["\']', 'John Doe placeholder name detected'),
    (r'["\']Jane\s+Doe["\']', 'Jane Doe placeholder name detected'),
    (r'["\']test@test\.com["\']', 'test@test.com placeholder email'),
    (r'["\']example@example\.com["\']', 'example@example.com placeholder email'),
    (r'["\']123-?45-?6789["\']', 'Placeholder SSN detected'),
    (r'["\']555-\d{4}["\']', 'Placeholder phone number (555-xxxx)'),
]

# Stub/Placeholder Code Patterns (FORBIDDEN)
STUB_PATTERNS = [
    (r'//\s*TODO(?!:.*placeholder)', 'TODO comment - implement before marking complete'),
    (r'//\s*FIXME', 'FIXME comment - fix before marking complete'),
    (r'//\s*HACK', 'HACK comment - refactor before marking complete'),
    (r'//\s*XXX', 'XXX comment - address before marking complete'),
    (r'//\s*STUB', 'STUB comment detected'),
    (r'#\s*TODO(?!:.*placeholder)', 'TODO comment - implement before marking complete'),
    (r'#\s*FIXME', 'FIXME comment - fix before marking complete'),
    (r'\bpass\s*#\s*stub', 'Python stub with pass'),
    (r'raise\s+NotImplementedError', 'NotImplementedError - implement before release'),
    (r'throw\s+new\s+Error\s*\(\s*["\']Not\s+implemented', 'Not implemented error'),
    (r'console\.log\s*\(\s*["\']TODO', 'TODO in console.log'),
    (r'return\s+null\s*//\s*stub', 'Null return stub'),
    (r'return\s+\[\s*\]\s*//\s*stub', 'Empty array return stub'),
    (r'return\s+\{\s*\}\s*//\s*stub', 'Empty object return stub'),
    (r'\/\*\s*placeholder\s*\*\/', 'Placeholder comment block'),
    (r'__placeholder__', 'Placeholder marker detected'),
    (r'\bTBD\b', 'TBD (To Be Determined) marker'),
    (r'\bWIP\b', 'WIP (Work In Progress) marker'),
]

# Security Issue Patterns (OWASP Top 10 2021)
SECURITY_PATTERNS = [
    # A01:2021 - Broken Access Control
    (r'\.innerHTML\s*=', 'A01:2021 - innerHTML assignment (XSS risk)', 'A01:2021 - Broken Access Control'),
    (r'document\.write\s*\(', 'A01:2021 - document.write (XSS risk)', 'A01:2021 - Broken Access Control'),
    (r'eval\s*\(', 'A01:2021 - eval() usage (code injection risk)', 'A01:2021 - Broken Access Control'),
    (r'new\s+Function\s*\(', 'A01:2021 - Function constructor (code injection)', 'A01:2021 - Broken Access Control'),

    # A02:2021 - Cryptographic Failures
    (r'\bmd5\s*\(', 'A02:2021 - MD5 is cryptographically weak', 'A02:2021 - Cryptographic Failures'),
    (r'\bsha1\s*\(', 'A02:2021 - SHA1 is cryptographically weak', 'A02:2021 - Cryptographic Failures'),
    (r'password\s*=\s*["\'][^"\']+["\']', 'A02:2021 - Hardcoded password detected', 'A02:2021 - Cryptographic Failures'),
    (r'secret\s*=\s*["\'][^"\']{8,}["\']', 'A02:2021 - Hardcoded secret detected', 'A02:2021 - Cryptographic Failures'),
    (r'api[_-]?key\s*=\s*["\'][a-zA-Z0-9]{16,}["\']', 'A02:2021 - Hardcoded API key', 'A02:2021 - Cryptographic Failures'),

    # A03:2021 - Injection
    (r'execute\s*\(\s*["\'].*\+', 'A03:2021 - SQL string concatenation (injection risk)', 'A03:2021 - Injection'),
    (r'query\s*\(\s*["\'].*\$\{', 'A03:2021 - SQL template literal (injection risk)', 'A03:2021 - Injection'),
    (r'exec\s*\(\s*["\'].*\+', 'A03:2021 - Command string concatenation (injection risk)', 'A03:2021 - Injection'),
    (r'subprocess\.call\s*\(\s*["\'].*\+', 'A03:2021 - Command injection risk', 'A03:2021 - Injection'),
    (r'os\.system\s*\(', 'A03:2021 - os.system (command injection risk)', 'A03:2021 - Injection'),
    (r'dangerouslySetInnerHTML', 'A03:2021 - dangerouslySetInnerHTML (XSS risk)', 'A03:2021 - Injection'),
    (r'v-html\s*=', 'A03:2021 - v-html directive (XSS risk in Vue)', 'A03:2021 - Injection'),

    # A04:2021 - Insecure Design
    (r'cors\s*\(\s*\{\s*origin\s*:\s*["\']\*["\']', 'A04:2021 - CORS allows all origins', 'A04:2021 - Insecure Design'),
    (r'Access-Control-Allow-Origin["\']?\s*:\s*["\']?\*', 'A04:2021 - CORS wildcard origin', 'A04:2021 - Insecure Design'),

    # A05:2021 - Security Misconfiguration
    (r'debug\s*=\s*True', 'A05:2021 - Debug mode enabled in production code', 'A05:2021 - Security Misconfiguration'),
    (r'DEBUG\s*=\s*true', 'A05:2021 - Debug mode enabled', 'A05:2021 - Security Misconfiguration'),
    (r'disable.*security', 'A05:2021 - Security disabled', 'A05:2021 - Security Misconfiguration'),
    (r'verify\s*=\s*False', 'A05:2021 - SSL verification disabled', 'A05:2021 - Security Misconfiguration'),
    (r'rejectUnauthorized\s*:\s*false', 'A05:2021 - TLS verification disabled', 'A05:2021 - Security Misconfiguration'),

    # A07:2021 - Identification and Authentication Failures
    (r'password.*length.*<\s*[1-7]\b', 'A07:2021 - Weak password length requirement', 'A07:2021 - Auth Failures'),
    (r'bcrypt.*rounds.*<\s*10', 'A07:2021 - Weak bcrypt rounds', 'A07:2021 - Auth Failures'),
    (r'jwt\.sign\s*\([^)]*expiresIn\s*:\s*["\']?\d+d', 'A07:2021 - Long JWT expiration (>1 day)', 'A07:2021 - Auth Failures'),

    # A08:2021 - Software and Data Integrity Failures
    (r'npm\s+install\s+--no-save', 'A08:2021 - npm install without lockfile', 'A08:2021 - Integrity Failures'),
    (r'pip\s+install(?!.*==)', 'A08:2021 - pip install without version pinning', 'A08:2021 - Integrity Failures'),

    # A09:2021 - Security Logging and Monitoring Failures
    (r'catch\s*\([^)]*\)\s*\{\s*\}', 'A09:2021 - Empty catch block (silent failure)', 'A09:2021 - Logging Failures'),
    (r'except\s*:\s*pass', 'A09:2021 - Bare except with pass (silent failure)', 'A09:2021 - Logging Failures'),

    # A10:2021 - Server-Side Request Forgery
    (r'fetch\s*\(\s*(?:req\.|request\.)', 'A10:2021 - Potential SSRF (user-controlled URL)', 'A10:2021 - SSRF'),
    (r'axios\s*\.\s*get\s*\(\s*(?:req\.|request\.)', 'A10:2021 - Potential SSRF', 'A10:2021 - SSRF'),
    (r'requests\.get\s*\(\s*(?:req\.|request\.)', 'A10:2021 - Potential SSRF', 'A10:2021 - SSRF'),
]

# Legitimate Placeholder Patterns (to be documented, not errors)
LEGITIMATE_PLACEHOLDER_PATTERNS = [
    (r'(?:ANTHROPIC|OPENAI|STRIPE|TWILIO|SENDGRID|AWS)_API_KEY\s*[=:]\s*["\'](?:your[_-]?|<|placeholder|xxx)', 'api_key', 'API key placeholder'),
    (r'(?:DATABASE|DB|MONGO|POSTGRES|MYSQL)_(?:URL|URI|HOST)\s*[=:]\s*["\'](?:your[_-]?|<|placeholder|localhost)', 'config', 'Database connection placeholder'),
    (r'(?:SECRET|JWT|SESSION)_(?:KEY|SECRET)\s*[=:]\s*["\'](?:your[_-]?|<|change[_-]?me|placeholder)', 'secret', 'Secret key placeholder'),
    (r'(?:SMTP|MAIL|EMAIL)_(?:HOST|SERVER|PASSWORD)\s*[=:]\s*["\'](?:your[_-]?|<|placeholder)', 'credential', 'Email configuration placeholder'),
    (r'(?:OAUTH|AUTH)_(?:CLIENT_ID|CLIENT_SECRET)\s*[=:]\s*["\'](?:your[_-]?|<|placeholder)', 'credential', 'OAuth credential placeholder'),
    (r'(?:WEBHOOK|CALLBACK)_URL\s*[=:]\s*["\'](?:https?://(?:your|example|placeholder))', 'url', 'Webhook URL placeholder'),
    (r'process\.env\.(\w+)', 'env_var', 'Environment variable reference'),
    (r'os\.environ(?:\.get)?\s*\(\s*["\'](\w+)["\']', 'env_var', 'Environment variable reference'),
]


def is_in_pattern_definition(line: str) -> bool:
    """Check if a line appears to be defining a regex pattern or documentation."""
    # Skip lines that are clearly pattern definitions or documentation
    pattern_indicators = [
        r"^\s*\(",  # Tuple/list item starting with (
        r"r['\"]",  # Raw string (regex pattern)
        r"re\.(search|match|findall|sub)",  # Regex function calls
        r"Pattern.*=",  # Pattern variable assignment
        r"_PATTERNS?\s*=",  # Pattern list definition
        r"#.*pattern",  # Comment about patterns
        r"description.*=",  # Description string
        r"message.*=",  # Message string
        r'^\s*["\'].*["\'],?\s*$',  # String-only line (documentation/checklist)
        r"checks.*=",  # Checklist definition
        r"Avoid\s+",  # Documentation about what to avoid
        r"Don't\s+",  # Documentation about what not to do
        r"Never\s+",  # Documentation warnings
    ]
    for indicator in pattern_indicators:
        if re.search(indicator, line, re.IGNORECASE):
            return True
    return False


def is_in_string_literal(line: str, match_start: int) -> bool:
    """Check if a match position is inside a string literal (approximate)."""
    # Count quotes before the match position
    before = line[:match_start]
    single_quotes = before.count("'") - before.count("\\'")
    double_quotes = before.count('"') - before.count('\\"')

    # If odd number of quotes, we're likely inside a string
    return (single_quotes % 2 == 1) or (double_quotes % 2 == 1)


def scan_file(file_path: Path) -> tuple[list[CodeIssue], list[Placeholder]]:
    """Scan a single file for issues and placeholders."""
    issues = []
    placeholders = []

    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        lines = content.split('\n')
    except Exception as e:
        logger.warning(f"Could not read file {file_path}: {e}")
        return issues, placeholders

    rel_path = str(file_path)

    # Check if this is a test file (more lenient with patterns)
    is_test_file = bool(re.search(r'(test|spec|__tests__)', rel_path, re.IGNORECASE))

    for line_num, line in enumerate(lines, 1):
        # Skip empty lines and very long lines (likely minified)
        if not line.strip() or len(line) > 500:
            continue

        # Skip lines that are pattern definitions or documentation
        if is_in_pattern_definition(line):
            continue

        # Check for mock data patterns
        for pattern, message in MOCK_DATA_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                issues.append(CodeIssue(
                    severity='high',
                    category='mock_data',
                    file_path=rel_path,
                    line_number=line_num,
                    line_content=line.strip()[:100],
                    message=message,
                ))

        # Check for stub patterns
        for pattern, message in STUB_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                issues.append(CodeIssue(
                    severity='medium',
                    category='placeholder',
                    file_path=rel_path,
                    line_number=line_num,
                    line_content=line.strip()[:100],
                    message=message,
                ))

        # Check for security patterns
        for pattern, message, owasp in SECURITY_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                issues.append(CodeIssue(
                    severity='critical' if 'injection' in message.lower() else 'high',
                    category='security',
                    file_path=rel_path,
                    line_number=line_num,
                    line_content=line.strip()[:100],
                    message=message,
                    owasp_category=owasp,
                ))

        # Check for legitimate placeholders
        for pattern, placeholder_type, description in LEGITIMATE_PLACEHOLDER_PATTERNS:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                placeholders.append(Placeholder(
                    file_path=rel_path,
                    line_number=line_num,
                    placeholder_type=placeholder_type,
                    current_value=line.strip()[:100],
                    description=description,
                    required_action=f"Replace with actual {placeholder_type} value",
                ))

    return issues, placeholders


def scan_directory(project_dir: Path) -> tuple[list[CodeIssue], list[Placeholder]]:
    """Scan entire project directory for issues and placeholders."""
    all_issues = []
    all_placeholders = []

    for file_path in project_dir.rglob('*'):
        # Skip directories
        if file_path.is_dir():
            continue

        # Skip non-code files
        if file_path.suffix.lower() not in CODE_EXTENSIONS:
            continue

        # Skip excluded directories
        if any(skip_dir in file_path.parts for skip_dir in SKIP_DIRS):
            continue

        # Skip specific files
        if file_path.name in SKIP_FILES:
            continue

        issues, placeholders = scan_file(file_path)
        all_issues.extend(issues)
        all_placeholders.extend(placeholders)

    return all_issues, all_placeholders


def generate_placeholder_document(project_dir: Path, placeholders: list[Placeholder]) -> Path:
    """Generate a markdown document listing all placeholders that need replacement."""
    doc_path = project_dir / "PLACEHOLDERS.md"

    # Group placeholders by type
    by_type: dict[str, list[Placeholder]] = {}
    for p in placeholders:
        if p.placeholder_type not in by_type:
            by_type[p.placeholder_type] = []
        by_type[p.placeholder_type].append(p)

    content = f"""# Placeholder Configuration Required

Generated: {datetime.now().isoformat()}

This document lists all configuration placeholders that need to be replaced with actual values before deployment.

## Summary

| Type | Count |
|------|-------|
"""

    for ptype, items in sorted(by_type.items()):
        content += f"| {ptype} | {len(items)} |\n"

    content += f"\n**Total: {len(placeholders)} placeholders**\n\n"
    content += "---\n\n"

    # Detail each type
    type_descriptions = {
        'api_key': 'API Keys',
        'secret': 'Secret Keys',
        'credential': 'Credentials',
        'config': 'Configuration Values',
        'url': 'URLs and Endpoints',
        'env_var': 'Environment Variables',
    }

    for ptype, items in sorted(by_type.items()):
        content += f"## {type_descriptions.get(ptype, ptype.title())}\n\n"

        for p in items:
            content += f"### `{p.file_path}:{p.line_number}`\n\n"
            content += f"**Type:** {p.placeholder_type}  \n"
            content += f"**Description:** {p.description}  \n"
            content += f"**Action Required:** {p.required_action}  \n\n"
            content += f"```\n{p.current_value}\n```\n\n"

    content += """---

## How to Configure

### Development
1. Copy `.env.example` to `.env`
2. Fill in development values
3. Never commit `.env` to version control

### Production
1. Set environment variables in your deployment platform
2. Use secrets management (AWS Secrets Manager, Vault, etc.)
3. Rotate credentials regularly

### Security Notes
- Never hardcode secrets in source code
- Use environment variables for all sensitive configuration
- Ensure `.env` is in `.gitignore`
"""

    doc_path.write_text(content, encoding='utf-8')
    logger.info(f"Generated placeholder document: {doc_path}")

    return doc_path


def generate_validation_report(
    project_dir: Path,
    issues: list[CodeIssue],
    placeholders: list[Placeholder]
) -> dict:
    """Generate a validation report summary."""
    # Count by severity
    severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}
    for issue in issues:
        severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1

    # Count by category
    category_counts = {}
    for issue in issues:
        category_counts[issue.category] = category_counts.get(issue.category, 0) + 1

    # OWASP violations
    owasp_counts = {}
    for issue in issues:
        if issue.owasp_category:
            owasp_counts[issue.owasp_category] = owasp_counts.get(issue.owasp_category, 0) + 1

    # Determine if code passes validation
    passes = severity_counts['critical'] == 0 and severity_counts['high'] == 0

    return {
        'passes': passes,
        'total_issues': len(issues),
        'total_placeholders': len(placeholders),
        'severity_counts': severity_counts,
        'category_counts': category_counts,
        'owasp_violations': owasp_counts,
        'blocking_issues': [asdict(i) for i in issues if i.severity in ('critical', 'high')][:20],
        'placeholder_summary': {
            p.placeholder_type: sum(1 for x in placeholders if x.placeholder_type == p.placeholder_type)
            for p in placeholders
        },
    }


def validate_project(project_dir: Path) -> dict:
    """
    Main entry point: validate entire project and return report.

    Returns:
        Dictionary with validation results including:
        - passes: bool (True if no critical/high issues)
        - issues: List of all issues found
        - placeholders: List of placeholders to document
        - report: Summary statistics
    """
    project_path = Path(project_dir)

    if not project_path.exists():
        return {
            'passes': False,
            'error': f"Project directory does not exist: {project_dir}",
        }

    issues, placeholders = scan_directory(project_path)
    report = generate_validation_report(project_path, issues, placeholders)

    # Generate placeholder document if there are any
    placeholder_doc = None
    if placeholders:
        placeholder_doc = generate_placeholder_document(project_path, placeholders)

    return {
        'passes': report['passes'],
        'issues': [asdict(i) for i in issues],
        'placeholders': [asdict(p) for p in placeholders],
        'report': report,
        'placeholder_document': str(placeholder_doc) if placeholder_doc else None,
    }
