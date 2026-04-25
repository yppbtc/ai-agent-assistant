# 删除原来 ChatZhipuAI 相关的导入和初始化
# 改为以下内容：
from crewai import Agent, Task, Crew, Process, LLM   # 确保导入 LLM
import os
from dotenv import load_dotenv
from tools import save_ticket_to_file, send_ticket_result

load_dotenv()

# 使用 CrewAI 内置的 LLM 类连接智谱 AI（通过 OpenAI 兼容接口）
zhipu_llm = LLM(
    model="openai/glm-4-plus",                     # 固定前缀 openai/ + 模型名
    base_url="https://open.bigmodel.cn/api/paas/v4/",
    api_key=os.getenv("ZHIPU_API_KEY"),
)

# 之后的 Agent 定义中，llm=zhipu_llm 保持不变

# 其他 Agent 定义完全不变，只是将 llm=zhipu_llm 传入即可

# ============= Agent 1：客服接待员 =============
receptionist = Agent(
    role='客服接待员',
    goal='理解用户问题，记录用户诉求和联系方式',
    backstory="""你是一家电商公司的客服接待员，负责接待客户投诉或咨询。
    你需要记录客户的姓名、联系方式（邮箱）、问题描述。
    输出格式要清晰，便于后续处理。""",
    verbose=True,
    allow_delegation=False,
    llm=zhipu_llm
)

# ============= Agent 2：工单分类员 =============
classifier = Agent(
    role='工单分类员',
    goal='对客户问题进行分类，并给出初步处理建议',
    backstory="""你是一名经验丰富的工单处理员，能将客户问题准确分类。
    类别包括：售后问题、物流查询、产品咨询、投诉建议、其他。
    你需要给出简要的处理建议。""",
    verbose=True,
    allow_delegation=False,
    llm=zhipu_llm
)

# ============= Agent 3：工单处理员 =============
handler = Agent(
    role='工单处理员',
    goal='将工单保存到文件，并通过邮件回复客户',
    backstory="""
    你负责工单的最终处理。你必须使用 'save_ticket_to_file' 工具来保存工单，使用 'send_ticket_result' 工具来发送邮件。
    工单内容应包含：客户信息、问题分类、处理结果。
    """,
    verbose=True,
    allow_delegation=False,
    tools=[save_ticket_to_file,send_ticket_result],
    llm=zhipu_llm
)

# ============= 创建任务 =============
user_input = input("请描述您的问题（务必留下邮箱以便回复，格式：xxx@xx.com）：\n")


task1 = Task(
    description=f"""客户问题：{user_input}
    请提取客户的核心诉求，如果客户提供了邮箱，务必记录下来。
    输出格式示例：
    客户邮箱：xxx@xx.com
    问题描述：xxxx
    """,
    agent=receptionist,
    expected_output="包含客户邮箱和问题描述的结构化文本",  # ← 添加这行
)

task2 = Task(
    description="""根据上一步的客户问题，进行分类并给出处理建议。
    分类标签：[售后问题/物流查询/产品咨询/投诉建议/其他]
    输出格式：
    分类：xxx
    处理建议：xxx
    """,
    agent=classifier,
    expected_output="包含问题分类和处理建议的文本",  # ← 添加这行
)

task3 = Task(
    description="""整合前两步的结果，生成完整工单。

然后按顺序执行以下两个操作：

1. 调用 save_ticket_to_file 工具，参数 ticket_content 的值为工单的完整文本内容。

2. 调用 send_ticket_result 工具，参数 ticket_info 的值为一个 JSON 字符串，格式严格如下：
{{"customer_email": "客户邮箱地址", "result": "感谢您的反馈，我们已记录您的问题，将在24小时内处理。"}}

注意：ticket_info 必须是合法的 JSON 字符串，customer_email 的值从 task1 的输出中获取。
""",
    agent=handler,
    expected_output="工单已保存并发送邮件的确认信息",
    context=[task1, task2]
)

# ============= 启动流程 =============
crew = Crew(
    agents=[receptionist, classifier, handler],
    tasks=[task1, task2, task3],
    verbose=True,
    process=Process.sequential
)

result = crew.kickoff()
print("\n" + "=" * 50)
print("工单处理完成！")
print("=" * 50)
print(result)