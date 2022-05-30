import cv2
import pickle
#ابعاد مربع التحقق من الموقف
width, height = 107, 48
#اضافة بيانات ملف يحتوي على احداثات الاماكن الفارغة الى مصفوفة
try:
    with open('CarParkPos', 'rb') as f:
        posList = pickle.load(f)#اضافة محتوى الملف الى المصفوفة
except:
    posList = []

#زر الفارة الايسر يرسم مربع التحقق و الزر الايمن يقوم بحذفه
def mouseClick(events, x, y, flags, params):
    if events == cv2.EVENT_LBUTTONDOWN:
        posList.append((x, y))
    if events == cv2.EVENT_RBUTTONDOWN:#التحقق من ان الزر تم ضغطه
        for i, pos in enumerate(posList):
            x1, y1 = pos
            if x1 < x < x1 + width and y1 < y < y1 + height:
                posList.pop(i)
#في كل مرة يتم حذف او اضافة مربع تحقق يتم وضع محتوى مصفوفة الاحداثيات في الملف
    with open('CarParkPos', 'wb') as f:
        pickle.dump(posList, f)

#   يرسم مربع التحقق على صورة من الفيديو عند كل ضغطة زر
while True:
    img = cv2.imread('carParkImg.png')
    for pos in posList:
        cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), (255, 0, 255), 2)

    cv2.imshow("Image", img)
    cv2.setMouseCallback("Image", mouseClick)
    cv2.waitKey(1)