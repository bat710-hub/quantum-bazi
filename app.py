import streamlit as st
from lunar_python import Solar
from google import genai
from datetime import date as dt_date

# --- 1. 页面配置 ---
st.set_page_config(page_title="量子命理实验室", page_icon="🌌", layout="wide")
st.title("🌌 量子八字命理推演系统")
st.caption("🔒 本系统采用纯量子无痕演算，所有输入信息在页面刷新后自动湮灭。")

# --- 2. 后台配置 ---
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("❌ 请在 Streamlit 后台配置 GEMINI_API_KEY")
else:
    client = genai.Client(api_key=api_key)

    # --- 3. 侧边栏：参数调节 ---
    with st.sidebar:
        st.header("⚙️ 实验室参数")
        st.info("当前模式：深度因果溯源")
        st.divider()
        if st.button("🧹 湮灭观测记录"):
            st.session_state.chat_history = []
            st.session_state.report_generated = False
            st.rerun()

    # --- 4. 用户输入区域 (已去掉出生城市) ---
    with st.container():
        st.subheader("📡 时空坐标录入")
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            date_input = st.date_input("出生日期", value=dt_date(1995, 1, 1), min_value=dt_date(1900, 1, 1))
        with col2:
            time_hour = st.number_input("出生小时 (0-23)", 0, 23, 12)
        with col3:
            gender = st.selectbox("性别", ["男", "女"])

    # --- 5. 八字计算核心 ---
    solar = Solar.fromYmdHms(date_input.year, date_input.month, date_input.day, time_hour, 0, 0)
    bazi_obj = solar.getLunar().getEightChar()
    bazi_text = f"{bazi_obj.getYear()} {bazi_obj.getMonth()} {bazi_obj.getDay()} {bazi_obj.getTime()}"
    gender_tag = "乾造" if gender == "男" else "坤造"
    
    st.info(f"🧬 **能量场锁定**：{gender_tag} | {bazi_text}")

    # --- 6. 五行能量场可视化 ---
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

    # --- 7. 强化版 AI 指令 (深度结合书单) ---
    master_knowledge = f"""
    # 核心身份
    你是一个量子命理观测者。你拒绝任何玄学迷信或情感抚慰，只基于时空坐标进行逻辑演算。

    # 底层理论框架
    1. 命理学基础：深谙《滴天髓》的象义精微、《穷通宝鉴》的干支调候、《子平真诠》的格局正理以及《易经》的阴阳变易。
    2. 量子物理模型：结合《量子计算和量子信息》的逻辑比特态、《量子力学与路径积分》的能量路径求和、《时间的秩序》中的热力学时间箭头、以及卡尔·荣格与泡利在《原子与原型》中探讨的共时性原理。

    # 演算原则
    - 将干支生克视为能量波函数的干涉与相干。
    - 大运流年代表“观测者效应”导致的概率坍缩。
    - 严禁使用“大吉大利”、“不必担心”等情绪化词汇。
    - 输出必须严谨、客观、学术化，直接指出命理结构的失衡与稳定态。
    
    当前观测对象：{gender_tag}。
    """

    # 初始化记忆
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "report_generated" not in st.session_state:
        st.session_state.report_generated = False

    # --- 8. 执行按钮 ---
    if st.button("✨ 开启逻辑观测"):
        with st.spinner("系统正在进行路径积分演算..."):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    config={'system_instruction': master_knowledge},
                    contents=f"基于八字：{bazi_text}。请提供该能量场的深度演算报告，分析其稳态与坍缩趋势。"
                )
                st.session_state.chat_history.append({"role": "ai", "content": response.text})
                st.session_state.report_generated = True
                st.rerun()
            except Exception as e:
                st.error(f"⚠️ 演算信道异常: {e}")

    # --- 9. 互动问答 ---
    if st.session_state.report_generated:
        st.markdown("---")
        st.subheader("🌀 观测报告与量子对话")
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"], avatar="🌌" if msg["role"]=="ai" else "👤"):
                st.write(msg["content"])

        user_q = st.chat_input("针对演算细节进行追问...")
        if user_q:
            st.session_state.chat_history.append({"role": "user", "content": user_q})
            with st.chat_message("assistant", avatar="🌌"):
                with st.spinner("正在重构概率云..."):
                    try:
                        ans = client.models.generate_content(
                            model="gemini-2.5-flash",
                            config={'system_instruction': master_knowledge},
                            contents=f"八字背景：{bazi_text}。追问请求：{user_q}"
                        )
                        st.write(ans.text)
                        st.session_state.chat_history.append({"role": "ai", "content": ans.text})
                    except:
                        st.error("量子场波动，请刷新或稍后。")

st.markdown("---")
st.caption("系统内核：Q-Bazi v2.0 | 基于路径积分与古典格局理论")
