import re
import secrets
import string
from typing import List, Tuple, Dict

TOKEN_PREFIX = "<[ANON_"
TOKEN_SUFFIX = "]>"
TOKEN_ALPHABET = string.ascii_uppercase + string.digits
TOKEN_LENGTH = 4

def generate_token(existing_tokens: set) -> str:
    """Generate a collision-proof unique token."""
    while True:
        random_str = ''.join(secrets.choice(TOKEN_ALPHABET) for _ in range(TOKEN_LENGTH))
        token = f"{TOKEN_PREFIX}{random_str}{TOKEN_SUFFIX}"
        if token not in existing_tokens:
            return token

def anonymize_text(text: str, words: List[str], existing_mapping: Dict[str, str] = None, match_whole_words: bool = True) -> Tuple[str, Dict[str, str]]:
    """
    Anonymize occurrences of specific words in the text.
    Handles Polish diacritics and regex special characters safely.
    Replaces longest phrases first (greedy).
    """
    # Sort words by length descending for greedy matching
    sorted_words = sorted(words, key=len, reverse=True)
    
    mapping = dict(existing_mapping) if existing_mapping else {}
    existing_tokens = set(mapping.values()) if mapping else set()
    
    if not sorted_words:
        return text, mapping
        
    pattern_parts = []
    for word in sorted_words:
        escaped_word = re.escape(word)
        if match_whole_words:
            starts_with_word_char = bool(re.match(r'^\w', word, re.UNICODE))
            ends_with_word_char = bool(re.search(r'\w$', word, re.UNICODE))
            
            left_boundary = r'(?<!\w)' if starts_with_word_char else r''
            right_boundary = r'(?!\w)' if ends_with_word_char else r''
            
            pattern_parts.append(f"{left_boundary}{escaped_word}{right_boundary}")
        else:
            pattern_parts.append(escaped_word)
            
    # Combine into a single regex pattern. This guarantees we don't accidentally
    # match and replace inside already generated tokens in subsequent passes.
    pattern = '|'.join(pattern_parts)
    
    def replacer(match):
        matched_str = match.group(0)
        # Using exact case-sensitive match for the dictionary key as before
        if matched_str not in mapping:
            token = generate_token(existing_tokens)
            existing_tokens.add(token)
            mapping[matched_str] = token
        return mapping[matched_str]
    
    result_text = re.sub(pattern, replacer, text, flags=re.UNICODE | re.IGNORECASE)

    return result_text, mapping

def deanonymize_text(text: str, mapping: Dict[str, str]) -> str:
    """
    Restore original words based on the token mapping.
    """
    result_text = text
    
    # We replace tokens with their original words.
    # Tokens are unique and structured, so direct replacement is safe.
    for original_word, token in mapping.items():
        # Escape token just in case, although it's alphanumeric + <[]>
        escaped_token = re.escape(token)
        result_text = re.sub(escaped_token, original_word, result_text)
        
    return result_text
