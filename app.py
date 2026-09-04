import streamlit as st
from datetime import date

# --- إعدادات الصفحة ---
st.set_page_config(page_title="حاسبة المعدل السنوي", page_icon="🎓")

# --- تنسيق خاص بالطباعة: يخفي كل شي إلا التقرير عند الطباعة/الحفظ كـ PDF ---
st.markdown("""
<style>
@media print {
    header, .stAppToolbar, section[data-testid="stSidebar"],
    div[data-testid="stNumberInput"], div[data-testid="stButton"],
    .no-print {
        display: none !important;
    }
    .print-only { display: block !important; }
}
.print-only { display: none; }
</style>
""", unsafe_allow_html=True)

st.title("🎓 حاسبة المعدل السنوي")
st.write("أدخل درجاتك في المواد الدراسية وشوف معدلك النهائي فوراً!")
st.caption("⚠️ حساب مبسط يفترض تساوي أوزان جميع المواد. لطلاب الثانوية العامة والدبلوم: راجع البوابة التعليمية الرسمية (eportal.moe.gov.om) لحساب النسبة الدقيقة المعتمدة.")

st.divider()

# --- اسم الطالب (يظهر بالتقرير) ---
student_name = st.text_input("اسم الطالب (يظهر في التقرير)", value="")

st.divider()

# --- إدخال عدد المواد ---
num_subjects = st.number_input(
    "كم عدد المواد الدراسية؟",
    min_value=1,
    max_value=30,
    value=5,
    step=1
)

st.divider()

# --- إدخال أسماء المواد والدرجات ---
subjects = []  # قائمة (list) بتخزن كل مادة مع درجتها
error_found = False

st.subheader("📝 أدخل أسماء المواد ودرجاتك:")

for i in range(1, int(num_subjects) + 1):
    col_name, col_mark = st.columns([2, 1])

    with col_name:
        name = col_name.text_input(
            f"اسم المادة رقم {i}",
            value=f"مادة {i}",
            key=f"name_{i}"
        )

    with col_mark:
        mark = col_mark.number_input(
            "الدرجة (من 100)",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=0.5,
            key=f"mark_{i}"
        )

    # نخزن الاسم والدرجة مع بعض بقائمة واحدة (list of tuples)
    subjects.append((name, mark))

st.divider()

# --- زر الحساب ---
if st.button("احسب المعدل ✅", type="primary"):

    # ناخذ بس الدرجات من القائمة عشان نجمعها (كل عنصر فيها هو (اسم, درجة))
    total_marks = sum(mark for name, mark in subjects)
    average = total_marks / num_subjects

    st.subheader("📊 النتيجة:")
    col1, col2 = st.columns(2)
    col1.metric("مجموع الدرجات", f"{total_marks:.1f} / {num_subjects * 100}")
    col2.metric("المعدل النهائي", f"{average:.2f}%")

    # --- التقدير ---
    if average >= 90:
        grade_text = "ممتاز (A) 🌟"
        st.success("🌟 التقدير: ممتاز (A)")
    elif average >= 80:
        grade_text = "جيد جداً (B) 👍"
        st.info("👍 التقدير: جيد جداً (B)")
    elif average >= 70:
        grade_text = "جيد (C) 📘"
        st.warning("📘 التقدير: جيد (C)")
    else:
        grade_text = "بحاجة لمزيد من الاجتهاد 💪"
        st.error("💪 تحتاج للمزيد من الاجتهاد!")

    st.divider()

    # --- تقرير جاهز للطباعة / الحفظ كـ PDF ---
    st.subheader("🖨️ تقرير جاهز للطباعة")
    st.caption("هذا تقرير غير رسمي لاستخدامك الشخصي — الشهادة الرسمية المعتمدة تصدر من المدرسة فقط.")

    marks_rows = "".join(
        f"<tr><td style='padding:6px;border:1px solid #444;'>{name}</td>"
        f"<td style='padding:6px;border:1px solid #444;'>{mark:.1f}</td></tr>"
        for name, mark in subjects
    )

    report_html = f"""
    <div class="print-only" style="direction:rtl;text-align:right;font-family:Arial;padding:20px;">
        <h2>🎓 تقرير المعدل السنوي</h2>
        <p><b>اسم الطالب:</b> {student_name if student_name else "—"}</p>
        <p><b>التاريخ:</b> {date.today().strftime('%Y-%m-%d')}</p>
        <table style="border-collapse:collapse;width:100%;margin-top:10px;">
            <tr><th style='padding:6px;border:1px solid #444;'>المادة</th>
                <th style='padding:6px;border:1px solid #444;'>الدرجة</th></tr>
            {marks_rows}
        </table>
        <p style="margin-top:15px;"><b>مجموع الدرجات:</b> {total_marks:.1f} / {num_subjects * 100}</p>
        <p><b>المعدل النهائي:</b> {average:.2f}%</p>
        <p><b>التقدير:</b> {grade_text}</p>
        <p style="margin-top:20px;font-size:12px;color:#888;">
            تقرير غير رسمي — لا يغني عن الشهادة الرسمية الصادرة من المدرسة.<br>
            حساب مبسط يفترض تساوي أوزان جميع المواد — لطلاب الثانوية والدبلوم راجع البوابة الرسمية لحساب النسبة الدقيقة.
        </p>
    </div>
    """
    st.markdown(report_html, unsafe_allow_html=True)

    st.markdown("""
    <div class="no-print">
    <button onclick="window.print()" style="
        background-color:#FF4B4B;color:white;padding:10px 20px;
        border:none;border-radius:8px;font-size:16px;cursor:pointer;">
        🖨️ اطبع / احفظ كـ PDF
    </button>
    </div>
    """, unsafe_allow_html=True)

st.divider()
st.caption("فالك النجاح 🌟 — من: أبو محمد")
