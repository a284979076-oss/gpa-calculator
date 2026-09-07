import streamlit as st
import streamlit.components.v1 as components
from datetime import date
import random
import pandas as pd

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

# --- زر مشاركة سريع: واتساب + نسخ الرابط ---
components.html("""
<div style="display:flex;gap:10px;margin:10px 0;font-family:Arial;">
    <a id="wa-share" href="#" target="_blank" style="
        background-color:#25D366;color:white;padding:8px 16px;
        border-radius:8px;text-decoration:none;font-size:14px;">
        📤 شارك عبر واتساب
    </a>
    <button id="copy-link-btn" style="
        background-color:#444;color:white;padding:8px 16px;
        border:none;border-radius:8px;font-size:14px;cursor:pointer;">
        🔗 انسخ الرابط
    </button>
</div>
<script>
    const currentUrl = window.parent.location.href;
    const waLink = document.getElementById('wa-share');
    waLink.href = "https://wa.me/?text=" + encodeURIComponent("جرب حاسبة المعدل السنوي: " + currentUrl);

    const copyBtn = document.getElementById('copy-link-btn');
    copyBtn.onclick = function() {
        navigator.clipboard.writeText(currentUrl);
        copyBtn.innerText = "✅ تم النسخ!";
        setTimeout(() => { copyBtn.innerText = "🔗 انسخ الرابط"; }, 2000);
    };
</script>
""", height=60)

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

# --- قوائم مواد شائعة (غير رسمية) لتسريع تعبئة النموذج ---
subject_presets = {
    "ابتدائي": ["اللغة العربية", "اللغة الإنجليزية", "الرياضيات", "العلوم",
                "التربية الإسلامية", "الهوية والمواطنة", "تقنية المعلومات",
                "التربية البدنية والصحية", "الفنون البصرية", "الفنون الموسيقية"],
    "إعدادي": ["اللغة العربية", "اللغة الإنجليزية", "الرياضيات", "العلوم",
               "التربية الإسلامية", "الدراسات الاجتماعية", "تقنية المعلومات",
               "التربية البدنية", "الفنون"],
    "ثانوي": ["اللغة العربية", "اللغة الإنجليزية", "الرياضيات", "الفيزياء",
              "الكيمياء", "الأحياء", "التربية الإسلامية", "الدراسات الاجتماعية",
              "تقنية المعلومات"],
}

if not is_university:
    with st.expander("📚 اختر مواد شائعة لتعبئتها تلقائياً (اختياري)"):
        st.caption("⚠️ هذي قائمة شائعة للمساعدة السريعة فقط، مو قائمة رسمية معتمدة من الوزارة — تقدر تعدل أو تحذف أي مادة بعدها.")
        picked_subjects = st.multiselect(
            "اختر المواد اللي تبيها",
            subject_presets[stage],
            key="picked_subjects"
        )
        if st.button("➕ املأ المواد المختارة تلقائياً"):
            if picked_subjects:
                st.session_state["num_subjects"] = len(picked_subjects)
                for idx, subj_name in enumerate(picked_subjects, start=1):
                    st.session_state[f"name_{idx}"] = subj_name
                st.rerun()
            else:
                st.warning("اختر مادة وحدة على الأقل أول!")

st.divider()

# --- إدخال عدد المواد ---
num_subjects = st.number_input(
    "كم عدد المواد الدراسية؟",
    min_value=1,
    max_value=30,
    value=5,
    step=1,
    key="num_subjects"
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

# --- أداة إضافية: حاسبة الدرجة المطلوبة للهدف ---
with st.expander("🎯 حاسبة الدرجة المطلوبة لتحقيق هدفك"):
    st.write("حدد هدفك، وشوف كم تحتاج تجيب بالمواد الباقية عشان توصله!")

    goal_current_avg = st.number_input(
        "معدلك الحالي (%) بالمواد اللي دخلتها لين الحين",
        min_value=0.0, max_value=100.0, value=0.0, step=0.5,
        key="goal_current_avg"
    )
    goal_done_count = st.number_input(
        "كم مادة دخلتها لين الحين؟",
        min_value=0, max_value=30, value=0, step=1,
        key="goal_done_count"
    )
    goal_remaining_count = st.number_input(
        "كم مادة باقية عليك؟",
        min_value=1, max_value=30, value=1, step=1,
        key="goal_remaining_count"
    )
    goal_target = st.number_input(
        "المعدل النهائي اللي تبيه (%)",
        min_value=0.0, max_value=100.0, value=90.0, step=0.5,
        key="goal_target"
    )

    if st.button("احسب المطلوب 🎯"):
        total_subjects_goal = goal_done_count + goal_remaining_count
        needed_total = (goal_target * total_subjects_goal) - (goal_current_avg * goal_done_count)
        needed_avg = needed_total / goal_remaining_count

        if needed_avg > 100:
            st.error(f"⚠️ للأسف هدفك غير ممكن رياضياً بالمواد الباقية — تحتاج {needed_avg:.1f}% وهذا أعلى من 100%.")
        elif needed_avg < 0:
            st.success("🎉 مبروك! هدفك محقق فعلاً حتى لو جبت صفر بالباقي!")
        else:
            st.success(f"✅ تحتاج تجيب بالمتوسط {needed_avg:.1f}% بالمواد الباقية عشان توصل لهدفك.")

st.divider()

# --- أداة إضافية: مقارنة الفصول (تشتغل بس بنفس الجلسة، تنمسح لو سكرت المتصفح) ---
if "semesters" not in st.session_state:
    st.session_state.semesters = []  # قائمة تخزن كل فصل: (اسم, معدل)

with st.expander("📊 قارن بين فصولك الدراسية"):
    st.caption("⚠️ هذي المقارنة تشتغل بس أثناء تصفحك الحالي — تنمسح لو سكرت المتصفح أو حدّثت الصفحة.")

    col_sem_name, col_sem_avg = st.columns(2)
    with col_sem_name:
        sem_name = st.text_input("اسم الفصل (مثلاً: الفصل الأول)", key="sem_name")
    with col_sem_avg:
        sem_avg = st.number_input(
            "معدل هذا الفصل (%)",
            min_value=0.0, max_value=100.0, value=0.0, step=0.5,
            key="sem_avg"
        )

    if st.button("➕ أضف هذا الفصل للمقارنة"):
        if sem_name:
            st.session_state.semesters.append((sem_name, sem_avg))
            st.success(f"تمت إضافة {sem_name} بمعدل {sem_avg}%")
        else:
            st.warning("لازم تكتب اسم للفصل أول!")

    if st.session_state.semesters:
        st.write("### الفصول المضافة:")
        for idx, (name, avg) in enumerate(st.session_state.semesters):
            col_a, col_b = st.columns([4, 1])
            col_a.write(f"**{name}:** {avg}%")
            if col_b.button("🗑️", key=f"del_sem_{idx}"):
                st.session_state.semesters.pop(idx)
                st.rerun()

        chart_labels = [name for name, avg in st.session_state.semesters]
        chart_values = [avg for name, avg in st.session_state.semesters]
        chart_df = pd.DataFrame({"المعدل": chart_values}, index=chart_labels)
        st.bar_chart(chart_df)

        if st.button("🧹 امسح كل الفصول"):
            st.session_state.semesters = []
            st.rerun()
