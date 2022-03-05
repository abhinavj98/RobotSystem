import cv2
import atexit
import time
class perception():
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        time.sleep(1)
        self.img = None
        # Check if the webcam is opened correctly
        if not self.cap.isOpened():
            raise IOError("Cannot open webcam")
        atexit.register(self.__cleanup)

    @staticmethod
    def thresh(img):
        # apply binary thresholding
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(img_gray, 180, 255, cv2.THRESH_BINARY)
        return thresh

    @staticmethod
    def find_contours(img):
        #Grayscale image
        thresh_img = cam.thresh(img)
        #detect the contours on the binary image using cv2.CHAIN_APPROX_NONE
        contours, hierarchy = cv2.findContours(thresh_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[-2:]
        # draw contours on the original image
        image_copy = img.copy()
        cv2.drawContours(image=image_copy, contours=contours, contourIdx=-1, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
        return image_copy
               

    def read(self):
        self.img = self.cap.read()
        return self.img

    def __cleanup(self):
        self.cap.release()

if __name__ == "__main__":

    cam = perception()
    while True:
        ret, frame = cam.read()
        
        # print(thresh_img.shape)
        frame = cam.find_contours(frame)

        frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
        cv2.imshow('Input', frame)
        c = cv2.waitKey(1)
        if c & 0xFF == 27:
            break

    cv2.destroyAllWindows()
