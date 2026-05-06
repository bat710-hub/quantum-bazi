import streamlit as st
from lunar_python import Solar
from google import genai
from datetime import date as dt_date # 引入日期处理逻辑

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
        # --- 核心改动点：定义允许的时间范围 ---
        min_d = dt_date(1900, 1, 1) # 最早支持到 1900 年
        max_d = dt_date(2100, 12, 31) # 最晚支持到 2100 年
        
        date_input = st.date_input(
            "选择出生公历日期", 
            value=None, 
            min_value=min_d, 
            max_value=max_d
        )
    with col2:
        time_hour = st.number_input("出生小时 (0-23)", min_value=0, max_value=23, value=12)

    # 4. 判断逻辑
    if date_input is not None:
        try:
            # 执行排盘计算
            solar = Solar.fromYmdHms(date_input.year, date_input.month, date_input.day, time_hour, 0, 0)
            lunar = solar.getLunar()
            eight_char = lunar.getEightChar()
            bazi_text = f"{eight_char.getYear()} {eight_char.getMonth()} {eight_char.getDay()} {eight_char.getTime()}"

            st.success(f"🎴 已锁定能量场（八字）：{bazi_text}")

            # 调用 Gemini 进行量子推演
            if st.button("💫 开始量子观测"):
                with st.spinner("波函数坍缩中..."):
                    system_prompt = "你是一个精通量子力学和传统八字的专家。请用专业且神秘的语气，将用户的八字视为能量场，分析其概率叠加态。禁止奉承，只要最客观的结果。"
                    user_prompt = f"用户的八字是：{bazi_text}。请进行量子命理分析。"
                    
                    response = client.models.generate_content(
                        model="gemini-1.5-flash",
                        config={'system_instruction': system_prompt},
                        contents=user_prompt
                    )
                    
                    st.markdown("### 🌀 观测报告")
                    st.write(response.text)
        except Exception as e:
            if "429" in str(e):
                st.error("🌌 量子场目前过于拥挤（API 频率限制），请等待 1 分钟后再试。")
            else:
                st.error(f"计算出错，请检查输入：{e}")
    else:
        st.info("💡 请先在上方选择您的出生日期（支持 1900 年至今）。")

st.markdown("---")
st.caption("基于量子概率理论与传统干支逻辑建模")
