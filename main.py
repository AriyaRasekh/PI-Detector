from tkinter import *
from PIL import Image, ImageTk, EpsImagePlugin, ImageDraw, ImageFont
EpsImagePlugin.gs_windows_binary =  r'C:\Program Files (x86)\gs\gs9.56.1\bin\gswin32c'
import math

class MedIMG:

    # https://www.youtube.com/watch?v=4ehHuDDH-uc&t=509s
    def __init__(self, ID, PATH=''):
        self.ID = ID
        self.PATH = PATH
        self.image = self.load_from_path()
        self.generate_text()

    def load_from_path(self):
        image = Image.open(f"{self.PATH}{self.ID}.png")

        return image

    def generate_text(self):
        random_word = "Hello boss!"
        font = ImageFont.truetype("arial.ttf", size=20)
        imgDraw = ImageDraw.Draw(self.image)
        imgDraw.text((10, 10), random_word, font=font, fill=255)


class DataGenerator(Tk):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title('Data Generator')
        self.geometry("1000x1000")
        self.resizable(False, False)

        self.canvas_frame = Frame(self)
        self.canvas = Canvas(self.canvas_frame , width=900, height=900, bg='black')
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
        self.canvas.postscript(file="save_name.eps") # save canvas as encapsulated postscript
        img = Image.open("save_name.eps")
        img.save("save_name.png", "png", quality=99)

if __name__ == '__main__':
    IMG_IDS = ['1', '2', '3', '4']

    app = DataGenerator()
    med_scan = MedIMG('1')

    image = med_scan.image
    image = image.resize((900, 900), Image.ANTIALIAS)
    image = ImageTk.PhotoImage(image)
    app.canvas.create_image(0, 0, image=image, anchor='nw')
    app.mainloop()
