import asyncio
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from typing import Dict, List, Any
import os

# 使用langgraph推荐方式定义大模型
llm = ChatOpenAI(
    model="qwen-plus",
    temperature=0,
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


# 解析消息列表
def parse_messages(messages: List[Any]) -> None:
    """
    解析消息列表，打印 HumanMessage、AIMessage 和 ToolMessage 的详细信息

    Args:
        messages: 包含消息的列表，每个消息是一个对象
    """
    print("=== 消息解析结果 ===")
    for idx, msg in enumerate(messages, 1):
        print(f"\n消息 {idx}:")
        # 获取消息类型
        msg_type = msg.__class__.__name__
        print(f"类型: {msg_type}")
        # 提取消息内容
        content = getattr(msg, 'content', '')
        print(f"内容: {content if content else '<空>'}")
        # 处理附加信息
        additional_kwargs = getattr(msg, 'additional_kwargs', {})
        if additional_kwargs:
            print("附加信息:")
            for key, value in additional_kwargs.items():
                if key == 'tool_calls' and value:
                    print("  工具调用:")
                    for tool_call in value:
                        print(f"    - ID: {tool_call['id']}")
                        print(f"      函数: {tool_call['function']['name']}")
                        print(f"      参数: {tool_call['function']['arguments']}")
                else:
                    print(f"  {key}: {value}")
        # 处理 ToolMessage 特有字段
        if msg_type == 'ToolMessage':
            tool_name = getattr(msg, 'name', '')
            tool_call_id = getattr(msg, 'tool_call_id', '')
            print(f"工具名称: {tool_name}")
            print(f"工具调用 ID: {tool_call_id}")
        # 处理 AIMessage 的工具调用和元数据
        if msg_type == 'AIMessage':
            tool_calls = getattr(msg, 'tool_calls', [])
            if tool_calls:
                print("工具调用:")
                for tool_call in tool_calls:
                    print(f"  - 名称: {tool_call['name']}")
                    print(f"    参数: {tool_call['args']}")
                    print(f"    ID: {tool_call['id']}")
            # 提取元数据
            metadata = getattr(msg, 'response_metadata', {})
            if metadata:
                print("元数据:")
                token_usage = metadata.get('token_usage', {})
                print(f"  令牌使用: {token_usage}")
                print(f"  模型名称: {metadata.get('model_name', '未知')}")
                print(f"  完成原因: {metadata.get('finish_reason', '未知')}")
        # 打印消息 ID
        msg_id = getattr(msg, 'id', '未知')
        print(f"消息 ID: {msg_id}")
        print("-" * 50)


# 保存状态图的可视化表示
def save_graph_visualization(graph, filename: str = "graph.png") -> None:
    """保存状态图的可视化表示。

    Args:
        graph: 状态图实例。
        filename: 保存文件路径。
    """
    # 尝试执行以下代码块
    try:
        # 以二进制写模式打开文件
        with open(filename, "wb") as f:
            # 将状态图转换为Mermaid格式的PNG并写入文件
            f.write(graph.get_graph().draw_mermaid_png())
        # 记录保存成功的日志
        print(f"Graph visualization saved as {filename}")
    # 捕获IO错误
    except IOError as e:
        # 记录警告日志
        print(f"Failed to save graph visualization: {e}")



# 定义并运行agent
async def run_agent():
    # 实例化MCP Server客户端
    # 检查环境变量是否设置
    amap_key = os.getenv('AMAP_WEATHER_KEY')
    if not amap_key:
        print("错误: AMAP_WEATHER_KEY 环境变量未设置")
        return
    print(f"使用的AMAP_KEY: {amap_key[:3]}...{amap_key[-3:]}")  # 仅显示部分密钥，保护隐私

    # 实例化MCP Server客户端
    client = MultiServerMCPClient({
        # 高德地图MCP Server
        "amap-amap-sse": {
                "url": f"https://mcp.amap.com/sse?key={amap_key}",
                "transport": "sse"
            }
    })

    try:
        # 从MCP Server中获取可提供使用的全部工具
        tools = await client.get_tools()
        print(f"成功获取工具数量: {len(tools)}")
        # 打印工具名称列表
        tool_names = [tool.name for tool in tools]
        print(f"工具名称列表: {tool_names}")
    except Exception as e:
        print(f"获取工具失败: {str(e)}")
        # 打印完整的错误堆栈
        import traceback
        traceback.print_exc()
        return
    # print(f"tools:{tools}\n")

    # 基于内存存储的short-term
    checkpointer = InMemorySaver()

    # 定义系统消息，指导如何使用工具
    system_message = SystemMessage(content=(
        "你是一个AI助手，使用高德地图工具获取信息。"
    ))

    # 创建ReAct风格的agent
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_message,
        # prompt=f"你是一个乐于助人的AI助手。",
        checkpointer=checkpointer
    )

    # 将定义的agent的graph进行可视化输出保存至本地
    #save_graph_visualization(agent)

    # 定义short-term需使用的thread_id
    config = {"configurable": {"thread_id": "1"}}

    # # 1、非流式处理查询
    # # 高德地图接口测试
    # agent_response = await agent.ainvoke({"messages": [HumanMessage(content="这个118.79815,32.01112经纬度对应的地方是哪里")]}, config)
    # # agent_response = await agent.ainvoke({"messages": [HumanMessage(content="夫子庙的经纬度坐标是多少")]}, config)
    # # agent_response = await agent.ainvoke({"messages": [HumanMessage(content="112.10.22.229这个IP所在位置")]}, config)
    # # agent_response = await agent.ainvoke({"messages": [HumanMessage(content="上海的天气如何")]}, config)
    # # agent_response = await agent.ainvoke({"messages": [HumanMessage(content="我要从苏州的虎丘区骑行到相城区，帮我规划下路径")]}, config)
    # # agent_response = await agent.ainvoke({"messages": [HumanMessage(content="我要从上海豫园骑行到上海人民广场，帮我规划下路径")]}, config)
    # # agent_response = await agent.ainvoke({"messages": [HumanMessage(content="我要从上海豫园步行到上海人民广场，帮我规划下路径")]}, config)
    # # agent_response = await agent.ainvoke({"messages": [HumanMessage(content="我要从上海豫园驾车到上海人民广场，帮我规划下路径")]}, config)
    # # agent_response = await agent.ainvoke({"messages": [HumanMessage(content="我要从上海豫园坐公共交通到上海人民广场，帮我规划下路径")]}, config)
    # # agent_response = await agent.ainvoke({"messages": [HumanMessage(content="测量下从上海豫园到上海人民广场驾车距离是多少")]}, config)
    # # agent_response = await agent.ainvoke({"messages": [HumanMessage(content="在上海豫园附近的中石化的加油站有哪些，需要有POI的ID")]}, config)
    # # agent_response = await agent.ainvoke({"messages": [HumanMessage(content="POI为B00155LA8A的详细信息")]}, config)
    agent_response = await agent.ainvoke({"messages": [HumanMessage(content="在上海豫园周围10公里的中石化的加油站")]}, config)
    # # 将返回的messages进行格式化输出
    parse_messages(agent_response['messages'])
    # agent_response_content = agent_response["messages"][-1].content
    # print(f"agent_response:{agent_response_content}")


    # 2、流式处理查询
    async for message_chunk, metadata in agent.astream(
            # input={"messages": [HumanMessage(content="这个118.79815,32.01112经纬度对应的地方是哪里。输出的内容中不要出现{}")]},
            input={"messages": [HumanMessage(content="我所在地深圳的天气怎么样?")]},
            config=config,
            stream_mode="messages"
    ):
        # 测试原始输出
        # print(f"Token:{message_chunk}\n")
        # print(f"Metadata:{metadata}\n\n")

        # # 跳过工具输出
        # if metadata["langgraph_node"]=="tools":
        #     continue

        # 输出最终结果
        if message_chunk.content:
            print(message_chunk.content, end="|", flush=True)



if __name__ == "__main__":
    asyncio.run(run_agent())



