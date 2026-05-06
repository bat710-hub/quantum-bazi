import streamlit as st
from lunar_python import Solar
from google import genai

# 1. 网页头部设计
st.set_page_config(page_title="量子命理实验室", page_icon="🌌")
st.title("🌌 量子八字命理推演")
st.markdown("---")

# 2. 从系统获取 API Key
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("后台尚未配置 API Key，请联系管理员。")
else:
    client = genai.Client(api_key=api_key)

    # 3. 用户输入生日信息
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("出生公历日期")
    with col2:
        time_hour = st.number_input("出生小时 (0-23)", min_value=0, max_value=23, value=12)

    # 4. 准确排盘 (使用 lunar-python 库)
    solar = Solar.fromYmdHms(date.year, date.month, date.day, time_hour, 0, 0)
    lunar = solar.getLunar()
    eight_char = lunar.getEightChar()
    bazi_text = f"{eight_char.getYear()} {eight_char.getMonth()} {eight_char.getDay()} {eight_char.getTime()}"

    st.success(f"🎴 已锁定能量场（八字）：{bazi_text}")

    # 5. 调用 Gemini 进行量子推演
    if st.button("💫 开始量子观测"):
        with st.spinner("波函数坍缩中..."):
            # 这里就是你调教 AI 的“系统指令”
            system_prompt = "你是一个精通量子力学和传统八字的专家。请用专业且神秘的语气，将用户的八字视为能量场，分析其概率叠加态。禁止奉承，只要最客观的结果。"
            user_prompt = f"用户的八字是：{bazi_text}。请进行量子命理分析。"
            
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                config={'system_instruction': system_prompt},
                contents=user_prompt
            )
            
            st.markdown("### 🌀 观测报告")
            st.write(response.text)

st.markdown("---")
st.caption("基于量子概率理论与传统干支逻辑建模")
