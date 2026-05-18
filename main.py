from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
from io import StringIO
import traceback
import re

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class CodeRequest(BaseModel):
    code: str

# Execute Python code
def execute_python_code(code: str):

    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
        exec(code)

        output = sys.stdout.getvalue()

        return {
            "success": True,
            "output": output
        }

    except Exception:

        output = traceback.format_exc()

        return {
            "success": False,
            "output": output
        }

    finally:
        sys.stdout = old_stdout

# Extract line numbers
def extract_error_lines(traceback_text):

    matches = re.findall(r'<string>", line (\d+)', traceback_text)

    return [int(x) for x in matches]

# API endpoint
@app.post("/code-interpreter")
def code_interpreter(req: CodeRequest):

    execution = execute_python_code(req.code)

    # Success case
    if execution["success"]:

        return {
            "error": [],
            "result": execution["output"]
        }

    # Error case
    error_lines = extract_error_lines(
        execution["output"]
    )

    return {
        "error": error_lines,
        "result": execution["output"]
    }