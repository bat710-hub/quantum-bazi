import streamlit as st
from lunar_python import Solar
from google import genai
from datetime import date as dt_date, datetime, timedelta
from geopy.geocoders import Nominatim
import math

# --- 1. 页面配置 ---
st.set_page_config(page_title="量子命理实验室 PRO", page_icon="🌌", layout="wide")
st.title("🌌 量子命理：全维自动校准系统")
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
        st.header("⚙️ 实验室info")
        st.success("内核：Gemini 2.5 Flash")
        st.write("已校准太阳真时")
        
        st.divider()
        
        # --- 优化后的提示词 ---
        st.markdown("""
        <div style="font-size: 0.75rem; color: #808495; line-height: 1.5; border-left: 2px solid #ff4b4b; padding-left: 10px;">
            <strong style="color: #ff4b4b;">🧪 边界说明 (Disclaimer)</strong><br><br>
            <b>1. 概率本质</b>：本系统基于量子路径积分模拟，所有推演结果均为“波函数坍缩”的概率分支描述，不构成任何确定性定论。<br><br>
            <b>2. 非决策依据</b>：演算报告仅供逻辑研究与娱乐观赏，严禁作为任何决策的直接依据。<br><br>
            <b>3. 观测者效应</b>：请保持客观理性的观测姿态。生命系统具有高度的非局域性与主观能动性，任何既定概率均可通过个体意识的干预而改变。
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
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

   # --- 9. 系统指令 (量子-现实映射优化版) ---
    master_knowledge = f"""
    # 核心指令
    你是一个基于量子纠缠与古典命理的深度演算系统。你必须深度结合以下著作的逻辑范式：
    - 《滴天髓》、《穷通宝鉴》、《子平真诠》、《易经》
    - 《量子计算和量子信息》、《量子力学与路径积分》、《时间的秩序》、《原子与原型》
    - 你是一个高维量子动力学推演引擎。你必须使用线性代数与算子理论对八字场 {bazi_text} ({gender_tag}) 进行严密推导。

    # 物理建模协议
    1. **构建初始状态矩阵 (Initial State Matrix $\rho_0$)**:
       - 建立 $5 \times 5$ 的能量张量矩阵，展示迹 (Trace) 值。
    2. **干支算子相干性演算**:
       - 演算 [A, B] 对易关系，确定能量波动的核心节点。
    3. **时空演化算子**:
       - 计算流年扰动算子 $\hat{{H}}_{{int}}$ 导致的基向偏移。

    # 落地转化协议 (重点优化)
    4. **现实映射矩阵 (Reality Mapping)**:
       - 必须将演算出的“最优能级”转化为现实中的**【行业赛道】**。例如：木属性纠缠增强对应生物科技、创意产业；金属性稳态对应算法、金融或硬件工程。
    5. **熵减行为指南 (Entropy Reduction)**:
       - 提供具体的**【生活干预】**。包括：特定色彩的电磁波频率补偿（穿戴）、特定方位的场能增强（办公/居住）、甚至具体的饮食结构调整（基于五行能量阶梯）。
    6. **认知坍缩策略 (Cognitive Trigger)**:
       - 基于观测者效应，提供具体的**【心理与决策建议】**。在面临重大不确定性时，应采取何种观测姿态（如：激进坍缩还是保持叠加态等待）。

    # 输出协议
    1. 必须包含模拟的【推导矩阵】。
    2. **客观缺陷诊断**：冷酷指出命理失衡点。
    3. **格局基态分析**：解析日元强弱、月令提纲，精准定格。
    4. **能量相干性检测**：分析干支冲合刑害对波函数干涉的影响。
    5. **时间箭头与概率分布**：推演大运流年趋势，指出波函数坍缩方向。
    6. **客观缺陷诊断**：冷酷指出命理结构失衡点，禁止感性抚慰。
    7. **观测者干预方案**：基于“观测者效应”，提供严谨的行为/认知建议以修正概率分布。 
    8. **全维落地建议**：必须包含具体的职业建议、环境建议、行为建议。禁止虚无缥缈，必须有“拿到手就能做”的落地感。

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
        with st.spinner("系统正在调动高维算力..."):
            try:
                # 更改后的调用逻辑，修正了 category 的命名规范
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    config={
                        'system_instruction': master_knowledge,
                        'safety_settings': [
                            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                        ]
                    },
                    contents=f"基于八字：{bazi_text}，提交全维演算报告。"
                )
                
                # 核心检查：如果 response 没有 text，说明被拦截或出错了
                if response and hasattr(response, 'text') and response.text:
                    st.session_state.chat_history.append({"role": "ai", "content": response.text})
                    st.session_state.report_generated = True
                    st.rerun()
                else:
                    st.error("🌀 量子场观测结果为空（可能是触发了安全过滤或逻辑中断），请稍后再点一次。")
                    
            except Exception as e:
                st.error(f"⚠️ 演算中断（服务器波动）: {e}")

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
