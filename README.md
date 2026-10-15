# Coding Agent V1

一个基于 Python 和 LLM Tool Calling 实现的最小 Coding Agent。

## 项目目标

理解并实现 Coding Agent 的基本工作机制，包括工具调用、Agent Loop、代码执行和自动错误修复。

## 已实现功能

- 使用 LLM 自主选择工具
- 列出项目文件、读取和修改代码
- 执行 Python 文件并获取运行结果
- 根据报错尝试自动修复代码
- 修改文件前请求用户确认
- 基础文件访问安全限制
- 记录 Agent 运行状态和工具调用历史
- 检测连续重复的工具调用

## 项目结构

- `main.py`：Agent Loop、工具分发、State 和 Control
- `llm.py`：LLM API 调用
- `tools.py`：工具实现及工具定义
- `example.py`：测试示例

## 当前版本

V1.0.0 — 最小可运行 Coding Agent。

本项目主要用于学习 Agent 的工作原理，尚不适用于生产环境。