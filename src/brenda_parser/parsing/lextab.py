# lextab.py. This file automatically created by PLY (version 3.10). Don't edit!
_tabversion   = '3.10'
_lextokens    = set(('COMMENT', 'RCURLY', 'REFERENCE_ENTRY', 'EC_NUMBER', 'CONTENT', 'ENTRY', 'RANGLE', 'LPARENS', 'RPARENS', 'LCURLY', 'ENZYME_ENTRY', 'PROTEIN', 'END', 'LANGLE', 'SPECIAL', 'AND', 'PROTEIN_ENTRY', 'CITATION', 'POUND', 'ACCESSION'))
_lexreflags   = 64
_lexliterals  = ''
_lexstateinfo = {'INITIAL': 'inclusive', 'citation': 'exclusive', 'protein': 'exclusive', 'special': 'exclusive', 'comment': 'exclusive', 'enzyme': 'exclusive', 'protentry': 'inclusive'}
_lexstatere   = {'INITIAL': [('(?P<t_ANY_newline>\\n+)|(?P<t_brenda_comment>\\*.+\\n)|(?P<t_POUND>[#])|(?P<t_LANGLE><)|(?P<t_LCURLY>{)|(?P<t_LPARENS>\\()|(?P<t_END>[/]{3}\\s)|(?P<t_ENZYME_ENTRY>ID\\t)|(?P<t_PROTEIN_ENTRY>PR\\t)|(?P<t_REFERENCE_ENTRY>RF\\t)|(?P<t_ENTRY>[A-Z0-9]{2,4}\\t)|(?P<t_brenda_header>[A-Z0-9_]{4,}\\n)|(?P<t_CONTENT>[^\\{\\}\\(\\)\\<\\>\\# \t\r\x0c\x0b\n]+)', [None, ('t_ANY_newline', 'newline'), ('t_brenda_comment', 'brenda_comment'), ('t_POUND', 'POUND'), ('t_LANGLE', 'LANGLE'), ('t_LCURLY', 'LCURLY'), ('t_LPARENS', 'LPARENS'), ('t_END', 'END'), ('t_ENZYME_ENTRY', 'ENZYME_ENTRY'), ('t_PROTEIN_ENTRY', 'PROTEIN_ENTRY'), ('t_REFERENCE_ENTRY', 'REFERENCE_ENTRY'), ('t_ENTRY', 'ENTRY'), ('t_brenda_header', 'brenda_header'), (None, 'CONTENT')])], 'citation': [('(?P<t_ANY_newline>\\n+)|(?P<t_citation_CITATION>\\d+)|(?P<t_citation_RANGLE>>)', [None, ('t_ANY_newline', 'newline'), ('t_citation_CITATION', 'CITATION'), ('t_citation_RANGLE', 'RANGLE')])], 'protein': [('(?P<t_ANY_newline>\\n+)|(?P<t_protein_PROTEIN>\\d+)|(?P<t_protein_POUND>[#])', [None, ('t_ANY_newline', 'newline'), ('t_protein_PROTEIN', 'PROTEIN'), ('t_protein_POUND', 'POUND')])], 'special': [('(?P<t_ANY_newline>\\n+)|(?P<t_special_SPECIAL>[^\\{\\}\\s]+)|(?P<t_special_RCURLY>})', [None, ('t_ANY_newline', 'newline'), ('t_special_SPECIAL', 'SPECIAL'), ('t_special_RCURLY', 'RCURLY')])], 'comment': [('(?P<t_ANY_newline>\\n+)|(?P<t_comment_COMMENT>[^\\(\\)\\s]+)|(?P<t_comment_LPARENS>\\()|(?P<t_comment_RPARENS>\\))', [None, ('t_ANY_newline', 'newline'), ('t_comment_COMMENT', 'COMMENT'), ('t_comment_LPARENS', 'LPARENS'), ('t_comment_RPARENS', 'RPARENS')])], 'enzyme': [('(?P<t_ANY_newline>\\n+)|(?P<t_enzyme_EC_NUMBER>(\\d+)\\.(\\d+)\\.(\\d+)\\.(\\d+))', [None, ('t_ANY_newline', 'newline'), ('t_enzyme_EC_NUMBER', 'EC_NUMBER')])], 'protentry': [('(?P<t_ANY_newline>\\n+)|(?P<t_protentry_PROTEIN_ENTRY>PR\\t)|(?P<t_protentry_ENTRY>[A-Z0-9]{2,4}\\t)|(?P<t_protentry_AND>AND)|(?P<t_protentry_ACCESSION>([A-N,R-Z][0-9]([A-Z][A-Z, 0-9][A-Z, 0-9][0-9]){1,2})|([O,P,Q][0-9][A-Z, 0-9][A-Z, 0-9][A-Z, 0-9][0-9])(\\.\\d+)?)', [None, ('t_ANY_newline', 'newline'), ('t_protentry_PROTEIN_ENTRY', 'PROTEIN_ENTRY'), ('t_protentry_ENTRY', 'ENTRY'), ('t_protentry_AND', 'AND'), ('t_protentry_ACCESSION', 'ACCESSION')]), ('(?P<t_ANY_newline>\\n+)|(?P<t_brenda_comment>\\*.+\\n)|(?P<t_POUND>[#])|(?P<t_LANGLE><)|(?P<t_LCURLY>{)|(?P<t_LPARENS>\\()|(?P<t_END>[/]{3}\\s)|(?P<t_ENZYME_ENTRY>ID\\t)|(?P<t_PROTEIN_ENTRY>PR\\t)|(?P<t_REFERENCE_ENTRY>RF\\t)|(?P<t_ENTRY>[A-Z0-9]{2,4}\\t)|(?P<t_brenda_header>[A-Z0-9_]{4,}\\n)|(?P<t_CONTENT>[^\\{\\}\\(\\)\\<\\>\\# \t\r\x0c\x0b\n]+)', [None, ('t_ANY_newline', 'newline'), ('t_brenda_comment', 'brenda_comment'), ('t_POUND', 'POUND'), ('t_LANGLE', 'LANGLE'), ('t_LCURLY', 'LCURLY'), ('t_LPARENS', 'LPARENS'), ('t_END', 'END'), ('t_ENZYME_ENTRY', 'ENZYME_ENTRY'), ('t_PROTEIN_ENTRY', 'PROTEIN_ENTRY'), ('t_REFERENCE_ENTRY', 'REFERENCE_ENTRY'), ('t_ENTRY', 'ENTRY'), ('t_brenda_header', 'brenda_header'), (None, 'CONTENT')])]}
_lexstateignore = {'citation': ' ,\t', 'protein': ' ,\t', 'INITIAL': ' \t\r\x0c\x0b', 'special': ' \t\r\x0c\x0b', 'comment': ' \t\r\x0c\x0b', 'enzyme': ' \t\r\x0c\x0b', 'protentry': ' \t\r\x0c\x0b'}
_lexstateerrorf = {'INITIAL': 't_ANY_error', 'citation': 't_ANY_error', 'protein': 't_ANY_error', 'special': 't_ANY_error', 'comment': 't_ANY_error', 'enzyme': 't_ANY_error', 'protentry': 't_ANY_error'}
_lexstateeoff = {}