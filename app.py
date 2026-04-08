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

# ===== 工具函式：解析列號 =====
def parse_row_input(row_text: str):
    """
    支援格式：
    - 3
    - 3,5,7
    - 3,5,7-10
    - 2-4,8,10-12
    回傳排序後且去重的 list[int]
    """
    if not row_text or not row_text.strip():
        raise ValueError("請輸入列號，例如：3,5,7-10")

    rows = set()
    parts = [p.strip() for p in row_text.split(",") if p.strip()]

    for part in parts:
        if "-" in part:
            start_str, end_str = part.split("-", 1)
            start = int(start_str.strip())
            end = int(end_str.strip())

            if start <= 0 or end <= 0:
                raise ValueError("列號必須大於 0")

            if start > end:
                raise ValueError(f"區間格式錯誤：{part}")

            rows.update(range(start, end + 1))
        else:
            row = int(part)
            if row <= 0:
                raise ValueError("列號必須大於 0")
            rows.add(row)

    return sorted(rows)

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


    with col2:
        st.markdown("### 📊 Sheet 設定")
        sheet_name = st.text_input("工作表名稱", value="202604")
        row_input = st.text_input(
            "執行列號",
            value="2-10",
            help="可輸入：3,5,7-10"
        )

    submitted = st.form_submit_button("🚀 開始執行")

# ===== 執行 =====
if submitted:
    if not backend_email.strip():
        st.error("請輸入後台帳號")
        st.stop()

    if not backend_password.strip():
        st.error("請輸入後台密碼")
        st.stop()

    try:
        target_rows = parse_row_input(row_input)

    except Exception as e:
        st.error(f"列號格式錯誤：{e}")
        st.stop()

    st.markdown("### 📡 執行中...")

    log_box = st.empty()
    logs = []

    def ui_log(msg):
        logs.append(str(msg))
        log_box.code("\n".join(logs[-50:]))

    total_success = 0
    total_fail = 0
    total_processed = 0

    try:
        for row_no in target_rows:
            ui_log(f"開始處理第 {row_no} 列...")

            result = run_process_web(
                env_name=env,
                region=region,
                backend_email=backend_email.strip(),
                backend_password=backend_password.strip(),
                sheet_name=sheet_name.strip(),
                start_row=row_no,
                end_row=row_no,
                logger=ui_log,
            )

            total_success += result.get("success_count", 0)
            total_fail += result.get("fail_count", 0)
            total_processed += result.get("total_processed", 0)

        st.success("✅ 執行完成")

        col1, col2, col3 = st.columns(3)
        col1.metric("成功", total_success)
        col2.metric("失敗", total_fail)
        col3.metric("總數", total_processed)

    except Exception as e:
        st.error(f"❌ 執行失敗：{e}")
