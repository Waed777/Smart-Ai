import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import os

# ===============================
# إعداد الصفحة
# ===============================
st.set_page_config(page_title="منصة الخطط العلاجية الذكية", layout="wide")

# ألوان زرقاء احترافية
st.markdown("""
<style>
.main {background-color: #f4f8ff;}
.stButton>button {background-color:#1f4ed8;color:white;border-radius:8px;}
.stTextInput>div>div>input {border-radius:8px;}
</style>
""", unsafe_allow_html=True)

# ===============================
# عرض الشعار
# ===============================
if os.path.exists("logoo.png"):
    st.image("logo.png", width=140)

st.title("🔵 منصة الخطط العلاجية الذكية")
st.caption("AI Smart Intervention Platform")

# ===============================
# تسجيل دخول بسيط
# ===============================
if "role" not in st.session_state:
    st.session_state.role = None

if st.session_state.role is None:
    st.subheader("🔐 تسجيل الدخول")

    role = st.selectbox("اختاري الدور", ["معلمة", "إدارة"])
    password = st.text_input("كلمة المرور", type="password")

    if st.button("دخول"):
        if role == "معلمة" and password == "teacher123":
            st.session_state.role = "معلمة"
        elif role == "إدارة" and password == "admin123":
            st.session_state.role = "إدارة"
        else:
            st.error("كلمة المرور غير صحيحة")

    st.stop()

# ===============================
# قاعدة بيانات محلية
# ===============================
if "plans" not in st.session_state:
    st.session_state.plans = []

# ===============================
# توليد خطة علاجية ذكية
# ===============================
def generate_plan(name, subject, grade, skill):
    plan = f"""
اسم المعلمة: {name}
المادة: {subject}
الصف: {grade}
المهارة الضعيفة: {skill}

🎯 الهدف السلوكي:
تحسين مستوى الطالبات في مهارة {skill} بنسبة 80٪ خلال أسبوعين.

🧠 الاستراتيجية:
التعلم التعاوني + التعزيز الإيجابي + أمثلة تطبيقية من الواقع.

📘 النشاط العلاجي:
تصميم ورقة عمل مركزة على {skill} مع أنشطة تفاعلية.

📝 أساليب التقويم:
اختبار قصير + ملاحظة أداء + تقييم ذاتي.

⏳ مدة التنفيذ:
حصتين أسبوعياً لمدة أسبوعين.

📊 مؤشر النجاح:
تحسن نتائج الطالبات في الاختبار البعدي بنسبة ملحوظة.
"""
    return plan

# ===============================
# واجهة المعلمة
# ===============================
if st.session_state.role == "معلمة":
    st.subheader("👩‍🏫 إنشاء خطة علاجية")

    name = st.text_input("اسم المعلمة")
    subject = st.text_input("المادة")
    grade = st.text_input("الصف")
    skill = st.text_area("المهارة الضعيفة")

    if st.button("✨ توليد الخطة العلاجية"):
        if name and subject and grade and skill:
            plan_text = generate_plan(name, subject, grade, skill)
            st.success("تم توليد الخطة بنجاح")
            st.text_area("الخطة العلاجية", plan_text, height=350)

            # حفظ في النظام
            st.session_state.plans.append({
                "التاريخ": datetime.now().strftime("%Y-%m-%d"),
                "المعلمة": name,
                "المادة": subject,
                "الصف": grade,
                "المهارة": skill
            })

            # إنشاء PDF
            pdf_file = "plan.pdf"
            doc = SimpleDocTemplate(pdf_file)
            styles = getSampleStyleSheet()

            pdfmetrics.registerFont(UnicodeCIDFont('HYSMyeongJo-Medium'))
            arabic_style = ParagraphStyle(
                'Arabic',
                parent=styles['Normal'],
                fontName='HYSMyeongJo-Medium',
                fontSize=12,
                textColor=colors.black
            )

            elements = []
            elements.append(Paragraph(plan_text.replace("\n", "<br/>"), arabic_style))
            doc.build(elements)

            with open(pdf_file, "rb") as f:
                st.download_button("📄 تحميل PDF", f, file_name="الخطة_العلاجية.pdf")

        else:
            st.warning("الرجاء تعبئة جميع الحقول")

# ===============================
# لوحة الإدارة
# ===============================
if st.session_state.role == "إدارة":
    st.subheader("📊 لوحة الإدارة")

    if len(st.session_state.plans) == 0:
        st.info("لا توجد خطط حالياً")
    else:
        df = pd.DataFrame(st.session_state.plans)

        col1, col2 = st.columns(2)
        col1.metric("عدد الخطط", len(df))
        col2.metric("عدد المعلمات", df["المعلمة"].nunique())

        st.dataframe(df, use_container_width=True)

        # تصدير Excel
        excel_file = "all_plans.xlsx"
        df.to_excel(excel_file, index=False)
        with open(excel_file, "rb") as f:
            st.download_button("⬇️ تحميل Excel", f, file_name="تقرير_الخطط.xlsx")

# ===============================
# تسجيل خروج
# ===============================
if st.button("تسجيل خروج"):
    st.session_state.role = None
    st.rerun()
