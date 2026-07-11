import ast
import re
from typing import Optional

import pandas as pd
from langchain_core.prompts import ChatPromptTemplate


# =========================
# Router: does this look like a statistical / structured-data question?
# =========================

_STAT_KEYWORDS = [
    # English — aggregate / quantitative intent
    "how many", "how much", "count", "number of", "total number",
    "average", "avg", "mean", "median", "percentage", "percent", "%",
    "most common", "most frequent", "least common", "highest", "lowest",
    "maximum", "max ", "minimum", "min ", "sum of", "distribution",
    "breakdown", "compare", "which doctor", "which hospital", "list patients",
    "list all patients", "how old", "youngest", "oldest",
    # English — specific patient record lookup
    "patient record", "patient named", "information about patient",
    "details of patient", "show me patient",
    # Arabic — aggregate / quantitative intent
    "كام", "عدد", "متوسط", "معدل", "نسبة", "أكتر", "اكتر", "الأكثر",
    "أكثر", "إجمالي", "اجمالي", "أعلى", "اعلى", "أقل", "اقل",
    "قايمة المرضى", "لستة المرضى", "توزيع", "احصائ", "إحصائ",
    # Arabic — specific patient record lookup
    "بيانات المريض", "معلومات عن المريض", "معلومات المريض", "سجل المريض",
]


def is_statistical_query(question: str) -> bool:
    """Heuristic router: True if the question looks like it needs exact
    computation over the patient dataset rather than semantic document search."""
    q = question.lower()
    return any(keyword in q for keyword in _STAT_KEYWORDS)


# =========================
# Safe expression validation
# =========================

_ALLOWED_NAMES = {
    "df", "pd", "len", "round", "min", "max", "sum", "sorted", "abs",
    "True", "False", "None", "str", "int", "float", "list",
}

_BLOCKED_ATTRS = {
    "to_csv", "to_excel", "to_pickle", "to_sql", "to_json", "to_parquet",
    "to_hdf", "to_feather", "to_html", "to_clipboard",
    "eval", "query", "apply", "applymap", "exec", "open", "read_csv",
    "read_excel", "read_sql", "read_pickle", "read_json",
}

_FORBIDDEN_NODE_TYPES = (
    ast.Import, ast.ImportFrom, ast.Lambda, ast.FunctionDef, ast.AsyncFunctionDef,
    ast.ClassDef, ast.With, ast.AsyncWith, ast.Assign, ast.AugAssign, ast.AnnAssign,
    ast.Delete, ast.Global, ast.Nonlocal, ast.Try, ast.Raise, ast.While, ast.For,
    ast.AsyncFor, ast.Await,
)


def _is_safe_expression(code: str) -> bool:
    """Parse `code` as a single expression and validate it against a strict allow-list."""
    try:
        tree = ast.parse(code, mode="eval")
    except SyntaxError:
        return False

    for node in ast.walk(tree):
        if isinstance(node, _FORBIDDEN_NODE_TYPES):
            return False
        if isinstance(node, ast.Name) and node.id not in _ALLOWED_NAMES:
            return False
        if isinstance(node, ast.Attribute):
            if node.attr.startswith("_") or node.attr in _BLOCKED_ATTRS:
                return False
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in _BLOCKED_ATTRS:
                return False

    return True


def _extract_expression(raw_text: str) -> str:
    """Pull a single pandas expression out of the LLM's raw response."""
    text = raw_text.strip()
    text = re.sub(r"^```(?:python)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            return line
    return text


# =========================
# Result formatting (no LLM involved — keeps numbers exact)
# =========================

def _format_result(result) -> str:
    if isinstance(result, pd.Series):
        if len(result) == 0:
            return "No matching records were found."
        rows = [f"- **{idx}**: {val}" for idx, val in result.head(20).items()]
        suffix = f"\n\n_(showing {min(20, len(result))} of {len(result)})_" if len(result) > 20 else ""
        return "\n".join(rows) + suffix

    if isinstance(result, pd.DataFrame):
        if result.empty:
            return "No matching records were found."
        preview = result.head(10)
        return preview.to_markdown(index=False) + (
            f"\n\n_(showing 10 of {len(result)} rows)_" if len(result) > 10 else ""
        )

    if isinstance(result, float):
        return f"{result:,.2f}"

    if isinstance(result, (int, list)):
        return f"{result:,}" if isinstance(result, int) else str(result)

    return str(result)


# =========================
# Prompt for translating a question into a pandas expression
# =========================

_SCHEMA_DESCRIPTION = """
The DataFrame `df` has these columns:
- Name (string)
- Age (int)
- Gender (string: 'Male' or 'Female')
- Blood Type (string)
- Medical Condition (string: one of 'Cancer', 'Obesity', 'Diabetes', 'Asthma', 'Hypertension', 'Arthritis')
- Date of Admission (string, format YYYY-MM-DD)
- Doctor (string)
- Hospital (string)
- Insurance Provider (string)
- Billing Amount (float)
- Room Number (int)
- Admission Type (string: 'Urgent', 'Emergency', or 'Elective')
- Discharge Date (string, format YYYY-MM-DD)
- Medication (string)
- Test Results (string: 'Normal', 'Abnormal', or 'Inconclusive')
"""

_QUERY_GEN_PROMPT = ChatPromptTemplate.from_messages([
    ("human", """You are a data analyst. You are given a pandas DataFrame called `df`.
{schema}

Respond with ONLY a single Python expression that computes the answer using `df` and `pd`.
Rules:
- No imports, no assignments, no loops, no function definitions.
- No file, network, or system operations.
- Return ONLY the raw expression — no markdown fences, no explanation, no extra text.

Examples:
Q: How many patients have diabetes?
A: df[df['Medical Condition'] == 'Diabetes'].shape[0]

Q: What is the average age of patients with cancer?
A: df[df['Medical Condition'] == 'Cancer']['Age'].mean()

Q: كام مريض عنده ضغط؟
A: df[df['Medical Condition'] == 'Hypertension'].shape[0]

Q: Which doctor treats the most patients?
A: df['Doctor'].value_counts().head(1)

Q: متوسط تكلفة العلاج للمرضى اللي عندهم سكر؟
A: df[df['Medical Condition'] == 'Diabetes']['Billing Amount'].mean()

Question: {question}
Expression:""")
])


class PatientAnalytics:
    """
    Answers statistical / structured-data questions about the patient dataset
    by translating them into a validated pandas expression and executing it
    directly, instead of going through semantic (RAG) retrieval.
    """

    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.df = pd.read_csv(csv_path)
        self._chain = _QUERY_GEN_PROMPT

    def is_statistical_query(self, question: str) -> bool:
        return is_statistical_query(question)

    def _generate_expression(self, question: str, llm) -> str:
        messages = self._chain.format_messages(schema=_SCHEMA_DESCRIPTION, question=question)
        response = llm.invoke(messages)
        raw_text = getattr(response, "content", str(response))
        return _extract_expression(raw_text)

    def answer(self, question: str, llm) -> Optional[str]:
        """
        Try to answer `question` using the patient dataset directly.
        Returns None if the question couldn't be safely/successfully answered,
        so the caller can fall back to the normal RAG pipeline.
        """
        try:
            expression = self._generate_expression(question, llm)
        except Exception as e:
            print(f"⚠️ Analytics: failed to generate expression: {e}")
            return None

        if not _is_safe_expression(expression):
            print(f"⚠️ Analytics: rejected unsafe/invalid expression: {expression!r}")
            return None

        try:
            code = compile(ast.parse(expression, mode="eval"), "<analytics_expr>", "eval")
            result = eval(
                code,
                {"__builtins__": {}},
                {
                    "df": self.df,
                    "pd": pd,
                    "len": len,
                    "round": round,
                    "min": min,
                    "max": max,
                    "sum": sum,
                    "sorted": sorted,
                    "abs": abs,
                },
            )
        except Exception as e:
            print(f"⚠️ Analytics: execution failed for {expression!r}: {e}")
            return None

        formatted = _format_result(result)
        return (
            f"📊 *Calculated directly from the patient dataset ({len(self.df):,} records)*\n\n"
            f"{formatted}"
        )
