import cv2 as cv

img_color = cv.imread('imgs/Screenshot_20220617-191333.png', cv.IMREAD_COLOR)

height, width = img_color.shape[:2]
center_x, center_y = int(width*0.5), int(height * 0.5)

#이미지 중심에서 일정 거리를 ROI영역으로 지정한다.
#copy메소드를 사용하면 원본 이미지 수정 없이 ROI영역을 다룰 수 있다.
img_roi = img_color[center_y - 100:center_y + 100, center_x -100:center_x + 100].copy()

#ROI영역을 그레이 스케일로 변환 후, 케니 에지를 구한다.
img_gray = cv.cvtColor(img_roi, cv.COLOR_BGR2GRAY)
img_edge = cv.Canny(img_gray, 100, 300)

#원본 컬러 영상에 다시 ROI이미지를 복사(합성)하기 위해 컬러영상으로 채널을 바꿔준다.
img_edge = cv.cvtColor(img_edge, cv.COLOR_GRAY2BGR)

#원본 컬러 영상에 다시 ROI를 복사한다.
img_color[center_y - 100:center_y + 100, center_x - 100:center_x + 100] = img_edge

cv.imshow('color', img_color)
cv.imshow('ROI', img_roi)
cv.waitKey(0)

cv.destroyAllWindows()