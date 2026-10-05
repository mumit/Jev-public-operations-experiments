"""Separate pre-inference sizing replacement; preserve all notes and option keys."""
import re
import json
from .public_note_features import (ARMS, DIMENSIONS, extraction, parser, annotated,
                                   semantics, verdict_request, extraction_request as original)


def extraction_request(packet):
    body = original(packet)
    state = json.loads(body['state'])
    state['extraction_definitions'] = {}
    for field, question in body['questions'].items():
        question['instructions'] = re.sub(
            r'Read candidates\[(\d+)\]\.text in the full note context\. Identify what the sentence says, not whether telemetry would establish it\. Resolve a pronoun only from an unambiguous antecedent in this note\. ',
            r'Read candidates[\1].text in the full note; classify its meaning, not telemetry truth. ',
            question['instructions'])
        dimension = field.split('_', 1)[1]
        if dimension == 'service':
            question['instructions'] += ' Resolve pronouns only from a unique antecedent in this note.'
            for service in packet['services']:
                question['criteria'][service] = 'Unique subject.'
        elif dimension == 'channel':
            for channel in packet['channels']:
                question['criteria'][channel] = 'Named channel.'
        elif dimension == 'measure':
            for measure in question['criteria']:
                if measure != 'none_or_unclear':
                    question['criteria'][measure] = 'Named duration measure.'
        text = question['instructions']
        definition = text.split('not telemetry truth. ', 1)[1]
        if dimension in state['extraction_definitions'] and state['extraction_definitions'][dimension] != definition:
            raise ValueError('Candidate-dependent extraction definition.')
        state['extraction_definitions'][dimension] = definition
        index = re.search(r'candidates\[(\d+)\]', text).group(1)
        question['instructions'] = (f'Classify candidates[{index}].text in the full note using '
                                    f'extraction_definitions.{dimension}. Interpret the text, not telemetry truth.')
    body['state'] = json.dumps(state, sort_keys=True, separators=(',', ':'), allow_nan=False)
    return body
