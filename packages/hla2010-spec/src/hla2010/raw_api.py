# Generated from specs/hla2010_api.json.
# Do not edit by hand. Run ./tools/spec-api generate.
"""Source-derived raw API surface for HLA IEEE 1516.1-2010.

Method names intentionally preserve the Java/C++ lowerCamelCase spelling.  The
methods accept ``*args``/``**kwargs`` because Java and C++ overloads do not map
1:1 onto a single Python signature.  See ``API_METADATA`` for overload records.

"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

API_METADATA = {   'FederateAmbassador': {   'announceSynchronizationPoint': [   {   'group': 'Federation Management',
                                                                      'language': 'java',
                                                                      'params': 'String synchronizationPointLabel, '
                                                                                'byte[] userSuppliedTag',
                                                                      'return_type': 'void',
                                                                      'service': '4.13',
                                                                      'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                      'source_line': 51,
                                                                      'throws': ['FederateInternalError']},
                                                                  {   'group': None,
                                                                      'language': 'cpp',
                                                                      'params': 'std::wstring const & label, '
                                                                                'VariableLengthData const & '
                                                                                'theUserSuppliedTag',
                                                                      'return_type': 'void',
                                                                      'service': None,
                                                                      'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                      'source_line': 69,
                                                                      'throws': ['FederateInternalError']}],
                              'attributeIsNotOwned': [   {   'group': 'Ownership Management',
                                                             'language': 'java',
                                                             'params': 'ObjectInstanceHandle theObject, '
                                                                       'AttributeHandle theAttribute',
                                                             'return_type': 'void',
                                                             'service': '7.18',
                                                             'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                             'source_line': 429,
                                                             'throws': ['FederateInternalError']},
                                                         {   'group': None,
                                                             'language': 'cpp',
                                                             'params': 'ObjectInstanceHandle theObject, '
                                                                       'AttributeHandle theAttribute',
                                                             'return_type': 'void',
                                                             'service': None,
                                                             'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                             'source_line': 458,
                                                             'throws': ['FederateInternalError']}],
                              'attributeIsOwnedByRTI': [   {   'group': 'Ownership Management',
                                                               'language': 'java',
                                                               'params': 'ObjectInstanceHandle theObject, '
                                                                         'AttributeHandle theAttribute',
                                                               'return_type': 'void',
                                                               'service': '7.18',
                                                               'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                               'source_line': 435,
                                                               'throws': ['FederateInternalError']},
                                                           {   'group': None,
                                                               'language': 'cpp',
                                                               'params': 'ObjectInstanceHandle theObject, '
                                                                         'AttributeHandle theAttribute',
                                                               'return_type': 'void',
                                                               'service': None,
                                                               'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                               'source_line': 464,
                                                               'throws': ['FederateInternalError']}],
                              'attributeOwnershipAcquisitionNotification': [   {   'group': 'Ownership Management',
                                                                                   'language': 'java',
                                                                                   'params': 'ObjectInstanceHandle '
                                                                                             'theObject, '
                                                                                             'AttributeHandleSet '
                                                                                             'securedAttributes, '
                                                                                             'byte[] userSuppliedTag',
                                                                                   'return_type': 'void',
                                                                                   'service': '7.7',
                                                                                   'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                                   'source_line': 396,
                                                                                   'throws': ['FederateInternalError']},
                                                                               {   'group': None,
                                                                                   'language': 'cpp',
                                                                                   'params': 'ObjectInstanceHandle '
                                                                                             'theObject, '
                                                                                             'AttributeHandleSet const '
                                                                                             '& securedAttributes, '
                                                                                             'VariableLengthData const '
                                                                                             '& theUserSuppliedTag',
                                                                                   'return_type': 'void',
                                                                                   'service': None,
                                                                                   'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                                   'source_line': 421,
                                                                                   'throws': [   'FederateInternalError']}],
                              'attributeOwnershipUnavailable': [   {   'group': 'Ownership Management',
                                                                       'language': 'java',
                                                                       'params': 'ObjectInstanceHandle theObject, '
                                                                                 'AttributeHandleSet theAttributes',
                                                                       'return_type': 'void',
                                                                       'service': '7.10',
                                                                       'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                       'source_line': 403,
                                                                       'throws': ['FederateInternalError']},
                                                                   {   'group': None,
                                                                       'language': 'cpp',
                                                                       'params': 'ObjectInstanceHandle theObject, '
                                                                                 'AttributeHandleSet const & '
                                                                                 'theAttributes',
                                                                       'return_type': 'void',
                                                                       'service': None,
                                                                       'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                       'source_line': 429,
                                                                       'throws': ['FederateInternalError']}],
                              'attributesInScope': [   {   'group': 'Object Management',
                                                           'language': 'java',
                                                           'params': 'ObjectInstanceHandle theObject, '
                                                                     'AttributeHandleSet theAttributes',
                                                           'return_type': 'void',
                                                           'service': '6.17',
                                                           'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                           'source_line': 314,
                                                           'throws': ['FederateInternalError']},
                                                       {   'group': None,
                                                           'language': 'cpp',
                                                           'params': 'ObjectInstanceHandle theObject, '
                                                                     'AttributeHandleSet const & theAttributes',
                                                           'return_type': 'void',
                                                           'service': None,
                                                           'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                           'source_line': 327,
                                                           'throws': ['FederateInternalError']}],
                              'attributesOutOfScope': [   {   'group': 'Object Management',
                                                              'language': 'java',
                                                              'params': 'ObjectInstanceHandle theObject, '
                                                                        'AttributeHandleSet theAttributes',
                                                              'return_type': 'void',
                                                              'service': '6.18',
                                                              'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                              'source_line': 320,
                                                              'throws': ['FederateInternalError']},
                                                          {   'group': None,
                                                              'language': 'cpp',
                                                              'params': 'ObjectInstanceHandle theObject, '
                                                                        'AttributeHandleSet const & theAttributes',
                                                              'return_type': 'void',
                                                              'service': None,
                                                              'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                              'source_line': 334,
                                                              'throws': ['FederateInternalError']}],
                              'confirmAttributeOwnershipAcquisitionCancellation': [   {   'group': 'Ownership '
                                                                                                   'Management',
                                                                                          'language': 'java',
                                                                                          'params': 'ObjectInstanceHandle '
                                                                                                    'theObject, '
                                                                                                    'AttributeHandleSet '
                                                                                                    'theAttributes',
                                                                                          'return_type': 'void',
                                                                                          'service': '7.16',
                                                                                          'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                                          'source_line': 416,
                                                                                          'throws': [   'FederateInternalError']},
                                                                                      {   'group': None,
                                                                                          'language': 'cpp',
                                                                                          'params': 'ObjectInstanceHandle '
                                                                                                    'theObject, '
                                                                                                    'AttributeHandleSet '
                                                                                                    'const & '
                                                                                                    'theAttributes',
                                                                                          'return_type': 'void',
                                                                                          'service': None,
                                                                                          'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                                          'source_line': 444,
                                                                                          'throws': [   'FederateInternalError']}],
                              'confirmAttributeTransportationTypeChange': [   {   'group': 'Object Management',
                                                                                  'language': 'java',
                                                                                  'params': 'ObjectInstanceHandle '
                                                                                            'theObject, '
                                                                                            'AttributeHandleSet '
                                                                                            'theAttributes, '
                                                                                            'TransportationTypeHandle '
                                                                                            'theTransportation',
                                                                                  'return_type': 'void',
                                                                                  'service': '6.24',
                                                                                  'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                                  'source_line': 352,
                                                                                  'throws': ['FederateInternalError']},
                                                                              {   'group': None,
                                                                                  'language': 'cpp',
                                                                                  'params': 'ObjectInstanceHandle '
                                                                                            'theObject, '
                                                                                            'AttributeHandleSet '
                                                                                            'theAttributes, '
                                                                                            'TransportationType '
                                                                                            'theTransportation',
                                                                                  'return_type': 'void',
                                                                                  'service': None,
                                                                                  'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                                  'source_line': 370,
                                                                                  'throws': ['FederateInternalError']}],
                              'confirmInteractionTransportationTypeChange': [   {   'group': 'Object Management',
                                                                                    'language': 'java',
                                                                                    'params': 'InteractionClassHandle '
                                                                                              'theInteraction, '
                                                                                              'TransportationTypeHandle '
                                                                                              'theTransportation',
                                                                                    'return_type': 'void',
                                                                                    'service': '6.28',
                                                                                    'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                                    'source_line': 366,
                                                                                    'throws': [   'FederateInternalError']},
                                                                                {   'group': None,
                                                                                    'language': 'cpp',
                                                                                    'params': 'InteractionClassHandle '
                                                                                              'theInteraction, '
                                                                                              'TransportationType '
                                                                                              'theTransportation',
                                                                                    'return_type': 'void',
                                                                                    'service': None,
                                                                                    'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                                    'source_line': 386,
                                                                                    'throws': [   'FederateInternalError']}],
                              'connectionLost': [   {   'group': 'Federation Management',
                                                        'language': 'java',
                                                        'params': 'String faultDescription',
                                                        'return_type': 'void',
                                                        'service': '4.4',
                                                        'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                        'source_line': 30,
                                                        'throws': ['FederateInternalError']},
                                                    {   'group': None,
                                                        'language': 'cpp',
                                                        'params': 'std::wstring const & faultDescription',
                                                        'return_type': 'void',
                                                        'service': None,
                                                        'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                        'source_line': 44,
                                                        'throws': ['FederateInternalError']}],
                              'discoverObjectInstance': [   {   'group': 'Object Management',
                                                                'language': 'java',
                                                                'params': 'ObjectInstanceHandle theObject, '
                                                                          'ObjectClassHandle theObjectClass, String '
                                                                          'objectName',
                                                                'return_type': 'void',
                                                                'service': '6.9',
                                                                'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                'source_line': 174,
                                                                'throws': ['FederateInternalError']},
                                                            {   'group': 'Object Management',
                                                                'language': 'java',
                                                                'params': 'ObjectInstanceHandle theObject, '
                                                                          'ObjectClassHandle theObjectClass, String '
                                                                          'objectName, FederateHandle '
                                                                          'producingFederate',
                                                                'return_type': 'void',
                                                                'service': '6.9',
                                                                'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                'source_line': 181,
                                                                'throws': ['FederateInternalError']},
                                                            {   'group': None,
                                                                'language': 'cpp',
                                                                'params': 'ObjectInstanceHandle theObject, '
                                                                          'ObjectClassHandle theObjectClass, '
                                                                          'std::wstring const & theObjectInstanceName',
                                                                'return_type': 'void',
                                                                'service': None,
                                                                'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                'source_line': 209,
                                                                'throws': ['FederateInternalError']},
                                                            {   'group': None,
                                                                'language': 'cpp',
                                                                'params': 'ObjectInstanceHandle theObject, '
                                                                          'ObjectClassHandle theObjectClass, '
                                                                          'std::wstring const & theObjectInstanceName, '
                                                                          'FederateHandle producingFederate',
                                                                'return_type': 'void',
                                                                'service': None,
                                                                'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                'source_line': 216,
                                                                'throws': ['FederateInternalError']}],
                              'federationNotRestored': [   {   'group': 'Federation Management',
                                                               'language': 'java',
                                                               'params': 'RestoreFailureReason reason',
                                                               'return_type': 'void',
                                                               'service': '4.29',
                                                               'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                               'source_line': 116,
                                                               'throws': ['FederateInternalError']},
                                                           {   'group': None,
                                                               'language': 'cpp',
                                                               'params': 'RestoreFailureReason theRestoreFailureReason',
                                                               'return_type': 'void',
                                                               'service': None,
                                                               'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                               'source_line': 141,
                                                               'throws': ['FederateInternalError']}],
                              'federationNotSaved': [   {   'group': 'Federation Management',
                                                            'language': 'java',
                                                            'params': 'SaveFailureReason reason',
                                                            'return_type': 'void',
                                                            'service': '4.20',
                                                            'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                            'source_line': 79,
                                                            'throws': ['FederateInternalError']},
                                                        {   'group': None,
                                                            'language': 'cpp',
                                                            'params': 'SaveFailureReason theSaveFailureReason',
                                                            'return_type': 'void',
                                                            'service': None,
                                                            'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                            'source_line': 99,
                                                            'throws': ['FederateInternalError']}],
                              'federationRestoreBegun': [   {   'group': 'Federation Management',
                                                                'language': 'java',
                                                                'params': '',
                                                                'return_type': 'void',
                                                                'service': '4.26',
                                                                'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                'source_line': 99,
                                                                'throws': ['FederateInternalError']},
                                                            {   'group': None,
                                                                'language': 'cpp',
                                                                'params': '',
                                                                'return_type': 'void',
                                                                'service': None,
                                                                'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                'source_line': 124,
                                                                'throws': ['FederateInternalError']}],
                              'federationRestoreStatusResponse': [   {   'group': 'Federation Management',
                                                                         'language': 'java',
                                                                         'params': 'FederateRestoreStatus[] response',
                                                                         'return_type': 'void',
                                                                         'service': '4.32',
                                                                         'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                         'source_line': 121,
                                                                         'throws': ['FederateInternalError']},
                                                                     {   'group': None,
                                                                         'language': 'cpp',
                                                                         'params': 'FederateRestoreStatusVector const '
                                                                                   '& theFederateRestoreStatusVector',
                                                                         'return_type': 'void',
                                                                         'service': None,
                                                                         'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                         'source_line': 147,
                                                                         'throws': ['FederateInternalError']}],
                              'federationRestored': [   {   'group': 'Federation Management',
                                                            'language': 'java',
                                                            'params': '',
                                                            'return_type': 'void',
                                                            'service': '4.29',
                                                            'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                            'source_line': 111,
                                                            'throws': ['FederateInternalError']},
                                                        {   'group': None,
                                                            'language': 'cpp',
                                                            'params': '',
                                                            'return_type': 'void',
                                                            'service': None,
                                                            'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                            'source_line': 137,
                                                            'throws': ['FederateInternalError']}],
                              'federationSaveStatusResponse': [   {   'group': 'Federation Management',
                                                                      'language': 'java',
                                                                      'params': 'FederateHandleSaveStatusPair[] '
                                                                                'response',
                                                                      'return_type': 'void',
                                                                      'service': '4.23',
                                                                      'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                      'source_line': 84,
                                                                      'throws': ['FederateInternalError']},
                                                                  {   'group': None,
                                                                      'language': 'cpp',
                                                                      'params': 'FederateHandleSaveStatusPairVector '
                                                                                'const & theFederateStatusVector',
                                                                      'return_type': 'void',
                                                                      'service': None,
                                                                      'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                      'source_line': 106,
                                                                      'throws': ['FederateInternalError']}],
                              'federationSaved': [   {   'group': 'Federation Management',
                                                         'language': 'java',
                                                         'params': '',
                                                         'return_type': 'void',
                                                         'service': '4.20',
                                                         'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                         'source_line': 74,
                                                         'throws': ['FederateInternalError']},
                                                     {   'group': None,
                                                         'language': 'cpp',
                                                         'params': '',
                                                         'return_type': 'void',
                                                         'service': None,
                                                         'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                         'source_line': 95,
                                                         'throws': ['FederateInternalError']}],
                              'federationSynchronized': [   {   'group': 'Federation Management',
                                                                'language': 'java',
                                                                'params': 'String synchronizationPointLabel, '
                                                                          'FederateHandleSet failedToSyncSet',
                                                                'return_type': 'void',
                                                                'service': '4.15',
                                                                'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                'source_line': 57,
                                                                'throws': ['FederateInternalError']},
                                                            {   'group': None,
                                                                'language': 'cpp',
                                                                'params': 'std::wstring const & label, '
                                                                          'FederateHandleSet const& failedToSyncSet',
                                                                'return_type': 'void',
                                                                'service': None,
                                                                'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                'source_line': 76,
                                                                'throws': ['FederateInternalError']}],
                              'getProducingFederate': [   {   'group': 'Object Management',
                                                              'language': 'java',
                                                              'params': '',
                                                              'return_type': 'FederateHandle',
                                                              'service': '6.9',
                                                              'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                              'source_line': 193,
                                                              'throws': []},
                                                          {   'group': 'Object Management',
                                                              'language': 'java',
                                                              'params': '',
                                                              'return_type': 'FederateHandle',
                                                              'service': '6.11',
                                                              'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                              'source_line': 238,
                                                              'throws': []},
                                                          {   'group': 'Object Management',
                                                              'language': 'java',
                                                              'params': '',
                                                              'return_type': 'FederateHandle',
                                                              'service': '6.13',
                                                              'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                              'source_line': 281,
                                                              'throws': []}],
                              'getSentRegions': [   {   'group': 'Object Management',
                                                        'language': 'java',
                                                        'params': '',
                                                        'return_type': 'RegionHandleSet',
                                                        'service': '6.9',
                                                        'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                        'source_line': 195,
                                                        'throws': []},
                                                    {   'group': 'Object Management',
                                                        'language': 'java',
                                                        'params': '',
                                                        'return_type': 'RegionHandleSet',
                                                        'service': '6.11',
                                                        'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                        'source_line': 240,
                                                        'throws': []}],
                              'hasProducingFederate': [   {   'group': 'Object Management',
                                                              'language': 'java',
                                                              'params': '',
                                                              'return_type': 'boolean',
                                                              'service': '6.9',
                                                              'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                              'source_line': 189,
                                                              'throws': []},
                                                          {   'group': 'Object Management',
                                                              'language': 'java',
                                                              'params': '',
                                                              'return_type': 'boolean',
                                                              'service': '6.11',
                                                              'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                              'source_line': 234,
                                                              'throws': []},
                                                          {   'group': 'Object Management',
                                                              'language': 'java',
                                                              'params': '',
                                                              'return_type': 'boolean',
                                                              'service': '6.13',
                                                              'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                              'source_line': 279,
                                                              'throws': []}],
                              'hasSentRegions': [   {   'group': 'Object Management',
                                                        'language': 'java',
                                                        'params': '',
                                                        'return_type': 'boolean',
                                                        'service': '6.9',
                                                        'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                        'source_line': 191,
                                                        'throws': []},
                                                    {   'group': 'Object Management',
                                                        'language': 'java',
                                                        'params': '',
                                                        'return_type': 'boolean',
                                                        'service': '6.11',
                                                        'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                        'source_line': 236,
                                                        'throws': []}],
                              'informAttributeOwnership': [   {   'group': 'Ownership Management',
                                                                  'language': 'java',
                                                                  'params': 'ObjectInstanceHandle theObject, '
                                                                            'AttributeHandle theAttribute, '
                                                                            'FederateHandle theOwner',
                                                                  'return_type': 'void',
                                                                  'service': '7.18',
                                                                  'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                  'source_line': 422,
                                                                  'throws': ['FederateInternalError']},
                                                              {   'group': None,
                                                                  'language': 'cpp',
                                                                  'params': 'ObjectInstanceHandle theObject, '
                                                                            'AttributeHandle theAttribute, '
                                                                            'FederateHandle theOwner',
                                                                  'return_type': 'void',
                                                                  'service': None,
                                                                  'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                  'source_line': 451,
                                                                  'throws': ['FederateInternalError']}],
                              'initiateFederateRestore': [   {   'group': 'Federation Management',
                                                                 'language': 'java',
                                                                 'params': 'String label, String federateName, '
                                                                           'FederateHandle federateHandle',
                                                                 'return_type': 'void',
                                                                 'service': '4.27',
                                                                 'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                 'source_line': 104,
                                                                 'throws': ['FederateInternalError']},
                                                             {   'group': None,
                                                                 'language': 'cpp',
                                                                 'params': 'std::wstring const & label, std::wstring '
                                                                           'const & federateName, FederateHandle '
                                                                           'handle',
                                                                 'return_type': 'void',
                                                                 'service': None,
                                                                 'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                 'source_line': 129,
                                                                 'throws': ['FederateInternalError']}],
                              'initiateFederateSave': [   {   'group': 'Federation Management',
                                                              'language': 'java',
                                                              'params': 'String label',
                                                              'return_type': 'void',
                                                              'service': '4.17',
                                                              'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                              'source_line': 63,
                                                              'throws': ['FederateInternalError']},
                                                          {   'group': 'Federation Management',
                                                              'language': 'java',
                                                              'params': 'String label, LogicalTime time',
                                                              'return_type': 'void',
                                                              'service': '4.17',
                                                              'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                              'source_line': 68,
                                                              'throws': ['FederateInternalError']},
                                                          {   'group': None,
                                                              'language': 'cpp',
                                                              'params': 'std::wstring const & label',
                                                              'return_type': 'void',
                                                              'service': None,
                                                              'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                              'source_line': 83,
                                                              'throws': ['FederateInternalError']},
                                                          {   'group': None,
                                                              'language': 'cpp',
                                                              'params': 'std::wstring const & label, LogicalTime const '
                                                                        '& theTime',
                                                              'return_type': 'void',
                                                              'service': None,
                                                              'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                              'source_line': 88,
                                                              'throws': ['FederateInternalError']}],
                              'multipleObjectInstanceNameReservationFailed': [   {   'group': 'Object Management',
                                                                                     'language': 'java',
                                                                                     'params': 'Set<String> '
                                                                                               'objectNames',
                                                                                     'return_type': 'void',
                                                                                     'service': '6.6',
                                                                                     'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                                     'source_line': 169,
                                                                                     'throws': [   'FederateInternalError']},
                                                                                 {   'group': None,
                                                                                     'language': 'cpp',
                                                                                     'params': 'std::set<std::wstring> '
                                                                                               'const & '
                                                                                               'theObjectInstanceNames',
                                                                                     'return_type': 'void',
                                                                                     'service': None,
                                                                                     'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                                     'source_line': 202,
                                                                                     'throws': [   'FederateInternalError']}],
                              'multipleObjectInstanceNameReservationSucceeded': [   {   'group': 'Object Management',
                                                                                        'language': 'java',
                                                                                        'params': 'Set<String> '
                                                                                                  'objectNames',
                                                                                        'return_type': 'void',
                                                                                        'service': '6.6',
                                                                                        'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                                        'source_line': 164,
                                                                                        'throws': [   'FederateInternalError']},
                                                                                    {   'group': None,
                                                                                        'language': 'cpp',
                                                                                        'params': 'std::set<std::wstring> '
                                                                                                  'const & '
                                                                                                  'theObjectInstanceNames',
                                                                                        'return_type': 'void',
                                                                                        'service': None,
                                                                                        'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                                        'source_line': 197,
                                                                                        'throws': [   'FederateInternalError']}],
                              'objectInstanceNameReservationFailed': [   {   'group': 'Object Management',
                                                                             'language': 'java',
                                                                             'params': 'String objectName',
                                                                             'return_type': 'void',
                                                                             'service': '6.3',
                                                                             'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                             'source_line': 159,
                                                                             'throws': ['FederateInternalError']},
                                                                         {   'group': None,
                                                                             'language': 'cpp',
                                                                             'params': 'std::wstring const & '
                                                                                       'theObjectInstanceName',
                                                                             'return_type': 'void',
                                                                             'service': None,
                                                                             'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                             'source_line': 191,
                                                                             'throws': ['FederateInternalError']}],
                              'objectInstanceNameReservationSucceeded': [   {   'group': 'Object Management',
                                                                                'language': 'java',
                                                                                'params': 'String objectName',
                                                                                'return_type': 'void',
                                                                                'service': '6.3',
                                                                                'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                                'source_line': 154,
                                                                                'throws': ['FederateInternalError']},
                                                                            {   'group': None,
                                                                                'language': 'cpp',
                                                                                'params': 'std::wstring const & '
                                                                                          'theObjectInstanceName',
                                                                                'return_type': 'void',
                                                                                'service': None,
                                                                                'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                                'source_line': 186,
                                                                                'throws': ['FederateInternalError']}],
                              'provideAttributeValueUpdate': [   {   'group': 'Object Management',
                                                                     'language': 'java',
                                                                     'params': 'ObjectInstanceHandle theObject, '
                                                                               'AttributeHandleSet theAttributes, '
                                                                               'byte[] userSuppliedTag',
                                                                     'return_type': 'void',
                                                                     'service': '6.20',
                                                                     'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                     'source_line': 326,
                                                                     'throws': ['FederateInternalError']},
                                                                 {   'group': None,
                                                                     'language': 'cpp',
                                                                     'params': 'ObjectInstanceHandle theObject, '
                                                                               'AttributeHandleSet const & '
                                                                               'theAttributes, VariableLengthData '
                                                                               'const & theUserSuppliedTag',
                                                                     'return_type': 'void',
                                                                     'service': None,
                                                                     'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                     'source_line': 341,
                                                                     'throws': ['FederateInternalError']}],
                              'receiveInteraction': [   {   'group': 'Object Management',
                                                            'language': 'java',
                                                            'params': 'InteractionClassHandle interactionClass, '
                                                                      'ParameterHandleValueMap theParameters, byte[] '
                                                                      'userSuppliedTag, OrderType sentOrdering, '
                                                                      'TransportationTypeHandle theTransport, '
                                                                      'SupplementalReceiveInfo receiveInfo',
                                                            'return_type': 'void',
                                                            'service': '6.13',
                                                            'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                            'source_line': 244,
                                                            'throws': ['FederateInternalError']},
                                                        {   'group': 'Object Management',
                                                            'language': 'java',
                                                            'params': 'InteractionClassHandle interactionClass, '
                                                                      'ParameterHandleValueMap theParameters, byte[] '
                                                                      'userSuppliedTag, OrderType sentOrdering, '
                                                                      'TransportationTypeHandle theTransport, '
                                                                      'LogicalTime theTime, OrderType '
                                                                      'receivedOrdering, SupplementalReceiveInfo '
                                                                      'receiveInfo',
                                                            'return_type': 'void',
                                                            'service': '6.13',
                                                            'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                            'source_line': 254,
                                                            'throws': ['FederateInternalError']},
                                                        {   'group': 'Object Management',
                                                            'language': 'java',
                                                            'params': 'InteractionClassHandle interactionClass, '
                                                                      'ParameterHandleValueMap theParameters, byte[] '
                                                                      'userSuppliedTag, OrderType sentOrdering, '
                                                                      'TransportationTypeHandle theTransport, '
                                                                      'LogicalTime theTime, OrderType '
                                                                      'receivedOrdering, MessageRetractionHandle '
                                                                      'retractionHandle, SupplementalReceiveInfo '
                                                                      'receiveInfo',
                                                            'return_type': 'void',
                                                            'service': '6.13',
                                                            'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                            'source_line': 266,
                                                            'throws': ['FederateInternalError']},
                                                        {   'group': None,
                                                            'language': 'cpp',
                                                            'params': 'InteractionClassHandle theInteraction, '
                                                                      'ParameterHandleValueMap const & '
                                                                      'theParameterValues, VariableLengthData const & '
                                                                      'theUserSuppliedTag, OrderType sentOrder, '
                                                                      'TransportationType theType, '
                                                                      'SupplementalReceiveInfo theReceiveInfo',
                                                            'return_type': 'void',
                                                            'service': None,
                                                            'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                            'source_line': 261,
                                                            'throws': ['FederateInternalError']},
                                                        {   'group': None,
                                                            'language': 'cpp',
                                                            'params': 'InteractionClassHandle theInteraction, '
                                                                      'ParameterHandleValueMap const & '
                                                                      'theParameterValues, VariableLengthData const & '
                                                                      'theUserSuppliedTag, OrderType sentOrder, '
                                                                      'TransportationType theType, LogicalTime const & '
                                                                      'theTime, OrderType receivedOrder, '
                                                                      'SupplementalReceiveInfo theReceiveInfo',
                                                            'return_type': 'void',
                                                            'service': None,
                                                            'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                            'source_line': 271,
                                                            'throws': ['FederateInternalError']},
                                                        {   'group': None,
                                                            'language': 'cpp',
                                                            'params': 'InteractionClassHandle theInteraction, '
                                                                      'ParameterHandleValueMap const & '
                                                                      'theParameterValues, VariableLengthData const & '
                                                                      'theUserSuppliedTag, OrderType sentOrder, '
                                                                      'TransportationType theType, LogicalTime const & '
                                                                      'theTime, OrderType receivedOrder, '
                                                                      'MessageRetractionHandle theHandle, '
                                                                      'SupplementalReceiveInfo theReceiveInfo',
                                                            'return_type': 'void',
                                                            'service': None,
                                                            'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                            'source_line': 283,
                                                            'throws': ['FederateInternalError']}],
                              'reflectAttributeValues': [   {   'group': 'Object Management',
                                                                'language': 'java',
                                                                'params': 'ObjectInstanceHandle theObject, '
                                                                          'AttributeHandleValueMap theAttributes, '
                                                                          'byte[] userSuppliedTag, OrderType '
                                                                          'sentOrdering, TransportationTypeHandle '
                                                                          'theTransport, SupplementalReflectInfo '
                                                                          'reflectInfo',
                                                                'return_type': 'void',
                                                                'service': '6.11',
                                                                'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                'source_line': 199,
                                                                'throws': ['FederateInternalError']},
                                                            {   'group': 'Object Management',
                                                                'language': 'java',
                                                                'params': 'ObjectInstanceHandle theObject, '
                                                                          'AttributeHandleValueMap theAttributes, '
                                                                          'byte[] userSuppliedTag, OrderType '
                                                                          'sentOrdering, TransportationTypeHandle '
                                                                          'theTransport, LogicalTime theTime, '
                                                                          'OrderType receivedOrdering, '
                                                                          'SupplementalReflectInfo reflectInfo',
                                                                'return_type': 'void',
                                                                'service': '6.11',
                                                                'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                'source_line': 209,
                                                                'throws': ['FederateInternalError']},
                                                            {   'group': 'Object Management',
                                                                'language': 'java',
                                                                'params': 'ObjectInstanceHandle theObject, '
                                                                          'AttributeHandleValueMap theAttributes, '
                                                                          'byte[] userSuppliedTag, OrderType '
                                                                          'sentOrdering, TransportationTypeHandle '
                                                                          'theTransport, LogicalTime theTime, '
                                                                          'OrderType receivedOrdering, '
                                                                          'MessageRetractionHandle retractionHandle, '
                                                                          'SupplementalReflectInfo reflectInfo',
                                                                'return_type': 'void',
                                                                'service': '6.11',
                                                                'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                'source_line': 221,
                                                                'throws': ['FederateInternalError']},
                                                            {   'group': None,
                                                                'language': 'cpp',
                                                                'params': 'ObjectInstanceHandle theObject, '
                                                                          'AttributeHandleValueMap const & '
                                                                          'theAttributeValues, VariableLengthData '
                                                                          'const & theUserSuppliedTag, OrderType '
                                                                          'sentOrder, TransportationType theType, '
                                                                          'SupplementalReflectInfo theReflectInfo',
                                                                'return_type': 'void',
                                                                'service': None,
                                                                'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                'source_line': 225,
                                                                'throws': ['FederateInternalError']},
                                                            {   'group': None,
                                                                'language': 'cpp',
                                                                'params': 'ObjectInstanceHandle theObject, '
                                                                          'AttributeHandleValueMap const & '
                                                                          'theAttributeValues, VariableLengthData '
                                                                          'const & theUserSuppliedTag, OrderType '
                                                                          'sentOrder, TransportationType theType, '
                                                                          'LogicalTime const & theTime, OrderType '
                                                                          'receivedOrder, SupplementalReflectInfo '
                                                                          'theReflectInfo',
                                                                'return_type': 'void',
                                                                'service': None,
                                                                'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                'source_line': 235,
                                                                'throws': ['FederateInternalError']},
                                                            {   'group': None,
                                                                'language': 'cpp',
                                                                'params': 'ObjectInstanceHandle theObject, '
                                                                          'AttributeHandleValueMap const & '
                                                                          'theAttributeValues, VariableLengthData '
                                                                          'const & theUserSuppliedTag, OrderType '
                                                                          'sentOrder, TransportationType theType, '
                                                                          'LogicalTime const & theTime, OrderType '
                                                                          'receivedOrder, MessageRetractionHandle '
                                                                          'theHandle, SupplementalReflectInfo '
                                                                          'theReflectInfo',
                                                                'return_type': 'void',
                                                                'service': None,
                                                                'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                'source_line': 247,
                                                                'throws': ['FederateInternalError']}],
                              'removeObjectInstance': [   {   'group': 'Object Management',
                                                              'language': 'java',
                                                              'params': 'ObjectInstanceHandle theObject, byte[] '
                                                                        'userSuppliedTag, OrderType sentOrdering, '
                                                                        'SupplementalRemoveInfo removeInfo',
                                                              'return_type': 'void',
                                                              'service': '6.15',
                                                              'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                              'source_line': 285,
                                                              'throws': ['FederateInternalError']},
                                                          {   'group': 'Object Management',
                                                              'language': 'java',
                                                              'params': 'ObjectInstanceHandle theObject, byte[] '
                                                                        'userSuppliedTag, OrderType sentOrdering, '
                                                                        'LogicalTime theTime, OrderType '
                                                                        'receivedOrdering, SupplementalRemoveInfo '
                                                                        'removeInfo',
                                                              'return_type': 'void',
                                                              'service': '6.15',
                                                              'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                              'source_line': 293,
                                                              'throws': ['FederateInternalError']},
                                                          {   'group': 'Object Management',
                                                              'language': 'java',
                                                              'params': 'ObjectInstanceHandle theObject, byte[] '
                                                                        'userSuppliedTag, OrderType sentOrdering, '
                                                                        'LogicalTime theTime, OrderType '
                                                                        'receivedOrdering, MessageRetractionHandle '
                                                                        'retractionHandle, SupplementalRemoveInfo '
                                                                        'removeInfo',
                                                              'return_type': 'void',
                                                              'service': '6.15',
                                                              'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                              'source_line': 303,
                                                              'throws': ['FederateInternalError']},
                                                          {   'group': None,
                                                              'language': 'cpp',
                                                              'params': 'ObjectInstanceHandle theObject, '
                                                                        'VariableLengthData const & '
                                                                        'theUserSuppliedTag, OrderType sentOrder, '
                                                                        'SupplementalRemoveInfo theRemoveInfo',
                                                              'return_type': 'void',
                                                              'service': None,
                                                              'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                              'source_line': 297,
                                                              'throws': ['FederateInternalError']},
                                                          {   'group': None,
                                                              'language': 'cpp',
                                                              'params': 'ObjectInstanceHandle theObject, '
                                                                        'VariableLengthData const & '
                                                                        'theUserSuppliedTag, OrderType sentOrder, '
                                                                        'LogicalTime const & theTime, OrderType '
                                                                        'receivedOrder, SupplementalRemoveInfo '
                                                                        'theRemoveInfo',
                                                              'return_type': 'void',
                                                              'service': None,
                                                              'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                              'source_line': 305,
                                                              'throws': ['FederateInternalError']},
                                                          {   'group': None,
                                                              'language': 'cpp',
                                                              'params': 'ObjectInstanceHandle theObject, '
                                                                        'VariableLengthData const & '
                                                                        'theUserSuppliedTag, OrderType sentOrder, '
                                                                        'LogicalTime const & theTime, OrderType '
                                                                        'receivedOrder, MessageRetractionHandle '
                                                                        'theHandle, SupplementalRemoveInfo '
                                                                        'theRemoveInfo',
                                                              'return_type': 'void',
                                                              'service': None,
                                                              'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                              'source_line': 315,
                                                              'throws': ['FederateInternalError']}],
                              'reportAttributeTransportationType': [   {   'group': 'Object Management',
                                                                           'language': 'java',
                                                                           'params': 'ObjectInstanceHandle theObject, '
                                                                                     'AttributeHandle theAttribute, '
                                                                                     'TransportationTypeHandle '
                                                                                     'theTransportation',
                                                                           'return_type': 'void',
                                                                           'service': '6.26',
                                                                           'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                           'source_line': 359,
                                                                           'throws': ['FederateInternalError']},
                                                                       {   'group': None,
                                                                           'language': 'cpp',
                                                                           'params': 'ObjectInstanceHandle theObject, '
                                                                                     'AttributeHandle theAttribute, '
                                                                                     'TransportationType '
                                                                                     'theTransportation',
                                                                           'return_type': 'void',
                                                                           'service': None,
                                                                           'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                           'source_line': 378,
                                                                           'throws': ['FederateInternalError']}],
                              'reportFederationExecutions': [   {   'group': 'Federation Management',
                                                                    'language': 'java',
                                                                    'params': 'FederationExecutionInformationSet '
                                                                              'theFederationExecutionInformationSet',
                                                                    'return_type': 'void',
                                                                    'service': '4.8',
                                                                    'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                    'source_line': 35,
                                                                    'throws': ['FederateInternalError']},
                                                                {   'group': None,
                                                                    'language': 'cpp',
                                                                    'params': 'FederationExecutionInformationVector '
                                                                              'const & '
                                                                              'theFederationExecutionInformationList',
                                                                    'return_type': 'void',
                                                                    'service': None,
                                                                    'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                    'source_line': 50,
                                                                    'throws': ['FederateInternalError']}],
                              'reportInteractionTransportationType': [   {   'group': 'Object Management',
                                                                             'language': 'java',
                                                                             'params': 'FederateHandle theFederate, '
                                                                                       'InteractionClassHandle '
                                                                                       'theInteraction, '
                                                                                       'TransportationTypeHandle '
                                                                                       'theTransportation',
                                                                             'return_type': 'void',
                                                                             'service': '6.30',
                                                                             'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                             'source_line': 372,
                                                                             'throws': ['FederateInternalError']},
                                                                         {   'group': None,
                                                                             'language': 'cpp',
                                                                             'params': 'FederateHandle federateHandle, '
                                                                                       'InteractionClassHandle '
                                                                                       'theInteraction, '
                                                                                       'TransportationType '
                                                                                       'theTransportation',
                                                                             'return_type': 'void',
                                                                             'service': None,
                                                                             'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                             'source_line': 393,
                                                                             'throws': ['FederateInternalError']}],
                              'requestAttributeOwnershipAssumption': [   {   'group': 'Ownership Management',
                                                                             'language': 'java',
                                                                             'params': 'ObjectInstanceHandle '
                                                                                       'theObject, AttributeHandleSet '
                                                                                       'offeredAttributes, byte[] '
                                                                                       'userSuppliedTag',
                                                                             'return_type': 'void',
                                                                             'service': '7.4',
                                                                             'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                             'source_line': 383,
                                                                             'throws': ['FederateInternalError']},
                                                                         {   'group': None,
                                                                             'language': 'cpp',
                                                                             'params': 'ObjectInstanceHandle '
                                                                                       'theObject, AttributeHandleSet '
                                                                                       'const & offeredAttributes, '
                                                                                       'VariableLengthData const & '
                                                                                       'theUserSuppliedTag',
                                                                             'return_type': 'void',
                                                                             'service': None,
                                                                             'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                             'source_line': 406,
                                                                             'throws': ['FederateInternalError']}],
                              'requestAttributeOwnershipRelease': [   {   'group': 'Ownership Management',
                                                                          'language': 'java',
                                                                          'params': 'ObjectInstanceHandle theObject, '
                                                                                    'AttributeHandleSet '
                                                                                    'candidateAttributes, byte[] '
                                                                                    'userSuppliedTag',
                                                                          'return_type': 'void',
                                                                          'service': '7.11',
                                                                          'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                          'source_line': 409,
                                                                          'throws': ['FederateInternalError']},
                                                                      {   'group': None,
                                                                          'language': 'cpp',
                                                                          'params': 'ObjectInstanceHandle theObject, '
                                                                                    'AttributeHandleSet const & '
                                                                                    'candidateAttributes, '
                                                                                    'VariableLengthData const & '
                                                                                    'theUserSuppliedTag',
                                                                          'return_type': 'void',
                                                                          'service': None,
                                                                          'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                          'source_line': 436,
                                                                          'throws': ['FederateInternalError']}],
                              'requestDivestitureConfirmation': [   {   'group': 'Ownership Management',
                                                                        'language': 'java',
                                                                        'params': 'ObjectInstanceHandle theObject, '
                                                                                  'AttributeHandleSet '
                                                                                  'offeredAttributes',
                                                                        'return_type': 'void',
                                                                        'service': '7.5',
                                                                        'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                        'source_line': 390,
                                                                        'throws': ['FederateInternalError']},
                                                                    {   'group': None,
                                                                        'language': 'cpp',
                                                                        'params': 'ObjectInstanceHandle theObject, '
                                                                                  'AttributeHandleSet const & '
                                                                                  'releasedAttributes',
                                                                        'return_type': 'void',
                                                                        'service': None,
                                                                        'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                        'source_line': 414,
                                                                        'throws': ['FederateInternalError']}],
                              'requestFederationRestoreFailed': [   {   'group': 'Federation Management',
                                                                        'language': 'java',
                                                                        'params': 'String label',
                                                                        'return_type': 'void',
                                                                        'service': '4.25',
                                                                        'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                        'source_line': 94,
                                                                        'throws': ['FederateInternalError']},
                                                                    {   'group': None,
                                                                        'language': 'cpp',
                                                                        'params': 'std::wstring const & label',
                                                                        'return_type': 'void',
                                                                        'service': None,
                                                                        'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                        'source_line': 118,
                                                                        'throws': ['FederateInternalError']}],
                              'requestFederationRestoreSucceeded': [   {   'group': 'Federation Management',
                                                                           'language': 'java',
                                                                           'params': 'String label',
                                                                           'return_type': 'void',
                                                                           'service': '4.25',
                                                                           'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                           'source_line': 89,
                                                                           'throws': ['FederateInternalError']},
                                                                       {   'group': None,
                                                                           'language': 'cpp',
                                                                           'params': 'std::wstring const & label',
                                                                           'return_type': 'void',
                                                                           'service': None,
                                                                           'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                           'source_line': 113,
                                                                           'throws': ['FederateInternalError']}],
                              'requestRetraction': [   {   'group': 'Time Management',
                                                           'language': 'java',
                                                           'params': 'MessageRetractionHandle theHandle',
                                                           'return_type': 'void',
                                                           'service': '8.22',
                                                           'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                           'source_line': 460,
                                                           'throws': ['FederateInternalError']},
                                                       {   'group': None,
                                                           'language': 'cpp',
                                                           'params': 'MessageRetractionHandle theHandle',
                                                           'return_type': 'void',
                                                           'service': None,
                                                           'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                           'source_line': 493,
                                                           'throws': ['FederateInternalError']}],
                              'startRegistrationForObjectClass': [   {   'group': 'Declaration Management',
                                                                         'language': 'java',
                                                                         'params': 'ObjectClassHandle theClass',
                                                                         'return_type': 'void',
                                                                         'service': '5.10',
                                                                         'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                         'source_line': 130,
                                                                         'throws': ['FederateInternalError']},
                                                                     {   'group': None,
                                                                         'language': 'cpp',
                                                                         'params': 'ObjectClassHandle theClass',
                                                                         'return_type': 'void',
                                                                         'service': None,
                                                                         'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                         'source_line': 158,
                                                                         'throws': ['FederateInternalError']}],
                              'stopRegistrationForObjectClass': [   {   'group': 'Declaration Management',
                                                                        'language': 'java',
                                                                        'params': 'ObjectClassHandle theClass',
                                                                        'return_type': 'void',
                                                                        'service': '5.11',
                                                                        'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                        'source_line': 135,
                                                                        'throws': ['FederateInternalError']},
                                                                    {   'group': None,
                                                                        'language': 'cpp',
                                                                        'params': 'ObjectClassHandle theClass',
                                                                        'return_type': 'void',
                                                                        'service': None,
                                                                        'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                        'source_line': 164,
                                                                        'throws': ['FederateInternalError']}],
                              'synchronizationPointRegistrationFailed': [   {   'group': 'Federation Management',
                                                                                'language': 'java',
                                                                                'params': 'String '
                                                                                          'synchronizationPointLabel, '
                                                                                          'SynchronizationPointFailureReason '
                                                                                          'reason',
                                                                                'return_type': 'void',
                                                                                'service': '4.12',
                                                                                'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                                'source_line': 45,
                                                                                'throws': ['FederateInternalError']},
                                                                            {   'group': None,
                                                                                'language': 'cpp',
                                                                                'params': 'std::wstring const & label, '
                                                                                          'SynchronizationPointFailureReason '
                                                                                          'reason',
                                                                                'return_type': 'void',
                                                                                'service': None,
                                                                                'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                                'source_line': 62,
                                                                                'throws': ['FederateInternalError']}],
                              'synchronizationPointRegistrationSucceeded': [   {   'group': 'Federation Management',
                                                                                   'language': 'java',
                                                                                   'params': 'String '
                                                                                             'synchronizationPointLabel',
                                                                                   'return_type': 'void',
                                                                                   'service': '4.12',
                                                                                   'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                                   'source_line': 40,
                                                                                   'throws': ['FederateInternalError']},
                                                                               {   'group': None,
                                                                                   'language': 'cpp',
                                                                                   'params': 'std::wstring const & '
                                                                                             'label',
                                                                                   'return_type': 'void',
                                                                                   'service': None,
                                                                                   'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                                   'source_line': 57,
                                                                                   'throws': [   'FederateInternalError']}],
                              'timeAdvanceGrant': [   {   'group': 'Time Management',
                                                          'language': 'java',
                                                          'params': 'LogicalTime theTime',
                                                          'return_type': 'void',
                                                          'service': '8.13',
                                                          'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                          'source_line': 455,
                                                          'throws': ['FederateInternalError']},
                                                      {   'group': None,
                                                          'language': 'cpp',
                                                          'params': 'LogicalTime const & theTime',
                                                          'return_type': 'void',
                                                          'service': None,
                                                          'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                          'source_line': 487,
                                                          'throws': ['FederateInternalError']}],
                              'timeConstrainedEnabled': [   {   'group': 'Time Management',
                                                                'language': 'java',
                                                                'params': 'LogicalTime time',
                                                                'return_type': 'void',
                                                                'service': '8.6',
                                                                'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                'source_line': 450,
                                                                'throws': ['FederateInternalError']},
                                                            {   'group': None,
                                                                'language': 'cpp',
                                                                'params': 'LogicalTime const & theFederateTime',
                                                                'return_type': 'void',
                                                                'service': None,
                                                                'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                'source_line': 481,
                                                                'throws': ['FederateInternalError']}],
                              'timeRegulationEnabled': [   {   'group': 'Time Management',
                                                               'language': 'java',
                                                               'params': 'LogicalTime time',
                                                               'return_type': 'void',
                                                               'service': '8.3',
                                                               'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                               'source_line': 445,
                                                               'throws': ['FederateInternalError']},
                                                           {   'group': None,
                                                               'language': 'cpp',
                                                               'params': 'LogicalTime const & theFederateTime',
                                                               'return_type': 'void',
                                                               'service': None,
                                                               'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                               'source_line': 475,
                                                               'throws': ['FederateInternalError']}],
                              'turnInteractionsOff': [   {   'group': 'Declaration Management',
                                                             'language': 'java',
                                                             'params': 'InteractionClassHandle theHandle',
                                                             'return_type': 'void',
                                                             'service': '5.13',
                                                             'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                             'source_line': 145,
                                                             'throws': ['FederateInternalError']},
                                                         {   'group': None,
                                                             'language': 'cpp',
                                                             'params': 'InteractionClassHandle theHandle',
                                                             'return_type': 'void',
                                                             'service': None,
                                                             'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                             'source_line': 176,
                                                             'throws': ['FederateInternalError']}],
                              'turnInteractionsOn': [   {   'group': 'Declaration Management',
                                                            'language': 'java',
                                                            'params': 'InteractionClassHandle theHandle',
                                                            'return_type': 'void',
                                                            'service': '5.12',
                                                            'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                            'source_line': 140,
                                                            'throws': ['FederateInternalError']},
                                                        {   'group': None,
                                                            'language': 'cpp',
                                                            'params': 'InteractionClassHandle theHandle',
                                                            'return_type': 'void',
                                                            'service': None,
                                                            'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                            'source_line': 170,
                                                            'throws': ['FederateInternalError']}],
                              'turnUpdatesOffForObjectInstance': [   {   'group': 'Object Management',
                                                                         'language': 'java',
                                                                         'params': 'ObjectInstanceHandle theObject, '
                                                                                   'AttributeHandleSet theAttributes',
                                                                         'return_type': 'void',
                                                                         'service': '6.22',
                                                                         'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                         'source_line': 346,
                                                                         'throws': ['FederateInternalError']},
                                                                     {   'group': None,
                                                                         'language': 'cpp',
                                                                         'params': 'ObjectInstanceHandle theObject, '
                                                                                   'AttributeHandleSet const & '
                                                                                   'theAttributes',
                                                                         'return_type': 'void',
                                                                         'service': None,
                                                                         'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                         'source_line': 363,
                                                                         'throws': ['FederateInternalError']}],
                              'turnUpdatesOnForObjectInstance': [   {   'group': 'Object Management',
                                                                        'language': 'java',
                                                                        'params': 'ObjectInstanceHandle theObject, '
                                                                                  'AttributeHandleSet theAttributes',
                                                                        'return_type': 'void',
                                                                        'service': '6.21',
                                                                        'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                        'source_line': 333,
                                                                        'throws': ['FederateInternalError']},
                                                                    {   'group': 'Object Management',
                                                                        'language': 'java',
                                                                        'params': 'ObjectInstanceHandle theObject, '
                                                                                  'AttributeHandleSet theAttributes, '
                                                                                  'String updateRateDesignator',
                                                                        'return_type': 'void',
                                                                        'service': '6.21',
                                                                        'source_file': 'apis/java/java/src/hla/rti1516e/FederateAmbassador.java',
                                                                        'source_line': 339,
                                                                        'throws': ['FederateInternalError']},
                                                                    {   'group': None,
                                                                        'language': 'cpp',
                                                                        'params': 'ObjectInstanceHandle theObject, '
                                                                                  'AttributeHandleSet const & '
                                                                                  'theAttributes',
                                                                        'return_type': 'void',
                                                                        'service': None,
                                                                        'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                        'source_line': 349,
                                                                        'throws': ['FederateInternalError']},
                                                                    {   'group': None,
                                                                        'language': 'cpp',
                                                                        'params': 'ObjectInstanceHandle theObject, '
                                                                                  'AttributeHandleSet const & '
                                                                                  'theAttributes, std::wstring const & '
                                                                                  'updateRateDesignator',
                                                                        'return_type': 'void',
                                                                        'service': None,
                                                                        'source_file': 'apis/cpp/cpp/src/RTI/FederateAmbassador.h',
                                                                        'source_line': 355,
                                                                        'throws': ['FederateInternalError']}]},
    'RTIambassador': {   'abortFederationRestore': [   {   'group': 'Federation Management',
                                                           'language': 'java',
                                                           'params': '',
                                                           'return_type': 'void',
                                                           'service': '4.30',
                                                           'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                           'source_line': 370,
                                                           'throws': [   'RestoreNotInProgress',
                                                                         'FederateNotExecutionMember',
                                                                         'NotConnected',
                                                                         'RTIinternalError']},
                                                       {   'group': None,
                                                           'language': 'cpp',
                                                           'params': '',
                                                           'return_type': 'void',
                                                           'service': None,
                                                           'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                           'source_line': 300,
                                                           'throws': [   'RestoreNotInProgress',
                                                                         'FederateNotExecutionMember',
                                                                         'NotConnected',
                                                                         'RTIinternalError']}],
                         'abortFederationSave': [   {   'group': 'Federation Management',
                                                        'language': 'java',
                                                        'params': '',
                                                        'return_type': 'void',
                                                        'service': '4.21',
                                                        'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                        'source_line': 327,
                                                        'throws': [   'SaveNotInProgress',
                                                                      'FederateNotExecutionMember',
                                                                      'NotConnected',
                                                                      'RTIinternalError']},
                                                    {   'group': None,
                                                        'language': 'cpp',
                                                        'params': '',
                                                        'return_type': 'void',
                                                        'service': None,
                                                        'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                        'source_line': 257,
                                                        'throws': [   'SaveNotInProgress',
                                                                      'FederateNotExecutionMember',
                                                                      'NotConnected',
                                                                      'RTIinternalError']}],
                         'associateRegionsForUpdates': [   {   'group': 'Data Distribution Management',
                                                               'language': 'java',
                                                               'params': 'ObjectInstanceHandle theObject, '
                                                                         'AttributeSetRegionSetPairList '
                                                                         'attributesAndRegions',
                                                               'return_type': 'void',
                                                               'service': '9.6',
                                                               'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                               'source_line': 1258,
                                                               'throws': [   'InvalidRegionContext',
                                                                             'RegionNotCreatedByThisFederate',
                                                                             'InvalidRegion',
                                                                             'AttributeNotDefined',
                                                                             'ObjectInstanceNotKnown',
                                                                             'SaveInProgress',
                                                                             'RestoreInProgress',
                                                                             'FederateNotExecutionMember',
                                                                             'NotConnected',
                                                                             'RTIinternalError']},
                                                           {   'group': None,
                                                               'language': 'cpp',
                                                               'params': 'ObjectInstanceHandle theObject, '
                                                                         'AttributeHandleSetRegionHandleSetPairVector '
                                                                         'const & '
                                                                         'theAttributeHandleSetRegionHandleSetPairVector',
                                                               'return_type': 'void',
                                                               'service': None,
                                                               'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                               'source_line': 1191,
                                                               'throws': [   'InvalidRegionContext',
                                                                             'RegionNotCreatedByThisFederate',
                                                                             'InvalidRegion',
                                                                             'AttributeNotDefined',
                                                                             'ObjectInstanceNotKnown',
                                                                             'SaveInProgress',
                                                                             'RestoreInProgress',
                                                                             'FederateNotExecutionMember',
                                                                             'NotConnected',
                                                                             'RTIinternalError']}],
                         'attributeOwnershipAcquisition': [   {   'group': 'Ownership Management',
                                                                  'language': 'java',
                                                                  'params': 'ObjectInstanceHandle theObject, '
                                                                            'AttributeHandleSet desiredAttributes, '
                                                                            'byte[] userSuppliedTag',
                                                                  'return_type': 'void',
                                                                  'service': '7.8',
                                                                  'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                  'source_line': 848,
                                                                  'throws': [   'AttributeNotPublished',
                                                                                'ObjectClassNotPublished',
                                                                                'FederateOwnsAttributes',
                                                                                'AttributeNotDefined',
                                                                                'ObjectInstanceNotKnown',
                                                                                'SaveInProgress',
                                                                                'RestoreInProgress',
                                                                                'FederateNotExecutionMember',
                                                                                'NotConnected',
                                                                                'RTIinternalError']},
                                                              {   'group': None,
                                                                  'language': 'cpp',
                                                                  'params': 'ObjectInstanceHandle theObject, '
                                                                            'AttributeHandleSet const & '
                                                                            'desiredAttributes, VariableLengthData '
                                                                            'const & theUserSuppliedTag',
                                                                  'return_type': 'void',
                                                                  'service': None,
                                                                  'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                  'source_line': 756,
                                                                  'throws': [   'AttributeNotPublished',
                                                                                'ObjectClassNotPublished',
                                                                                'FederateOwnsAttributes',
                                                                                'AttributeNotDefined',
                                                                                'ObjectInstanceNotKnown',
                                                                                'SaveInProgress',
                                                                                'RestoreInProgress',
                                                                                'FederateNotExecutionMember',
                                                                                'NotConnected',
                                                                                'RTIinternalError']}],
                         'attributeOwnershipAcquisitionIfAvailable': [   {   'group': 'Ownership Management',
                                                                             'language': 'java',
                                                                             'params': 'ObjectInstanceHandle '
                                                                                       'theObject, AttributeHandleSet '
                                                                                       'desiredAttributes',
                                                                             'return_type': 'void',
                                                                             'service': '7.9',
                                                                             'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                             'source_line': 864,
                                                                             'throws': [   'AttributeAlreadyBeingAcquired',
                                                                                           'AttributeNotPublished',
                                                                                           'ObjectClassNotPublished',
                                                                                           'FederateOwnsAttributes',
                                                                                           'AttributeNotDefined',
                                                                                           'ObjectInstanceNotKnown',
                                                                                           'SaveInProgress',
                                                                                           'RestoreInProgress',
                                                                                           'FederateNotExecutionMember',
                                                                                           'NotConnected',
                                                                                           'RTIinternalError']},
                                                                         {   'group': None,
                                                                             'language': 'cpp',
                                                                             'params': 'ObjectInstanceHandle '
                                                                                       'theObject, AttributeHandleSet '
                                                                                       'const & desiredAttributes',
                                                                             'return_type': 'void',
                                                                             'service': None,
                                                                             'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                             'source_line': 773,
                                                                             'throws': [   'AttributeAlreadyBeingAcquired',
                                                                                           'AttributeNotPublished',
                                                                                           'ObjectClassNotPublished',
                                                                                           'FederateOwnsAttributes',
                                                                                           'AttributeNotDefined',
                                                                                           'ObjectInstanceNotKnown',
                                                                                           'SaveInProgress',
                                                                                           'RestoreInProgress',
                                                                                           'FederateNotExecutionMember',
                                                                                           'NotConnected',
                                                                                           'RTIinternalError']}],
                         'attributeOwnershipDivestitureIfWanted': [   {   'group': 'Ownership Management',
                                                                          'language': 'java',
                                                                          'params': 'ObjectInstanceHandle theObject, '
                                                                                    'AttributeHandleSet theAttributes',
                                                                          'return_type': 'AttributeHandleSet',
                                                                          'service': '7.13',
                                                                          'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                          'source_line': 893,
                                                                          'throws': [   'AttributeNotOwned',
                                                                                        'AttributeNotDefined',
                                                                                        'ObjectInstanceNotKnown',
                                                                                        'SaveInProgress',
                                                                                        'RestoreInProgress',
                                                                                        'FederateNotExecutionMember',
                                                                                        'NotConnected',
                                                                                        'RTIinternalError']},
                                                                      {   'group': None,
                                                                          'language': 'cpp',
                                                                          'params': 'ObjectInstanceHandle theObject, '
                                                                                    'AttributeHandleSet const & '
                                                                                    'theAttributes, AttributeHandleSet '
                                                                                    '& theDivestedAttributes) // '
                                                                                    'filled by RTI throw ( '
                                                                                    'AttributeNotOwned, '
                                                                                    'AttributeNotDefined, '
                                                                                    'ObjectInstanceNotKnown, '
                                                                                    'SaveInProgress, '
                                                                                    'RestoreInProgress, '
                                                                                    'FederateNotExecutionMember, '
                                                                                    'NotConnected, RTIinternalError',
                                                                          'return_type': 'void',
                                                                          'service': None,
                                                                          'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                          'source_line': 804,
                                                                          'throws': []}],
                         'attributeOwnershipReleaseDenied': [   {   'group': 'Ownership Management',
                                                                    'language': 'java',
                                                                    'params': 'ObjectInstanceHandle theObject, '
                                                                              'AttributeHandleSet theAttributes',
                                                                    'return_type': 'void',
                                                                    'service': '7.12',
                                                                    'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                    'source_line': 880,
                                                                    'throws': [   'AttributeNotOwned',
                                                                                  'AttributeNotDefined',
                                                                                  'ObjectInstanceNotKnown',
                                                                                  'SaveInProgress',
                                                                                  'RestoreInProgress',
                                                                                  'FederateNotExecutionMember',
                                                                                  'NotConnected',
                                                                                  'RTIinternalError']},
                                                                {   'group': None,
                                                                    'language': 'cpp',
                                                                    'params': 'ObjectInstanceHandle theObject, '
                                                                              'AttributeHandleSet const & '
                                                                              'theAttributes',
                                                                    'return_type': 'void',
                                                                    'service': None,
                                                                    'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                    'source_line': 790,
                                                                    'throws': [   'AttributeNotOwned',
                                                                                  'AttributeNotDefined',
                                                                                  'ObjectInstanceNotKnown',
                                                                                  'SaveInProgress',
                                                                                  'RestoreInProgress',
                                                                                  'FederateNotExecutionMember',
                                                                                  'NotConnected',
                                                                                  'RTIinternalError']}],
                         'cancelAttributeOwnershipAcquisition': [   {   'group': 'Ownership Management',
                                                                        'language': 'java',
                                                                        'params': 'ObjectInstanceHandle theObject, '
                                                                                  'AttributeHandleSet theAttributes',
                                                                        'return_type': 'void',
                                                                        'service': '7.15',
                                                                        'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                        'source_line': 920,
                                                                        'throws': [   'AttributeAcquisitionWasNotRequested',
                                                                                      'AttributeAlreadyOwned',
                                                                                      'AttributeNotDefined',
                                                                                      'ObjectInstanceNotKnown',
                                                                                      'SaveInProgress',
                                                                                      'RestoreInProgress',
                                                                                      'FederateNotExecutionMember',
                                                                                      'NotConnected',
                                                                                      'RTIinternalError']},
                                                                    {   'group': None,
                                                                        'language': 'cpp',
                                                                        'params': 'ObjectInstanceHandle theObject, '
                                                                                  'AttributeHandleSet const & '
                                                                                  'theAttributes',
                                                                        'return_type': 'void',
                                                                        'service': None,
                                                                        'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                        'source_line': 834,
                                                                        'throws': [   'AttributeAcquisitionWasNotRequested',
                                                                                      'AttributeAlreadyOwned',
                                                                                      'AttributeNotDefined',
                                                                                      'ObjectInstanceNotKnown',
                                                                                      'SaveInProgress',
                                                                                      'RestoreInProgress',
                                                                                      'FederateNotExecutionMember',
                                                                                      'NotConnected',
                                                                                      'RTIinternalError']}],
                         'cancelNegotiatedAttributeOwnershipDivestiture': [   {   'group': 'Ownership Management',
                                                                                  'language': 'java',
                                                                                  'params': 'ObjectInstanceHandle '
                                                                                            'theObject, '
                                                                                            'AttributeHandleSet '
                                                                                            'theAttributes',
                                                                                  'return_type': 'void',
                                                                                  'service': '7.14',
                                                                                  'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                                  'source_line': 906,
                                                                                  'throws': [   'AttributeDivestitureWasNotRequested',
                                                                                                'AttributeNotOwned',
                                                                                                'AttributeNotDefined',
                                                                                                'ObjectInstanceNotKnown',
                                                                                                'SaveInProgress',
                                                                                                'RestoreInProgress',
                                                                                                'FederateNotExecutionMember',
                                                                                                'NotConnected',
                                                                                                'RTIinternalError']},
                                                                              {   'group': None,
                                                                                  'language': 'cpp',
                                                                                  'params': 'ObjectInstanceHandle '
                                                                                            'theObject, '
                                                                                            'AttributeHandleSet const '
                                                                                            '& theAttributes',
                                                                                  'return_type': 'void',
                                                                                  'service': None,
                                                                                  'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                                  'source_line': 819,
                                                                                  'throws': [   'AttributeDivestitureWasNotRequested',
                                                                                                'AttributeNotOwned',
                                                                                                'AttributeNotDefined',
                                                                                                'ObjectInstanceNotKnown',
                                                                                                'SaveInProgress',
                                                                                                'RestoreInProgress',
                                                                                                'FederateNotExecutionMember',
                                                                                                'NotConnected',
                                                                                                'RTIinternalError']}],
                         'changeAttributeOrderType': [   {   'group': 'Time Management',
                                                             'language': 'java',
                                                             'params': 'ObjectInstanceHandle theObject, '
                                                                       'AttributeHandleSet theAttributes, OrderType '
                                                                       'theType',
                                                             'return_type': 'void',
                                                             'service': '8.23',
                                                             'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                             'source_line': 1158,
                                                             'throws': [   'AttributeNotOwned',
                                                                           'AttributeNotDefined',
                                                                           'ObjectInstanceNotKnown',
                                                                           'SaveInProgress',
                                                                           'RestoreInProgress',
                                                                           'FederateNotExecutionMember',
                                                                           'NotConnected',
                                                                           'RTIinternalError']},
                                                         {   'group': None,
                                                             'language': 'cpp',
                                                             'params': 'ObjectInstanceHandle theObject, '
                                                                       'AttributeHandleSet const & theAttributes, '
                                                                       'OrderType theType',
                                                             'return_type': 'void',
                                                             'service': None,
                                                             'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                             'source_line': 1083,
                                                             'throws': [   'AttributeNotOwned',
                                                                           'AttributeNotDefined',
                                                                           'ObjectInstanceNotKnown',
                                                                           'SaveInProgress',
                                                                           'RestoreInProgress',
                                                                           'FederateNotExecutionMember',
                                                                           'NotConnected',
                                                                           'RTIinternalError']}],
                         'changeInteractionOrderType': [   {   'group': 'Time Management',
                                                               'language': 'java',
                                                               'params': 'InteractionClassHandle theClass, OrderType '
                                                                         'theType',
                                                               'return_type': 'void',
                                                               'service': '8.24',
                                                               'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                               'source_line': 1172,
                                                               'throws': [   'InteractionClassNotPublished',
                                                                             'InteractionClassNotDefined',
                                                                             'SaveInProgress',
                                                                             'RestoreInProgress',
                                                                             'FederateNotExecutionMember',
                                                                             'NotConnected',
                                                                             'RTIinternalError']},
                                                           {   'group': None,
                                                               'language': 'cpp',
                                                               'params': 'InteractionClassHandle theClass, OrderType '
                                                                         'theType',
                                                               'return_type': 'void',
                                                               'service': None,
                                                               'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                               'source_line': 1098,
                                                               'throws': [   'InteractionClassNotPublished',
                                                                             'InteractionClassNotDefined',
                                                                             'SaveInProgress',
                                                                             'RestoreInProgress',
                                                                             'FederateNotExecutionMember',
                                                                             'NotConnected',
                                                                             'RTIinternalError']}],
                         'commitRegionModifications': [   {   'group': 'Data Distribution Management',
                                                              'language': 'java',
                                                              'params': 'RegionHandleSet regions',
                                                              'return_type': 'void',
                                                              'service': '9.3',
                                                              'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                              'source_line': 1198,
                                                              'throws': [   'RegionNotCreatedByThisFederate',
                                                                            'InvalidRegion',
                                                                            'SaveInProgress',
                                                                            'RestoreInProgress',
                                                                            'FederateNotExecutionMember',
                                                                            'NotConnected',
                                                                            'RTIinternalError']},
                                                          {   'group': None,
                                                              'language': 'cpp',
                                                              'params': 'RegionHandleSet const & theRegionHandleSet',
                                                              'return_type': 'void',
                                                              'service': None,
                                                              'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                              'source_line': 1126,
                                                              'throws': [   'RegionNotCreatedByThisFederate',
                                                                            'InvalidRegion',
                                                                            'SaveInProgress',
                                                                            'RestoreInProgress',
                                                                            'FederateNotExecutionMember',
                                                                            'NotConnected',
                                                                            'RTIinternalError']}],
                         'confirmDivestiture': [   {   'group': 'Ownership Management',
                                                       'language': 'java',
                                                       'params': 'ObjectInstanceHandle theObject, AttributeHandleSet '
                                                                 'theAttributes, byte[] userSuppliedTag',
                                                       'return_type': 'void',
                                                       'service': '7.6',
                                                       'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                       'source_line': 832,
                                                       'throws': [   'NoAcquisitionPending',
                                                                     'AttributeDivestitureWasNotRequested',
                                                                     'AttributeNotOwned',
                                                                     'AttributeNotDefined',
                                                                     'ObjectInstanceNotKnown',
                                                                     'SaveInProgress',
                                                                     'RestoreInProgress',
                                                                     'FederateNotExecutionMember',
                                                                     'NotConnected',
                                                                     'RTIinternalError']},
                                                   {   'group': None,
                                                       'language': 'cpp',
                                                       'params': 'ObjectInstanceHandle theObject, AttributeHandleSet '
                                                                 'const & confirmedAttributes, VariableLengthData '
                                                                 'const & theUserSuppliedTag',
                                                       'return_type': 'void',
                                                       'service': None,
                                                       'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                       'source_line': 739,
                                                       'throws': [   'NoAcquisitionPending',
                                                                     'AttributeDivestitureWasNotRequested',
                                                                     'AttributeNotOwned',
                                                                     'AttributeNotDefined',
                                                                     'ObjectInstanceNotKnown',
                                                                     'SaveInProgress',
                                                                     'RestoreInProgress',
                                                                     'FederateNotExecutionMember',
                                                                     'NotConnected',
                                                                     'RTIinternalError']}],
                         'connect': [   {   'group': 'Federation Management',
                                            'language': 'java',
                                            'params': 'FederateAmbassador federateReference, CallbackModel '
                                                      'callbackModel, String localSettingsDesignator',
                                            'return_type': 'void',
                                            'service': '4.2',
                                            'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                            'source_line': 49,
                                            'throws': [   'ConnectionFailed',
                                                          'InvalidLocalSettingsDesignator',
                                                          'UnsupportedCallbackModel',
                                                          'AlreadyConnected',
                                                          'CallNotAllowedFromWithinCallback',
                                                          'RTIinternalError']},
                                        {   'group': 'Federation Management',
                                            'language': 'java',
                                            'params': 'FederateAmbassador federateReference, CallbackModel '
                                                      'callbackModel',
                                            'return_type': 'void',
                                            'service': '4.2',
                                            'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                            'source_line': 61,
                                            'throws': [   'ConnectionFailed',
                                                          'InvalidLocalSettingsDesignator',
                                                          'UnsupportedCallbackModel',
                                                          'AlreadyConnected',
                                                          'CallNotAllowedFromWithinCallback',
                                                          'RTIinternalError']},
                                        {   'group': None,
                                            'language': 'cpp',
                                            'params': 'FederateAmbassador & federateAmbassador, CallbackModel '
                                                      'theCallbackModel, std::wstring const & '
                                                      'localSettingsDesignator=L""',
                                            'return_type': 'void',
                                            'service': None,
                                            'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                            'source_line': 45,
                                            'throws': [   'ConnectionFailed',
                                                          'InvalidLocalSettingsDesignator',
                                                          'UnsupportedCallbackModel',
                                                          'AlreadyConnected',
                                                          'CallNotAllowedFromWithinCallback',
                                                          'RTIinternalError']}],
                         'createFederationExecution': [   {   'group': 'Federation Management',
                                                              'language': 'java',
                                                              'params': 'String federationExecutionName, URL[] '
                                                                        'fomModules, URL mimModule, String '
                                                                        'logicalTimeImplementationName',
                                                              'return_type': 'void',
                                                              'service': '4.5',
                                                              'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                              'source_line': 79,
                                                              'throws': [   'CouldNotCreateLogicalTimeFactory',
                                                                            'InconsistentFDD',
                                                                            'ErrorReadingFDD',
                                                                            'CouldNotOpenFDD',
                                                                            'ErrorReadingMIM',
                                                                            'CouldNotOpenMIM',
                                                                            'DesignatorIsHLAstandardMIM',
                                                                            'FederationExecutionAlreadyExists',
                                                                            'NotConnected',
                                                                            'RTIinternalError']},
                                                          {   'group': 'Federation Management',
                                                              'language': 'java',
                                                              'params': 'String federationExecutionName, URL[] '
                                                                        'fomModules, String '
                                                                        'logicalTimeImplementationName',
                                                              'return_type': 'void',
                                                              'service': '4.5',
                                                              'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                              'source_line': 96,
                                                              'throws': [   'CouldNotCreateLogicalTimeFactory',
                                                                            'InconsistentFDD',
                                                                            'ErrorReadingFDD',
                                                                            'CouldNotOpenFDD',
                                                                            'FederationExecutionAlreadyExists',
                                                                            'NotConnected',
                                                                            'RTIinternalError']},
                                                          {   'group': 'Federation Management',
                                                              'language': 'java',
                                                              'params': 'String federationExecutionName, URL[] '
                                                                        'fomModules, URL mimModule',
                                                              'return_type': 'void',
                                                              'service': '4.5',
                                                              'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                              'source_line': 109,
                                                              'throws': [   'InconsistentFDD',
                                                                            'ErrorReadingFDD',
                                                                            'CouldNotOpenFDD',
                                                                            'ErrorReadingMIM',
                                                                            'CouldNotOpenMIM',
                                                                            'DesignatorIsHLAstandardMIM',
                                                                            'FederationExecutionAlreadyExists',
                                                                            'NotConnected',
                                                                            'RTIinternalError']},
                                                          {   'group': 'Federation Management',
                                                              'language': 'java',
                                                              'params': 'String federationExecutionName, URL[] '
                                                                        'fomModules',
                                                              'return_type': 'void',
                                                              'service': '4.5',
                                                              'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                              'source_line': 124,
                                                              'throws': [   'InconsistentFDD',
                                                                            'ErrorReadingFDD',
                                                                            'CouldNotOpenFDD',
                                                                            'FederationExecutionAlreadyExists',
                                                                            'NotConnected',
                                                                            'RTIinternalError']},
                                                          {   'group': 'Federation Management',
                                                              'language': 'java',
                                                              'params': 'String federationExecutionName, URL fomModule',
                                                              'return_type': 'void',
                                                              'service': '4.5',
                                                              'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                              'source_line': 135,
                                                              'throws': [   'InconsistentFDD',
                                                                            'ErrorReadingFDD',
                                                                            'CouldNotOpenFDD',
                                                                            'FederationExecutionAlreadyExists',
                                                                            'NotConnected',
                                                                            'RTIinternalError']},
                                                          {   'group': None,
                                                              'language': 'cpp',
                                                              'params': 'std::wstring const & federationExecutionName, '
                                                                        'std::wstring const & fomModule, std::wstring '
                                                                        'const & logicalTimeImplementationName = L""',
                                                              'return_type': 'void',
                                                              'service': None,
                                                              'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                              'source_line': 65,
                                                              'throws': [   'CouldNotCreateLogicalTimeFactory',
                                                                            'InconsistentFDD',
                                                                            'ErrorReadingFDD',
                                                                            'CouldNotOpenFDD',
                                                                            'FederationExecutionAlreadyExists',
                                                                            'NotConnected',
                                                                            'RTIinternalError']},
                                                          {   'group': None,
                                                              'language': 'cpp',
                                                              'params': 'std::wstring const & federationExecutionName, '
                                                                        'std::vector<std::wstring> const & fomModules, '
                                                                        'std::wstring const & '
                                                                        'logicalTimeImplementationName = L""',
                                                              'return_type': 'void',
                                                              'service': None,
                                                              'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                              'source_line': 78,
                                                              'throws': [   'CouldNotCreateLogicalTimeFactory',
                                                                            'InconsistentFDD',
                                                                            'ErrorReadingFDD',
                                                                            'CouldNotOpenFDD',
                                                                            'FederationExecutionAlreadyExists',
                                                                            'NotConnected',
                                                                            'RTIinternalError']}],
                         'createFederationExecutionWithMIM': [   {   'group': None,
                                                                     'language': 'cpp',
                                                                     'params': 'std::wstring const & '
                                                                               'federationExecutionName, '
                                                                               'std::vector<std::wstring> const & '
                                                                               'fomModules, std::wstring const & '
                                                                               'mimModule, std::wstring const & '
                                                                               'logicalTimeImplementationName = L""',
                                                                     'return_type': 'void',
                                                                     'service': None,
                                                                     'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                     'source_line': 91,
                                                                     'throws': [   'CouldNotCreateLogicalTimeFactory',
                                                                                   'InconsistentFDD',
                                                                                   'ErrorReadingFDD',
                                                                                   'CouldNotOpenFDD',
                                                                                   'DesignatorIsHLAstandardMIM',
                                                                                   'ErrorReadingMIM',
                                                                                   'CouldNotOpenMIM',
                                                                                   'FederationExecutionAlreadyExists',
                                                                                   'NotConnected',
                                                                                   'RTIinternalError']}],
                         'createRegion': [   {   'group': 'Data Distribution Management',
                                                 'language': 'java',
                                                 'params': 'DimensionHandleSet dimensions',
                                                 'return_type': 'RegionHandle',
                                                 'service': '9.2',
                                                 'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                 'source_line': 1188,
                                                 'throws': [   'InvalidDimensionHandle',
                                                               'SaveInProgress',
                                                               'RestoreInProgress',
                                                               'FederateNotExecutionMember',
                                                               'NotConnected',
                                                               'RTIinternalError']},
                                             {   'group': None,
                                                 'language': 'cpp',
                                                 'params': 'DimensionHandleSet const & theDimensions',
                                                 'return_type': 'RegionHandle',
                                                 'service': None,
                                                 'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                 'source_line': 1115,
                                                 'throws': [   'InvalidDimensionHandle',
                                                               'SaveInProgress',
                                                               'RestoreInProgress',
                                                               'FederateNotExecutionMember',
                                                               'NotConnected',
                                                               'RTIinternalError']}],
                         'decodeAttributeHandle': [   {   'group': None,
                                                          'language': 'cpp',
                                                          'params': 'VariableLengthData const & encodedValue) const '
                                                                    'throw ( CouldNotDecode, '
                                                                    'FederateNotExecutionMember, NotConnected, '
                                                                    'RTIinternalError',
                                                          'return_type': 'AttributeHandle',
                                                          'service': None,
                                                          'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                          'source_line': 1808,
                                                          'throws': []}],
                         'decodeDimensionHandle': [   {   'group': None,
                                                          'language': 'cpp',
                                                          'params': 'VariableLengthData const & encodedValue) const '
                                                                    'throw ( CouldNotDecode, '
                                                                    'FederateNotExecutionMember, NotConnected, '
                                                                    'RTIinternalError',
                                                          'return_type': 'DimensionHandle',
                                                          'service': None,
                                                          'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                          'source_line': 1824,
                                                          'throws': []}],
                         'decodeFederateHandle': [   {   'group': None,
                                                         'language': 'cpp',
                                                         'params': 'VariableLengthData const & encodedValue) const '
                                                                   'throw ( CouldNotDecode, '
                                                                   'FederateNotExecutionMember, NotConnected, '
                                                                   'RTIinternalError',
                                                         'return_type': 'FederateHandle',
                                                         'service': None,
                                                         'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                         'source_line': 1776,
                                                         'throws': []}],
                         'decodeInteractionClassHandle': [   {   'group': None,
                                                                 'language': 'cpp',
                                                                 'params': 'VariableLengthData const & encodedValue) '
                                                                           'const throw ( CouldNotDecode, '
                                                                           'FederateNotExecutionMember, NotConnected, '
                                                                           'RTIinternalError',
                                                                 'return_type': 'InteractionClassHandle',
                                                                 'service': None,
                                                                 'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                 'source_line': 1792,
                                                                 'throws': []}],
                         'decodeMessageRetractionHandle': [   {   'group': None,
                                                                  'language': 'cpp',
                                                                  'params': 'VariableLengthData const & encodedValue) '
                                                                            'const throw ( CouldNotDecode, '
                                                                            'FederateNotExecutionMember, NotConnected, '
                                                                            'RTIinternalError',
                                                                  'return_type': 'MessageRetractionHandle',
                                                                  'service': None,
                                                                  'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                  'source_line': 1832,
                                                                  'throws': []}],
                         'decodeObjectClassHandle': [   {   'group': None,
                                                            'language': 'cpp',
                                                            'params': 'VariableLengthData const & encodedValue) const '
                                                                      'throw ( CouldNotDecode, '
                                                                      'FederateNotExecutionMember, NotConnected, '
                                                                      'RTIinternalError',
                                                            'return_type': 'ObjectClassHandle',
                                                            'service': None,
                                                            'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                            'source_line': 1784,
                                                            'throws': []}],
                         'decodeObjectInstanceHandle': [   {   'group': None,
                                                               'language': 'cpp',
                                                               'params': 'VariableLengthData const & encodedValue) '
                                                                         'const throw ( CouldNotDecode, '
                                                                         'FederateNotExecutionMember, NotConnected, '
                                                                         'RTIinternalError',
                                                               'return_type': 'ObjectInstanceHandle',
                                                               'service': None,
                                                               'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                               'source_line': 1800,
                                                               'throws': []}],
                         'decodeParameterHandle': [   {   'group': None,
                                                          'language': 'cpp',
                                                          'params': 'VariableLengthData const & encodedValue) const '
                                                                    'throw ( CouldNotDecode, '
                                                                    'FederateNotExecutionMember, NotConnected, '
                                                                    'RTIinternalError',
                                                          'return_type': 'ParameterHandle',
                                                          'service': None,
                                                          'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                          'source_line': 1816,
                                                          'throws': []}],
                         'decodeRegionHandle': [   {   'group': None,
                                                       'language': 'cpp',
                                                       'params': 'VariableLengthData const & encodedValue) const throw '
                                                                 '( CouldNotDecode, FederateNotExecutionMember, '
                                                                 'NotConnected, RTIinternalError',
                                                       'return_type': 'RegionHandle',
                                                       'service': None,
                                                       'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                       'source_line': 1840,
                                                       'throws': []}],
                         'deleteObjectInstance': [   {   'group': 'Object Management',
                                                         'language': 'java',
                                                         'params': 'ObjectInstanceHandle objectHandle, byte[] '
                                                                   'userSuppliedTag',
                                                         'return_type': 'void',
                                                         'service': '6.14',
                                                         'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                         'source_line': 683,
                                                         'throws': [   'DeletePrivilegeNotHeld',
                                                                       'ObjectInstanceNotKnown',
                                                                       'SaveInProgress',
                                                                       'RestoreInProgress',
                                                                       'FederateNotExecutionMember',
                                                                       'NotConnected',
                                                                       'RTIinternalError']},
                                                     {   'group': 'Object Management',
                                                         'language': 'java',
                                                         'params': 'ObjectInstanceHandle objectHandle, byte[] '
                                                                   'userSuppliedTag, LogicalTime theTime',
                                                         'return_type': 'MessageRetractionReturn',
                                                         'service': '6.14',
                                                         'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                         'source_line': 695,
                                                         'throws': [   'InvalidLogicalTime',
                                                                       'DeletePrivilegeNotHeld',
                                                                       'ObjectInstanceNotKnown',
                                                                       'SaveInProgress',
                                                                       'RestoreInProgress',
                                                                       'FederateNotExecutionMember',
                                                                       'NotConnected',
                                                                       'RTIinternalError']},
                                                     {   'group': None,
                                                         'language': 'cpp',
                                                         'params': 'ObjectInstanceHandle theObject, VariableLengthData '
                                                                   'const & theUserSuppliedTag',
                                                         'return_type': 'void',
                                                         'service': None,
                                                         'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                         'source_line': 580,
                                                         'throws': [   'DeletePrivilegeNotHeld',
                                                                       'ObjectInstanceNotKnown',
                                                                       'SaveInProgress',
                                                                       'RestoreInProgress',
                                                                       'FederateNotExecutionMember',
                                                                       'NotConnected',
                                                                       'RTIinternalError']},
                                                     {   'group': None,
                                                         'language': 'cpp',
                                                         'params': 'ObjectInstanceHandle theObject, VariableLengthData '
                                                                   'const & theUserSuppliedTag, LogicalTime const & '
                                                                   'theTime',
                                                         'return_type': 'MessageRetractionHandle',
                                                         'service': None,
                                                         'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                         'source_line': 592,
                                                         'throws': [   'InvalidLogicalTime',
                                                                       'DeletePrivilegeNotHeld',
                                                                       'ObjectInstanceNotKnown',
                                                                       'SaveInProgress',
                                                                       'RestoreInProgress',
                                                                       'FederateNotExecutionMember',
                                                                       'NotConnected',
                                                                       'RTIinternalError']}],
                         'deleteRegion': [   {   'group': 'Data Distribution Management',
                                                 'language': 'java',
                                                 'params': 'RegionHandle theRegion',
                                                 'return_type': 'void',
                                                 'service': '9.4',
                                                 'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                 'source_line': 1209,
                                                 'throws': [   'RegionInUseForUpdateOrSubscription',
                                                               'RegionNotCreatedByThisFederate',
                                                               'InvalidRegion',
                                                               'SaveInProgress',
                                                               'RestoreInProgress',
                                                               'FederateNotExecutionMember',
                                                               'NotConnected',
                                                               'RTIinternalError']},
                                             {   'group': None,
                                                 'language': 'cpp',
                                                 'params': 'RegionHandle const & theRegion',
                                                 'return_type': 'void',
                                                 'service': None,
                                                 'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                 'source_line': 1138,
                                                 'throws': [   'RegionInUseForUpdateOrSubscription',
                                                               'RegionNotCreatedByThisFederate',
                                                               'InvalidRegion',
                                                               'SaveInProgress',
                                                               'RestoreInProgress',
                                                               'FederateNotExecutionMember',
                                                               'NotConnected',
                                                               'RTIinternalError']}],
                         'destroyFederationExecution': [   {   'group': 'Federation Management',
                                                               'language': 'java',
                                                               'params': 'String federationExecutionName',
                                                               'return_type': 'void',
                                                               'service': '4.6',
                                                               'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                               'source_line': 146,
                                                               'throws': [   'FederatesCurrentlyJoined',
                                                                             'FederationExecutionDoesNotExist',
                                                                             'NotConnected',
                                                                             'RTIinternalError']},
                                                           {   'group': None,
                                                               'language': 'cpp',
                                                               'params': 'std::wstring const & federationExecutionName',
                                                               'return_type': 'void',
                                                               'service': None,
                                                               'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                               'source_line': 109,
                                                               'throws': [   'FederatesCurrentlyJoined',
                                                                             'FederationExecutionDoesNotExist',
                                                                             'NotConnected',
                                                                             'RTIinternalError']}],
                         'disableAsynchronousDelivery': [   {   'group': 'Time Management',
                                                                'language': 'java',
                                                                'params': '',
                                                                'return_type': 'void',
                                                                'service': '8.15',
                                                                'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                'source_line': 1087,
                                                                'throws': [   'AsynchronousDeliveryAlreadyDisabled',
                                                                              'SaveInProgress',
                                                                              'RestoreInProgress',
                                                                              'FederateNotExecutionMember',
                                                                              'NotConnected',
                                                                              'RTIinternalError']},
                                                            {   'group': None,
                                                                'language': 'cpp',
                                                                'params': '',
                                                                'return_type': 'void',
                                                                'service': None,
                                                                'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                'source_line': 1010,
                                                                'throws': [   'AsynchronousDeliveryAlreadyDisabled',
                                                                              'SaveInProgress',
                                                                              'RestoreInProgress',
                                                                              'FederateNotExecutionMember',
                                                                              'NotConnected',
                                                                              'RTIinternalError']}],
                         'disableAttributeRelevanceAdvisorySwitch': [   {   'group': 'Support Services',
                                                                            'language': 'java',
                                                                            'params': '',
                                                                            'return_type': 'void',
                                                                            'service': '10.36',
                                                                            'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                            'source_line': 1772,
                                                                            'throws': [   'AttributeRelevanceAdvisorySwitchIsOff',
                                                                                          'SaveInProgress',
                                                                                          'RestoreInProgress',
                                                                                          'FederateNotExecutionMember',
                                                                                          'NotConnected',
                                                                                          'RTIinternalError']},
                                                                        {   'group': None,
                                                                            'language': 'cpp',
                                                                            'params': '',
                                                                            'return_type': 'void',
                                                                            'service': None,
                                                                            'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                            'source_line': 1688,
                                                                            'throws': [   'AttributeRelevanceAdvisorySwitchIsOff',
                                                                                          'SaveInProgress',
                                                                                          'RestoreInProgress',
                                                                                          'FederateNotExecutionMember',
                                                                                          'NotConnected',
                                                                                          'RTIinternalError']}],
                         'disableAttributeScopeAdvisorySwitch': [   {   'group': 'Support Services',
                                                                        'language': 'java',
                                                                        'params': '',
                                                                        'return_type': 'void',
                                                                        'service': '10.38',
                                                                        'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                        'source_line': 1792,
                                                                        'throws': [   'AttributeScopeAdvisorySwitchIsOff',
                                                                                      'SaveInProgress',
                                                                                      'RestoreInProgress',
                                                                                      'FederateNotExecutionMember',
                                                                                      'NotConnected',
                                                                                      'RTIinternalError']},
                                                                    {   'group': None,
                                                                        'language': 'cpp',
                                                                        'params': '',
                                                                        'return_type': 'void',
                                                                        'service': None,
                                                                        'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                        'source_line': 1708,
                                                                        'throws': [   'AttributeScopeAdvisorySwitchIsOff',
                                                                                      'SaveInProgress',
                                                                                      'RestoreInProgress',
                                                                                      'FederateNotExecutionMember',
                                                                                      'NotConnected',
                                                                                      'RTIinternalError']}],
                         'disableCallbacks': [   {   'group': 'Support Services',
                                                     'language': 'java',
                                                     'params': '',
                                                     'return_type': 'void',
                                                     'service': '10.44',
                                                     'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                     'source_line': 1842,
                                                     'throws': [   'SaveInProgress',
                                                                   'RestoreInProgress',
                                                                   'RTIinternalError']},
                                                 {   'group': None,
                                                     'language': 'cpp',
                                                     'params': '',
                                                     'return_type': 'void',
                                                     'service': None,
                                                     'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                     'source_line': 1760,
                                                     'throws': [   'SaveInProgress',
                                                                   'RestoreInProgress',
                                                                   'RTIinternalError']}],
                         'disableInteractionRelevanceAdvisorySwitch': [   {   'group': 'Support Services',
                                                                              'language': 'java',
                                                                              'params': '',
                                                                              'return_type': 'void',
                                                                              'service': '10.40',
                                                                              'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                              'source_line': 1812,
                                                                              'throws': [   'InteractionRelevanceAdvisorySwitchIsOff',
                                                                                            'SaveInProgress',
                                                                                            'RestoreInProgress',
                                                                                            'FederateNotExecutionMember',
                                                                                            'NotConnected',
                                                                                            'RTIinternalError']},
                                                                          {   'group': None,
                                                                              'language': 'cpp',
                                                                              'params': '',
                                                                              'return_type': 'void',
                                                                              'service': None,
                                                                              'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                              'source_line': 1728,
                                                                              'throws': [   'InteractionRelevanceAdvisorySwitchIsOff',
                                                                                            'SaveInProgress',
                                                                                            'RestoreInProgress',
                                                                                            'FederateNotExecutionMember',
                                                                                            'NotConnected',
                                                                                            'RTIinternalError']}],
                         'disableObjectClassRelevanceAdvisorySwitch': [   {   'group': 'Support Services',
                                                                              'language': 'java',
                                                                              'params': '',
                                                                              'return_type': 'void',
                                                                              'service': '10.34',
                                                                              'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                              'source_line': 1752,
                                                                              'throws': [   'ObjectClassRelevanceAdvisorySwitchIsOff',
                                                                                            'SaveInProgress',
                                                                                            'RestoreInProgress',
                                                                                            'FederateNotExecutionMember',
                                                                                            'NotConnected',
                                                                                            'RTIinternalError']},
                                                                          {   'group': None,
                                                                              'language': 'cpp',
                                                                              'params': '',
                                                                              'return_type': 'void',
                                                                              'service': None,
                                                                              'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                              'source_line': 1668,
                                                                              'throws': [   'ObjectClassRelevanceAdvisorySwitchIsOff',
                                                                                            'SaveInProgress',
                                                                                            'RestoreInProgress',
                                                                                            'FederateNotExecutionMember',
                                                                                            'NotConnected',
                                                                                            'RTIinternalError']}],
                         'disableTimeConstrained': [   {   'group': 'Time Management',
                                                           'language': 'java',
                                                           'params': '',
                                                           'return_type': 'void',
                                                           'service': '8.7',
                                                           'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                           'source_line': 997,
                                                           'throws': [   'TimeConstrainedIsNotEnabled',
                                                                         'SaveInProgress',
                                                                         'RestoreInProgress',
                                                                         'FederateNotExecutionMember',
                                                                         'NotConnected',
                                                                         'RTIinternalError']},
                                                       {   'group': None,
                                                           'language': 'cpp',
                                                           'params': '',
                                                           'return_type': 'void',
                                                           'service': None,
                                                           'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                           'source_line': 915,
                                                           'throws': [   'TimeConstrainedIsNotEnabled',
                                                                         'SaveInProgress',
                                                                         'RestoreInProgress',
                                                                         'FederateNotExecutionMember',
                                                                         'NotConnected',
                                                                         'RTIinternalError']}],
                         'disableTimeRegulation': [   {   'group': 'Time Management',
                                                          'language': 'java',
                                                          'params': '',
                                                          'return_type': 'void',
                                                          'service': '8.4',
                                                          'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                          'source_line': 975,
                                                          'throws': [   'TimeRegulationIsNotEnabled',
                                                                        'SaveInProgress',
                                                                        'RestoreInProgress',
                                                                        'FederateNotExecutionMember',
                                                                        'NotConnected',
                                                                        'RTIinternalError']},
                                                      {   'group': None,
                                                          'language': 'cpp',
                                                          'params': '',
                                                          'return_type': 'void',
                                                          'service': None,
                                                          'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                          'source_line': 893,
                                                          'throws': [   'TimeRegulationIsNotEnabled',
                                                                        'SaveInProgress',
                                                                        'RestoreInProgress',
                                                                        'FederateNotExecutionMember',
                                                                        'NotConnected',
                                                                        'RTIinternalError']}],
                         'disconnect': [   {   'group': 'Federation Management',
                                               'language': 'java',
                                               'params': '',
                                               'return_type': 'void',
                                               'service': '4.3',
                                               'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                               'source_line': 72,
                                               'throws': [   'FederateIsExecutionMember',
                                                             'CallNotAllowedFromWithinCallback',
                                                             'RTIinternalError']},
                                           {   'group': None,
                                               'language': 'cpp',
                                               'params': '',
                                               'return_type': 'void',
                                               'service': None,
                                               'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                               'source_line': 58,
                                               'throws': [   'FederateIsExecutionMember',
                                                             'CallNotAllowedFromWithinCallback',
                                                             'RTIinternalError']}],
                         'enableAsynchronousDelivery': [   {   'group': 'Time Management',
                                                               'language': 'java',
                                                               'params': '',
                                                               'return_type': 'void',
                                                               'service': '8.14',
                                                               'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                               'source_line': 1077,
                                                               'throws': [   'AsynchronousDeliveryAlreadyEnabled',
                                                                             'SaveInProgress',
                                                                             'RestoreInProgress',
                                                                             'FederateNotExecutionMember',
                                                                             'NotConnected',
                                                                             'RTIinternalError']},
                                                           {   'group': None,
                                                               'language': 'cpp',
                                                               'params': '',
                                                               'return_type': 'void',
                                                               'service': None,
                                                               'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                               'source_line': 1000,
                                                               'throws': [   'AsynchronousDeliveryAlreadyEnabled',
                                                                             'SaveInProgress',
                                                                             'RestoreInProgress',
                                                                             'FederateNotExecutionMember',
                                                                             'NotConnected',
                                                                             'RTIinternalError']}],
                         'enableAttributeRelevanceAdvisorySwitch': [   {   'group': 'Support Services',
                                                                           'language': 'java',
                                                                           'params': '',
                                                                           'return_type': 'void',
                                                                           'service': '10.35',
                                                                           'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                           'source_line': 1762,
                                                                           'throws': [   'AttributeRelevanceAdvisorySwitchIsOn',
                                                                                         'SaveInProgress',
                                                                                         'RestoreInProgress',
                                                                                         'FederateNotExecutionMember',
                                                                                         'NotConnected',
                                                                                         'RTIinternalError']},
                                                                       {   'group': None,
                                                                           'language': 'cpp',
                                                                           'params': '',
                                                                           'return_type': 'void',
                                                                           'service': None,
                                                                           'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                           'source_line': 1678,
                                                                           'throws': [   'AttributeRelevanceAdvisorySwitchIsOn',
                                                                                         'SaveInProgress',
                                                                                         'RestoreInProgress',
                                                                                         'FederateNotExecutionMember',
                                                                                         'NotConnected',
                                                                                         'RTIinternalError']}],
                         'enableAttributeScopeAdvisorySwitch': [   {   'group': 'Support Services',
                                                                       'language': 'java',
                                                                       'params': '',
                                                                       'return_type': 'void',
                                                                       'service': '10.37',
                                                                       'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                       'source_line': 1782,
                                                                       'throws': [   'AttributeScopeAdvisorySwitchIsOn',
                                                                                     'SaveInProgress',
                                                                                     'RestoreInProgress',
                                                                                     'FederateNotExecutionMember',
                                                                                     'NotConnected',
                                                                                     'RTIinternalError']},
                                                                   {   'group': None,
                                                                       'language': 'cpp',
                                                                       'params': '',
                                                                       'return_type': 'void',
                                                                       'service': None,
                                                                       'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                       'source_line': 1698,
                                                                       'throws': [   'AttributeScopeAdvisorySwitchIsOn',
                                                                                     'SaveInProgress',
                                                                                     'RestoreInProgress',
                                                                                     'FederateNotExecutionMember',
                                                                                     'NotConnected',
                                                                                     'RTIinternalError']}],
                         'enableCallbacks': [   {   'group': 'Support Services',
                                                    'language': 'java',
                                                    'params': '',
                                                    'return_type': 'void',
                                                    'service': '10.43',
                                                    'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                    'source_line': 1835,
                                                    'throws': [   'SaveInProgress',
                                                                  'RestoreInProgress',
                                                                  'RTIinternalError']},
                                                {   'group': None,
                                                    'language': 'cpp',
                                                    'params': '',
                                                    'return_type': 'void',
                                                    'service': None,
                                                    'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                    'source_line': 1753,
                                                    'throws': [   'SaveInProgress',
                                                                  'RestoreInProgress',
                                                                  'RTIinternalError']}],
                         'enableInteractionRelevanceAdvisorySwitch': [   {   'group': 'Support Services',
                                                                             'language': 'java',
                                                                             'params': '',
                                                                             'return_type': 'void',
                                                                             'service': '10.39',
                                                                             'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                             'source_line': 1802,
                                                                             'throws': [   'InteractionRelevanceAdvisorySwitchIsOn',
                                                                                           'SaveInProgress',
                                                                                           'RestoreInProgress',
                                                                                           'FederateNotExecutionMember',
                                                                                           'NotConnected',
                                                                                           'RTIinternalError']},
                                                                         {   'group': None,
                                                                             'language': 'cpp',
                                                                             'params': '',
                                                                             'return_type': 'void',
                                                                             'service': None,
                                                                             'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                             'source_line': 1718,
                                                                             'throws': [   'InteractionRelevanceAdvisorySwitchIsOn',
                                                                                           'SaveInProgress',
                                                                                           'RestoreInProgress',
                                                                                           'FederateNotExecutionMember',
                                                                                           'NotConnected',
                                                                                           'RTIinternalError']}],
                         'enableObjectClassRelevanceAdvisorySwitch': [   {   'group': 'Support Services',
                                                                             'language': 'java',
                                                                             'params': '',
                                                                             'return_type': 'void',
                                                                             'service': '10.33',
                                                                             'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                             'source_line': 1742,
                                                                             'throws': [   'ObjectClassRelevanceAdvisorySwitchIsOn',
                                                                                           'SaveInProgress',
                                                                                           'RestoreInProgress',
                                                                                           'FederateNotExecutionMember',
                                                                                           'NotConnected',
                                                                                           'RTIinternalError']},
                                                                         {   'group': None,
                                                                             'language': 'cpp',
                                                                             'params': '',
                                                                             'return_type': 'void',
                                                                             'service': None,
                                                                             'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                             'source_line': 1658,
                                                                             'throws': [   'ObjectClassRelevanceAdvisorySwitchIsOn',
                                                                                           'SaveInProgress',
                                                                                           'RestoreInProgress',
                                                                                           'FederateNotExecutionMember',
                                                                                           'NotConnected',
                                                                                           'RTIinternalError']}],
                         'enableTimeConstrained': [   {   'group': 'Time Management',
                                                          'language': 'java',
                                                          'params': '',
                                                          'return_type': 'void',
                                                          'service': '8.5',
                                                          'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                          'source_line': 985,
                                                          'throws': [   'InTimeAdvancingState',
                                                                        'RequestForTimeConstrainedPending',
                                                                        'TimeConstrainedAlreadyEnabled',
                                                                        'SaveInProgress',
                                                                        'RestoreInProgress',
                                                                        'FederateNotExecutionMember',
                                                                        'NotConnected',
                                                                        'RTIinternalError']},
                                                      {   'group': None,
                                                          'language': 'cpp',
                                                          'params': '',
                                                          'return_type': 'void',
                                                          'service': None,
                                                          'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                          'source_line': 903,
                                                          'throws': [   'InTimeAdvancingState',
                                                                        'RequestForTimeConstrainedPending',
                                                                        'TimeConstrainedAlreadyEnabled',
                                                                        'SaveInProgress',
                                                                        'RestoreInProgress',
                                                                        'FederateNotExecutionMember',
                                                                        'NotConnected',
                                                                        'RTIinternalError']}],
                         'enableTimeRegulation': [   {   'group': 'Time Management',
                                                         'language': 'java',
                                                         'params': 'LogicalTimeInterval theLookahead',
                                                         'return_type': 'void',
                                                         'service': '8.2',
                                                         'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                         'source_line': 962,
                                                         'throws': [   'InvalidLookahead',
                                                                       'InTimeAdvancingState',
                                                                       'RequestForTimeRegulationPending',
                                                                       'TimeRegulationAlreadyEnabled',
                                                                       'SaveInProgress',
                                                                       'RestoreInProgress',
                                                                       'FederateNotExecutionMember',
                                                                       'NotConnected',
                                                                       'RTIinternalError']},
                                                     {   'group': None,
                                                         'language': 'cpp',
                                                         'params': 'LogicalTimeInterval const & theLookahead',
                                                         'return_type': 'void',
                                                         'service': None,
                                                         'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                         'source_line': 879,
                                                         'throws': [   'InvalidLookahead',
                                                                       'InTimeAdvancingState',
                                                                       'RequestForTimeRegulationPending',
                                                                       'TimeRegulationAlreadyEnabled',
                                                                       'SaveInProgress',
                                                                       'RestoreInProgress',
                                                                       'FederateNotExecutionMember',
                                                                       'NotConnected',
                                                                       'RTIinternalError']}],
                         'evokeCallback': [   {   'group': 'Support Services',
                                                  'language': 'java',
                                                  'params': 'double approximateMinimumTimeInSeconds',
                                                  'return_type': 'boolean',
                                                  'service': '10.41',
                                                  'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                  'source_line': 1822,
                                                  'throws': ['CallNotAllowedFromWithinCallback', 'RTIinternalError']},
                                              {   'group': None,
                                                  'language': 'cpp',
                                                  'params': 'double approximateMinimumTimeInSeconds',
                                                  'return_type': 'bool',
                                                  'service': None,
                                                  'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                  'source_line': 1738,
                                                  'throws': ['CallNotAllowedFromWithinCallback', 'RTIinternalError']}],
                         'evokeMultipleCallbacks': [   {   'group': 'Support Services',
                                                           'language': 'java',
                                                           'params': 'double approximateMinimumTimeInSeconds, double '
                                                                     'approximateMaximumTimeInSeconds',
                                                           'return_type': 'boolean',
                                                           'service': '10.42',
                                                           'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                           'source_line': 1828,
                                                           'throws': [   'CallNotAllowedFromWithinCallback',
                                                                         'RTIinternalError']},
                                                       {   'group': None,
                                                           'language': 'cpp',
                                                           'params': 'double approximateMinimumTimeInSeconds, double '
                                                                     'approximateMaximumTimeInSeconds',
                                                           'return_type': 'bool',
                                                           'service': None,
                                                           'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                           'source_line': 1745,
                                                           'throws': [   'CallNotAllowedFromWithinCallback',
                                                                         'RTIinternalError']}],
                         'federateRestoreComplete': [   {   'group': 'Federation Management',
                                                            'language': 'java',
                                                            'params': '',
                                                            'return_type': 'void',
                                                            'service': '4.28',
                                                            'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                            'source_line': 352,
                                                            'throws': [   'RestoreNotRequested',
                                                                          'SaveInProgress',
                                                                          'FederateNotExecutionMember',
                                                                          'NotConnected',
                                                                          'RTIinternalError']},
                                                        {   'group': None,
                                                            'language': 'cpp',
                                                            'params': '',
                                                            'return_type': 'void',
                                                            'service': None,
                                                            'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                            'source_line': 283,
                                                            'throws': [   'RestoreNotRequested',
                                                                          'SaveInProgress',
                                                                          'FederateNotExecutionMember',
                                                                          'NotConnected',
                                                                          'RTIinternalError']}],
                         'federateRestoreNotComplete': [   {   'group': 'Federation Management',
                                                               'language': 'java',
                                                               'params': '',
                                                               'return_type': 'void',
                                                               'service': '4.28',
                                                               'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                               'source_line': 361,
                                                               'throws': [   'RestoreNotRequested',
                                                                             'SaveInProgress',
                                                                             'FederateNotExecutionMember',
                                                                             'NotConnected',
                                                                             'RTIinternalError']},
                                                           {   'group': None,
                                                               'language': 'cpp',
                                                               'params': '',
                                                               'return_type': 'void',
                                                               'service': None,
                                                               'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                               'source_line': 291,
                                                               'throws': [   'RestoreNotRequested',
                                                                             'SaveInProgress',
                                                                             'FederateNotExecutionMember',
                                                                             'NotConnected',
                                                                             'RTIinternalError']}],
                         'federateSaveBegun': [   {   'group': 'Federation Management',
                                                      'language': 'java',
                                                      'params': '',
                                                      'return_type': 'void',
                                                      'service': '4.18',
                                                      'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                      'source_line': 300,
                                                      'throws': [   'SaveNotInitiated',
                                                                    'RestoreInProgress',
                                                                    'FederateNotExecutionMember',
                                                                    'NotConnected',
                                                                    'RTIinternalError']},
                                                  {   'group': None,
                                                      'language': 'cpp',
                                                      'params': '',
                                                      'return_type': 'void',
                                                      'service': None,
                                                      'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                      'source_line': 231,
                                                      'throws': [   'SaveNotInitiated',
                                                                    'RestoreInProgress',
                                                                    'FederateNotExecutionMember',
                                                                    'NotConnected',
                                                                    'RTIinternalError']}],
                         'federateSaveComplete': [   {   'group': 'Federation Management',
                                                         'language': 'java',
                                                         'params': '',
                                                         'return_type': 'void',
                                                         'service': '4.19',
                                                         'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                         'source_line': 309,
                                                         'throws': [   'FederateHasNotBegunSave',
                                                                       'RestoreInProgress',
                                                                       'FederateNotExecutionMember',
                                                                       'NotConnected',
                                                                       'RTIinternalError']},
                                                     {   'group': None,
                                                         'language': 'cpp',
                                                         'params': '',
                                                         'return_type': 'void',
                                                         'service': None,
                                                         'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                         'source_line': 240,
                                                         'throws': [   'FederateHasNotBegunSave',
                                                                       'RestoreInProgress',
                                                                       'FederateNotExecutionMember',
                                                                       'NotConnected',
                                                                       'RTIinternalError']}],
                         'federateSaveNotComplete': [   {   'group': 'Federation Management',
                                                            'language': 'java',
                                                            'params': '',
                                                            'return_type': 'void',
                                                            'service': '4.19',
                                                            'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                            'source_line': 318,
                                                            'throws': [   'FederateHasNotBegunSave',
                                                                          'RestoreInProgress',
                                                                          'FederateNotExecutionMember',
                                                                          'NotConnected',
                                                                          'RTIinternalError']},
                                                        {   'group': None,
                                                            'language': 'cpp',
                                                            'params': '',
                                                            'return_type': 'void',
                                                            'service': None,
                                                            'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                            'source_line': 248,
                                                            'throws': [   'FederateHasNotBegunSave',
                                                                          'RestoreInProgress',
                                                                          'FederateNotExecutionMember',
                                                                          'NotConnected',
                                                                          'RTIinternalError']}],
                         'flushQueueRequest': [   {   'group': 'Time Management',
                                                      'language': 'java',
                                                      'params': 'LogicalTime theTime',
                                                      'return_type': 'void',
                                                      'service': '8.12',
                                                      'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                      'source_line': 1063,
                                                      'throws': [   'LogicalTimeAlreadyPassed',
                                                                    'InvalidLogicalTime',
                                                                    'InTimeAdvancingState',
                                                                    'RequestForTimeRegulationPending',
                                                                    'RequestForTimeConstrainedPending',
                                                                    'SaveInProgress',
                                                                    'RestoreInProgress',
                                                                    'FederateNotExecutionMember',
                                                                    'NotConnected',
                                                                    'RTIinternalError']},
                                                  {   'group': None,
                                                      'language': 'cpp',
                                                      'params': 'LogicalTime const & theTime',
                                                      'return_type': 'void',
                                                      'service': None,
                                                      'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                      'source_line': 985,
                                                      'throws': [   'LogicalTimeAlreadyPassed',
                                                                    'InvalidLogicalTime',
                                                                    'InTimeAdvancingState',
                                                                    'RequestForTimeRegulationPending',
                                                                    'RequestForTimeConstrainedPending',
                                                                    'SaveInProgress',
                                                                    'RestoreInProgress',
                                                                    'FederateNotExecutionMember',
                                                                    'NotConnected',
                                                                    'RTIinternalError']}],
                         'getAttributeHandle': [   {   'group': 'Support Services',
                                                       'language': 'java',
                                                       'params': 'ObjectClassHandle whichClass, String theName',
                                                       'return_type': 'AttributeHandle',
                                                       'service': '10.11',
                                                       'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                       'source_line': 1538,
                                                       'throws': [   'NameNotFound',
                                                                     'InvalidObjectClassHandle',
                                                                     'FederateNotExecutionMember',
                                                                     'NotConnected',
                                                                     'RTIinternalError']},
                                                   {   'group': None,
                                                       'language': 'cpp',
                                                       'params': 'ObjectClassHandle whichClass, std::wstring const & '
                                                                 'theAttributeName',
                                                       'return_type': 'AttributeHandle',
                                                       'service': None,
                                                       'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                       'source_line': 1432,
                                                       'throws': [   'NameNotFound',
                                                                     'InvalidObjectClassHandle',
                                                                     'FederateNotExecutionMember',
                                                                     'NotConnected',
                                                                     'RTIinternalError']}],
                         'getAttributeHandleFactory': [   {   'group': 'Support Services',
                                                              'language': 'java',
                                                              'params': '',
                                                              'return_type': 'AttributeHandleFactory',
                                                              'service': '10.44',
                                                              'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                              'source_line': 1849,
                                                              'throws': [   'FederateNotExecutionMember',
                                                                            'NotConnected']}],
                         'getAttributeHandleSetFactory': [   {   'group': 'Support Services',
                                                                 'language': 'java',
                                                                 'params': '',
                                                                 'return_type': 'AttributeHandleSetFactory',
                                                                 'service': '10.44',
                                                                 'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                 'source_line': 1854,
                                                                 'throws': [   'FederateNotExecutionMember',
                                                                               'NotConnected']}],
                         'getAttributeHandleValueMapFactory': [   {   'group': 'Support Services',
                                                                      'language': 'java',
                                                                      'params': '',
                                                                      'return_type': 'AttributeHandleValueMapFactory',
                                                                      'service': '10.44',
                                                                      'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                      'source_line': 1859,
                                                                      'throws': [   'FederateNotExecutionMember',
                                                                                    'NotConnected']}],
                         'getAttributeName': [   {   'group': 'Support Services',
                                                     'language': 'java',
                                                     'params': 'ObjectClassHandle whichClass, AttributeHandle '
                                                               'theHandle',
                                                     'return_type': 'String',
                                                     'service': '10.12',
                                                     'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                     'source_line': 1548,
                                                     'throws': [   'AttributeNotDefined',
                                                                   'InvalidAttributeHandle',
                                                                   'InvalidObjectClassHandle',
                                                                   'FederateNotExecutionMember',
                                                                   'NotConnected',
                                                                   'RTIinternalError']},
                                                 {   'group': None,
                                                     'language': 'cpp',
                                                     'params': 'ObjectClassHandle whichClass, AttributeHandle '
                                                               'theHandle',
                                                     'return_type': 'std::wstring',
                                                     'service': None,
                                                     'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                     'source_line': 1443,
                                                     'throws': [   'AttributeNotDefined',
                                                                   'InvalidAttributeHandle',
                                                                   'InvalidObjectClassHandle',
                                                                   'FederateNotExecutionMember',
                                                                   'NotConnected',
                                                                   'RTIinternalError']}],
                         'getAttributeSetRegionSetPairListFactory': [   {   'group': 'Support Services',
                                                                            'language': 'java',
                                                                            'params': '',
                                                                            'return_type': 'AttributeSetRegionSetPairListFactory',
                                                                            'service': '10.44',
                                                                            'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                            'source_line': 1864,
                                                                            'throws': [   'FederateNotExecutionMember',
                                                                                          'NotConnected']}],
                         'getAutomaticResignDirective': [   {   'group': 'Support Services',
                                                                'language': 'java',
                                                                'params': '',
                                                                'return_type': 'ResignAction',
                                                                'service': '10.2',
                                                                'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                'source_line': 1466,
                                                                'throws': [   'FederateNotExecutionMember',
                                                                              'NotConnected',
                                                                              'RTIinternalError']},
                                                            {   'group': None,
                                                                'language': 'cpp',
                                                                'params': '',
                                                                'return_type': 'ResignAction',
                                                                'service': None,
                                                                'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                'source_line': 1352,
                                                                'throws': [   'FederateNotExecutionMember',
                                                                              'NotConnected',
                                                                              'RTIinternalError']}],
                         'getAvailableDimensionsForClassAttribute': [   {   'group': 'Support Services',
                                                                            'language': 'java',
                                                                            'params': 'ObjectClassHandle whichClass, '
                                                                                      'AttributeHandle theHandle',
                                                                            'return_type': 'DimensionHandleSet',
                                                                            'service': '10.23',
                                                                            'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                            'source_line': 1646,
                                                                            'throws': [   'AttributeNotDefined',
                                                                                          'InvalidAttributeHandle',
                                                                                          'InvalidObjectClassHandle',
                                                                                          'FederateNotExecutionMember',
                                                                                          'NotConnected',
                                                                                          'RTIinternalError']},
                                                                        {   'group': None,
                                                                            'language': 'cpp',
                                                                            'params': 'ObjectClassHandle theClass, '
                                                                                      'AttributeHandle theHandle',
                                                                            'return_type': 'DimensionHandleSet',
                                                                            'service': None,
                                                                            'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                            'source_line': 1552,
                                                                            'throws': [   'AttributeNotDefined',
                                                                                          'InvalidAttributeHandle',
                                                                                          'InvalidObjectClassHandle',
                                                                                          'FederateNotExecutionMember',
                                                                                          'NotConnected',
                                                                                          'RTIinternalError']}],
                         'getAvailableDimensionsForInteractionClass': [   {   'group': 'Support Services',
                                                                              'language': 'java',
                                                                              'params': 'InteractionClassHandle '
                                                                                        'theHandle',
                                                                              'return_type': 'DimensionHandleSet',
                                                                              'service': '10.24',
                                                                              'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                              'source_line': 1657,
                                                                              'throws': [   'InvalidInteractionClassHandle',
                                                                                            'FederateNotExecutionMember',
                                                                                            'NotConnected',
                                                                                            'RTIinternalError']},
                                                                          {   'group': None,
                                                                              'language': 'cpp',
                                                                              'params': 'InteractionClassHandle '
                                                                                        'theClass',
                                                                              'return_type': 'DimensionHandleSet',
                                                                              'service': None,
                                                                              'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                              'source_line': 1564,
                                                                              'throws': [   'InvalidInteractionClassHandle',
                                                                                            'FederateNotExecutionMember',
                                                                                            'NotConnected',
                                                                                            'RTIinternalError']}],
                         'getDimensionHandle': [   {   'group': 'Support Services',
                                                       'language': 'java',
                                                       'params': 'String theName',
                                                       'return_type': 'DimensionHandle',
                                                       'service': '10.25',
                                                       'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                       'source_line': 1665,
                                                       'throws': [   'NameNotFound',
                                                                     'FederateNotExecutionMember',
                                                                     'NotConnected',
                                                                     'RTIinternalError']},
                                                   {   'group': None,
                                                       'language': 'cpp',
                                                       'params': 'std::wstring const & theName',
                                                       'return_type': 'DimensionHandle',
                                                       'service': None,
                                                       'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                       'source_line': 1573,
                                                       'throws': [   'NameNotFound',
                                                                     'FederateNotExecutionMember',
                                                                     'NotConnected',
                                                                     'RTIinternalError']}],
                         'getDimensionHandleFactory': [   {   'group': 'Support Services',
                                                              'language': 'java',
                                                              'params': '',
                                                              'return_type': 'DimensionHandleFactory',
                                                              'service': '10.44',
                                                              'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                              'source_line': 1869,
                                                              'throws': [   'FederateNotExecutionMember',
                                                                            'NotConnected']}],
                         'getDimensionHandleSet': [   {   'group': 'Support Services',
                                                          'language': 'java',
                                                          'params': 'RegionHandle region',
                                                          'return_type': 'DimensionHandleSet',
                                                          'service': '10.28',
                                                          'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                          'source_line': 1689,
                                                          'throws': [   'InvalidRegion',
                                                                        'SaveInProgress',
                                                                        'RestoreInProgress',
                                                                        'FederateNotExecutionMember',
                                                                        'NotConnected',
                                                                        'RTIinternalError']},
                                                      {   'group': None,
                                                          'language': 'cpp',
                                                          'params': 'RegionHandle theRegionHandle',
                                                          'return_type': 'DimensionHandleSet',
                                                          'service': None,
                                                          'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                          'source_line': 1600,
                                                          'throws': [   'InvalidRegion',
                                                                        'SaveInProgress',
                                                                        'RestoreInProgress',
                                                                        'FederateNotExecutionMember',
                                                                        'NotConnected',
                                                                        'RTIinternalError']}],
                         'getDimensionHandleSetFactory': [   {   'group': 'Support Services',
                                                                 'language': 'java',
                                                                 'params': '',
                                                                 'return_type': 'DimensionHandleSetFactory',
                                                                 'service': '10.44',
                                                                 'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                 'source_line': 1874,
                                                                 'throws': [   'FederateNotExecutionMember',
                                                                               'NotConnected']}],
                         'getDimensionName': [   {   'group': 'Support Services',
                                                     'language': 'java',
                                                     'params': 'DimensionHandle theHandle',
                                                     'return_type': 'String',
                                                     'service': '10.26',
                                                     'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                     'source_line': 1673,
                                                     'throws': [   'InvalidDimensionHandle',
                                                                   'FederateNotExecutionMember',
                                                                   'NotConnected',
                                                                   'RTIinternalError']},
                                                 {   'group': None,
                                                     'language': 'cpp',
                                                     'params': 'DimensionHandle theHandle',
                                                     'return_type': 'std::wstring',
                                                     'service': None,
                                                     'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                     'source_line': 1582,
                                                     'throws': [   'InvalidDimensionHandle',
                                                                   'FederateNotExecutionMember',
                                                                   'NotConnected',
                                                                   'RTIinternalError']}],
                         'getDimensionUpperBound': [   {   'group': 'Support Services',
                                                           'language': 'java',
                                                           'params': 'DimensionHandle theHandle',
                                                           'return_type': 'long',
                                                           'service': '10.27',
                                                           'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                           'source_line': 1681,
                                                           'throws': [   'InvalidDimensionHandle',
                                                                         'FederateNotExecutionMember',
                                                                         'NotConnected',
                                                                         'RTIinternalError']},
                                                       {   'group': None,
                                                           'language': 'cpp',
                                                           'params': 'DimensionHandle theHandle',
                                                           'return_type': 'unsigned long',
                                                           'service': None,
                                                           'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                           'source_line': 1591,
                                                           'throws': [   'InvalidDimensionHandle',
                                                                         'FederateNotExecutionMember',
                                                                         'NotConnected',
                                                                         'RTIinternalError']}],
                         'getFederateHandle': [   {   'group': 'Support Services',
                                                      'language': 'java',
                                                      'params': 'String theName',
                                                      'return_type': 'FederateHandle',
                                                      'service': '10.4',
                                                      'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                      'source_line': 1481,
                                                      'throws': [   'NameNotFound',
                                                                    'FederateNotExecutionMember',
                                                                    'NotConnected',
                                                                    'RTIinternalError']},
                                                  {   'group': None,
                                                      'language': 'cpp',
                                                      'params': 'std::wstring const & theName',
                                                      'return_type': 'FederateHandle',
                                                      'service': None,
                                                      'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                      'source_line': 1368,
                                                      'throws': [   'NameNotFound',
                                                                    'FederateNotExecutionMember',
                                                                    'NotConnected',
                                                                    'RTIinternalError']}],
                         'getFederateHandleFactory': [   {   'group': 'Support Services',
                                                             'language': 'java',
                                                             'params': '',
                                                             'return_type': 'FederateHandleFactory',
                                                             'service': '10.44',
                                                             'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                             'source_line': 1879,
                                                             'throws': ['FederateNotExecutionMember', 'NotConnected']}],
                         'getFederateHandleSetFactory': [   {   'group': 'Support Services',
                                                                'language': 'java',
                                                                'params': '',
                                                                'return_type': 'FederateHandleSetFactory',
                                                                'service': '10.44',
                                                                'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                'source_line': 1884,
                                                                'throws': [   'FederateNotExecutionMember',
                                                                              'NotConnected']}],
                         'getFederateName': [   {   'group': 'Support Services',
                                                    'language': 'java',
                                                    'params': 'FederateHandle theHandle',
                                                    'return_type': 'String',
                                                    'service': '10.5',
                                                    'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                    'source_line': 1489,
                                                    'throws': [   'InvalidFederateHandle',
                                                                  'FederateHandleNotKnown',
                                                                  'FederateNotExecutionMember',
                                                                  'NotConnected',
                                                                  'RTIinternalError']},
                                                {   'group': None,
                                                    'language': 'cpp',
                                                    'params': 'FederateHandle theHandle',
                                                    'return_type': 'std::wstring',
                                                    'service': None,
                                                    'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                    'source_line': 1377,
                                                    'throws': [   'InvalidFederateHandle',
                                                                  'FederateHandleNotKnown',
                                                                  'FederateNotExecutionMember',
                                                                  'NotConnected',
                                                                  'RTIinternalError']}],
                         'getHLAversion': [   {   'group': 'Support Services',
                                                  'language': 'java',
                                                  'params': '',
                                                  'return_type': 'String',
                                                  'service': '10.44',
                                                  'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                  'source_line': 1924,
                                                  'throws': []}],
                         'getInteractionClassHandle': [   {   'group': 'Support Services',
                                                              'language': 'java',
                                                              'params': 'String theName',
                                                              'return_type': 'InteractionClassHandle',
                                                              'service': '10.15',
                                                              'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                              'source_line': 1577,
                                                              'throws': [   'NameNotFound',
                                                                            'FederateNotExecutionMember',
                                                                            'NotConnected',
                                                                            'RTIinternalError']},
                                                          {   'group': None,
                                                              'language': 'cpp',
                                                              'params': 'std::wstring const & theName',
                                                              'return_type': 'InteractionClassHandle',
                                                              'service': None,
                                                              'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                              'source_line': 1475,
                                                              'throws': [   'NameNotFound',
                                                                            'FederateNotExecutionMember',
                                                                            'NotConnected',
                                                                            'RTIinternalError']}],
                         'getInteractionClassHandleFactory': [   {   'group': 'Support Services',
                                                                     'language': 'java',
                                                                     'params': '',
                                                                     'return_type': 'InteractionClassHandleFactory',
                                                                     'service': '10.44',
                                                                     'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                     'source_line': 1889,
                                                                     'throws': [   'FederateNotExecutionMember',
                                                                                   'NotConnected']}],
                         'getInteractionClassName': [   {   'group': 'Support Services',
                                                            'language': 'java',
                                                            'params': 'InteractionClassHandle theHandle',
                                                            'return_type': 'String',
                                                            'service': '10.16',
                                                            'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                            'source_line': 1585,
                                                            'throws': [   'InvalidInteractionClassHandle',
                                                                          'FederateNotExecutionMember',
                                                                          'NotConnected',
                                                                          'RTIinternalError']},
                                                        {   'group': None,
                                                            'language': 'cpp',
                                                            'params': 'InteractionClassHandle theHandle',
                                                            'return_type': 'std::wstring',
                                                            'service': None,
                                                            'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                            'source_line': 1484,
                                                            'throws': [   'InvalidInteractionClassHandle',
                                                                          'FederateNotExecutionMember',
                                                                          'NotConnected',
                                                                          'RTIinternalError']}],
                         'getKnownObjectClassHandle': [   {   'group': 'Support Services',
                                                              'language': 'java',
                                                              'params': 'ObjectInstanceHandle theObject',
                                                              'return_type': 'ObjectClassHandle',
                                                              'service': '10.8',
                                                              'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                              'source_line': 1514,
                                                              'throws': [   'ObjectInstanceNotKnown',
                                                                            'FederateNotExecutionMember',
                                                                            'NotConnected',
                                                                            'RTIinternalError']},
                                                          {   'group': None,
                                                              'language': 'cpp',
                                                              'params': 'ObjectInstanceHandle theObject',
                                                              'return_type': 'ObjectClassHandle',
                                                              'service': None,
                                                              'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                              'source_line': 1405,
                                                              'throws': [   'ObjectInstanceNotKnown',
                                                                            'FederateNotExecutionMember',
                                                                            'NotConnected',
                                                                            'RTIinternalError']}],
                         'getObjectClassHandle': [   {   'group': 'Support Services',
                                                         'language': 'java',
                                                         'params': 'String theName',
                                                         'return_type': 'ObjectClassHandle',
                                                         'service': '10.6',
                                                         'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                         'source_line': 1498,
                                                         'throws': [   'NameNotFound',
                                                                       'FederateNotExecutionMember',
                                                                       'NotConnected',
                                                                       'RTIinternalError']},
                                                     {   'group': None,
                                                         'language': 'cpp',
                                                         'params': 'std::wstring const & theName',
                                                         'return_type': 'ObjectClassHandle',
                                                         'service': None,
                                                         'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                         'source_line': 1387,
                                                         'throws': [   'NameNotFound',
                                                                       'FederateNotExecutionMember',
                                                                       'NotConnected',
                                                                       'RTIinternalError']}],
                         'getObjectClassHandleFactory': [   {   'group': 'Support Services',
                                                                'language': 'java',
                                                                'params': '',
                                                                'return_type': 'ObjectClassHandleFactory',
                                                                'service': '10.44',
                                                                'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                'source_line': 1894,
                                                                'throws': [   'FederateNotExecutionMember',
                                                                              'NotConnected']}],
                         'getObjectClassName': [   {   'group': 'Support Services',
                                                       'language': 'java',
                                                       'params': 'ObjectClassHandle theHandle',
                                                       'return_type': 'String',
                                                       'service': '10.7',
                                                       'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                       'source_line': 1506,
                                                       'throws': [   'InvalidObjectClassHandle',
                                                                     'FederateNotExecutionMember',
                                                                     'NotConnected',
                                                                     'RTIinternalError']},
                                                   {   'group': None,
                                                       'language': 'cpp',
                                                       'params': 'ObjectClassHandle theHandle',
                                                       'return_type': 'std::wstring',
                                                       'service': None,
                                                       'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                       'source_line': 1396,
                                                       'throws': [   'InvalidObjectClassHandle',
                                                                     'FederateNotExecutionMember',
                                                                     'NotConnected',
                                                                     'RTIinternalError']}],
                         'getObjectInstanceHandle': [   {   'group': 'Support Services',
                                                            'language': 'java',
                                                            'params': 'String theName',
                                                            'return_type': 'ObjectInstanceHandle',
                                                            'service': '10.9',
                                                            'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                            'source_line': 1522,
                                                            'throws': [   'ObjectInstanceNotKnown',
                                                                          'FederateNotExecutionMember',
                                                                          'NotConnected',
                                                                          'RTIinternalError']},
                                                        {   'group': None,
                                                            'language': 'cpp',
                                                            'params': 'std::wstring const & theName',
                                                            'return_type': 'ObjectInstanceHandle',
                                                            'service': None,
                                                            'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                            'source_line': 1414,
                                                            'throws': [   'ObjectInstanceNotKnown',
                                                                          'FederateNotExecutionMember',
                                                                          'NotConnected',
                                                                          'RTIinternalError']}],
                         'getObjectInstanceHandleFactory': [   {   'group': 'Support Services',
                                                                   'language': 'java',
                                                                   'params': '',
                                                                   'return_type': 'ObjectInstanceHandleFactory',
                                                                   'service': '10.44',
                                                                   'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                   'source_line': 1899,
                                                                   'throws': [   'FederateNotExecutionMember',
                                                                                 'NotConnected']}],
                         'getObjectInstanceName': [   {   'group': 'Support Services',
                                                          'language': 'java',
                                                          'params': 'ObjectInstanceHandle theHandle',
                                                          'return_type': 'String',
                                                          'service': '10.10',
                                                          'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                          'source_line': 1530,
                                                          'throws': [   'ObjectInstanceNotKnown',
                                                                        'FederateNotExecutionMember',
                                                                        'NotConnected',
                                                                        'RTIinternalError']},
                                                      {   'group': None,
                                                          'language': 'cpp',
                                                          'params': 'ObjectInstanceHandle theHandle',
                                                          'return_type': 'std::wstring',
                                                          'service': None,
                                                          'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                          'source_line': 1423,
                                                          'throws': [   'ObjectInstanceNotKnown',
                                                                        'FederateNotExecutionMember',
                                                                        'NotConnected',
                                                                        'RTIinternalError']}],
                         'getOrderName': [   {   'group': 'Support Services',
                                                 'language': 'java',
                                                 'params': 'OrderType theType',
                                                 'return_type': 'String',
                                                 'service': '10.20',
                                                 'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                 'source_line': 1622,
                                                 'throws': [   'InvalidOrderType',
                                                               'FederateNotExecutionMember',
                                                               'NotConnected',
                                                               'RTIinternalError']},
                                             {   'group': None,
                                                 'language': 'cpp',
                                                 'params': 'OrderType orderType',
                                                 'return_type': 'std::wstring',
                                                 'service': None,
                                                 'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                 'source_line': 1525,
                                                 'throws': [   'InvalidOrderType',
                                                               'FederateNotExecutionMember',
                                                               'NotConnected',
                                                               'RTIinternalError']}],
                         'getOrderType': [   {   'group': 'Support Services',
                                                 'language': 'java',
                                                 'params': 'String theName',
                                                 'return_type': 'OrderType',
                                                 'service': '10.19',
                                                 'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                 'source_line': 1614,
                                                 'throws': [   'InvalidOrderName',
                                                               'FederateNotExecutionMember',
                                                               'NotConnected',
                                                               'RTIinternalError']},
                                             {   'group': None,
                                                 'language': 'cpp',
                                                 'params': 'std::wstring const & orderName',
                                                 'return_type': 'OrderType',
                                                 'service': None,
                                                 'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                 'source_line': 1516,
                                                 'throws': [   'InvalidOrderName',
                                                               'FederateNotExecutionMember',
                                                               'NotConnected',
                                                               'RTIinternalError']}],
                         'getParameterHandle': [   {   'group': 'Support Services',
                                                       'language': 'java',
                                                       'params': 'InteractionClassHandle whichClass, String theName',
                                                       'return_type': 'ParameterHandle',
                                                       'service': '10.17',
                                                       'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                       'source_line': 1593,
                                                       'throws': [   'NameNotFound',
                                                                     'InvalidInteractionClassHandle',
                                                                     'FederateNotExecutionMember',
                                                                     'NotConnected',
                                                                     'RTIinternalError']},
                                                   {   'group': None,
                                                       'language': 'cpp',
                                                       'params': 'InteractionClassHandle whichClass, std::wstring '
                                                                 'const & theName',
                                                       'return_type': 'ParameterHandle',
                                                       'service': None,
                                                       'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                       'source_line': 1493,
                                                       'throws': [   'NameNotFound',
                                                                     'InvalidInteractionClassHandle',
                                                                     'FederateNotExecutionMember',
                                                                     'NotConnected',
                                                                     'RTIinternalError']}],
                         'getParameterHandleFactory': [   {   'group': 'Support Services',
                                                              'language': 'java',
                                                              'params': '',
                                                              'return_type': 'ParameterHandleFactory',
                                                              'service': '10.44',
                                                              'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                              'source_line': 1904,
                                                              'throws': [   'FederateNotExecutionMember',
                                                                            'NotConnected']}],
                         'getParameterHandleValueMapFactory': [   {   'group': 'Support Services',
                                                                      'language': 'java',
                                                                      'params': '',
                                                                      'return_type': 'ParameterHandleValueMapFactory',
                                                                      'service': '10.44',
                                                                      'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                      'source_line': 1909,
                                                                      'throws': [   'FederateNotExecutionMember',
                                                                                    'NotConnected']}],
                         'getParameterName': [   {   'group': 'Support Services',
                                                     'language': 'java',
                                                     'params': 'InteractionClassHandle whichClass, ParameterHandle '
                                                               'theHandle',
                                                     'return_type': 'String',
                                                     'service': '10.18',
                                                     'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                     'source_line': 1603,
                                                     'throws': [   'InteractionParameterNotDefined',
                                                                   'InvalidParameterHandle',
                                                                   'InvalidInteractionClassHandle',
                                                                   'FederateNotExecutionMember',
                                                                   'NotConnected',
                                                                   'RTIinternalError']},
                                                 {   'group': None,
                                                     'language': 'cpp',
                                                     'params': 'InteractionClassHandle whichClass, ParameterHandle '
                                                               'theHandle',
                                                     'return_type': 'std::wstring',
                                                     'service': None,
                                                     'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                     'source_line': 1504,
                                                     'throws': [   'InteractionParameterNotDefined',
                                                                   'InvalidParameterHandle',
                                                                   'InvalidInteractionClassHandle',
                                                                   'FederateNotExecutionMember',
                                                                   'NotConnected',
                                                                   'RTIinternalError']}],
                         'getRangeBounds': [   {   'group': 'Support Services',
                                                   'language': 'java',
                                                   'params': 'RegionHandle region, DimensionHandle dimension',
                                                   'return_type': 'RangeBounds',
                                                   'service': '10.29',
                                                   'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                   'source_line': 1699,
                                                   'throws': [   'RegionDoesNotContainSpecifiedDimension',
                                                                 'InvalidRegion',
                                                                 'SaveInProgress',
                                                                 'RestoreInProgress',
                                                                 'FederateNotExecutionMember',
                                                                 'NotConnected',
                                                                 'RTIinternalError']},
                                               {   'group': None,
                                                   'language': 'cpp',
                                                   'params': 'RegionHandle theRegionHandle, DimensionHandle '
                                                             'theDimensionHandle',
                                                   'return_type': 'RangeBounds',
                                                   'service': None,
                                                   'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                   'source_line': 1611,
                                                   'throws': [   'RegionDoesNotContainSpecifiedDimension',
                                                                 'InvalidRegion',
                                                                 'SaveInProgress',
                                                                 'RestoreInProgress',
                                                                 'FederateNotExecutionMember',
                                                                 'NotConnected',
                                                                 'RTIinternalError']}],
                         'getRegionHandleSetFactory': [   {   'group': 'Support Services',
                                                              'language': 'java',
                                                              'params': '',
                                                              'return_type': 'RegionHandleSetFactory',
                                                              'service': '10.44',
                                                              'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                              'source_line': 1914,
                                                              'throws': [   'FederateNotExecutionMember',
                                                                            'NotConnected']}],
                         'getTimeFactory': [   {   'group': 'Support Services',
                                                   'language': 'java',
                                                   'params': '',
                                                   'return_type': 'LogicalTimeFactory',
                                                   'service': '10.44',
                                                   'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                   'source_line': 1926,
                                                   'throws': ['FederateNotExecutionMember', 'NotConnected']},
                                               {   'group': None,
                                                   'language': 'cpp',
                                                   'params': ') const throw ( FederateNotExecutionMember, '
                                                             'NotConnected, RTIinternalError',
                                                   'return_type': 'std::auto_ptr<LogicalTimeFactory>',
                                                   'service': None,
                                                   'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                   'source_line': 1769,
                                                   'throws': []}],
                         'getTransportationName': [   {   'group': None,
                                                          'language': 'cpp',
                                                          'params': 'TransportationType transportationType',
                                                          'return_type': 'std::wstring',
                                                          'service': None,
                                                          'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                          'source_line': 1543,
                                                          'throws': [   'InvalidTransportationType',
                                                                        'FederateNotExecutionMember',
                                                                        'NotConnected',
                                                                        'RTIinternalError']}],
                         'getTransportationType': [   {   'group': None,
                                                          'language': 'cpp',
                                                          'params': 'std::wstring const & transportationName',
                                                          'return_type': 'TransportationType',
                                                          'service': None,
                                                          'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                          'source_line': 1534,
                                                          'throws': [   'InvalidTransportationName',
                                                                        'FederateNotExecutionMember',
                                                                        'NotConnected',
                                                                        'RTIinternalError']}],
                         'getTransportationTypeHandle': [   {   'group': 'Support Services',
                                                                'language': 'java',
                                                                'params': 'String theName',
                                                                'return_type': 'TransportationTypeHandle',
                                                                'service': '10.21',
                                                                'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                'source_line': 1630,
                                                                'throws': [   'InvalidTransportationName',
                                                                              'FederateNotExecutionMember',
                                                                              'NotConnected',
                                                                              'RTIinternalError']}],
                         'getTransportationTypeHandleFactory': [   {   'group': 'Support Services',
                                                                       'language': 'java',
                                                                       'params': '',
                                                                       'return_type': 'TransportationTypeHandleFactory',
                                                                       'service': '10.44',
                                                                       'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                       'source_line': 1919,
                                                                       'throws': [   'FederateNotExecutionMember',
                                                                                     'NotConnected']}],
                         'getTransportationTypeName': [   {   'group': 'Support Services',
                                                              'language': 'java',
                                                              'params': 'TransportationTypeHandle theHandle',
                                                              'return_type': 'String',
                                                              'service': '10.22',
                                                              'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                              'source_line': 1638,
                                                              'throws': [   'InvalidTransportationType',
                                                                            'FederateNotExecutionMember',
                                                                            'NotConnected',
                                                                            'RTIinternalError']}],
                         'getUpdateRateValue': [   {   'group': 'Support Services',
                                                       'language': 'java',
                                                       'params': 'String updateRateDesignator',
                                                       'return_type': 'double',
                                                       'service': '10.13',
                                                       'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                       'source_line': 1559,
                                                       'throws': [   'InvalidUpdateRateDesignator',
                                                                     'FederateNotExecutionMember',
                                                                     'NotConnected',
                                                                     'RTIinternalError']},
                                                   {   'group': None,
                                                       'language': 'cpp',
                                                       'params': 'std::wstring const & updateRateDesignator',
                                                       'return_type': 'double',
                                                       'service': None,
                                                       'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                       'source_line': 1455,
                                                       'throws': [   'InvalidUpdateRateDesignator',
                                                                     'FederateNotExecutionMember',
                                                                     'NotConnected',
                                                                     'RTIinternalError']}],
                         'getUpdateRateValueForAttribute': [   {   'group': 'Support Services',
                                                                   'language': 'java',
                                                                   'params': 'ObjectInstanceHandle theObject, '
                                                                             'AttributeHandle theAttribute',
                                                                   'return_type': 'double',
                                                                   'service': '10.14',
                                                                   'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                   'source_line': 1567,
                                                                   'throws': [   'ObjectInstanceNotKnown',
                                                                                 'AttributeNotDefined',
                                                                                 'FederateNotExecutionMember',
                                                                                 'NotConnected',
                                                                                 'RTIinternalError']},
                                                               {   'group': None,
                                                                   'language': 'cpp',
                                                                   'params': 'ObjectInstanceHandle theObject, '
                                                                             'AttributeHandle theAttribute',
                                                                   'return_type': 'double',
                                                                   'service': None,
                                                                   'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                   'source_line': 1464,
                                                                   'throws': [   'ObjectInstanceNotKnown',
                                                                                 'AttributeNotDefined',
                                                                                 'FederateNotExecutionMember',
                                                                                 'NotConnected',
                                                                                 'RTIinternalError']}],
                         'isAttributeOwnedByFederate': [   {   'group': 'Ownership Management',
                                                               'language': 'java',
                                                               'params': 'ObjectInstanceHandle theObject, '
                                                                         'AttributeHandle theAttribute',
                                                               'return_type': 'boolean',
                                                               'service': '7.19',
                                                               'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                               'source_line': 946,
                                                               'throws': [   'AttributeNotDefined',
                                                                             'ObjectInstanceNotKnown',
                                                                             'SaveInProgress',
                                                                             'RestoreInProgress',
                                                                             'FederateNotExecutionMember',
                                                                             'NotConnected',
                                                                             'RTIinternalError']},
                                                           {   'group': None,
                                                               'language': 'cpp',
                                                               'params': 'ObjectInstanceHandle theObject, '
                                                                         'AttributeHandle theAttribute',
                                                               'return_type': 'bool',
                                                               'service': None,
                                                               'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                               'source_line': 862,
                                                               'throws': [   'AttributeNotDefined',
                                                                             'ObjectInstanceNotKnown',
                                                                             'SaveInProgress',
                                                                             'RestoreInProgress',
                                                                             'FederateNotExecutionMember',
                                                                             'NotConnected',
                                                                             'RTIinternalError']}],
                         'joinFederationExecution': [   {   'group': 'Federation Management',
                                                            'language': 'java',
                                                            'params': 'String federateName, String federateType, '
                                                                      'String federationExecutionName, URL[] '
                                                                      'additionalFomModules',
                                                            'return_type': 'FederateHandle',
                                                            'service': '4.9',
                                                            'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                            'source_line': 160,
                                                            'throws': [   'CouldNotCreateLogicalTimeFactory',
                                                                          'FederateNameAlreadyInUse',
                                                                          'FederationExecutionDoesNotExist',
                                                                          'InconsistentFDD',
                                                                          'ErrorReadingFDD',
                                                                          'CouldNotOpenFDD',
                                                                          'SaveInProgress',
                                                                          'RestoreInProgress',
                                                                          'FederateAlreadyExecutionMember',
                                                                          'NotConnected',
                                                                          'CallNotAllowedFromWithinCallback',
                                                                          'RTIinternalError']},
                                                        {   'group': 'Federation Management',
                                                            'language': 'java',
                                                            'params': 'String federateType, String '
                                                                      'federationExecutionName, URL[] '
                                                                      'additionalFomModules',
                                                            'return_type': 'FederateHandle',
                                                            'service': '4.9',
                                                            'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                            'source_line': 179,
                                                            'throws': [   'CouldNotCreateLogicalTimeFactory',
                                                                          'FederationExecutionDoesNotExist',
                                                                          'InconsistentFDD',
                                                                          'ErrorReadingFDD',
                                                                          'CouldNotOpenFDD',
                                                                          'SaveInProgress',
                                                                          'RestoreInProgress',
                                                                          'FederateAlreadyExecutionMember',
                                                                          'NotConnected',
                                                                          'CallNotAllowedFromWithinCallback',
                                                                          'RTIinternalError']},
                                                        {   'group': 'Federation Management',
                                                            'language': 'java',
                                                            'params': 'String federateName, String federateType, '
                                                                      'String federationExecutionName',
                                                            'return_type': 'FederateHandle',
                                                            'service': '4.9',
                                                            'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                            'source_line': 196,
                                                            'throws': [   'CouldNotCreateLogicalTimeFactory',
                                                                          'FederateNameAlreadyInUse',
                                                                          'FederationExecutionDoesNotExist',
                                                                          'SaveInProgress',
                                                                          'RestoreInProgress',
                                                                          'FederateAlreadyExecutionMember',
                                                                          'NotConnected',
                                                                          'CallNotAllowedFromWithinCallback',
                                                                          'RTIinternalError']},
                                                        {   'group': 'Federation Management',
                                                            'language': 'java',
                                                            'params': 'String federateType, String '
                                                                      'federationExecutionName',
                                                            'return_type': 'FederateHandle',
                                                            'service': '4.9',
                                                            'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                            'source_line': 211,
                                                            'throws': [   'CouldNotCreateLogicalTimeFactory',
                                                                          'FederationExecutionDoesNotExist',
                                                                          'SaveInProgress',
                                                                          'RestoreInProgress',
                                                                          'FederateAlreadyExecutionMember',
                                                                          'NotConnected',
                                                                          'CallNotAllowedFromWithinCallback',
                                                                          'RTIinternalError']},
                                                        {   'group': None,
                                                            'language': 'cpp',
                                                            'params': 'std::wstring const & federateType, std::wstring '
                                                                      'const & federationExecutionName, '
                                                                      'std::vector<std::wstring> const & '
                                                                      'additionalFomModules=std::vector<std::wstring>()',
                                                            'return_type': 'FederateHandle',
                                                            'service': None,
                                                            'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                            'source_line': 124,
                                                            'throws': [   'CouldNotCreateLogicalTimeFactory',
                                                                          'FederationExecutionDoesNotExist',
                                                                          'InconsistentFDD',
                                                                          'ErrorReadingFDD',
                                                                          'CouldNotOpenFDD',
                                                                          'SaveInProgress',
                                                                          'RestoreInProgress',
                                                                          'FederateAlreadyExecutionMember',
                                                                          'NotConnected',
                                                                          'CallNotAllowedFromWithinCallback',
                                                                          'RTIinternalError']},
                                                        {   'group': None,
                                                            'language': 'cpp',
                                                            'params': 'std::wstring const & federateName, std::wstring '
                                                                      'const & federateType, std::wstring const & '
                                                                      'federationExecutionName, '
                                                                      'std::vector<std::wstring> const & '
                                                                      'additionalFomModules=std::vector<std::wstring>()',
                                                            'return_type': 'FederateHandle',
                                                            'service': None,
                                                            'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                            'source_line': 141,
                                                            'throws': [   'CouldNotCreateLogicalTimeFactory',
                                                                          'FederateNameAlreadyInUse',
                                                                          'FederationExecutionDoesNotExist',
                                                                          'InconsistentFDD',
                                                                          'ErrorReadingFDD',
                                                                          'CouldNotOpenFDD',
                                                                          'SaveInProgress',
                                                                          'RestoreInProgress',
                                                                          'FederateAlreadyExecutionMember',
                                                                          'NotConnected',
                                                                          'CallNotAllowedFromWithinCallback',
                                                                          'RTIinternalError']}],
                         'listFederationExecutions': [   {   'group': 'Federation Management',
                                                             'language': 'java',
                                                             'params': '',
                                                             'return_type': 'void',
                                                             'service': '4.7',
                                                             'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                             'source_line': 154,
                                                             'throws': ['NotConnected', 'RTIinternalError']},
                                                         {   'group': None,
                                                             'language': 'cpp',
                                                             'params': '',
                                                             'return_type': 'void',
                                                             'service': None,
                                                             'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                             'source_line': 118,
                                                             'throws': ['NotConnected', 'RTIinternalError']}],
                         'localDeleteObjectInstance': [   {   'group': 'Object Management',
                                                              'language': 'java',
                                                              'params': 'ObjectInstanceHandle objectHandle',
                                                              'return_type': 'void',
                                                              'service': '6.16',
                                                              'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                              'source_line': 709,
                                                              'throws': [   'OwnershipAcquisitionPending',
                                                                            'FederateOwnsAttributes',
                                                                            'ObjectInstanceNotKnown',
                                                                            'SaveInProgress',
                                                                            'RestoreInProgress',
                                                                            'FederateNotExecutionMember',
                                                                            'NotConnected',
                                                                            'RTIinternalError']},
                                                          {   'group': None,
                                                              'language': 'cpp',
                                                              'params': 'ObjectInstanceHandle theObject',
                                                              'return_type': 'void',
                                                              'service': None,
                                                              'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                              'source_line': 607,
                                                              'throws': [   'OwnershipAcquisitionPending',
                                                                            'FederateOwnsAttributes',
                                                                            'ObjectInstanceNotKnown',
                                                                            'SaveInProgress',
                                                                            'RestoreInProgress',
                                                                            'FederateNotExecutionMember',
                                                                            'NotConnected',
                                                                            'RTIinternalError']}],
                         'modifyLookahead': [   {   'group': 'Time Management',
                                                    'language': 'java',
                                                    'params': 'LogicalTimeInterval theLookahead',
                                                    'return_type': 'void',
                                                    'service': '8.19',
                                                    'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                    'source_line': 1124,
                                                    'throws': [   'InvalidLookahead',
                                                                  'InTimeAdvancingState',
                                                                  'TimeRegulationIsNotEnabled',
                                                                  'SaveInProgress',
                                                                  'RestoreInProgress',
                                                                  'FederateNotExecutionMember',
                                                                  'NotConnected',
                                                                  'RTIinternalError']},
                                                {   'group': None,
                                                    'language': 'cpp',
                                                    'params': 'LogicalTimeInterval const & theLookahead',
                                                    'return_type': 'void',
                                                    'service': None,
                                                    'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                    'source_line': 1047,
                                                    'throws': [   'InvalidLookahead',
                                                                  'InTimeAdvancingState',
                                                                  'TimeRegulationIsNotEnabled',
                                                                  'SaveInProgress',
                                                                  'RestoreInProgress',
                                                                  'FederateNotExecutionMember',
                                                                  'NotConnected',
                                                                  'RTIinternalError']}],
                         'negotiatedAttributeOwnershipDivestiture': [   {   'group': 'Ownership Management',
                                                                            'language': 'java',
                                                                            'params': 'ObjectInstanceHandle theObject, '
                                                                                      'AttributeHandleSet '
                                                                                      'theAttributes, byte[] '
                                                                                      'userSuppliedTag',
                                                                            'return_type': 'void',
                                                                            'service': '7.3',
                                                                            'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                            'source_line': 817,
                                                                            'throws': [   'AttributeAlreadyBeingDivested',
                                                                                          'AttributeNotOwned',
                                                                                          'AttributeNotDefined',
                                                                                          'ObjectInstanceNotKnown',
                                                                                          'SaveInProgress',
                                                                                          'RestoreInProgress',
                                                                                          'FederateNotExecutionMember',
                                                                                          'NotConnected',
                                                                                          'RTIinternalError']},
                                                                        {   'group': None,
                                                                            'language': 'cpp',
                                                                            'params': 'ObjectInstanceHandle theObject, '
                                                                                      'AttributeHandleSet const & '
                                                                                      'theAttributes, '
                                                                                      'VariableLengthData const & '
                                                                                      'theUserSuppliedTag',
                                                                            'return_type': 'void',
                                                                            'service': None,
                                                                            'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                            'source_line': 723,
                                                                            'throws': [   'AttributeAlreadyBeingDivested',
                                                                                          'AttributeNotOwned',
                                                                                          'AttributeNotDefined',
                                                                                          'ObjectInstanceNotKnown',
                                                                                          'SaveInProgress',
                                                                                          'RestoreInProgress',
                                                                                          'FederateNotExecutionMember',
                                                                                          'NotConnected',
                                                                                          'RTIinternalError']}],
                         'nextMessageRequest': [   {   'group': 'Time Management',
                                                       'language': 'java',
                                                       'params': 'LogicalTime theTime',
                                                       'return_type': 'void',
                                                       'service': '8.10',
                                                       'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                       'source_line': 1035,
                                                       'throws': [   'LogicalTimeAlreadyPassed',
                                                                     'InvalidLogicalTime',
                                                                     'InTimeAdvancingState',
                                                                     'RequestForTimeRegulationPending',
                                                                     'RequestForTimeConstrainedPending',
                                                                     'SaveInProgress',
                                                                     'RestoreInProgress',
                                                                     'FederateNotExecutionMember',
                                                                     'NotConnected',
                                                                     'RTIinternalError']},
                                                   {   'group': None,
                                                       'language': 'cpp',
                                                       'params': 'LogicalTime const & theTime',
                                                       'return_type': 'void',
                                                       'service': None,
                                                       'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                       'source_line': 955,
                                                       'throws': [   'LogicalTimeAlreadyPassed',
                                                                     'InvalidLogicalTime',
                                                                     'InTimeAdvancingState',
                                                                     'RequestForTimeRegulationPending',
                                                                     'RequestForTimeConstrainedPending',
                                                                     'SaveInProgress',
                                                                     'RestoreInProgress',
                                                                     'FederateNotExecutionMember',
                                                                     'NotConnected',
                                                                     'RTIinternalError']}],
                         'nextMessageRequestAvailable': [   {   'group': 'Time Management',
                                                                'language': 'java',
                                                                'params': 'LogicalTime theTime',
                                                                'return_type': 'void',
                                                                'service': '8.11',
                                                                'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                'source_line': 1049,
                                                                'throws': [   'LogicalTimeAlreadyPassed',
                                                                              'InvalidLogicalTime',
                                                                              'InTimeAdvancingState',
                                                                              'RequestForTimeRegulationPending',
                                                                              'RequestForTimeConstrainedPending',
                                                                              'SaveInProgress',
                                                                              'RestoreInProgress',
                                                                              'FederateNotExecutionMember',
                                                                              'NotConnected',
                                                                              'RTIinternalError']},
                                                            {   'group': None,
                                                                'language': 'cpp',
                                                                'params': 'LogicalTime const & theTime',
                                                                'return_type': 'void',
                                                                'service': None,
                                                                'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                'source_line': 970,
                                                                'throws': [   'LogicalTimeAlreadyPassed',
                                                                              'InvalidLogicalTime',
                                                                              'InTimeAdvancingState',
                                                                              'RequestForTimeRegulationPending',
                                                                              'RequestForTimeConstrainedPending',
                                                                              'SaveInProgress',
                                                                              'RestoreInProgress',
                                                                              'FederateNotExecutionMember',
                                                                              'NotConnected',
                                                                              'RTIinternalError']}],
                         'normalizeFederateHandle': [   {   'group': 'Support Services',
                                                            'language': 'java',
                                                            'params': 'FederateHandle federateHandle',
                                                            'return_type': 'long',
                                                            'service': '10.31',
                                                            'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                            'source_line': 1726,
                                                            'throws': [   'InvalidFederateHandle',
                                                                          'FederateNotExecutionMember',
                                                                          'NotConnected',
                                                                          'RTIinternalError']},
                                                        {   'group': None,
                                                            'language': 'cpp',
                                                            'params': 'FederateHandle theFederateHandle',
                                                            'return_type': 'unsigned long',
                                                            'service': None,
                                                            'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                            'source_line': 1640,
                                                            'throws': [   'InvalidFederateHandle',
                                                                          'FederateNotExecutionMember',
                                                                          'NotConnected',
                                                                          'RTIinternalError']}],
                         'normalizeServiceGroup': [   {   'group': 'Support Services',
                                                          'language': 'java',
                                                          'params': 'ServiceGroup group',
                                                          'return_type': 'long',
                                                          'service': '10.32',
                                                          'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                          'source_line': 1734,
                                                          'throws': [   'InvalidServiceGroup',
                                                                        'FederateNotExecutionMember',
                                                                        'NotConnected',
                                                                        'RTIinternalError']},
                                                      {   'group': None,
                                                          'language': 'cpp',
                                                          'params': 'ServiceGroup theServiceGroup',
                                                          'return_type': 'unsigned long',
                                                          'service': None,
                                                          'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                          'source_line': 1649,
                                                          'throws': [   'InvalidServiceGroup',
                                                                        'FederateNotExecutionMember',
                                                                        'NotConnected',
                                                                        'RTIinternalError']}],
                         'publishInteractionClass': [   {   'group': 'Declaration Management',
                                                            'language': 'java',
                                                            'params': 'InteractionClassHandle theInteraction',
                                                            'return_type': 'void',
                                                            'service': '5.4',
                                                            'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                            'source_line': 427,
                                                            'throws': [   'InteractionClassNotDefined',
                                                                          'SaveInProgress',
                                                                          'RestoreInProgress',
                                                                          'FederateNotExecutionMember',
                                                                          'NotConnected',
                                                                          'RTIinternalError']},
                                                        {   'group': None,
                                                            'language': 'cpp',
                                                            'params': 'InteractionClassHandle theInteraction',
                                                            'return_type': 'void',
                                                            'service': None,
                                                            'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                            'source_line': 358,
                                                            'throws': [   'InteractionClassNotDefined',
                                                                          'SaveInProgress',
                                                                          'RestoreInProgress',
                                                                          'FederateNotExecutionMember',
                                                                          'NotConnected',
                                                                          'RTIinternalError']}],
                         'publishObjectClassAttributes': [   {   'group': 'Declaration Management',
                                                                 'language': 'java',
                                                                 'params': 'ObjectClassHandle theClass, '
                                                                           'AttributeHandleSet attributeList',
                                                                 'return_type': 'void',
                                                                 'service': '5.2',
                                                                 'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                 'source_line': 391,
                                                                 'throws': [   'AttributeNotDefined',
                                                                               'ObjectClassNotDefined',
                                                                               'SaveInProgress',
                                                                               'RestoreInProgress',
                                                                               'FederateNotExecutionMember',
                                                                               'NotConnected',
                                                                               'RTIinternalError']},
                                                             {   'group': None,
                                                                 'language': 'cpp',
                                                                 'params': 'ObjectClassHandle theClass, '
                                                                           'AttributeHandleSet const & attributeList',
                                                                 'return_type': 'void',
                                                                 'service': None,
                                                                 'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                 'source_line': 320,
                                                                 'throws': [   'AttributeNotDefined',
                                                                               'ObjectClassNotDefined',
                                                                               'SaveInProgress',
                                                                               'RestoreInProgress',
                                                                               'FederateNotExecutionMember',
                                                                               'NotConnected',
                                                                               'RTIinternalError']}],
                         'queryAttributeOwnership': [   {   'group': 'Ownership Management',
                                                            'language': 'java',
                                                            'params': 'ObjectInstanceHandle theObject, AttributeHandle '
                                                                      'theAttribute',
                                                            'return_type': 'void',
                                                            'service': '7.17',
                                                            'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                            'source_line': 934,
                                                            'throws': [   'AttributeNotDefined',
                                                                          'ObjectInstanceNotKnown',
                                                                          'SaveInProgress',
                                                                          'RestoreInProgress',
                                                                          'FederateNotExecutionMember',
                                                                          'NotConnected',
                                                                          'RTIinternalError']},
                                                        {   'group': None,
                                                            'language': 'cpp',
                                                            'params': 'ObjectInstanceHandle theObject, AttributeHandle '
                                                                      'theAttribute',
                                                            'return_type': 'void',
                                                            'service': None,
                                                            'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                            'source_line': 849,
                                                            'throws': [   'AttributeNotDefined',
                                                                          'ObjectInstanceNotKnown',
                                                                          'SaveInProgress',
                                                                          'RestoreInProgress',
                                                                          'FederateNotExecutionMember',
                                                                          'NotConnected',
                                                                          'RTIinternalError']}],
                         'queryAttributeTransportationType': [   {   'group': 'Object Management',
                                                                     'language': 'java',
                                                                     'params': 'ObjectInstanceHandle theObject, '
                                                                               'AttributeHandle theAttribute',
                                                                     'return_type': 'void',
                                                                     'service': '6.25',
                                                                     'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                     'source_line': 763,
                                                                     'throws': [   'AttributeNotDefined',
                                                                                   'ObjectInstanceNotKnown',
                                                                                   'SaveInProgress',
                                                                                   'RestoreInProgress',
                                                                                   'FederateNotExecutionMember',
                                                                                   'NotConnected',
                                                                                   'RTIinternalError']},
                                                                 {   'group': None,
                                                                     'language': 'cpp',
                                                                     'params': 'ObjectInstanceHandle theObject, '
                                                                               'AttributeHandle theAttribute',
                                                                     'return_type': 'void',
                                                                     'service': None,
                                                                     'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                     'source_line': 664,
                                                                     'throws': [   'AttributeNotDefined',
                                                                                   'ObjectInstanceNotKnown',
                                                                                   'SaveInProgress',
                                                                                   'RestoreInProgress',
                                                                                   'FederateNotExecutionMember',
                                                                                   'NotConnected',
                                                                                   'RTIinternalError']}],
                         'queryFederationRestoreStatus': [   {   'group': 'Federation Management',
                                                                 'language': 'java',
                                                                 'params': '',
                                                                 'return_type': 'void',
                                                                 'service': '4.31',
                                                                 'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                 'source_line': 378,
                                                                 'throws': [   'SaveInProgress',
                                                                               'FederateNotExecutionMember',
                                                                               'NotConnected',
                                                                               'RTIinternalError']},
                                                             {   'group': None,
                                                                 'language': 'cpp',
                                                                 'params': '',
                                                                 'return_type': 'void',
                                                                 'service': None,
                                                                 'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                 'source_line': 308,
                                                                 'throws': [   'SaveInProgress',
                                                                               'FederateNotExecutionMember',
                                                                               'NotConnected',
                                                                               'RTIinternalError']}],
                         'queryFederationSaveStatus': [   {   'group': 'Federation Management',
                                                              'language': 'java',
                                                              'params': '',
                                                              'return_type': 'void',
                                                              'service': '4.22',
                                                              'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                              'source_line': 335,
                                                              'throws': [   'RestoreInProgress',
                                                                            'FederateNotExecutionMember',
                                                                            'NotConnected',
                                                                            'RTIinternalError']},
                                                          {   'group': None,
                                                              'language': 'cpp',
                                                              'params': '',
                                                              'return_type': 'void',
                                                              'service': None,
                                                              'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                              'source_line': 265,
                                                              'throws': [   'RestoreInProgress',
                                                                            'FederateNotExecutionMember',
                                                                            'NotConnected',
                                                                            'RTIinternalError']}],
                         'queryGALT': [   {   'group': 'Time Management',
                                              'language': 'java',
                                              'params': '',
                                              'return_type': 'TimeQueryReturn',
                                              'service': '8.16',
                                              'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                              'source_line': 1097,
                                              'throws': [   'SaveInProgress',
                                                            'RestoreInProgress',
                                                            'FederateNotExecutionMember',
                                                            'NotConnected',
                                                            'RTIinternalError']},
                                          {   'group': None,
                                              'language': 'cpp',
                                              'params': 'LogicalTime & theTime',
                                              'return_type': 'bool',
                                              'service': None,
                                              'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                              'source_line': 1020,
                                              'throws': [   'SaveInProgress',
                                                            'RestoreInProgress',
                                                            'FederateNotExecutionMember',
                                                            'NotConnected',
                                                            'RTIinternalError']}],
                         'queryInteractionTransportationType': [   {   'group': 'Object Management',
                                                                       'language': 'java',
                                                                       'params': 'FederateHandle theFederate, '
                                                                                 'InteractionClassHandle '
                                                                                 'theInteraction',
                                                                       'return_type': 'void',
                                                                       'service': '6.29',
                                                                       'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                       'source_line': 789,
                                                                       'throws': [   'InteractionClassNotDefined',
                                                                                     'SaveInProgress',
                                                                                     'RestoreInProgress',
                                                                                     'FederateNotExecutionMember',
                                                                                     'NotConnected',
                                                                                     'RTIinternalError']},
                                                                   {   'group': None,
                                                                       'language': 'cpp',
                                                                       'params': 'FederateHandle theFederate, '
                                                                                 'InteractionClassHandle '
                                                                                 'theInteraction',
                                                                       'return_type': 'void',
                                                                       'service': None,
                                                                       'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                       'source_line': 692,
                                                                       'throws': [   'InteractionClassNotDefined',
                                                                                     'SaveInProgress',
                                                                                     'RestoreInProgress',
                                                                                     'FederateNotExecutionMember',
                                                                                     'NotConnected',
                                                                                     'RTIinternalError']}],
                         'queryLITS': [   {   'group': 'Time Management',
                                              'language': 'java',
                                              'params': '',
                                              'return_type': 'TimeQueryReturn',
                                              'service': '8.18',
                                              'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                              'source_line': 1115,
                                              'throws': [   'SaveInProgress',
                                                            'RestoreInProgress',
                                                            'FederateNotExecutionMember',
                                                            'NotConnected',
                                                            'RTIinternalError']},
                                          {   'group': None,
                                              'language': 'cpp',
                                              'params': 'LogicalTime & theTime',
                                              'return_type': 'bool',
                                              'service': None,
                                              'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                              'source_line': 1038,
                                              'throws': [   'SaveInProgress',
                                                            'RestoreInProgress',
                                                            'FederateNotExecutionMember',
                                                            'NotConnected',
                                                            'RTIinternalError']}],
                         'queryLogicalTime': [   {   'group': 'Time Management',
                                                     'language': 'java',
                                                     'params': '',
                                                     'return_type': 'LogicalTime',
                                                     'service': '8.17',
                                                     'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                     'source_line': 1106,
                                                     'throws': [   'SaveInProgress',
                                                                   'RestoreInProgress',
                                                                   'FederateNotExecutionMember',
                                                                   'NotConnected',
                                                                   'RTIinternalError']},
                                                 {   'group': None,
                                                     'language': 'cpp',
                                                     'params': 'LogicalTime & theTime',
                                                     'return_type': 'void',
                                                     'service': None,
                                                     'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                     'source_line': 1029,
                                                     'throws': [   'SaveInProgress',
                                                                   'RestoreInProgress',
                                                                   'FederateNotExecutionMember',
                                                                   'NotConnected',
                                                                   'RTIinternalError']}],
                         'queryLookahead': [   {   'group': 'Time Management',
                                                   'language': 'java',
                                                   'params': '',
                                                   'return_type': 'LogicalTimeInterval',
                                                   'service': '8.20',
                                                   'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                   'source_line': 1136,
                                                   'throws': [   'TimeRegulationIsNotEnabled',
                                                                 'SaveInProgress',
                                                                 'RestoreInProgress',
                                                                 'FederateNotExecutionMember',
                                                                 'NotConnected',
                                                                 'RTIinternalError']},
                                               {   'group': None,
                                                   'language': 'cpp',
                                                   'params': 'LogicalTimeInterval & interval',
                                                   'return_type': 'void',
                                                   'service': None,
                                                   'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                   'source_line': 1060,
                                                   'throws': [   'TimeRegulationIsNotEnabled',
                                                                 'SaveInProgress',
                                                                 'RestoreInProgress',
                                                                 'FederateNotExecutionMember',
                                                                 'NotConnected',
                                                                 'RTIinternalError']}],
                         'registerFederationSynchronizationPoint': [   {   'group': 'Federation Management',
                                                                           'language': 'java',
                                                                           'params': 'String '
                                                                                     'synchronizationPointLabel, '
                                                                                     'byte[] userSuppliedTag',
                                                                           'return_type': 'void',
                                                                           'service': '4.11',
                                                                           'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                           'source_line': 235,
                                                                           'throws': [   'SaveInProgress',
                                                                                         'RestoreInProgress',
                                                                                         'FederateNotExecutionMember',
                                                                                         'NotConnected',
                                                                                         'RTIinternalError']},
                                                                       {   'group': 'Federation Management',
                                                                           'language': 'java',
                                                                           'params': 'String '
                                                                                     'synchronizationPointLabel, '
                                                                                     'byte[] userSuppliedTag, '
                                                                                     'FederateHandleSet '
                                                                                     'synchronizationSet',
                                                                           'return_type': 'void',
                                                                           'service': '4.11',
                                                                           'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                           'source_line': 245,
                                                                           'throws': [   'InvalidFederateHandle',
                                                                                         'SaveInProgress',
                                                                                         'RestoreInProgress',
                                                                                         'FederateNotExecutionMember',
                                                                                         'NotConnected',
                                                                                         'RTIinternalError']},
                                                                       {   'group': None,
                                                                           'language': 'cpp',
                                                                           'params': 'std::wstring const & label, '
                                                                                     'VariableLengthData const & '
                                                                                     'theUserSuppliedTag',
                                                                           'return_type': 'void',
                                                                           'service': None,
                                                                           'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                           'source_line': 173,
                                                                           'throws': [   'SaveInProgress',
                                                                                         'RestoreInProgress',
                                                                                         'FederateNotExecutionMember',
                                                                                         'NotConnected',
                                                                                         'RTIinternalError']},
                                                                       {   'group': None,
                                                                           'language': 'cpp',
                                                                           'params': 'std::wstring const & label, '
                                                                                     'VariableLengthData const & '
                                                                                     'theUserSuppliedTag, '
                                                                                     'FederateHandleSet const & '
                                                                                     'synchronizationSet',
                                                                           'return_type': 'void',
                                                                           'service': None,
                                                                           'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                           'source_line': 183,
                                                                           'throws': [   'InvalidFederateHandle',
                                                                                         'SaveInProgress',
                                                                                         'RestoreInProgress',
                                                                                         'FederateNotExecutionMember',
                                                                                         'NotConnected',
                                                                                         'RTIinternalError']}],
                         'registerObjectInstance': [   {   'group': 'Object Management',
                                                           'language': 'java',
                                                           'params': 'ObjectClassHandle theClass',
                                                           'return_type': 'ObjectInstanceHandle',
                                                           'service': '6.8',
                                                           'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                           'source_line': 598,
                                                           'throws': [   'ObjectClassNotPublished',
                                                                         'ObjectClassNotDefined',
                                                                         'SaveInProgress',
                                                                         'RestoreInProgress',
                                                                         'FederateNotExecutionMember',
                                                                         'NotConnected',
                                                                         'RTIinternalError']},
                                                       {   'group': 'Object Management',
                                                           'language': 'java',
                                                           'params': 'ObjectClassHandle theClass, String theObjectName',
                                                           'return_type': 'ObjectInstanceHandle',
                                                           'service': '6.8',
                                                           'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                           'source_line': 609,
                                                           'throws': [   'ObjectInstanceNameInUse',
                                                                         'ObjectInstanceNameNotReserved',
                                                                         'ObjectClassNotPublished',
                                                                         'ObjectClassNotDefined',
                                                                         'SaveInProgress',
                                                                         'RestoreInProgress',
                                                                         'FederateNotExecutionMember',
                                                                         'NotConnected',
                                                                         'RTIinternalError']},
                                                       {   'group': None,
                                                           'language': 'cpp',
                                                           'params': 'ObjectClassHandle theClass',
                                                           'return_type': 'ObjectInstanceHandle',
                                                           'service': None,
                                                           'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                           'source_line': 492,
                                                           'throws': [   'ObjectClassNotPublished',
                                                                         'ObjectClassNotDefined',
                                                                         'SaveInProgress',
                                                                         'RestoreInProgress',
                                                                         'FederateNotExecutionMember',
                                                                         'NotConnected',
                                                                         'RTIinternalError']},
                                                       {   'group': None,
                                                           'language': 'cpp',
                                                           'params': 'ObjectClassHandle theClass, std::wstring const & '
                                                                     'theObjectInstanceName',
                                                           'return_type': 'ObjectInstanceHandle',
                                                           'service': None,
                                                           'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                           'source_line': 503,
                                                           'throws': [   'ObjectInstanceNameInUse',
                                                                         'ObjectInstanceNameNotReserved',
                                                                         'ObjectClassNotPublished',
                                                                         'ObjectClassNotDefined',
                                                                         'SaveInProgress',
                                                                         'RestoreInProgress',
                                                                         'FederateNotExecutionMember',
                                                                         'NotConnected',
                                                                         'RTIinternalError']}],
                         'registerObjectInstanceWithRegions': [   {   'group': 'Data Distribution Management',
                                                                      'language': 'java',
                                                                      'params': 'ObjectClassHandle theClass, '
                                                                                'AttributeSetRegionSetPairList '
                                                                                'attributesAndRegions',
                                                                      'return_type': 'ObjectInstanceHandle',
                                                                      'service': '9.5',
                                                                      'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                      'source_line': 1221,
                                                                      'throws': [   'InvalidRegionContext',
                                                                                    'RegionNotCreatedByThisFederate',
                                                                                    'InvalidRegion',
                                                                                    'AttributeNotPublished',
                                                                                    'ObjectClassNotPublished',
                                                                                    'AttributeNotDefined',
                                                                                    'ObjectClassNotDefined',
                                                                                    'SaveInProgress',
                                                                                    'RestoreInProgress',
                                                                                    'FederateNotExecutionMember',
                                                                                    'NotConnected',
                                                                                    'RTIinternalError']},
                                                                  {   'group': 'Data Distribution Management',
                                                                      'language': 'java',
                                                                      'params': 'ObjectClassHandle theClass, '
                                                                                'AttributeSetRegionSetPairList '
                                                                                'attributesAndRegions, String '
                                                                                'theObject',
                                                                      'return_type': 'ObjectInstanceHandle',
                                                                      'service': '9.5',
                                                                      'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                      'source_line': 1238,
                                                                      'throws': [   'ObjectInstanceNameInUse',
                                                                                    'ObjectInstanceNameNotReserved',
                                                                                    'InvalidRegionContext',
                                                                                    'RegionNotCreatedByThisFederate',
                                                                                    'InvalidRegion',
                                                                                    'AttributeNotPublished',
                                                                                    'ObjectClassNotPublished',
                                                                                    'AttributeNotDefined',
                                                                                    'ObjectClassNotDefined',
                                                                                    'SaveInProgress',
                                                                                    'RestoreInProgress',
                                                                                    'FederateNotExecutionMember',
                                                                                    'NotConnected',
                                                                                    'RTIinternalError']},
                                                                  {   'group': None,
                                                                      'language': 'cpp',
                                                                      'params': 'ObjectClassHandle theClass, '
                                                                                'AttributeHandleSetRegionHandleSetPairVector '
                                                                                'const & '
                                                                                'theAttributeHandleSetRegionHandleSetPairVector',
                                                                      'return_type': 'ObjectInstanceHandle',
                                                                      'service': None,
                                                                      'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                      'source_line': 1151,
                                                                      'throws': [   'InvalidRegionContext',
                                                                                    'RegionNotCreatedByThisFederate',
                                                                                    'InvalidRegion',
                                                                                    'AttributeNotPublished',
                                                                                    'ObjectClassNotPublished',
                                                                                    'AttributeNotDefined',
                                                                                    'ObjectClassNotDefined',
                                                                                    'SaveInProgress',
                                                                                    'RestoreInProgress',
                                                                                    'FederateNotExecutionMember',
                                                                                    'NotConnected',
                                                                                    'RTIinternalError']},
                                                                  {   'group': None,
                                                                      'language': 'cpp',
                                                                      'params': 'ObjectClassHandle theClass, '
                                                                                'AttributeHandleSetRegionHandleSetPairVector '
                                                                                'const & '
                                                                                'theAttributeHandleSetRegionHandleSetPairVector, '
                                                                                'std::wstring const & '
                                                                                'theObjectInstanceName',
                                                                      'return_type': 'ObjectInstanceHandle',
                                                                      'service': None,
                                                                      'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                      'source_line': 1169,
                                                                      'throws': [   'ObjectInstanceNameInUse',
                                                                                    'ObjectInstanceNameNotReserved',
                                                                                    'InvalidRegionContext',
                                                                                    'RegionNotCreatedByThisFederate',
                                                                                    'InvalidRegion',
                                                                                    'AttributeNotPublished',
                                                                                    'ObjectClassNotPublished',
                                                                                    'AttributeNotDefined',
                                                                                    'ObjectClassNotDefined',
                                                                                    'SaveInProgress',
                                                                                    'RestoreInProgress',
                                                                                    'FederateNotExecutionMember',
                                                                                    'NotConnected',
                                                                                    'RTIinternalError']}],
                         'releaseMultipleObjectInstanceName': [   {   'group': 'Object Management',
                                                                      'language': 'java',
                                                                      'params': 'Set<String> theObjectNames',
                                                                      'return_type': 'void',
                                                                      'service': '6.7',
                                                                      'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                      'source_line': 588,
                                                                      'throws': [   'ObjectInstanceNameNotReserved',
                                                                                    'SaveInProgress',
                                                                                    'RestoreInProgress',
                                                                                    'FederateNotExecutionMember',
                                                                                    'NotConnected',
                                                                                    'RTIinternalError']},
                                                                  {   'group': None,
                                                                      'language': 'cpp',
                                                                      'params': 'std::set<std::wstring> const & '
                                                                                'theObjectInstanceNames',
                                                                      'return_type': 'void',
                                                                      'service': None,
                                                                      'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                      'source_line': 481,
                                                                      'throws': [   'ObjectInstanceNameNotReserved',
                                                                                    'SaveInProgress',
                                                                                    'RestoreInProgress',
                                                                                    'FederateNotExecutionMember',
                                                                                    'NotConnected',
                                                                                    'RTIinternalError']}],
                         'releaseObjectInstanceName': [   {   'group': 'Object Management',
                                                              'language': 'java',
                                                              'params': 'String theObjectInstanceName',
                                                              'return_type': 'void',
                                                              'service': '6.4',
                                                              'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                              'source_line': 567,
                                                              'throws': [   'ObjectInstanceNameNotReserved',
                                                                            'SaveInProgress',
                                                                            'RestoreInProgress',
                                                                            'FederateNotExecutionMember',
                                                                            'NotConnected',
                                                                            'RTIinternalError']},
                                                          {   'group': None,
                                                              'language': 'cpp',
                                                              'params': 'std::wstring const & theObjectInstanceName',
                                                              'return_type': 'void',
                                                              'service': None,
                                                              'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                              'source_line': 458,
                                                              'throws': [   'ObjectInstanceNameNotReserved',
                                                                            'SaveInProgress',
                                                                            'RestoreInProgress',
                                                                            'FederateNotExecutionMember',
                                                                            'NotConnected',
                                                                            'RTIinternalError']}],
                         'requestAttributeTransportationTypeChange': [   {   'group': 'Object Management',
                                                                             'language': 'java',
                                                                             'params': 'ObjectInstanceHandle '
                                                                                       'theObject, AttributeHandleSet '
                                                                                       'theAttributes, '
                                                                                       'TransportationTypeHandle '
                                                                                       'theType',
                                                                             'return_type': 'void',
                                                                             'service': '6.23',
                                                                             'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                             'source_line': 747,
                                                                             'throws': [   'AttributeAlreadyBeingChanged',
                                                                                           'AttributeNotOwned',
                                                                                           'AttributeNotDefined',
                                                                                           'ObjectInstanceNotKnown',
                                                                                           'InvalidTransportationType',
                                                                                           'SaveInProgress',
                                                                                           'RestoreInProgress',
                                                                                           'FederateNotExecutionMember',
                                                                                           'NotConnected',
                                                                                           'RTIinternalError']},
                                                                         {   'group': None,
                                                                             'language': 'cpp',
                                                                             'params': 'ObjectInstanceHandle '
                                                                                       'theObject, AttributeHandleSet '
                                                                                       'const & theAttributes, '
                                                                                       'TransportationType theType',
                                                                             'return_type': 'void',
                                                                             'service': None,
                                                                             'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                             'source_line': 647,
                                                                             'throws': [   'AttributeAlreadyBeingChanged',
                                                                                           'AttributeNotOwned',
                                                                                           'AttributeNotDefined',
                                                                                           'ObjectInstanceNotKnown',
                                                                                           'InvalidTransportationType',
                                                                                           'SaveInProgress',
                                                                                           'RestoreInProgress',
                                                                                           'FederateNotExecutionMember',
                                                                                           'NotConnected',
                                                                                           'RTIinternalError']}],
                         'requestAttributeValueUpdate': [   {   'group': 'Object Management',
                                                                'language': 'java',
                                                                'params': 'ObjectInstanceHandle theObject, '
                                                                          'AttributeHandleSet theAttributes, byte[] '
                                                                          'userSuppliedTag',
                                                                'return_type': 'void',
                                                                'service': '6.19',
                                                                'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                'source_line': 721,
                                                                'throws': [   'AttributeNotDefined',
                                                                              'ObjectInstanceNotKnown',
                                                                              'SaveInProgress',
                                                                              'RestoreInProgress',
                                                                              'FederateNotExecutionMember',
                                                                              'NotConnected',
                                                                              'RTIinternalError']},
                                                            {   'group': 'Object Management',
                                                                'language': 'java',
                                                                'params': 'ObjectClassHandle theClass, '
                                                                          'AttributeHandleSet theAttributes, byte[] '
                                                                          'userSuppliedTag',
                                                                'return_type': 'void',
                                                                'service': '6.19',
                                                                'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                'source_line': 734,
                                                                'throws': [   'AttributeNotDefined',
                                                                              'ObjectClassNotDefined',
                                                                              'SaveInProgress',
                                                                              'RestoreInProgress',
                                                                              'FederateNotExecutionMember',
                                                                              'NotConnected',
                                                                              'RTIinternalError']},
                                                            {   'group': None,
                                                                'language': 'cpp',
                                                                'params': 'ObjectInstanceHandle theObject, '
                                                                          'AttributeHandleSet const & theAttributes, '
                                                                          'VariableLengthData const & '
                                                                          'theUserSuppliedTag',
                                                                'return_type': 'void',
                                                                'service': None,
                                                                'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                'source_line': 620,
                                                                'throws': [   'AttributeNotDefined',
                                                                              'ObjectInstanceNotKnown',
                                                                              'SaveInProgress',
                                                                              'RestoreInProgress',
                                                                              'FederateNotExecutionMember',
                                                                              'NotConnected',
                                                                              'RTIinternalError']},
                                                            {   'group': None,
                                                                'language': 'cpp',
                                                                'params': 'ObjectClassHandle theClass, '
                                                                          'AttributeHandleSet const & theAttributes, '
                                                                          'VariableLengthData const & '
                                                                          'theUserSuppliedTag',
                                                                'return_type': 'void',
                                                                'service': None,
                                                                'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                'source_line': 633,
                                                                'throws': [   'AttributeNotDefined',
                                                                              'ObjectClassNotDefined',
                                                                              'SaveInProgress',
                                                                              'RestoreInProgress',
                                                                              'FederateNotExecutionMember',
                                                                              'NotConnected',
                                                                              'RTIinternalError']}],
                         'requestAttributeValueUpdateWithRegions': [   {   'group': 'Data Distribution Management',
                                                                           'language': 'java',
                                                                           'params': 'ObjectClassHandle theClass, '
                                                                                     'AttributeSetRegionSetPairList '
                                                                                     'attributesAndRegions, byte[] '
                                                                                     'userSuppliedTag',
                                                                           'return_type': 'void',
                                                                           'service': '9.13',
                                                                           'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                           'source_line': 1446,
                                                                           'throws': [   'InvalidRegionContext',
                                                                                         'RegionNotCreatedByThisFederate',
                                                                                         'InvalidRegion',
                                                                                         'AttributeNotDefined',
                                                                                         'ObjectClassNotDefined',
                                                                                         'SaveInProgress',
                                                                                         'RestoreInProgress',
                                                                                         'FederateNotExecutionMember',
                                                                                         'NotConnected',
                                                                                         'RTIinternalError']},
                                                                       {   'group': None,
                                                                           'language': 'cpp',
                                                                           'params': 'ObjectClassHandle theClass, '
                                                                                     'AttributeHandleSetRegionHandleSetPairVector '
                                                                                     'const & theSet, '
                                                                                     'VariableLengthData const & '
                                                                                     'theUserSuppliedTag',
                                                                           'return_type': 'void',
                                                                           'service': None,
                                                                           'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                           'source_line': 1331,
                                                                           'throws': [   'InvalidRegionContext',
                                                                                         'RegionNotCreatedByThisFederate',
                                                                                         'InvalidRegion',
                                                                                         'AttributeNotDefined',
                                                                                         'ObjectClassNotDefined',
                                                                                         'SaveInProgress',
                                                                                         'RestoreInProgress',
                                                                                         'FederateNotExecutionMember',
                                                                                         'NotConnected',
                                                                                         'RTIinternalError']}],
                         'requestFederationRestore': [   {   'group': 'Federation Management',
                                                             'language': 'java',
                                                             'params': 'String label',
                                                             'return_type': 'void',
                                                             'service': '4.24',
                                                             'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                             'source_line': 343,
                                                             'throws': [   'SaveInProgress',
                                                                           'RestoreInProgress',
                                                                           'FederateNotExecutionMember',
                                                                           'NotConnected',
                                                                           'RTIinternalError']},
                                                         {   'group': None,
                                                             'language': 'cpp',
                                                             'params': 'std::wstring const & label',
                                                             'return_type': 'void',
                                                             'service': None,
                                                             'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                             'source_line': 273,
                                                             'throws': [   'SaveInProgress',
                                                                           'RestoreInProgress',
                                                                           'FederateNotExecutionMember',
                                                                           'NotConnected',
                                                                           'RTIinternalError']}],
                         'requestFederationSave': [   {   'group': 'Federation Management',
                                                          'language': 'java',
                                                          'params': 'String label',
                                                          'return_type': 'void',
                                                          'service': '4.16',
                                                          'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                          'source_line': 278,
                                                          'throws': [   'SaveInProgress',
                                                                        'RestoreInProgress',
                                                                        'FederateNotExecutionMember',
                                                                        'NotConnected',
                                                                        'RTIinternalError']},
                                                      {   'group': 'Federation Management',
                                                          'language': 'java',
                                                          'params': 'String label, LogicalTime theTime',
                                                          'return_type': 'void',
                                                          'service': '4.16',
                                                          'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                          'source_line': 287,
                                                          'throws': [   'LogicalTimeAlreadyPassed',
                                                                        'InvalidLogicalTime',
                                                                        'FederateUnableToUseTime',
                                                                        'SaveInProgress',
                                                                        'RestoreInProgress',
                                                                        'FederateNotExecutionMember',
                                                                        'NotConnected',
                                                                        'RTIinternalError']},
                                                      {   'group': None,
                                                          'language': 'cpp',
                                                          'params': 'std::wstring const & label',
                                                          'return_type': 'void',
                                                          'service': None,
                                                          'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                          'source_line': 208,
                                                          'throws': [   'SaveInProgress',
                                                                        'RestoreInProgress',
                                                                        'FederateNotExecutionMember',
                                                                        'NotConnected',
                                                                        'RTIinternalError']},
                                                      {   'group': None,
                                                          'language': 'cpp',
                                                          'params': 'std::wstring const & label, LogicalTime const & '
                                                                    'theTime',
                                                          'return_type': 'void',
                                                          'service': None,
                                                          'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                          'source_line': 217,
                                                          'throws': [   'LogicalTimeAlreadyPassed',
                                                                        'InvalidLogicalTime',
                                                                        'FederateUnableToUseTime',
                                                                        'SaveInProgress',
                                                                        'RestoreInProgress',
                                                                        'FederateNotExecutionMember',
                                                                        'NotConnected',
                                                                        'RTIinternalError']}],
                         'requestInteractionTransportationTypeChange': [   {   'group': 'Object Management',
                                                                               'language': 'java',
                                                                               'params': 'InteractionClassHandle '
                                                                                         'theClass, '
                                                                                         'TransportationTypeHandle '
                                                                                         'theType',
                                                                               'return_type': 'void',
                                                                               'service': '6.27',
                                                                               'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                               'source_line': 775,
                                                                               'throws': [   'InteractionClassAlreadyBeingChanged',
                                                                                             'InteractionClassNotPublished',
                                                                                             'InteractionClassNotDefined',
                                                                                             'InvalidTransportationType',
                                                                                             'SaveInProgress',
                                                                                             'RestoreInProgress',
                                                                                             'FederateNotExecutionMember',
                                                                                             'NotConnected',
                                                                                             'RTIinternalError']},
                                                                           {   'group': None,
                                                                               'language': 'cpp',
                                                                               'params': 'InteractionClassHandle '
                                                                                         'theClass, TransportationType '
                                                                                         'theType',
                                                                               'return_type': 'void',
                                                                               'service': None,
                                                                               'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                               'source_line': 677,
                                                                               'throws': [   'InteractionClassAlreadyBeingChanged',
                                                                                             'InteractionClassNotPublished',
                                                                                             'InteractionClassNotDefined',
                                                                                             'InvalidTransportationType',
                                                                                             'SaveInProgress',
                                                                                             'RestoreInProgress',
                                                                                             'FederateNotExecutionMember',
                                                                                             'NotConnected',
                                                                                             'RTIinternalError']}],
                         'reserveMultipleObjectInstanceName': [   {   'group': 'Object Management',
                                                                      'language': 'java',
                                                                      'params': 'Set<String> theObjectNames',
                                                                      'return_type': 'void',
                                                                      'service': '6.5',
                                                                      'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                      'source_line': 577,
                                                                      'throws': [   'IllegalName',
                                                                                    'NameSetWasEmpty',
                                                                                    'SaveInProgress',
                                                                                    'RestoreInProgress',
                                                                                    'FederateNotExecutionMember',
                                                                                    'NotConnected',
                                                                                    'RTIinternalError']},
                                                                  {   'group': None,
                                                                      'language': 'cpp',
                                                                      'params': 'std::set<std::wstring> const & '
                                                                                'theObjectInstanceNames',
                                                                      'return_type': 'void',
                                                                      'service': None,
                                                                      'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                      'source_line': 469,
                                                                      'throws': [   'IllegalName',
                                                                                    'NameSetWasEmpty',
                                                                                    'SaveInProgress',
                                                                                    'RestoreInProgress',
                                                                                    'FederateNotExecutionMember',
                                                                                    'NotConnected',
                                                                                    'RTIinternalError']}],
                         'reserveObjectInstanceName': [   {   'group': 'Object Management',
                                                              'language': 'java',
                                                              'params': 'String theObjectName',
                                                              'return_type': 'void',
                                                              'service': '6.2',
                                                              'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                              'source_line': 557,
                                                              'throws': [   'IllegalName',
                                                                            'SaveInProgress',
                                                                            'RestoreInProgress',
                                                                            'FederateNotExecutionMember',
                                                                            'NotConnected',
                                                                            'RTIinternalError']},
                                                          {   'group': None,
                                                              'language': 'cpp',
                                                              'params': 'std::wstring const & theObjectInstanceName',
                                                              'return_type': 'void',
                                                              'service': None,
                                                              'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                              'source_line': 447,
                                                              'throws': [   'IllegalName',
                                                                            'SaveInProgress',
                                                                            'RestoreInProgress',
                                                                            'FederateNotExecutionMember',
                                                                            'NotConnected',
                                                                            'RTIinternalError']}],
                         'resignFederationExecution': [   {   'group': 'Federation Management',
                                                              'language': 'java',
                                                              'params': 'ResignAction resignAction',
                                                              'return_type': 'void',
                                                              'service': '4.10',
                                                              'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                              'source_line': 224,
                                                              'throws': [   'InvalidResignAction',
                                                                            'OwnershipAcquisitionPending',
                                                                            'FederateOwnsAttributes',
                                                                            'FederateNotExecutionMember',
                                                                            'NotConnected',
                                                                            'CallNotAllowedFromWithinCallback',
                                                                            'RTIinternalError']},
                                                          {   'group': None,
                                                              'language': 'cpp',
                                                              'params': 'ResignAction resignAction',
                                                              'return_type': 'void',
                                                              'service': None,
                                                              'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                              'source_line': 161,
                                                              'throws': [   'InvalidResignAction',
                                                                            'OwnershipAcquisitionPending',
                                                                            'FederateOwnsAttributes',
                                                                            'FederateNotExecutionMember',
                                                                            'NotConnected',
                                                                            'CallNotAllowedFromWithinCallback',
                                                                            'RTIinternalError']}],
                         'retract': [   {   'group': 'Time Management',
                                            'language': 'java',
                                            'params': 'MessageRetractionHandle theHandle',
                                            'return_type': 'void',
                                            'service': '8.21',
                                            'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                            'source_line': 1146,
                                            'throws': [   'MessageCanNoLongerBeRetracted',
                                                          'InvalidMessageRetractionHandle',
                                                          'TimeRegulationIsNotEnabled',
                                                          'SaveInProgress',
                                                          'RestoreInProgress',
                                                          'FederateNotExecutionMember',
                                                          'NotConnected',
                                                          'RTIinternalError']},
                                        {   'group': None,
                                            'language': 'cpp',
                                            'params': 'MessageRetractionHandle theHandle',
                                            'return_type': 'void',
                                            'service': None,
                                            'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                            'source_line': 1070,
                                            'throws': [   'MessageCanNoLongerBeRetracted',
                                                          'InvalidMessageRetractionHandle',
                                                          'TimeRegulationIsNotEnabled',
                                                          'SaveInProgress',
                                                          'RestoreInProgress',
                                                          'FederateNotExecutionMember',
                                                          'NotConnected',
                                                          'RTIinternalError']}],
                         'sendInteraction': [   {   'group': 'Object Management',
                                                    'language': 'java',
                                                    'params': 'InteractionClassHandle theInteraction, '
                                                              'ParameterHandleValueMap theParameters, byte[] '
                                                              'userSuppliedTag',
                                                    'return_type': 'void',
                                                    'service': '6.12',
                                                    'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                    'source_line': 653,
                                                    'throws': [   'InteractionClassNotPublished',
                                                                  'InteractionParameterNotDefined',
                                                                  'InteractionClassNotDefined',
                                                                  'SaveInProgress',
                                                                  'RestoreInProgress',
                                                                  'FederateNotExecutionMember',
                                                                  'NotConnected',
                                                                  'RTIinternalError']},
                                                {   'group': 'Object Management',
                                                    'language': 'java',
                                                    'params': 'InteractionClassHandle theInteraction, '
                                                              'ParameterHandleValueMap theParameters, byte[] '
                                                              'userSuppliedTag, LogicalTime theTime',
                                                    'return_type': 'MessageRetractionReturn',
                                                    'service': '6.12',
                                                    'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                    'source_line': 667,
                                                    'throws': [   'InvalidLogicalTime',
                                                                  'InteractionClassNotPublished',
                                                                  'InteractionParameterNotDefined',
                                                                  'InteractionClassNotDefined',
                                                                  'SaveInProgress',
                                                                  'RestoreInProgress',
                                                                  'FederateNotExecutionMember',
                                                                  'NotConnected',
                                                                  'RTIinternalError']},
                                                {   'group': None,
                                                    'language': 'cpp',
                                                    'params': 'InteractionClassHandle theInteraction, '
                                                              'ParameterHandleValueMap const & theParameterValues, '
                                                              'VariableLengthData const & theUserSuppliedTag',
                                                    'return_type': 'void',
                                                    'service': None,
                                                    'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                    'source_line': 549,
                                                    'throws': [   'InteractionClassNotPublished',
                                                                  'InteractionParameterNotDefined',
                                                                  'InteractionClassNotDefined',
                                                                  'SaveInProgress',
                                                                  'RestoreInProgress',
                                                                  'FederateNotExecutionMember',
                                                                  'NotConnected',
                                                                  'RTIinternalError']},
                                                {   'group': None,
                                                    'language': 'cpp',
                                                    'params': 'InteractionClassHandle theInteraction, '
                                                              'ParameterHandleValueMap const & theParameterValues, '
                                                              'VariableLengthData const & theUserSuppliedTag, '
                                                              'LogicalTime const & theTime',
                                                    'return_type': 'MessageRetractionHandle',
                                                    'service': None,
                                                    'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                    'source_line': 563,
                                                    'throws': [   'InvalidLogicalTime',
                                                                  'InteractionClassNotPublished',
                                                                  'InteractionParameterNotDefined',
                                                                  'InteractionClassNotDefined',
                                                                  'SaveInProgress',
                                                                  'RestoreInProgress',
                                                                  'FederateNotExecutionMember',
                                                                  'NotConnected',
                                                                  'RTIinternalError']}],
                         'sendInteractionWithRegions': [   {   'group': 'Data Distribution Management',
                                                               'language': 'java',
                                                               'params': 'InteractionClassHandle theInteraction, '
                                                                         'ParameterHandleValueMap theParameters, '
                                                                         'RegionHandleSet regions, byte[] '
                                                                         'userSuppliedTag',
                                                               'return_type': 'void',
                                                               'service': '9.12',
                                                               'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                               'source_line': 1408,
                                                               'throws': [   'InvalidRegionContext',
                                                                             'RegionNotCreatedByThisFederate',
                                                                             'InvalidRegion',
                                                                             'InteractionClassNotPublished',
                                                                             'InteractionParameterNotDefined',
                                                                             'InteractionClassNotDefined',
                                                                             'SaveInProgress',
                                                                             'RestoreInProgress',
                                                                             'FederateNotExecutionMember',
                                                                             'NotConnected',
                                                                             'RTIinternalError']},
                                                           {   'group': 'Data Distribution Management',
                                                               'language': 'java',
                                                               'params': 'InteractionClassHandle theInteraction, '
                                                                         'ParameterHandleValueMap theParameters, '
                                                                         'RegionHandleSet regions, byte[] '
                                                                         'userSuppliedTag, LogicalTime theTime',
                                                               'return_type': 'MessageRetractionReturn',
                                                               'service': '9.12',
                                                               'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                               'source_line': 1426,
                                                               'throws': [   'InvalidLogicalTime',
                                                                             'InvalidRegionContext',
                                                                             'RegionNotCreatedByThisFederate',
                                                                             'InvalidRegion',
                                                                             'InteractionClassNotPublished',
                                                                             'InteractionParameterNotDefined',
                                                                             'InteractionClassNotDefined',
                                                                             'SaveInProgress',
                                                                             'RestoreInProgress',
                                                                             'FederateNotExecutionMember',
                                                                             'NotConnected',
                                                                             'RTIinternalError']},
                                                           {   'group': None,
                                                               'language': 'cpp',
                                                               'params': 'InteractionClassHandle theInteraction, '
                                                                         'ParameterHandleValueMap const & '
                                                                         'theParameterValues, RegionHandleSet const & '
                                                                         'theRegionHandleSet, VariableLengthData const '
                                                                         '& theUserSuppliedTag',
                                                               'return_type': 'void',
                                                               'service': None,
                                                               'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                               'source_line': 1292,
                                                               'throws': [   'InvalidRegionContext',
                                                                             'RegionNotCreatedByThisFederate',
                                                                             'InvalidRegion',
                                                                             'InteractionClassNotPublished',
                                                                             'InteractionParameterNotDefined',
                                                                             'InteractionClassNotDefined',
                                                                             'SaveInProgress',
                                                                             'RestoreInProgress',
                                                                             'FederateNotExecutionMember',
                                                                             'NotConnected',
                                                                             'RTIinternalError']},
                                                           {   'group': None,
                                                               'language': 'cpp',
                                                               'params': 'InteractionClassHandle theInteraction, '
                                                                         'ParameterHandleValueMap const & '
                                                                         'theParameterValues, RegionHandleSet const & '
                                                                         'theRegionHandleSet, VariableLengthData const '
                                                                         '& theUserSuppliedTag, LogicalTime const & '
                                                                         'theTime',
                                                               'return_type': 'MessageRetractionHandle',
                                                               'service': None,
                                                               'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                               'source_line': 1310,
                                                               'throws': [   'InvalidLogicalTime',
                                                                             'InvalidRegionContext',
                                                                             'RegionNotCreatedByThisFederate',
                                                                             'InvalidRegion',
                                                                             'InteractionClassNotPublished',
                                                                             'InteractionParameterNotDefined',
                                                                             'InteractionClassNotDefined',
                                                                             'SaveInProgress',
                                                                             'RestoreInProgress',
                                                                             'FederateNotExecutionMember',
                                                                             'NotConnected',
                                                                             'RTIinternalError']}],
                         'setAutomaticResignDirective': [   {   'group': 'Support Services',
                                                                'language': 'java',
                                                                'params': 'ResignAction resignAction',
                                                                'return_type': 'void',
                                                                'service': '10.3',
                                                                'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                'source_line': 1473,
                                                                'throws': [   'InvalidResignAction',
                                                                              'FederateNotExecutionMember',
                                                                              'NotConnected',
                                                                              'RTIinternalError']},
                                                            {   'group': None,
                                                                'language': 'cpp',
                                                                'params': 'ResignAction resignAction',
                                                                'return_type': 'void',
                                                                'service': None,
                                                                'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                'source_line': 1359,
                                                                'throws': [   'InvalidResignAction',
                                                                              'FederateNotExecutionMember',
                                                                              'NotConnected',
                                                                              'RTIinternalError']}],
                         'setRangeBounds': [   {   'group': 'Support Services',
                                                   'language': 'java',
                                                   'params': 'RegionHandle region, DimensionHandle dimension, '
                                                             'RangeBounds bounds',
                                                   'return_type': 'void',
                                                   'service': '10.30',
                                                   'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                   'source_line': 1711,
                                                   'throws': [   'InvalidRangeBound',
                                                                 'RegionDoesNotContainSpecifiedDimension',
                                                                 'RegionNotCreatedByThisFederate',
                                                                 'InvalidRegion',
                                                                 'SaveInProgress',
                                                                 'RestoreInProgress',
                                                                 'FederateNotExecutionMember',
                                                                 'NotConnected',
                                                                 'RTIinternalError']},
                                               {   'group': None,
                                                   'language': 'cpp',
                                                   'params': 'RegionHandle theRegionHandle, DimensionHandle '
                                                             'theDimensionHandle, RangeBounds const & theRangeBounds',
                                                   'return_type': 'void',
                                                   'service': None,
                                                   'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                   'source_line': 1624,
                                                   'throws': [   'InvalidRangeBound',
                                                                 'RegionDoesNotContainSpecifiedDimension',
                                                                 'RegionNotCreatedByThisFederate',
                                                                 'InvalidRegion',
                                                                 'SaveInProgress',
                                                                 'RestoreInProgress',
                                                                 'FederateNotExecutionMember',
                                                                 'NotConnected',
                                                                 'RTIinternalError']}],
                         'subscribeInteractionClass': [   {   'group': 'Declaration Management',
                                                              'language': 'java',
                                                              'params': 'InteractionClassHandle theClass',
                                                              'return_type': 'void',
                                                              'service': '5.8',
                                                              'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                              'source_line': 521,
                                                              'throws': [   'FederateServiceInvocationsAreBeingReportedViaMOM',
                                                                            'InteractionClassNotDefined',
                                                                            'SaveInProgress',
                                                                            'RestoreInProgress',
                                                                            'FederateNotExecutionMember',
                                                                            'NotConnected',
                                                                            'RTIinternalError']},
                                                          {   'group': None,
                                                              'language': 'cpp',
                                                              'params': 'InteractionClassHandle theClass, bool active '
                                                                        '= true',
                                                              'return_type': 'void',
                                                              'service': None,
                                                              'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                              'source_line': 419,
                                                              'throws': [   'FederateServiceInvocationsAreBeingReportedViaMOM',
                                                                            'InteractionClassNotDefined',
                                                                            'SaveInProgress',
                                                                            'RestoreInProgress',
                                                                            'FederateNotExecutionMember',
                                                                            'NotConnected',
                                                                            'RTIinternalError']}],
                         'subscribeInteractionClassPassively': [   {   'group': 'Declaration Management',
                                                                       'language': 'java',
                                                                       'params': 'InteractionClassHandle theClass',
                                                                       'return_type': 'void',
                                                                       'service': '5.8',
                                                                       'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                       'source_line': 532,
                                                                       'throws': [   'FederateServiceInvocationsAreBeingReportedViaMOM',
                                                                                     'InteractionClassNotDefined',
                                                                                     'SaveInProgress',
                                                                                     'RestoreInProgress',
                                                                                     'FederateNotExecutionMember',
                                                                                     'NotConnected',
                                                                                     'RTIinternalError']}],
                         'subscribeInteractionClassPassivelyWithRegions': [   {   'group': 'Data Distribution '
                                                                                           'Management',
                                                                                  'language': 'java',
                                                                                  'params': 'InteractionClassHandle '
                                                                                            'theClass, RegionHandleSet '
                                                                                            'regions',
                                                                                  'return_type': 'void',
                                                                                  'service': '9.10',
                                                                                  'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                                  'source_line': 1380,
                                                                                  'throws': [   'FederateServiceInvocationsAreBeingReportedViaMOM',
                                                                                                'InvalidRegionContext',
                                                                                                'RegionNotCreatedByThisFederate',
                                                                                                'InvalidRegion',
                                                                                                'InteractionClassNotDefined',
                                                                                                'SaveInProgress',
                                                                                                'RestoreInProgress',
                                                                                                'FederateNotExecutionMember',
                                                                                                'NotConnected',
                                                                                                'RTIinternalError']}],
                         'subscribeInteractionClassWithRegions': [   {   'group': 'Data Distribution Management',
                                                                         'language': 'java',
                                                                         'params': 'InteractionClassHandle theClass, '
                                                                                   'RegionHandleSet regions',
                                                                         'return_type': 'void',
                                                                         'service': '9.10',
                                                                         'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                         'source_line': 1365,
                                                                         'throws': [   'FederateServiceInvocationsAreBeingReportedViaMOM',
                                                                                       'InvalidRegionContext',
                                                                                       'RegionNotCreatedByThisFederate',
                                                                                       'InvalidRegion',
                                                                                       'InteractionClassNotDefined',
                                                                                       'SaveInProgress',
                                                                                       'RestoreInProgress',
                                                                                       'FederateNotExecutionMember',
                                                                                       'NotConnected',
                                                                                       'RTIinternalError']},
                                                                     {   'group': None,
                                                                         'language': 'cpp',
                                                                         'params': 'InteractionClassHandle theClass, '
                                                                                   'RegionHandleSet const & '
                                                                                   'theRegionHandleSet, bool active = '
                                                                                   'true',
                                                                         'return_type': 'void',
                                                                         'service': None,
                                                                         'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                         'source_line': 1261,
                                                                         'throws': [   'FederateServiceInvocationsAreBeingReportedViaMOM',
                                                                                       'InvalidRegionContext',
                                                                                       'RegionNotCreatedByThisFederate',
                                                                                       'InvalidRegion',
                                                                                       'InteractionClassNotDefined',
                                                                                       'SaveInProgress',
                                                                                       'RestoreInProgress',
                                                                                       'FederateNotExecutionMember',
                                                                                       'NotConnected',
                                                                                       'RTIinternalError']}],
                         'subscribeObjectClassAttributes': [   {   'group': 'Declaration Management',
                                                                   'language': 'java',
                                                                   'params': 'ObjectClassHandle theClass, '
                                                                             'AttributeHandleSet attributeList',
                                                                   'return_type': 'void',
                                                                   'service': '5.6',
                                                                   'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                   'source_line': 447,
                                                                   'throws': [   'AttributeNotDefined',
                                                                                 'ObjectClassNotDefined',
                                                                                 'SaveInProgress',
                                                                                 'RestoreInProgress',
                                                                                 'FederateNotExecutionMember',
                                                                                 'NotConnected',
                                                                                 'RTIinternalError']},
                                                               {   'group': 'Declaration Management',
                                                                   'language': 'java',
                                                                   'params': 'ObjectClassHandle theClass, '
                                                                             'AttributeHandleSet attributeList, String '
                                                                             'updateRateDesignator',
                                                                   'return_type': 'void',
                                                                   'service': '5.6',
                                                                   'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                   'source_line': 459,
                                                                   'throws': [   'AttributeNotDefined',
                                                                                 'ObjectClassNotDefined',
                                                                                 'InvalidUpdateRateDesignator',
                                                                                 'SaveInProgress',
                                                                                 'RestoreInProgress',
                                                                                 'FederateNotExecutionMember',
                                                                                 'NotConnected',
                                                                                 'RTIinternalError']},
                                                               {   'group': None,
                                                                   'language': 'cpp',
                                                                   'params': 'ObjectClassHandle theClass, '
                                                                             'AttributeHandleSet const & '
                                                                             'attributeList, bool active = true, '
                                                                             'std::wstring const & '
                                                                             'updateRateDesignator = L""',
                                                                   'return_type': 'void',
                                                                   'service': None,
                                                                   'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                   'source_line': 380,
                                                                   'throws': [   'AttributeNotDefined',
                                                                                 'ObjectClassNotDefined',
                                                                                 'InvalidUpdateRateDesignator',
                                                                                 'SaveInProgress',
                                                                                 'RestoreInProgress',
                                                                                 'FederateNotExecutionMember',
                                                                                 'NotConnected',
                                                                                 'RTIinternalError']}],
                         'subscribeObjectClassAttributesPassively': [   {   'group': 'Declaration Management',
                                                                            'language': 'java',
                                                                            'params': 'ObjectClassHandle theClass, '
                                                                                      'AttributeHandleSet '
                                                                                      'attributeList',
                                                                            'return_type': 'void',
                                                                            'service': '5.6',
                                                                            'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                            'source_line': 473,
                                                                            'throws': [   'AttributeNotDefined',
                                                                                          'ObjectClassNotDefined',
                                                                                          'SaveInProgress',
                                                                                          'RestoreInProgress',
                                                                                          'FederateNotExecutionMember',
                                                                                          'NotConnected',
                                                                                          'RTIinternalError']},
                                                                        {   'group': 'Declaration Management',
                                                                            'language': 'java',
                                                                            'params': 'ObjectClassHandle theClass, '
                                                                                      'AttributeHandleSet '
                                                                                      'attributeList, String '
                                                                                      'updateRateDesignator',
                                                                            'return_type': 'void',
                                                                            'service': '5.6',
                                                                            'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                            'source_line': 485,
                                                                            'throws': [   'AttributeNotDefined',
                                                                                          'ObjectClassNotDefined',
                                                                                          'InvalidUpdateRateDesignator',
                                                                                          'SaveInProgress',
                                                                                          'RestoreInProgress',
                                                                                          'FederateNotExecutionMember',
                                                                                          'NotConnected',
                                                                                          'RTIinternalError']}],
                         'subscribeObjectClassAttributesPassivelyWithRegions': [   {   'group': 'Data Distribution '
                                                                                                'Management',
                                                                                       'language': 'java',
                                                                                       'params': 'ObjectClassHandle '
                                                                                                 'theClass, '
                                                                                                 'AttributeSetRegionSetPairList '
                                                                                                 'attributesAndRegions',
                                                                                       'return_type': 'void',
                                                                                       'service': '9.8',
                                                                                       'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                                       'source_line': 1319,
                                                                                       'throws': [   'InvalidRegionContext',
                                                                                                     'RegionNotCreatedByThisFederate',
                                                                                                     'InvalidRegion',
                                                                                                     'AttributeNotDefined',
                                                                                                     'ObjectClassNotDefined',
                                                                                                     'SaveInProgress',
                                                                                                     'RestoreInProgress',
                                                                                                     'FederateNotExecutionMember',
                                                                                                     'NotConnected',
                                                                                                     'RTIinternalError']},
                                                                                   {   'group': 'Data Distribution '
                                                                                                'Management',
                                                                                       'language': 'java',
                                                                                       'params': 'ObjectClassHandle '
                                                                                                 'theClass, '
                                                                                                 'AttributeSetRegionSetPairList '
                                                                                                 'attributesAndRegions, '
                                                                                                 'String '
                                                                                                 'updateRateDesignator',
                                                                                       'return_type': 'void',
                                                                                       'service': '9.8',
                                                                                       'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                                       'source_line': 1334,
                                                                                       'throws': [   'InvalidRegionContext',
                                                                                                     'RegionNotCreatedByThisFederate',
                                                                                                     'InvalidRegion',
                                                                                                     'AttributeNotDefined',
                                                                                                     'ObjectClassNotDefined',
                                                                                                     'InvalidUpdateRateDesignator',
                                                                                                     'SaveInProgress',
                                                                                                     'RestoreInProgress',
                                                                                                     'FederateNotExecutionMember',
                                                                                                     'NotConnected',
                                                                                                     'RTIinternalError']}],
                         'subscribeObjectClassAttributesWithRegions': [   {   'group': 'Data Distribution Management',
                                                                              'language': 'java',
                                                                              'params': 'ObjectClassHandle theClass, '
                                                                                        'AttributeSetRegionSetPairList '
                                                                                        'attributesAndRegions',
                                                                              'return_type': 'void',
                                                                              'service': '9.8',
                                                                              'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                              'source_line': 1287,
                                                                              'throws': [   'InvalidRegionContext',
                                                                                            'RegionNotCreatedByThisFederate',
                                                                                            'InvalidRegion',
                                                                                            'AttributeNotDefined',
                                                                                            'ObjectClassNotDefined',
                                                                                            'SaveInProgress',
                                                                                            'RestoreInProgress',
                                                                                            'FederateNotExecutionMember',
                                                                                            'NotConnected',
                                                                                            'RTIinternalError']},
                                                                          {   'group': 'Data Distribution Management',
                                                                              'language': 'java',
                                                                              'params': 'ObjectClassHandle theClass, '
                                                                                        'AttributeSetRegionSetPairList '
                                                                                        'attributesAndRegions, String '
                                                                                        'updateRateDesignator',
                                                                              'return_type': 'void',
                                                                              'service': '9.8',
                                                                              'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                              'source_line': 1302,
                                                                              'throws': [   'InvalidRegionContext',
                                                                                            'RegionNotCreatedByThisFederate',
                                                                                            'InvalidRegion',
                                                                                            'AttributeNotDefined',
                                                                                            'ObjectClassNotDefined',
                                                                                            'InvalidUpdateRateDesignator',
                                                                                            'SaveInProgress',
                                                                                            'RestoreInProgress',
                                                                                            'FederateNotExecutionMember',
                                                                                            'NotConnected',
                                                                                            'RTIinternalError']},
                                                                          {   'group': None,
                                                                              'language': 'cpp',
                                                                              'params': 'ObjectClassHandle theClass, '
                                                                                        'AttributeHandleSetRegionHandleSetPairVector '
                                                                                        'const & '
                                                                                        'theAttributeHandleSetRegionHandleSetPairVector, '
                                                                                        'bool active = true, '
                                                                                        'std::wstring const & '
                                                                                        'updateRateDesignator = L""',
                                                                              'return_type': 'void',
                                                                              'service': None,
                                                                              'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                              'source_line': 1224,
                                                                              'throws': [   'InvalidRegionContext',
                                                                                            'RegionNotCreatedByThisFederate',
                                                                                            'InvalidRegion',
                                                                                            'AttributeNotDefined',
                                                                                            'ObjectClassNotDefined',
                                                                                            'InvalidUpdateRateDesignator',
                                                                                            'SaveInProgress',
                                                                                            'RestoreInProgress',
                                                                                            'FederateNotExecutionMember',
                                                                                            'NotConnected',
                                                                                            'RTIinternalError']}],
                         'synchronizationPointAchieved': [   {   'group': 'Federation Management',
                                                                 'language': 'java',
                                                                 'params': 'String synchronizationPointLabel',
                                                                 'return_type': 'void',
                                                                 'service': '4.14',
                                                                 'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                 'source_line': 257,
                                                                 'throws': [   'SynchronizationPointLabelNotAnnounced',
                                                                               'SaveInProgress',
                                                                               'RestoreInProgress',
                                                                               'FederateNotExecutionMember',
                                                                               'NotConnected',
                                                                               'RTIinternalError']},
                                                             {   'group': 'Federation Management',
                                                                 'language': 'java',
                                                                 'params': 'String synchronizationPointLabel, boolean '
                                                                           'successIndicator',
                                                                 'return_type': 'void',
                                                                 'service': '4.14',
                                                                 'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                 'source_line': 267,
                                                                 'throws': [   'SynchronizationPointLabelNotAnnounced',
                                                                               'SaveInProgress',
                                                                               'RestoreInProgress',
                                                                               'FederateNotExecutionMember',
                                                                               'NotConnected',
                                                                               'RTIinternalError']},
                                                             {   'group': None,
                                                                 'language': 'cpp',
                                                                 'params': 'std::wstring const & label, bool '
                                                                           'successfully = true',
                                                                 'return_type': 'void',
                                                                 'service': None,
                                                                 'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                 'source_line': 196,
                                                                 'throws': [   'SynchronizationPointLabelNotAnnounced',
                                                                               'SaveInProgress',
                                                                               'RestoreInProgress',
                                                                               'FederateNotExecutionMember',
                                                                               'NotConnected',
                                                                               'RTIinternalError']}],
                         'timeAdvanceRequest': [   {   'group': 'Time Management',
                                                       'language': 'java',
                                                       'params': 'LogicalTime theTime',
                                                       'return_type': 'void',
                                                       'service': '8.8',
                                                       'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                       'source_line': 1007,
                                                       'throws': [   'LogicalTimeAlreadyPassed',
                                                                     'InvalidLogicalTime',
                                                                     'InTimeAdvancingState',
                                                                     'RequestForTimeRegulationPending',
                                                                     'RequestForTimeConstrainedPending',
                                                                     'SaveInProgress',
                                                                     'RestoreInProgress',
                                                                     'FederateNotExecutionMember',
                                                                     'NotConnected',
                                                                     'RTIinternalError']},
                                                   {   'group': None,
                                                       'language': 'cpp',
                                                       'params': 'LogicalTime const & theTime',
                                                       'return_type': 'void',
                                                       'service': None,
                                                       'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                       'source_line': 925,
                                                       'throws': [   'LogicalTimeAlreadyPassed',
                                                                     'InvalidLogicalTime',
                                                                     'InTimeAdvancingState',
                                                                     'RequestForTimeRegulationPending',
                                                                     'RequestForTimeConstrainedPending',
                                                                     'SaveInProgress',
                                                                     'RestoreInProgress',
                                                                     'FederateNotExecutionMember',
                                                                     'NotConnected',
                                                                     'RTIinternalError']}],
                         'timeAdvanceRequestAvailable': [   {   'group': 'Time Management',
                                                                'language': 'java',
                                                                'params': 'LogicalTime theTime',
                                                                'return_type': 'void',
                                                                'service': '8.9',
                                                                'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                'source_line': 1021,
                                                                'throws': [   'LogicalTimeAlreadyPassed',
                                                                              'InvalidLogicalTime',
                                                                              'InTimeAdvancingState',
                                                                              'RequestForTimeRegulationPending',
                                                                              'RequestForTimeConstrainedPending',
                                                                              'SaveInProgress',
                                                                              'RestoreInProgress',
                                                                              'FederateNotExecutionMember',
                                                                              'NotConnected',
                                                                              'RTIinternalError']},
                                                            {   'group': None,
                                                                'language': 'cpp',
                                                                'params': 'LogicalTime const & theTime',
                                                                'return_type': 'void',
                                                                'service': None,
                                                                'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                'source_line': 940,
                                                                'throws': [   'LogicalTimeAlreadyPassed',
                                                                              'InvalidLogicalTime',
                                                                              'InTimeAdvancingState',
                                                                              'RequestForTimeRegulationPending',
                                                                              'RequestForTimeConstrainedPending',
                                                                              'SaveInProgress',
                                                                              'RestoreInProgress',
                                                                              'FederateNotExecutionMember',
                                                                              'NotConnected',
                                                                              'RTIinternalError']}],
                         'unassociateRegionsForUpdates': [   {   'group': 'Data Distribution Management',
                                                                 'language': 'java',
                                                                 'params': 'ObjectInstanceHandle theObject, '
                                                                           'AttributeSetRegionSetPairList '
                                                                           'attributesAndRegions',
                                                                 'return_type': 'void',
                                                                 'service': '9.7',
                                                                 'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                 'source_line': 1273,
                                                                 'throws': [   'RegionNotCreatedByThisFederate',
                                                                               'InvalidRegion',
                                                                               'AttributeNotDefined',
                                                                               'ObjectInstanceNotKnown',
                                                                               'SaveInProgress',
                                                                               'RestoreInProgress',
                                                                               'FederateNotExecutionMember',
                                                                               'NotConnected',
                                                                               'RTIinternalError']},
                                                             {   'group': None,
                                                                 'language': 'cpp',
                                                                 'params': 'ObjectInstanceHandle theObject, '
                                                                           'AttributeHandleSetRegionHandleSetPairVector '
                                                                           'const & '
                                                                           'theAttributeHandleSetRegionHandleSetPairVector',
                                                                 'return_type': 'void',
                                                                 'service': None,
                                                                 'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                 'source_line': 1208,
                                                                 'throws': [   'RegionNotCreatedByThisFederate',
                                                                               'InvalidRegion',
                                                                               'AttributeNotDefined',
                                                                               'ObjectInstanceNotKnown',
                                                                               'SaveInProgress',
                                                                               'RestoreInProgress',
                                                                               'FederateNotExecutionMember',
                                                                               'NotConnected',
                                                                               'RTIinternalError']}],
                         'unconditionalAttributeOwnershipDivestiture': [   {   'group': 'Ownership Management',
                                                                               'language': 'java',
                                                                               'params': 'ObjectInstanceHandle '
                                                                                         'theObject, '
                                                                                         'AttributeHandleSet '
                                                                                         'theAttributes',
                                                                               'return_type': 'void',
                                                                               'service': '7.2',
                                                                               'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                               'source_line': 804,
                                                                               'throws': [   'AttributeNotOwned',
                                                                                             'AttributeNotDefined',
                                                                                             'ObjectInstanceNotKnown',
                                                                                             'SaveInProgress',
                                                                                             'RestoreInProgress',
                                                                                             'FederateNotExecutionMember',
                                                                                             'NotConnected',
                                                                                             'RTIinternalError']},
                                                                           {   'group': None,
                                                                               'language': 'cpp',
                                                                               'params': 'ObjectInstanceHandle '
                                                                                         'theObject, '
                                                                                         'AttributeHandleSet const & '
                                                                                         'theAttributes',
                                                                               'return_type': 'void',
                                                                               'service': None,
                                                                               'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                               'source_line': 709,
                                                                               'throws': [   'AttributeNotOwned',
                                                                                             'AttributeNotDefined',
                                                                                             'ObjectInstanceNotKnown',
                                                                                             'SaveInProgress',
                                                                                             'RestoreInProgress',
                                                                                             'FederateNotExecutionMember',
                                                                                             'NotConnected',
                                                                                             'RTIinternalError']}],
                         'unpublishInteractionClass': [   {   'group': 'Declaration Management',
                                                              'language': 'java',
                                                              'params': 'InteractionClassHandle theInteraction',
                                                              'return_type': 'void',
                                                              'service': '5.5',
                                                              'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                              'source_line': 437,
                                                              'throws': [   'InteractionClassNotDefined',
                                                                            'SaveInProgress',
                                                                            'RestoreInProgress',
                                                                            'FederateNotExecutionMember',
                                                                            'NotConnected',
                                                                            'RTIinternalError']},
                                                          {   'group': None,
                                                              'language': 'cpp',
                                                              'params': 'InteractionClassHandle theInteraction',
                                                              'return_type': 'void',
                                                              'service': None,
                                                              'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                              'source_line': 369,
                                                              'throws': [   'InteractionClassNotDefined',
                                                                            'SaveInProgress',
                                                                            'RestoreInProgress',
                                                                            'FederateNotExecutionMember',
                                                                            'NotConnected',
                                                                            'RTIinternalError']}],
                         'unpublishObjectClass': [   {   'group': 'Declaration Management',
                                                         'language': 'java',
                                                         'params': 'ObjectClassHandle theClass',
                                                         'return_type': 'void',
                                                         'service': '5.3',
                                                         'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                         'source_line': 403,
                                                         'throws': [   'OwnershipAcquisitionPending',
                                                                       'ObjectClassNotDefined',
                                                                       'SaveInProgress',
                                                                       'RestoreInProgress',
                                                                       'FederateNotExecutionMember',
                                                                       'NotConnected',
                                                                       'RTIinternalError']},
                                                     {   'group': None,
                                                         'language': 'cpp',
                                                         'params': 'ObjectClassHandle theClass',
                                                         'return_type': 'void',
                                                         'service': None,
                                                         'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                         'source_line': 333,
                                                         'throws': [   'OwnershipAcquisitionPending',
                                                                       'ObjectClassNotDefined',
                                                                       'SaveInProgress',
                                                                       'RestoreInProgress',
                                                                       'FederateNotExecutionMember',
                                                                       'NotConnected',
                                                                       'RTIinternalError']}],
                         'unpublishObjectClassAttributes': [   {   'group': 'Declaration Management',
                                                                   'language': 'java',
                                                                   'params': 'ObjectClassHandle theClass, '
                                                                             'AttributeHandleSet attributeList',
                                                                   'return_type': 'void',
                                                                   'service': '5.3',
                                                                   'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                   'source_line': 414,
                                                                   'throws': [   'OwnershipAcquisitionPending',
                                                                                 'AttributeNotDefined',
                                                                                 'ObjectClassNotDefined',
                                                                                 'SaveInProgress',
                                                                                 'RestoreInProgress',
                                                                                 'FederateNotExecutionMember',
                                                                                 'NotConnected',
                                                                                 'RTIinternalError']},
                                                               {   'group': None,
                                                                   'language': 'cpp',
                                                                   'params': 'ObjectClassHandle theClass, '
                                                                             'AttributeHandleSet const & attributeList',
                                                                   'return_type': 'void',
                                                                   'service': None,
                                                                   'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                   'source_line': 344,
                                                                   'throws': [   'OwnershipAcquisitionPending',
                                                                                 'AttributeNotDefined',
                                                                                 'ObjectClassNotDefined',
                                                                                 'SaveInProgress',
                                                                                 'RestoreInProgress',
                                                                                 'FederateNotExecutionMember',
                                                                                 'NotConnected',
                                                                                 'RTIinternalError']}],
                         'unsubscribeInteractionClass': [   {   'group': 'Declaration Management',
                                                                'language': 'java',
                                                                'params': 'InteractionClassHandle theClass',
                                                                'return_type': 'void',
                                                                'service': '5.9',
                                                                'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                'source_line': 543,
                                                                'throws': [   'InteractionClassNotDefined',
                                                                              'SaveInProgress',
                                                                              'RestoreInProgress',
                                                                              'FederateNotExecutionMember',
                                                                              'NotConnected',
                                                                              'RTIinternalError']},
                                                            {   'group': None,
                                                                'language': 'cpp',
                                                                'params': 'InteractionClassHandle theClass',
                                                                'return_type': 'void',
                                                                'service': None,
                                                                'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                'source_line': 432,
                                                                'throws': [   'InteractionClassNotDefined',
                                                                              'SaveInProgress',
                                                                              'RestoreInProgress',
                                                                              'FederateNotExecutionMember',
                                                                              'NotConnected',
                                                                              'RTIinternalError']}],
                         'unsubscribeInteractionClassWithRegions': [   {   'group': 'Data Distribution Management',
                                                                           'language': 'java',
                                                                           'params': 'InteractionClassHandle theClass, '
                                                                                     'RegionHandleSet regions',
                                                                           'return_type': 'void',
                                                                           'service': '9.11',
                                                                           'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                           'source_line': 1395,
                                                                           'throws': [   'RegionNotCreatedByThisFederate',
                                                                                         'InvalidRegion',
                                                                                         'InteractionClassNotDefined',
                                                                                         'SaveInProgress',
                                                                                         'RestoreInProgress',
                                                                                         'FederateNotExecutionMember',
                                                                                         'NotConnected',
                                                                                         'RTIinternalError']},
                                                                       {   'group': None,
                                                                           'language': 'cpp',
                                                                           'params': 'InteractionClassHandle theClass, '
                                                                                     'RegionHandleSet const & '
                                                                                     'theRegionHandleSet',
                                                                           'return_type': 'void',
                                                                           'service': None,
                                                                           'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                           'source_line': 1278,
                                                                           'throws': [   'RegionNotCreatedByThisFederate',
                                                                                         'InvalidRegion',
                                                                                         'InteractionClassNotDefined',
                                                                                         'SaveInProgress',
                                                                                         'RestoreInProgress',
                                                                                         'FederateNotExecutionMember',
                                                                                         'NotConnected',
                                                                                         'RTIinternalError']}],
                         'unsubscribeObjectClass': [   {   'group': 'Declaration Management',
                                                           'language': 'java',
                                                           'params': 'ObjectClassHandle theClass',
                                                           'return_type': 'void',
                                                           'service': '5.7',
                                                           'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                           'source_line': 499,
                                                           'throws': [   'ObjectClassNotDefined',
                                                                         'SaveInProgress',
                                                                         'RestoreInProgress',
                                                                         'FederateNotExecutionMember',
                                                                         'NotConnected',
                                                                         'RTIinternalError']},
                                                       {   'group': None,
                                                           'language': 'cpp',
                                                           'params': 'ObjectClassHandle theClass',
                                                           'return_type': 'void',
                                                           'service': None,
                                                           'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                           'source_line': 396,
                                                           'throws': [   'ObjectClassNotDefined',
                                                                         'SaveInProgress',
                                                                         'RestoreInProgress',
                                                                         'FederateNotExecutionMember',
                                                                         'NotConnected',
                                                                         'RTIinternalError']}],
                         'unsubscribeObjectClassAttributes': [   {   'group': 'Declaration Management',
                                                                     'language': 'java',
                                                                     'params': 'ObjectClassHandle theClass, '
                                                                               'AttributeHandleSet attributeList',
                                                                     'return_type': 'void',
                                                                     'service': '5.7',
                                                                     'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                     'source_line': 509,
                                                                     'throws': [   'AttributeNotDefined',
                                                                                   'ObjectClassNotDefined',
                                                                                   'SaveInProgress',
                                                                                   'RestoreInProgress',
                                                                                   'FederateNotExecutionMember',
                                                                                   'NotConnected',
                                                                                   'RTIinternalError']},
                                                                 {   'group': None,
                                                                     'language': 'cpp',
                                                                     'params': 'ObjectClassHandle theClass, '
                                                                               'AttributeHandleSet const & '
                                                                               'attributeList',
                                                                     'return_type': 'void',
                                                                     'service': None,
                                                                     'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                     'source_line': 406,
                                                                     'throws': [   'AttributeNotDefined',
                                                                                   'ObjectClassNotDefined',
                                                                                   'SaveInProgress',
                                                                                   'RestoreInProgress',
                                                                                   'FederateNotExecutionMember',
                                                                                   'NotConnected',
                                                                                   'RTIinternalError']}],
                         'unsubscribeObjectClassAttributesWithRegions': [   {   'group': 'Data Distribution Management',
                                                                                'language': 'java',
                                                                                'params': 'ObjectClassHandle theClass, '
                                                                                          'AttributeSetRegionSetPairList '
                                                                                          'attributesAndRegions',
                                                                                'return_type': 'void',
                                                                                'service': '9.9',
                                                                                'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                                                'source_line': 1351,
                                                                                'throws': [   'RegionNotCreatedByThisFederate',
                                                                                              'InvalidRegion',
                                                                                              'AttributeNotDefined',
                                                                                              'ObjectClassNotDefined',
                                                                                              'SaveInProgress',
                                                                                              'RestoreInProgress',
                                                                                              'FederateNotExecutionMember',
                                                                                              'NotConnected',
                                                                                              'RTIinternalError']},
                                                                            {   'group': None,
                                                                                'language': 'cpp',
                                                                                'params': 'ObjectClassHandle theClass, '
                                                                                          'AttributeHandleSetRegionHandleSetPairVector '
                                                                                          'const & '
                                                                                          'theAttributeHandleSetRegionHandleSetPairVector',
                                                                                'return_type': 'void',
                                                                                'service': None,
                                                                                'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                                                'source_line': 1245,
                                                                                'throws': [   'RegionNotCreatedByThisFederate',
                                                                                              'InvalidRegion',
                                                                                              'AttributeNotDefined',
                                                                                              'ObjectClassNotDefined',
                                                                                              'SaveInProgress',
                                                                                              'RestoreInProgress',
                                                                                              'FederateNotExecutionMember',
                                                                                              'NotConnected',
                                                                                              'RTIinternalError']}],
                         'updateAttributeValues': [   {   'group': 'Object Management',
                                                          'language': 'java',
                                                          'params': 'ObjectInstanceHandle theObject, '
                                                                    'AttributeHandleValueMap theAttributes, byte[] '
                                                                    'userSuppliedTag',
                                                          'return_type': 'void',
                                                          'service': '6.10',
                                                          'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                          'source_line': 623,
                                                          'throws': [   'AttributeNotOwned',
                                                                        'AttributeNotDefined',
                                                                        'ObjectInstanceNotKnown',
                                                                        'SaveInProgress',
                                                                        'RestoreInProgress',
                                                                        'FederateNotExecutionMember',
                                                                        'NotConnected',
                                                                        'RTIinternalError']},
                                                      {   'group': 'Object Management',
                                                          'language': 'java',
                                                          'params': 'ObjectInstanceHandle theObject, '
                                                                    'AttributeHandleValueMap theAttributes, byte[] '
                                                                    'userSuppliedTag, LogicalTime theTime',
                                                          'return_type': 'MessageRetractionReturn',
                                                          'service': '6.10',
                                                          'source_file': 'apis/java/java/src/hla/rti1516e/RTIambassador.java',
                                                          'source_line': 637,
                                                          'throws': [   'InvalidLogicalTime',
                                                                        'AttributeNotOwned',
                                                                        'AttributeNotDefined',
                                                                        'ObjectInstanceNotKnown',
                                                                        'SaveInProgress',
                                                                        'RestoreInProgress',
                                                                        'FederateNotExecutionMember',
                                                                        'NotConnected',
                                                                        'RTIinternalError']},
                                                      {   'group': None,
                                                          'language': 'cpp',
                                                          'params': 'ObjectInstanceHandle theObject, '
                                                                    'AttributeHandleValueMap const & '
                                                                    'theAttributeValues, VariableLengthData const & '
                                                                    'theUserSuppliedTag',
                                                          'return_type': 'void',
                                                          'service': None,
                                                          'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                          'source_line': 518,
                                                          'throws': [   'AttributeNotOwned',
                                                                        'AttributeNotDefined',
                                                                        'ObjectInstanceNotKnown',
                                                                        'SaveInProgress',
                                                                        'RestoreInProgress',
                                                                        'FederateNotExecutionMember',
                                                                        'NotConnected',
                                                                        'RTIinternalError']},
                                                      {   'group': None,
                                                          'language': 'cpp',
                                                          'params': 'ObjectInstanceHandle theObject, '
                                                                    'AttributeHandleValueMap const & '
                                                                    'theAttributeValues, VariableLengthData const & '
                                                                    'theUserSuppliedTag, LogicalTime const & theTime',
                                                          'return_type': 'MessageRetractionHandle',
                                                          'service': None,
                                                          'source_file': 'apis/cpp/cpp/src/RTI/RTIambassador.h',
                                                          'source_line': 532,
                                                          'throws': [   'InvalidLogicalTime',
                                                                        'AttributeNotOwned',
                                                                        'AttributeNotDefined',
                                                                        'ObjectInstanceNotKnown',
                                                                        'SaveInProgress',
                                                                        'RestoreInProgress',
                                                                        'FederateNotExecutionMember',
                                                                        'NotConnected',
                                                                        'RTIinternalError']}]}}

class RTIambassador(ABC):
    """Abstract RTI ambassador interface. RTI adapters implement these methods."""

    @abstractmethod
    def abortFederationRestore(self, *args: Any, **kwargs: Any) -> Any:
        """abortFederationRestore; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def abortFederationSave(self, *args: Any, **kwargs: Any) -> Any:
        """abortFederationSave; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def associateRegionsForUpdates(self, *args: Any, **kwargs: Any) -> Any:
        """associateRegionsForUpdates; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def attributeOwnershipAcquisition(self, *args: Any, **kwargs: Any) -> Any:
        """attributeOwnershipAcquisition; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def attributeOwnershipAcquisitionIfAvailable(self, *args: Any, **kwargs: Any) -> Any:
        """attributeOwnershipAcquisitionIfAvailable; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def attributeOwnershipDivestitureIfWanted(self, *args: Any, **kwargs: Any) -> Any:
        """attributeOwnershipDivestitureIfWanted; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def attributeOwnershipReleaseDenied(self, *args: Any, **kwargs: Any) -> Any:
        """attributeOwnershipReleaseDenied; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def cancelAttributeOwnershipAcquisition(self, *args: Any, **kwargs: Any) -> Any:
        """cancelAttributeOwnershipAcquisition; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def cancelNegotiatedAttributeOwnershipDivestiture(self, *args: Any, **kwargs: Any) -> Any:
        """cancelNegotiatedAttributeOwnershipDivestiture; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def changeAttributeOrderType(self, *args: Any, **kwargs: Any) -> Any:
        """changeAttributeOrderType; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def changeInteractionOrderType(self, *args: Any, **kwargs: Any) -> Any:
        """changeInteractionOrderType; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def commitRegionModifications(self, *args: Any, **kwargs: Any) -> Any:
        """commitRegionModifications; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def confirmDivestiture(self, *args: Any, **kwargs: Any) -> Any:
        """confirmDivestiture; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def connect(self, *args: Any, **kwargs: Any) -> Any:
        """connect; 3 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def createFederationExecution(self, *args: Any, **kwargs: Any) -> Any:
        """createFederationExecution; 7 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def createFederationExecutionWithMIM(self, *args: Any, **kwargs: Any) -> Any:
        """createFederationExecutionWithMIM; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def createRegion(self, *args: Any, **kwargs: Any) -> Any:
        """createRegion; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def decodeAttributeHandle(self, *args: Any, **kwargs: Any) -> Any:
        """decodeAttributeHandle; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def decodeDimensionHandle(self, *args: Any, **kwargs: Any) -> Any:
        """decodeDimensionHandle; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def decodeFederateHandle(self, *args: Any, **kwargs: Any) -> Any:
        """decodeFederateHandle; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def decodeInteractionClassHandle(self, *args: Any, **kwargs: Any) -> Any:
        """decodeInteractionClassHandle; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def decodeMessageRetractionHandle(self, *args: Any, **kwargs: Any) -> Any:
        """decodeMessageRetractionHandle; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def decodeObjectClassHandle(self, *args: Any, **kwargs: Any) -> Any:
        """decodeObjectClassHandle; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def decodeObjectInstanceHandle(self, *args: Any, **kwargs: Any) -> Any:
        """decodeObjectInstanceHandle; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def decodeParameterHandle(self, *args: Any, **kwargs: Any) -> Any:
        """decodeParameterHandle; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def decodeRegionHandle(self, *args: Any, **kwargs: Any) -> Any:
        """decodeRegionHandle; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def deleteObjectInstance(self, *args: Any, **kwargs: Any) -> Any:
        """deleteObjectInstance; 4 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def deleteRegion(self, *args: Any, **kwargs: Any) -> Any:
        """deleteRegion; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def destroyFederationExecution(self, *args: Any, **kwargs: Any) -> Any:
        """destroyFederationExecution; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def disableAsynchronousDelivery(self, *args: Any, **kwargs: Any) -> Any:
        """disableAsynchronousDelivery; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def disableAttributeRelevanceAdvisorySwitch(self, *args: Any, **kwargs: Any) -> Any:
        """disableAttributeRelevanceAdvisorySwitch; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def disableAttributeScopeAdvisorySwitch(self, *args: Any, **kwargs: Any) -> Any:
        """disableAttributeScopeAdvisorySwitch; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def disableCallbacks(self, *args: Any, **kwargs: Any) -> Any:
        """disableCallbacks; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def disableInteractionRelevanceAdvisorySwitch(self, *args: Any, **kwargs: Any) -> Any:
        """disableInteractionRelevanceAdvisorySwitch; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def disableObjectClassRelevanceAdvisorySwitch(self, *args: Any, **kwargs: Any) -> Any:
        """disableObjectClassRelevanceAdvisorySwitch; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def disableTimeConstrained(self, *args: Any, **kwargs: Any) -> Any:
        """disableTimeConstrained; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def disableTimeRegulation(self, *args: Any, **kwargs: Any) -> Any:
        """disableTimeRegulation; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def disconnect(self, *args: Any, **kwargs: Any) -> Any:
        """disconnect; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def enableAsynchronousDelivery(self, *args: Any, **kwargs: Any) -> Any:
        """enableAsynchronousDelivery; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def enableAttributeRelevanceAdvisorySwitch(self, *args: Any, **kwargs: Any) -> Any:
        """enableAttributeRelevanceAdvisorySwitch; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def enableAttributeScopeAdvisorySwitch(self, *args: Any, **kwargs: Any) -> Any:
        """enableAttributeScopeAdvisorySwitch; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def enableCallbacks(self, *args: Any, **kwargs: Any) -> Any:
        """enableCallbacks; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def enableInteractionRelevanceAdvisorySwitch(self, *args: Any, **kwargs: Any) -> Any:
        """enableInteractionRelevanceAdvisorySwitch; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def enableObjectClassRelevanceAdvisorySwitch(self, *args: Any, **kwargs: Any) -> Any:
        """enableObjectClassRelevanceAdvisorySwitch; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def enableTimeConstrained(self, *args: Any, **kwargs: Any) -> Any:
        """enableTimeConstrained; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def enableTimeRegulation(self, *args: Any, **kwargs: Any) -> Any:
        """enableTimeRegulation; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def evokeCallback(self, *args: Any, **kwargs: Any) -> Any:
        """evokeCallback; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def evokeMultipleCallbacks(self, *args: Any, **kwargs: Any) -> Any:
        """evokeMultipleCallbacks; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def federateRestoreComplete(self, *args: Any, **kwargs: Any) -> Any:
        """federateRestoreComplete; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def federateRestoreNotComplete(self, *args: Any, **kwargs: Any) -> Any:
        """federateRestoreNotComplete; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def federateSaveBegun(self, *args: Any, **kwargs: Any) -> Any:
        """federateSaveBegun; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def federateSaveComplete(self, *args: Any, **kwargs: Any) -> Any:
        """federateSaveComplete; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def federateSaveNotComplete(self, *args: Any, **kwargs: Any) -> Any:
        """federateSaveNotComplete; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def flushQueueRequest(self, *args: Any, **kwargs: Any) -> Any:
        """flushQueueRequest; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getAttributeHandle(self, *args: Any, **kwargs: Any) -> Any:
        """getAttributeHandle; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getAttributeHandleFactory(self, *args: Any, **kwargs: Any) -> Any:
        """getAttributeHandleFactory; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getAttributeHandleSetFactory(self, *args: Any, **kwargs: Any) -> Any:
        """getAttributeHandleSetFactory; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getAttributeHandleValueMapFactory(self, *args: Any, **kwargs: Any) -> Any:
        """getAttributeHandleValueMapFactory; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getAttributeName(self, *args: Any, **kwargs: Any) -> Any:
        """getAttributeName; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getAttributeSetRegionSetPairListFactory(self, *args: Any, **kwargs: Any) -> Any:
        """getAttributeSetRegionSetPairListFactory; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getAutomaticResignDirective(self, *args: Any, **kwargs: Any) -> Any:
        """getAutomaticResignDirective; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getAvailableDimensionsForClassAttribute(self, *args: Any, **kwargs: Any) -> Any:
        """getAvailableDimensionsForClassAttribute; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getAvailableDimensionsForInteractionClass(self, *args: Any, **kwargs: Any) -> Any:
        """getAvailableDimensionsForInteractionClass; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getDimensionHandle(self, *args: Any, **kwargs: Any) -> Any:
        """getDimensionHandle; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getDimensionHandleFactory(self, *args: Any, **kwargs: Any) -> Any:
        """getDimensionHandleFactory; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getDimensionHandleSet(self, *args: Any, **kwargs: Any) -> Any:
        """getDimensionHandleSet; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getDimensionHandleSetFactory(self, *args: Any, **kwargs: Any) -> Any:
        """getDimensionHandleSetFactory; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getDimensionName(self, *args: Any, **kwargs: Any) -> Any:
        """getDimensionName; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getDimensionUpperBound(self, *args: Any, **kwargs: Any) -> Any:
        """getDimensionUpperBound; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getFederateHandle(self, *args: Any, **kwargs: Any) -> Any:
        """getFederateHandle; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getFederateHandleFactory(self, *args: Any, **kwargs: Any) -> Any:
        """getFederateHandleFactory; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getFederateHandleSetFactory(self, *args: Any, **kwargs: Any) -> Any:
        """getFederateHandleSetFactory; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getFederateName(self, *args: Any, **kwargs: Any) -> Any:
        """getFederateName; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getHLAversion(self, *args: Any, **kwargs: Any) -> Any:
        """getHLAversion; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getInteractionClassHandle(self, *args: Any, **kwargs: Any) -> Any:
        """getInteractionClassHandle; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getInteractionClassHandleFactory(self, *args: Any, **kwargs: Any) -> Any:
        """getInteractionClassHandleFactory; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getInteractionClassName(self, *args: Any, **kwargs: Any) -> Any:
        """getInteractionClassName; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getKnownObjectClassHandle(self, *args: Any, **kwargs: Any) -> Any:
        """getKnownObjectClassHandle; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getObjectClassHandle(self, *args: Any, **kwargs: Any) -> Any:
        """getObjectClassHandle; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getObjectClassHandleFactory(self, *args: Any, **kwargs: Any) -> Any:
        """getObjectClassHandleFactory; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getObjectClassName(self, *args: Any, **kwargs: Any) -> Any:
        """getObjectClassName; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getObjectInstanceHandle(self, *args: Any, **kwargs: Any) -> Any:
        """getObjectInstanceHandle; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getObjectInstanceHandleFactory(self, *args: Any, **kwargs: Any) -> Any:
        """getObjectInstanceHandleFactory; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getObjectInstanceName(self, *args: Any, **kwargs: Any) -> Any:
        """getObjectInstanceName; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getOrderName(self, *args: Any, **kwargs: Any) -> Any:
        """getOrderName; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getOrderType(self, *args: Any, **kwargs: Any) -> Any:
        """getOrderType; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getParameterHandle(self, *args: Any, **kwargs: Any) -> Any:
        """getParameterHandle; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getParameterHandleFactory(self, *args: Any, **kwargs: Any) -> Any:
        """getParameterHandleFactory; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getParameterHandleValueMapFactory(self, *args: Any, **kwargs: Any) -> Any:
        """getParameterHandleValueMapFactory; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getParameterName(self, *args: Any, **kwargs: Any) -> Any:
        """getParameterName; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getRangeBounds(self, *args: Any, **kwargs: Any) -> Any:
        """getRangeBounds; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getRegionHandleSetFactory(self, *args: Any, **kwargs: Any) -> Any:
        """getRegionHandleSetFactory; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getTimeFactory(self, *args: Any, **kwargs: Any) -> Any:
        """getTimeFactory; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getTransportationName(self, *args: Any, **kwargs: Any) -> Any:
        """getTransportationName; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getTransportationType(self, *args: Any, **kwargs: Any) -> Any:
        """getTransportationType; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getTransportationTypeHandle(self, *args: Any, **kwargs: Any) -> Any:
        """getTransportationTypeHandle; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getTransportationTypeHandleFactory(self, *args: Any, **kwargs: Any) -> Any:
        """getTransportationTypeHandleFactory; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getTransportationTypeName(self, *args: Any, **kwargs: Any) -> Any:
        """getTransportationTypeName; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getUpdateRateValue(self, *args: Any, **kwargs: Any) -> Any:
        """getUpdateRateValue; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def getUpdateRateValueForAttribute(self, *args: Any, **kwargs: Any) -> Any:
        """getUpdateRateValueForAttribute; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def isAttributeOwnedByFederate(self, *args: Any, **kwargs: Any) -> Any:
        """isAttributeOwnedByFederate; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def joinFederationExecution(self, *args: Any, **kwargs: Any) -> Any:
        """joinFederationExecution; 6 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def listFederationExecutions(self, *args: Any, **kwargs: Any) -> Any:
        """listFederationExecutions; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def localDeleteObjectInstance(self, *args: Any, **kwargs: Any) -> Any:
        """localDeleteObjectInstance; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def modifyLookahead(self, *args: Any, **kwargs: Any) -> Any:
        """modifyLookahead; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def negotiatedAttributeOwnershipDivestiture(self, *args: Any, **kwargs: Any) -> Any:
        """negotiatedAttributeOwnershipDivestiture; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def nextMessageRequest(self, *args: Any, **kwargs: Any) -> Any:
        """nextMessageRequest; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def nextMessageRequestAvailable(self, *args: Any, **kwargs: Any) -> Any:
        """nextMessageRequestAvailable; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def normalizeFederateHandle(self, *args: Any, **kwargs: Any) -> Any:
        """normalizeFederateHandle; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def normalizeServiceGroup(self, *args: Any, **kwargs: Any) -> Any:
        """normalizeServiceGroup; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def publishInteractionClass(self, *args: Any, **kwargs: Any) -> Any:
        """publishInteractionClass; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def publishObjectClassAttributes(self, *args: Any, **kwargs: Any) -> Any:
        """publishObjectClassAttributes; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def queryAttributeOwnership(self, *args: Any, **kwargs: Any) -> Any:
        """queryAttributeOwnership; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def queryAttributeTransportationType(self, *args: Any, **kwargs: Any) -> Any:
        """queryAttributeTransportationType; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def queryFederationRestoreStatus(self, *args: Any, **kwargs: Any) -> Any:
        """queryFederationRestoreStatus; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def queryFederationSaveStatus(self, *args: Any, **kwargs: Any) -> Any:
        """queryFederationSaveStatus; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def queryGALT(self, *args: Any, **kwargs: Any) -> Any:
        """queryGALT; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def queryInteractionTransportationType(self, *args: Any, **kwargs: Any) -> Any:
        """queryInteractionTransportationType; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def queryLITS(self, *args: Any, **kwargs: Any) -> Any:
        """queryLITS; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def queryLogicalTime(self, *args: Any, **kwargs: Any) -> Any:
        """queryLogicalTime; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def queryLookahead(self, *args: Any, **kwargs: Any) -> Any:
        """queryLookahead; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def registerFederationSynchronizationPoint(self, *args: Any, **kwargs: Any) -> Any:
        """registerFederationSynchronizationPoint; 4 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def registerObjectInstance(self, *args: Any, **kwargs: Any) -> Any:
        """registerObjectInstance; 4 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def registerObjectInstanceWithRegions(self, *args: Any, **kwargs: Any) -> Any:
        """registerObjectInstanceWithRegions; 4 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def releaseMultipleObjectInstanceName(self, *args: Any, **kwargs: Any) -> Any:
        """releaseMultipleObjectInstanceName; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def releaseObjectInstanceName(self, *args: Any, **kwargs: Any) -> Any:
        """releaseObjectInstanceName; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def requestAttributeTransportationTypeChange(self, *args: Any, **kwargs: Any) -> Any:
        """requestAttributeTransportationTypeChange; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def requestAttributeValueUpdate(self, *args: Any, **kwargs: Any) -> Any:
        """requestAttributeValueUpdate; 4 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def requestAttributeValueUpdateWithRegions(self, *args: Any, **kwargs: Any) -> Any:
        """requestAttributeValueUpdateWithRegions; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def requestFederationRestore(self, *args: Any, **kwargs: Any) -> Any:
        """requestFederationRestore; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def requestFederationSave(self, *args: Any, **kwargs: Any) -> Any:
        """requestFederationSave; 4 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def requestInteractionTransportationTypeChange(self, *args: Any, **kwargs: Any) -> Any:
        """requestInteractionTransportationTypeChange; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def reserveMultipleObjectInstanceName(self, *args: Any, **kwargs: Any) -> Any:
        """reserveMultipleObjectInstanceName; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def reserveObjectInstanceName(self, *args: Any, **kwargs: Any) -> Any:
        """reserveObjectInstanceName; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def resignFederationExecution(self, *args: Any, **kwargs: Any) -> Any:
        """resignFederationExecution; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def retract(self, *args: Any, **kwargs: Any) -> Any:
        """retract; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def sendInteraction(self, *args: Any, **kwargs: Any) -> Any:
        """sendInteraction; 4 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def sendInteractionWithRegions(self, *args: Any, **kwargs: Any) -> Any:
        """sendInteractionWithRegions; 4 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def setAutomaticResignDirective(self, *args: Any, **kwargs: Any) -> Any:
        """setAutomaticResignDirective; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def setRangeBounds(self, *args: Any, **kwargs: Any) -> Any:
        """setRangeBounds; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def subscribeInteractionClass(self, *args: Any, **kwargs: Any) -> Any:
        """subscribeInteractionClass; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def subscribeInteractionClassPassively(self, *args: Any, **kwargs: Any) -> Any:
        """subscribeInteractionClassPassively; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def subscribeInteractionClassPassivelyWithRegions(self, *args: Any, **kwargs: Any) -> Any:
        """subscribeInteractionClassPassivelyWithRegions; 1 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def subscribeInteractionClassWithRegions(self, *args: Any, **kwargs: Any) -> Any:
        """subscribeInteractionClassWithRegions; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def subscribeObjectClassAttributes(self, *args: Any, **kwargs: Any) -> Any:
        """subscribeObjectClassAttributes; 3 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def subscribeObjectClassAttributesPassively(self, *args: Any, **kwargs: Any) -> Any:
        """subscribeObjectClassAttributesPassively; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def subscribeObjectClassAttributesPassivelyWithRegions(self, *args: Any, **kwargs: Any) -> Any:
        """subscribeObjectClassAttributesPassivelyWithRegions; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def subscribeObjectClassAttributesWithRegions(self, *args: Any, **kwargs: Any) -> Any:
        """subscribeObjectClassAttributesWithRegions; 3 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def synchronizationPointAchieved(self, *args: Any, **kwargs: Any) -> Any:
        """synchronizationPointAchieved; 3 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def timeAdvanceRequest(self, *args: Any, **kwargs: Any) -> Any:
        """timeAdvanceRequest; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def timeAdvanceRequestAvailable(self, *args: Any, **kwargs: Any) -> Any:
        """timeAdvanceRequestAvailable; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def unassociateRegionsForUpdates(self, *args: Any, **kwargs: Any) -> Any:
        """unassociateRegionsForUpdates; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def unconditionalAttributeOwnershipDivestiture(self, *args: Any, **kwargs: Any) -> Any:
        """unconditionalAttributeOwnershipDivestiture; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def unpublishInteractionClass(self, *args: Any, **kwargs: Any) -> Any:
        """unpublishInteractionClass; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def unpublishObjectClass(self, *args: Any, **kwargs: Any) -> Any:
        """unpublishObjectClass; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def unpublishObjectClassAttributes(self, *args: Any, **kwargs: Any) -> Any:
        """unpublishObjectClassAttributes; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def unsubscribeInteractionClass(self, *args: Any, **kwargs: Any) -> Any:
        """unsubscribeInteractionClass; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def unsubscribeInteractionClassWithRegions(self, *args: Any, **kwargs: Any) -> Any:
        """unsubscribeInteractionClassWithRegions; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def unsubscribeObjectClass(self, *args: Any, **kwargs: Any) -> Any:
        """unsubscribeObjectClass; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def unsubscribeObjectClassAttributes(self, *args: Any, **kwargs: Any) -> Any:
        """unsubscribeObjectClassAttributes; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def unsubscribeObjectClassAttributesWithRegions(self, *args: Any, **kwargs: Any) -> Any:
        """unsubscribeObjectClassAttributesWithRegions; 2 source overload(s). See API_METADATA."""
        raise NotImplementedError

    @abstractmethod
    def updateAttributeValues(self, *args: Any, **kwargs: Any) -> Any:
        """updateAttributeValues; 4 source overload(s). See API_METADATA."""
        raise NotImplementedError

class FederateAmbassador:
    """No-op federate callback base preserving source method names."""

    def announceSynchronizationPoint(self, *args: Any, **kwargs: Any) -> Any:
        """announceSynchronizationPoint; 2 source overload(s). Override in a federate."""
        return None

    def attributeIsNotOwned(self, *args: Any, **kwargs: Any) -> Any:
        """attributeIsNotOwned; 2 source overload(s). Override in a federate."""
        return None

    def attributeIsOwnedByRTI(self, *args: Any, **kwargs: Any) -> Any:
        """attributeIsOwnedByRTI; 2 source overload(s). Override in a federate."""
        return None

    def attributeOwnershipAcquisitionNotification(self, *args: Any, **kwargs: Any) -> Any:
        """attributeOwnershipAcquisitionNotification; 2 source overload(s). Override in a federate."""
        return None

    def attributeOwnershipUnavailable(self, *args: Any, **kwargs: Any) -> Any:
        """attributeOwnershipUnavailable; 2 source overload(s). Override in a federate."""
        return None

    def attributesInScope(self, *args: Any, **kwargs: Any) -> Any:
        """attributesInScope; 2 source overload(s). Override in a federate."""
        return None

    def attributesOutOfScope(self, *args: Any, **kwargs: Any) -> Any:
        """attributesOutOfScope; 2 source overload(s). Override in a federate."""
        return None

    def confirmAttributeOwnershipAcquisitionCancellation(self, *args: Any, **kwargs: Any) -> Any:
        """confirmAttributeOwnershipAcquisitionCancellation; 2 source overload(s). Override in a federate."""
        return None

    def confirmAttributeTransportationTypeChange(self, *args: Any, **kwargs: Any) -> Any:
        """confirmAttributeTransportationTypeChange; 2 source overload(s). Override in a federate."""
        return None

    def confirmInteractionTransportationTypeChange(self, *args: Any, **kwargs: Any) -> Any:
        """confirmInteractionTransportationTypeChange; 2 source overload(s). Override in a federate."""
        return None

    def connectionLost(self, *args: Any, **kwargs: Any) -> Any:
        """connectionLost; 2 source overload(s). Override in a federate."""
        return None

    def discoverObjectInstance(self, *args: Any, **kwargs: Any) -> Any:
        """discoverObjectInstance; 4 source overload(s). Override in a federate."""
        return None

    def federationNotRestored(self, *args: Any, **kwargs: Any) -> Any:
        """federationNotRestored; 2 source overload(s). Override in a federate."""
        return None

    def federationNotSaved(self, *args: Any, **kwargs: Any) -> Any:
        """federationNotSaved; 2 source overload(s). Override in a federate."""
        return None

    def federationRestoreBegun(self, *args: Any, **kwargs: Any) -> Any:
        """federationRestoreBegun; 2 source overload(s). Override in a federate."""
        return None

    def federationRestoreStatusResponse(self, *args: Any, **kwargs: Any) -> Any:
        """federationRestoreStatusResponse; 2 source overload(s). Override in a federate."""
        return None

    def federationRestored(self, *args: Any, **kwargs: Any) -> Any:
        """federationRestored; 2 source overload(s). Override in a federate."""
        return None

    def federationSaveStatusResponse(self, *args: Any, **kwargs: Any) -> Any:
        """federationSaveStatusResponse; 2 source overload(s). Override in a federate."""
        return None

    def federationSaved(self, *args: Any, **kwargs: Any) -> Any:
        """federationSaved; 2 source overload(s). Override in a federate."""
        return None

    def federationSynchronized(self, *args: Any, **kwargs: Any) -> Any:
        """federationSynchronized; 2 source overload(s). Override in a federate."""
        return None

    def getProducingFederate(self, *args: Any, **kwargs: Any) -> Any:
        """getProducingFederate; 3 source overload(s). Override in a federate."""
        return None

    def getSentRegions(self, *args: Any, **kwargs: Any) -> Any:
        """getSentRegions; 2 source overload(s). Override in a federate."""
        return None

    def hasProducingFederate(self, *args: Any, **kwargs: Any) -> Any:
        """hasProducingFederate; 3 source overload(s). Override in a federate."""
        return None

    def hasSentRegions(self, *args: Any, **kwargs: Any) -> Any:
        """hasSentRegions; 2 source overload(s). Override in a federate."""
        return None

    def informAttributeOwnership(self, *args: Any, **kwargs: Any) -> Any:
        """informAttributeOwnership; 2 source overload(s). Override in a federate."""
        return None

    def initiateFederateRestore(self, *args: Any, **kwargs: Any) -> Any:
        """initiateFederateRestore; 2 source overload(s). Override in a federate."""
        return None

    def initiateFederateSave(self, *args: Any, **kwargs: Any) -> Any:
        """initiateFederateSave; 4 source overload(s). Override in a federate."""
        return None

    def multipleObjectInstanceNameReservationFailed(self, *args: Any, **kwargs: Any) -> Any:
        """multipleObjectInstanceNameReservationFailed; 2 source overload(s). Override in a federate."""
        return None

    def multipleObjectInstanceNameReservationSucceeded(self, *args: Any, **kwargs: Any) -> Any:
        """multipleObjectInstanceNameReservationSucceeded; 2 source overload(s). Override in a federate."""
        return None

    def objectInstanceNameReservationFailed(self, *args: Any, **kwargs: Any) -> Any:
        """objectInstanceNameReservationFailed; 2 source overload(s). Override in a federate."""
        return None

    def objectInstanceNameReservationSucceeded(self, *args: Any, **kwargs: Any) -> Any:
        """objectInstanceNameReservationSucceeded; 2 source overload(s). Override in a federate."""
        return None

    def provideAttributeValueUpdate(self, *args: Any, **kwargs: Any) -> Any:
        """provideAttributeValueUpdate; 2 source overload(s). Override in a federate."""
        return None

    def receiveInteraction(self, *args: Any, **kwargs: Any) -> Any:
        """receiveInteraction; 6 source overload(s). Override in a federate."""
        return None

    def reflectAttributeValues(self, *args: Any, **kwargs: Any) -> Any:
        """reflectAttributeValues; 6 source overload(s). Override in a federate."""
        return None

    def removeObjectInstance(self, *args: Any, **kwargs: Any) -> Any:
        """removeObjectInstance; 6 source overload(s). Override in a federate."""
        return None

    def reportAttributeTransportationType(self, *args: Any, **kwargs: Any) -> Any:
        """reportAttributeTransportationType; 2 source overload(s). Override in a federate."""
        return None

    def reportFederationExecutions(self, *args: Any, **kwargs: Any) -> Any:
        """reportFederationExecutions; 2 source overload(s). Override in a federate."""
        return None

    def reportInteractionTransportationType(self, *args: Any, **kwargs: Any) -> Any:
        """reportInteractionTransportationType; 2 source overload(s). Override in a federate."""
        return None

    def requestAttributeOwnershipAssumption(self, *args: Any, **kwargs: Any) -> Any:
        """requestAttributeOwnershipAssumption; 2 source overload(s). Override in a federate."""
        return None

    def requestAttributeOwnershipRelease(self, *args: Any, **kwargs: Any) -> Any:
        """requestAttributeOwnershipRelease; 2 source overload(s). Override in a federate."""
        return None

    def requestDivestitureConfirmation(self, *args: Any, **kwargs: Any) -> Any:
        """requestDivestitureConfirmation; 2 source overload(s). Override in a federate."""
        return None

    def requestFederationRestoreFailed(self, *args: Any, **kwargs: Any) -> Any:
        """requestFederationRestoreFailed; 2 source overload(s). Override in a federate."""
        return None

    def requestFederationRestoreSucceeded(self, *args: Any, **kwargs: Any) -> Any:
        """requestFederationRestoreSucceeded; 2 source overload(s). Override in a federate."""
        return None

    def requestRetraction(self, *args: Any, **kwargs: Any) -> Any:
        """requestRetraction; 2 source overload(s). Override in a federate."""
        return None

    def startRegistrationForObjectClass(self, *args: Any, **kwargs: Any) -> Any:
        """startRegistrationForObjectClass; 2 source overload(s). Override in a federate."""
        return None

    def stopRegistrationForObjectClass(self, *args: Any, **kwargs: Any) -> Any:
        """stopRegistrationForObjectClass; 2 source overload(s). Override in a federate."""
        return None

    def synchronizationPointRegistrationFailed(self, *args: Any, **kwargs: Any) -> Any:
        """synchronizationPointRegistrationFailed; 2 source overload(s). Override in a federate."""
        return None

    def synchronizationPointRegistrationSucceeded(self, *args: Any, **kwargs: Any) -> Any:
        """synchronizationPointRegistrationSucceeded; 2 source overload(s). Override in a federate."""
        return None

    def timeAdvanceGrant(self, *args: Any, **kwargs: Any) -> Any:
        """timeAdvanceGrant; 2 source overload(s). Override in a federate."""
        return None

    def timeConstrainedEnabled(self, *args: Any, **kwargs: Any) -> Any:
        """timeConstrainedEnabled; 2 source overload(s). Override in a federate."""
        return None

    def timeRegulationEnabled(self, *args: Any, **kwargs: Any) -> Any:
        """timeRegulationEnabled; 2 source overload(s). Override in a federate."""
        return None

    def turnInteractionsOff(self, *args: Any, **kwargs: Any) -> Any:
        """turnInteractionsOff; 2 source overload(s). Override in a federate."""
        return None

    def turnInteractionsOn(self, *args: Any, **kwargs: Any) -> Any:
        """turnInteractionsOn; 2 source overload(s). Override in a federate."""
        return None

    def turnUpdatesOffForObjectInstance(self, *args: Any, **kwargs: Any) -> Any:
        """turnUpdatesOffForObjectInstance; 2 source overload(s). Override in a federate."""
        return None

    def turnUpdatesOnForObjectInstance(self, *args: Any, **kwargs: Any) -> Any:
        """turnUpdatesOnForObjectInstance; 4 source overload(s). Override in a federate."""
        return None

RTIAmbassador = RTIambassador
NullFederateAmbassador = FederateAmbassador
__all__ = ["API_METADATA", "RTIambassador", "RTIAmbassador", "FederateAmbassador", "NullFederateAmbassador"]
