import copy
import numpy as np
import cv2
import random

from bbox import Bbox


class MedIMG:

    def __init__(self, ID, PATH=''):
        self.ID = ID
        self.PATH = PATH
        self.image = self.load_from_path()
        for i in range(14):
            self.generate_text()

    def load_from_path(self):
        image = cv2.imread(f"{self.PATH}{self.ID}.png", cv2.IMREAD_COLOR)
        return image

    def generate_text(self):
        out_raw = np.zeros((512, 512, 3), np.uint8)
        x_initial, y_initial = 200, 300
        word_info = self.generate_random_word_info()
        FONTSCALE = 1
        OVERLAP = False
        cv2.putText(out_raw, 'Hello World!',
                    (x_initial, y_initial),
                    word_info["FONT"],
                    FONTSCALE,
                    word_info["COLOR"],
                    word_info["THICKNESS"],
                    word_info["LINE_TYPE"])

        text_width, text_height = cv2.getTextSize('Hello World!', word_info["FONT"], FONTSCALE, word_info["LINE_TYPE"])[
            0]

        x_c, y_c = int(x_initial + text_width / 2), int(y_initial - text_height / 2)

        M = cv2.getRotationMatrix2D((x_c, y_c), word_info["ANGLE"], 1)
        out_raw = cv2.warpAffine(out_raw, M, (out_raw.shape[1], out_raw.shape[0]))

        cos, sin = abs(M[0, 0]), abs(M[0, 1])
        newW = int((text_height * sin) + (text_width * cos))
        newH = int((text_height * cos) + (text_width * sin))
        newX = x_c - int(newW / 2)
        newY = y_c - int(newH / 2)
        newX2 = x_c + int(newW / 2)
        newY2 = y_c + int(newH / 2)

        text_box = out_raw[newY:newY2, newX:newX2, :]

        # bbox location which text is watermarked on image
        l, r = Bbox.random_bbox_location(self.image, text_box)

        if not OVERLAP:
            while Bbox.do_overlap(l, r):
                # get another random location
                l, r = Bbox.random_bbox_location(self.image, text_box)

        self.watermark_word(text_box, l[0], l[1])
        Bbox(l[0], l[1], r[0], r[1], TYPE=1)  # adding bbox
        # cv2.rectangle(self.image, (l[0], l[1]), (r[0], r[1]), (255, 255, 255), 1)

    def watermark_word(self, word, x, y):
        for i, row in enumerate(word):
            for j, pixel in enumerate(row):
                if np.amax(pixel) > 0:
                    self.image[y + i, x + j] = [pixel[2], pixel[1], pixel[0]]

    @staticmethod
    def generate_random_word_info():
        # available_fonts = ["FONT_HERSHEY_SIMPLEX",
        #                    "FONT_HERSHEY_PLAIN",
        #                    "FONT_HERSHEY_DUPLEX",
        #                    "FONT_HERSHEY_COMPLEX",
        #                    "FONT_HERSHEY_TRIPLEX",
        #                    "FONT_HERSHEY_COMPLEX_SMALL",
        #                    "FONT_HERSHEY_SCRIPT_SIMPLEX",
        #                    "FONT_HERSHEY_SCRIPT_COMPLEX"]
        available_fonts = [0, 1, 2, 3, 4, 5, 6, 7]

        available_colors = [(255, 255, 255),
                            (255, 255, 0),
                            (255, 0, 255),
                            (0, 255, 255)]

        available_thickness = [1, 2, 3]
        available_lineType = [2]
        ANGLE = random.randrange(360)
        FONT = available_fonts[random.randrange(len(available_fonts))]
        COLOR = available_colors[random.randrange(len(available_colors))]
        THICKNESS = available_thickness[random.randrange(len(available_thickness))]
        LINE_TYPE = available_lineType[random.randrange(len(available_lineType))]

        word_info = {
            "ANGLE": ANGLE,
            "FONT": FONT,
            "COLOR": COLOR,
            "THICKNESS": THICKNESS,
            "LINE_TYPE": LINE_TYPE
        }

        return word_info


class DataGenerator:

    def __init__(self, row_img, *args, **kwargs):

        self.no_bbox_img = copy.deepcopy(row_img)
        self.bbox_img = copy.deepcopy(row_img)
        Bbox.draw_bboxes(self.bbox_img)
        self.drawing = False

        self.line_color = None
        self.line_thickness = None
        self.last_x = None
        self.last_y = None
        self.make_random_line()

        # to store bbox
        self.l_x = None
        self.l_y = None
        self.r_x = None
        self.r_y = None

        # to store shape's initial x and y
        self.shape_initial_x = None
        self.shape_initial_y = None

    def draw_line(self, event, x, y, flags, param):

        if event == cv2.EVENT_LBUTTONDOWN:

            self.drawing = True
            cv2.line(self.no_bbox_img, (x, y), (x, y), self.line_color, thickness=self.line_thickness)
            cv2.line(self.bbox_img, (x, y), (x, y), self.line_color, thickness=self.line_thickness)
            self.last_x, self.last_y = x, y

            # only initial when drawing the first point of the shape
            if self.l_x is None:
                self.l_x = x
                self.l_y = y
                self.r_x = x
                self.r_y = y

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                cv2.line(self.no_bbox_img, (self.last_x, self.last_y), (x, y), self.line_color,
                         thickness=self.line_thickness)
                cv2.line(self.bbox_img, (self.last_x, self.last_y), (x, y), self.line_color,
                         thickness=self.line_thickness)
                self.last_x, self.last_y = x, y

        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            cv2.line(self.no_bbox_img, (self.last_x, self.last_y), (x, y), self.line_color,
                     thickness=self.line_thickness)
            cv2.line(self.bbox_img, (self.last_x, self.last_y), (x, y), self.line_color, thickness=self.line_thickness)

        if self.drawing:
            if x < self.l_x:
                self.l_x = x

            if x > self.r_x:
                self.r_x = x

            if y < self.l_y:
                self.l_y = y

            if y > self.r_y:
                self.r_y = y

    def save_img(self):
        cv2.imwrite("savedImage.png", self.no_bbox_img)

    def make_random_line(self):
        LINE_COLORS = [(255, 255, 255), (255, 0, 0), (0, 0, 255), (0, 255, 0), (0, 0, 0)]
        THICKNESS_MAX = 10
        self.line_color = LINE_COLORS[random.randrange(len(LINE_COLORS))]
        self.line_thickness = random.randint(1, THICKNESS_MAX)

    def add_to_bbox(self):

        if self.l_x is None or self.l_y is None or self.r_x is None or self.r_y is None:
            print("ERROR: could no detect any drawing...")

        else:
            bbox_dimension = (self.l_x - (self.line_thickness//2+1),
                              self.l_y - (self.line_thickness//2+1),
                              self.r_x + (self.line_thickness//2+1),
                              self.r_y + (self.line_thickness//2+1))

            Bbox(bbox_dimension[0], bbox_dimension[1], bbox_dimension[2], bbox_dimension[3], TYPE=2)
            Bbox.draw_last_bbox(self.bbox_img)
            self.l_x = None
            self.l_y = None
            self.r_x = None
            self.r_y = None


if __name__ == '__main__':

    SHOW_BBOX = True
    med_scan = MedIMG('1')
    image_array = med_scan.image

    app = DataGenerator(image_array)

    cv2.namedWindow('test draw')
    cv2.setMouseCallback('test draw', app.draw_line)
    while True:
        if SHOW_BBOX:
            cv2.imshow('test draw', app.bbox_img)
        else:
            cv2.imshow('test draw', app.no_bbox_img)

        key = cv2.waitKey(1)

        if key == ord('s'):  # save and exit
            app.save_img()
            break

        elif key == ord('r'):
            app.make_random_line()

        elif key == ord('b'):
            SHOW_BBOX = not SHOW_BBOX
            print(SHOW_BBOX)

        elif key == ord(' '):
            app.add_to_bbox()

    cv2.destroyAllWindows()
