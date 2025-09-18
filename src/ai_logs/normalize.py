import hashlib
from collections import defaultdict
import re
from typing import List
from .schema import LogItem, Cluster

NUM_PATTERN = re.compile(r'\b\d+\b')
IDENTIFIER_PATTERN = re.compile(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b')
QUOTED_STRING_PATTERN = re.compile(r"'[^']*'")

def fingerprint(msg: str) -> str:
    template = NUM_PATTERN.sub('<NUM>', msg)
    template = QUOTED_STRING_PATTERN.sub("'<SIG>'", template)
    keywords = {'signal', 'port', 'module', 'net', 'driver', 'assignment', 'reference', 'instance', 'variable'}
    words = template.split()
    normalized_words = []
    
    for word in words:
        clean_word = re.sub(r'[^\w]', '', word)
        if clean_word and clean_word not in keywords and IDENTIFIER_PATTERN.match(clean_word):
            normalized_word = re.sub(r'\b' + re.escape(clean_word) + r'\b', '<ID>', word)
            normalized_words.append(normalized_word)
        else:
            normalized_words.append(word)
    
    template = ' '.join(normalized_words)
    
    return hashlib.md5(template.encode()).hexdigest()


def cluster_logs(items: List[LogItem]) -> List[Cluster]:
    clusters = defaultdict(list)
    
    for item in items:
        fp = fingerprint(item.msg)
        clusters[fp].append(item)
    
    result = []
    for i, (fp, cluster_items) in enumerate(clusters.items()):
        template = cluster_items[0].msg
        
        key = NUM_PATTERN.sub('<NUM>', template)
        key = QUOTED_STRING_PATTERN.sub("'<SIG>'", key)
        
        result.append(Cluster(
            id=f"cluster_{i}",
            key=key,
            count=len(cluster_items),
            items=cluster_items
        ))
    
    return result