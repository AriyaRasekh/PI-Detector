import numpy as np
import cv2
import math
# Create a black image
out_raw = np.zeros((512,512,3), np.uint8)

# Write some Text
x,y = 200, 300
angle = 30
font                   = cv2.FONT_HERSHEY_SIMPLEX
bottomLeftCornerOfText = (x,y)
fontScale              = 1
fontColor              = (255,255,255)
thickness              = 1
lineType               = 2

cv2.putText(out_raw,'Hello World!',
    bottomLeftCornerOfText,
    font,
    fontScale,
    fontColor,
    thickness,
    lineType)

w, h = cv2.getTextSize('Hello World!', font, fontScale, lineType)[0]
x2, y2 = x+w, y-h
x_c, y_c = int(x+w/2), int(y-h/2)
print(f"{x} | {y} | {x_c} | {y_c}")

# print(cv2.getTextSize('Hello World!', font, fontScale, lineType))

M = cv2.getRotationMatrix2D((x_c, y_c), angle, 1)
cos, sin = abs(M[0, 0]), abs(M[0, 1])
newW = int((h * sin) + (w * cos))
newH = int((h * cos) + (w * sin))

out = np.copy(out_raw)
out = cv2.rectangle(out, (x, y), (x + w, y - h), (255,255,255), 1)
out = cv2.warpAffine(out, M, (out.shape[1], out.shape[0]))
out_raw = cv2.warpAffine(out_raw, M, (out_raw.shape[1], out_raw.shape[0]))

newX = x_c - int(newW/2)
newY = y_c - int(newH/2)

newX2 = x_c + int(newW/2)
newY2 = y_c + int(newH/2)

out_trimmed_no_bbox = out_raw[newY:newY2, newX:newX2, :]
out = cv2.rectangle(out, (newX, newY), (newX2, newY2), (255,255,255), 1)
out_trimmed = out[newY:newY2+1, newX:newX2+1, :]

#Display the image
cv2.imshow("out", out)

#Save image
cv2.imwrite("out.jpg", out)
cv2.imwrite("out_trimmed.jpg", out_trimmed)
cv2.imwrite("out_no_bbox.jpg", out_raw)
cv2.imwrite("out_trimmed_no_bbox.jpg", out_trimmed_no_bbox)

cv2.waitKey(0)

