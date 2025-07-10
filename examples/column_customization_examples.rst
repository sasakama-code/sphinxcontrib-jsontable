Column Customization Examples
============================

This document demonstrates the new column customization features added in Issue #48.

Basic Column Selection
----------------------

You can specify which columns to display using the `columns` option:

.. jsontable::
   :columns: name,age,city

   [
     {"name": "Alice", "age": 25, "city": "Tokyo", "country": "Japan", "id": 1},
     {"name": "Bob", "age": 30, "city": "NYC", "country": "USA", "id": 2},
     {"name": "Carol", "age": 28, "city": "London", "country": "UK", "id": 3}
   ]

Column Hiding
-------------

You can hide specific columns using the `hide-columns` option:

.. jsontable::
   :hide-columns: id,country

   [
     {"name": "Alice", "age": 25, "city": "Tokyo", "country": "Japan", "id": 1},
     {"name": "Bob", "age": 30, "city": "NYC", "country": "USA", "id": 2},
     {"name": "Carol", "age": 28, "city": "London", "country": "UK", "id": 3}
   ]

Column Ordering
---------------

You can specify the order of columns using the `column-order` option:

.. jsontable::
   :column-order: name,city,age

   [
     {"name": "Alice", "age": 25, "city": "Tokyo", "country": "Japan"},
     {"name": "Bob", "age": 30, "city": "NYC", "country": "USA"},
     {"name": "Carol", "age": 28, "city": "London", "country": "UK"}
   ]

Column Widths
-------------

You can specify custom column widths using the `column-widths` option:

.. jsontable::
   :column-widths: 3,1,2
   :columns: name,age,city

   [
     {"name": "Alice", "age": 25, "city": "Tokyo"},
     {"name": "Bob", "age": 30, "city": "NYC"},
     {"name": "Carol", "age": 28, "city": "London"}
   ]

Combined Features
-----------------

You can combine multiple column customization options:

.. jsontable::
   :columns: name,age,city,country
   :hide-columns: age
   :column-order: country,city,name
   :column-widths: 2,2,3

   [
     {"name": "Alice", "age": 25, "city": "Tokyo", "country": "Japan", "id": 1, "timestamp": "2024-01-01"},
     {"name": "Bob", "age": 30, "city": "NYC", "country": "USA", "id": 2, "timestamp": "2024-01-02"},
     {"name": "Carol", "age": 28, "city": "London", "country": "UK", "id": 3, "timestamp": "2024-01-03"}
   ]

This will:
1. Start with specified columns: name, age, city, country
2. Hide the age column: name, city, country
3. Reorder to: country, city, name
4. Apply widths [2, 2, 3] to the final columns

2D Array Support
----------------

Column customization also works with 2D arrays:

.. jsontable::
   :column-order: City,Name,Age
   :column-widths: 2,3,1

   [
     ["Name", "Age", "City"],
     ["Alice", "25", "Tokyo"],
     ["Bob", "30", "NYC"],
     ["Carol", "28", "London"]
   ]

File-based Data
---------------

Column customization works with file-based data as well:

.. jsontable:: data/sample_users.json
   :columns: name,email,city
   :column-order: city,name,email
   :column-widths: 2,3,4