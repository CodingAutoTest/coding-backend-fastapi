def classify_error(status: str, compile_output: str, stderr: str) -> str:
    if "Compilation Error" in status or compile_output:
        if "SyntaxError" in compile_output:
            return "Syntax Error"
        if "TypeError" in compile_output:
            return "Type Error"
        return "Compilation Error"

    if "Runtime Error" in status or stderr:
        for key, value in {
            "ZeroDivisionError": "Zero Division Error",
            "IndexError": "Index Error",
            "KeyError": "Key Error",
            "ValueError": "Value Error"
        }.items():
            if key in stderr:
                return value
        return "Runtime Error"

    if "Time Limit Exceeded" in status:
        return "Time Limit Exceeded"
    if "Memory Limit Exceeded" in status:
        return "Memory Limit Exceeded"

    return status
