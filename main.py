import cv2
import pickle
import cvzone
import numpy as np
import pyrebase
#تهيثة قاعدة البيانات
firebaseConfig = {
    'apiKey': "AIzaSyC1_097qAqEfRNb_FWebTr4J28IqECtczo",
    'authDomain': "praking-e62a6.firebaseapp.com",
    'databaseURL': "https://praking-e62a6-default-rtdb.europe-west1.firebasedatabase.app/",
    'projectId': "praking-e62a6",
    'storageBucket': "praking-e62a6.appspot.com",
    'messagingSenderId': "151173470046",
    'appId': "1:151173470046:web:adc92bf4f4a808877821cf",
    'measurementId': "G-JJE5BEYWWS"}
#الربط مع قاعدة البيانات firebase
firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()
#اضافة الفيديو
cap = cv2.VideoCapture('carPark.mp4')
with open('CarParkPos', 'rb') as f:
    posList = pickle.load(f)
width, height = 107, 48

def checkParkingSpace(imgPro,sleep):
    spaceCounter = 0
    spaceValue=[]
    count_list = []
    for index, pos in enumerate(posList):
        try:
            isEmpty = False
            x, y = posList[index]
            imgCrop = imgPro[y:y + height, x:x + width]  #قص صورة كل موقف
           #الحصول على عدد البيكسلات للصورة بعد القص
            count = cv2.countNonZero(imgCrop)  # get the count of pixels
           #من خلال عدد البكسلات نحدد اذا كان الموقف فارغ او لا وثم رسم مربع التحقق باللون المناسب
            if count < 900:
                color = (0, 255, 0)
                thickness = 5
                spaceCounter += 1
                isEmpty = True
            else:
                color = (0, 0, 255)
                thickness = 2
            count_list.insert(index,isEmpty)
            cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), color, thickness)
            # اظهار عدد البكسلات لمربع التحقق
            cvzone.putTextRect(img, str(count), (x, y + height - 3), scale=1,
                               thickness=2, offset=0, colorR=color)
        except IndexError:
            continue
  #المقارنة بين محتوى قاعدة البيانات ومحتوى الفيديو مع تاخير بسبب بعد السيرفر
    park_list = []
    if sleep % 60 == 0:
        parks = db.child('parking').order_by_child('isempty').get()
        for park in parks.each():
            park_list.append(park.val()['isempty'])

    for k in range(len(count_list)):
        try:
            if count_list[k] != park_list[k]:
                # عند وجود تغيير بتم استبدال حالة الموقف بالحالة الجديدة
                db.child('parking').child(k).update({'isempty': count_list[k]})
                db.child('count').update({'empty': spaceCounter})
        except IndexError:
            continue
#اظهار عدد المواقف الفارغة
    cvzone.putTextRect(img, f'Free: {spaceCounter}/{len(posList)}', (100, 50), scale=3,
                       thickness=5, offset=20, colorR=(0, 200, 0))  # show the count of SPACES when there is no car
sleep = 0
while True:
    sleep += 1
    #اعادة قيمة الفريم الى الصفر عند الوصول لنهاية الفيديو لتكرار الفيديو
    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        #الحصول على فريمات الفيديو
    success, img = cap.read()
    #تحويل الصورة الى اللون الرمادي
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #تنعيم الصورة
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
    #تعتيب متكيف للصورة
    imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY_INV, 25, 16)
    #ازلة النقاط البضاء لتقليل الضجيج
    imgMedian = cv2.medianBlur(imgThreshold, 5)
    #اعادة مصفوفة مؤشرة من المرتبة الثالثة
    kernel = np.ones((3, 3), np.uint8)
    #زيادة حجم البكسلات
    imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)
    checkParkingSpace(imgDilate,sleep)
    cv2.imshow("Image", img)
    #اضافة تاخير للفيديو
    cv2.waitKey(35)
