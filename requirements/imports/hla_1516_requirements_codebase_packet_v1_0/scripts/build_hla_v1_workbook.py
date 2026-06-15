from __future__ import annotations

import csv
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from artifact_tool import SpreadsheetFile, Workbook

BASE = Path('/mnt/data')
OUT_XLSX = BASE / 'hla_1516_requirements_master_v1_0.xlsx'
OUT_PNG = BASE / 'hla_1516_requirements_dashboard_v1_0_preview.png'


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))
####


def col_letter(n: int) -> str:
    s = ''
    while n:
        n, rem = divmod(n - 1, 26)
        s = chr(65 + rem) + s
    return s
####

req_rows = read_csv(BASE / 'hla_1516_requirements_master_v1_0.csv')
delta_rows = read_csv(BASE / 'hla_1516_requirements_delta_v1_0.csv')
ver_rows = read_csv(BASE / 'hla_1516_verification_matrix_v1_0.csv')
tracker_rows = read_csv(BASE / 'hla_1516_clause_tracker_v1_0.csv')
detail_rows = read_csv(BASE / 'hla_1516_clause6_11_detailed_requirements_v1_0.csv')
omt_xml_rows = read_csv(BASE / 'hla_1516_omt_xml_detailed_requirements_v1_0.csv')
api_rows = read_csv(BASE / 'hla_1516_api_service_catalog_v0_3.csv')
mim_rows = read_csv(BASE / 'hla_1516_mim_catalog_v0_3.csv')
xsd_rows = read_csv(BASE / 'hla_1516_xsd_catalog_v0_3.csv')
wsdl_rows = read_csv(BASE / 'hla_1516_wsdl_catalog_v0_3.csv')

req_headers = list(req_rows[0].keys())
ver_headers = list(ver_rows[0].keys())
tracker_headers = list(tracker_rows[0].keys())

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


def rows_to_matrix(headers: list[str], rows: list[dict[str, str]]) -> list[list[str]]:
    return [headers] + [[str(row.get(h, '')) for h in headers] for row in rows]
####


def add_sheet(name: str, headers: list[str], rows: list[dict[str, str]], *, widths: dict[str, int] | None = None) -> Any:
    sheet = wb.worksheets.add(name)
    matrix = rows_to_matrix(headers, rows)
    nrows = len(matrix)
    ncols = len(headers)
    sheet.get_range_by_indexes(0, 0, nrows, ncols).values = matrix
    sheet.get_range_by_indexes(0, 0, 1, ncols).format = header_fmt
    sheet.freeze_panes.freeze_rows(1)
    widths = widths or {}
    # Conservative width formatting only on important columns to avoid slow operations.
    for header, width in widths.items():
        if header in headers:
            idx = headers.index(header)
            sheet.get_range_by_indexes(0, idx, nrows, 1).format.column_width = width
        ####
    ####
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
dash.merge_cells('A1:H1')
dash.get_range('A1').values = [['HLA 1516-2010 Requirements Catalog v1.0']]
dash.get_range('A1:H1').format = title_fmt

dash.get_range('A3:B12').values = [
    ['Metric', 'Value'],
    ['Total requirements', str(len(req_rows))],
    ['New v1.0 requirements', str(len(delta_rows))],
    ['Verification rows', str(len(ver_rows))],
    ['Tracked clauses', str(len(tracker_rows))],
    ['1516.1 Clause 6-11 detail rows', str(len(detail_rows))],
    ['1516.2 OMT/XML detail rows', str(len(omt_xml_rows))],
    ['MIM catalog rows', str(len(mim_rows))],
    ['XSD catalog rows', str(len(xsd_rows))],
    ['WSDL operation rows', str(len(wsdl_rows))],
]
dash.get_range('A3:B3').format = header_fmt

dash.get_range('D3:E12').values = [
    ['Formula metric', 'Formula'],
    ['Total requirements', "=COUNTA('Requirements v1.0'!A:A)-1"],
    ['New v1.0 requirements', "=COUNTA('Delta v1.0'!A:A)-1"],
    ['Verification rows', "=COUNTA('Verification v1.0'!A:A)-1"],
    ['Tracked clauses', "=COUNTA('Clause Tracker v1.0'!A:A)-1"],
    ['Native tests', "=COUNTIF('Verification v1.0'!F:F,\"native\")"],
    ['gRPC tests', "=COUNTIF('Verification v1.0'!F:F,\"grpc\")"],
    ['REST tests', "=COUNTIF('Verification v1.0'!F:F,\"rest\")"],
    ['Static tests', "=COUNTIF('Verification v1.0'!F:F,\"static\")"],
    ['', ''],
]
dash.get_range('D3:E3').format = header_fmt
# Apply formulas to E4:E11 from formula strings; keep visible formulas in cells.
dash.get_range('E4:E11').formulas = [[row[1]] for row in dash.get_range('D4:E11').values]

dash.get_range('A14:C14').values = [['Capability', 'Total requirements', 'New v1.0']]
dash.get_range('A14:C14').format = header_fmt
dash.get_range_by_indexes(14, 0, len(summary_cap), 3).values = summary_cap

dash.get_range('E14:G14').values = [['Standard', 'Total requirements', 'New v1.0']]
dash.get_range('E14:G14').format = header_fmt
dash.get_range_by_indexes(14, 4, len(summary_std), 3).values = summary_std

dash.get_range('I14:J14').values = [['Verification transport', 'Rows']]
dash.get_range('I14:J14').format = header_fmt
dash.get_range_by_indexes(14, 8, len(summary_transport), 2).values = summary_transport

dash.get_range('A:A').format.column_width = 30
dash.get_range('B:B').format.column_width = 18
dash.get_range('D:D').format.column_width = 24
dash.get_range('E:E').format.column_width = 22
dash.get_range('I:I').format.column_width = 22
dash.freeze_panes.freeze_rows(3)
try:
    chart = dash.charts.add('bar', dash.get_range(f'A14:C{14 + len(summary_cap)}'))
    chart.title_text = 'Requirement Rows by Capability'
    chart.set_position('L3', 'S22')
except Exception as exc:
    print(f'chart skipped: {exc}')

# ReadMe
readme_rows = [
    {'field': 'Artifact', 'value': 'HLA 1516-2010 Requirements Catalog v1.0'},
    {'field': 'Generated', 'value': datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
    {'field': 'Scope', 'value': 'IEEE 1516-2010 (2010 edition), IEEE 1516.1-2010 (2010 edition), IEEE 1516.2-2010 (2010 edition), Java API, WSDL, MIM XML, OMT/FDD/DIF XSD.'},
    {'field': 'v1.0 additions', 'value': 'Detailed rows for IEEE 1516.1 Clauses 6-11 and IEEE 1516.2 OMT/XML schema codification.'},
    {'field': 'Caveat', 'value': 'Engineering codification and traceability scaffold; not a certified legal/compliance extraction.'},
    {'field': 'Suggested next step', 'value': 'Perform PDF prose audit and convert planned verification rows into executable pytest/MOM observer tests.'},
]
readme = add_sheet('ReadMe v1.0', ['field', 'value'], readme_rows, widths={'field': 24, 'value': 92})

# Main sheets
add_sheet('Clause Tracker v1.0', tracker_headers, tracker_rows, widths={'clause_title': 34, 'codification_status_v1_0': 28, 'codification_depth': 55, 'residual_action': 55, 'notes': 55})
add_sheet('Requirements v1.0', req_headers, req_rows, widths={'requirement_id': 36, 'requirement_text': 70, 'source_detail': 55, 'verification_notes': 55})
add_sheet('Delta v1.0', req_headers, delta_rows, widths={'requirement_id': 36, 'requirement_text': 70, 'source_detail': 55, 'verification_notes': 55})
add_sheet('Clause6-11 Detail v1.0', req_headers, detail_rows, widths={'requirement_id': 36, 'requirement_text': 70, 'source_detail': 55})
add_sheet('OMT XML Detail v1.0', req_headers, omt_xml_rows, widths={'requirement_id': 36, 'requirement_text': 70, 'source_detail': 55})
add_sheet('Verification v1.0', ver_headers, ver_rows, widths={'test_id': 38, 'requirement_id': 36, 'expected_evidence': 70, 'verification_notes': 55})

# Catalogs
add_sheet('API Catalog', list(api_rows[0].keys()), api_rows, widths={'arguments': 60, 'exceptions': 60, 'signature': 80})
add_sheet('MIM Catalog', list(mim_rows[0].keys()), mim_rows, widths={'path_or_owner': 55, 'semantics': 80})
add_sheet('XSD Catalog', list(xsd_rows[0].keys()), xsd_rows, widths={'name': 40, 'type_or_kind': 35, 'ref_or_mixed': 40})
add_sheet('WSDL Catalog', list(wsdl_rows[0].keys()), wsdl_rows, widths={'operation': 45, 'input': 45, 'output': 45})

# Data dictionary and work queue
DATA_DICTIONARY = [
    {'column': 'requirement_id', 'meaning': 'Stable identifier for traceability to implementation, tests, and evidence.'},
    {'column': 'standard', 'meaning': 'Source standard document or artifact family.'},
    {'column': 'clause', 'meaning': 'Clause, service clause, annex, or artifact grouping.'},
    {'column': 'capability', 'meaning': 'Top-level capability bucket.'},
    {'column': 'feature', 'meaning': 'Feature/topic grouping within the capability.'},
    {'column': 'requirement_text', 'meaning': 'Engineering requirement statement. v1.0 rows are implementation-driving paraphrases, not legal quotes.'},
    {'column': 'requirement_type', 'meaning': 'Decomposition type: SVC/SIG/ARG/PRE/EFF/EXC/MOM/XSD/MIM/semantic/etc.'},
    {'column': 'transport_scope', 'meaning': 'Static/native/gRPC/REST applicability.'},
    {'column': 'mom_observable', 'meaning': 'Whether MOM observer evidence is expected.'},
]
add_sheet('Data Dictionary', ['column', 'meaning'], DATA_DICTIONARY, widths={'column': 30, 'meaning': 95})
WORK_QUEUE = [
    {'priority': 'P0', 'work_item': 'PDF prose audit', 'scope': '1516.1 clauses 4-11', 'status': 'next', 'notes': 'Compare generated rows against exact PDF prose and edge cases.'},
    {'priority': 'P0', 'work_item': 'Executable conformance tests', 'scope': 'native RTI', 'status': 'next', 'notes': 'Convert requirement IDs into pytest tests and MOM observer scenarios.'},
    {'priority': 'P0', 'work_item': 'Transport equivalence harness', 'scope': 'native/gRPC/REST', 'status': 'planned', 'notes': 'Run dynamic requirements against all enabled transports with identical expected evidence.'},
    {'priority': 'P0', 'work_item': 'MOM observer', 'scope': 'Clause 11/MIM', 'status': 'planned', 'notes': 'Monitor federate subscribes to MOM objects/interactions and compares reports to RTI state.'},
    {'priority': 'P1', 'work_item': 'OMT parser fixtures', 'scope': '1516.2 OMT/DIF/FDD', 'status': 'planned', 'notes': 'Use Restaurant FOM/SOM modules and generated negative fixtures.'},
    {'priority': 'P1', 'work_item': 'Traceability review', 'scope': 'whole product set', 'status': 'planned', 'notes': 'Resolve overlaps and mark exact normative source paragraphs after manual review.'},
]
add_sheet('Work Queue v1.0', ['priority', 'work_item', 'scope', 'status', 'notes'], WORK_QUEUE, widths={'work_item': 30, 'scope': 28, 'notes': 80})

# Verify dashboard and error scan before export.
print(wb.inspect({'kind': 'table', 'range': 'Dashboard v1.0!A1:J25', 'include': 'values,formulas', 'table_max_rows': 25, 'table_max_cols': 12}).ndjson)
print(wb.inspect({'kind': 'match', 'search_term': '#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A', 'options': {'use_regex': True, 'max_results': 300}, 'summary': 'formula error scan'}).ndjson)

SpreadsheetFile.export_xlsx(wb).save(str(OUT_XLSX))
# Render dashboard preview after export path is valid.
try:
    wb.render({'sheet_name': 'Dashboard v1.0', 'range': 'A1:J28', 'scale': 1}).save(str(OUT_PNG))
except Exception as exc:
    print(f'render skipped: {exc}')
print(f'saved {OUT_XLSX} {OUT_XLSX.stat().st_size}')
if OUT_PNG.exists():
    print(f'saved {OUT_PNG} {OUT_PNG.stat().st_size}')
