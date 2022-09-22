from tkinter import *
from PIL import Image, ImageTk, EpsImagePlugin

import numpy as np
import cv2
from random import randrange

from bbox import Bbox

EpsImagePlugin.gs_windows_binary = r'C:\Program Files (x86)\gs\gs9.56.1\bin\gswin32c'


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

        text_width, text_height = cv2.getTextSize('Hello World!', word_info["FONT"], FONTSCALE, word_info["LINE_TYPE"])[0]

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
        Bbox(l[0], l[1], r[0], r[1])  # adding bbox
        cv2.rectangle(self.image, (l[0], l[1]), (l[0] + text_box.shape[1], l[1] + text_box.shape[0]), (255, 255, 255), 1)

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
        ANGLE = randrange(360)
        FONT = available_fonts[randrange(len(available_fonts))]
        COLOR = available_colors[randrange(len(available_colors))]
        THICKNESS = available_thickness[randrange(len(available_thickness))]
        LINE_TYPE = available_lineType[randrange(len(available_lineType))]

        word_info = {
            "ANGLE": ANGLE,
            "FONT": FONT,
            "COLOR": COLOR,
            "THICKNESS": THICKNESS,
            "LINE_TYPE": LINE_TYPE
        }

        return word_info


class DataGenerator(Tk):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title('Data Generator')
        self.geometry("1300x1300")
        self.resizable(False, False)

        self.canvas_frame = Frame(self)
        self.canvas = Canvas(self.canvas_frame, width=1024, height=1024, bg='black')
        self.save_button = Button(self, text='save', command=self.save_canvas)

        self.canvas_frame.pack()
        self.canvas.pack()
        self.save_button.pack()

        self.last_x = None
        self.last_y = None

        self.canvas.bind("<Button-1>", self.get_x_and_y)
        self.canvas.bind("<B1-Motion>", self.draw_line)

    def get_x_and_y(self, event):
        self.last_x, self.last_y = event.x, event.y

    def draw_line(self, event):
        self.canvas.create_line((self.last_x, self.last_y, event.x, event.y),
                                fill='red',
                                width=2)
        self.last_x, self.last_y = event.x, event.y

    def save_canvas(self):
        self.canvas.postscript(file="save_name.eps")  # save canvas as encapsulated postscript
        img = Image.open("save_name.eps")
        img.save("save_name.png", "png", quality=99)


if __name__ == '__main__':


    app = DataGenerator()
    med_scan = MedIMG('1')

    image_array = med_scan.image
    image = ImageTk.PhotoImage(image=Image.fromarray(image_array))
    app.canvas.create_image(0, 0, image=image, anchor='nw')
    app.mainloop()
