# sphinxcontrib-jsontable

A Sphinx extension that renders JSON (from files or inline content) as reStructuredText tables.

## Background / Motivation

In recent years, there has been an increasing trend of using documents as data sources for Retrieval Augmented Generation (RAG). However, tabular data within documents often loses its structural relevance during the process of being ingested by RAG systems. This presented a challenge where the original value of the structured data could not be fully leveraged.

Against this backdrop, sphinxcontrib-jsontable was developed to directly embed structured data, such as JSON, as meaningful tables in Sphinx-generated documents, with the objective to ensure that readability and the data's value as a source effectively coexist.

## Features

* Load JSON from files within your Sphinx project or inline in your documentation.
* Support for JSON objects and arrays (of objects or arrays).
* Optional header row, row limits, and custom file encoding.
* Safe path resolution to prevent directory traversal.

## Installation

Install from PyPI:

```bash
pip install sphinxcontrib-jsontable
```

Or add to your `pyproject.toml`:

```toml
[project.dependencies]
sphinxcontrib-jsontable = "^0.1.0"
```

## Quickstart

1. In your `conf.py`, add:

   ```python
   extensions = [
       # ... other extensions
       'sphinxcontrib.jsontable',
   ]
   ```

2. Create a JSON file (e.g. `data/sample.json`):

   ```json
   [
     {"name": "Alice", "age": 30},
     {"name": "Bob", "age": 25}
   ]
   ```

3. In an `.rst` document:

   ```rst
   .. jsontable:: data/sample.json
      :header:
      :limit: 10
   ```

   or in a Markdown file (if you use myst-parser):

   ````markdown
   ```{jsontable} data/sample.json
   :header:
   :encoding: utf-8
   :limit: 5
   ````

   ```
   ```

4. Build your docs:

   ```bash
   sphinx-build -b html docs/ build/
   ```

## Directive Options

| Option     | Type         | Default | Description                                      |
| ---------- | ------------ | ------- | ------------------------------------------------ |
| `header`   | flag         | off     | Include first row (object keys) as table header. |
| `encoding` | string       | `utf-8` | Character encoding when reading JSON files.      |
| `limit`    | positive int | none    | Maximum number of rows to render from the JSON.  |

## Examples

See the [`examples/`](examples/) directory for a minimal Sphinx project demonstrating usage with both `.rst` and Markdown (`myst-parser`).

```bash
examples/
├── conf.py
├── index.rst
└── example.md
```

## API Reference

The key classes and functions are in `sphinxcontrib/jsontable/directives.py`:

* **JsonDataLoader**: loads JSON from file or inline content, validates encoding and safety.
* **TableConverter**: transforms JSON structures into 2D lists for table building.
* **TableBuilder**: generates Docutils table nodes from table data.
* **JsonTableDirective**: the Sphinx directive `.. jsontable::`.

Refer to the inline docstrings in the source for full details.

## License

This project is licensed under the [MIT License](LICENSE).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on opening issues and submitting pull requests.
