import os
import json
import time
import uuid
import random
from datetime import datetime, timedelta
from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

SUBMIT_URL = "https://forms.guest.usercontent.microsoft/formapi/api/4fef011a-ec15-4171-b293-1b10bc52fda1/users/f4a071e2-1d10-4211-b1d1-20d4fc6077c8/forms('GgHvTxXscUGykxsQvFL9oeJxoPQQHRFCsdEg1Pxgd8hUMzFCN0hQTVRQNFU0WEtPME4yV1A1NVNZUS4u')/responses"
VERIFICATION_TOKEN = "obaT70YNbCwA8dGTULQREx9ulu2tPmNfx5OozWcaqKH-ZA57ImT-alP29FfDFSkT8qv82f0wob47qoj2_3BTMAQ7o5_1WvjvAeTFgUwymwHnYE3vwwghavvY8ENadG8Ga7U0N4uHWHPgsbxFbrAUTw2"

# ----------------- محرك التوليد المنطقي والشرطي الذكي -----------------
def generate_smart_response(prefs):
    # تفضيلات الديموغرافيا
    male_pct = int(prefs.get('male_pct', 50))
    youth_pct = int(prefs.get('youth_pct', 70))
    region_pref = prefs.get('region_pref', 'mixed')
    
    # تفضيلات النيكوتين
    smoker_pct = int(prefs.get('smoker_pct', 45))
    vape_w = int(prefs.get('vape_w', 40))
    cig_w = int(prefs.get('cig_w', 35))
    shisha_w = int(prefs.get('shisha_w', 15))
    pouch_w = int(prefs.get('pouch_w', 10))
    
    # تفضيلات الشهية والصحة
    diet_pct = int(prefs.get('diet_pct', 25))
    control_level = prefs.get('control_level', 'medium')
    activity_level = prefs.get('activity_level', 'medium')

    # 1. تحديد الجنس وحالة الحمل التابعة
    gender = "ذكر" if random.randint(1, 100) <= male_pct else "أنثى"
    pregnancy = "لا"  # افتراضي آمن للأسئلة الإجبارية
    if gender == "أنثى" and random.randint(1, 100) <= 6:
        pregnancy = "نعم"

    # 2. العمر والترابط الاجتماعي
    if random.randint(1, 100) <= youth_pct:
        age = random.choices(["١٨-٢٤ سنة", "٢٥-٣٤ سنة"], weights=[45, 55])[0]
        marital = random.choices(["أعزب / عزباء ", "متزوج / متزوجة"], weights=[82, 18])[0]
        education = random.choices(["بكالوريوس", "ثانوي", "دبلوم"], weights=[65, 20, 15])[0]
    else:
        age = random.choices(["٣٥-٤٤ سنة", "٤٥-٥٤ سنة", "٥٥ سنة فأكثر"], weights=[60, 30, 10])[0]
        marital = random.choices(["متزوج / متزوجة", "أعزب / عزباء ", "مطلق / مطلقة", "أرمل / أرملة"], weights=[75, 15, 8, 2])[0]
        education = random.choices(["بكالوريوس", "دراسات عليا", "دبلوم", "ثانوي"], weights=[55, 20, 15, 10])[0]

    nationality = random.choices(["سعودي", "غير سعودي"], weights=[88, 12])[0]

    # ترابط الطول والوزن الواقعي
    if gender == "ذكر":
        height = random.choices(["١٥٦ سم - ١٦٥ سم", "١٦٦ سم - ١٧٥ سم", "١٧٦ سم - ١٨٥ سم", "١٨٦ سم - ١٩٥ سم"], weights=[15, 52, 28, 5])[0]
        weight = random.choices(["٦١ كجم - ٦٥ كجم", "٦٦ كجم - ٧٠ كجم", "٧١ كجم - ٧٥ كجم", "٧٦ كجم - ٨٠ كجم", "٨١ كجم - ٨٥ كجم", "٨٦ كجم - ٩٠ كجم"], weights=[10, 18, 26, 24, 14, 8])[0]
    else:
        height = random.choices(["١٣٦ سم - ١٤٥ سم", "١٤٦ سم - ١٥٥ سم", "١٥٦ سم - ١٦٥ سم", "١٦٦ سم - ١٧٥ سم"], weights=[5, 35, 45, 15])[0]
        weight = random.choices(["٤٦ كجم - ٥٠ كجم", "٥١ كجم - ٦٠ كجم", "٦١ كجم - ٦٥ كجم", "٦٦ كجم - ٧٠ كجم", "٧١ كجم - ٧٥ كجم"], weights=[12, 28, 32, 18, 10])[0]

    income = random.choices(["أقل من ٣٠٠٠", "من ٣٠٠٠ إلى ٧٠٠٠", "من ٧٠٠١ إلى ١٢٠٠٠", "من ١٢٠٠١ إلى ٢٠٠٠٠", "أكثر من ٢٠٠٠٠"], weights=[20, 25, 30, 18, 7])[0]
    
    if region_pref == 'central':
        region = random.choices(["الوسطى", "الغربية", "الشرقية", "الجنوبية", "الشمالية"], weights=[70, 15, 8, 4, 3])[0]
    elif region_pref == 'western':
        region = random.choices(["الغربية", "الوسطى", "الشرقية", "الجنوبية", "الشمالية"], weights=[65, 20, 8, 4, 3])[0]
    else:
        region = random.choices(["الوسطى", "الغربية", "الشرقية", "الجنوبية", "الشمالية"], weights=[40, 28, 18, 8, 6])[0]

    # 3. الصحة والحمية
    diet = "نعم" if random.randint(1, 100) <= diet_pct else "لا"
    chronic = random.choices(["نعم", "لا"], weights=[9, 91])[0]
    respiratory = random.choices(["نعم", "لا"], weights=[8, 92])[0]
    weight_meds = random.choices(["نعم", "لا"], weights=[11, 89])[0]

    # 4. التدخين والنيكوتين - التفرع المنطقي الذكي
    is_smoker = "مدخن حالي" if (random.randint(1, 100) <= smoker_pct) else random.choices(["غير مدخن", "مدخن سابق"], weights=[82, 18])[0]
    uses_nicotine = "نعم" if is_smoker == "مدخن حالي" else ("لا" if is_smoker == "غير مدخن" else random.choice(["نعم", "لا"]))

    tot_prod = vape_w + cig_w + shisha_w + pouch_w or 1
    primary_product = random.choices(
        ["السجائر التقليدية", "السجائر الإلكترونية (الفيب)", "الشيشة", "أكياس النيكوتين "],
        weights=[cig_w/tot_prod, vape_w/tot_prod, shisha_w/tot_prod, pouch_w/tot_prod]
    )[0]

    # منطق التفرع الخاص بالمنتج (تعبئة الإجابات التابعة بذكاء):
    # السجائر
    if is_smoker == "مدخن حالي" and primary_product == "السجائر التقليدية":
        cig_freq = random.choices(["يومياً", "احيانا"], weights=[75, 25])[0]
        cig_count = random.choices(["١-٥ سجائر", "٦-١٠ سجائر", "١١-٢٠ سيجارة", "أكثر من ٢٠ سيجارة"], weights=[25, 40, 25, 10])[0]
    else:
        cig_freq = "نادرا"
        cig_count = "١-٥ سجائر"

    # الشيشة
    if is_smoker == "مدخن حالي" and primary_product == "الشيشة":
        shisha_freq = random.choices(["يومياً", "احيانا"], weights=[35, 65])[0]
        shisha_sess = random.choices(["١-٢ جلسة", "٣-٥ جلسات", "اكثر من ٥ جلسات"], weights=[55, 35, 10])[0]
        shisha_dur = random.choices(["ساعات", "دقائق"], weights=[65, 35])[0]
    else:
        shisha_freq = "نادرا"
        shisha_sess = "١-٢ جلسة"
        shisha_dur = "دقائق"

    # الفيب
    if is_smoker == "مدخن حالي" and primary_product == "السجائر الإلكترونية (الفيب)":
        vape_freq = random.choices(["يومياً", "احيانا"], weights=[80, 20])[0]
        vape_count = random.choices(["١-٥ مرات", "٦-١٠ مرات", "اكثر من ١٠ مرات"], weights=[25, 40, 35])[0]
    else:
        vape_freq = "نادرا"
        vape_count = "١-٥ مرات"

    # الأكياس
    if is_smoker == "مدخن حالي" and primary_product == "أكياس النيكوتين ":
        pouch_freq = random.choices(["يومياً", "احيانا"], weights=[70, 30])[0]
        pouch_count = random.choices(["١-٥ أكياس", "٦-١٠ أكياس ", "١١-١٥ كيساً"], weights=[45, 40, 15])[0]
        pouch_conc = random.choices(["٥-٨ ملغم", "٩-١٢ ملغم", "١٣-٢٠ ملغم"], weights=[45, 40, 15])[0]
    else:
        pouch_freq = "نادرا"
        pouch_count = "١-٥ أكياس"
        pouch_conc = "٢-٤ ملغم"

    # 5. النشاط والنوم
    if activity_level == 'high':
        v_act = random.choices(["٣-٤ مرات في الأسبوع", "٥-٧ مرات في الأسبوع"], weights=[55, 45])[0]
        m_act = random.choices(["٣-٤ مرات في الأسبوع", "٥-٧ مرات في الأسبوع"], weights=[50, 50])[0]
    elif activity_level == 'low':
        v_act = random.choices(["لا أمارس الرياضة", "١-٢ مره في الأسبوع "], weights=[75, 25])[0]
        m_act = random.choices(["لا أمارس الرياضة", "١-٢ مره في الأسبوع "], weights=[65, 35])[0]
    else:
        v_act = random.choices(["لا أمارس الرياضة", "١-٢ مره في الأسبوع ", "٣-٤ مرات في الأسبوع"], weights=[35, 45, 20])[0]
        m_act = random.choices(["١-٢ مره في الأسبوع ", "٣-٤ مرات في الأسبوع", "لا أمارس الرياضة"], weights=[45, 35, 20])[0]

    sleep_h = random.choices(["أقل من ٥ ساعات ", "٥-٧ ساعات", "أكثر من ٧ ساعات"], weights=[16, 64, 20])[0]
    sleep_q = random.choices(["جيدة جدا", "جيدة نوعا ما", "سيئة نوعا ما"], weights=[30, 52, 18])[0]
    sleep_lat = random.choices(["١٥ دقيقة او اقل", "١٦-٣٠ دقيقة", "٣١-٦٠ دقيقة"], weights=[42, 38, 20])[0]
    night_wake = random.choices(["لم يحدث ابدا", "اقل من مرة في الأسبوع", "مرة او مرتين في الأسبوع "], weights=[35, 35, 30])[0]
    day_fat = random.choices(["لم يحدث خلال الشهر الماضي", "أقل من مرة في الأسبوع", "مرة أو مرتين في الأسبوع"], weights=[30, 40, 30])[0]

    # 6. الشهية ومقياس 1-8
    if control_level == 'high':
        control_score = str(random.choices([6, 7, 8], weights=[35, 45, 20])[0])
        matrix_weights = [5, 15, 35, 45]
    elif control_level == 'low':
        control_score = str(random.choices([1, 2, 3, 4], weights=[20, 35, 30, 15])[0])
        matrix_weights = [35, 35, 20, 10]
    else:
        control_score = str(random.choices([3, 4, 5, 6], weights=[15, 30, 35, 20])[0])
        matrix_weights = [12, 28, 42, 18]

    # بناء مصفوفة الإجابات الكاملة (تضمن عدم نقص أي سؤال إجباري)
    answers = [
        {"questionId": "r41af6ec4edc64e478058417d69a06d68", "answer1": "أوافق على المشاركة "},
        {"questionId": "r09bce8ea15a34987ae59742bee682c3a", "answer1": gender},
        {"questionId": "r1e31048731aa49d69a5bc40cc91f114b", "answer1": age},
        {"questionId": "r893a149db2c24d81b8f9e9108eca4b33", "answer1": nationality},
        {"questionId": "r05790a41766f4f59ba81ca2ed7d8eda2", "answer1": height},
        {"questionId": "rc66361b19e9b4f87a6bc2e1e6c8fc102", "answer1": weight},
        {"questionId": "rad1e4a623ca843098aa38329ab4ca826", "answer1": marital},
        {"questionId": "r808287efa4bb49a597292533f9169e1e", "answer1": education},
        {"questionId": "rb6294016a8674110adafb959ec421446", "answer1": income},
        {"questionId": "ra5fd4c1c93a24c6797b98cdaacce033d", "answer1": region},
        {"questionId": "r3fb69a6c961a4d39b727df798493e34c", "answer1": diet},
        {"questionId": "r0f33b1d94e974c7daff13dca59a872d8", "answer1": chronic},
        {"questionId": "r58c3bbeabb2f4ef79330d39c9b0b6ef7", "answer1": respiratory},
        {"questionId": "r7cbe9441d8754bac987fe49cf1fdde89", "answer1": weight_meds},
        {"questionId": "rc5b3ca21c44c43acbd0339a2c7b95395", "answer1": is_smoker},
        {"questionId": "r929c33f1365f4db59d66ecb9b2088f77", "answer1": uses_nicotine},
        {"questionId": "r87150ac5fd0c4ad8afa7d47048cbb718", "answer1": primary_product},
        
        # إجابات المسارات الذكية لمنتجات النيكوتين
        {"questionId": "r98f43ecbaff147889167566860f149ab", "answer1": pouch_freq if primary_product == "أكياس النيكوتين " else cig_freq},
        {"questionId": "rfa7f543df5d34f2f9d8402cef51b8ae5", "answer1": pouch_count if primary_product == "أكياس النيكوتين " else cig_count},
        {"questionId": "rd9bbcc354a8f4fad86ffbf9c968e8cb4", "answer1": pouch_conc},

        # النشاط والنوم
        {"questionId": "rc13c64558dfc4ecdba67381d17536c85", "answer1": v_act},
        {"questionId": "r14a6dbc8b563410fb1cb35e447b7e358", "answer1": "٣٠ إلى ٦٠ دقيقة"},
        {"questionId": "rbbee9bae96b54449ac2634e32f188d7a", "answer1": m_act},
        {"questionId": "r1e6cf7947f2344c7ba18a41de29f0290", "answer1": "٣٠ إلى ٦٠ دقيقة"},
        {"questionId": "rd78b2fe562004f2180bae99684d2f134", "answer1": "٣٠ إلى ٦٠ دقيقة"},
        {"questionId": "r9e24b8523d5a4495b235d5894ccfc9af", "answer1": sleep_h},
        {"questionId": "rd6c8c768f0a548bba0c3d3be8c17006a", "answer1": sleep_q},
        {"questionId": "r6542a2b43ee64e38989528336f60d8a2", "answer1": sleep_lat},
        {"questionId": "rd66ea66c2f8e42e0b3c5f0f578900be4", "answer1": night_wake},
        {"questionId": "r69b0ade4d0e74796bc023f7a2f6062ad", "answer1": day_fat},
        
        # أسئلة الشهية وضبط الأكل
        {"questionId": "r2393b1085172446d891c99bdca3491fd", "answer1": random.choice(["محتمل باعتدال", "من المحتمل جدا", "من المحتمل قليلا"])},
        {"questionId": "r0960b62ee63d403395ed15da0f4887bd", "answer1": random.choice(["عادة", "دائما تقريبا", "نادرا "])},
        {"questionId": "r6d869d8015bc4577b044885ac965cefc", "answer1": control_score},
        {"questionId": "r1a5592a6f3ce4a7ab529373f0b67391a", "answer1": {"id": random.randint(1, 4), "key": "778f8880-03ce-4e19-89c3-b9c6aefc6500"}},
        {"questionId": "r5956b9c6bcfe47a2ae2ee5279e3aeb90", "answer1": {"id": random.randint(1, 3), "key": "d65b0472-066c-4a05-88a5-d6b9699fefd3"}},
        {"questionId": "r38137ca693d043a2bac7daf7c77e57a3", "answer1": {"id": random.randint(2, 4), "key": "d65b0472-066c-4a05-88a5-d6b9699fefd3"}}
    ]

    # أسئلة المصفوفة الـ 13
    matrix_ids = [
        "rbd92822cc5434bc9b7c27730395a2fe2", "r8c05c3f922b74896b7ac7b37459c692b",
        "rf0ab48eea584423a9adc9ab5676a504e", "r9eab681b3fe04b36bb01331695e77805",
        "rdc8c8c889eb84bbeb1c31fbee931c499", "rd5f4c5c3221e4588b18923faa7019f38",
        "r7ff13811ef744b66bd7f0e2cf3b8dd6a", "rd4aae7070cfd4c56b4864eb11885e08c",
        "r321bed2367084e4e90791fd87d63ac34", "r28b2cc01f44340d8ae6628bff98157f3",
        "rd13f05520b274f0eb28d11e4d9c91217", "rdeb4728c8dd34fb5837bd214fc88315a",
        "r0a686129643b488d91bf00a0b5b2b24c"
    ]
    for qid in matrix_ids:
        choice_id = random.choices([1, 2, 3, 4], weights=matrix_weights)[0]
        answers.append({"questionId": qid, "answer1": {"id": choice_id, "key": "c37feec2-3e87-45b4-be5d-f21d837da0f3"}})

    info_summary = f"{gender} | {age} | {is_smoker} ({primary_product.split()[0]})"
    return answers, info_summary

# ----------------- واجهة المستخدم الشاملة ذات التبويبات والشرائح -----------------
HTML_PAGE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>لوحة التحكم الشاملة بالاستبيان</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        input[type=range] { accent-color: #0d9488; }
        .no-scrollbar::-webkit-scrollbar { display: none; }
    </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen p-3 sm:p-5 pb-28 font-sans antialiased">
    <div class="max-w-lg mx-auto space-y-4">
        
        <!-- الهيدر -->
        <div class="bg-slate-900 border border-slate-800 rounded-3xl p-4 shadow-xl flex items-center justify-between">
            <div class="flex items-center space-x-3 space-x-reverse">
                <div class="w-10 h-10 rounded-2xl bg-teal-500 text-slate-950 font-black flex items-center justify-center text-base shadow-lg shadow-teal-500/25">
                    🎛️
                </div>
                <div>
                    <h1 class="text-sm font-bold text-white">التحكم الكامل والمنطقي بالاستبيان</h1>
                    <p class="text-[11px] text-teal-400">تفرع ذكي + تغطية جميع الأسئلة الإجبارية</p>
                </div>
            </div>
            <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
        </div>

        <!-- شريط التبويبات للتنقل السهل على الجوال -->
        <div class="flex space-x-2 space-x-reverse overflow-x-auto no-scrollbar py-1 text-xs">
            <button onclick="switchTab('tab-demo')" id="btn-tab-demo" class="tab-btn px-3.5 py-2 bg-teal-600/30 border border-teal-500 text-teal-300 font-bold rounded-xl whitespace-nowrap shadow-sm">1. الديموغرافيا</button>
            <button onclick="switchTab('tab-nicotine')" id="btn-tab-nicotine" class="tab-btn px-3.5 py-2 bg-slate-900 border border-slate-800 text-slate-400 font-bold rounded-xl whitespace-nowrap shadow-sm">2. التدخين والتفرع الذكي</button>
            <button onclick="switchTab('tab-health')" id="btn-tab-health" class="tab-btn px-3.5 py-2 bg-slate-900 border border-slate-800 text-slate-400 font-bold rounded-xl whitespace-nowrap shadow-sm">3. الشهية والحمية</button>
            <button onclick="switchTab('tab-activity')" id="btn-tab-activity" class="tab-btn px-3.5 py-2 bg-slate-900 border border-slate-800 text-slate-400 font-bold rounded-xl whitespace-nowrap shadow-sm">4. النشاط والنوم</button>
        </div>

        <!-- تبويب 1: الديموغرافيا -->
        <div id="tab-demo" class="tab-content bg-slate-900 border border-slate-800 rounded-3xl p-4 space-y-4 shadow-xl">
            <h2 class="text-xs font-black text-teal-400 uppercase tracking-wider border-b border-slate-800 pb-2">خيارات السكان والديموغرافيا</h2>
            
            <div class="space-y-1.5">
                <div class="flex justify-between text-xs font-semibold">
                    <span class="text-slate-300">نسبة الجنس (ذكور / إناث)</span>
                    <span id="maleLabel" class="text-teal-400 font-mono">50% ذكور | 50% إناث</span>
                </div>
                <input id="male_pct" type="range" min="0" max="100" value="50" oninput="updateGenderLabel(this.value)" class="w-full h-1.5 bg-slate-800 rounded-lg">
            </div>

            <div class="space-y-1.5">
                <div class="flex justify-between text-xs font-semibold">
                    <span class="text-slate-300">ترجيح فئة الشباب (١٨-٣٤ سنة)</span>
                    <span id="youthLabel" class="text-teal-400 font-mono">70%</span>
                </div>
                <input id="youth_pct" type="range" min="10" max="100" value="70" oninput="document.getElementById('youthLabel').innerText = this.value + '%'" class="w-full h-1.5 bg-slate-800 rounded-lg">
            </div>

            <div class="space-y-1.5">
                <label class="text-xs font-semibold text-slate-300 block">تركيز المنطقة السكنية الغالبة:</label>
                <select id="region_pref" class="w-full bg-slate-800 text-xs text-slate-200 border border-slate-700 rounded-xl p-2.5 focus:border-teal-500">
                    <option value="mixed">توزيع طبيعي متوازن بين كل مناطق المملكة</option>
                    <option value="central">تركيز عالي على المنطقة الوسطى (الرياض)</option>
                    <option value="western">تركيز عالي على المنطقة الغربية (جدة / مكة)</option>
                </select>
            </div>
        </div>

        <!-- تبويب 2: النيكوتين والتفرع الذكي -->
        <div id="tab-nicotine" class="tab-content hidden bg-slate-900 border border-slate-800 rounded-3xl p-4 space-y-4 shadow-xl">
            <div class="border-b border-slate-800 pb-2 flex justify-between items-center">
                <h2 class="text-xs font-black text-teal-400 uppercase tracking-wider">منطق التفرع الذكي للتدخين</h2>
                <span class="text-[10px] bg-teal-500/20 text-teal-300 px-2 py-0.5 rounded-full font-bold">تفرع تلقائي آمن</span>
            </div>

            <div class="bg-teal-950/30 border border-teal-500/30 rounded-2xl p-3 text-[11px] text-teal-200 leading-relaxed">
                💡 <b>كيف يعمل التفرع الذكي؟</b><br>
                عندما يختار النظام "السجائر"، يتم توجيهه إجبارياً لتعبئة كمية وتكرار السجائر بدقة، ونفس الأمر للفيب والشيشة والأكياس. ولن تبقى أي خانات فارغة في النتائج.
            </div>

            <div class="space-y-1.5">
                <div class="flex justify-between text-xs font-semibold">
                    <span class="text-slate-300">نسبة المدخنين العامة بالعينة</span>
                    <span id="smokerLabel" class="text-teal-400 font-mono">45% مدخن</span>
                </div>
                <input id="smoker_pct" type="range" min="0" max="100" value="45" oninput="document.getElementById('smokerLabel').innerText = this.value + '% مدخن'" class="w-full h-1.5 bg-slate-800 rounded-lg">
            </div>

            <div class="space-y-2 pt-2 border-t border-slate-800/80">
                <label class="text-[11px] font-bold text-slate-400 block">ترجيح المنتجات بين المدخنين:</label>
                <div class="grid grid-cols-2 gap-2 text-xs">
                    <div class="bg-slate-800/60 p-2.5 rounded-xl border border-slate-800">
                        <div class="flex justify-between text-[11px] mb-1">
                            <span>🚬 سجائر تقليدية</span>
                            <span id="cigLbl" class="text-teal-400">35%</span>
                        </div>
                        <input id="cig_w" type="range" min="0" max="100" value="35" oninput="document.getElementById('cigLbl').innerText = this.value + '%'" class="w-full h-1 bg-slate-700 rounded-lg">
                    </div>
                    <div class="bg-slate-800/60 p-2.5 rounded-xl border border-slate-800">
                        <div class="flex justify-between text-[11px] mb-1">
                            <span>💨 فيب / سحبة</span>
                            <span id="vapeLbl" class="text-teal-400">40%</span>
                        </div>
                        <input id="vape_w" type="range" min="0" max="100" value="40" oninput="document.getElementById('vapeLbl').innerText = this.value + '%'" class="w-full h-1 bg-slate-700 rounded-lg">
                    </div>
                    <div class="bg-slate-800/60 p-2.5 rounded-xl border border-slate-800">
                        <div class="flex justify-between text-[11px] mb-1">
                            <span>🏺 شيشة / معسل</span>
                            <span id="shishaLbl" class="text-teal-400">15%</span>
                        </div>
                        <input id="shisha_w" type="range" min="0" max="100" value="15" oninput="document.getElementById('shishaLbl').innerText = this.value + '%'" class="w-full h-1 bg-slate-700 rounded-lg">
                    </div>
                    <div class="bg-slate-800/60 p-2.5 rounded-xl border border-slate-800">
                        <div class="flex justify-between text-[11px] mb-1">
                            <span>⚪ أكياس النيكوتين</span>
                            <span id="pouchLbl" class="text-teal-400">10%</span>
                        </div>
                        <input id="pouch_w" type="range" min="0" max="100" value="10" oninput="document.getElementById('pouchLbl').innerText = this.value + '%'" class="w-full h-1 bg-slate-700 rounded-lg">
                    </div>
                </div>
            </div>
        </div>

        <!-- تبويب 3: الشهية وسلوك الأكل -->
        <div id="tab-health" class="tab-content hidden bg-slate-900 border border-slate-800 rounded-3xl p-4 space-y-4 shadow-xl">
            <h2 class="text-xs font-black text-teal-400 uppercase tracking-wider border-b border-slate-800 pb-2">الشهية، الحمية وضبط الأكل</h2>

            <div class="space-y-1.5">
                <div class="flex justify-between text-xs font-semibold">
                    <span class="text-slate-300">نسبة متبعي حمية أو نظام غذائي صارم</span>
                    <span id="dietLbl" class="text-teal-400 font-mono">25%</span>
                </div>
                <input id="diet_pct" type="range" min="0" max="100" value="25" oninput="document.getElementById('dietLbl').innerText = this.value + '%'" class="w-full h-1.5 bg-slate-800 rounded-lg">
            </div>

            <div class="space-y-2 pt-2 border-t border-slate-800/80">
                <label class="text-xs font-semibold text-slate-300 block">نمط التحكم بالشهية وسلوك الأكل:</label>
                <div class="grid grid-cols-3 gap-2">
                    <label class="cursor-pointer text-center">
                        <input type="radio" name="control_level" value="low" class="peer hidden">
                        <div class="py-2.5 px-1 text-[11px] font-bold rounded-xl border border-slate-700 peer-checked:bg-teal-500/20 peer-checked:border-teal-500 peer-checked:text-teal-300 text-slate-400 transition">
                            أكل عاطفي / تحكم ضعيف
                        </div>
                    </label>
                    <label class="cursor-pointer text-center">
                        <input type="radio" name="control_level" value="medium" checked class="peer hidden">
                        <div class="py-2.5 px-1 text-[11px] font-bold rounded-xl border border-slate-700 peer-checked:bg-teal-500/20 peer-checked:border-teal-500 peer-checked:text-teal-300 text-slate-400 transition">
                            متوسط وطبيعي
                        </div>
                    </label>
                    <label class="cursor-pointer text-center">
                        <input type="radio" name="control_level" value="high" class="peer hidden">
                        <div class="py-2.5 px-1 text-[11px] font-bold rounded-xl border border-slate-700 peer-checked:bg-teal-500/20 peer-checked:border-teal-500 peer-checked:text-teal-300 text-slate-400 transition">
                            تحكم صارم بالوزن
                        </div>
                    </label>
                </div>
            </div>
        </div>

        <!-- تبويب 4: النشاط والنوم -->
        <div id="tab-activity" class="tab-content hidden bg-slate-900 border border-slate-800 rounded-3xl p-4 space-y-4 shadow-xl">
            <h2 class="text-xs font-black text-teal-400 uppercase tracking-wider border-b border-slate-800 pb-2">النشاط البدني وجودة النوم</h2>

            <div class="space-y-2">
                <label class="text-xs font-semibold text-slate-300 block">معدل النشاط والتمارين الرياضية بالعينة:</label>
                <select id="activity_level" class="w-full bg-slate-800 text-xs text-slate-200 border border-slate-700 rounded-xl p-2.5 focus:border-teal-500">
                    <option value="medium">متوسط (تمارين 1-3 مرات أسبوعياً)</option>
                    <option value="high">مرتفع (رياضيون نشطون 4-7 مرات)</option>
                    <option value="low">منخفض (أغلب العينة خامل ولا يمارس)</option>
                </select>
            </div>
        </div>

        <!-- بطاقة الإرسال والتشغيل -->
        <div class="bg-slate-900 border border-slate-800 rounded-3xl p-4 space-y-3 shadow-xl">
            <div class="grid grid-cols-2 gap-3">
                <div class="bg-slate-800/50 p-2.5 rounded-2xl border border-slate-800 text-center">
                    <span class="block text-[11px] font-bold text-slate-400">العدد المطلوب</span>
                    <input id="subCount" type="number" value="10" min="1" max="500" class="w-full bg-transparent text-center text-lg font-black text-white focus:outline-none">
                </div>
                <div class="bg-slate-800/50 p-2.5 rounded-2xl border border-slate-800 text-center">
                    <span class="block text-[11px] font-bold text-slate-400">الفاصل (ثانية)</span>
                    <input id="subDelay" type="number" value="0.5" step="0.1" min="0.2" class="w-full bg-transparent text-center text-lg font-black text-white focus:outline-none">
                </div>
            </div>

            <button id="startBtn" onclick="startGeneration()" class="w-full py-4 bg-teal-500 hover:bg-teal-400 active:scale-95 text-slate-950 font-black rounded-2xl shadow-lg shadow-teal-500/25 text-sm flex items-center justify-center gap-2 transition duration-200">
                <span>🚀 إرسال الردود بالتفضيلات المحددة</span>
            </button>
        </div>

        <!-- شريط التقدم والسجل المباشر -->
        <div class="bg-slate-900 border border-slate-800 rounded-3xl p-4 shadow-xl space-y-2.5">
            <div class="flex justify-between text-xs font-bold text-slate-400">
                <span id="progressTxt">الاستجابات: 0</span>
                <span id="percentTxt">0%</span>
            </div>
            <div class="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                <div id="progressBar" class="bg-teal-400 h-2 transition-all duration-150" style="width: 0%"></div>
            </div>

            <div id="logBox" class="w-full h-36 bg-slate-950 rounded-2xl p-3 font-mono text-[11px] text-teal-400 overflow-y-auto space-y-1 text-left border border-slate-800/80" dir="ltr">
                <p class="text-slate-500">// Smart branching engine ready.</p>
            </div>
        </div>

    </div>

    <script>
        function switchTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('bg-teal-600/30', 'border-teal-500', 'text-teal-300');
                btn.classList.add('bg-slate-900', 'border-slate-800', 'text-slate-400');
            });
            document.getElementById(tabId).classList.remove('hidden');
            const activeBtn = document.getElementById('btn-' + tabId);
            activeBtn.classList.add('bg-teal-600/30', 'border-teal-500', 'text-teal-300');
            activeBtn.classList.remove('bg-slate-900', 'border-slate-800', 'text-slate-400');
        }

        function updateGenderLabel(val) {
            document.getElementById('maleLabel').innerText = `${val}% ذكور | ${100 - val}% إناث`;
        }

        function log(msg, color='text-teal-400') {
            const b = document.getElementById('logBox');
            const p = document.createElement('p');
            p.className = color;
            p.innerText = `[${new Date().toLocaleTimeString()}] ${msg}`;
            b.appendChild(p);
            b.scrollTop = b.scrollHeight;
        }

        async function startGeneration() {
            const count = parseInt(document.getElementById('subCount').value) || 10;
            const delay = parseFloat(document.getElementById('subDelay').value) || 0.5;
            const btn = document.getElementById('startBtn');
            const bar = document.getElementById('progressBar');
            const pTxt = document.getElementById('progressTxt');
            const pct = document.getElementById('percentTxt');

            const prefs = {
                male_pct: document.getElementById('male_pct').value,
                youth_pct: document.getElementById('youth_pct').value,
                region_pref: document.getElementById('region_pref').value,
                smoker_pct: document.getElementById('smoker_pct').value,
                cig_w: document.getElementById('cig_w').value,
                vape_w: document.getElementById('vape_w').value,
                shisha_w: document.getElementById('shisha_w').value,
                pouch_w: document.getElementById('pouch_w').value,
                diet_pct: document.getElementById('diet_pct').value,
                control_level: document.querySelector('input[name="control_level"]:checked').value,
                activity_level: document.getElementById('activity_level').value
            };

            btn.disabled = true;
            btn.classList.add('opacity-50');
            log(`Starting smart branching run for ${count} responses...`, 'text-cyan-400 font-bold');

            let success = 0;
            for(let i = 1; i <= count; i++) {
                pTxt.innerText = `Submitting: ${i} / ${count}`;
                try {
                    const res = await fetch('/api/submit', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ prefs: prefs })
                    });
                    const data = await res.json();
                    if(data.status === 201 || data.status === 200) {
                        success++;
                        log(`[✓] #${i} [${data.info}] Recorded (201 OK)`);
                    } else {
                        log(`[!] #${i} Server rejected: ${data.msg}`, 'text-rose-400');
                    }
                } catch(e) {
                    log(`[!] Connection Error: ${e.message}`, 'text-rose-400');
                }

                const currentPct = Math.round((i / count) * 100);
                bar.style.width = `${currentPct}%`;
                pct.innerText = `${currentPct}%`;

                if(i < count) await new Promise(r => setTimeout(r, delay * 1000));
            }

            btn.disabled = false;
            btn.classList.remove('opacity-50');
            log(`Done! Total ${success} responses recorded with full branching.`, 'text-amber-300 font-bold');
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/api/submit', methods=['POST'])
def submit_response():
    data = request.get_json() or {}
    prefs = data.get('prefs', {})
    
    answers, info_summary = generate_smart_response(prefs)
    
    now = datetime.utcnow()
    start = now - timedelta(minutes=random.randint(2, 5), seconds=random.randint(5, 50))
    
    payload = {
        "startDate": start.isoformat() + "Z",
        "submitDate": now.isoformat() + "Z",
        "answers": json.dumps(answers, ensure_ascii=False)
    }

    headers = {
        "__requestverificationtoken": VERIFICATION_TOKEN,
        "accept": "application/json",
        "content-type": "application/json",
        "odata-maxverion": "4.0",
        "odata-version": "4.0",
        "x-ms-form-request-ring": "business",
        "x-ms-form-request-source": "ms-formweb",
        "x-correlationid": str(uuid.uuid4()),
        "x-usersessionid": str(uuid.uuid4())
    }

    try:
        res = requests.post(SUBMIT_URL, headers=headers, json=payload, timeout=12)
        return jsonify({"status": res.status_code, "info": info_summary, "msg": res.text if res.status_code not in [200, 201] else "OK"})
    except Exception as e:
        return jsonify({"status": 500, "msg": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
