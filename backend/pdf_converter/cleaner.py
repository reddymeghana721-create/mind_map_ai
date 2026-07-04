import re


class TextCleaner:
    """
    Cleans raw PDF-extracted text before it's saved or sent to an LLM.

    Handles:
    - Exact duplicate consecutive lines
    - Drop-cap artifacts (e.g. "H" + "ow do we tell" -> "How do we tell")
    - Duplicated caption labels (e.g. "Figure 5.3" + "Figure 5.3 (a) Open..." -> keeps only the full one)
    - Broken/overlapping numbered section headings
      (e.g. "5.1 WHA" + "T ARE LIFE PROCESSES?" -> "5.1 WHAT ARE LIFE PROCESSES?")
      (e.g. "5.4 TRANSPORT" + "ANSPORTATION" + "TION" -> "5.4 TRANSPORTATION")
    - Letter-spaced headers (e.g. "Q\\nU\\nE\\nS\\nT\\nI\\nO\\nN\\nS" -> "QUESTIONS")
    - Repeated page furniture (page numbers, "Reprint 2026-27", running headers)
    - Bullet artifacts (stray "n" used as a bullet character)
    """

    PAGE_FURNITURE_PATTERNS = [
        r'^Reprint\s+\d{4}-\d{2,4}$',
        r'^\d{1,4}$',
    ]

    # Matches numbered section headings like "5.1", "5.2.1", "5.4"
    HEADING_NUMBER_RE = re.compile(r'^\d+(\.\d+){0,3}\s+\S')

    def __init__(self, repeated_headers=None):
        self.repeated_headers = repeated_headers or []

    def clean(self, text: str) -> str:
        lines = text.split("\n")

        lines = self._strip_whitespace(lines)
        lines = self._collapse_immediate_duplicates(lines)
        lines = self._merge_dropcap_lines(lines)
        lines = self._drop_caption_prefix_duplicates(lines)
        lines = self._merge_numbered_heading_fragments(lines)
        lines = self._join_letter_spaced_runs(lines)
        lines = self._remove_page_furniture(lines)
        lines = self._fix_bullet_markers(lines)
        lines = self._collapse_immediate_duplicates(lines)
        lines = self._collapse_blank_lines(lines)

        return "\n".join(lines).strip()

    # ---------- Step 1: whitespace ----------
    def _strip_whitespace(self, lines):
        return [line.strip() for line in lines]

    # ---------- Step 2: exact consecutive duplicates ----------
    def _collapse_immediate_duplicates(self, lines):
        cleaned = []
        prev = None
        for line in lines:
            if line == prev and line != "":
                continue
            cleaned.append(line)
            prev = line
        return cleaned

    # ---------- Step 3: drop-cap merge ----------
    def _merge_dropcap_lines(self, lines):
        cleaned = []
        i = 0
        n = len(lines)
        while i < n:
            current = lines[i].strip()
            if (
                len(current) == 1 and current.isalpha() and current.isupper()
                and i + 1 < n
                and lines[i + 1].strip()
                and lines[i + 1].strip()[0].islower()
            ):
                merged = current + lines[i + 1].strip()
                cleaned.append(merged)
                i += 2
            else:
                cleaned.append(lines[i])
                i += 1
        return cleaned

    # ---------- Step 4: drop short caption labels fully repeated in next line ----------
    # e.g. "Figure 5.3" followed by "Figure 5.3 (a) Open and (b) closed stomatal pore"
    def _drop_caption_prefix_duplicates(self, lines):
        cleaned = []
        i = 0
        n = len(lines)
        while i < n:
            current = lines[i].strip()
            if (
                current and len(current) <= 40
                and i + 1 < n
                and lines[i + 1].strip().startswith(current)
                and lines[i + 1].strip() != current
            ):
                i += 1  # skip the short duplicate label, keep the fuller next line
                continue
            cleaned.append(lines[i])
            i += 1
        return cleaned

    # ---------- Step 5: reconstruct broken numbered section headings ----------
    # Only applies to lines starting with a section number (e.g. "5.1", "5.4.2")
    # since that's the only place this PDF artifact reliably occurs — keeps
    # this from ever touching normal standalone headings like "QUESTIONS?" or "ATP".
    def _merge_numbered_heading_fragments(self, lines):
        cleaned = []
        i = 0
        n = len(lines)

        while i < n:
            line = lines[i]
            if self.HEADING_NUMBER_RE.match(line.strip()):
                merged = line
                j = i + 1
                while j < n and self._is_short_caps_fragment(lines[j]):
                    new_merged = self._merge_two(merged, lines[j])
                    if new_merged is None:
                        break
                    merged = new_merged
                    j += 1
                cleaned.append(merged)
                i = j
            else:
                cleaned.append(line)
                i += 1

        return cleaned

    def _is_short_caps_fragment(self, line):
        s = line.strip()
        if not s or len(s) > 40:
            return False
        if s.endswith(('.', ',', ';', ':')):
            return False
        letters = [c for c in s if c.isalpha()]
        if len(letters) < 1:
            return False
        upper_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
        return upper_ratio > 0.8

    def _merge_two(self, a, b):
        """
        Merge fragment b into a by finding the largest overlap between
        the end of a and the start of b (handles decorative repeated-text
        artifacts), falling back to plain concatenation (k=0) when there's
        no real overlap (handles plain word-splits like "RESPIR" + "ATION").
        """
        a_norm, _ = self._normalize_with_map(a)
        b_norm, b_map = self._normalize_with_map(b)

        if not a_norm or not b_norm:
            return None

        max_check = min(len(a_norm), len(b_norm))
        for k in range(max_check, -1, -1):
            if a_norm.endswith(b_norm[:k]):
                if k >= len(b_norm):
                    return a  # b fully contained in a already, nothing to add
                start_idx = b_map[k]
                remainder = b[start_idx:]
                return a + remainder

        return None  # shouldn't happen since k=0 always matches

    def _normalize_with_map(self, s):
        chars = []
        idx_map = []
        for idx, ch in enumerate(s):
            if ch.isalpha():
                chars.append(ch.lower())
                idx_map.append(idx)
        return "".join(chars), idx_map

    # ---------- Step 6: join letter-spaced headers ----------
    def _join_letter_spaced_runs(self, lines):
        cleaned = []
        i = 0
        n = len(lines)

        while i < n:
            if self._is_single_char_line(lines[i]):
                run = [lines[i]]
                j = i + 1
                while j < n and self._is_single_char_line(lines[j]):
                    run.append(lines[j])
                    j += 1

                if len(run) >= 3:
                    joined = "".join(c.strip() for c in run)
                    cleaned.append(joined)
                    i = j
                    continue

            cleaned.append(lines[i])
            i += 1

        return cleaned

    def _is_single_char_line(self, line):
        stripped = line.strip()
        return len(stripped) == 1 and (stripped.isalpha() or stripped == "?")

    # ---------- Step 7: page furniture ----------
    def _remove_page_furniture(self, lines):
        cleaned = []
        for line in lines:
            stripped = line.strip()
            if stripped in self.repeated_headers:
                continue
            if any(re.match(pattern, stripped) for pattern in self.PAGE_FURNITURE_PATTERNS):
                continue
            cleaned.append(line)
        return cleaned

    # ---------- Step 8: bullet markers ----------
    def _fix_bullet_markers(self, lines):
        cleaned = []
        for line in lines:
            match = re.match(r'^n\s+(.*)$', line)
            if match and len(match.group(1)) > 3:
                cleaned.append(f"• {match.group(1)}")
            else:
                cleaned.append(line)
        return cleaned

    # ---------- Step 9: blank line collapsing ----------
    def _collapse_blank_lines(self, lines):
        cleaned = []
        prev_blank = False
        for line in lines:
            is_blank = (line.strip() == "")
            if is_blank and prev_blank:
                continue
            cleaned.append(line)
            prev_blank = is_blank
        return cleaned