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

def anonymize_text(text: str, words: List[str]) -> Tuple[str, Dict[str, str]]:
    """
    Anonymize occurrences of specific words in the text.
    Handles Polish diacritics and regex special characters safely.
    Replaces longest phrases first (greedy).
    """
    # Sort words by length descending for greedy matching
    sorted_words = sorted(words, key=len, reverse=True)
    
    mapping = {}
    existing_tokens = set()
    
    # We will build a single regex or iterate and replace.
    # Iterating and replacing with a negative lookaround is safe.
    
    result_text = text
    
    for word in sorted_words:
        escaped_word = re.escape(word)
        starts_with_word_char = bool(re.match(r'^\w', word, re.UNICODE))
        ends_with_word_char = bool(re.search(r'\w$', word, re.UNICODE))
        
        left_boundary = r'(?<!\w)' if starts_with_word_char else r''
        right_boundary = r'(?!\w)' if ends_with_word_char else r''
        
        pattern = f"{left_boundary}{escaped_word}{right_boundary}"
        
        def replacer(match):
            matched_str = match.group(0)
            if matched_str not in mapping:
                token = generate_token(existing_tokens)
                existing_tokens.add(token)
                mapping[matched_str] = token
            return mapping[matched_str]
        
        result_text = re.sub(pattern, replacer, result_text, flags=re.UNICODE | re.IGNORECASE)

    # Invert mapping to match requirements format if needed, but the spec says mapping is:
    # "Original Word": "<[ANON_XXXX]>"
    
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
