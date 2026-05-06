import streamlit as st
from lunar_python import Solar
from google import genai
from datetime import date as dt_date

# --- 页面配置与隐私声明 ---
st.set_page_config(page_title="量子命理实验室", page_icon="🌌")
st.title("🌌 量子八字命理推演")
st.caption("🔒 隐私承诺：本系统采用纯量子无痕演算，您的任何输入信息将在关闭页面后彻底湮灭。")
st.markdown("---")

api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("请在后台配置 API Key")
else:
    client = genai.Client(api_key=api_key)
    
    # --- 1. 底层资料库 ---
    master_knowledge = """
    你是一个精通传统八字（如《三命通会》、《滴天髓》）与现代量子力学的专家。
    分析时请结合量子概率、观测者效应等概念。语言要有神秘感且客观，严禁迷信，强调主观能动性。
    """

    col1, col2 = st.columns(2)
    with col1:
        date_input = st.date_input("出生日期", value=dt_date(1995, 1, 1), min_value=dt_date(1900, 1, 1))
    with col2:
        time_hour = st.number_input("小时 (0-23)", 0, 23, 12)

    solar = Solar.fromYmdHms(date_input.year, date_input.month, date_input.day, time_hour, 0, 0)
    bazi = solar.getLunar().getEightChar()
    bazi_text = f"{bazi.getYear()} {bazi.getMonth()} {bazi.getDay()} {bazi.getTime()}"
    
    st.info(f"🧬 原始能量场锁定：{bazi_text}")

    # --- 初始化 Session State ---
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "report_generated" not in st.session_state:
        st.session_state.report_generated = False
    if "current_bazi" not in st.session_state:
        st.session_state.current_bazi = bazi_text

    # 如果换了八字，清空历史
    if st.session_state.current_bazi != bazi_text:
        st.session_state.chat_history = []
        st.session_state.report_generated = False
        st.session_state.current_bazi = bazi_text

    # --- 2. 初次观测（带自动切换通道） ---
    if st.button("✨ 开启量子观测"):
        with st.spinner("正在链接量子场..."):
            try:
                # 优先尝试 2.5 Flash
                response = client.models.generate_content(
                    model="gemini-2.5-flash", 
                    config={'system_instruction': master_knowledge},
                    contents=f"请基于八字：{bazi_text}，给出一份简明扼要的分析报告。"
                )
                st.session_state.chat_history.append({"role": "ai", "content": response.text})
                st.session_state.report_generated = True
                st.rerun()
            except Exception as e:
                # 如果主通道报错，尝试 Lite 通道
                try:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash-lite", 
                        config={'system_instruction': master_knowledge},
                        contents=f"请基于八字：{bazi_text}，给出一份简明扼要的分析报告。"
                    )
                    st.session_state.chat_history.append({"role": "ai", "content": response.text})
                    st.session_state.report_generated = True
                    st.rerun()
                except Exception as e_lite:
                    st.error(f"量子通道拥挤，请一分钟后再试。错误码: {e_lite}")

    # --- 3. 互动问答环节 ---
    if st.session_state.report_generated:
        st.markdown("### 🌀 观测报告与互动")
        
        for msg in st.session_state.chat_history:
            role_icon = "👤" if msg["role"] == "user" else "🌌"
            with st.chat_message(msg["role"], avatar=role_icon):
                st.write(msg["content"])

        user_question = st.chat_input("追问细节（如：事业、财运、观测建议）")
        
        if user_question:
            with st.chat_message("user", avatar="👤"):
                st.write(user_question)
            
            st.session_state.chat_history.append({"role": "user", "content": user_question})
            
            with st.chat_message("assistant", avatar="🌌"):
                with st.spinner("量子演算中..."):
                    context_prompt = f"八字：{bazi_text}。问题：{user_question}"
                    try:
                        answer = client.models.generate_content(
                            model="gemini-2.5-flash",
                            config={'system_instruction': master_knowledge},
                            contents=context_prompt
                        )
                        st.write(answer.text)
                        st.session_state.chat_history.append({"role": "ai", "content": answer.text})
                    except Exception as e:
                        try:
                            # 追问时也使用备用通道
                            answer = client.models.generate_content(
                                model="gemini-2.5-flash-lite",
                                config={'system_instruction': master_knowledge},
                                contents=context_prompt
                            )
                            st.write(answer.text)
                            st.session_state.chat_history.append({"role": "ai", "content": answer.text})
                        except:
                            st.error("通讯受阻，当前算力不足，请稍后刷新页面。")

st.markdown("---")
st.caption("注：本工具仅供学习参考。")
