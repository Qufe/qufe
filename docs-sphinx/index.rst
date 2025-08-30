qufe Documentation
==================

A comprehensive Python utility library for data processing, file handling, database management, and automation tasks.

Features
--------

**Core Utilities** (:mod:`qufe.base`)
   - Timestamp handling with timezone support
   - Code comparison with multiple diff formats
   - Dynamic module import capabilities
   - List flattening with configurable depth
   - Dictionary utilities for nested structures

**Database Management** (:mod:`qufe.dbhandler`)
   - PostgreSQL integration using SQLAlchemy
   - Database exploration and metadata retrieval
   - Connection management with automatic cleanup

**Text Processing** (:mod:`qufe.texthandler`, :mod:`qufe.excludebracket`)
   - Bracket content removal with validation
   - DokuWiki formatting utilities
   - String search with context
   - Dictionary pretty-printing
   - Column formatting and alignment

**File Operations** (:mod:`qufe.filehandler`)
   - Directory traversal with Unicode normalization
   - Pattern-based file discovery
   - Pickle operations for object serialization
   - Path utilities and filename sanitization
   - Content extraction from directory structures

**Data Analysis** (:mod:`qufe.pdhandler`)
   - DataFrame utilities and transformations
   - Column analysis across multiple DataFrames
   - Missing data detection and validation
   - Comprehensive data quality checks

**Automation & Screen Interaction** (:mod:`qufe.interactionhandler`)
   - Screen capture and image processing
   - Color detection and analysis
   - Mouse automation for testing
   - Progress tracking for Jupyter notebooks
   - Color code extraction from screen regions

**Web Browser Automation** (:mod:`qufe.wbhandler`)
   - SeleniumBase integration with custom timeouts
   - Network request monitoring and capture
   - Interactive element discovery
   - URL parsing and parameter extraction
   - Multi-browser support (Chrome/Firefox)

Installation
------------

.. code-block:: bash

   pip install qufe

Quick Start
-----------

.. code-block:: python

   import qufe

   # Example usage of core utilities
   from qufe.base import flatten_list
   nested_list = [[1, 2], [3, [4, 5]]]
   flat_list = flatten_list(nested_list)

   # File handling example
   from qufe.filehandler import get_file_list
   files = get_file_list("/path/to/directory", "*.py")

API Reference
=============

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api/base
   api/dbhandler
   api/excludebracket
   api/filehandler
   api/interactionhandler
   api/pdhandler
   api/texthandler
   api/wbhandler

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`