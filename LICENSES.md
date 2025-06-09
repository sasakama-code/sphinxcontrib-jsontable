# 📋 Third-Party Licenses & Attribution

This document provides comprehensive license information for all third-party software components and models used in the **sphinxcontrib-jsontable** project.

## 📖 Overview

This project utilizes various open-source software libraries and the PLaMo-Embedding-1B model. All components are used in compliance with their respective licenses.

---

## 🤖 AI Model Licenses

### PLaMo-Embedding-1B
- **Provider**: Preferred Networks, Inc.
- **License**: Apache License 2.0
- **Commercial Use**: ✅ Permitted
- **Source**: https://huggingface.co/pfnet/plamo-embedding-1b
- **Description**: Japanese text embedding model optimized for information retrieval, text classification, and clustering tasks.

**License Details**:
```
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

---

## 📦 Core Dependencies

### Production Dependencies

| Package | Version | License | Description |
|---------|---------|---------|-------------|
| **Sphinx** | ≥3.0 | BSD License | Python documentation generator |
| **docutils** | ≥0.18 | Public Domain/BSD/GPL | Python Documentation Utilities |
| **NumPy** | ≥2.2.6 | BSD License | Fundamental package for scientific computing |
| **pytest-cov** | ≥6.1.1 | MIT License | Coverage plugin for pytest |

### Development Dependencies

| Package | Version | License | Description |
|---------|---------|---------|-------------|
| **pytest** | ≥8.3.5 | MIT License | Testing framework |
| **pytest-benchmark** | ≥5.1.0 | BSD License | Benchmarking plugin for pytest |
| **pytest-asyncio** | ≥0.24.0 | Apache License 2.0 | Asyncio support for pytest |
| **coverage** | ≥7.6.1 | Apache License 2.0 | Code coverage measurement |
| **mypy** | ≥1.14.1 | MIT License | Static type checker |
| **ruff** | ≥0.11.11 | MIT License | Fast Python linter and formatter |
| **pre-commit** | ≥3.5.0 | MIT License | Git pre-commit hook framework |
| **pytest-mock** | ≥3.10.0 | MIT License | Thin-wrapper around mock for pytest |
| **pytest-xdist** | ≥3.2.0 | MIT License | Distributed testing plugin |

### Build & Distribution

| Package | Version | License | Description |
|---------|---------|---------|-------------|
| **build** | ≥1.2.2.post1 | MIT License | Modern Python build system |
| **twine** | ≥6.1.0 | Apache License 2.0 | PyPI package uploader |
| **setuptools** | ≥77.0.0 | MIT License | Python package development |
| **wheel** | - | MIT License | Built-package format for Python |

### Documentation

| Package | Version | License | Description |
|---------|---------|---------|-------------|
| **sphinx-rtd-theme** | ≥3.0.2 | MIT License | Read the Docs Sphinx theme |
| **sphinx-autodoc-typehints** | ≥2.0.1 | MIT License | Type hints support for Sphinx |
| **myst-parser** | ≥0.18 | MIT License | MyST Markdown parser for Sphinx |

---

## 🔒 Security Tools (CI/CD)

### Dependency Scanning & SAST

| Tool | License | Description |
|------|---------|-------------|
| **safety** | MIT License | Vulnerability scanner for Python dependencies |
| **pip-audit** | Apache License 2.0 | Official PyPA vulnerability scanner |
| **bandit** | Apache License 2.0 | Security-oriented static analyzer for Python |
| **semgrep** | LGPL 2.1 | Static analysis tool for finding bugs and security issues |

### Code Quality & Analysis

| Tool | License | Description |
|------|---------|-------------|
| **CodeQL** | MIT License | GitHub's static analysis engine |
| **cyclonedx-bom** | Apache License 2.0 | SBOM generator for CycloneDX format |

---

## 🌐 GitHub Actions

### Official Actions

| Action | License | Description |
|--------|---------|-------------|
| **actions/checkout** | MIT License | Checkout repository content |
| **actions/setup-python** | MIT License | Set up Python environment |
| **actions/cache** | MIT License | Cache dependencies and build outputs |
| **actions/upload-artifact** | MIT License | Upload build artifacts |
| **codecov/codecov-action** | MIT License | Upload coverage to Codecov |
| **github/codeql-action** | MIT License | GitHub CodeQL analysis |
| **pypa/gh-action-pypi-publish** | BSD 3-Clause | Official PyPI publishing action |

---

## 📝 License Classifications

### Permissive Licenses (Commercial Use Allowed)

#### MIT License
**Packages**: pytest, mypy, ruff, pre-commit, pytest-mock, pytest-xdist, build, sphinx-rtd-theme, sphinx-autodoc-typehints, myst-parser, safety, CodeQL, GitHub Actions

**Summary**: Very permissive license allowing commercial use, modification, and distribution with minimal restrictions.

#### BSD License  
**Packages**: Sphinx, NumPy, pytest-benchmark

**Summary**: Permissive license similar to MIT, allowing free use with attribution requirements.

#### Apache License 2.0
**Packages**: PLaMo-Embedding-1B, coverage, pytest-asyncio, twine, pip-audit, bandit, cyclonedx-bom

**Summary**: Permissive license with additional patent protection clauses.

### Multiple License Options

#### docutils
**Available Licenses**: Public Domain, Python License, 2-Clause BSD, GPL 3
**Our Usage**: Public Domain (most permissive option)

---

## ✅ Compliance Statement

### Commercial Use Authorization
- ✅ All dependencies support commercial use
- ✅ No copyleft restrictions in production code
- ✅ All license obligations met through attribution

### Attribution Requirements Met
- ✅ MIT License: Copyright notices preserved
- ✅ BSD License: Attribution and disclaimer included
- ✅ Apache License 2.0: License and notice files maintained

### SBOM Compliance
- ✅ CycloneDx SBOM generated automatically in CI/CD
- ✅ Vulnerability scanning integrated
- ✅ Dependency audit automated

---

## 🔄 License Updates

### Maintenance Policy
- **Quarterly Reviews**: License compatibility verification
- **Automated Scanning**: CI/CD pipeline includes license checks
- **Version Updates**: Dependencies updated with license verification

### Contact Information
For license-related questions or concerns:
- **Email**: sasakamacode@gmail.com
- **Repository**: https://github.com/sasakama-code/sphinxcontrib-jsontable
- **Issues**: https://github.com/sasakama-code/sphinxcontrib-jsontable/issues

---

## 📚 License Text References

### Full License Texts
Complete license texts are available at:
- **MIT License**: https://opensource.org/licenses/MIT
- **BSD License**: https://opensource.org/licenses/BSD-3-Clause
- **Apache License 2.0**: https://apache.org/licenses/LICENSE-2.0
- **Public Domain**: https://creativecommons.org/publicdomain/zero/1.0/

### Project License
This project itself is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

**Last Updated**: 2025-06-09  
**Document Version**: 1.0  
**Generated**: Automatically maintained via CI/CD pipeline

*This document is automatically updated when dependencies change through automated license scanning and SBOM generation.*