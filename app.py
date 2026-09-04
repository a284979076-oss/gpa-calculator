import streamlit as st
from datetime import date
import random

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

/* --- لون جديد يتناسق مع الخلفية الغامقة --- */
div.stButton > button[kind="primary"] {
    background-color: #00C2A8;
    border-color: #00C2A8;
}
div.stButton > button[kind="primary"]:hover {
    background-color: #00A691;
    border-color: #00A691;
}
div[data-testid="stMetricValue"] {
    color: #00C2A8;
}
</style>
""", unsafe_allow_html=True)

st.title("🎓 حاسبة المعدل السنوي")
st.write("أدخل درجاتك في المواد الدراسية وشوف معدلك النهائي فوراً!")
st.caption("⚠️ اختر مرحلتك الدراسية تحت لعرض نظام الحساب المناسب لك.")

st.divider()

# --- اسم الطالب (يظهر بالتقرير) ---
student_name = st.text_input("اسم الطالب (يظهر في التقرير)", value="")

# --- المرحلة الدراسية: تحدد نظام الحساب المستخدم ---
stage = st.selectbox(
    "المرحلة الدراسية",
    ["ابتدائي", "إعدادي", "ثانوي", "جامعي"]
)
is_university = (stage == "جامعي")

if stage == "ثانوي":
    st.caption("⚠️ للثانوية العامة والدبلوم: راجع البوابة التعليمية الرسمية (eportal.moe.gov.om) لحساب النسبة الدقيقة المعتمدة.")
elif is_university:
    st.caption("📚 للجامعيين: أدخل عدد الساعات المعتمدة لكل مادة ليُحسب معدلك التراكمي (GPA) بدقة.")

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

# --- إدخال أسماء المواد والدرجات (والساعات المعتمدة للجامعيين) ---
subjects = []  # قائمة (list) بتخزن كل مادة: (اسم, درجة, وزن/ساعات)
error_found = False

st.subheader("📝 أدخل أسماء المواد ودرجاتك:")

for i in range(1, int(num_subjects) + 1):
    if is_university:
        col_name, col_mark, col_credit = st.columns([2, 1, 1])
    else:
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

    if is_university:
        with col_credit:
            credit = col_credit.number_input(
                "الساعات",
                min_value=1,
                max_value=6,
                value=3,
                step=1,
                key=f"credit_{i}"
            )
    else:
        credit = 1  # وزن متساوٍ لكل مادة بغير الجامعي

    # نخزن الاسم والدرجة والوزن مع بعض بقائمة واحدة (list of tuples)
    subjects.append((name, mark, credit))

st.divider()

# --- زر الحساب ---
if st.button("احسب المعدل ✅", type="primary"):

    # المعدل المرجح: كل مادة تأثر حسب وزنها (الساعات المعتمدة)
    # لغير الجامعي، كل الأوزان = 1 فتكون النتيجة متوسط عادي كالمعتاد
    total_weighted = sum(mark * credit for name, mark, credit in subjects)
    total_credits = sum(credit for name, mark, credit in subjects)
    average = total_weighted / total_credits
    total_marks = sum(mark for name, mark, credit in subjects)

    st.subheader("📊 النتيجة:")
    col1, col2 = st.columns(2)
    if is_university:
        col1.metric("مجموع الساعات المعتمدة", f"{total_credits}")
        col2.metric("المعدل المرجّح (من 100)", f"{average:.2f}%")
    else:
        col1.metric("مجموع الدرجات", f"{total_marks:.1f} / {num_subjects * 100}")
        col2.metric("المعدل النهائي", f"{average:.2f}%")

    # --- التقدير ---
    excellent_msgs = [
        "ما شاء الله! مستوى رهيب، استمر كذا 🌟",
        "أداء ممتاز فعلاً، فخورين فيك! 🏆",
        "قمة التميز، خلك على هالمستوى 🚀"
    ]
    good_msgs = [
        "شغل جميل، خطوة كمان توصل للممتاز 👍",
        "مستوى جيد جداً، كمّل بنفس الجهد 💫",
        "أنت قريب من القمة، استمر! 🔥"
    ]
    ok_msgs = [
        "مستوى مقبول، تقدر تتحسن بشوي جهد إضافي 📘",
        "بداية كويسة، ركّز أكثر بالمواد الصعبة 💡",
        "تقدر توصل لمستوى أعلى، لا تستسلم 🌱"
    ]
    weak_msgs = [
        "ما تشوف مستواك الحالي نهاية الطريق، الفصل الجاي فرصتك 💪",
        "كل بداية فيها تحديات، خطط للمذاكرة أكثر وبتتحسن 🌟",
        "لا تحبط، غيّر طريقة مذاكرتك وشوف الفرق الفصل الجاي 📚"
    ]

    if average >= 90:
        grade_text = "ممتاز (A) 🌟"
        st.success("🌟 التقدير: ممتاز (A)")
        st.info(random.choice(excellent_msgs))
    elif average >= 80:
        grade_text = "جيد جداً (B) 👍"
        st.info("👍 التقدير: جيد جداً (B)")
        st.info(random.choice(good_msgs))
    elif average >= 70:
        grade_text = "جيد (C) 📘"
        st.warning("📘 التقدير: جيد (C)")
        st.info(random.choice(ok_msgs))
    else:
        grade_text = "بحاجة لمزيد من الاجتهاد 💪"
        st.error("💪 تحتاج للمزيد من الاجتهاد!")
        st.info(random.choice(weak_msgs))

    st.divider()

    # --- تقرير جاهز للطباعة / الحفظ كـ PDF ---
    st.subheader("🖨️ تقرير جاهز للطباعة")
    st.caption("هذا تقرير غير رسمي لاستخدامك الشخصي — الشهادة الرسمية المعتمدة تصدر من المدرسة فقط.")

    if is_university:
        marks_rows = "".join(
            f"<tr><td style='padding:6px;border:1px solid #444;'>{name}</td>"
            f"<td style='padding:6px;border:1px solid #444;'>{mark:.1f}</td>"
            f"<td style='padding:6px;border:1px solid #444;'>{credit}</td></tr>"
            for name, mark, credit in subjects
        )
        table_header = """<tr><th style='padding:6px;border:1px solid #444;'>المادة</th>
                <th style='padding:6px;border:1px solid #444;'>الدرجة</th>
                <th style='padding:6px;border:1px solid #444;'>الساعات</th></tr>"""
    else:
        marks_rows = "".join(
            f"<tr><td style='padding:6px;border:1px solid #444;'>{name}</td>"
            f"<td style='padding:6px;border:1px solid #444;'>{mark:.1f}</td></tr>"
            for name, mark, credit in subjects
        )
        table_header = """<tr><th style='padding:6px;border:1px solid #444;'>المادة</th>
                <th style='padding:6px;border:1px solid #444;'>الدرجة</th></tr>"""

    report_html = f"""
    <div class="print-only" style="direction:rtl;text-align:right;font-family:Arial;padding:20px;">
        <h2>🎓 تقرير المعدل السنوي</h2>
        <p><b>اسم الطالب:</b> {student_name if student_name else "—"}</p>
        <p><b>المرحلة الدراسية:</b> {stage}</p>
        <p><b>التاريخ:</b> {date.today().strftime('%Y-%m-%d')}</p>
        <table style="border-collapse:collapse;width:100%;margin-top:10px;">
            {table_header}
            {marks_rows}
        </table>
        <p style="margin-top:15px;"><b>{"مجموع الساعات المعتمدة" if is_university else "مجموع الدرجات"}:</b> {f"{total_credits}" if is_university else f"{total_marks:.1f} / {num_subjects * 100}"}</p>
        <p><b>{"المعدل المرجّح (من 100)" if is_university else "المعدل النهائي"}:</b> {average:.2f}%</p>
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
