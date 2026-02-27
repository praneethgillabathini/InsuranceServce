import re
from ..config import settings


class PolicyPruner:
    def __init__(self):
        raw_keywords = settings.policy_pruner.junk_keywords
        self.header_pattern = re.compile(r'^(#+)\s+(.*)')
        pattern_str = '|'.join(map(re.escape, raw_keywords))
        self.junk_pattern = re.compile(rf'\b({pattern_str})(?:s|es)?\b', re.IGNORECASE)

    def prune(self, markdown_text: str) -> str:
        lines = markdown_text.split('\n')
        kept_lines = []
        is_skipping = False
        skip_level = 0

        for line in lines:
            header_match = self.header_pattern.match(line.strip())
            if header_match:
                header_level = len(header_match.group(1))
                header_text = header_match.group(2)
                clean_header = re.sub(r'[*_]', '', header_text)
                if self.junk_pattern.search(clean_header):
                    is_skipping = True
                    skip_level = header_level
                    continue
                elif is_skipping and header_level <= skip_level:
                    is_skipping = False
            if not is_skipping:
                kept_lines.append(line)

        return '\n'.join(kept_lines)
