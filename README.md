# sphinxcontrib-jsontable

[![Tests](https://github.com/sasakama-code/sphinxcontrib-jsontable/actions/workflows/ci.yml/badge.svg)](https://github.com/sasakama-code/sphinxcontrib-jsontable/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/sasakama-code/sphinxcontrib-jsontable/graph/badge.svg)](https://codecov.io/gh/sasakama-code/sphinxcontrib-jsontable)
[![Python](https://img.shields.io/pypi/pyversions/sphinxcontrib-jsontable.svg)](https://pypi.org/project/sphinxcontrib-jsontable/)

**Languages:** [English](README.md) | [日本語](README_ja.md)

A Sphinx extension that renders JSON data as structured tables with advanced **RAG (Retrieval Augmented Generation)** capabilities. Features Japanese language processing optimized for **PLaMo-Embedding-1B**.

## 🚀 What's New in v0.3.0

✨ **RAG Integration** - `enhanced-jsontable` directive with automatic metadata generation  
🇯🇵 **Japanese Entity Recognition** - Native support for 人名, 地名, 組織名, ビジネス用語  
📤 **Multi-format Export** - JSON-LD, OpenSearch, PLaMo-ready formats  
🤖 **PLaMo-Embedding-1B Integration** - 1024-dimensional vector generation for Japanese text  

### 📚 **Quick Start & Documentation**
- **🚀 [5-Minute Quick Start](docs/v0.3.0_quick_start.md)** - Start using new features immediately
- **🎓 [Feature Guide](docs/v0.3.0_feature_tutorial.md)** - Complete reference with examples

## Background / Motivation

In recent years, there has been an increasing trend of using documents as data sources for Retrieval Augmented Generation (RAG). However, tabular data within documents often loses its structural relevance during the process of being ingested by RAG systems. This presented a challenge where the original value of the structured data could not be fully leveraged.

Against this backdrop, **sphinxcontrib-jsontable v0.3.0** was developed to directly embed structured data as meaningful tables in Sphinx-generated documents, with advanced RAG capabilities that ensure readability and semantic understanding effectively coexist. The integration with PLaMo-Embedding-1B provides Japanese-specialized RAG functionality for documentation systems.

## Installation

```bash
pip install sphinxcontrib-jsontable
```

## Quick Start

### 1. Enable Extension
```python
# conf.py
extensions = ['sphinxcontrib.jsontable']
```

### 2. Basic Usage
```rst
.. jsontable:: data/users.json
   :header:
```

### 3. New RAG Features
```rst
.. enhanced-jsontable:: data/companies.json
   :header:
   :entity-recognition: japanese
   :export-format: opensearch
```

## Core Features

- **Traditional Table Rendering** - JSON files and inline data to HTML tables
- **Japanese Entity Recognition** - Automatic detection of names, places, organizations
- **Multi-format Export** - Generate optimized files for search engines and AI systems
- **Enterprise Security** - Path protection, performance limits, memory-safe processing

## Use Cases

- **Business Intelligence** - Japanese corporate data with automatic entity recognition
- **Technical Documentation** - API specifications with search optimization
- **Knowledge Management** - Semantic data extraction for RAG systems

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

MIT License. See [LICENSE](LICENSE) for details.