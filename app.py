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

HTML_PAGE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>التحكم الكامل بجميع خيارات الاستبيان</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        input[type=range] { accent-color: #0d9488; }
        .no-scrollbar::-webkit-scrollbar { display: none; }
    </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen p-3 sm:p-5 pb-36 font-sans antialiased">
    <div class="max-w-xl mx-auto space-y-4">
        
        <!-- الهيدر الرئيسي -->
        <header class="bg-slate-900 border border-slate-800 rounded-3xl p-4 shadow-xl flex items-center justify-between">
            <div class="flex items-center space-x-3 space-x-reverse">
                <div class="w-10 h-10 rounded-2xl bg-teal-500 text-slate-950 font-black flex items-center justify-center text-base shadow-lg shadow-teal-500/25">
                    🎛️
                </div>
                <div>
                    <h1 class="text-sm font-bold text-white">التحكم الفردي بجميع الخيارات</h1>
                    <p class="text-[11px] text-teal-400">45 سؤالاً مع شرائح تحكم مستقلة لكل خيار</p>
                </div>
            </div>
            <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
        </header>

        <!-- كرت القوالب السريعة والإعدادات العامة -->
        <div class="bg-slate-900 border border-slate-800 rounded-3xl p-4 space-y-3 shadow-xl">
            <div class="flex justify-between items-center">
                <span class="text-xs font-bold text-slate-300">قوالب جاهزة لتسهيل الضبط:</span>
            </div>
            <div class="grid grid-cols-3 gap-2">
                <button onclick="applyPreset('balanced')" class="py-2.5 px-1 bg-slate-800 hover:bg-slate-700 border border-slate-700 active:border-teal-500 rounded-xl text-center text-xs font-bold text-slate-200 transition">
                    ⚖️ عينة متوازنة
                </button>
                <button onclick="applyPreset('smoker')" class="py-2.5 px-1 bg-slate-800 hover:bg-slate-700 border border-slate-700 active:border-teal-500 rounded-xl text-center text-xs font-bold text-slate-200 transition">
                    🚬 مدخنون
                </button>
                <button onclick="applyPreset('healthy')" class="py-2.5 px-1 bg-slate-800 hover:bg-slate-700 border border-slate-700 active:border-teal-500 rounded-xl text-center text-xs font-bold text-slate-200 transition">
                    🥗 نمط صحي
                </button>
            </div>

            <div class="grid grid-cols-2 gap-3 pt-2 border-t border-slate-800">
                <div class="bg-slate-800/50 p-2.5 rounded-2xl border border-slate-800 text-center">
                    <span class="block text-[11px] font-bold text-slate-400">عدد الاستجابات</span>
                    <input id="subCount" type="number" value="10" min="1" max="500" class="w-full bg-transparent text-center text-lg font-black text-white focus:outline-none">
                </div>
                <div class="bg-slate-800/50 p-2.5 rounded-2xl border border-slate-800 text-center">
                    <span class="block text-[11px] font-bold text-slate-400">الفاصل (ثانية)</span>
                    <input id="subDelay" type="number" value="0.5" step="0.1" min="0.2" class="w-full bg-transparent text-center text-lg font-black text-white focus:outline-none">
                </div>
            </div>

            <label class="flex items-center space-x-2 space-x-reverse text-xs font-semibold text-slate-300 cursor-pointer pt-1">
                <input id="enforceConsent" type="checkbox" checked class="w-4 h-4 rounded text-teal-600 focus:ring-teal-500">
                <span>تثبيت السؤال الأول (الموافقة) 100% "أوافق على المشاركة"</span>
            </label>
        </div>

        <!-- أزرار تبويبات الأقسام للتنقل السلس على الجوال -->
        <div class="flex space-x-2 space-x-reverse overflow-x-auto no-scrollbar py-1 text-xs">
            <button onclick="switchTab('tab-demographics')" id="btn-tab-demographics" class="tab-btn px-3.5 py-2 bg-teal-600/30 border border-teal-500 text-teal-300 font-bold rounded-xl whitespace-nowrap shadow-sm">1. الديموغرافيا</button>
            <button onclick="switchTab('tab-health')" id="btn-tab-health" class="tab-btn px-3.5 py-2 bg-slate-900 border border-slate-800 text-slate-400 font-bold rounded-xl whitespace-nowrap shadow-sm">2. الصحة والحمية</button>
            <button onclick="switchTab('tab-nicotine')" id="btn-tab-nicotine" class="tab-btn px-3.5 py-2 bg-slate-900 border border-slate-800 text-slate-400 font-bold rounded-xl whitespace-nowrap shadow-sm">3. التدخين والنيكوتين</button>
            <button onclick="switchTab('tab-sleep-act')" id="btn-tab-sleep-act" class="tab-btn px-3.5 py-2 bg-slate-900 border border-slate-800 text-slate-400 font-bold rounded-xl whitespace-nowrap shadow-sm">4. النشاط والنوم</button>
            <button onclick="switchTab('tab-appetite')" id="btn-tab-appetite" class="tab-btn px-3.5 py-2 bg-slate-900 border border-slate-800 text-slate-400 font-bold rounded-xl whitespace-nowrap shadow-sm">5. الشهية ومقاييس الأكل</button>
        </div>

        <!-- الحاوية الديناميكية لكروت الأسئلة وشرائح الخيارات -->
        <div id="questionsContainer" class="space-y-3">
            <!-- يتم رسم الأسئلة بالكامل هنا عبر الجافاسكريبت -->
        </div>

        <!-- سجل الإرسال المباشر -->
        <div class="bg-slate-900 border border-slate-800 rounded-3xl p-4 shadow-xl space-y-2.5">
            <div class="flex justify-between text-xs font-bold text-slate-400">
                <span id="progressTxt">الاستجابات: 0</span>
                <span id="percentTxt">0%</span>
            </div>
            <div class="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                <div id="progressBar" class="bg-teal-400 h-2 transition-all duration-150" style="width: 0%"></div>
            </div>

            <div id="logBox" class="w-full h-36 bg-slate-950 rounded-2xl p-3 font-mono text-[11px] text-teal-400 overflow-y-auto space-y-1 text-left border border-slate-800/80" dir="ltr">
                <p class="text-slate-500">// Individual sliders ready. Adjust percentages and start.</p>
            </div>
        </div>

    </div>

    <!-- الشريط السفلي الثابت للتشغيل الفوري من الجوال -->
    <div class="fixed bottom-0 inset-x-0 bg-slate-900/90 backdrop-blur-md border-t border-slate-800 p-3 z-40 shadow-2xl">
        <div class="max-w-xl mx-auto">
            <button id="startBtn" onclick="runSubmissions()" class="w-full py-3.5 bg-teal-500 hover:bg-teal-400 active:scale-95 text-slate-950 font-black rounded-2xl shadow-lg shadow-teal-500/25 text-sm flex items-center justify-center gap-2 transition duration-200">
                <span>🚀 إرسال الردود بالخيارات والنسب المحددة</span>
            </button>
        </div>
    </div>

    <script>
        const EATING_SCALE_OPTIONS = ["دائماً", "غالباً", "أحياناً", "أبداً"];

        // قائمة الأسئلة الـ 45 الكاملة بجميع خياراتها
        const surveyQuestions = [
            // 1. الديموغرافيا
            { section: "tab-demographics", id: "r41af6ec4edc64e478058417d69a06d68", label: "1. نموذج الموافقة المستنيرة", options: ["أوافق على المشاركة ", "لا أوافق على المشاركة"], weights: { smoker: [100, 0], balanced: [100, 0], healthy: [100, 0] } },
            { section: "tab-demographics", id: "r09bce8ea15a34987ae59742bee682c3a", label: "2. الجنس", options: ["ذكر", "أنثى"], weights: { smoker: [65, 35], balanced: [50, 50], healthy: [45, 55] } },
            { section: "tab-demographics", id: "r1e31048731aa49d69a5bc40cc91f114b", label: "4. العمر", options: ["أقل من ١٨ سنة", "١٨-٢٤ سنة", "٢٥-٣٤ سنة", "٣٥-٤٤ سنة", "٤٥-٥٤ سنة", "٥٥ سنة فأكثر"], weights: { smoker: [2, 35, 40, 15, 6, 2], balanced: [2, 30, 35, 20, 10, 3], healthy: [1, 28, 40, 20, 8, 3] } },
            { section: "tab-demographics", id: "r893a149db2c24d81b8f9e9108eca4b33", label: "5. الجنسية", options: ["سعودي", "غير سعودي"], weights: { smoker: [88, 12], balanced: [85, 15], healthy: [85, 15] } },
            { section: "tab-demographics", id: "r05790a41766f4f59ba81ca2ed7d8eda2", label: "6. الطول (سم)", options: ["١٣٦ سم - ١٤٥ سم", "١٤٦ سم - ١٥٥ سم", "١٥٦ سم - ١٦٥ سم", "١٦٦ سم - ١٧٥ سم", "١٧٦ سم - ١٨٥ سم", "١٨٦ سم - ١٩٥ سم"], weights: { smoker: [2, 10, 30, 38, 18, 2], balanced: [2, 12, 32, 36, 16, 2], healthy: [1, 10, 30, 40, 17, 2] } },
            { section: "tab-demographics", id: "rc66361b19e9b4f87a6bc2e1e6c8fc102", label: "7. الوزن (كجم)", options: ["٤٠ كجم - ٤٥ كجم", "٤٦ كجم - ٥٠ كجم", "٥١ كجم - ٦٠ كجم", "٦١ كجم - ٦٥ كجم", "٦٦ كجم - ٧٠ كجم", "٧١ كجم - ٧٥ كجم", "٧٦ كجم - ٨٠ كجم", "٨١ كجم - ٨٥ كجم", "٨٦ كجم - ٩٠ كجم", "٩١ كجم - ٩٥ كجم", "٩٦ كجم - ١٠٠ كجم", "١٠١ كجم - ١٠٥ كجم", "١٠٦ كجم - ١١٠ كجم", "١١١ كجم - ١١٥ كجم"], weights: { smoker: [3, 6, 15, 18, 16, 14, 10, 8, 4, 3, 1, 1, 0.5, 0.5], balanced: [2, 5, 14, 16, 18, 15, 12, 8, 4, 3, 1.5, 0.5, 0.5, 0.5], healthy: [2, 5, 16, 20, 20, 16, 10, 5, 3, 1.5, 1, 0.5, 0, 0] } },
            { section: "tab-demographics", id: "rad1e4a623ca843098aa38329ab4ca826", label: "8. الحالة الاجتماعية", options: ["أعزب / عزباء ", "متزوج / متزوجة", "مطلق / مطلقة", "أرمل / أرملة"], weights: { smoker: [55, 40, 4, 1], balanced: [50, 45, 4, 1], healthy: [48, 48, 3, 1] } },
            { section: "tab-demographics", id: "r808287efa4bb49a597292533f9169e1e", label: "9. الحالة التعليمية", options: ["أقل من الثانوية", "ثانوي", "دبلوم", "بكالوريوس", "دراسات عليا"], weights: { smoker: [4, 25, 15, 50, 6], balanced: [3, 22, 12, 55, 8], healthy: [1, 18, 10, 60, 11] } },
            { section: "tab-demographics", id: "rb6294016a8674110adafb959ec421446", label: "10. الدخل الشهري (ريال سعودي)", options: ["أقل من ٣٠٠٠", "من ٣٠٠٠ إلى ٧٠٠٠", "من ٧٠٠١ إلى ١٢٠٠٠", "من ١٢٠٠١ إلى ٢٠٠٠٠", "أكثر من ٢٠٠٠٠"], weights: { smoker: [25, 20, 28, 18, 9], balanced: [22, 22, 30, 18, 8], healthy: [18, 20, 32, 21, 9] } },
            { section: "tab-demographics", id: "ra5fd4c1c93a24c6797b98cdaacce033d", label: "11. المنطقة السكنية", options: ["الوسطى", "الشمالية", "الجنوبية", "الغربية", "الشرقية"], weights: { smoker: [42, 6, 9, 25, 18], balanced: [40, 6, 8, 28, 18], healthy: [38, 6, 8, 30, 18] } },

            // 2. الصحة والحمية
            { section: "tab-health", id: "r3fb69a6c961a4d39b727df798493e34c", label: "12. هل تتبع حمية أو نظام غذائي صارم؟", options: ["نعم", "لا"], weights: { smoker: [15, 85], balanced: [25, 75], healthy: [45, 55] } },
            { section: "tab-health", id: "r0f33b1d94e974c7daff13dca59a872d8", label: "13. هل لديك أي مرض مزمن مشخص من قبل طبيب؟", options: ["نعم", "لا"], weights: { smoker: [12, 88], balanced: [10, 90], healthy: [6, 94] } },
            { section: "tab-health", id: "r58c3bbeabb2f4ef79330d39c9b0b6ef7", label: "14. هل لديك مرض تنفسي مشخص (مثل الربو)؟", options: ["نعم", "لا"], weights: { smoker: [14, 86], balanced: [9, 91], healthy: [5, 95] } },
            { section: "tab-health", id: "r7cbe9441d8754bac987fe49cf1fdde89", label: "15. هل تستخدم حالياً أدوية تؤثر على الوزن أو الشهية؟", options: ["نعم", "لا"], weights: { smoker: [8, 92], balanced: [12, 88], healthy: [10, 90] } },

            // 3. النيكوتين والتدخين
            { section: "tab-nicotine", id: "rc5b3ca21c44c43acbd0339a2c7b95395", label: "16. حالة التدخين العامة", options: ["مدخن حالي", "مدخن سابق", "غير مدخن"], weights: { smoker: [88, 10, 2], balanced: [35, 15, 50], healthy: [0, 8, 92] } },
            { section: "tab-nicotine", id: "r929c33f1365f4db59d66ecb9b2088f77", label: "17. هل تستخدم أي من منتجات النيكوتين حالياً؟", options: ["نعم", "لا"], weights: { smoker: [96, 4], balanced: [40, 60], healthy: [0, 100] } },
            { section: "tab-nicotine", id: "r87150ac5fd0c4ad8afa7d47048cbb718", label: "18. نوع منتج النيكوتين الرئيسي الذي تستخدمه حالياً", options: ["السجائر التقليدية", "السجائر الإلكترونية (الفيب)", "الشيشة", "أكياس النيكوتين "], weights: { smoker: [35, 42, 16, 7], balanced: [30, 42, 20, 8], healthy: [25, 25, 25, 25] } },
            { section: "tab-nicotine", id: "r98f43ecbaff147889167566860f149ab", label: "19-26. تكرار استخدام المنتج", options: ["يومياً", "احيانا", "نادرا"], weights: { smoker: [68, 22, 10], balanced: [40, 35, 25], healthy: [5, 15, 80] } },
            { section: "tab-nicotine", id: "rfa7f543df5d34f2f9d8402cef51b8ae5", label: "20-27. الكمية اليومية المستهلكة", options: ["١-٥ سجائر / أكياس", "٦-١٠ سجائر / أكياس ", "١١-١٥ سيجارة / كيس", "اكثر من ١٥"], weights: { smoker: [25, 45, 20, 10], balanced: [45, 35, 15, 5], healthy: [70, 20, 8, 2] } },
            { section: "tab-nicotine", id: "rd9bbcc354a8f4fad86ffbf9c968e8cb4", label: "28. تركيز النيكوتين المستخدم غالباً", options: ["اقل من ٢ ملغم", "٢-٤ ملغم", "٥-٨ ملغم", "٩-١٢ ملغم", "١٣-٢٠ ملغم", "اكثر من ٢٠ ملغم"], weights: { smoker: [8, 20, 32, 22, 12, 6], balanced: [15, 25, 30, 18, 8, 4], healthy: [30, 35, 20, 10, 3, 2] } },

            // 4. النشاط والنوم
            { section: "tab-sleep-act", id: "rc13c64558dfc4ecdba67381d17536c85", label: "29. النشاطات البدنية الكثيفة في الأسبوع", options: ["لا أمارس الرياضة", "١-٢ مره في الأسبوع ", "٣-٤ مرات في الأسبوع", "٥-٧ مرات في الأسبوع"], weights: { smoker: [48, 32, 15, 5], balanced: [35, 35, 22, 8], healthy: [10, 25, 45, 20] } },
            { section: "tab-sleep-act", id: "r14a6dbc8b563410fb1cb35e447b7e358", label: "30. الوقت المستغرق في الأنشطة المكثفة", options: ["اقل من ٣٠ دقيقة", "٣٠ إلى ٦٠ دقيقة", "ساعة إلى ساعتين", "اكثر من ساعتين"], weights: { smoker: [35, 45, 16, 4], balanced: [25, 50, 20, 5], healthy: [10, 50, 35, 5] } },
            { section: "tab-sleep-act", id: "rbbee9bae96b54449ac2634e32f188d7a", label: "31. النشاطات البدنية المتوسطة الكثافة", options: ["لا أمارس الرياضة", "١-٢ مره في الأسبوع ", "٣-٤ مرات في الأسبوع", "٥-٧ مرات في الأسبوع"], weights: { smoker: [40, 36, 18, 6], balanced: [28, 38, 24, 10], healthy: [8, 22, 45, 25] } },
            { section: "tab-sleep-act", id: "r1e6cf7947f2344c7ba18a41de29f0290", label: "32. الوقت المستغرق في الأنشطة المتوسطة", options: ["اقل من ٣٠ دقيقة", "٣٠ إلى ٦٠ دقيقة", "ساعة إلى ساعتين", "اكثر من ساعتين"], weights: { smoker: [32, 48, 16, 4], balanced: [22, 53, 20, 5], healthy: [12, 50, 32, 6] } },
            { section: "tab-sleep-act", id: "rd78b2fe562004f2180bae99684d2f134", label: "33. الوقت المستغرق في المشي عادة", options: ["اقل من ٣٠ دقيقة", "٣٠ إلى ٦٠ دقيقة", "ساعة إلى ساعتين", "اكثر من ساعتين"], weights: { smoker: [36, 44, 16, 4], balanced: [26, 48, 20, 6], healthy: [15, 50, 28, 7] } },
            { section: "tab-sleep-act", id: "r9e24b8523d5a4495b235d5894ccfc9af", label: "34. كم متوسط عدد ساعات نومك؟", options: ["أقل من ٥ ساعات ", "٥-٧ ساعات", "أكثر من ٧ ساعات"], weights: { smoker: [32, 53, 15], balanced: [18, 62, 20], healthy: [8, 62, 30] } },
            { section: "tab-sleep-act", id: "rd6c8c768f0a548bba0c3d3be8c17006a", label: "35. جودة نومك بشكل عام", options: ["جيدة جدا", "جيدة نوعا ما", "سيئة نوعا ما", "سيئة جدا"], weights: { smoker: [15, 38, 34, 13], balanced: [26, 48, 20, 6], healthy: [45, 42, 11, 2] } },
            { section: "tab-sleep-act", id: "r6542a2b43ee64e38989528336f60d8a2", label: "36. الوقت المستغرق للنوم كل ليلة", options: ["١٥ دقيقة او اقل", "١٦-٣٠ دقيقة", "٣١-٦٠ دقيقة", "اكثر من ٦٠ دقيقة"], weights: { smoker: [25, 35, 26, 14], balanced: [38, 38, 18, 6], healthy: [52, 36, 10, 2] } },
            { section: "tab-sleep-act", id: "rd66ea66c2f8e42e0b3c5f0f578900be4", label: "37. الاستيقاظ منتصف الليل أو الصباح الباكر", options: ["لم يحدث ابدا", "اقل من مرة في الأسبوع", "مرة او مرتين في الأسبوع ", "ثلاث مرات او اكثر في الأسبوع"], weights: { smoker: [12, 24, 38, 26], balanced: [25, 34, 28, 13], healthy: [42, 36, 16, 6] } },
            { section: "tab-sleep-act", id: "r69b0ade4d0e74796bc023f7a2f6062ad", label: "38. النعاس أو نقص الطاقة بالنهار", options: ["لم يحدث خلال الشهر الماضي", "أقل من مرة في الأسبوع", "مرة أو مرتين في الأسبوع", "ثلاث مرات أو أكثر في الأسبوع"], weights: { smoker: [10, 22, 40, 28], balanced: [20, 32, 33, 15], healthy: [38, 38, 18, 6] } },

            // 5. الشهية ومقاييس الأكل
            { section: "tab-appetite", id: "r1a5592a6f3ce4a7ab529373f0b67391a", isMatrix: true, matrixKey: "778f8880-03ce-4e19-89c3-b9c6aefc6500", label: "39. هل تعتقد أن التدخين أو الفيب يؤثر على شهيتك؟", options: ["يقلل الشهية", "لا يسبب اي تغيير", "يزيد الشهية", "غير متأكد"], weights: { smoker: [62, 22, 6, 10], balanced: [52, 28, 7, 13], healthy: [45, 30, 5, 20] } },
            
            // بنود المصفوفة الـ 13
            { section: "tab-appetite", id: "rbd92822cc5434bc9b7c27730395a2fe2", isMatrix: true, matrixKey: "c37feec2-3e87-45b4-be5d-f21d837da0f3", label: "40.1 عندما أبدأ بتناول الطعام أجد صعوبة في التوقف", options: EATING_SCALE_OPTIONS, weights: { smoker: [14, 26, 42, 18], balanced: [10, 22, 46, 22], healthy: [5, 15, 45, 35] } },
            { section: "tab-appetite", id: "r8c05c3f922b74896b7ac7b37459c692b", isMatrix: true, matrixKey: "c37feec2-3e87-45b4-be5d-f21d837da0f3", label: "40.2 معدتي تبدو بلا قاع من شدة الجوع", options: EATING_SCALE_OPTIONS, weights: { smoker: [10, 20, 44, 26], balanced: [8, 18, 46, 28], healthy: [3, 10, 42, 45] } },
            { section: "tab-appetite", id: "rf0ab48eea584423a9adc9ab5676a504e", isMatrix: true, matrixKey: "c37feec2-3e87-45b4-be5d-f21d837da0f3", label: "40.3 أشعر دائماً بالجوع لدرجة الأكل في أي وقت", options: EATING_SCALE_OPTIONS, weights: { smoker: [12, 24, 40, 24], balanced: [9, 20, 43, 28], healthy: [4, 12, 38, 46] } },
            { section: "tab-appetite", id: "r9eab681b3fe04b36bb01331695e77805", isMatrix: true, matrixKey: "c37feec2-3e87-45b4-be5d-f21d837da0f3", label: "40.4 صعوبة الامتناع عن أكل شريحة لحم مشوية مغرية", options: EATING_SCALE_OPTIONS, weights: { smoker: [18, 28, 36, 18], balanced: [14, 28, 38, 20], healthy: [8, 20, 42, 30] } },
            { section: "tab-appetite", id: "rdc8c8c889eb84bbeb1c31fbee931c499", isMatrix: true, matrixKey: "c37feec2-3e87-45b4-be5d-f21d837da0f3", label: "40.5 أتعمد تناول كميات صغيرة للتحكم في وزني", options: EATING_SCALE_OPTIONS, weights: { smoker: [15, 25, 40, 20], balanced: [22, 32, 32, 14], healthy: [32, 38, 22, 8] } },
            { section: "tab-appetite", id: "rd5f4c5c3221e4588b18923faa7019f38", isMatrix: true, matrixKey: "c37feec2-3e87-45b4-be5d-f21d837da0f3", label: "40.6 عندما أشعر بالقلق، أجد نفسي أتناول الطعام", options: EATING_SCALE_OPTIONS, weights: { smoker: [22, 30, 32, 16], balanced: [18, 26, 36, 20], healthy: [8, 18, 38, 36] } },
            { section: "tab-appetite", id: "r7ff13811ef744b66bd7f0e2cf3b8dd6a", isMatrix: true, matrixKey: "c37feec2-3e87-45b4-be5d-f21d837da0f3", label: "40.7 وجودي مع شخص يأكل كثيراً يجعلني جائعاً", options: EATING_SCALE_OPTIONS, weights: { smoker: [14, 30, 38, 18], balanced: [12, 28, 42, 18], healthy: [6, 20, 44, 30] } },
            { section: "tab-appetite", id: "rd4aae7070cfd4c56b4864eb11885e08c", isMatrix: true, matrixKey: "c37feec2-3e87-45b4-be5d-f21d837da0f3", label: "40.8 رؤية طعام فاخر تجعلني أرغب في الأكل فوراً", options: EATING_SCALE_OPTIONS, weights: { smoker: [16, 28, 36, 20], balanced: [12, 26, 42, 20], healthy: [6, 18, 44, 32] } },
            { section: "tab-appetite", id: "r321bed2367084e4e90791fd87d63ac34", isMatrix: true, matrixKey: "c37feec2-3e87-45b4-be5d-f21d837da0f3", label: "40.9 دائماً جائع ويصعب التوقف قبل إنهاء كامل الصحن", options: EATING_SCALE_OPTIONS, weights: { smoker: [16, 26, 38, 20], balanced: [12, 24, 42, 22], healthy: [5, 15, 40, 40] } },
            { section: "tab-appetite", id: "r28b2cc01f44340d8ae6628bff98157f3", isMatrix: true, matrixKey: "c37feec2-3e87-45b4-be5d-f21d837da0f3", label: "40.10 عندما أشعر بالوحدة، أواسي نفسي بالأكل", options: EATING_SCALE_OPTIONS, weights: { smoker: [20, 28, 32, 20], balanced: [15, 25, 35, 25], healthy: [6, 14, 35, 45] } },
            { section: "tab-appetite", id: "rd13f05520b274f0eb28d11e4d9c91217", isMatrix: true, matrixKey: "c37feec2-3e87-45b4-be5d-f21d837da0f3", label: "40.11 أتحكم عمداً في كمية الطعام لتجنب زيادة الوزن", options: EATING_SCALE_OPTIONS, weights: { smoker: [16, 26, 38, 20], balanced: [24, 34, 30, 12], healthy: [35, 40, 18, 7] } },
            { section: "tab-appetite", id: "rdeb4728c8dd34fb5837bd214fc88315a", isMatrix: true, matrixKey: "c37feec2-3e87-45b4-be5d-f21d837da0f3", label: "40.12 لا آكل بعض الأطعمة لأنها تجعلني سميناً", options: EATING_SCALE_OPTIONS, weights: { smoker: [18, 26, 34, 22], balanced: [25, 33, 28, 14], healthy: [36, 38, 18, 8] } },
            { section: "tab-appetite", id: "r0a686129643b488d91bf00a0b5b2b24c", isMatrix: true, matrixKey: "c37feec2-3e87-45b4-be5d-f21d837da0f3", label: "40.13 عندما أشعر بالحزن أفرط في الأكل", options: EATING_SCALE_OPTIONS, weights: { smoker: [22, 28, 30, 20], balanced: [16, 25, 34, 25], healthy: [7, 15, 33, 45] } },

            { section: "tab-appetite", id: "r2393b1085172446d891c99bdca3491fd", label: "41. احتمال أن تأكل أقل مما تريد عن وعي؟", options: ["من غير المحتمل", "من المحتمل قليلا", "محتمل باعتدال", "من المحتمل جدا"], weights: { smoker: [25, 35, 28, 12], balanced: [18, 32, 34, 16], healthy: [8, 22, 42, 28] } },
            { section: "tab-appetite", id: "r0960b62ee63d403395ed15da0f4887bd", label: "42. كم مرة تتجنب شراء الأطعمة المغرية والاحتفاظ بها؟", options: ["نادرا جدا", "نادرا ", "عادة", "دائما تقريبا"], weights: { smoker: [32, 38, 22, 8], balanced: [22, 34, 32, 12], healthy: [10, 22, 42, 26] } },
            { section: "tab-appetite", id: "r5956b9c6bcfe47a2ae2ee5279e3aeb90", isMatrix: true, matrixKey: "d65b0472-066c-4a05-88a5-d6b9699fefd3", label: "43. كم مرة تشعر بالجوع؟", options: ["فقط أوقات الوجبات", "أحياناً بين الوجبات", "غالباً بين الوجبات", "معظم الوقت"], weights: { smoker: [22, 45, 24, 9], balanced: [30, 48, 17, 5], healthy: [45, 42, 11, 2] } },
            { section: "tab-appetite", id: "r38137ca693d043a2bac7daf7c77e57a3", isMatrix: true, matrixKey: "d65b0472-066c-4a05-88a5-d6b9699fefd3", label: "44. هل تستمر في الأكل رغم عدم شعورك بالجوع؟", options: ["مرة واحدة على الأقل اسبوعياً", "أحياناً", "نادراً", "أبداً"], weights: { smoker: [28, 38, 24, 10], balanced: [20, 40, 28, 12], healthy: [8, 25, 42, 25] } },
            { section: "tab-appetite", id: "r6d869d8015bc4577b044885ac965cefc", label: "45. مقياس التحكم بتناول الطعام (1 لا يوجد تحكم، 8 تحكم كامل)", options: ["١", "٢", "٣", "٤", "٥", "٦", "٧", "٨"], weights: { smoker: [4, 8, 15, 22, 24, 15, 8, 4], balanced: [2, 5, 12, 20, 26, 20, 10, 5], healthy: [1, 2, 6, 12, 22, 26, 20, 11] } }
        ];

        let activeTab = "tab-demographics";

        function switchTab(tabId) {
            activeTab = tabId;
            document.querySelectorAll(".tab-btn").forEach(b => {
                b.classList.remove("bg-teal-600/30", "border-teal-500", "text-teal-300");
                b.classList.add("bg-slate-900", "border-slate-800", "text-slate-400");
            });
            const btn = document.getElementById(`btn-${tabId}`);
            if (btn) {
                btn.classList.add("bg-teal-600/30", "border-teal-500", "text-teal-300");
                btn.classList.remove("bg-slate-900", "border-slate-800", "text-slate-400");
            }
            renderQuestions();
        }

        // رسم كروت الأسئلة بجميع شرائحها
        function renderQuestions() {
            const container = document.getElementById("questionsContainer");
            container.innerHTML = "";
            const list = surveyQuestions.filter(q => q.section === activeTab);

            list.forEach(q => {
                const card = document.createElement("div");
                card.className = "bg-slate-900 p-4 rounded-3xl border border-slate-800 shadow-xl space-y-3";

                const header = document.createElement("div");
                header.className = "flex justify-between items-start gap-2 border-b border-slate-800 pb-2";

                const title = document.createElement("h4");
                title.className = "text-xs font-bold text-slate-200 leading-snug";
                title.innerText = q.label;

                const idBadge = document.createElement("span");
                idBadge.className = "text-[9px] font-mono px-2 py-0.5 rounded bg-slate-800 text-teal-400 font-bold";
                idBadge.innerText = q.id.slice(0, 8);

                header.appendChild(title);
                header.appendChild(idBadge);
                card.appendChild(header);

                q.options.forEach((opt, idx) => {
                    const row = document.createElement("div");
                    row.className = "space-y-1";

                    const meta = document.createElement("div");
                    meta.className = "flex justify-between text-[11px] text-slate-400";

                    const optName = document.createElement("span");
                    optName.className = "truncate pl-2 font-medium";
                    optName.innerText = opt;

                    const pctText = document.createElement("span");
                    pctText.id = `${q.id}_pct_${idx}`;
                    pctText.className = "font-bold text-teal-400 font-mono text-xs";
                    const currentVal = q.currentWeights ? q.currentWeights[idx] : q.weights.balanced[idx];
                    pctText.innerText = `${currentVal}%`;

                    meta.appendChild(optName);
                    meta.appendChild(pctText);

                    const slider = document.createElement("input");
                    slider.type = "range";
                    slider.min = "0";
                    slider.max = "100";
                    slider.value = currentVal;
                    slider.className = "w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer";
                    slider.oninput = (e) => {
                        pctText.innerText = `${e.target.value}%`;
                        if (!q.currentWeights) q.currentWeights = [...q.weights.balanced];
                        q.currentWeights[idx] = parseFloat(e.target.value);
                    };

                    row.appendChild(meta);
                    row.appendChild(slider);
                    card.appendChild(row);
                });

                container.appendChild(card);
            });
        }

        function applyPreset(name) {
            surveyQuestions.forEach(q => {
                if (q.weights && q.weights[name]) {
                    q.currentWeights = [...q.weights[name]];
                }
            });
            renderQuestions();
            log(`Applied preset: ${name.toUpperCase()}`, "text-teal-300 font-bold");
        }

        function selectWeightedChoice(options, weights) {
            const sum = weights.reduce((acc, v) => acc + v, 0);
            if (sum === 0) return { opt: options[0], idx: 0 };
            let rand = Math.random() * sum;
            for (let i = 0; i < options.length; i++) {
                if (rand < weights[i]) return { opt: options[i], idx: i };
                rand -= weights[i];
            }
            return { opt: options[0], idx: 0 };
        }

        function log(msg, color='text-teal-400') {
            const b = document.getElementById('logBox');
            const p = document.createElement('p');
            p.className = color;
            p.innerText = `[${new Date().toLocaleTimeString()}] ${msg}`;
            b.appendChild(p);
            b.scrollTop = b.scrollHeight;
        }

        async function runSubmissions() {
            const count = parseInt(document.getElementById("subCount").value) || 10;
            const delay = parseFloat(document.getElementById("subDelay").value) || 0.5;
            const enforceConsent = document.getElementById("enforceConsent").checked;

            const btn = document.getElementById("startBtn");
            const bar = document.getElementById("progressBar");
            const pTxt = document.getElementById("progressTxt");
            const pct = document.getElementById("percentTxt");

            btn.disabled = true;
            btn.classList.add("opacity-50");
            log(`Starting dispatch of ${count} responses with your custom sliders...`, "text-cyan-400 font-bold");

            let successful = 0;

            for (let i = 1; i <= count; i++) {
                pTxt.innerText = `Submitting: ${i} / ${count}`;

                let answersList = [];
                let respondentGender = "ذكر";
                let primaryProduct = "السجائر التقليدية";

                surveyQuestions.forEach(q => {
                    const weights = q.options.map((_, oIdx) => q.currentWeights ? q.currentWeights[oIdx] : q.weights.balanced[oIdx]);
                    const { opt: chosen, idx: chosenIdx } = selectWeightedChoice(q.options, weights);

                    if (q.id === "r41af6ec4edc64e478058417d69a06d68" && enforceConsent) {
                        answersList.push({ questionId: q.id, answer1: "أوافق على المشاركة " });
                        return;
                    }

                    if (q.id === "r09bce8ea15a34987ae59742bee682c3a") respondentGender = chosen;
                    if (q.id === "r87150ac5fd0c4ad8afa7d47048cbb718") primaryProduct = chosen;

                    if (q.isMatrix) {
                        answersList.push({
                            questionId: q.id,
                            answer1: {
                                id: chosenIdx + 1,
                                key: q.matrixKey
                            }
                        });
                    } else {
                        answersList.push({
                            questionId: q.id,
                            answer1: chosen
                        });
                    }
                });

                try {
                    const res = await fetch('/api/submit', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ answers: answersList })
                    });
                    const data = await res.json();
                    if(data.status === 201 || data.status === 200) {
                        successful++;
                        log(`[✓] #${i} [${respondentGender} | ${primaryProduct.split()[0]}] Recorded (201 OK)`);
                    } else {
                        log(`[!] #${i} Error: ${data.msg}`, 'text-rose-400');
                    }
                } catch(e) {
                    log(`[!] Connection Error: ${e.message}`, 'text-rose-400');
                }

                const currentPct = Math.round((i / count) * 100);
                bar.style.width = `${currentPct}%`;
                pct.innerText = `${currentPct}%`;

                if (i < count) await new Promise(r => setTimeout(r, delay * 1000));
            }

            btn.disabled = false;
            btn.classList.remove("opacity-50");
            log(`Done! Total ${successful} responses permanently saved.`, "text-amber-300 font-bold");
        }

        window.addEventListener("DOMContentLoaded", () => {
            applyPreset("balanced");
        });
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
    answers = data.get('answers', [])
    
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
        return jsonify({"status": res.status_code, "msg": res.text if res.status_code not in [200, 201] else "OK"})
    except Exception as e:
        return jsonify({"status": 500, "msg": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
