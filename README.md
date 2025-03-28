# Big Backlink Analyzer

Tool for analyzing backlink data from Ahrefs against content URLs to identify and track syndicated content performance.

## Features
- Visual analysis of backlink distribution
- Domain rating (DR) metrics and comparison
- Link weight calculations
- Historical report tracking
- Multi-client support

## Setup and Requirements
- Python 3.10+
- Required packages: `pip install -r requirements.txt`
- Client directory with reports subdirectory:
```
clients/
└── [ClientName]/
    └── reports/
```

## Usage Guide

### Getting Content Data
1. Navigate to client on portal
2. Click "Manage"
3. Click "Export"
4. Download CSV file
5. Place file in client's directory

### Getting Ahrefs Data
1. Go to Ahrefs
2. Search for client domain
3. Select "Subdomains" on the right panel
4. Select "Backlinks" from left menu
5. Apply filters:
   - Select "Dofollow"
   - Select "New"
6. Set date range from client's start date to today
7. Export as UTF-8 CSV
8. Place file in client's directory

### Running Analysis
1. Launch Big Backlink: `python src/gui.py`
2. For new clients:
   - Click "New Client"
   - Enter client name
   - Drag and drop both files when prompted
3. For existing clients:
   - Select client from dropdown
   - Click "Analyze"
   - Wait for report generation

### Reports
Reports are automatically generated in timestamped folders under the client's reports directory:
- Full analysis CSV
- Metrics summary
- Visualizations showing:
  - Link distribution between partner/non-partner
  - Average DR comparison
  - Link weight distribution
  - DR distribution across links