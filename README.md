# sphinxcontrib-jsontable

[![Tests](https://github.com/sasakama-code/sphinxcontrib-jsontable/actions/workflows/ci.yml/badge.svg)](https://github.com/sasakama-code/sphinxcontrib-jsontable/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/sasakama-code/sphinxcontrib-jsontable/graph/badge.svg)](https://codecov.io/gh/sasakama-code/sphinxcontrib-jsontable)
[![Python](https://img.shields.io/pypi/pyversions/sphinxcontrib-jsontable.svg)](https://pypi.org/project/sphinxcontrib-jsontable/)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/sasakama-code/sphinxcontrib-jsontable)

**Languages:** [English](README.md) | [日本語](README_ja.md)

A next-generation Sphinx extension that renders JSON data as structured tables with advanced **RAG (Retrieval Augmented Generation)** capabilities. Features world-class Japanese language processing optimized for **PLaMo-Embedding-1B**, making it the first Japanese-specialized RAG-enabled documentation system.

## 🚀 What's New in v0.3.0

### 🌟 **Revolutionary RAG Integration**
- **Enhanced Directive**: `enhanced-jsontable` with automatic metadata generation
- **Japanese Entity Recognition**: Native support for 人名, 地名, 組織名, ビジネス用語
- **PLaMo-Embedding-1B Integration**: 1024-dimensional vector generation for Japanese text
- **Multi-format Export**: JSON-LD, OpenSearch, PLaMo-ready formats

### 🎯 **Enterprise-Grade Features**  
- **Automatic Search Facets**: Statistical analysis with quartile-based ranges
- **Semantic Chunking**: Japanese-optimized content segmentation
- **Business Term Enhancement**: Specialized processing for Japanese business documents
- **Vector Search Indexing**: Production-ready search infrastructure

### 📚 **Complete Feature Guide**
**🎓 [v0.3.0 New Features Tutorial](docs/v0.3.0_feature_tutorial.md)** - Comprehensive guide with flowcharts, examples, and migration strategies

## Background / Motivation

In recent years, there has been an increasing trend of using documents as data sources for Retrieval Augmented Generation (RAG). However, tabular data within documents often loses its structural relevance during the process of being ingested by RAG systems. This presented a challenge where the original value of the structured data could not be fully leveraged.

Against this backdrop, **sphinxcontrib-jsontable v0.3.0** was developed to directly embed structured data as meaningful tables in Sphinx-generated documents, with advanced RAG capabilities that ensure readability and semantic understanding effectively coexist. The integration with PLaMo-Embedding-1B makes it the world's first Japanese-specialized RAG documentation system.

## 🌟 Core Features

### ✨ **Traditional Table Rendering**
* Load JSON from files within your Sphinx project
* Embed JSON directly inline in your documentation
* Support for relative file paths with safe path resolution
* Multiple data formats (objects, arrays, nested structures)
* Customizable output with headers and row limiting

### 🧠 **Advanced RAG Capabilities (v0.3.0)**
* **Automatic Metadata Extraction**: Schema analysis, statistics, data quality assessment
* **Japanese Entity Recognition**: 
  - 人名 (Personal names): 田中太郎, 佐藤花子
  - 地名 (Place names): 東京都, 大阪市, 新宿駅  
  - 組織名 (Organizations): 株式会社○○, ○○部
  - ビジネス用語 (Business terms): 売上高, 営業利益
* **Semantic Chunking**: Intelligent content segmentation for optimal search
* **Vector Processing**: PLaMo-Embedding-1B integration for Japanese text
* **Search Index Generation**: Automatic creation of search-optimized indices

### 🔍 **Multi-Format Export**
* **JSON-LD**: Semantic Web standard format
* **OpenSearch**: Elasticsearch/OpenSearch mapping
* **PLaMo-ready**: PLaMo-Embedding-1B optimized format  
* **Custom**: User-defined export formats

### 🔒 **Enterprise Security & Performance**
* Path traversal protection with comprehensive security measures
* Automatic performance optimization for large datasets
* Memory-safe processing with configurable limits
* Japanese Unicode normalization and character encoding support

## Installation

### From PyPI
```bash
pip install sphinxcontrib-jsontable
```

### From Source
```bash
git clone https://github.com/sasakama-code/sphinxcontrib-jsontable.git
cd sphinxcontrib-jsontable
pip install -e .
```

### Dependencies
- **Python**: 3.10+ (recommended: 3.11+)
- **Sphinx**: 3.0+ (recommended: 4.0+)
- **NumPy**: 2.2.6+ (for advanced statistical analysis)

## Quick Start

### 1. Enable the Extension

Add to your `conf.py`:

```python
extensions = [
    # ... your other extensions
    'sphinxcontrib.jsontable',
]

# Optional: Configure performance limits
jsontable_max_rows = 5000  # Default: 10000
```

### 2. Basic Usage (Legacy Compatible)

Create `data/users.json`:
```json
[
  {
    "id": 1,
    "name": "Alice Johnson",
    "email": "alice@example.com", 
    "department": "Engineering",
    "active": true
  },
  {
    "id": 2,
    "name": "Bob Smith",
    "email": "bob@example.com",
    "department": "Marketing", 
    "active": false
  }
]
```

**In reStructuredText (.rst):**
```rst
User Database
=============

.. jsontable:: data/users.json
   :header:
   :limit: 10
```

### 3. Enhanced RAG-Enabled Usage (v0.3.0)

**For Japanese business documents with RAG capabilities:**

```rst
Japanese Company Data with RAG
==============================

.. enhanced-jsontable:: data/japanese_companies.json
   :header:
   :rag-metadata: true
   :export-format: json-ld,opensearch,plamo-ready
   :entity-recognition: japanese
   :facet-generation: auto
   :semantic-chunking: business
```

**Sample Japanese data:**
```json
[
  {
    "会社名": "株式会社テクノロジー",
    "代表者": "田中太郎",
    "所在地": "東京都新宿区",
    "業種": "情報通信業", 
    "売上高": "50億円",
    "従業員数": "250名"
  },
  {
    "会社名": "サンプル工業株式会社",
    "代表者": "佐藤花子", 
    "所在地": "大阪市中央区",
    "業種": "製造業",
    "売上高": "120億円",
    "従業員数": "480名"
  }
]
```

### 4. Build Your Documentation

```bash
sphinx-build -b html docs/ build/html/
```

## RAG Integration Guide (v0.3.0)

### Enhanced Directive Options

| Option | Type | Default | Description | Example |
|--------|------|---------|-------------|---------|
| `rag-metadata` | flag | off | Enable RAG metadata generation | `:rag-metadata:` |
| `export-format` | string | none | Export formats (comma-separated) | `:export-format: json-ld,opensearch` |
| `entity-recognition` | string | off | Enable entity recognition | `:entity-recognition: japanese` |
| `facet-generation` | string | off | Auto-generate search facets | `:facet-generation: auto` |
| `semantic-chunking` | string | off | Semantic content chunking | `:semantic-chunking: business` |

### Export Formats

#### JSON-LD (Semantic Web)
```rst
.. enhanced-jsontable:: data/products.json
   :rag-metadata:
   :export-format: json-ld
```

**Output**: `products_metadata.jsonld` with semantic markup

#### OpenSearch/Elasticsearch
```rst  
.. enhanced-jsontable:: data/logs.json
   :rag-metadata:
   :export-format: opensearch
```

**Output**: `logs_opensearch_mapping.json` with optimized field mappings

#### PLaMo-ready Format
```rst
.. enhanced-jsontable:: data/japanese_text.json
   :rag-metadata:
   :export-format: plamo-ready
   :entity-recognition: japanese
```

**Output**: `japanese_text_plamo.json` with PLaMo-Embedding-1B optimizations

### Japanese Entity Recognition

The extension automatically detects and classifies Japanese entities:

```rst
.. enhanced-jsontable:: data/japanese_data.json
   :entity-recognition: japanese
   :rag-metadata:
```

**Supported Entity Types:**
- **人名** (Personal Names): 田中太郎, 佐藤花子, 山田次郎
- **地名** (Place Names): 東京都, 大阪市, 新宿駅, 渋谷区
- **組織名** (Organizations): 株式会社○○, ○○部, 経済産業省
- **ビジネス用語** (Business Terms): 売上高, 営業利益, ROI, KPI

### Automatic Search Facets

Generate intelligent search facets automatically:

```rst
.. enhanced-jsontable:: data/sales_data.json
   :facet-generation: auto
   :rag-metadata:
```

**Generated Facets:**
- **Categorical**: Automatic grouping of text fields
- **Numerical**: Quartile-based ranges for numeric data
- **Temporal**: Smart date/time period detection
- **Entity-based**: Japanese entity classification facets

### Semantic Chunking Strategies

Choose optimal chunking for your content:

```rst
.. enhanced-jsontable:: data/documents.json
   :semantic-chunking: business
   :entity-recognition: japanese
```

**Available Strategies:**
- `business`: Optimized for Japanese business documents
- `technical`: Technical documentation and manuals
- `general`: General-purpose content chunking
- `conversational`: Chat logs and communications

## Advanced RAG Examples

### Enterprise Business Intelligence

```rst
Quarterly Business Report
========================

.. enhanced-jsontable:: data/quarterly_report.json
   :header:
   :rag-metadata: true
   :export-format: json-ld,opensearch
   :entity-recognition: japanese
   :facet-generation: auto
   :semantic-chunking: business

.. note::
   This data is automatically processed for:
   
   - **Entity Recognition**: Company names, executive names, locations
   - **Search Facets**: Revenue ranges, department categories, geographic regions
   - **Vector Embeddings**: PLaMo-Embedding-1B for semantic search
   - **Export Formats**: JSON-LD for knowledge graphs, OpenSearch for analytics
```

### Technical Documentation with RAG

```rst  
API Documentation
================

.. enhanced-jsontable:: data/api_endpoints.json
   :header:
   :rag-metadata: true
   :export-format: plamo-ready
   :semantic-chunking: technical
   :facet-generation: auto

.. enhanced-jsontable:: data/error_codes.json
   :header:
   :rag-metadata: true
   :export-format: opensearch
   :semantic-chunking: technical
```

### Multi-language Content Processing

```rst
Global Office Directory
======================

.. enhanced-jsontable:: data/global_offices.json
   :header:
   :rag-metadata: true
   :entity-recognition: japanese
   :export-format: json-ld,opensearch,plamo-ready
   :facet-generation: auto
   :semantic-chunking: business
```

## Traditional Usage (Backward Compatible)

All existing documentation continues to work unchanged:

### Data Format Support

#### Array of Objects (Most Common)
```json
[
  {"name": "Redis", "port": 6379, "ssl": false},
  {"name": "PostgreSQL", "port": 5432, "ssl": true},
  {"name": "MongoDB", "port": 27017, "ssl": true}
]
```

#### 2D Arrays with Headers
```json
[
  ["Service", "Port", "Protocol", "Status"],
  ["HTTP", 80, "TCP", "Active"],
  ["HTTPS", 443, "TCP", "Active"],
  ["SSH", 22, "TCP", "Inactive"]
]
```

#### Single Objects
```json
{
  "database_host": "localhost",
  "database_port": 5432,
  "debug_mode": true,
  "max_connections": 100
}
```

### Traditional Directive Options

| Option | Type | Default | Description | Example |
|--------|------|---------|-------------|---------|
| `header` | flag | off | Include first row as table header | `:header:` |
| `encoding` | string | `utf-8` | File encoding for JSON files | `:encoding: utf-16` |
| `limit` | positive int/0 | automatic | Maximum rows to display (0 = unlimited) | `:limit: 50` |

## Performance & Security

### Automatic Performance Protection

For large datasets, the extension provides intelligent protection:

```rst
.. jsontable:: data/huge_dataset.json
   :header:
   # If dataset > 10,000 rows, automatically shows first 10,000 with warning
```

### Security Features

- **Path Traversal Protection**: Only files within Sphinx source directory
- **Safe File Access**: Comprehensive validation and sanitization
- **Memory Protection**: Configurable limits prevent resource exhaustion
- **Japanese Unicode Security**: Proper normalization and validation

### Configuration Options

```python
# In conf.py - Performance tuning
jsontable_max_rows = 5000  # Default: 10000

# Example configurations:
# For small documentation sites
jsontable_max_rows = 100

# For large data-heavy documentation  
jsontable_max_rows = 50000

# For development/testing
jsontable_max_rows = 1000
```

## Architecture Overview

### Core Components

**Legacy System (Backward Compatible):**
- `JsonTableDirective`: Original table rendering
- `JsonDataLoader`: File and content loading with security validation
- `TableConverter`: JSON to 2D table transformation
- `TableBuilder`: Docutils table node generation

**RAG Enhancement System (v0.3.0):**
- `EnhancedJsonTableDirective`: RAG-aware directive with metadata generation
- `RAGMetadataExtractor`: JSON schema analysis and statistics
- `SemanticChunker`: Japanese-optimized content chunking  
- `AdvancedMetadataGenerator`: Deep statistical analysis with entity recognition
- `SearchFacetGenerator`: Automatic facet generation for search optimization
- `MetadataExporter`: Multi-format export (JSON-LD, OpenSearch, PLaMo-ready)
- `PLaMoVectorProcessor`: PLaMo-Embedding-1B vector generation
- `IntelligentQueryProcessor`: Semantic query processing
- `SearchIndexGenerator`: Vector search index creation

### Integration Patterns

#### With Modern Documentation Tools

**MyST Markdown:**
````markdown
# Company Database

```{enhanced-jsontable} data/companies.json
:header:
:rag-metadata:
:entity-recognition: japanese
:export-format: json-ld
```
````

**Sphinx Tabs:**
```rst
.. tabs::

   .. tab:: Table View
   
      .. enhanced-jsontable:: data/sales.json
         :header:
         :rag-metadata:
   
   .. tab:: Raw Data
   
      .. literalinclude:: data/sales.json
         :language: json
```

#### With Search Systems

**Elasticsearch Integration:**
```rst
.. enhanced-jsontable:: data/products.json
   :export-format: opensearch
   :facet-generation: auto
   
# Generates products_opensearch_mapping.json for direct Elasticsearch import
```

**Knowledge Graph Integration:**
```rst
.. enhanced-jsontable:: data/entities.json
   :export-format: json-ld
   :entity-recognition: japanese
   
# Generates entities_metadata.jsonld for semantic web applications
```

## Migration Guide

### From v0.2.x to v0.3.0

**No Breaking Changes**: All existing documentation works unchanged.

**New Features Available:**
```rst
# Before (v0.2.x) - Basic table rendering
.. jsontable:: data/companies.json
   :header:

# After (v0.3.0) - Enhanced with RAG capabilities  
.. enhanced-jsontable:: data/companies.json
   :header:
   :rag-metadata: true
   :entity-recognition: japanese
   :export-format: json-ld,opensearch
```

**Recommended Configuration Update:**
```python
# Add to conf.py for v0.3.0 features
extensions = [
    'sphinxcontrib.jsontable',  # Enables both jsontable and enhanced-jsontable
]

# Optional: Tune for your data size
jsontable_max_rows = 5000
```

### From Other Extensions

**From sphinx-jsonschema:**
- Replace `.. jsonschema::` with `.. jsontable::` or `.. enhanced-jsontable::`
- Remove schema validation options, add RAG options
- Update file paths to be relative to source directory

## Development & Contributing

### Development Setup

```bash
git clone https://github.com/sasakama-code/sphinxcontrib-jsontable.git
cd sphinxcontrib-jsontable  
pip install -e ".[dev]"
```

### Quality Assurance

```bash
# Code formatting
ruff format

# Linting 
ruff check

# Type checking
mypy sphinxcontrib/jsontable/

# Testing
pytest

# Coverage report
pytest --cov=sphinxcontrib.jsontable --cov-report=html
```

### Contributing Guidelines

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup and workflow
- Code style guidelines  
- Testing procedures
- Pull request process

## Examples & Documentation

### Complete Examples

The [`examples/`](examples/) directory contains:
- Complete Sphinx project setup
- Various data format examples
- RAG integration demonstrations
- Japanese content processing examples
- Advanced configuration examples

```bash
cd examples/
sphinx-build -b html . _build/html/
```

### Development Tools

The [`scripts/`](scripts/) directory contains enterprise-grade development tools:

- **`performance_benchmark.py`** - Performance measurement and analysis
- **`memory_analysis.py`** - Memory usage analysis for different dataset sizes  
- **`competitive_analysis.py`** - Industry standard research and benchmarking
- **`validate_ci_tests.py`** - CI environment testing and validation
- **`knowledge_extraction.py`** - RAG metadata extraction utilities

These tools provide scientific foundation for performance optimization and enterprise reliability.

## Support & Community

- **Documentation**: Complete guides and API reference
- **Issues**: [GitHub Issues](https://github.com/sasakama-code/sphinxcontrib-jsontable/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sasakama-code/sphinxcontrib-jsontable/discussions)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md) for detailed version history

## License

This project is licensed under the [MIT License](LICENSE).

---

## 🏆 Project Status

**sphinxcontrib-jsontable v0.3.0** represents a major advancement in documentation tooling, combining traditional table rendering with cutting-edge RAG capabilities. With world-class Japanese language processing and PLaMo-Embedding-1B integration, it sets new standards for semantic documentation systems.

**Ready for Enterprise**: Production-grade quality with comprehensive testing, security validation, and performance optimization.

**Future-Proof**: Extensible architecture designed for integration with emerging AI and search technologies.