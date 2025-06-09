"""Docutils table node builder for structured table data rendering.

Converts 2D string arrays into properly formatted docutils table nodes suitable
for Sphinx documentation generation with comprehensive layout and formatting support.

Features:
- Docutils table node generation
- Header row support
- Multi-column layout handling
- Content escaping and validation
- Empty table handling
"""

from __future__ import annotations

from typing import cast

from docutils import nodes

from .table_converters import TableData


class TableBuilder:
    """
    Build docutils table nodes from structured table data.

    Converts 2D string arrays into properly formatted docutils table nodes
    suitable for Sphinx documentation generation with support for headers,
    multi-column layouts, and proper content escaping.
    """

    def build(self, table_data: TableData, has_header: bool = False) -> nodes.table:
        """
        Build a docutils.nodes.table from 2D list of strings.

        Args:
            table_data: 2D list representing table content.
            has_header: Whether the first row is a header (default False).

        Returns:
            nodes.table node ready for inclusion in document.
        """
        if not table_data:
            return self._create_empty_table()

        max_cols = max(len(row) for row in table_data)
        table = self._create_table_structure(max_cols)

        if has_header:
            self._add_header(table, table_data[0])
            body_data = table_data[1:]
        else:
            body_data = table_data

        self._add_body(table, body_data, max_cols)
        return table

    def _create_empty_table(self) -> nodes.table:
        """
        Create an empty table node with one column.

        Returns:
            nodes.table with a single colspec.
        """
        table = nodes.table()
        tgroup = nodes.tgroup(cols=1)
        tgroup.append(nodes.colspec(colwidth=1))
        tbody = nodes.tbody()
        row = nodes.row()
        entry = nodes.entry()
        entry.append(nodes.paragraph(text="No data available"))
        row.append(entry)
        cast(nodes.Element, tbody).append(row)
        cast(nodes.Element, tgroup).append(tbody)
        table.append(tgroup)
        return table

    def _create_table_structure(self, num_cols: int) -> nodes.table:
        """
        Create basic table structure with column specifications.

        Args:
            num_cols: Number of columns for the table.

        Returns:
            nodes.table with tgroup and colspecs configured.
        """
        table = nodes.table()
        tgroup = nodes.tgroup(cols=num_cols)

        # Add column specifications
        for _ in range(num_cols):
            colspec = nodes.colspec(colwidth=1)
            tgroup.append(colspec)

        table.append(tgroup)
        return table

    def _add_header(self, table: nodes.table, header_row: list[str]) -> None:
        """
        Add header row to table structure.

        Args:
            table: Table node to add header to.
            header_row: List of header cell values.
        """
        tgroup = table[0]
        thead = nodes.thead()

        row = nodes.row()
        for cell_content in header_row:
            entry = nodes.entry()
            entry.append(nodes.paragraph(text=str(cell_content)))
            row.append(entry)

        cast(nodes.Element, thead).append(row)
        cast(nodes.Element, tgroup).append(thead)

    def _add_body(
        self, table: nodes.table, body_data: TableData, max_cols: int
    ) -> None:
        """
        Add body rows to table structure.

        Args:
            table: Table node to add body to.
            body_data: 2D list of body cell values.
            max_cols: Maximum number of columns for padding.
        """
        tgroup = table[0]
        tbody = nodes.tbody()

        for row_data in body_data:
            row = nodes.row()

            # Pad row to match max columns
            padded_row = list(row_data) + [""] * (max_cols - len(row_data))

            for cell_content in padded_row:
                entry = nodes.entry()
                entry.append(nodes.paragraph(text=str(cell_content)))
                row.append(entry)

            tbody.append(row)

        cast(nodes.Element, tgroup).append(tbody)
