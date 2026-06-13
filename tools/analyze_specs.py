from __future__ import annotations

import json
import os
import re
import shutil
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path('/mnt/data')
SPEC = ROOT/'hla_specs'
JAVA_ROOT = SPEC/'apis/java/java/src/hla/rti1516e'
CPP_ROOT = SPEC/'apis/cpp/cpp/src/RTI'
OUT = ROOT/'hla2010_python_v0_3'
ZIP = ROOT/'hla2010_python_v0_3.zip'

@dataclass
class Method:
    language: str
    interface: str
    name: str
    return_type: str
    params: str
    throws: list[str]
    service: str|None = None
    group: str|None = None
    source_file: str|None = None
    source_line: int|None = None

def ensure_specs_unpacked() -> None:
    # Unpack top-level zips if hla_specs was not already present.
    SPEC.mkdir(exist_ok=True)
    for zip_name in ['1516.1-2010_downloads.zip','1516.2-2010_downloads.zip']:
        zpath = ROOT/zip_name
        if zpath.exists():
            with zipfile.ZipFile(zpath) as zf:
                zf.extractall(SPEC)
    apis = SPEC/'apis'
    (apis/'java').mkdir(parents=True, exist_ok=True)
    (apis/'cpp').mkdir(parents=True, exist_ok=True)
    jzip = SPEC/'1516.1-2010_downloads'/'IEEE1516-2010_Java_API.zip'
    czip = SPEC/'1516.1-2010_downloads'/'IEEE1516-2010_C++_API.zip'
    if jzip.exists() and not JAVA_ROOT.exists():
        with zipfile.ZipFile(jzip) as zf:
            zf.extractall(apis/'java')
    if czip.exists() and not CPP_ROOT.exists():
        with zipfile.ZipFile(czip) as zf:
            zf.extractall(apis/'cpp')

def strip_block_comments_keep_lines(s: str) -> str:
    # preserve line count for source_line estimates
    def repl(m):
        return '\n' * m.group(0).count('\n')
    return re.sub(r'/\*.*?\*/', repl, s, flags=re.S)

def parse_java_methods(file: Path, interface: str) -> list[Method]:
    text = file.read_text(errors='replace')
    clean = strip_block_comments_keep_lines(text)
    lines = clean.splitlines()
    group = None
    service = None
    methods: list[Method] = []
    current = ''
    start_line = None
    collecting = False
    group_patterns = [
        ('Federation Management Services','Federation Management'),
        ('Declaration Management Services','Declaration Management'),
        ('Object Management Services','Object Management'),
        ('Ownership Management Services','Ownership Management'),
        ('Time Management Services','Time Management'),
        ('Data Distribution Management','Data Distribution Management'),
        ('RTI Support Services','Support Services'),
    ]
    start_re = re.compile(
        r"^\s*(?:void|boolean|byte|short|int|long|float|double|String|URL|Set<[^>]+>|"
        r"[A-Za-z_][\w<>\[\], ?]*?)\s+([a-zA-Z_]\w*)\s*\("
    )
    sig_re = re.compile(
        r"(?P<return>[A-Za-z_][\w<>\[\], ?]*?|void|boolean|int|long|double|float|String|URL)\s+"
        r"(?P<name>[A-Za-z_]\w*)\s*\((?P<params>.*?)\)\s*(?:throws\s*(?P<throws>.*?))?;",
        re.S,
    )
    for i, line in enumerate(lines, start=1):
        raw = line
        for marker, gname in group_patterns:
            if marker in raw:
                group = gname
        msvc = re.match(r'\s*//\s*([0-9]+(?:\.[0-9]+)+)', raw)
        if msvc:
            service = msvc.group(1)
        if not collecting:
            # skip comments / package / imports
            if start_re.search(raw) and not raw.lstrip().startswith('//') and ' interface ' not in raw and ' enum ' not in raw:
                collecting = True
                current = raw.strip() + ' '
                start_line = i
                if ';' in raw:
                    collecting = False
            else:
                continue
        else:
            current += raw.strip() + ' '
            if ';' in raw:
                collecting = False
        if not collecting and current:
            m = sig_re.search(current)
            if m:
                ret = ' '.join(m.group('return').split())
                name = m.group('name')
                params = ' '.join((m.group('params') or '').split())
                throws_blob = m.group('throws') or ''
                throws_blob = re.sub(r'\s+', '', throws_blob)
                throws = [x for x in throws_blob.split(',') if x]
                methods.append(Method('java', interface, name, ret, params, throws, service, group, str(file.relative_to(SPEC)), start_line))
            current = ''
            start_line = None
    return methods

def parse_cpp_methods(file: Path, interface: str) -> list[Method]:
    text = file.read_text(errors='replace')
    clean = strip_block_comments_keep_lines(text)
    # remove C++ line comments but preserve group? no group needed
    sig_re = re.compile(
        r"virtual\s+(?P<return>[^;()]+?)\s+(?P<name>[A-Za-z_]\w*)\s*\((?P<params>.*?)\)\s*"
        r"(?:throw\s*\((?P<throws>.*?)\))?\s*(?:=\s*0)?\s*;",
        re.S,
    )
    methods: list[Method] = []
    for m in sig_re.finditer(clean):
        name = m.group('name')
        if name in {'RTIambassador','FederateAmbassador'} or name.startswith('~'):
            continue
        # line number
        line = clean[:m.start()].count('\n') + 1
        ret = ' '.join(m.group('return').split())
        params = ' '.join((m.group('params') or '').split())
        throws_blob = m.group('throws') or ''
        throws = []
        if throws_blob.strip():
            throws = [re.sub(r'\bRTI_EXPORT\b|\s', '', t) for t in throws_blob.split(',') if t.strip()]
        methods.append(Method('cpp', interface, name, ret, params, throws, source_file=str(file.relative_to(SPEC)), source_line=line))
    return methods

def parse_enums() -> dict[str, list[tuple[str,int|None]]]:
    enums: dict[str, list[tuple[str,int|None]]] = {}
    for f in JAVA_ROOT.glob('*.java'):
        txt = f.read_text(errors='replace')
        m = re.search(r'public\s+enum\s+(\w+)\s*\{(?P<body>.*?)\n\}', txt, flags=re.S)
        if not m:
            continue
        name = m.group(1)
        body = strip_block_comments_keep_lines(m.group('body'))
        # constants end at first semicolon if present, else full body before methods
        const = body.split(';', 1)[0]
        vals = []
        for part in const.split(','):
            part = part.strip()
            if not part:
                continue
            mm = re.match(r'([A-Z][A-Z0-9_]*)\s*(?:\(\s*([0-9]+)\s*\))?', part)
            if mm:
                vals.append((mm.group(1), int(mm.group(2)) if mm.group(2) else None))
        if vals:
            enums[name] = vals
    # Add C++-only TransportationType
    c = (CPP_ROOT/'Enums.h').read_text(errors='replace')
    for m in re.finditer(r'enum\s+(\w+)\s*\{(.*?)\};', c, flags=re.S):
        name = m.group(1)
        if name in enums:
            continue
        vals=[]
        for part in m.group(2).split(','):
            part = re.sub(r'//.*', '', part).strip()
            if not part:
                continue
            mm = re.match(r'([A-Z][A-Z0-9_]*)\s*(?:=\s*([0-9]+))?', part)
            if mm:
                vals.append((mm.group(1), int(mm.group(2)) if mm.group(2) else None))
        if vals:
            enums[name] = vals
    return enums

def parse_exception_names() -> list[str]:
    names = []
    for f in sorted((JAVA_ROOT/'exceptions').glob('*.java')):
        txt = f.read_text(errors='replace')
        m = re.search(r'class\s+(\w+)\s+extends\s+(\w+)', txt)
        if m:
            names.append(m.group(1))
    return names

def parse_handles() -> list[str]:
    handles = []
    for f in JAVA_ROOT.glob('*Handle.java'):
        handles.append(f.stem)
    return sorted(set(handles))

def camel_to_snake(name: str) -> str:
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    return s2.replace('HLA', 'hla').lower()

def write(path: Path, data: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding='utf-8')

def method_metadata(methods: list[Method]) -> dict[str, dict[str, list[dict]]]:
    meta: dict[str, dict[str, list[dict]]] = {}
    for m in methods:
        meta.setdefault(m.interface, {}).setdefault(m.name, []).append(asdict(m))
    return meta

def py_str(obj) -> str:
    return repr(obj)

def make_enums_py(enums: dict[str, list[tuple[str,int|None]]]) -> str:
    chunks = [f'''"""Enumerations derived from the public IEEE 1516.1-2010 Java/C++ API files.

"""
from __future__ import annotations
from enum import Enum, auto

    ''']
    for name in sorted(enums):
        chunks.append(f'class {name}(Enum):\n')
        for const, val in enums[name]:
            if val is None:
                chunks.append(f'    {const} = auto()\n')
            else:
                chunks.append(f'    {const} = {val}\n')
        chunks.append('\n')
    chunks.append('__all__ = [name for name, value in globals().items() if isinstance(value, type) and issubclass(value, Enum)]\n')
    return ''.join(chunks)

def make_exceptions_py(names: list[str]) -> str:
    body = f'''"""Exception hierarchy derived from the public IEEE 1516.1-2010 Java API files.

The Java binding declares checked exceptions on API methods. Python keeps the
standard names for adapter compatibility, but does not use checked exception
declarations.

"""
from __future__ import annotations

class RTIexception(Exception):
    """Base class for HLA RTI exceptions."""

    def __init__(self, message: str | None = None, *, cause: BaseException | None = None):
        super().__init__(message if message is not None else self.__class__.__name__)
        self.cause = cause

# Python spelling alias; the Java API uses RTIexception.
RTIException = RTIexception

'''
    for name in names:
        if name == 'RTIexception':
            continue
        body += f'class {name}(RTIexception):\n    """HLA exception {name}."""\n\n'
    body += "__all__ = ['RTIexception', 'RTIException', " + ', '.join(repr(n) for n in names if n != 'RTIexception') + "]\n"
    return body

def make_handles_py(handles: list[str]) -> str:
    body = f'''"""Opaque handle value objects for the HLA 1516.1-2010 Python API.

"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, TypeVar, Generic

@dataclass(frozen=True, order=True)
class Handle:
    """Opaque, hashable handle. The numeric value is adapter-local."""
    value: int

    def encoded(self) -> bytes:
        return int(self.value).to_bytes(8, byteorder='big', signed=False)

    @classmethod
    def decode(cls, data: bytes) -> 'Handle':
        return cls(int.from_bytes(data, byteorder='big', signed=False))

T = TypeVar('T', bound=Handle)

class HandleFactory(Generic[T]):
    def __init__(self, handle_type: type[T]):
        self.handle_type = handle_type

    def decode(self, data: bytes) -> T:
        return self.handle_type(int.from_bytes(data, byteorder='big', signed=False))

    def make(self, value: int) -> T:
        return self.handle_type(value)

'''
    for h in handles:
        body += f'@dataclass(frozen=True, order=True)\nclass {h}(Handle):\n    pass\n\n'
    # aliases for sets and maps
    set_names = ['AttributeHandleSet','DimensionHandleSet','FederateHandleSet','InteractionClassHandleSet','RegionHandleSet']
    map_names = ['AttributeHandleValueMap','ParameterHandleValueMap']
    body += '# Collection aliases matching the Java API names.\n'
    body += 'AttributeHandleSet = set[AttributeHandle]\n'
    body += 'DimensionHandleSet = set[DimensionHandle]\n'
    body += 'FederateHandleSet = set[FederateHandle]\n'
    body += 'InteractionClassHandleSet = set[InteractionClassHandle]\n'
    body += 'RegionHandleSet = set[RegionHandle]\n'
    body += 'AttributeHandleValueMap = dict[AttributeHandle, bytes]\n'
    body += 'ParameterHandleValueMap = dict[ParameterHandle, bytes]\n'
    for h in handles:
        body += f'class {h}Factory(HandleFactory[{h}]):\n    def __init__(self):\n        super().__init__({h})\n\n'
    exports = ['Handle','HandleFactory'] + handles + set_names + map_names + [h+'Factory' for h in handles]
    body += '__all__ = ' + repr(exports) + '\n'
    return body

def make_time_py() -> str:
    return f'''"""Logical time support for the starter HLA 1516.1-2010 Python binding.

"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, TypeVar, Generic
import math, struct

class LogicalTimeInterval(Protocol):
    def is_zero(self) -> bool: ...
    def is_epsilon(self) -> bool: ...

TInterval = TypeVar('TInterval', bound=LogicalTimeInterval)

class LogicalTime(Protocol[TInterval]):
    def is_initial(self) -> bool: ...
    def is_final(self) -> bool: ...
    def add(self, val: TInterval): ...
    def subtract(self, val: TInterval): ...
    def distance(self, val): ...
    def encoded_length(self) -> int: ...
    def encode(self) -> bytes: ...

@dataclass(frozen=True, order=True)
class HLAinteger64Interval:
    value: int = 0
    def is_zero(self) -> bool: return self.value == 0
    def is_epsilon(self) -> bool: return self.value == 1
    def encode(self) -> bytes: return struct.pack('>q', self.value)
    @classmethod
    def decode(cls, data: bytes) -> 'HLAinteger64Interval': return cls(struct.unpack('>q', data[:8])[0])

@dataclass(frozen=True, order=True)
class HLAinteger64Time:
    value: int = 0
    INITIAL: int = 0
    FINAL: int = 2**63 - 1
    def is_initial(self) -> bool: return self.value == self.INITIAL
    def is_final(self) -> bool: return self.value == self.FINAL
    def add(self, val: HLAinteger64Interval) -> 'HLAinteger64Time': return HLAinteger64Time(self.value + val.value)
    def subtract(self, val: HLAinteger64Interval) -> 'HLAinteger64Time': return HLAinteger64Time(self.value - val.value)
    def distance(self, val: 'HLAinteger64Time') -> HLAinteger64Interval: return HLAinteger64Interval(self.value - val.value)
    def encoded_length(self) -> int: return 8
    def encode(self) -> bytes: return struct.pack('>q', self.value)
    @classmethod
    def decode(cls, data: bytes) -> 'HLAinteger64Time': return cls(struct.unpack('>q', data[:8])[0])

@dataclass(frozen=True, order=True)
class HLAfloat64Interval:
    value: float = 0.0
    def is_zero(self) -> bool: return self.value == 0.0
    def is_epsilon(self) -> bool: return self.value == math.ulp(1.0)
    def encode(self) -> bytes: return struct.pack('>d', self.value)
    @classmethod
    def decode(cls, data: bytes) -> 'HLAfloat64Interval': return cls(struct.unpack('>d', data[:8])[0])

@dataclass(frozen=True, order=True)
class HLAfloat64Time:
    value: float = 0.0
    def is_initial(self) -> bool: return self.value == 0.0
    def is_final(self) -> bool: return math.isinf(self.value) and self.value > 0
    def add(self, val: HLAfloat64Interval) -> 'HLAfloat64Time': return HLAfloat64Time(self.value + val.value)
    def subtract(self, val: HLAfloat64Interval) -> 'HLAfloat64Time': return HLAfloat64Time(self.value - val.value)
    def distance(self, val: 'HLAfloat64Time') -> HLAfloat64Interval: return HLAfloat64Interval(self.value - val.value)
    def encoded_length(self) -> int: return 8
    def encode(self) -> bytes: return struct.pack('>d', self.value)
    @classmethod
    def decode(cls, data: bytes) -> 'HLAfloat64Time': return cls(struct.unpack('>d', data[:8])[0])

class HLAinteger64TimeFactory:
    name = 'HLAinteger64Time'
    def make_initial(self) -> HLAinteger64Time: return HLAinteger64Time(HLAinteger64Time.INITIAL)
    def make_final(self) -> HLAinteger64Time: return HLAinteger64Time(HLAinteger64Time.FINAL)
    def make_time(self, value: int) -> HLAinteger64Time: return HLAinteger64Time(value)
    def make_interval(self, value: int) -> HLAinteger64Interval: return HLAinteger64Interval(value)

class HLAfloat64TimeFactory:
    name = 'HLAfloat64Time'
    def make_initial(self) -> HLAfloat64Time: return HLAfloat64Time(0.0)
    def make_final(self) -> HLAfloat64Time: return HLAfloat64Time(float('inf'))
    def make_time(self, value: float) -> HLAfloat64Time: return HLAfloat64Time(value)
    def make_interval(self, value: float) -> HLAfloat64Interval: return HLAfloat64Interval(value)

__all__ = [
    'LogicalTime',
    'LogicalTimeInterval',
    'HLAinteger64Interval',
    'HLAinteger64Time',
    'HLAinteger64TimeFactory',
    'HLAfloat64Interval',
    'HLAfloat64Time',
    'HLAfloat64TimeFactory',
]
'''

def make_types_py() -> str:
    return f'''"""Small value objects and collection aliases for the HLA Python API scaffold.

"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .handles import *
from .enums import SaveStatus, RestoreStatus
from .time import LogicalTime

@dataclass(frozen=True)
class RangeBounds:
    lower_bound: int
    upper_bound: int

@dataclass(frozen=True)
class AttributeRegionAssociation:
    attributes: AttributeHandleSet
    regions: RegionHandleSet

AttributeSetRegionSetPairList = list[AttributeRegionAssociation]

@dataclass(frozen=True)
class MessageRetractionReturn:
    handle: MessageRetractionHandle
    time: Any | None = None

@dataclass(frozen=True)
class TimeQueryReturn:
    time_is_valid: bool
    time: Any | None = None

@dataclass(frozen=True)
class FederateHandleSaveStatusPair:
    federate_handle: FederateHandle
    save_status: SaveStatus

@dataclass(frozen=True)
class FederateRestoreStatus:
    pre_restore_handle: FederateHandle
    post_restore_handle: FederateHandle
    restore_status: RestoreStatus

@dataclass(frozen=True)
class FederationExecutionInformation:
    federation_execution_name: str
    logical_time_implementation_name: str | None = None

FederationExecutionInformationSet = set[FederationExecutionInformation]

__all__ = [name for name in globals() if not name.startswith('_')]
'''

def make_encoding_py() -> str:
    return f'''"""Minimal HLA encoding elements for early tests and FOM adapters.

This module intentionally implements a small, practical subset first. It uses
big/little-endian names that match the public API names and can be extended to
full encoder-factory coverage.

"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Iterable, Sequence
import struct

class EncoderException(Exception): pass
class DecoderException(Exception): pass

class DataElement:
    def encode(self) -> bytes: raise NotImplementedError
    def decode(self, data: bytes) -> None: raise NotImplementedError
    def encoded_length(self) -> int: return len(self.encode())

@dataclass
class _Scalar(DataElement):
    value: object = 0
    _fmt: str = ''
    def encode(self) -> bytes: return struct.pack(self._fmt, self.value)
    def decode(self, data: bytes) -> None: self.value = struct.unpack(self._fmt, data[:struct.calcsize(self._fmt)])[0]

class HLAboolean(_Scalar):
    def __init__(self, value: bool=False): super().__init__(bool(value), '>B')
    def encode(self) -> bytes: return struct.pack('>B', 1 if self.value else 0)
    def decode(self, data: bytes) -> None: self.value = bool(struct.unpack('>B', data[:1])[0])

class HLAbyte(_Scalar):
    def __init__(self, value: int=0): super().__init__(value, 'b')
class HLAoctet(_Scalar):
    def __init__(self, value: int=0): super().__init__(value, 'B')
class HLAinteger16BE(_Scalar):
    def __init__(self, value: int=0): super().__init__(value, '>h')
class HLAinteger16LE(_Scalar):
    def __init__(self, value: int=0): super().__init__(value, '<h')
class HLAinteger32BE(_Scalar):
    def __init__(self, value: int=0): super().__init__(value, '>i')
class HLAinteger32LE(_Scalar):
    def __init__(self, value: int=0): super().__init__(value, '<i')
class HLAinteger64BE(_Scalar):
    def __init__(self, value: int=0): super().__init__(value, '>q')
class HLAinteger64LE(_Scalar):
    def __init__(self, value: int=0): super().__init__(value, '<q')
class HLAfloat32BE(_Scalar):
    def __init__(self, value: float=0.0): super().__init__(value, '>f')
class HLAfloat32LE(_Scalar):
    def __init__(self, value: float=0.0): super().__init__(value, '<f')
class HLAfloat64BE(_Scalar):
    def __init__(self, value: float=0.0): super().__init__(value, '>d')
class HLAfloat64LE(_Scalar):
    def __init__(self, value: float=0.0): super().__init__(value, '<d')
class HLAoctetPairBE(_Scalar):
    def __init__(self, value: int=0): super().__init__(value, '>H')
class HLAoctetPairLE(_Scalar):
    def __init__(self, value: int=0): super().__init__(value, '<H')

@dataclass
class HLAASCIIchar(DataElement):
    value: str = '\\x00'
    def encode(self) -> bytes: return self.value.encode('ascii')[:1]
    def decode(self, data: bytes) -> None: self.value = data[:1].decode('ascii')

@dataclass
class HLAunicodeChar(DataElement):
    value: str = '\\x00'
    def encode(self) -> bytes: return self.value.encode('utf-16-be')[:2]
    def decode(self, data: bytes) -> None: self.value = data[:2].decode('utf-16-be')

@dataclass
class HLAASCIIstring(DataElement):
    value: str = ''
    def encode(self) -> bytes:
        payload = self.value.encode('ascii')
        return struct.pack('>I', len(payload)) + payload
    def decode(self, data: bytes) -> None:
        n = struct.unpack('>I', data[:4])[0]
        self.value = data[4:4+n].decode('ascii')

@dataclass
class HLAunicodeString(DataElement):
    value: str = ''
    def encode(self) -> bytes:
        payload = self.value.encode('utf-16-be')
        return struct.pack('>I', len(payload)) + payload
    def decode(self, data: bytes) -> None:
        n = struct.unpack('>I', data[:4])[0]
        self.value = data[4:4+n].decode('utf-16-be')

@dataclass
class HLAopaqueData(DataElement):
    value: bytes = b''
    def encode(self) -> bytes: return struct.pack('>I', len(self.value)) + self.value
    def decode(self, data: bytes) -> None:
        n = struct.unpack('>I', data[:4])[0]
        self.value = data[4:4+n]

@dataclass
class HLAfixedRecord(DataElement):
    fields: list[DataElement] = field(default_factory=list)
    def encode(self) -> bytes: return b''.join(f.encode() for f in self.fields)
    def decode(self, data: bytes) -> None:
        offset = 0
        for f in self.fields:
            f.decode(data[offset:])
            offset += f.encoded_length()

@dataclass
class HLAfixedArray(DataElement):
    elements: list[DataElement] = field(default_factory=list)
    def encode(self) -> bytes: return b''.join(e.encode() for e in self.elements)
    def decode(self, data: bytes) -> None:
        offset = 0
        for e in self.elements:
            e.decode(data[offset:])
            offset += e.encoded_length()

@dataclass
class HLAvariableArray(DataElement):
    elements: list[DataElement] = field(default_factory=list)
    def encode(self) -> bytes: return struct.pack('>I', len(self.elements)) + b''.join(e.encode() for e in self.elements)
    def decode(self, data: bytes) -> None:
        # Caller must provide pre-sized element instances; we decode up to that count.
        count = struct.unpack('>I', data[:4])[0]
        if count != len(self.elements):
            raise DecoderException(f'variable array expected {{len(self.elements)}} elements, encoded {{count}}')
        offset = 4
        for e in self.elements:
            e.decode(data[offset:])
            offset += e.encoded_length()

__all__ = [name for name in globals() if name.startswith('HLA') or name in {'DataElement','EncoderException','DecoderException'}]
'''

def make_raw_api_py(java_methods: list[Method], cpp_methods: list[Method]) -> str:
    methods = java_methods + cpp_methods
    meta = method_metadata(methods)
    rti_names = sorted(set(meta.get('RTIambassador',{})))
    fed_names = sorted(set(meta.get('FederateAmbassador',{})))
    # prepare compact source metadata as dict literal of only keys we want
    simple_meta = {}
    for iface, byname in meta.items():
        simple_meta[iface] = {}
        for name, vals in byname.items():
            simple_meta[iface][name] = [
                {k:v for k,v in m.items() if k in ['language','return_type','params','throws','service','group','source_file','source_line']}
                for m in vals
            ]
    body = f'''"""Source-derived raw API surface for HLA IEEE 1516.1-2010.

Method names intentionally preserve the Java/C++ lowerCamelCase spelling.  The
methods accept ``*args``/``**kwargs`` because Java and C++ overloads do not map
1:1 onto a single Python signature.  See ``API_METADATA`` for overload records.

"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

API_METADATA = {py_str(simple_meta)}

class RTIambassador(ABC):
    """Abstract RTI ambassador interface. RTI adapters implement these methods."""

'''
    for name in rti_names:
        count = len(meta['RTIambassador'][name])
        body += (
            f"    @abstractmethod\n"
            f"    def {name}(self, *args: Any, **kwargs: Any) -> Any:\n"
            f'        """{name}; {count} source overload(s). See API_METADATA. """\n'
            f"        raise NotImplementedError\n\n"
        )
    body += 'class FederateAmbassador:\n    """No-op federate callback base preserving source method names."""\n\n'
    for name in fed_names:
        count = len(meta['FederateAmbassador'][name])
        body += (
            f"    def {name}(self, *args: Any, **kwargs: Any) -> Any:\n"
            f'        """{name}; {count} source overload(s). Override in a federate."""\n'
            f"        return None\n\n"
        )
    body += (
        "RTIAmbassador = RTIambassador\n"
        "NullFederateAmbassador = FederateAmbassador\n"
        "__all__ = ['API_METADATA', 'RTIambassador', 'RTIAmbassador', "
        "'FederateAmbassador', 'NullFederateAmbassador']\n"
    )
    return body

def make_api_py(java_methods: list[Method], cpp_methods: list[Method]) -> str:
    methods = java_methods + cpp_methods
    meta = method_metadata(methods)
    rti_names = sorted(set(meta.get('RTIambassador',{})))
    fed_names = sorted(set(meta.get('FederateAmbassador',{})))
    body = f'''"""Pythonic convenience layer for the HLA 1516.1-2010 API scaffold.

This layer exposes explicit runtime facade classes with snake_case aliases while
retaining the source lowerCamelCase API.

"""
from __future__ import annotations
from typing import Any
from ._spec_impl import RTIambassadorSpec as RawRTIambassador, FederateAmbassadorSpec as RawFederateAmbassador

class RTIambassador(RawRTIambassador):
    """Concrete subclass point for Python RTI adapters with explicit snake_case aliases."""

'''
    used = set()
    for name in rti_names:
        snake = camel_to_snake(name)
        if snake == name or snake in used:
            continue
        used.add(snake)
        body += (
            f"    def {snake}(self, *args: Any, **kwargs: Any) -> Any:\n"
            f"        return self.{name}(*args, **kwargs)\n\n"
        )
    body += "RTIAmbassador = RTIambassador\n\n"
    body += (
        "class FederateAmbassador(RawFederateAmbassador):\n"
        '    """Federate callback base with snake_case hooks.\n\n'
        "    Override either the source lowerCamelCase callback or the corresponding\n"
        "    snake_case hook. The lowerCamelCase default forwards to the hook.\n"
        '    """\n\n'
    )
    used = set()
    for name in fed_names:
        snake = camel_to_snake(name)
        if snake == name or snake in used:
            continue
        used.add(snake)
        # source method forwards to hook, hook no-op. However this overrides all callbacks and loses raw docstrings.
        body += (
            f"    def {name}(self, *args: Any, **kwargs: Any) -> Any:\n"
            f"        return self.{snake}(*args, **kwargs)\n\n"
        )
        body += (
            f"    def {snake}(self, *args: Any, **kwargs: Any) -> Any:\n"
            f"        return None\n\n"
        )
    body += (
        "NullFederateAmbassador = FederateAmbassador\n"
        "__all__ = ['RTIambassador', 'RTIAmbassador', 'FederateAmbassador', "
        "'NullFederateAmbassador']\n"
    )
    return body

def make_init_py(enums, handles, exceptions) -> str:
    return f'''"""Unofficial Python scaffold for IEEE 1516.1-2010 HLA APIs.

This package is an API surface and utility scaffold, not a complete RTI.
"""
from .enums import *
from .exceptions import *
from .handles import *
from .time import *
from .types import *
from ._spec_impl import RTIambassadorSpec, FederateAmbassadorSpec
from .runtime_api import RTIambassador, RTIAmbassador, FederateAmbassador, NullFederateAmbassador

__version__ = '0.3.0'
'''

def make_analysis(api_inventory: dict, java_methods, cpp_methods, enums, exceptions, handles) -> tuple[str,str,str]:
    j_rti = [m for m in java_methods if m.interface=='RTIambassador']
    j_fed = [m for m in java_methods if m.interface=='FederateAmbassador']
    c_rti = [m for m in cpp_methods if m.interface=='RTIambassador']
    c_fed = [m for m in cpp_methods if m.interface=='FederateAmbassador']
    def uniq(ms): return sorted(set(m.name for m in ms))
    jr, jf, cr, cf = map(uniq, [j_rti,j_fed,c_rti,c_fed])
    comparison = f'''# HLA 1516.1-2010 Java/C++ API comparison

Source material: official public API ZIPs from `1516.1-2010_downloads.zip` and schema/examples from `1516.2-2010_downloads.zip`.


## Inventory

| Area | Count |
|---|---:|
| Java `.java` files | {api_inventory['java_file_count']} |
| Java exception classes | {len(exceptions)} |
| Java `RTIambassador` overloads / unique names | {len(j_rti)} / {len(jr)} |
| Java `FederateAmbassador` overloads / unique names | {len(j_fed)} / {len(jf)} |
| C++ header files | {api_inventory['cpp_header_count']} |
| C++ `RTIambassador` overloads / unique names | {len(c_rti)} / {len(cr)} |
| C++ `FederateAmbassador` overloads / unique names | {len(c_fed)} / {len(cf)} |
| Enum classes | {len(enums)} |
| Opaque handle classes | {len(handles)} |

## Mapping strategy for Python

1. Preserve the raw lowerCamelCase API in `hla2010.raw_api` so Java/C++ method names remain searchable.
2. Add snake_case aliases in `hla2010.api` for Python code.
3. Collapse Java/C++ overloads into `*args`/`**kwargs` at the raw scaffold level;
   a later typed facade can turn the common overload families into explicit
   keyword signatures.
4. Represent Java `byte[]` and C++ `VariableLengthData` as `bytes`.
5. Represent C++ output parameters as Python return values.
6. Preserve named exceptions, but do not emulate Java checked-exception declarations.
7. Treat handles as opaque, hashable value objects; adapter implementations decide the local encoding.

## Java-only `RTIambassador` method names

{', '.join(sorted(set(jr)-set(cr))) or 'None'}

## C++-only `RTIambassador` method names

{', '.join(sorted(set(cr)-set(jr))) or 'None'}

## Java-only `FederateAmbassador` callback names

{', '.join(sorted(set(jf)-set(cf))) or 'None'}

## C++-only `FederateAmbassador` callback names

{', '.join(sorted(set(cf)-set(jf))) or 'None'}

## Service groups in Java `RTIambassador`

'''
    bygroup = {}
    for m in j_rti:
        bygroup.setdefault(m.group or 'Unclassified', set()).add(m.name)
    for g, names in bygroup.items():
        comparison += f'- {g}: {len(names)} unique method names\n'
    manifest = '# Extracted source manifest\n\n'
    for key, val in api_inventory.items():
        manifest += f'- {key}: {val}\n'
    return comparison, manifest, json.dumps(api_inventory, indent=2, sort_keys=True)

def build():
    ensure_specs_unpacked()
    if OUT.exists():
        shutil.rmtree(OUT)
    if ZIP.exists():
        ZIP.unlink()
    java_methods = parse_java_methods(JAVA_ROOT / 'RTIambassador.java', 'RTIambassador') + parse_java_methods(
        JAVA_ROOT / 'FederateAmbassador.java', 'FederateAmbassador'
    )
    cpp_methods = parse_cpp_methods(CPP_ROOT / 'RTIambassador.h', 'RTIambassador') + parse_cpp_methods(
        CPP_ROOT / 'FederateAmbassador.h', 'FederateAmbassador'
    )
    enums = parse_enums()
    exceptions = parse_exception_names()
    handles = parse_handles()
    api_inventory = {
        'source_zip_1516_1': str((ROOT/'1516.1-2010_downloads.zip')),
        'source_zip_1516_2': str((ROOT/'1516.2-2010_downloads.zip')),
        'java_source_root': str(JAVA_ROOT),
        'cpp_source_root': str(CPP_ROOT),
        'java_file_count': len(list(JAVA_ROOT.rglob('*.java'))),
        'cpp_header_count': len(list(CPP_ROOT.rglob('*.h'))),
        'java_rti_overloads': len([m for m in java_methods if m.interface=='RTIambassador']),
        'java_rti_unique': len(set(m.name for m in java_methods if m.interface=='RTIambassador')),
        'java_federate_overloads': len([m for m in java_methods if m.interface=='FederateAmbassador']),
        'java_federate_unique': len(set(m.name for m in java_methods if m.interface=='FederateAmbassador')),
        'cpp_rti_overloads': len([m for m in cpp_methods if m.interface=='RTIambassador']),
        'cpp_rti_unique': len(set(m.name for m in cpp_methods if m.interface=='RTIambassador')),
        'cpp_federate_overloads': len([m for m in cpp_methods if m.interface=='FederateAmbassador']),
        'cpp_federate_unique': len(set(m.name for m in cpp_methods if m.interface=='FederateAmbassador')),
        'exceptions_count': len(exceptions),
        'enum_count': len(enums),
        'handle_count': len(handles),
        'schemas_and_examples': sorted(
            [str(p.relative_to(SPEC)) for p in (SPEC / '1516.1-2010_downloads').glob('*') if p.suffix.lower() in {'.xsd', '.xml', '.wsdl'}]
            + [str(p.relative_to(SPEC)) for p in (SPEC / '1516.2-2010_downloads').glob('*') if p.suffix.lower() in {'.xsd', '.xml', '.wsdl'}]
        ),
    }
    comparison, manifest, inventory_json = make_analysis(api_inventory, java_methods, cpp_methods, enums, exceptions, handles)
    # package files
    write(
        OUT / 'NOTICE',
        f'''This package is an unofficial Python scaffold generated from the public
IEEE 1516.1-2010 Java/C++ API materials and IEEE 1516.2-2010 schema/example
materials provided in the downloaded ZIP bundles.

This package is not an IEEE publication and is not a complete RTI implementation.
''',
    )
    write(OUT/'pyproject.toml', '''[project]
name = "hla2010-python-scaffold"
version = "0.3.0"
description = "Unofficial Python API scaffold for IEEE 1516.1-2010 HLA APIs"
requires-python = ">=3.10"

[tool.setuptools.packages.find]
include = ["hla2010*"]
''')
    write(OUT/'hla2010/enums.py', make_enums_py(enums))
    write(OUT/'hla2010/exceptions.py', make_exceptions_py(exceptions))
    write(OUT/'hla2010/handles.py', make_handles_py(handles))
    write(OUT/'hla2010/time.py', make_time_py())
    write(OUT/'hla2010/types.py', make_types_py())
    write(OUT/'hla2010/encoding.py', make_encoding_py())
    write(OUT/'hla2010/raw_api.py', make_raw_api_py(java_methods, cpp_methods))
    write(OUT/'hla2010/api.py', make_api_py(java_methods, cpp_methods))
    write(OUT/'hla2010/__init__.py', make_init_py(enums, handles, exceptions))
    write(OUT/'analysis/api_inventory.json', inventory_json)
    write(OUT/'analysis/java_methods.json', json.dumps([asdict(m) for m in java_methods], indent=2, sort_keys=True))
    write(OUT/'analysis/cpp_methods.json', json.dumps([asdict(m) for m in cpp_methods], indent=2, sort_keys=True))
    write(OUT/'analysis/api_comparison.md', comparison)
    write(OUT/'analysis/source_manifest.md', manifest)
    write(OUT/'docs_mapping.md', comparison)
    write(OUT/'README.md', f'''# hla2010-python-scaffold

Unofficial Python API scaffold for HLA Evolved / IEEE 1516.1-2010-style interfaces.

## What this contains

- `hla2010.raw_api`: source-derived lowerCamelCase API names from Java/C++.
- `hla2010.api`: snake_case convenience layer for Python code.
- `hla2010.enums`: enum classes derived from Java and C++ API files.
- `hla2010.exceptions`: the 110 Java exception names as Python exception classes.
- `hla2010.handles`: opaque handle value objects and collection aliases.
- `hla2010.time`: initial `HLAinteger64Time` and `HLAfloat64Time` support.
- `hla2010.encoding`: minimal HLA primitive/composite encoding elements for tests.
- `analysis/`: machine-readable method inventories and Java/C++ comparison notes.

This is not a complete RTI. It is a starting API and adapter target for writing a Python binding or a Python-facing RTI wrapper.

## Current source inventory

- Java files parsed: {api_inventory['java_file_count']}
- C++ headers parsed: {api_inventory['cpp_header_count']}
- Java `RTIambassador`: {api_inventory['java_rti_overloads']} overloads, {api_inventory['java_rti_unique']} unique names
- Java `FederateAmbassador`: {api_inventory['java_federate_overloads']} overloads, {api_inventory['java_federate_unique']} unique names
- C++ `RTIambassador`: {api_inventory['cpp_rti_overloads']} overloads, {api_inventory['cpp_rti_unique']} unique names
- C++ `FederateAmbassador`: {api_inventory['cpp_federate_overloads']} overloads, {api_inventory['cpp_federate_unique']} unique names

## Minimal use

```python
from hla2010 import CallbackModel
from hla2010.spec import FederateAmbassadorSpec as FederateAmbassador

class MyFederate(FederateAmbassador):
    def time_advance_grant(self, the_time):
        print("granted", the_time)

# vendor_or_local_rti.connect(MyFederate(), CallbackModel.HLA_EVOKED)
```

See `analysis/api_comparison.md` for the Java/C++ differences that the Python surface needs to reconcile.
''')
    write(OUT/'examples/minimal_federate.py', '''from hla2010 import CallbackModel
from hla2010.spec import FederateAmbassadorSpec as FederateAmbassador

class MinimalFederate(FederateAmbassador):
    def connection_lost(self, fault_description: str):
        print("connection lost:", fault_description)

    def time_advance_grant(self, the_time):
        print("time advance granted:", the_time)

# A real federate will obtain a vendor-backed or local RTIAmbassador adapter.
# rti.connect(MinimalFederate(), CallbackModel.HLA_EVOKED)
''')
    write(OUT/'tools/analyze_specs.py', Path('/tmp/build_hla2010_package.py').read_text())
    # validation
    os.system(f'PYTHONPATH={OUT} python -m compileall -q {OUT}/hla2010')
    # import smoke test
    import subprocess
    import sys
    subprocess.run(
        [
            sys.executable,
            '-c',
            'import hla2010; from hla2010 import SaveFailureReason, RTIexception, AttributeHandle; '
            'import hla2010.raw_api as r; print(hla2010.__version__, len(r.API_METADATA["RTIambassador"]))',
        ],
        env={**os.environ, 'PYTHONPATH': str(OUT)},
        check=True,
    )
    # zip
    shutil.make_archive(str(ZIP.with_suffix('')), 'zip', OUT)
    print(json.dumps({'out': str(OUT), 'zip': str(ZIP), **api_inventory}, indent=2))

if __name__ == '__main__':
    build()
