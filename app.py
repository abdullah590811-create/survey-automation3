import os
import json
import time
import uuid
import random
import socket
from datetime import datetime, timedelta
from flask import Flask, render_template_string, request, jsonify, Response
import requests

app = Flask(__name__)

# الرابط والتوكن المستخرجة من حسابك
SUBMIT_URL = "https://forms.guest.usercontent.microsoft/formapi/api/4fef011a-ec15-4171-b293-1b10bc52fda1/users/f4a071e2-1d10-4211-b1d1-20d4fc6077c8/forms('GgHvTxXscUGykxsQvFL9oeJxoPQQHRFCsdEg1Pxgd8hUMzFCN0hQTVRQNFU0WEtPME4yV1A1NVNZUS4u')/responses"
VERIFICATION_TOKEN = "obaT70YNbCwA8dGTULQREx9ulu2tPmNfx5OozWcaqKH-ZA57ImT-alP29FfDFSkT8qv82f0wob47qoj2_3BTMAQ7o5_1WvjvAeTFgUwymwHnYE3vwwghavvY8ENadG8Ga7U0N4uHWHPgsbxFbrAUTw2"

# ----------------- خوارزمية التوليد الإحصائي المتنوع والواقعي -----------------
def generate_realistic_response(persona="balanced"):
    # 1. الديموغرافيا
    gender = random.choices(["ذكر", "أنثى"], weights=[52, 48])[0]
    
    age_brackets = ["١٨-٢٤ سنة", "٢٥-٣٤ سنة", "٣٥-٤٤ سنة", "٤٥-٥٤ سنة", "٥٥ سنة فأكثر"]
    age_weights = [35, 42, 15, 6, 2]
    age = random.choices(age_brackets, weights=age_weights)[0]
    
    # ترابط الحالة الاجتماعية مع العمر
    if age == "١٨-٢٤ سنة":
        marital = random.choices(["أعزب / عزباء ", "متزوج / متزوجة"], weights=[85, 15])[0]
    else:
        marital = random.choices(["متزوج / متزوجة", "أعزب / عزباء ", "مطلق / مطلقة", "أرمل / أرملة"], weights=[68, 22, 8, 2])[0]
        
    nationality = random.choices(["سعودي", "غير سعودي"], weights=[88, 12])[0]
    
    # ترابط الطول والوزن
    if gender == "ذكر":
        height = random.choices(["١٥٦ سم - ١٦٥ سم", "١٦٦ سم - ١٧٥ سم", "١٧٦ سم - ١٨٥ سم", "١٨٦ سم - ١٩٥ سم"], weights=[15, 50, 30, 5])[0]
        weight = random.choices(["٦١ كجم - ٦٥ كجم", "٦٦ كجم - ٧٠ كجم", "٧١ كجم - ٧٥ كجم", "٧٦ كجم - ٨٠ كجم", "٨١ كجم - ٨٥ كجم", "٨٦ كجم - ٩٠ كجم", "٩١ كجم - ٩٥ كجم"], weights=[10, 15, 25, 25, 15, 7, 3])[0]
    else:
        height = random.choices(["١٣٦ سم - ١٤٥ سم", "١٤٦ سم - ١٥٥ سم", "١٥٦ سم - ١٦٥ سم", "١٦٦ سم - ١٧٥ سم"], weights=[5, 35, 45, 15])[0]
        weight = random.choices(["٤٦ كجم - ٥٠ كجم", "٥١ كجم - ٦٠ كجم", "٦١ كجم - ٦٥ كجم", "٦٦ كجم - ٧٠ كجم", "٧١ كجم - ٧٥ كجم", "٧٦ كجم - ٨٠ كجم"], weights=[10, 25, 30, 20, 10, 5])[0]
        
    education = random.choices(["ثانوي", "دبلوم", "بكالوريوس", "دراسات عليا"], weights=[18, 14, 58, 10])[0]
    income = random.choices(["أقل من ٣٠٠٠", "من ٣٠٠٠ إلى ٧٠٠٠", "من ٧٠٠١ إلى ١٢٠٠٠", "من ١٢٠٠١ إلى ٢٠٠٠٠", "أكثر من ٢٠٠٠٠"], weights=[20, 25, 30, 18, 7])[0]
    region = random.choices(["الوسطى", "الغربية", "الشرقية", "الجنوبية", "الشمالية"], weights=[40, 28, 18, 8, 6])[0]

    # 2. الصحة
    diet = random.choices(["نعم", "لا"], weights=[22, 78])[0]
    chronic = random.choices(["نعم", "لا"], weights=[9, 91])[0]
    respiratory = random.choices(["نعم", "لا"], weights=[8, 92])[0]
    weight_meds = random.choices(["نعم", "لا"], weights=[12, 88])[0]

    # 3. النيكوتين والتدخين
    if persona == "smoker":
        is_smoker = random.choices(["مدخن حالي", "مدخن سابق"], weights=[90, 10])[0]
        uses_nicotine = "نعم"
    elif persona == "healthy":
        is_smoker = "غير مدخن"
        uses_nicotine = "لا"
    else:
        is_smoker = random.choices(["مدخن حالي", "غير مدخن", "مدخن سابق"], weights=[40, 48, 12])[0]
        uses_nicotine = "نعم" if is_smoker == "مدخن حالي" else ("لا" if is_smoker == "غير مدخن" else random.choice(["نعم", "لا"]))

    product = random.choices(["السجائر الإلكترونية (الفيب)", "السجائر التقليدية", "الشيشة", "أكياس النيكوتين "], weights=[45, 28, 18, 9])[0]
    freq = random.choices(["يومياً", "احيانا", "نادرا"], weights=[60, 28, 12])[0]
    pouch_count = random.choices(["١-٥ أكياس", "٦-١٠ أكياس ", "١١-١٥ كيساً"], weights=[50, 35, 15])[0]
    pouch_conc = random.choices(["٢-٤ ملغم", "٥-٨ ملغم", "٩-١٢ ملغم", "١٣-٢٠ ملغم"], weights=[25, 40, 25, 10])[0]

    # 4. النشاط والنوم
    v_act = random.choices(["لا أمارس الرياضة", "١-٢ مره في الأسبوع ", "٣-٤ مرات في الأسبوع", "٥-٧ مرات في الأسبوع"], weights=[35, 35, 22, 8])[0]
    m_act = random.choices(["لا أمارس الرياضة", "١-٢ مره في الأسبوع ", "٣-٤ مرات في الأسبوع", "٥-٧ مرات في الأسبوع"], weights=[28, 40, 24, 8])[0]
    sleep_h = random.choices(["أقل من ٥ ساعات ", "٥-٧ ساعات", "أكثر من ٧ ساعات"], weights=[18, 62, 20])[0]
    sleep_q = random.choices(["جيدة جدا", "جيدة نوعا ما", "سيئة نوعا ما", "سيئة جدا"], weights=[28, 48, 18, 6])[0]
    sleep_lat = random.choices(["١٥ دقيقة او اقل", "١٦-٣٠ دقيقة", "٣١-٦٠ دقيقة"], weights=[40, 38, 22])[0]
    night_wake = random.choices(["لم يحدث ابدا", "اقل من مرة في الأسبوع", "مرة او مرتين في الأسبوع "], weights=[35, 35, 30])[0]
    day_fat = random.choices(["لم يحدث خلال الشهر الماضي", "أقل من مرة في الأسبوع", "مرة أو مرتين في الأسبوع"], weights=[28, 38, 34])[0]

    # 5. مقياس التحكم بالأكل (1 إلى 8)
    control_score = str(random.choices([1, 2, 3, 4, 5, 6, 7, 8], weights=[2, 4, 10, 20, 26, 22, 12, 4])[0])

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
        {"questionId": "r87150ac5fd0c4ad8afa7d47048cbb718", "answer1": product},
        {"questionId": "r98f43ecbaff147889167566860f149ab", "answer1": freq},
        {"questionId": "rfa7f543df5d34f2f9d8402cef51b8ae5", "answer1": pouch_count},
        {"questionId": "rd9bbcc354a8f4fad86ffbf9c968e8cb4", "answer1": pouch_conc},
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
        {"questionId": "r2393b1085172446d891c99bdca3491fd", "answer1": random.choice(["محتمل باعتدال", "من المحتمل جدا", "من المحتمل قليلا"])},
        {"questionId": "r0960b62ee63d403395ed15da0f4887bd", "answer1": random.choice(["عادة", "دائما تقريبا", "نادرا "])},
        {"questionId": "r6d869d8015bc4577b044885ac965cefc", "answer1": control_score},
        {"questionId": "r1a5592a6f3ce4a7ab529373f0b67391a", "answer1": {"id": random.randint(1, 4), "key": "778f8880-03ce-4e19-89c3-b9c6aefc6500"}},
        {"questionId": "r5956b9c6bcfe47a2ae2ee5279e3aeb90", "answer1": {"id": random.randint(1, 3), "key": "d65b0472-066c-4a05-88a5-d6b9699fefd3"}},
        {"questionId": "r38137ca693d043a2bac7daf7c77e57a3", "answer1": {"id": random.randint(2, 4), "key": "d65b0472-066c-4a05-88a5-d6b9699fefd3"}}
    ]

    # أسئلة المصفوفة الـ 13 مع تنوع إحصائي فردي لكل بند
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
        choice_id = random.choices([1, 2, 3, 4], weights=[12, 28, 42, 18])[0]
        answers.append({"questionId": qid, "answer1": {"id": choice_id, "key": "c37feec2-3e87-45b4-be5d-f21d837da0f3"}})

    return answers, gender, age, is_smoker

# ----------------- واجهة الويب المتجاوبة مع الجوال -----------------
HTML_PAGE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>أداة تعبئة استبيان النيكوتين الذكية</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen p-4 pb-20 font-sans">
    <div class="max-w-md mx-auto space-y-4">
        
        <!-- البطاقة الرئيسية -->
        <div class="bg-slate-800 border border-slate-700 rounded-3xl p-5 shadow-2xl space-y-4">
            <div class="flex items-center justify-between border-b border-slate-700 pb-3">
                <div class="flex items-center space-x-3 space-x-reverse">
                    <div class="w-10 h-10 rounded-2xl bg-teal-500 text-slate-950 font-black flex items-center justify-center text-sm shadow-lg shadow-teal-500/30">
                        ⚡
                    </div>
                    <div>
                        <h1 class="text-sm font-bold text-white leading-tight">تعبئة استبيان النيكوتين</h1>
                        <p class="text-[11px] text-teal-400">توليد بيانات متنوعة وواقعية 100%</p>
                    </div>
                </div>
                <span class="w-3 h-3 rounded-full bg-emerald-400 animate-pulse"></span>
            </div>

            <!-- خيارات الأنماط -->
            <div class="space-y-1.5">
                <label class="text-xs font-semibold text-slate-400">النمط الإحصائي:</label>
                <div class="grid grid-cols-3 gap-2">
                    <button onclick="setPersona('balanced', this)" class="persona-btn active py-2 px-1 bg-teal-600/30 border border-teal-500 rounded-xl text-center text-xs font-bold text-teal-300">
                        ⚖️ متوازن
                    </button>
                    <button onclick="setPersona('smoker', this)" class="persona-btn py-2 px-1 bg-slate-700/50 border border-slate-600 rounded-xl text-center text-xs font-bold text-slate-300">
                        🚬 مدخنون
                    </button>
                    <button onclick="setPersona('healthy', this)" class="persona-btn py-2 px-1 bg-slate-700/50 border border-slate-600 rounded-xl text-center text-xs font-bold text-slate-300">
                        🥗 غير مدخن
                    </button>
                </div>
            </div>

            <!-- إعدادات العدد والسرعة -->
            <div class="grid grid-cols-2 gap-3 pt-1">
                <div class="bg-slate-900/60 p-3 rounded-2xl border border-slate-700">
                    <label class="block text-[11px] font-bold text-slate-400 mb-1">العدد الإجمالي</label>
                    <input id="subCount" type="number" value="10" min="1" max="500" class="w-full bg-transparent text-center text-lg font-black text-white focus:outline-none">
                </div>
                <div class="bg-slate-900/60 p-3 rounded-2xl border border-slate-700">
                    <label class="block text-[11px] font-bold text-slate-400 mb-1">الفاصل (ثانية)</label>
                    <input id="subDelay" type="number" value="0.5" step="0.1" min="0.2" class="w-full bg-transparent text-center text-lg font-black text-white focus:outline-none">
                </div>
            </div>

            <!-- زر التشغيل -->
            <button id="startBtn" onclick="startGeneration()" class="w-full py-4 bg-teal-500 hover:bg-teal-400 active:scale-95 text-slate-950 font-black rounded-2xl shadow-lg shadow-teal-500/25 text-sm flex items-center justify-center gap-2 transition duration-200">
                <span>🚀 إرسال الردود الآن</span>
            </button>
        </div>

        <!-- شريط التقدم والسجل المباشر -->
        <div class="bg-slate-800 border border-slate-700 rounded-3xl p-5 shadow-2xl space-y-3">
            <div class="flex justify-between text-xs font-bold text-slate-400">
                <span id="progressTxt">الاستجابات: 0</span>
                <span id="percentTxt">0%</span>
            </div>
            <div class="w-full bg-slate-900 rounded-full h-2.5 overflow-hidden">
                <div id="progressBar" class="bg-teal-400 h-2.5 transition-all duration-200" style="width: 0%"></div>
            </div>

            <!-- صندوق السجل التفاعلي -->
            <div id="logBox" class="w-full h-44 bg-slate-950 rounded-2xl p-3 font-mono text-[11px] text-teal-400 overflow-y-auto space-y-1 text-left border border-slate-800/80" dir="ltr">
                <p class="text-slate-500">// Ready to dispatch realistic responses.</p>
            </div>
        </div>

    </div>

    <script>
        let currentPersona = 'balanced';

        function setPersona(type, el) {
            currentPersona = type;
            document.querySelectorAll('.persona-btn').forEach(b => {
                b.classList.remove('bg-teal-600/30', 'border-teal-500', 'text-teal-300');
                b.classList.add('bg-slate-700/50', 'border-slate-600', 'text-slate-300');
            });
            el.classList.add('bg-teal-600/30', 'border-teal-500', 'text-teal-300');
            el.classList.remove('bg-slate-700/50', 'border-slate-600', 'text-slate-300');
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

            btn.disabled = true;
            btn.classList.add('opacity-50');
            log(`Starting realistic dispatch of ${count} responses...`, 'text-cyan-400 font-bold');

            let success = 0;
            for(let i = 1; i <= count; i++) {
                pTxt.innerText = `Submitting: ${i} / ${count}`;
                try {
                    const res = await fetch('/api/submit', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ persona: currentPersona })
                    });
                    const data = await res.json();
                    if(data.status === 201 || data.status === 200) {
                        success++;
                        log(`[✓] #${i} [${data.info}] Recorded (201 OK)`);
                    } else {
                        log(`[!] #${i} Error: ${data.msg}`, 'text-rose-400');
                    }
                } catch(e) {
                    log(`[!] Network Error: ${e.message}`, 'text-rose-400');
                }

                const currentPct = Math.round((i / count) * 100);
                bar.style.width = `${currentPct}%`;
                pct.innerText = `${currentPct}%`;

                if(i < count) await new Promise(r => setTimeout(r, delay * 1000));
            }

            btn.disabled = false;
            btn.classList.remove('opacity-50');
            log(`Complete! Total ${success} responses recorded in Microsoft Forms.`, 'text-amber-300 font-bold');
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
    persona = data.get('persona', 'balanced')
    
    answers, gender, age, is_smoker = generate_realistic_response(persona)
    
    now = datetime.utcnow()
    # وقت عشوائي منطقي لملء الاستبيان (بين دقيقتين و 5 دقائق)
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
        info_str = f"{gender} | {age} | {is_smoker}"
        return jsonify({"status": res.status_code, "info": info_str})
    except Exception as e:
        return jsonify({"status": 500, "msg": str(e)})

if __name__ == '__main__':
    # معرفة الآي بي المحلي لفتحه من الجوال
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'
    finally:
        s.close()

    print("\n" + "="*50)
    print("🚀 تم تشغيل الأداة بنجاح!")
    print(f"📱 لفتحها والتحكم بها من جوالك، افتح المتصفح واكتب:")
    print(f"👉 http://{local_ip}:5000")
    print("="*50 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)