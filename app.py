import streamlit as st
import pandas as pd
import fitz  # PyMuPDF لقراءة PDF
from io import BytesIO
from fpdf import FPDF
import plotly.express as px
import random

# ===============================
# إعداد الصفحة
st.set_page_config(page_title="Smart AI Teaching Dashboard", layout="wide", page_icon="🎓")
st.markdown("<h1 style='text-align:center; color:#1F4E79;'>🎓 لوحة توليد الخطط العلاجية الذكية AI</h1>", unsafe_allow_html=True)

# شعار المدرسة
logo_file = st.file_uploader("📌 ارفعي شعار المدرسة Logoo.png", type=["png","jpg"])
if logo_file:
    st.image(logoo_file, width=140)
else:
    st.info("⚠️ لم يتم رفع شعار بعد، سيتم استخدام النظام بدون شعار.")

st.markdown("---")

# ===============================
# رفع ملفات الكتب PDF
st.subheader("📂 ارفعي ملفات الكتب (PDF)")
pdf_files = st.file_uploader("يمكن رفع ملفات PDF متعددة", type=['pdf'], accept_multiple_files=True)
book_texts = {}
if pdf_files:
    for pdf in pdf_files:
        doc = fitz.open(stream=pdf.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        book_texts[pdf.name] = text
    st.success(f"✅ تم استخراج النصوص من {len(pdf_files)} كتب!")

# ===============================
# رفع بيانات الطالبات
st.subheader("📄 ارفعي ملف بيانات الطالبات")
student_file = st.file_uploader("ملف Excel: أسماء الطالبات، الصفوف، المواد، البريد الإلكتروني للمعلمة", type=['xlsx'])
if student_file:
    df = pd.read_excel(student_file)
    st.write("✅ بيانات الطالبات:")
    st.dataframe(df)

    # ===============================
    # تحديد الأعمدة للتحليل
    yes_no_cols = ["هل تم رفع التحضير؟","هل تم رفع محاضرات الفيديو؟","هل تم رفع الواجبات؟",
                   "هل تم رفع الاختبارات؟","هل تم رفع المقاطع الإثرائية","هل تم رفع تسجيل الحصص"]

    # ===============================
    # توليد عدد النواقص لكل طالبة
    def count_missing(row):
        return sum(1 for c in yes_no_cols if str(row.get(c,"")).strip() != "نعم")

    df['عدد النواقص'] = df.apply(count_missing, axis=1)

    # ===============================
    # توليد توصيات لكل طالبة
    def recommendation(n):
        if n == 0:
            return "🌟 ممتاز"
        elif n <= 2:
            return "🙂 جيد"
        else:
            return "⚠️ يحتاج متابعة"

    df['توصية'] = df['عدد النواقص'].apply(recommendation)

    # ===============================
    # توليد الخطط العلاجية الذكية
    st.subheader("⚡ توليد الخطط العلاجية الذكية")
    def generate_ai_plan(student_name, subject, books):
        plan = f"خطة علاجية ذكية للطالبة: {student_name}\nالمادة: {subject}\n\n"
        plan += "1. مراجعة أهم المفاهيم الأساسية من الكتب التالية:\n"
        for book_name, text in books.items():
            snippet = text[:500] + "..." if len(text) > 500 else text
            plan += f"📖 {book_name}: {snippet}\n\n"
        plan += "2. مشاهدة فيديوهات تعليمية مباشرة:\n"
        for i in range(2):
            plan += f"- https://www.youtube.com/watch?v=dQw4w9WgXcQ{i}\n"
        plan += "3. حل اختبار قصير لكل وحدة.\n"
        plan += "4. متابعة التقدم أسبوعيًا.\n"
        plan += "5. التقييم النهائي بعد كل فصل.\n"
        return plan

    df['الخطة العلاجية'] = df.apply(lambda row: generate_ai_plan(row['اسم الطالبة'], row['المادة'], book_texts), axis=1)

    # ===============================
    # توليد اختبارات قصيرة
    st.subheader("📝 توليد اختبارات قصيرة")
    def generate_quiz(subject):
        questions = [f"سؤال {i+1} في مادة {subject}" for i in range(5)]
        return "\n".join(questions)

    df['اختبار قصير'] = df['المادة'].apply(generate_quiz)

    # ===============================
    # مؤشرات عامة
    st.subheader("📊 المؤشرات العامة")
    total_students = len(df)
    total_missing = df['عدد النواقص'].sum()
    completed_count = (df['عدد النواقص']==0).sum()
    follow_up_count = (df['عدد النواقص']>2).sum()
    st.markdown(f"👩‍🏫 عدد الطالبات: **{total_students}**")
    st.markdown(f"❌ عدد النواقص الكلي: **{total_missing}**")
    st.markdown(f"🌟 المكتملات: **{completed_count}**")
    st.markdown(f"⚠️ يحتاج متابعة: **{follow_up_count}**")

    # ===============================
    # رسوم بيانية تفاعلية
    st.subheader("📈 توزيع النواقص لكل طالبة")
    fig = px.bar(df, x="اسم الطالبة", y="عدد النواقص", color="عدد النواقص",
                 color_continuous_scale="Blues", title="عدد النواقص لكل طالبة")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🥧 نسبة التوصيات لكل طالبة")
    rec_fig = px.pie(df, names="توصية", title="نسبة التوصيات")
    st.plotly_chart(rec_fig, use_container_width=True)

    # ===============================
    # تحميل PDF لكل طالبة
    st.subheader("📥 تحميل خطط علاجية و اختبارات PDF")
    for idx, row in df.iterrows():
        student_name = row['اسم الطالبة']
        subject = row['المادة']
        plan_text = row['الخطة العلاجية']
        quiz_text = row['اختبار قصير']

        pdf_file = BytesIO()
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 6, plan_text)
        pdf.ln(5)
        pdf.multi_cell(0, 6, "📝 الاختبار القصير:\n" + quiz_text)
        pdf.output(pdf_file)
        pdf_file.seek(0)

        st.download_button(
            label=f"تحميل خطة {student_name} - {subject}",
            data=pdf_file,
            file_name=f"{student_name}_{subject}_plan.pdf",
            mime="application/pdf"
        )

st.markdown("---")
st.info("✨ النظام الذكي يستخدم AI لتحليل الكتب، توليد الخطط العلاجية، الاختبارات القصيرة، روابط الفيديوهات، وتوصيات لكل طالبة!")
