
Ontology-related products are posted to the SISO Digital Library under the C2SIM PDG/PSG space in folder “_C2SIM PDG Products/Ontologies". The initial version (1.0.0) and subsequent versions (e.g., 1.0.1) are in their own subdirectories.

README.txt: The present README file describes the content of its containing folder.

C2SIMV1.0.1_Files.zip: The full set of approved C2SIM files are contained in the C2SIMV1.0.1_Files.zip archive. The contents of that archive are are described below.

-- C2SIM_v1.0.0.rdf: Original C2SIM Core ontology rendered in the RDF/XML format.

-- C2SIM_SMX_v1.0.0.rdf: Original C2SIM Standard Military Extension (SMX) ontology rendered in the RDF/XML format.

-- C2SIM_LOX_v1.0.0.rdf: Original C2SIM Land Operations Extension (LOX) ontology rendered in the RDF/XML format.

-- C2SIMOntologyToC2SIMSchema_v1.0.1.xslt: An XSLT file to generate a C2SIM XML schema from a merged set of C2SIM ontologies. This XSLT file was updated in response to Problem Report/Change Report PR2021-1.

-- C2SIM_SMX__LOX_v1.0.1.xsd: An xsd (XML Schema Document) generated from the merged C2SIM core, SMX, and LOX ontologies (merged using the Stanford Protégé ontology editing tool and rendered in the RDF/XML format) by using the C2SIMOntologyToC2SIMSchemaV1.0.1 extensible stylesheet language transformations (XSLT) file. This XSLT file was updated in response to Problem Report/Change Report PR2021-1.

-- C2SIMAlphabetize1.0.0beta.zip: A zip file containing a software tool to post-process output of the XSLT transformation to alphabetize named groups and elements in the generated XML schema file.

-- C2SIM PR-CR-2021-1.docx: A Microsoft Word document describing the Problem Report / Change Report that prompted this change to C2SIM files. 

---------------------------
NOTE: The higher ontology layers SMX and LOX require access to the lower layers (for example the Core C2SIM_v1.0.0.rdf). When using Protégé, this can be achieved by including C2SIM_SMX_v1.0.0.rdf in the same directory/folder as C2SIM_SMX_v1.0.0.rdf and C2SIM_LOX_v1.0.0.rdf. Protégé will then find the lower layers automatically.


