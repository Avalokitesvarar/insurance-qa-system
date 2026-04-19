"""
Prompt模板管理
分离代码与Prompt，便于优化和版本控制
"""

# 问答系统Prompt
QA_PROMPT_TEMPLATE = """你是一位专业的保险经纪人，请基于以下保险产品信息回答用户问题。

相关产品信息：
{context}

用户问题：{question}

请提供专业、客观的建议，包括：
1. 直接回答用户问题
2. 如果涉及产品推荐，说明推荐理由
3. 提醒用户注意事项（如等待期、免责条款等）

注意：
- 只基于提供的产品信息回答，不要编造不存在的产品
- 如果信息不足，明确告知用户
- 涉及具体保费时，提醒用户以实际核保为准

回答："""

# 产品对比分析Prompt
COMPARISON_PROMPT_TEMPLATE = """请对以下保险产品进行专业对比分析：

{comparison_data}

请从以下角度分析：
1. **核心差异**：各产品在保障范围、保额、保费上的主要区别
2. **适用人群**：每款产品分别适合什么样的客户
3. **性价比分析**：综合保障和价格的性价比评估
4. **选择建议**：针对不同需求给出推荐

要求：
- 客观中立，不偏袒任何产品
- 指出各产品的优势和不足
- 给出明确的选择建议"""

# 需求分析Prompt
NEEDS_ANALYSIS_TEMPLATE = """基于以下客户信息，分析保险需求并推荐合适的产品：

客户信息：
- 年龄：{age}岁
- 性别：{gender}
- 职业：{occupation}
- 家庭状况：{family_status}
- 年度预算：{budget}元
- 已有保障：{existing_coverage}

可选产品：
{available_products}

请提供：
1. **保障缺口分析**：基于客户情况，分析当前保障的不足
2. **产品类型优先级**：建议优先配置哪些险种（重疾/医疗/寿险/意外）
3. **具体产品推荐**：从可选产品中推荐2-3款，说明理由
4. **配置方案**：给出具体的保额和保费分配建议

要求：
- 方案必须在预算范围内
- 考虑客户的年龄、职业风险和家庭责任
- 优先保障核心风险"""

# 条款解读Prompt
POLICY_EXPLANATION_TEMPLATE = """请用通俗易懂的语言解释以下保险条款：

条款内容：
{policy_text}

用户问题：{question}

请：
1. 用简单的语言解释条款含义
2. 举例说明什么情况下适用/不适用
3. 提醒用户需要特别注意的地方

避免使用过多专业术语，确保普通用户能理解。"""


def get_qa_prompt():
    """获取问答Prompt"""
    from langchain.prompts import PromptTemplate
    return PromptTemplate(
        template=QA_PROMPT_TEMPLATE,
        input_variables=["context", "question"]
    )


def get_comparison_prompt():
    """获取对比分析Prompt"""
    return COMPARISON_PROMPT_TEMPLATE


def get_needs_analysis_prompt():
    """获取需求分析Prompt"""
    return NEEDS_ANALYSIS_TEMPLATE


def get_policy_explanation_prompt():
    """获取条款解读Prompt"""
    return POLICY_EXPLANATION_TEMPLATE
