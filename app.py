import streamlit as st

# --- إعدادات الصفحة ---
st.set_page_config(page_title="حاسبة المعدل السنوي", page_icon="🎓")

st.title("🎓 حاسبة المعدل السنوي")
st.write("أدخل درجاتك في المواد الدراسية وشوف معدلك النهائي فوراً!")

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

# --- إدخال الدرجات ---
marks = []
error_found = False

st.subheader("📝 أدخل درجاتك:")

for i in range(1, int(num_subjects) + 1):
    mark = st.number_input(
        f"درجة المادة رقم {i} (من 100)",
        min_value=0.0,
        max_value=100.0,
        value=0.0,
        step=0.5,
        key=f"mark_{i}"
    )
    marks.append(mark)

st.divider()

# --- زر الحساب ---
if st.button("احسب المعدل ✅", type="primary"):

    total_marks = sum(marks)
    average = total_marks / num_subjects

    st.subheader("📊 النتيجة:")
    col1, col2 = st.columns(2)
    col1.metric("مجموع الدرجات", f"{total_marks:.1f} / {num_subjects * 100}")
    col2.metric("المعدل النهائي", f"{average:.2f}%")

    # --- التقدير ---
    if average >= 90:
        st.success("🌟 التقدير: ممتاز (A)")
    elif average >= 80:
        st.info("👍 التقدير: جيد جداً (B)")
    elif average >= 70:
        st.warning("📘 التقدير: جيد (C)")
    else:
        st.error("💪 تحتاج للمزيد من الاجتهاد!")

st.divider()
st.caption("فالك النجاح 🌟 — من: أبو محمد")
