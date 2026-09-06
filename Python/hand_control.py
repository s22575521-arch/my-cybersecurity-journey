import cv2
import mediapipe as mp
import pyautogui
import time
import os
import urllib.request


# ==========================================
# تحميل نموذج MediaPipe تلقائيًا
# ==========================================

MODEL_URL = (
    "https://storage.googleapis.com/"
    "mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)

MODEL_PATH = "hand_landmarker.task"

if not os.path.exists(MODEL_PATH):
    print("جاري تحميل نموذج اليد...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    print("تم تحميل النموذج.")


# ==========================================
# إعداد MediaPipe الحديث
# ==========================================

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path=MODEL_PATH
    ),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=2,
    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.7,
    min_tracking_confidence=0.7
)

landmarker = HandLandmarker.create_from_options(options)


# ==========================================
# الكاميرا
# ==========================================

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("لم يتم العثور على الكاميرا.")
    exit()


# ==========================================
# متغيرات
# ==========================================

last_action_time = 0
cooldown = 1.5

timestamp_ms = 0


# ==========================================
# معرفة اليد المفتوحة
# ==========================================

def is_open_hand(hand_landmarks):

    # أطراف الأصابع:
    # السبابة 8
    # الوسطى 12
    # البنصر 16
    # الخنصر 20

    fingertips = [8, 12, 16, 20]

    open_fingers = 0

    for tip in fingertips:

        # مفصل الإصبع الأوسط تقريبًا
        pip = tip - 2

        if hand_landmarks[tip].y < hand_landmarks[pip].y:
            open_fingers += 1

    return open_fingers >= 4


# ==========================================
# رسم النقاط والخطوط
# ==========================================

def draw_hand(frame, landmarks):

    h, w, _ = frame.shape

    connections = [
        (0, 1), (1, 2), (2, 3), (3, 4),
        (0, 5), (5, 6), (6, 7), (7, 8),
        (5, 9), (9, 10), (10, 11), (11, 12),
        (9, 13), (13, 14), (14, 15), (15, 16),
        (13, 17), (17, 18), (18, 19), (19, 20),
        (0, 17)
    ]

    # الخطوط
    for start, end in connections:

        x1 = int(landmarks[start].x * w)
        y1 = int(landmarks[start].y * h)

        x2 = int(landmarks[end].x * w)
        y2 = int(landmarks[end].y * h)

        cv2.line(
            frame,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )

    # النقاط
    for landmark in landmarks:

        x = int(landmark.x * w)
        y = int(landmark.y * h)

        cv2.circle(
            frame,
            (x, y),
            5,
            (0, 0, 255),
            -1
        )


# ==========================================
# الحلقة الرئيسية
# ==========================================

while True:

    ret, frame = cap.read()

    if not ret:
        print("تعذر قراءة الكاميرا.")
        break

    # قلب الصورة مثل المرآة
    frame = cv2.flip(frame, 1)

    # OpenCV يستخدم BGR
    # MediaPipe يحتاج RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # إنشاء صورة MediaPipe
    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb
    )

    timestamp_ms += 33

    # اكتشاف اليد
    result = landmarker.detect_for_video(
        mp_image,
        timestamp_ms
    )

    hands_found = []

    if result.hand_landmarks:

        for i, hand_landmarks in enumerate(
            result.hand_landmarks
        ):

            # رسم اليد
            draw_hand(frame, hand_landmarks)

            # هل اليد مفتوحة؟
            if is_open_hand(hand_landmarks):

                handedness = "Unknown"

                if i < len(result.handedness):

                    handedness = (
                        result.handedness[i][0].category_name
                    )

                hands_found.append(handedness)


    # ======================================
    # تنفيذ الأوامر
    # ======================================

    current_time = time.time()

    if current_time - last_action_time >= cooldown:

        # اليدان مفتوحتان
        if len(hands_found) >= 2:

            print("اليدان -> التالي")

            pyautogui.press("right")

            last_action_time = current_time

        # اليد اليمنى مفتوحة
        elif "Right" in hands_found:

            print("اليد اليمنى -> تشغيل")

            pyautogui.press("space")

            last_action_time = current_time

        # اليد اليسرى مفتوحة
        elif "Left" in hands_found:

            print("اليد اليسرى -> إيقاف")

            pyautogui.press("space")

            last_action_time = current_time


    # ======================================
    # عرض المعلومات
    # ======================================

    cv2.putText(
        frame,
        "ESC = Exit",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )

    cv2.imshow(
        "Hand Gesture Control",
        frame
    )


    # ESC للخروج
    if cv2.waitKey(1) & 0xFF == 27:
        break


# ==========================================
# إغلاق البرنامج
# ==========================================

cap.release()
cv2.destroyAllWindows()
landmarker.close()
