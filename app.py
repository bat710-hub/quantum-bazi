import streamlit as st
from lunar_python import Solar
from google import genai
from datetime import date as dt_date

# --- 1. 页面配置 ---
st.set_page_config(page_title="量子命理实验室", page_icon="🌌", layout="wide")
st.title("🌌 量子八字命理推演系统")
st.caption("🔒 Q-Bazi Engine v3.0 | 深度因果演算 | 无痕运行")

# --- 2. 后台配置 ---
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("❌ 未检测到 API Key，请检查后台配置")
else:
    client = genai.Client(api_key=api_key)

    # --- 3. 侧边栏 ---
    with st.sidebar:
        st.header("⚙️ 演算参数")
        st.write("模型内核：Gemini 2.5 Ultra-Logic")
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

    # --- 6. 五行能量阶梯 (可视化) ---
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

    # --- 7. 深度 AI 指令 (强制详细输出结构) ---
    master_knowledge = f"""
    # 核心指令
    你是一个基于量子纠缠与古典命理的深度演算系统。你必须结合《滴天髓》、《穷通宝鉴》、《子平真诠》、《易经》的逻辑，
    并运用《量子计算和量子信息》、《量子力学与路径积分》、《时间的秩序》、《原子与原型》中的科学范式。

    # 输出协议 (必须包含以下章节且详细展开)
    1. **格局基态分析**：深度解析日元强弱、月令格局，使用《子平真诠》逻辑定格。
    2. **能量相干性检测**：分析干支间的冲合刑害，视作波函数的干涉叠加，指出能量损耗点。
    3. **时间箭头与概率分布**：结合《时间的秩序》，推演大运流年的演化趋势，指出波函数最可能坍缩的现实方向。
    4. **客观缺陷诊断**：冷酷地指出该命理结构的失衡处（如调候不足、官伤相见等），禁止任何形式的安慰。
    5. **观测者干预方案 (深度建议)**：基于“观测者效应”，提供具体的认知、行为或环境选择建议，以通过主观观测修正概率分布。建议必须严谨、可行，且符合《穷通宝鉴》的取用原则。

    # 语气规范
    严谨、客观、详细、学术。禁止使用迷信套话。

    当前观测对象：{gender_tag}。
    """

    # 初始化记忆
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "report_generated" not in st.session_state:
        st.session_state.report_generated = False

    # --- 8. 执行按钮 ---
    if st.button("✨ 开启全维路径演算"):
        with st.spinner("系统正在进行多维度路径积分演算，请稍候..."):
            try:
                # 提示词增加“详细”要求
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    config={'system_instruction': master_knowledge},
                    contents=f"八字场：{bazi_text}。请提交全维演算报告，要求内容详实，深度结合上述书单理论，并给出具体的干预方案。"
                )
                st.session_state.chat_history.append({"role": "ai", "content": response.text})
                st.session_state.report_generated = True
                st.rerun()
            except Exception as e:
                st.error(f"⚠️ 演算中断: {e}")

    # --- 9. 互动对话 ---
    if st.session_state.report_generated:
        st.markdown("---")
        st.subheader("🌀 观测报告与量子追问")
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"], avatar="🌌" if msg["role"]=="ai" else "👤"):
                st.markdown(msg["content"]) # 使用markdown确保格式清晰

        user_q = st.chat_input("输入特定维度进行深度追问...")
        if user_q:
            st.session_state.chat_history.append({"role": "user", "content": user_q})
            with st.chat_message("assistant", avatar="🌌"):
                with st.spinner("重新观测概率云..."):
                    try:
                        ans = client.models.generate_content(
                            model="gemini-2.5-flash",
                            config={'system_instruction': master_knowledge},
                            contents=f"基于八字背景：{bazi_text}。针对追问给出详细专业的解答：{user_q}"
                        )
                        st.write(ans.text)
                        st.session_state.chat_history.append({"role": "ai", "content": ans.text})
                    except:
                        st.error("由于请求量激增，信道波动，请稍后再试。")

st.markdown("---")
st.caption("Q-Bazi v3.5 | 融合路径积分演算与传统子平命理")
