import streamlit as st
import io
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Marriage Certificate Generator", page_icon="💍", layout="centered")

# 2. SECURITY LOCK & STEALTH MODE
if st.query_params.get("access") != "namaste":
    st.error("🔒 Access Denied / アクセス拒否")
    st.warning("Please use the official link provided to access this tool. / このツールにアクセスするには、提供された公式リンクを使用してください。")
    st.stop()
    
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# 3. APP HEADER
st.title("💍 Marriage Certificate Generator")
st.markdown("Fill out the details below to instantly generate your formatted PDF certificate. / 以下の詳細を入力して、PDF証明書を作成してください。")
st.write("---")

def load_font():
    font_path = "msgothic.ttc" 
    try:
        pdfmetrics.registerFont(TTFont('JapaneseFont', font_path, subfontIndex=0))
        return 'JapaneseFont'
    except Exception as e:
        st.error(f"⚠️ Font Error: Could not load '{font_path}'. Please ensure the font file is uploaded to the server.")
        return 'Helvetica'

def generate_pdf(data):
    buffer = io.BytesIO()
    font_name = load_font()

    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=60, bottomMargin=40)
    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('TitleStyle', parent=styles['Normal'], fontName=font_name, fontSize=16, alignment=1, spaceAfter=20)
    center_style = ParagraphStyle('Center', fontName=font_name, fontSize=11, alignment=1)
    left_style = ParagraphStyle('Left', fontName=font_name, fontSize=10, leading=14)
    cell_style = ParagraphStyle('CellStyle', fontName=font_name, fontSize=10, leading=12)

    def P(text):
        return Paragraph(text, cell_style)

    # Issued Place & Title
    elements.append(Paragraph(data["Issued Place (発行地)"], center_style))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("婚姻届証明書（Marriage certificate）", title_style))

    # --- REGISTRATION DATA ---
    reg_info = f"""
    <b>登録番号 (Registration No.):</b> {data['Registration No. (登録番号)']}<br/>
    <b>登録日 (Registration Date):</b> {data['Registration Date (登録日)']}<br/>
    <b>結婚日 (Marriage Date):</b> {data['Marriage Date (結婚日)']}<br/>
    <b>結婚の種類 (Marriage Type):</b> {data['Marriage Type (結婚の種類)']}
    """
    elements.append(Paragraph(reg_info, left_style))
    elements.append(Spacer(1, 15))

    # --- MAIN TABLE: HUSBAND & WIFE DETAILS (NIN Removed) ---
    main_table_data = [
        [P("<b>詳細 (Details)</b>"), P("<b>夫 (Husband)</b>"), P("<b>妻 (Wife)</b>")],
        [P("フルネーム<br/>(Full name)"), P(data["Husband's Name (夫の氏名)"]), P(data["Wife's Name (妻の氏名)"])],
        [P("生年月日<br/>(Date of birth)"), P(data["Husband's Date of Birth (夫の生年月日)"]), P(data["Wife's Date of Birth (妻の生年月日)"])],
        [P("市民権/パスポート番号<br/>(Citizenship/Passport No.)"), P(data["Husband's Citizenship/Passport (夫の身分証番号)"]), P(data["Wife's Citizenship/Passport (妻の身分証番号)"])],
        [P("永住住所<br/>(Permanent address)"), P(data["Husband's Address (夫の永住住所)"]), P(data["Wife's Address (妻の永住住所)"])],
        [P("父親のフルネーム<br/>(Full name of father)"), P(data["Husband's Father's Name (夫の父親の氏名)"]), P(data["Wife's Father's Name (妻の父親の氏名)"])],
        [P("母親のフルネーム<br/>(Full name of mother)"), P(data["Husband's Mother's Name (夫の母親の氏名)"]), P(data["Wife's Mother's Name (妻の母親の氏名)"])]
    ]

    t_main = Table(main_table_data, colWidths=[155, 180, 180]) 
    t_main.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
    ]))
    
    elements.append(t_main)
    elements.append(Spacer(1, 20))

    # --- REGISTRAR INFO ---
    registrar_info = f"""
    <b>地方登記官の名前 (Registrar's Name):</b> {data['Registrar Name (地方登記官の名前)']}<br/>
    <b>署名 (Signature):</b> ___________________________
    """
    elements.append(Paragraph(registrar_info, left_style))
    elements.append(Spacer(1, 25))

    # --- TRANSLATOR TABLE ---
    translator_table_data = [
        [P("翻訳者<br/>(Translator)"), "", P(data["Translator Name (翻訳者の氏名)"])],
        [P("日本の住所<br/>(Address in Japan)"), "", P(data["Address in Japan (日本での住所)"])]
    ]

    t_translator = Table(translator_table_data, colWidths=[110, 140, 265])
    t_translator.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BACKGROUND', (0,0), (1,-1), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('SPAN', (0, 0), (1, 0)),
        ('SPAN', (0, 1), (1, 1)),
    ]))

    elements.append(t_translator)
    doc.build(elements)
    
    buffer.seek(0)
    return buffer

# --- HELPER FUNCTION FOR DATE DROPDOWNS ---
years = ["Year"] + [str(y) for y in range(2040, 1920, -1)]
months = ["Month"] + [str(m).zfill(2) for m in range(1, 13)]
days = ["Day"] + [str(d).zfill(2) for d in range(1, 32)]

def render_date_dropdowns(label, key_prefix):
    st.write(label)
    col1, col2, col3 = st.columns(3)
    y = col1.selectbox("年 (Year)", years, key=f"{key_prefix}_y")
    m = col2.selectbox("月 (Month)", months, key=f"{key_prefix}_m")
    d = col3.selectbox("日 (Day)", days, key=f"{key_prefix}_d")
    if "Year" not in y and "Month" not in m and "Day" not in d:
        return f"{y}-{m}-{d}"
    return ""

# --- UI FORM ---
st.subheader("Registration Details / 登録情報")
issued_place = st.text_input("Issued Place (発行地)", placeholder="eg.ネパール・ガンダキ州カスキ郡ポカラ市役所")
reg_no = st.text_input("Registration No. (登録番号)")
reg_date = render_date_dropdowns("Registration Date (登録日)", "reg")
mar_date = render_date_dropdowns("Marriage Date (結婚日)", "mar")
mar_type = st.text_input("Marriage Type (結婚の種類)", value="2017年国市民（法典）法")

st.write("---")

st.subheader("Husband's Details / 夫の詳細")
h_name = st.text_input("Husband's Name (夫の氏名)")
h_dob = render_date_dropdowns("Husband's Date of Birth (夫の生年月日)", "h_dob")
h_id = st.text_input("Husband's Citizenship/Passport (夫の身分証番号)")
h_address = st.text_input("Husband's Address (夫の永住住所)")
h_father = st.text_input("Husband's Father's Name (夫の父親の氏名)")
h_mother = st.text_input("Husband's Mother's Name (夫の母親の氏名)")

st.write("---")

st.subheader("Wife's Details / 妻の詳細")
w_name = st.text_input("Wife's Name (妻の氏名)")
w_dob = render_date_dropdowns("Wife's Date of Birth (妻の生年月日)", "w_dob")
w_id = st.text_input("Wife's Citizenship/Passport (妻の身分証番号)")
w_address = st.text_input("Wife's Address (妻の永住住所)")
w_father = st.text_input("Wife's Father's Name (妻の父親の氏名)")
w_mother = st.text_input("Wife's Mother's Name (妻の母親の氏名)")

st.write("---")

st.subheader("Official Details / 公式詳細")
registrar = st.text_input("Registrar Name (地方登記官の名前)")

# --- SMART TRANSLATOR LOGIC ---
translator_options = []
if h_name: translator_options.append(h_name)
if w_name: translator_options.append(w_name)
translator_options.append("Other (手動入力)")

translator_choice = st.selectbox("Translator Name (翻訳者の氏名)", translator_options)

if translator_choice == "Other (手動入力)":
    translator_name = st.text_input("Enter the Translator's Full Name / 翻訳者の氏名を入力してください")
else:
    translator_name = translator_choice

address_japan = st.text_input("Address in Japan (日本での住所)")

st.write("---")

# --- GENERATE PDF BUTTON ---
if st.button("Generate PDF / PDFを作成", type="primary"):
    user_data = {
        "Issued Place (発行地)": issued_place,
        "Registration No. (登録番号)": reg_no,
        "Registration Date (登録日)": reg_date,
        "Marriage Date (結婚日)": mar_date,
        "Marriage Type (結婚の種類)": mar_type,
        "Husband's Name (夫の氏名)": h_name,
        "Husband's Date of Birth (夫の生年月日)": h_dob,
        "Husband's Citizenship/Passport (夫の身分証番号)": h_id,
        "Husband's Address (夫の永住住所)": h_address,
        "Husband's Father's Name (夫の父親の氏名)": h_father,
        "Husband's Mother's Name (夫の母親の氏名)": h_mother,
        "Wife's Name (妻の氏名)": w_name,
        "Wife's Date of Birth (妻の生年月日)": w_dob,
        "Wife's Citizenship/Passport (妻の身分証番号)": w_id,
        "Wife's Address (妻の永住住所)": w_address,
        "Wife's Father's Name (妻の父親の氏名)": w_father,
        "Wife's Mother's Name (妻の母親の氏名)": w_mother,
        "Registrar Name (地方登記官の名前)": registrar,
        "Translator Name (翻訳者の氏名)": translator_name,
        "Address in Japan (日本での住所)": address_japan
    }

    client_name = h_name if h_name else "Client"
    file_name = f"Marriage_Certificate_{client_name}.pdf"
    
    with st.spinner("Generating document... / ドキュメントを作成中..."):
        pdf_buffer = generate_pdf(user_data)
        
        st.success("Success! Click the button below to download the certificate. / 成功しました！")
        
        st.download_button(
            label="📄 Download PDF",
            data=pdf_buffer,
            file_name=file_name,
            mime="application/pdf"
        )