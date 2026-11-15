import requests
import json
import uuid
import time
import random
from datetime import datetime, timedelta

# الرابط والتوكن المستخرجة من حسابك
URL = "https://forms.guest.usercontent.microsoft/formapi/api/4fef011a-ec15-4171-b293-1b10bc52fda1/users/f4a071e2-1d10-4211-b1d1-20d4fc6077c8/forms('GgHvTxXscUGykxsQvFL9oeJxoPQQHRFCsdEg1Pxgd8hUMzFCN0hQTVRQNFU0WEtPME4yV1A1NVNZUS4u')/responses"
TOKEN = "obaT70YNbCwA8dGTULQREx9ulu2tPmNfx5OozWcaqKH-ZA57ImT-alP29FfDFSkT8qv82f0wob47qoj2_3BTMAQ7o5_1WvjvAeTFgUwymwHnYE3vwwghavvY8ENadG8Ga7U0N4uHWHPgsbxFbrAUTw2"

HEADERS = {
    "__requestverificationtoken": TOKEN,
    "accept": "application/json",
    "content-type": "application/json",
    "odata-maxverion": "4.0",
    "odata-version": "4.0",
    "x-ms-form-request-ring": "business",
    "x-ms-form-request-source": "ms-formweb"
}

def generate_answers():
    is_smoker = random.choice([True, False])
    gender = random.choice(["ذكر", "أنثى"])
    
    answers = [
        {"questionId": "r41af6ec4edc64e478058417d69a06d68", "answer1": "أوافق على المشاركة "},
        {"questionId": "r09bce8ea15a34987ae59742bee682c3a", "answer1": gender},
        {"questionId": "r1e31048731aa49d69a5bc40cc91f114b", "answer1": random.choice(["١٨-٢٤ سنة", "٢٥-٣٤ سنة", "٣٥-٤٤ سنة"])},
        {"questionId": "r893a149db2c24d81b8f9e9108eca4b33", "answer1": "سعودي"},
        {"questionId": "r05790a41766f4f59ba81ca2ed7d8eda2", "answer1": random.choice(["١٥٦ سم - ١٦٥ سم", "١٦٦ سم - ١٧٥ سم", "١٧٦ سم - ١٨٥ سم"])},
        {"questionId": "rc66361b19e9b4f87a6bc2e1e6c8fc102", "answer1": random.choice(["٦١ كجم - ٦٥ كجم", "٦٦ كجم - ٧٠ كجم", "٧١ كجم - ٧٥ كجم", "٧٦ كجم - ٨٠ كجم", "٨١ كجم - ٨٥ كجم"])},
        {"questionId": "rad1e4a623ca843098aa38329ab4ca826", "answer1": random.choice(["أعزب / عزباء ", "متزوج / متزوجة"])},
        {"questionId": "r808287efa4bb49a597292533f9169e1e", "answer1": random.choice(["بكالوريوس", "دبلوم", "دراسات عليا"])},
        {"questionId": "rb6294016a8674110adafb959ec421446", "answer1": random.choice(["من ٣٠٠٠ إلى ٧٠٠٠", "من ٧٠٠١ إلى ١٢٠٠٠", "من ١٢٠٠١ إلى ٢٠٠٠٠"])},
        {"questionId": "ra5fd4c1c93a24c6797b98cdaacce033d", "answer1": random.choice(["الوسطى", "الغربية", "الشرقية", "الجنوبية"])},
        {"questionId": "r3fb69a6c961a4d39b727df798493e34c", "answer1": "لا"},
        {"questionId": "r0f33b1d94e974c7daff13dca59a872d8", "answer1": "لا"},
        {"questionId": "r58c3bbeabb2f4ef79330d39c9b0b6ef7", "answer1": "لا"},
        {"questionId": "r7cbe9441d8754bac987fe49cf1fdde89", "answer1": "لا"},
        {"questionId": "rc5b3ca21c44c43acbd0339a2c7b95395", "answer1": "مدخن حالي" if is_smoker else "غير مدخن"},
        {"questionId": "r929c33f1365f4db59d66ecb9b2088f77", "answer1": "نعم" if is_smoker else "لا"},
        {"questionId": "r87150ac5fd0c4ad8afa7d47048cbb718", "answer1": random.choice(["السجائر الإلكترونية (الفيب)", "السجائر التقليدية", "الشيشة", "أكياس النيكوتين "])},
        {"questionId": "r98f43ecbaff147889167566860f149ab", "answer1": random.choice(["يومياً", "احيانا", "نادرا"])},
        {"questionId": "rfa7f543df5d34f2f9d8402cef51b8ae5", "answer1": random.choice(["١-٥ أكياس", "٦-١٠ أكياس ", "١١-١٥ كيساً"])},
        {"questionId": "rd9bbcc354a8f4fad86ffbf9c968e8cb4", "answer1": random.choice(["٥-٨ ملغم", "٩-١٢ ملغم", "١٣-٢٠ ملغم"])},
        {"questionId": "rc13c64558dfc4ecdba67381d17536c85", "answer1": random.choice(["١-٢ مره في الأسبوع ", "٣-٤ مرات في الأسبوع"])},
        {"questionId": "r14a6dbc8b563410fb1cb35e447b7e358", "answer1": "٣٠ إلى ٦٠ دقيقة"},
        {"questionId": "rbbee9bae96b54449ac2634e32f188d7a", "answer1": random.choice(["١-٢ مره في الأسبوع ", "٣-٤ مرات في الأسبوع"])},
        {"questionId": "r1e6cf7947f2344c7ba18a41de29f0290", "answer1": "٣٠ إلى ٦٠ دقيقة"},
        {"questionId": "rd78b2fe562004f2180bae99684d2f134", "answer1": "٣٠ إلى ٦٠ دقيقة"},
        {"questionId": "r9e24b8523d5a4495b235d5894ccfc9af", "answer1": random.choice(["٥-٧ ساعات", "أكثر من ٧ ساعات"])},
        {"questionId": "rd6c8c768f0a548bba0c3d3be8c17006a", "answer1": random.choice(["جيدة جدا", "جيدة نوعا ما"])},
        {"questionId": "r6542a2b43ee64e38989528336f60d8a2", "answer1": random.choice(["١٥ دقيقة او اقل", "١٦-٣٠ دقيقة"])},
        {"questionId": "rd66ea66c2f8e42e0b3c5f0f578900be4", "answer1": random.choice(["لم يحدث ابدا", "اقل من مرة في الأسبوع", "مرة او مرتين في الأسبوع "])},
        {"questionId": "r69b0ade4d0e74796bc023f7a2f6062ad", "answer1": random.choice(["لم يحدث خلال الشهر الماضي", "أقل من مرة في الأسبوع"])},
        {"questionId": "r2393b1085172446d891c99bdca3491fd", "answer1": random.choice(["محتمل باعتدال", "من المحتمل جدا", "من المحتمل قليلا"])},
        {"questionId": "r0960b62ee63d403395ed15da0f4887bd", "answer1": random.choice(["عادة", "دائما تقريبا", "نادرا "])},
        {"questionId": "r6d869d8015bc4577b044885ac965cefc", "answer1": str(random.randint(4, 7))},
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
        answers.append({"questionId": qid, "answer1": {"id": random.randint(2, 4), "key": "c37feec2-3e87-45b4-be5d-f21d837da0f3"}})

    return answers

def send_responses(count=10):
    print(f"🚀 بدء إرسال {count} استجابة حقيقية إلى Microsoft Forms...")
    success = 0
    for i in range(count):
        now = datetime.utcnow()
        start = now - timedelta(minutes=random.randint(2, 5))
        payload = {
            "startDate": start.isoformat() + "Z",
            "submitDate": now.isoformat() + "Z",
            "answers": json.dumps(generate_answers(), ensure_ascii=False)
        }
        
        headers = dict(HEADERS)
        headers["x-correlationid"] = str(uuid.uuid4())
        headers["x-usersessionid"] = str(uuid.uuid4())

        try:
            res = requests.post(URL, headers=headers, json=payload, timeout=10)
            if res.status_code in [200, 201]:
                success += 1
                print(f"[{i+1}/{count}] ✅ تم تسجيل الرد بنجاح في مايكروسوفت فورمز! (كود {res.status_code})")
            else:
                print(f"[{i+1}/{count}] ❌ رد السيرفر: {res.status_code} - {res.text}")
        except Exception as e:
            print(f"[{i+1}/{count}] ⚠️ خطأ اتصال: {e}")

        time.sleep(0.5)

    print(f"\n🎉 انتهى! تم إرسال {success} استجابة كاملة، وتستطيع الآن تحديث صفحة نتائجك في مايكروسوفت فورمز لتراها مباشرة.")

if __name__ == "__main__":
    count = int(input("كم عدد الاستجابات التي تريد إرسالها؟ (مثلاً 20): ") or 10)
    send_responses(count)