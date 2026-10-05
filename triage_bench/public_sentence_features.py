"""Validate independent answers without repairing them; quarantine the sentence."""
from .profile import MODEL
from .public_rca_trial import normalize
from .public_note_features import DIMENSIONS, extraction


class GlobalReplyError(ValueError):
    """The reply cannot safely be associated with its planned questions."""


def sentence_id(field):
    return field.split('_', 1)[0]


def validate_reply(raw, body, context_tokens):
    if not isinstance(raw, dict) or raw.get('model') != MODEL:
        raise GlobalReplyError('checkpoint_mismatch')
    supplied = raw.get('answers')
    if not isinstance(supplied, dict) or set(supplied) - set(body['questions']):
        raise GlobalReplyError('answer_envelope_mismatch')
    usage = raw.get('usage')
    tokens = usage.get('input_tokens') if isinstance(usage, dict) else None
    if isinstance(tokens, bool) or not isinstance(tokens, int) or tokens < 1:
        raise GlobalReplyError('untrustworthy_usage')
    if tokens > context_tokens:
        raise GlobalReplyError('reported_context_overflow')
    valid, errors = {}, {}
    for field, question in body['questions'].items():
        answer = supplied.get(field)
        try:
            if not isinstance(answer, dict) or answer.get('type') != 'choice':
                raise ValueError('Missing or malformed Choice answer.')
            choice, probabilities, confidence = normalize(
                {'model': MODEL, 'answers': {'cause': answer}}, question['criteria'])
            valid[field] = {'choice': choice, 'probabilities': probabilities, 'provider_confidence': confidence}
        except (ValueError, TypeError, KeyError) as error:
            errors[field] = str(error)
    return {'answers': valid, 'field_errors': errors,
            'quarantined_sentences': sorted({sentence_id(f) for f in errors}), 'usage': usage,
            'status': 'ok_with_review' if errors else 'ok'}


def extract(packet, row):
    if not row or row.get('status') not in ('ok', 'ok_with_review'):
        return {c['id']: {'accepted': False, 'review_reason': 'unavailable_reply',
                         'minimum_required_probability': None} for c in packet['candidates']}
    result = extraction(packet, row['answers'])
    for candidate in row['quarantined_sentences']:
        # Even a malformed unused dimension blocks its sentence. Valid fields stay
        # visible, but there is no invented probability or corrected choice.
        result[candidate].update(accepted=False, review_reason='invalid_sentence_answer',
            minimum_required_probability=None,
            validation_errors={f: e for f, e in row['field_errors'].items() if sentence_id(f) == candidate})
    return result


def whole_note_counterfactual(packet, row):
    """Same new reply under the old whole-note validator, with no extra calls."""
    from .public_binding_trial import answers
    try:
        valid = answers(row['raw_response'], packet['extraction_request'])
    except (ValueError, TypeError, KeyError):
        return {c['id']: {'accepted': False, 'review_reason': 'whole_note_rejected'} for c in packet['candidates']}
    return extraction(packet, valid)
