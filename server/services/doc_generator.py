"""
Technical Documentation Generator
=================================

Generates comprehensive technical documentation for codebases.
Creates documentation about architecture, components, APIs, and inner workings.
"""

import json
import logging
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# File extensions for different languages
LANGUAGE_EXTENSIONS = {
    'javascript': {'.js', '.jsx', '.mjs'},
    'typescript': {'.ts', '.tsx'},
    'vue': {'.vue'},
    'python': {'.py'},
    'css': {'.css', '.scss', '.sass', '.less'},
    'html': {'.html', '.htm'},
    'json': {'.json'},
    'markdown': {'.md'},
}

# Directories to skip
SKIP_DIRS = {
    'node_modules', '.git', 'dist', 'build', '.next', '.nuxt',
    '__pycache__', 'venv', '.venv', 'env', '.env',
    'coverage', '.pytest_cache', '.mypy_cache', '.cache',
}


@dataclass
class FileInfo:
    """Information about a source file."""
    path: str
    language: str
    line_count: int
    size_bytes: int
    has_tests: bool
    exports: list[str]
    imports: list[str]
    functions: list[str]
    classes: list[str]
    description: Optional[str] = None


@dataclass
class ComponentInfo:
    """Information about a component/module."""
    name: str
    path: str
    type: str  # component, page, service, util, model, etc.
    description: str
    dependencies: list[str]
    exports: list[str]
    props: Optional[list[dict]] = None  # For Vue/React components


def detect_language(file_path: Path) -> Optional[str]:
    """Detect programming language from file extension."""
    ext = file_path.suffix.lower()
    for lang, exts in LANGUAGE_EXTENSIONS.items():
        if ext in exts:
            return lang
    return None


def extract_file_info(file_path: Path, project_dir: Path) -> Optional[FileInfo]:
    """Extract information from a source file."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        lines = content.split('\n')
        language = detect_language(file_path)

        if not language:
            return None

        rel_path = str(file_path.relative_to(project_dir))

        # Extract exports
        exports = []
        if language in ('javascript', 'typescript'):
            exports = re.findall(r'export\s+(?:default\s+)?(?:const|let|var|function|class|interface|type)\s+(\w+)', content)
            exports += re.findall(r'export\s*\{\s*([^}]+)\s*\}', content)
        elif language == 'python':
            exports = re.findall(r'^(?:def|class)\s+(\w+)', content, re.MULTILINE)
        elif language == 'vue':
            exports = re.findall(r'name:\s*["\'](\w+)["\']', content)

        # Extract imports
        imports = []
        if language in ('javascript', 'typescript', 'vue'):
            imports = re.findall(r'import\s+.*?from\s+["\']([^"\']+)["\']', content)
            imports += re.findall(r'require\s*\(\s*["\']([^"\']+)["\']', content)
        elif language == 'python':
            imports = re.findall(r'^(?:from\s+(\S+)\s+)?import\s+(\S+)', content, re.MULTILINE)
            imports = [i[0] or i[1] for i in imports]

        # Extract functions
        functions = []
        if language in ('javascript', 'typescript'):
            functions = re.findall(r'(?:async\s+)?function\s+(\w+)', content)
            functions += re.findall(r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>', content)
        elif language == 'python':
            functions = re.findall(r'^def\s+(\w+)', content, re.MULTILINE)
        elif language == 'vue':
            functions = re.findall(r'(?:const|let|var|function)\s+(\w+)', content)

        # Extract classes
        classes = []
        if language in ('javascript', 'typescript'):
            classes = re.findall(r'class\s+(\w+)', content)
        elif language == 'python':
            classes = re.findall(r'^class\s+(\w+)', content, re.MULTILINE)

        # Check if test file
        has_tests = bool(re.search(r'(?:test|spec|__tests__)', rel_path, re.IGNORECASE))
        has_tests = has_tests or bool(re.search(r'(?:describe|it|test|expect)\s*\(', content))

        # Extract description from file docstring/comment
        description = None
        if language == 'python':
            match = re.match(r'^["\'\s]*(?:"""|\'\'\')(.*?)(?:"""|\'\'\')', content, re.DOTALL)
            if match:
                description = match.group(1).strip().split('\n')[0]
        elif language in ('javascript', 'typescript'):
            match = re.match(r'^\s*/\*\*?\s*(.*?)\s*\*/', content, re.DOTALL)
            if match:
                description = match.group(1).strip().split('\n')[0].replace('*', '').strip()

        return FileInfo(
            path=rel_path,
            language=language,
            line_count=len(lines),
            size_bytes=len(content),
            has_tests=has_tests,
            exports=list(set(exports))[:20],  # Limit to top 20
            imports=list(set(imports))[:30],  # Limit to top 30
            functions=list(set(functions))[:30],
            classes=list(set(classes))[:20],
            description=description,
        )

    except Exception as e:
        logger.warning(f"Could not extract info from {file_path}: {e}")
        return None


def analyze_project_structure(project_dir: Path) -> dict:
    """Analyze project structure and return summary."""
    structure = {
        'directories': [],
        'file_count': 0,
        'line_count': 0,
        'languages': {},
        'frameworks': [],
        'files': [],
    }

    # Detect frameworks from package.json or requirements.txt
    package_json = project_dir / 'package.json'
    if package_json.exists():
        try:
            pkg = json.loads(package_json.read_text())
            deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}

            if 'vue' in deps:
                structure['frameworks'].append('Vue.js')
            if 'nuxt' in deps:
                structure['frameworks'].append('Nuxt.js')
            if 'react' in deps:
                structure['frameworks'].append('React')
            if 'next' in deps:
                structure['frameworks'].append('Next.js')
            if 'express' in deps:
                structure['frameworks'].append('Express')
            if 'fastify' in deps:
                structure['frameworks'].append('Fastify')
            if 'tailwindcss' in deps:
                structure['frameworks'].append('Tailwind CSS')
            if 'prisma' in deps:
                structure['frameworks'].append('Prisma')
        except Exception:
            pass

    requirements = project_dir / 'requirements.txt'
    if requirements.exists():
        try:
            reqs = requirements.read_text().lower()
            if 'fastapi' in reqs:
                structure['frameworks'].append('FastAPI')
            if 'django' in reqs:
                structure['frameworks'].append('Django')
            if 'flask' in reqs:
                structure['frameworks'].append('Flask')
            if 'sqlalchemy' in reqs:
                structure['frameworks'].append('SQLAlchemy')
        except Exception:
            pass

    # Scan files
    for file_path in project_dir.rglob('*'):
        if file_path.is_dir():
            continue

        if any(skip_dir in file_path.parts for skip_dir in SKIP_DIRS):
            continue

        language = detect_language(file_path)
        if not language:
            continue

        file_info = extract_file_info(file_path, project_dir)
        if file_info:
            structure['files'].append(asdict(file_info))
            structure['file_count'] += 1
            structure['line_count'] += file_info.line_count
            structure['languages'][language] = structure['languages'].get(language, 0) + 1

    # Get unique directories
    dirs = set()
    for f in structure['files']:
        path_parts = Path(f['path']).parts[:-1]
        for i in range(len(path_parts)):
            dirs.add('/'.join(path_parts[:i+1]))
    structure['directories'] = sorted(dirs)

    return structure


def generate_architecture_section(structure: dict) -> str:
    """Generate architecture overview section."""
    content = "## Architecture Overview\n\n"

    # Frameworks
    if structure['frameworks']:
        content += "### Technology Stack\n\n"
        for fw in structure['frameworks']:
            content += f"- **{fw}**\n"
        content += "\n"

    # Languages
    content += "### Languages\n\n"
    content += "| Language | Files | Percentage |\n"
    content += "|----------|-------|------------|\n"
    total = sum(structure['languages'].values())
    for lang, count in sorted(structure['languages'].items(), key=lambda x: -x[1]):
        pct = (count / total * 100) if total > 0 else 0
        content += f"| {lang.title()} | {count} | {pct:.1f}% |\n"
    content += "\n"

    # Project stats
    content += "### Project Statistics\n\n"
    content += f"- **Total Files:** {structure['file_count']}\n"
    content += f"- **Total Lines of Code:** {structure['line_count']:,}\n"
    content += f"- **Directories:** {len(structure['directories'])}\n\n"

    return content


def generate_directory_structure(structure: dict) -> str:
    """Generate directory structure section."""
    content = "## Directory Structure\n\n"
    content += "```\n"

    # Build tree
    dirs = sorted(structure['directories'])
    for d in dirs[:30]:  # Limit depth
        depth = d.count('/')
        indent = "  " * depth
        name = d.split('/')[-1]
        content += f"{indent}{name}/\n"

    if len(dirs) > 30:
        content += f"  ... and {len(dirs) - 30} more directories\n"

    content += "```\n\n"
    return content


def generate_components_section(structure: dict) -> str:
    """Generate components/modules documentation."""
    content = "## Components & Modules\n\n"

    # Group files by directory
    by_dir: dict[str, list] = {}
    for f in structure['files']:
        dir_path = str(Path(f['path']).parent)
        if dir_path == '.':
            dir_path = 'root'
        if dir_path not in by_dir:
            by_dir[dir_path] = []
        by_dir[dir_path].append(f)

    # Document key directories
    key_dirs = ['src', 'components', 'pages', 'views', 'api', 'services', 'utils', 'lib', 'stores', 'composables']

    for key_dir in key_dirs:
        matching_dirs = [d for d in by_dir.keys() if key_dir in d.lower()]
        if not matching_dirs:
            continue

        content += f"### {key_dir.title()}\n\n"

        for dir_path in sorted(matching_dirs)[:5]:  # Limit subdirs
            files = by_dir[dir_path]

            for f in files[:10]:  # Limit files per dir
                content += f"#### `{f['path']}`\n\n"

                if f.get('description'):
                    content += f"{f['description']}\n\n"

                if f.get('classes'):
                    content += f"**Classes:** `{'`, `'.join(f['classes'][:5])}`\n\n"

                if f.get('functions'):
                    content += f"**Functions:** `{'`, `'.join(f['functions'][:8])}`\n\n"

                if f.get('exports'):
                    content += f"**Exports:** `{'`, `'.join(f['exports'][:5])}`\n\n"

    return content


def generate_api_section(structure: dict) -> str:
    """Generate API documentation section."""
    content = "## API Reference\n\n"

    # Find API-related files
    api_files = [f for f in structure['files']
                 if any(x in f['path'].lower() for x in ['api', 'routes', 'endpoints', 'server'])]

    if not api_files:
        content += "_No API files detected._\n\n"
        return content

    content += "### Endpoints\n\n"

    for f in api_files[:15]:
        content += f"#### `{f['path']}`\n\n"

        if f.get('functions'):
            content += "| Function | Description |\n"
            content += "|----------|-------------|\n"
            for func in f['functions'][:10]:
                content += f"| `{func}` | |\n"
            content += "\n"

    return content


def generate_technical_documentation(project_dir: Path) -> tuple[str, Path]:
    """
    Generate comprehensive technical documentation for a project.

    Returns:
        Tuple of (markdown content, output file path)
    """
    structure = analyze_project_structure(project_dir)

    # Build the documentation
    doc = f"""# Technical Documentation

**Project:** {project_dir.name}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Files:** {structure['file_count']}
**Total Lines:** {structure['line_count']:,}

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Directory Structure](#directory-structure)
3. [Components & Modules](#components--modules)
4. [API Reference](#api-reference)
5. [Dependencies](#dependencies)
6. [Configuration](#configuration)
7. [Development Guide](#development-guide)

---

"""

    doc += generate_architecture_section(structure)
    doc += generate_directory_structure(structure)
    doc += generate_components_section(structure)
    doc += generate_api_section(structure)

    # Dependencies section
    doc += "## Dependencies\n\n"

    package_json = project_dir / 'package.json'
    if package_json.exists():
        try:
            pkg = json.loads(package_json.read_text())
            deps = pkg.get('dependencies', {})
            dev_deps = pkg.get('devDependencies', {})

            if deps:
                doc += "### Production Dependencies\n\n"
                doc += "| Package | Version |\n"
                doc += "|---------|---------|n"
                for name, version in sorted(deps.items())[:20]:
                    doc += f"| {name} | {version} |\n"
                doc += "\n"

            if dev_deps:
                doc += "### Development Dependencies\n\n"
                doc += "| Package | Version |\n"
                doc += "|---------|---------|\n"
                for name, version in sorted(dev_deps.items())[:15]:
                    doc += f"| {name} | {version} |\n"
                doc += "\n"
        except Exception:
            pass

    # Configuration section
    doc += "## Configuration\n\n"
    doc += "### Environment Variables\n\n"

    env_example = project_dir / '.env.example'
    if env_example.exists():
        doc += "```bash\n"
        doc += env_example.read_text()[:2000]
        doc += "\n```\n\n"
    else:
        doc += "_No `.env.example` file found. Create one to document required environment variables._\n\n"

    # Development guide
    doc += """## Development Guide

### Getting Started

1. Clone the repository
2. Install dependencies
3. Configure environment variables
4. Run the development server

### Scripts

"""

    if package_json.exists():
        try:
            pkg = json.loads(package_json.read_text())
            scripts = pkg.get('scripts', {})
            if scripts:
                doc += "| Command | Description |\n"
                doc += "|---------|-------------|\n"
                for name, cmd in sorted(scripts.items()):
                    doc += f"| `npm run {name}` | `{cmd[:50]}` |\n"
                doc += "\n"
        except Exception:
            pass

    doc += """
### Code Style

- Follow the existing code patterns
- Use TypeScript/type hints where applicable
- Write tests for new functionality
- Document public APIs

---

*This documentation was automatically generated. For more details, refer to the source code and inline comments.*
"""

    # Write to file
    output_path = project_dir / 'TECHNICAL_DOCS.md'
    output_path.write_text(doc, encoding='utf-8')

    return doc, output_path
