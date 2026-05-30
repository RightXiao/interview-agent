from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class InterviewTemplate:
    name: str
    label: str
    description: str
    question_style: str
    review_focus: list[str]
    follow_up_hints: list[str]
    study_plan_extra: list[str] = field(default_factory=list)


TEMPLATES: dict[str, InterviewTemplate] = {
    "bigtech": InterviewTemplate(
        name="bigtech",
        label="互联网大厂",
        description="面向字节、腾讯、阿里、美团、快手等一线互联网公司的面试风格",
        question_style="注重系统设计、算法思维、高并发场景和项目深度追问",
        review_focus=[
            "系统设计能力：能否从0到1描述架构方案",
            "技术深度：对核心技术栈的理解是否到位",
            "数据驱动：是否能量化业务效果",
            "高并发/高可用：是否考虑过极端场景",
            "闭环思维：从业务问题到技术方案再到效果验证",
        ],
        follow_up_hints=[
            "这个方案的QPS瓶颈在哪里？如何优化？",
            "如果数据量增长10倍，架构需要怎么调整？",
            "线上出过什么故障？你是怎么排查和解决的？",
            "这个技术选型和XX方案相比，优劣是什么？",
            "你在项目中遇到的最大技术挑战是什么？",
        ],
        study_plan_extra=[
            "深入学习系统设计经典案例（秒杀、Feed流、推荐系统）",
            "准备2-3个能体现技术深度的项目亮点",
            "复习高并发、分布式系统核心概念",
        ],
    ),
    "soe": InterviewTemplate(
        name="soe",
        label="央国企",
        description="面向银行、运营商、能源、央企信息化等部门的面试风格",
        question_style="注重基础知识扎实度、稳定性、合规意识和团队协作",
        review_focus=[
            "基础功底：计算机网络、操作系统、数据库原理是否扎实",
            "合规与安全：是否了解数据安全、等保、信创等要求",
            "稳定性优先：方案是否考虑容灾、备份、灰度发布",
            "文档与规范：是否有良好的文档习惯和代码规范意识",
            "团队协作：沟通能力和跨部门协作经验",
        ],
        follow_up_hints=[
            "请介绍一下计算机网络的七层模型",
            "数据库事务的ACID特性分别是什么？",
            "你对信创替代有什么了解？",
            "项目中如何保证数据安全和用户隐私？",
            "遇到需求变更频繁的情况，你是怎么处理的？",
        ],
        study_plan_extra=[
            "复习计算机基础（网络、OS、数据库原理）",
            "了解信创、等保2.0、数据安全法等政策法规",
            "准备体现稳定性和规范性的项目案例",
        ],
    ),
    "foreign": InterviewTemplate(
        name="foreign",
        label="外企",
        description="面向微软、Google、Amazon、Apple等外企的面试风格",
        question_style="注重英语表达、算法能力、行为面试（Behavioral）和系统设计",
        review_focus=[
            "English communication: Can you articulate technical concepts clearly",
            "Behavioral questions: STAR method for past experiences",
            "Algorithm & data structures: LeetCode medium/hard level",
            "System design: Scalable architecture with trade-off analysis",
            "Cultural fit: Ownership, bias for action, customer obsession",
        ],
        follow_up_hints=[
            "Tell me about a time you disagreed with your team. How did you resolve it?",
            "Describe a project where you had to learn a new technology quickly.",
            "How would you design a URL shortener serving 100M users?",
            "What's the most impactful thing you've done in your career?",
            "Walk me through your thought process for solving this problem.",
        ],
        study_plan_extra=[
            "Practice behavioral questions using the STAR method",
            "Grind LeetCode: focus on arrays, trees, graphs, and DP",
            "Prepare system design: practice on whiteboard or paper",
            "Improve English technical vocabulary",
        ],
    ),
    "unicorn": InterviewTemplate(
        name="unicorn",
        label="独角兽企业",
        description="面向SHEIN、米哈游、智谱AI、月之暗面等高速成长型公司的面试风格",
        question_style="注重快速落地能力、技术广度、学习能力和业务理解",
        review_focus=[
            "落地速度：能否快速从0到1交付",
            "技术广度：前后端、DevOps、数据是否都有涉猎",
            "业务理解：是否理解公司核心业务逻辑",
            "学习能力：面对新技术的学习速度和方法",
            "Owner意识：是否能独立推动项目闭环",
        ],
        follow_up_hints=[
            "如果让你一周内上线一个MVP，你会怎么做？",
            "你平时怎么学习新技术？最近学了什么？",
            "你觉得我们公司的核心竞争力是什么？",
            "一个需求从PRD到上线，你的完整工作流是什么？",
            "你有没有做过超出你职责范围的事情？",
        ],
        study_plan_extra=[
            "准备快速交付的项目案例（强调速度和结果）",
            "了解目标公司的产品和业务模式",
            "拓宽技术栈：了解云原生、CI/CD、容器化等",
        ],
    ),
    "boutique": InterviewTemplate(
        name="boutique",
        label="小而美公司",
        description="面向技术氛围好、团队精干的优质中小公司的面试风格",
        question_style="注重实际动手能力、代码质量、技术热情和团队契合度",
        review_focus=[
            "动手能力：能否现场写出可运行的代码",
            "代码质量：命名、结构、可读性是否过关",
            "技术热情：是否有个人项目、开源贡献或技术博客",
            "团队契合：性格和沟通风格是否适合小团队",
            "解决问题：遇到卡点时的思路和方法",
        ],
        follow_up_hints=[
            "能给我看一下你的GitHub或者个人项目吗？",
            "你最近在技术上最有成就感的一件事是什么？",
            "如果给你一个完全自由的技术选型，你会怎么做？",
            "你更喜欢独立负责还是团队协作？为什么？",
            "你对我们团队或产品有什么想了解的？",
        ],
        study_plan_extra=[
            "整理个人GitHub，确保有可展示的项目",
            "写一篇技术博客展示深度思考",
            "准备一个能现场演示的demo或代码片段",
        ],
    ),
}


def get_template(name: str) -> InterviewTemplate | None:
    return TEMPLATES.get(name)


def list_templates() -> list[InterviewTemplate]:
    return list(TEMPLATES.values())
