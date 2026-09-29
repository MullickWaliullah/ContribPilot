from __future__ import annotations
import logging
import json

from groq import Groq
from app.core.config import settings

from pathlib import Path

logger = logging.getLogger(__name__)

_groq_client : Groq | None = None

PROMPT_PATH = Path(__file__).parent / "prompts" / "breakdown.txt"

def _get_client() -> Groq :
    global _groq_client

    if _groq_client is not None:
        return _groq_client

    api_key = settings.LLM_API_KEY

    if not api_key:
        raise RuntimeError("LLM API KEY is not configured. Please set LLM API KEY")

    _groq_client=Groq(api_key=api_key)

    return _groq_client

def _load_prompt() -> str :
    if not PROMPT_PATH.exists():
        raise FileNotFoundError(f"Breakdown prompt file not found : {PROMPT_PATH}")

    if not PROMPT_PATH.is_file():
        raise FileNotFoundError(f"Breakdown prompt path is not a file : {PROMPT_PATH}")
    
    with open(PROMPT_PATH,"r", encoding="utf-8") as File:
        return File.read()


def _truncate(text : str, limit : int) -> str :
    if limit<0:
        raise ValueError("Truncate limit cannot be negative")

    if len(text)<=limit:
        return text

    return text[:limit]+"...[truncate]"

def _build_user_message(issue : dict, repository_context : dict) -> str :
    repository_name = repository_context.get("repository_name","")
    repository_description = repository_context.get("repository_description","")
    primary_language = repository_context.get("primary_language","")
    repository_structure = repository_context.get("repository_structure",[])
    relevant_files = repository_context.get("relevant_files",[])
    relevant_source_code = repository_context.get("relevant_source_code",{})
    existing_tests = repository_context.get("existing_tests",{})
    issue_title = issue.get("title","")
    issue_body = _truncate(str(issue.get("body","")),3000)
    issue_labels = issue.get("labels",[])


    if isinstance(issue_labels,list):
        issue_labels_text = ",".join(
            str(label) for label in issue_labels
        )
    else:
        issue_labels_text = str(issue_labels)


    if isinstance(repository_structure,list):
        structure_text = "\n".join(
            str(path)
            for path in repository_structure[:200]
        )
    else:
        structure_text=str(repository_structure)


    if isinstance(relevant_files,list):
        relevant_files_text = "\n".join(
            str(path)
            for path in relevant_files[:200]
        )
    else:
        relevant_files_text=str(relevant_files)


    source_sections = []

    if isinstance(relevant_source_code,dict):
        for file_path, content in list(relevant_source_code.items())[:200]:
            source_sections.append(
                f"--- FILE : {file_path}--- \n"
                f"{_truncate(str(content),4000)}\n"
                f"--- END FILE ---"
            )
    elif relevant_source_code :
        source_sections.append(
            _truncate(str(relevant_source_code),4000)
        )

    source_code_text = "\n\n".join(source_sections)


    test_sections = []
    if isinstance(existing_tests, dict):
        for file_path, content in list(existing_tests.items())[:200]:
            test_sections.append(
                f"--- TEST FILE : {file_path} ---\n"
                f"{_truncate(str(content),4000)}\n"
                f"--- END FILE---"
            )
    elif isinstance(existing_tests, list):
        test_sections.append(
            "\n".join( str(test) for test in existing_tests[:200])
        )

    elif existing_tests:
        test_sections.append(
            _truncate(str(existing_tests),4000)
        )

    existing_tests_text = "\n\n".join(test_sections)

    return f"""
    Issue Information :
    - Title : {issue_title}
    - Body : {issue_body}
    - Labels : {issue_labels_text}

    Repository Context : 
    - Repository Name : {repository_name}
    - Description : {repository_description}
    - Primary Language : {primary_language}
    - Directory Structure : {structure_text}

    - Relevant Files : {relevant_files_text}

    - Relevant Source Code: {source_code_text}

    - Existing Tests : {existing_tests_text}
""".strip()


def _validate_against_context(result : dict, repository_context : dict) -> dict :
    tree = repository_context.get("repository_structure", [])
    relevant_files = repository_context.get("relevant_files",[])
    source_code = repository_context.get("relevant_source_code",{})

    known_files : set[str] = set()

    if isinstance(tree, list):
        known_files.update(str(path) for path in tree)

    if isinstance(relevant_files, list):
        known_files.update(str(path) for path in relevant_files)

    if isinstance(source_code, dict):
        known_files.update(str(path) for path in source_code.keys())

    file_content : dict[str, str] = {}

    if isinstance(source_code,dict):
        for file_path, content in source_code.items():
            file_content[str(file_path)] = str(content)


    files_to_inspect = result.get("files_to_inspect",[])

    if not isinstance(files_to_inspect,list):
        files_to_inspect=[]

    valid_files = []

    for file_path in files_to_inspect:
        file_path=str(file_path).strip()

        if not file_path:
            continue

        if file_path in known_files:
            valid_files.append(file_path)

    result["files_to_inspect"] = valid_files


    relevant_symbols = result.get("relevant_symbols",[])

    if not isinstance(relevant_symbols, list):
        relevant_symbols=[]

    valid_symbol = []

    for symbol in relevant_symbols:
        symbol = str(symbol).strip()

        if not symbol:
            continue

        symbol_found = False

        if "." in symbol:
            parts = symbol.split(".",1)

            if len(parts) == 2:
                class_name, method_name = parts

                for content in file_content.values():
                    if (class_name in content and method_name in content):
                        symbol_found=True
                        break

        else:
            for content in file_content.values():
                if symbol in content:
                    symbol_found=True
                    break

        if symbol_found:
            valid_symbol.append(symbol)

    result["relevant_symbols"] = valid_symbol


    return result


def breakdown_issue(issue:dict, repository_context:dict) -> dict :
    client = _get_client()

    system_prompt = _load_prompt()

    user_message = _build_user_message(issue, repository_context)

    last_error = None
    raw_response = None

    for attempts in range(2):

        try:
            response = client.chat.completions.create(
                model=settings.LLM_API_MODEL,
                messages=[
                    {
                        "role":"system",
                        "content" : system_prompt
                    },
                    {
                        "role" : "user",
                        "content" : user_message
                    }
                ],
                temperature=0.2,
                max_tokens=1500,
                stream=False
            )

            raw_response = response.choices[0].message.content

            if not raw_response:
                raise ValueError("Groq retured an empty response")

            break
        except Exception as exc:
            last_error=exc

            logger.warning("Breakdown LLM Failed , attempts(%d/2): %s",attempts+1,exc)

    if not raw_response:
        raise RuntimeError(f" Breakdown LLM Failed after retry : {last_error}")

    try :
        data=json.loads(raw_response)
    except json.JSONDecodeError as exc:
        preview = raw_response[:500]

        raise ValueError("Groq return invalid json " f"Response preview : {preview}") from exc

    if not isinstance(data,dict):
        raise ValueError("Groq breakdown must be json object")

    data = _validate_against_context(data, repository_context)

    return data