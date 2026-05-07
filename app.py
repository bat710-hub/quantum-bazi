import streamlit as st
from lunar_python import Solar
from google import genai
from datetime import date as dt_date, datetime, timedelta
from geopy.geocoders import Nominatim
import math

# --- 1. 页面配置 ---
st.set_page_config(page_title="量子命理实验室 PRO", page_icon="🌌", layout="wide")
st.title("🌌 量子八字：全维自动校准系统")
st.caption("🚀 PRO v4.5 | 自动地理定位 | 真太阳时精密校正 | 旗舰算力")

# --- 2. 后台配置 ---
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("❌ 未检测到 API Key，请在 Streamlit Settings -> Secrets 中配置")
else:
    client = genai.Client(api_key=api_key)

    # --- 3. 核心工具函数：地理与时间校准 ---
    @st.cache_data
    def get_longitude(city_name):
        try:
            # 使用 Nominatim 自动获取经度
            geolocator = Nominatim(user_agent="q_bazi_lab_v4")
            location = geolocator.geocode(city_name)
            if location:
                return location.longitude, location.address
            return None, None
        except:
            return None, None

    def calculate_eot(day_of_year):
        """均时差计算公式"""
        b = 2 * math.pi * (day_of_year - 81) / 365
        return 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)

    # --- 4. 侧边栏 ---
    with st.sidebar:
        st.header("⚙️ 演算参数")
        st.success("内核：Gemini 2.5 Flash ")
        st.info("校准标准：真太阳时 (视太阳时)")
        if st.button("🧹 清除观测痕迹"):
            st.session_state.chat_history = []
            st.session_state.report_generated = False
            st.rerun()

    # --- 5. 用户输入区域 ---
    with st.container():
        st.subheader("📡 时空能量场锁定")
        col1, col2, col3 = st.columns([1.5, 1, 1])
        with col1:
            date_input = st.date_input("出生日期", value=dt_date(1995, 1, 1))
        with col2:
            time_input = st.time_input("出生时间 (钟表时间)", value=datetime.strptime("12:00", "%H:%M").time())
        with col3:
            gender = st.selectbox("性别", ["男", "女"])

        birth_place = st.text_input("出生城市 (自动校准)", placeholder="请精确到区、县、镇 例如：北京朝阳区, 广东东莞虎门镇")

    # --- 6. 自动化时空校准逻辑 ---
    final_lng = 120.0
    if birth_place:
        lng, full_addr = get_longitude(birth_place)
        if lng:
            final_lng = lng
            st.success(f"📍 坐标锁定：{full_addr} (经度: {lng:.2f}°)")
        else:
            st.error("无法自动定位，请确保城市名称正确。")

    # 计算校准偏差
    long_offset = (final_lng - 120.0) * 4
    eot_offset = calculate_eot(date_input.timetuple().tm_yday)
    total_offset = long_offset + eot_offset

    dt_naive = datetime.combine(date_input, time_input)
    true_solar_dt = dt_naive + timedelta(minutes=total_offset)
    
    # --- 7. 八字计算核心 ---
    solar = Solar.fromYmdHms(true_solar_dt.year, true_solar_dt.month, true_solar_dt.day, true_solar_dt.hour, true_solar_dt.minute, 0)
    bazi_obj = solar.getLunar().getEightChar()
    bazi_text = f"{bazi_obj.getYear()} {bazi_obj.getMonth()} {bazi_obj.getDay()} {bazi_obj.getTime()}"
    gender_tag = "乾造" if gender == "男" else "坤造"
    
    st.warning(f"🕒 **时空校准激活**：原始 {time_input} → **真太阳时 {true_solar_dt.strftime('%H:%M')}** (偏差: {total_offset:.1f}分)")
    st.info(f"🧬 **最终场锁定**：{gender_tag} | {bazi_text}")

    # --- 8. 五行能量可视化 ---
    wuxing_counts = {
        "木": bazi_text.count("甲")+bazi_text.count("乙")+bazi_text.count("寅")+bazi_text.count("卯"),
        "火": bazi_text.count("丙")+bazi_text.count("丁")+bazi_text.count("巳")+bazi_text.count("午"),
        "土": bazi_text.count("戊")+bazi_text.count("己")+bazi_text.count("辰")+bazi_text.count("戌")+bazi_text.count("丑")+bazi_text.count("未"),
        "金": bazi_text.count("庚")+bazi_text.count("辛")+bazi_text.count("申")+bazi_text.count("酉"),
        "水": bazi_text.count("壬")+bazi_text.count("癸")+bazi_text.count("亥")+bazi_text.count("子"),
    }
    v_cols = st.columns(5)
    for i, label in enumerate(wuxing_counts.keys()):
        v_cols[i].metric(label, f"{wuxing_counts[label]} 阶")

    # --- 9. 系统指令 (注入顶级书单逻辑) ---
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
    当前对象：{gender_tag}，校准后真太阳时：{true_solar_dt}。
    """

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "report_generated" not in st.session_state:
        st.session_state.report_generated = False

    # --- 10. 执行按钮 ---
    if st.button("✨ 开启全维路径演算"):
        with st.spinner("信道连接中..."):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash", 
                    config={'system_instruction': master_knowledge},
                    contents=f"基于八字：{bazi_text}，提交全维演算报告。"
                )
                st.session_state.chat_history.append({"role": "ai", "content": response.text})
                st.session_state.report_generated = True
                st.rerun()
            except Exception as e:
                st.error(f"演算中断: {e}")

    # --- 11. 互动对话 ---
    if st.session_state.report_generated:
        st.markdown("---")
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"], avatar="🌌" if msg["role"]=="ai" else "👤"):
                st.markdown(msg["content"])

        user_q = st.chat_input("针对演算细节进行追问...")
        if user_q:
            st.session_state.chat_history.append({"role": "user", "content": user_q})
            with st.chat_message("assistant", avatar="🌌"):
                with st.spinner("计算中..."):
                    try:
                        ans = client.models.generate_content(
                            model="gemini-2.5-flash",
                            config={'system_instruction': master_knowledge},
                            contents=f"背景：{bazi_text}。追问：{user_q}"
                        )
                        st.write(ans.text)
                        st.session_state.chat_history.append({"role": "ai", "content": ans.text})
                    except:
                        st.error("信道波动。")
