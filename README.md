# 大模型对话助手 + Agent智能体

基于CrewAI框架开发的多Agent智能工单处理系统，集成智谱AI在线大模型，客服接待→工单分类→工单处理的全自动化流程。

## 功能
- Agent 1 客服接待员：理解用户问题，提取诉求和联系方式
- Agent 2 工单分类员：对问题自动分类（售后/物流/咨询/投诉等）
- Agent 3 工单处理员：保存工单到本地文件，并通过邮件回复客户
- 三个Agent顺序协作，全程无需人工干预

## 文件结构
- agent_ticket_workflow.py：Agent 定义、任务编排、流程启动
- tools.py：工具函数（保存工单到文件、发送邮件）

## 运行方式
1. 安装依赖：pip install crewai zhipuai
2. 在 .env 文件中配置：ZHIPU_API_KEY、EMAIL_FROM_ADDR、EMAIL_PWD（QQ邮箱授权码）
3. 运行：python agent_ticket_workflow.py
4. 按提示输入客户问题（需包含邮箱），等待Agent自动处理
