from __future__ import annotations

import csv
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from artifact_tool import SpreadsheetFile, Workbook

BASE = Path('/mnt/data')
OUT_XLSX = BASE / 'hla_1516_requirements_index_v1_0.xlsx'
OUT_PNG = BASE / 'hla_1516_requirements_dashboard_v1_0_preview.png'

FILES = {
    'master_requirements_csv': BASE / 'hla_1516_requirements_master_v1_0.csv',
    'delta_requirements_csv': BASE / 'hla_1516_requirements_delta_v1_0.csv',
    'verification_matrix_csv': BASE / 'hla_1516_verification_matrix_v1_0.csv',
    'clause_tracker_csv': BASE / 'hla_1516_clause_tracker_v1_0.csv',
    'clause6_11_detail_csv': BASE / 'hla_1516_clause6_11_detailed_requirements_v1_0.csv',
    'omt_xml_detail_csv': BASE / 'hla_1516_omt_xml_detailed_requirements_v1_0.csv',
    'api_catalog_csv': BASE / 'hla_1516_api_service_catalog_v0_3.csv',
    'mim_catalog_csv': BASE / 'hla_1516_mim_catalog_v0_3.csv',
    'xsd_catalog_csv': BASE / 'hla_1516_xsd_catalog_v0_3.csv',
    'wsdl_catalog_csv': BASE / 'hla_1516_wsdl_catalog_v0_3.csv',
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))
####

req_rows = read_csv(FILES['master_requirements_csv'])
delta_rows = read_csv(FILES['delta_requirements_csv'])
ver_rows = read_csv(FILES['verification_matrix_csv'])
tracker_rows = read_csv(FILES['clause_tracker_csv'])
detail_rows = read_csv(FILES['clause6_11_detail_csv'])
omt_rows = read_csv(FILES['omt_xml_detail_csv'])
api_rows = read_csv(FILES['api_catalog_csv'])
mim_rows = read_csv(FILES['mim_catalog_csv'])
xsd_rows = read_csv(FILES['xsd_catalog_csv'])
wsdl_rows = read_csv(FILES['wsdl_catalog_csv'])

wb = Workbook.create()
header_fmt = {
    'fill': '#1F4E78',
    'font': {'bold': True, 'color': '#FFFFFF'},
    'horizontal_alignment': 'center',
    'vertical_alignment': 'center',
    'wrap_text': True,
}
title_fmt = {
    'fill': '#0F172A',
    'font': {'bold': True, 'color': '#FFFFFF', 'size': 16},
    'horizontal_alignment': 'center',
    'vertical_alignment': 'center',
}
subheader_fmt = {
    'fill': '#D9EAF7',
    'font': {'bold': True, 'color': '#0F172A'},
    'horizontal_alignment': 'center',
    'vertical_alignment': 'center',
    'wrap_text': True,
}


def add_sheet(name: str, headers: list[str], rows: list[list[str]], widths: dict[int, int] | None = None) -> Any:
    sheet = wb.worksheets.add(name)
    matrix = [headers] + rows
    sheet.get_range_by_indexes(0, 0, len(matrix), len(headers)).values = matrix
    sheet.get_range_by_indexes(0, 0, 1, len(headers)).format = header_fmt
    sheet.freeze_panes.freeze_rows(1)
    for idx, width in (widths or {}).items():
        sheet.get_range_by_indexes(0, idx, len(matrix), 1).format.column_width = width
    return sheet
####

# Dashboard
cap_total = Counter(row['capability'] for row in req_rows)
cap_new = Counter(row['capability'] for row in delta_rows)
std_total = Counter(row['standard'] for row in req_rows)
std_new = Counter(row['standard'] for row in delta_rows)
transport_counts = Counter(row['transport'] for row in ver_rows)

summary_cap = [[cap, str(cap_total[cap]), str(cap_new.get(cap, 0))] for cap in sorted(cap_total)]
summary_std = [[std, str(std_total[std]), str(std_new.get(std, 0))] for std in sorted(std_total)]
summary_transport = [[transport, str(transport_counts[transport])] for transport in sorted(transport_counts)]

dash = wb.worksheets.add('Dashboard v1.0')
dash.merge_cells('A1:J1')
dash.get_range('A1').values = [['HLA 1516-2010 Requirements Catalog v1.0 — Final Engineering Codification']]
dash.get_range('A1:J1').format = title_fmt

dash.get_range('A3:B14').values = [
    ['Metric', 'Value'],
    ['Total requirements', str(len(req_rows))],
    ['New v1.0 requirements', str(len(delta_rows))],
    ['Verification rows', str(len(ver_rows))],
    ['Tracked clauses', str(len(tracker_rows))],
    ['1516.1 Clause 6-11 detail rows', str(len(detail_rows))],
    ['1516.2 OMT/XML detail rows', str(len(omt_rows))],
    ['API service/callback catalog rows', str(len(api_rows))],
    ['MIM catalog rows', str(len(mim_rows))],
    ['XSD catalog rows', str(len(xsd_rows))],
    ['WSDL operation rows', str(len(wsdl_rows))],
    ['Package files', str(len(FILES) + 2)],
]
dash.get_range('A3:B3').format = header_fmt

dash.get_range('D3:F3').values = [['Capability', 'Total requirements', 'New v1.0']]
dash.get_range('D3:F3').format = header_fmt
dash.get_range_by_indexes(3, 3, len(summary_cap), 3).values = summary_cap

dash.get_range('H3:J3').values = [['Standard', 'Total requirements', 'New v1.0']]
dash.get_range('H3:J3').format = header_fmt
dash.get_range_by_indexes(3, 7, len(summary_std), 3).values = summary_std

dash.get_range('H10:I10').values = [['Verification transport', 'Rows']]
dash.get_range('H10:I10').format = header_fmt
dash.get_range_by_indexes(10, 7, len(summary_transport), 2).values = summary_transport

dash.get_range('A:A').format.column_width = 34
dash.get_range('B:B').format.column_width = 18
dash.get_range('D:D').format.column_width = 22
dash.get_range('H:H').format.column_width = 28
dash.freeze_panes.freeze_rows(2)
try:
    chart = dash.charts.add('bar', dash.get_range(f'D3:F{3 + len(summary_cap)}'))
    chart.title_text = 'Requirement Rows by Capability'
    chart.set_position('L3', 'S22')
except Exception as exc:
    print(f'chart skipped: {exc}')

# README
readme_rows = [
    ['Artifact', 'HLA 1516-2010 Requirements Catalog v1.0'],
    ['Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
    ['Scope', 'IEEE 1516-2010, IEEE 1516.1-2010, IEEE 1516.2-2010, Java API, WSDL, MIM XML, OMT/FDD/DIF XSD.'],
    ['v1.0 additions', 'Detailed rows for IEEE 1516.1 Clauses 6-11 and IEEE 1516.2 OMT/XML schema codification.'],
    ['Caveat', 'Engineering codification and traceability scaffold; not a certified legal/compliance extraction.'],
    ['Full data', 'Full row-level data is stored in the CSV files listed in File Manifest. This index workbook is intentionally compact for reliable review.'],
    ['Next step', 'PDF prose audit, exact exception edge-case review, and executable pytest/MOM observer implementation.'],
]
add_sheet('ReadMe v1.0', ['field', 'value'], readme_rows, {0: 24, 1: 105})

# File manifest
manifest_rows = []
for label, path in FILES.items():
    manifest_rows.append([label, path.name, str(path.stat().st_size), '/mnt/data/' + path.name])
manifest_rows.append(['index_workbook', OUT_XLSX.name, '', '/mnt/data/' + OUT_XLSX.name])
manifest_rows.append(['dashboard_preview', OUT_PNG.name, '', '/mnt/data/' + OUT_PNG.name])
add_sheet('File Manifest', ['artifact', 'filename', 'bytes', 'sandbox_path'], manifest_rows, {0: 30, 1: 55, 3: 80})

# Clause tracker full sheet
tracker_headers = list(tracker_rows[0].keys())
add_sheet('Clause Tracker v1.0', tracker_headers, [[row.get(h, '') for h in tracker_headers] for row in tracker_rows], {2: 34, 4: 30, 7: 55, 8: 55, 10: 55})

# Summary sheets
add_sheet('Capability Summary', ['capability', 'total_requirements', 'new_v1_0_requirements'], summary_cap, {0: 22})
add_sheet('Standard Summary', ['standard', 'total_requirements', 'new_v1_0_requirements'], summary_std, {0: 32})
add_sheet('Verification Summary', ['transport', 'verification_rows'], summary_transport, {0: 24})

# Sample of the v1.0 delta to give quick review inside the workbook.
delta_headers = list(delta_rows[0].keys())
delta_sample = [[row.get(h, '') for h in delta_headers] for row in delta_rows[:250]]
add_sheet('Delta Sample v1.0', delta_headers, delta_sample, {0: 38, 6: 72, 16: 55, 21: 55})

# Data dictionary and work queue
DATA_DICTIONARY = [
    ['requirement_id', 'Stable identifier for traceability to implementation, tests, and evidence.'],
    ['standard', 'Source standard document or artifact family.'],
    ['clause', 'Clause, service clause, annex, or artifact grouping.'],
    ['capability', 'Top-level capability bucket.'],
    ['feature', 'Feature/topic grouping within the capability.'],
    ['requirement_text', 'Engineering requirement statement. v1.0 rows are implementation-driving paraphrases, not legal quotes.'],
    ['requirement_type', 'Decomposition type: SVC/SIG/ARG/PRE/EFF/EXC/MOM/XSD/MIM/semantic/etc.'],
    ['transport_scope', 'Static/native/gRPC/REST applicability.'],
    ['mom_observable', 'Whether MOM observer evidence is expected.'],
]
add_sheet('Data Dictionary', ['column', 'meaning'], DATA_DICTIONARY, {0: 28, 1: 100})
WORK_QUEUE = [
    ['P0', 'PDF prose audit', '1516.1 clauses 4-11', 'next', 'Compare generated rows against exact PDF prose and edge cases.'],
    ['P0', 'Executable conformance tests', 'native RTI', 'next', 'Convert requirement IDs into pytest tests and MOM observer scenarios.'],
    ['P0', 'Transport equivalence harness', 'native/gRPC/REST', 'planned', 'Run dynamic requirements against all enabled transports with identical expected evidence.'],
    ['P0', 'MOM observer', 'Clause 11/MIM', 'planned', 'Monitor federate subscribes to MOM objects/interactions and compares reports to RTI state.'],
    ['P1', 'OMT parser fixtures', '1516.2 OMT/DIF/FDD', 'planned', 'Use Restaurant FOM/SOM modules and generated negative fixtures.'],
    ['P1', 'Traceability review', 'whole product set', 'planned', 'Resolve overlaps and mark exact normative source paragraphs after manual review.'],
]
add_sheet('Work Queue v1.0', ['priority', 'work_item', 'scope', 'status', 'notes'], WORK_QUEUE, {1: 30, 2: 30, 4: 85})

print(wb.inspect({'kind': 'table', 'range': 'Dashboard v1.0!A1:J24', 'include': 'values,formulas', 'table_max_rows': 24, 'table_max_cols': 10}).ndjson)
print(wb.inspect({'kind': 'match', 'search_term': '#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A', 'options': {'use_regex': True, 'max_results': 300}, 'summary': 'formula error scan'}).ndjson)

SpreadsheetFile.export_xlsx(wb).save(str(OUT_XLSX))
try:
    wb.render({'sheet_name': 'Dashboard v1.0', 'range': 'A1:J24', 'scale': 1}).save(str(OUT_PNG))
except Exception as exc:
    print(f'render skipped: {exc}')
print(f'saved {OUT_XLSX} {OUT_XLSX.stat().st_size}')
if OUT_PNG.exists():
    print(f'saved {OUT_PNG} {OUT_PNG.stat().st_size}')
