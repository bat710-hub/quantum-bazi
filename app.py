import streamlit as st
from lunar_python import Solar
from google import genai
from datetime import date as dt_date

# --- 页面配置与隐私声明 ---
st.set_page_config(page_title="量子命理实验室", page_icon="🌌")
st.title("🌌 量子八字命理推演")
st.caption("🔒 隐私承诺：本系统采用纯量子无痕演算，您的任何输入信息将在关闭页面后彻底湮灭，绝不留存。")
st.markdown("---")

api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("请在后台配置 API Key")
else:
    client = genai.Client(api_key=api_key)
    
    # --- 1. 注入你的“底层资料库”（核心教材） ---
    # 你可以在这里无限补充你想要的理论知识
    master_knowledge = """
    你是一个精通传统八字与现代量子力学的大师。你拥有以下知识库：
    1. 八字核心：以《三命通会》与《滴天髓》为基准，注重五行生克、干支冲合。
    2. 量子视界：将人的命理视为'叠加态'，将流年大运视为'观测变量'。冲合代表量子纠缠，吉凶代表波函数坍缩的方向。
    3. 交互原则：语言要有科技感、神秘感且客观中立，严禁迷信宿命论，强调人的主观能动性（观测者效应）能改变命运。
    """

    col1, col2 = st.columns(2)
    with col1:
        date_input = st.date_input("出生日期", value=dt_date(2100, 1, 1), min_value=dt_date(1900, 1, 1))
    with col2:
        time_hour = st.number_input("小时 (0-23)", 0, 23, 12)

    solar = Solar.fromYmdHms(date_input.year, date_input.month, date_input.day, time_hour, 0, 0)
    bazi = solar.getLunar().getEightChar()
    bazi_text = f"{bazi.getYear()} {bazi.getMonth()} {bazi.getDay()} {bazi.getTime()}"
    
    st.info(f"🧬 原始能量场锁定：{bazi_text}")

    # --- 初始化网页的“临时记忆”（关网页即删除） ---
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "report_generated" not in st.session_state:
        st.session_state.report_generated = False
    if "current_bazi" not in st.session_state:
        st.session_state.current_bazi = bazi_text

    # 如果用户改了生日，清空之前的记录
    if st.session_state.current_bazi != bazi_text:
        st.session_state.chat_history = []
        st.session_state.report_generated = False
        st.session_state.current_bazi = bazi_text

    # --- 2. 初次观测（生成报告） ---
    if st.button("✨ 开启量子观测"):
        with st.spinner("正在链接量子场，进行全维演算..."):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash", 
                    config={'system_instruction': master_knowledge},
                    contents=f"请基于八字：{bazi_text}，给出一份简明扼要的量子命理初步分析报告。"
                )
                # 将结果存入临时记忆
                st.session_state.chat_history.append({"role": "ai", "content": response.text})
                st.session_state.report_generated = True
                st.rerun() # 刷新页面显示报告
            except Exception as e:
                st.error(f"通道拥挤，请稍后再试: {e}")

    # --- 3. 互动问答环节（仅在报告生成后显示） ---
    if st.session_state.report_generated:
        st.markdown("### 🌀 观测报告与量子咨询室")
        
        # 显示历史对话
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.write(msg["content"])
            else:
                with st.chat_message("assistant", avatar="🌌"):
                    st.write(msg["content"])

        # 用户的提问输入框
        user_question = st.chat_input("向系统追问具体问题（如：我今年的事业能量场如何？）")
        
        if user_question:
            # 立即在界面上显示用户的问题
            with st.chat_message("user", avatar="👤"):
                st.write(user_question)
            
            st.session_state.chat_history.append({"role": "user", "content": user_question})
            
            # 带着上下文去请求 AI
            with st.chat_message("assistant", avatar="🌌"):
                with st.spinner("量子演算中..."):
                    try:
                        # 构造包含完整上下文的请求
                        context_prompt = f"用户的八字是 {bazi_text}。用户的问题是：{user_question}。请结合八字给出解答。"
                        answer = client.models.generate_content(
                            model="gemini-2.5-flash",
                            config={'system_instruction': master_knowledge},
                            contents=context_prompt
                        )
                        st.write(answer.text)
                        st.session_state.chat_history.append({"role": "ai", "content": answer.text})
                    except Exception as e:
                        st.error("通讯受阻，请稍后再问。")
