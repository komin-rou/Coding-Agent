from pathlib import Path
#`Path` 用来包装文件 / 目录路径，提供面向对象的文件操作。
import subprocess
import sys




PROJECT_ROOT = Path(__file__).resolve().parent
#.parrent表示tools.py 所在目录
# resolve()：将路径规范化为绝对路径，处理 .. 等路径片段
# relative_to(PROJECT_ROOT)：判断最终路径是否仍位于项目目录内

BLOCKED_PARTS = {
    ".env",
    ".venv",
    ".git",
    "__pycache__",
}


def resolve_safe_path(file_path: str):

    path = (PROJECT_ROOT / file_path).resolve()

    try:
        relative_path = path.relative_to(PROJECT_ROOT)

    except ValueError:
        return None

    for part in relative_path.parts:
        if part in BLOCKED_PARTS:
            return None

    return path


def read_file(file_path: str) -> str:
    """
    读取文本文件内容。
    """

    path = resolve_safe_path(file_path)

    if path is None:
        return f"拒绝访问：路径超出项目目录: {file_path}"

    if not path.exists():
        return f"文件不存在: {file_path}"

    if not path.is_file():
        return f"这不是一个文件: {file_path}"


    try:
        return path.read_text(encoding="utf-8")
        #读取文本文件，以 utf-8 解码，返回字符串。

    except Exception as e:
        return f"读取文件失败: {e}"

READ_FILE_TOOL = {
    "type": "function",

    "function":
    {
        "name": "read_file",

        "description": "读取指定文本文件的内容",

        "parameters": #参数
        {
            "type": "object",

            "properties":#属性，有哪些参数，每个参数类型 + 说明
            {
                "file_path":
                {
                    "type": "string",
                    "description": "需要读取的文件路径"
                }
            },

            "required": ["file_path"]
        }
    }
}

# ==========================================
# 工具 2：列出目录内容
# 复用时主要修改：工具名称、参数和返回内容
# ==========================================

def list_files(directory: str = ".") -> str:#directory目录

    path = resolve_safe_path(directory)

    if path is None:
        return f"拒绝访问：目录路径不安全: {directory}"

    if not path.exists():
        return f"目录不存在: {directory}"

    if not path.is_dir():
        return f"不是目录: {directory}"

    try:
        items = []

        for item in sorted(path.iterdir()):
            if item.name in BLOCKED_PARTS:
                continue
            item_type = "目录" if item.is_dir() else "文件"
            items.append(f"[{item_type}] {item.name}")

        return "\n".join(items) if items else "目录为空"

    except Exception as e:
        return f"列出目录失败: {e}"


# ==========================================
# 工具 Schema：提供给模型
# ==========================================

LIST_FILES_TOOL = {
    "type": "function",
    "function":
    {
        "name": "list_files",
        "description": "列出指定目录中的文件和子目录",
        "parameters": #参数
        {
            "type": "object",
            "properties": #属性
            {
                "directory":
                {
                    "type": "string",
                    "description": "需要查看的目录路径"
                }
            },
            "required": ["directory"]
        }
    }
}

def write_file(file_path: str, content: str) -> str:

    # 1. 把字符串路径转换成 Path 对象
    path = resolve_safe_path(file_path)

    if path is None:
        return f"拒绝写入：路径不安全: {file_path}"

    try:
        # 2. 把 content 写入文件
        # 提示：你之前见过 read_text()
        # 写入对应的是 write_text()
        path.write_text(content,encoding="utf-8")

        # 3. 返回执行结果
        return f"文件写入成功: {file_path}"

    except Exception as e:
        return f"文件写入失败: {e}"


WRITE_FILE_TOOL = {
    "type": "function",
    "function":
    {
        "name": "write_file",
        "description": "写入代码",
        "parameters": #参数
        {
            "type": "object",
            "properties": #属性
            {
                "file_path":
                {
                    "type": "string",
                    "description": "需要写入的文件路径"
                },
                "content":

                {
                    "type": "string",
                    "description": "需要写入的内容"
                }
            },
            "required": ["file_path","content"]
        }
    }
}

def run_python(file_path: str) -> str:

    path = resolve_safe_path(file_path)

    if path is None:
        return f"拒绝执行：路径不安全: {file_path}"

    if path.suffix != ".py":
        return f"拒绝执行：只允许运行 Python 文件: {file_path}"

    try:

        result = subprocess.run(
            [sys.executable, str(path)],#python使用的是系统python，sys.executable是使用当前环境下的python
            capture_output=True,#把程序的输出和错误抓回来
            text=True,#返回字符串，而不是 bytes
            timeout=10#最多运行 10 秒，防止程序卡死
        )

        return (
            f"stdout:\n{result.stdout}\n"#standard output
            f"stderr:\n{result.stderr}\n"#standard error
            f"returncode: {result.returncode}"
        )

    except Exception as e:
        return f"Python 执行失败: {e}"


RUN_PYTHON_TOOL = {
    "type": "function",
    "function":
    {
        "name":"run_python",
        "description":"运行目标python",
        "parameters":
        {
            "type": "object",
            "properties":
            {
                "file_path":
                {
                    "type":"string",
                    "description":"需要运行的python文件路径"
                }
            },
            "required": ["file_path"]
        }
    }
}