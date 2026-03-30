import streamlit as st
from 儲值金系統設定 import run_process_web

# ===== 頁面設定 =====
st.set_page_config(
    page_title="儲值金系統",
    page_icon="💰",
    layout="wide"
)

# ===== CSS 美化 =====
st.markdown("""
<style>
.main {
    background-color: #f7f9fc;
}
.block-container {
    padding-top: 2rem;
}
.card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}
.title {
    font-size: 26px;
    font-weight: 700;
}
.subtitle {
    color: #888;
    margin-bottom: 10px;
}
.stButton > button {
    background-color: #4F46E5;
    color: white;
    border-radius: 8px;
    height: 42px;
    font-weight: 600;
}
.stButton > button:hover {
    background-color: #4338CA;
}
</style>
""", unsafe_allow_html=True)

# ===== 標題 =====
st.markdown('<div class="title">💰 儲值金訂單系統</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">自動建立訂單 / 發送確認信 / 日曆同步</div>', unsafe_allow_html=True)

# ===== 表單 =====
with st.form("run_form"):

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ⚙️ 系統設定")
        env = st.selectbox("執行環境", ["dev", "prod"])
        region = st.selectbox("執行區域", ["台北", "台中"])

        st.markdown("### 🔐 後台登入")
        backend_email = st.text_input("後台帳號")
        backend_password = st.text_input("後台密碼", type="password")
        backend_user_id = st.text_input("後台使用者ID（is_backend）")

    with col2:
        st.markdown("### 📊 Sheet 設定")
        sheet_name = st.text_input("工作表名稱", value="202604")

        col_a, col_b = st.columns(2)
        with col_a:
            start_row = st.number_input("開始列", min_value=1, value=2)
        with col_b:
            end_row = st.number_input("結束列", min_value=1, value=10)

    submitted = st.form_submit_button("🚀 開始執行")

# ===== 執行 =====
if submitted:
    if not backend_email.strip():
        st.error("請輸入後台帳號")
        st.stop()

    if not backend_password.strip():
        st.error("請輸入後台密碼")
        st.stop()

    if not backend_user_id.strip():
        st.error("請輸入後台使用者ID")
        st.stop()

    st.markdown("### 📡 執行中...")

    log_box = st.empty()
    logs = []

    def ui_log(msg):
        logs.append(msg)
        log_box.code("\n".join(logs[-50:]))

    try:
        result = run_process_web(
            env_name=env,
            region=region,
            backend_email=backend_email.strip(),
            backend_password=backend_password.strip(),
            backend_user_id=backend_user_id.strip(),
            sheet_name=sheet_name.strip(),
            start_row=int(start_row),
            end_row=int(end_row),
            logger=ui_log,
        )

        st.success("✅ 執行完成")

        col1, col2, col3 = st.columns(3)
        col1.metric("成功", result["success_count"])
        col2.metric("失敗", result["fail_count"])
        col3.metric("總數", result["total_processed"])

    except Exception as e:
        st.error(f"❌ 執行失敗：{e}")
