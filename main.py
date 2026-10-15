import json
import time
from llm import chat
from tools import (
    read_file,
    list_files,
    write_file,
    run_python,
    READ_FILE_TOOL,
    LIST_FILES_TOOL,
    WRITE_FILE_TOOL,
    RUN_PYTHON_TOOL,
)

TOOLS = [
    READ_FILE_TOOL,
    LIST_FILES_TOOL,
    WRITE_FILE_TOOL,
    RUN_PYTHON_TOOL

]


# ==========================================
# 配置区：以后复用主要修改这里
# ==========================================

MAX_ITERATIONS = 10




# ==========================================
# 工具执行器
# 作用：根据模型返回的工具名称，执行 Python 函数
# ==========================================

def execute_tool(tool_call):

    # 1. 获取工具名称
    tool_name = tool_call.function.name

    try:
        # 2. 先解析工具参数
        arguments = json.loads(tool_call.function.arguments)

        print(f"\n[TOOL] 工具名称: {tool_name}")
        print(f"[TOOL] 工具参数: {arguments}")

        # ==================================
        # 3. 工具调度区
        # 以后增加工具，主要修改这里
        # ==================================

        if tool_name == "read_file":

            result = read_file(
                arguments["file_path"]
            )

        elif tool_name == "list_files":

            result = list_files(
                arguments["directory"]
            )

        elif tool_name == "write_file":

            confirm = input(
                f"\nAgent 请求修改 {arguments['file_path']}，是否允许？(y/n): "
            )

            if confirm == "y":
                result = write_file(
                    arguments["file_path"],
                    arguments["content"]
                )

            else:
                result = "用户拒绝了文件修改"

        elif tool_name == "run_python":

            result = run_python(
                arguments["file_path"]
            )


        else:

            result = f"未知工具: {tool_name}"

        # 4. 输出执行结果
        print(f"[TOOL] 执行结果:\n{result}")

        # 5. 返回给 run_agent()
        return str(result)

    except (ValueError, TypeError, KeyError) as e:
        return f"工具参数错误: {e}"

    except Exception as e:
        return f"工具执行失败: {e}"



#用于检测工具调用是否重复，重复时有没有必要保留
#原理：文件内容相同，哈希值通常相同；文件内容变化，哈希值也会变化。
def check_repeated_call(state, tool_name, tool_arguments):

    history = state["tool_calls"]

    if not history:
        return False

    last_call = history[-1]

    same_name = last_call["name"] == tool_name
    same_arguments = last_call["arguments"] == tool_arguments

    if same_name and same_arguments:
        return True

    return False



# ==========================================
# Agent 主循环
# ==========================================

def run_agent(user_input):

    # 1. 初始化对话历史
    messages = [
        {
            "role": "system",
            "content": (
            """
            你是一个 Coding Agent，可以使用工具完成代码任务。

            工作原则：

            1. 每次调用工具前，判断这个调用是否有助于完成用户目标
            2. 已经获得的信息不要无意义重复获取
            3. 当用户目标已经满足，并且有足够证据验证成功时，停止调用工具，直接回答用户
            4. 工具执行失败时，根据错误结果决定下一步，不要无条件重复相同调用
            5. 修复代码时采用最小必要修改，不要修改与问题无关的代码或为了绕过错误而改变原测试条件；修复后应尽量使用原失败条件重新验证。

            需要了解文件真实内容时必须调用工具，不要编造。
            """
            )
        },
        {
            "role": "user",
            "content": user_input
        }
    ]

    state = {
        "goal": user_input,
        "tool_calls": [],
        "iteration": 0,
    }



    # 2. Agent Loop
    # 每轮最多执行一次模型请求
    for iteration in range(MAX_ITERATIONS):

        state["iteration"] = iteration + 1

        print(
            f"\n========== 第 {iteration + 1} 轮 =========="
        )

        # 调用 llm.py 中的 chat()
        #并测试耗时
        start_time = time.perf_counter()

        assistant_message = chat(
            messages=messages,
            tools=TOOLS
        )

        elapsed = time.perf_counter() - start_time

        print(f"[TIME] 本轮 LLM 耗时: {elapsed:.2f} 秒")

        # 保存模型回复
        messages.append(assistant_message)

        # 3. 模型没有请求工具 → 结束
        if not assistant_message.tool_calls:

            print("\n[STATE]")
            print(state)

            print("\nAgent:")
            print(assistant_message.content)

            return assistant_message.content

        # 4. 模型请求工具 → 执行这一批工具
        for tool_call in assistant_message.tool_calls:

            tool_name = tool_call.function.name
            tool_arguments = json.loads(
                tool_call.function.arguments
            )

            repeated = check_repeated_call(
                state,
                tool_name,
                tool_arguments
            )

            if repeated:
                result = (
                    "CONTROL_BLOCKED: 检测到连续相同的工具调用。"
                    "请检查已有结果，选择其他操作，"
                    "或在任务已完成时直接回答用户。"
                )

                print(f"\n[CONTROL] {result}")

            else:
                result = execute_tool(tool_call)

            #将调用工具的记录存进state
            state["tool_calls"].append({
                "name": tool_name,
                "arguments": tool_arguments,
                "result": result,
                "status": "blocked" if repeated else "executed"
            })



            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })

        # 本轮结束，自动回到循环顶部

    # 6. 达到最大迭代次数
    print("\n[STOP] 已达到最大迭代次数。")

    return "Agent 已达到最大迭代次数，任务可能尚未完成。"


# ==========================================
# 程序入口
# ==========================================

def main():

    user_input = input("User: ")

    run_agent(user_input)


if __name__ == "__main__":

    main()
