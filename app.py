import streamlit as st
from lunar_python import Solar
from google import genai
from datetime import date as dt_date

# --- 1. 页面配置 ---
st.set_page_config(page_title="量子命理实验室 PRO", page_icon="🌌", layout="wide")
st.title("🌌 量子八字命理推演系统")
st.caption("🚀 PRO 版 | 接入 Gemini 2.5 Flash 高优先级算力 | 深度因果演算")

# --- 2. 后台配置 ---
# 请确保在 Streamlit Cloud 后台的 Settings -> Secrets 中
# 已配置 GEMINI_API_KEY，且该 Key 已在 Google AI Studio 绑定信用卡开启 Pay-as-you-go
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("❌ 未检测到 API Key，请在 Streamlit 后台配置 GEMINI_API_KEY")
else:
    # 初始化 Paid 客户端
    client = genai.Client(api_key=api_key)

    # --- 3. 侧边栏 ---
    with st.sidebar:
        st.header("⚙️ 演算参数")
        st.success("状态：Paid API 模式激活")
        st.write("内核：Gemini 2.5 Flash (Paid)")
        st.divider()
        if st.button("🧹 清除当前观测数据"):
            st.session_state.chat_history = []
            st.session_state.report_generated = False
            st.rerun()

    # --- 4. 用户输入区域 ---
    with st.container():
        st.subheader("📡 时空能量场锁定")
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            date_input = st.date_input("公历生日", value=dt_date(1995, 1, 1), min_value=dt_date(1900, 1, 1))
        with c2:
            time_hour = st.number_input("出生小时 (0-23)", 0, 23, 12)
        with c3:
            gender = st.selectbox("性别 (乾坤定位)", ["男", "女"])

    # --- 5. 八字计算核心 ---
    solar = Solar.fromYmdHms(date_input.year, date_input.month, date_input.day, time_hour, 0, 0)
    bazi_obj = solar.getLunar().getEightChar()
    bazi_text = f"{bazi_obj.getYear()} {bazi_obj.getMonth()} {bazi_obj.getDay()} {bazi_obj.getTime()}"
    gender_tag = "乾造" if gender == "男" else "坤造"
    
    st.info(f"🧬 **原始场锁定**：{gender_tag} | {bazi_text}")

    # --- 6. 五行能量阶梯可视化 ---
    wuxing_counts = {
        "木": bazi_text.count("甲")+bazi_text.count("乙")+bazi_text.count("寅")+bazi_text.count("卯"),
        "火": bazi_text.count("丙")+bazi_text.count("丁")+bazi_text.count("巳")+bazi_text.count("午"),
        "土": bazi_text.count("戊")+bazi_text.count("己")+bazi_text.count("辰")+bazi_text.count("戌")+bazi_text.count("丑")+bazi_text.count("未"),
        "金": bazi_text.count("庚")+bazi_text.count("辛")+bazi_text.count("申")+bazi_text.count("酉"),
        "水": bazi_text.count("壬")+bazi_text.count("癸")+bazi_text.count("亥")+bazi_text.count("子"),
    }
    v_cols = st.columns(5)
    labels = list(wuxing_counts.keys())
    for i, col in enumerate(v_cols):
        col.metric(labels[i], f"{wuxing_counts[labels[i]]} 阶")

    # --- 7. 深度 AI 指令 (Paid 模式下可承载更复杂的指令逻辑) ---
    master_knowledge = f"""
    # 核心指令
    你是一个基于量子纠缠与古典命理的深度演算系统。你必须深度结合以下著作的逻辑范式：
    - 《滴天髓》、《穷通宝鉴》、《子平真诠》、《易经》
    - 《量子计算和量子信息》、《量子力学与路径积分》、《时间的秩序》、《原子与原型》

    # 输出协议 (必须详细展开)
    1. **格局基态分析**：解析日元强弱、月令提纲，精准定格。
    2. **能量相干性检测**：分析干支冲合刑害对波函数干涉的影响。
    3. **时间箭头与概率分布**：推演大运流年趋势，指出波函数坍缩方向。
    4. **客观缺陷诊断**：冷酷指出命理结构失衡点，禁止感性抚慰。
    5. **观测者干预方案**：基于“观测者效应”，提供严谨的行为/认知建议以修正概率分布。

    # 语气规范
    严谨、客观、学术。禁止使用迷信套话。
    当前观测对象：{gender_tag}。
    """

    # 初始化状态
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "report_generated" not in st.session_state:
        st.session_state.report_generated = False

    # --- 8. 执行按钮 ---
    if st.button("✨ 开启全维路径演算"):
        with st.spinner("系统正在调动付费通道算力，进行多维路径积分演算..."):
            try:
                # 锁定 gemini-2.5-flash
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    config={'system_instruction': master_knowledge},
                    contents=f"八字场：{bazi_text}。请提交全维演算报告，要求深度结合物理与命理理论，给出具体干预方案。"
                )
                st.session_state.chat_history.append({"role": "ai", "content": response.text})
                st.session_state.report_generated = True
                st.rerun()
            except Exception as e:
                st.error(f"⚠️ 演算信道波动 (请检查余额或配置): {e}")

    # --- 9. 互动对话 ---
    if st.session_state.report_generated:
        st.markdown("---")
        st.subheader("🌀 观测报告与量子追问")
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"], avatar="🌌" if msg["role"]=="ai" else "👤"):
                st.markdown(msg["content"])

        user_q = st.chat_input("针对特定维度进行高优先级追问...")
        if user_q:
            st.session_state.chat_history.append({"role": "user", "content": user_q})
            with st.chat_message("assistant", avatar="🌌"):
                with st.spinner("高优先级重构概率云..."):
                    try:
                        ans = client.models.generate_content(
                            model="gemini-2.5-flash",
                            config={'system_instruction': master_knowledge},
                            contents=f"背景：{bazi_text}。追问：{user_q}"
                        )
                        st.write(ans.text)
                        st.session_state.chat_history.append({"role": "ai", "content": ans.text})
                    except Exception as e:
                        st.error(f"信道暂时阻塞: {e}")

st.markdown("---")
st.caption("Q-Bazi PRO v3.8 | 个人实验室专用 | Gemini 2.5 Flash Powered")
