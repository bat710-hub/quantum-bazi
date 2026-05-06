import streamlit as st
from lunar_python import Solar
from google import genai
from datetime import date as dt_date

# --- 1. 页面配置与视觉样式 ---
st.set_page_config(page_title="量子命理实验室", page_icon="🌌", layout="wide")
st.title("🌌 量子八字命理推演系统")
st.caption("🔒 隐私承诺：采用纯量子无痕演算，所有输入信息在关闭页面后自动湮灭。")

# --- 2. 后台连接配置 ---
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("❌ 请在 Streamlit 后台配置您的 GEMINI_API_KEY")
else:
    client = genai.Client(api_key=api_key)

    # --- 3. 侧边栏：实验室参数 (增加专业仪式感) ---
    with st.sidebar:
        st.header("⚙️ 观测参数")
        st.slider("量子纠缠强度", 0.0, 1.0, 0.85)
        st.selectbox("分析深度", ["全维演算", "因果溯源", "快速扫描"])
        st.divider()
        if st.button("🧹 湮灭观测记录"):
            st.session_state.chat_history = []
            st.session_state.report_generated = False
            st.rerun()

    # --- 4. 用户输入区域 (新增：性别、出生地) ---
    with st.container():
        st.subheader("📡 时空坐标输入")
        col1, col2 = st.columns(2)
        with col1:
            date_input = st.date_input("出生日期", value=dt_date(1995, 1, 1), min_value=dt_date(1900, 1, 1))
        with col2:
            time_hour = st.number_input("出生小时 (0-23)", 0, 23, 12)

        col3, col4 = st.columns(2)
        with col3:
            gender = st.selectbox("性别", ["男", "女"])
        with col4:
            location = st.text_input("出生城市", placeholder="例如：曼谷")

    # --- 5. 八字计算核心 ---
    solar = Solar.fromYmdHms(date_input.year, date_input.month, date_input.day, time_hour, 0, 0)
    bazi_obj = solar.getLunar().getEightChar()
    bazi_text = f"{bazi_obj.getYear()} {bazi_obj.getMonth()} {bazi_obj.getDay()} {bazi_obj.getTime()}"
    gender_tag = "乾造" if gender == "男" else "坤造"
    
    st.info(f"🧬 **能量场锁定**：{gender_tag} | {bazi_text} | 观测坐标：{location if location else '全球叠加态'}")

    # --- 6. 五行能量场可视化 (新增功能) ---
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

    # --- 7. 系统知识库配置 ---
    master_knowledge = f"""
    你是一个精通传统八字（《渊海子平》、《滴天髓》）与现代量子力学的专家。
    当前观测对象：{gender_tag}（性别影响大运顺逆，请严格遵循）。
    观测地点：{location}。
    分析要求：请结合干支生克与波函数坍缩理论，提供具有科学感且神秘精准的命理报告。
    """

    # 初始化记忆
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "report_generated" not in st.session_state:
        st.session_state.report_generated = False

    # --- 8. 观测执行按钮 ---
    if st.button("✨ 开启全维观测"):
        with st.spinner("量子信道链接中，正在坍缩概率云..."):
            try:
                # 优先尝试 Flash 通道
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    config={'system_instruction': master_knowledge},
                    contents=f"基于八字：{bazi_text}，生成初步观测报告。"
                )
                st.session_state.chat_history.append({"role": "ai", "content": response.text})
                st.session_state.report_generated = True
                st.rerun()
            except Exception as e:
                st.error(f"⚠️ 量子信道波动: {e}")

    # --- 9. 互动问答区域 ---
    if st.session_state.report_generated:
        st.markdown("---")
        st.subheader("🌀 观测报告与追问")
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"], avatar="🌌" if msg["role"]=="ai" else "👤"):
                st.write(msg["content"])

        user_q = st.chat_input("向实验室追问细节...")
        if user_q:
            st.session_state.chat_history.append({"role": "user", "content": user_q})
            with st.chat_message("assistant", avatar="🌌"):
                with st.spinner("演算中..."):
                    try:
                        ans = client.models.generate_content(
                            model="gemini-2.5-flash",
                            config={'system_instruction': master_knowledge},
                            contents=f"背景：{bazi_text}。问题：{user_q}"
                        )
                        st.write(ans.text)
                        st.session_state.chat_history.append({"role": "ai", "content": ans.text})
                    except:
                        st.error("由于请求频繁，量子场暂不稳定，请稍后。")

st.markdown("---")
st.caption("实验说明：本系统基于开源算法与 AI 推演，观测结果仅供参考。")
