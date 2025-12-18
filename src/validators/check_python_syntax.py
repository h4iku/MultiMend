import ast
import codeop
import tokenize
from io import BytesIO


def format_python_code(code_str):
    """
    Formats a string of python code concatenated with spaces into valid, indented python code.

    Returns the original string if the input is invalid or deemed too complex to format.
    """
    if not code_str or not code_str.strip():
        return ""

    tokens = []
    try:
        # iterate manually to catch TokenError (e.g., unclosed strings at EOF)
        # while preserving the tokens collected so far.
        for t in tokenize.tokenize(BytesIO(code_str.encode("utf-8")).readline):
            tokens.append(t)
    except tokenize.TokenError:
        # This occurs if the string is cut off in the middle of a multi-line string
        # or quoted string. We ignore the error and process what we have.
        pass

    # --- COMPLEXITY & SANITY CHECK ---
    # Heuristic to detect weird inputs to avoid processing.
    max_nesting = 0
    curr_nesting = 0
    error_token_count = 0

    for t in tokens:
        if t.type == tokenize.ERRORTOKEN:
            error_token_count += 1
            # Specific check for Regex patterns or non-Python syntax:
            # '?' is invalid in Python code (outside strings) but common in Regex (?:...)
            # If we see a raw '?', it's not python code we should format.
            if "?" in t.string:
                return code_str

        elif t.exact_type in (tokenize.LPAR, tokenize.LSQB, tokenize.LBRACE):
            curr_nesting += 1
            max_nesting = max(max_nesting, curr_nesting)
        elif t.exact_type in (tokenize.RPAR, tokenize.RSQB, tokenize.RBRACE):
            curr_nesting -= 1

    # Thresholds:
    # 1. Depth > 20
    # 2. Error Ratio > 10%
    if max_nesting > 20:
        return code_str

    if len(tokens) > 5 and (error_token_count / len(tokens) > 0.1):
        return code_str
    # ---------------------------------

    # Filter out tokens that are artifacts of the initial parsing
    meaningful_tokens = [
        t
        for t in tokens
        if t.type
        not in (
            tokenize.ENCODING,
            tokenize.NL,
            tokenize.NEWLINE,
            tokenize.INDENT,
            tokenize.DEDENT,
            tokenize.ENDMARKER,
        )
    ]

    formatted_lines = []
    current_stmt = []
    indent_level = 0
    paren_level = 0

    # Keywords that start a block
    block_start_keywords = {
        "if",
        "for",
        "while",
        "def",
        "class",
        "with",
        "try",
        "except",
        "elif",
        "else",
        "finally",
        "match",
        "case",
    }

    # Keywords that must align with the block starter (dedent before printing)
    dedent_keywords = {"elif", "else", "except", "finally"}

    # Keywords that typically start a new statement
    stmt_keywords = {
        "if",
        "for",
        "while",
        "def",
        "class",
        "with",
        "try",
        "except",
        "elif",
        "else",
        "finally",
        "print",
        "return",
        "raise",
        "break",
        "continue",
        "pass",
        "import",
        "from",
        "assert",
        "del",
        "global",
        "nonlocal",
    }

    # Keywords that extend an expression (logic operators)
    # We shouldn't split before these even if the previous part looks like a valid statement
    continuation_keywords = {"not", "and", "or", "is", "in", "lambda", "yield"}

    def clean_unparse(tokens):
        """
        Reconstructs a clean string from tokens using AST if possible,
        or a heuristic token joining if AST fails.
        """
        # 1. Try AST Unparse
        # Join with spaces to ensure tokens aren't merged for parsing checks
        text = " ".join([t.string for t in tokens])
        try:
            if hasattr(ast, "unparse"):
                tree = ast.parse(text)
                return ast.unparse(tree)
        except Exception:
            pass

        # 2. Heuristic Reconstruction (Fallback)
        # This handles incomplete code or syntax errors by reconstructing
        # the string token-by-token with basic spacing rules.

        result = []
        prev_tok = None

        # Keywords that typically require a space before an opening parenthesis
        space_before_paren_keywords = {
            "if",
            "for",
            "while",
            "with",
            "except",
            "assert",
            "return",
            "and",
            "or",
            "not",
            "is",
            "in",
            "lambda",
            "yield",
        }

        for t in tokens:
            token_str = t.string

            # Determine if we need a space before this token
            if not prev_tok:
                prefix = ""
            else:
                prev_str = prev_tok.string
                prev_type = prev_tok.type

                # No space before punctuation/delimiters
                if token_str in {",", ".", ":", ";", ")", "]", "}"}:
                    # Exception: Space before '.' if it is part of relative import "from . import"
                    if token_str == "." and prev_str == "from":
                        prefix = " "
                    else:
                        prefix = ""

                # Handling Opening Parentheses/Brackets
                elif token_str in {"(", "[", "{"}:
                    if (
                        prev_type == tokenize.NAME
                        and prev_str not in space_before_paren_keywords
                    ):
                        # Function call or indexing: func(), list[] -> No space
                        prefix = ""
                    elif prev_str in {"(", "[", "{"}:
                        # Nested: (( -> No space
                        prefix = ""
                    else:
                        # Default space: "if (", "1 + ("
                        prefix = " "

                # No space after opening Parentheses/Brackets or dot
                elif prev_str in {"(", "[", "{", "."}:
                    prefix = ""

                # Default space around operators and between names
                else:
                    prefix = " "

            result.append(prefix + token_str)
            prev_tok = t

        return "".join(result)

    i = 0
    while i < len(meaningful_tokens):
        token = meaningful_tokens[i]
        current_stmt.append(token)

        # Track parenthesis/bracket nesting level
        if token.exact_type in (tokenize.LPAR, tokenize.LSQB, tokenize.LBRACE):
            paren_level += 1
        elif token.exact_type in (tokenize.RPAR, tokenize.RSQB, tokenize.RBRACE):
            paren_level -= 1

        split_here = False
        is_block_header = False

        # We only split logical lines when nesting is zero
        if paren_level == 0:
            # Colon Detection (Block headers)
            if token.exact_type == tokenize.COLON:
                # Check if the statement started with a block keyword
                if current_stmt and current_stmt[0].string in block_start_keywords:
                    split_here = True
                    is_block_header = True

            # Semicolon Detection
            elif token.string == ";":
                split_here = True

            # Lookahead for new statement boundaries
            elif i + 1 < len(meaningful_tokens):
                next_tok = meaningful_tokens[i + 1]

                # A. Next token is a keyword that starts a new line
                if next_tok.string in stmt_keywords:
                    should_split = True

                    # Exception 1: Ternary 'if' (x = 1 if y else z)
                    if next_tok.string == "if":
                        is_ternary = False
                        # Scan ahead for 'else' before ':'
                        for k in range(i + 2, len(meaningful_tokens)):
                            tk = meaningful_tokens[k]
                            if tk.string == ":" and tk.exact_type == tokenize.COLON:
                                break
                            if tk.string == "else":
                                is_ternary = True
                                break
                        if is_ternary:
                            should_split = False

                    # Exception 2: 'import' following 'from' (from x import y)
                    elif next_tok.string == "import":
                        if current_stmt and current_stmt[0].string == "from":
                            should_split = False

                    # Exception 3: Ternary 'else' (x if y else z) vs Block 'else' (else:)
                    elif next_tok.string == "else":
                        # Assume ternary (don't split) unless definitively followed by a colon
                        should_split = False
                        if i + 2 < len(meaningful_tokens):
                            if meaningful_tokens[i + 2].exact_type == tokenize.COLON:
                                should_split = True

                    if should_split:
                        split_here = True

                # General Syntax Check
                # If "Current + Next" is invalid syntax, but "Current" is valid, split.
                elif next_tok.type == tokenize.NAME:
                    # Don't split if next token is a continuation keyword
                    if next_tok.string in continuation_keywords:
                        pass
                    else:
                        try:
                            curr_text = " ".join([t.string for t in current_stmt])
                            ast.parse(curr_text)
                            is_curr_valid = True
                        except SyntaxError:
                            is_curr_valid = False

                        if is_curr_valid:
                            try:
                                ext_text = curr_text + " " + next_tok.string
                                ast.parse(ext_text)
                            except SyntaxError:
                                split_here = True

        # Finalize the line if split detected or end of stream
        if split_here or i == len(meaningful_tokens) - 1:
            # Formatting logic
            line_str = clean_unparse(current_stmt).strip()
            if line_str.endswith(";"):
                line_str = line_str[:-1]

            # Indentation Logic

            # Check for dedent keywords (else, elif, etc.)
            first_word = line_str.split(" ")[0] if line_str else ""
            if first_word in dedent_keywords:
                indent_level = max(0, indent_level - 1)

            # Append the line
            formatted_lines.append("    " * indent_level + line_str)

            # Prepare indent for next line
            if is_block_header:
                indent_level += 1
            else:
                # If statement finished and indentation is deep, dedent.
                if indent_level > 0:
                    indent_level -= 1

            current_stmt = []

        i += 1

    return "\n".join(formatted_lines)


def is_valid_python_snippet(snippet: str) -> bool:
    """
    Check if a Python snippet is syntactically valid in a common Python context.
    """
    snippet = snippet.strip()

    if not snippet:
        return True

    indented = f"    {snippet}"

    environments = [
        snippet,  # Top-level
        f"def _dummy():\n{indented}",  # return, yield, yield from
        f"async def _dummy():\n{indented}",  # await, async for, async with
        f"class _Dummy:\n{indented}",  # class-level
        f"for _ in range(1):\n{indented}",  # break, continue
        f"if True:\n    pass\n{snippet}",  # elif, else
    ]

    for code in environments:
        try:
            codeop.compile_command(code)
            return True
        except Exception:
            continue

    return False


def get_valid_python(snippet: str) -> str:
    snippet = snippet.strip()

    if is_valid_python_snippet(snippet):
        return snippet

    try:
        return format_python_code(snippet)
    except SyntaxError:
        return snippet
