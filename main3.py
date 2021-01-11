import json
import os
import tkinter as tk
from tkinter import *
from tkinter import messagebox

import PIL.Image
import pytesseract
from PIL import ImageTk
from win32api import GetSystemMetrics
import math

ROOT_IMAGE_PATH = './images/'
INPUT_JSON_PATH = './Sara_CRINF-600.json'
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'
IMG_ZOOM_VALUE = 1


class Region:
    def __init__(self, x=None, y=None, w=None, h=None, r_class='machine printed', legibility='legible',
                 detected_text='', r_id=""):
        self.r_id = r_id
        self.r_class = r_class
        self.legibility = legibility
        self.detected_text = detected_text
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def print_region(self):
        print('X: {}, Y: {}, W: {}, H: {}'.format(self.x, self.y, self.w, self.h))


class ImageItem:
    def __init__(self, file_name, width, height, category, boxes_regions=0, regions=[]):
        self.file_name = file_name
        self.width = width
        self.height = height
        self.category = category
        self.boxes_regions = boxes_regions
        self.regions = regions

    def dumpy2json(self):
        fn = os.path.splitext(self.file_name)
        regions = [{
            'id': '{}_{}{}'.format(fn[0], idx, fn[1]),
            'class': x.r_class,
            'legibility': x.legibility,
            'bbox': [x.x, x.y, x.w, x.h],
            'detected_text': x.detected_text
        }
            for idx, x in enumerate(self.regions)]
        output = {
            "file_name": self.file_name,
            "width": self.width,
            "height": self.height,
            "boxes_regions": len(self.regions),
            "category": "OT",
            "regions": regions
        }
        with open('./done_json/{}.json'.format(fn[0]), "w", encoding='utf-8') as outfile:
            json.dump(output, outfile, indent=4, ensure_ascii=False)

            # now let's initialize the list of reference point


class ExampleApp(Frame):
    def __init__(self, master, img_json):
        Frame.__init__(self, master=None)
        self.x = self.y = 0

        self.canvas = Canvas(self, cursor="cross")
        self.canvas.config(width=GetSystemMetrics(0) - 100, height=GetSystemMetrics(1) - 200)
        self.sbarv = Scrollbar(self, orient=VERTICAL, command=self.canvas.yview)
        self.sbarh = Scrollbar(self, orient=HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.sbarv.set, xscrollcommand=self.sbarh.set)

        self.canvas.grid_rowconfigure(0, weight=1)
        self.canvas.grid_columnconfigure(0, weight=1)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.sbarv.grid(row=0, column=1, sticky="ns")
        self.sbarh.grid(row=1, column=0, sticky="ew")

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.rect = None
        self.start_x = None
        self.start_y = None

        img_name = os.path.join(ROOT_IMAGE_PATH, img_json['file_name'])

        self.im = PIL.Image.open(img_name).convert('RGB')
        basewidth = max(int(GetSystemMetrics(0) * IMG_ZOOM_VALUE), self.im.size[0])

        self.wpercent = (basewidth / float(self.im.size[0]))
        hsize = int((float(self.im.size[1]) * float(self.wpercent)))

        self.im = self.im.resize((basewidth, hsize), PIL.Image.ANTIALIAS)

        self.tk_im = ImageTk.PhotoImage(self.im)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_im)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

        self.img_json = img_json
        fn = os.path.splitext(img_json['file_name'])
        if os.path.exists('./done_json/{}.json'.format(fn[0])):
            self.image_item = loadjson('./done_json/{}.json'.format(fn[0]))
            self.image_regions = self.image_item.regions

            for rg in self.image_item.regions:
                self.canvas.create_rectangle(rg.x * self.wpercent,
                                             rg.y * self.wpercent,
                                             (rg.x + rg.w) * self.wpercent,
                                             (rg.y + rg.h) * self.wpercent,
                                             outline='green')

        else:
            self.image_regions = []
            self.image_item = ImageItem(file_name=self.img_json['file_name'],
                                        category=self.img_json['category'],
                                        height=int(self.img_json['height']),
                                        width=int(self.img_json['width'])
                                        )

    def on_button_press(self, event):
        # save mouse drag start position
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

        # create rectangle if not yet exist
        # if not self.rect:
        self.rect = self.canvas.create_rectangle(self.x, self.y, 1, 1, outline='red')

    def on_move_press(self, event):
        curX = self.canvas.canvasx(event.x)
        curY = self.canvas.canvasy(event.y)

        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if event.x > 0.9 * w:
            self.canvas.xview_scroll(1, 'units')
        elif event.x < 0.1 * w:
            self.canvas.xview_scroll(-1, 'units')
        if event.y > 0.9 * h:
            self.canvas.yview_scroll(1, 'units')
        elif event.y < 0.1 * h:
            self.canvas.yview_scroll(-1, 'units')

        # expand rectangle as you drag the mouse
        self.canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)

    def on_button_release(self, event):
        canvas = event.widget
        new_x = canvas.canvasx(event.x)
        new_y = canvas.canvasy(event.y)

        x = self.start_x
        y = self.start_y

        w = abs(x - new_x)
        h = abs(y - new_y)

        # import random

        new_bb_img = (x, y, new_x, new_y)
        sub_img = self.im.crop(new_bb_img)
        # sub_img.save(str(random.randint(10, 10000)) + '.png', 'PNG')
        detected_text = pytesseract.image_to_string(sub_img).strip()
        if detected_text == '':
            detected_text = 'NO'
        entry.delete(0, END)
        entry.insert(0, detected_text)
        x = math.floor(x / self.wpercent)
        y = math.floor(y / self.wpercent)
        w = round(w / self.wpercent)
        h = round(h / self.wpercent)
        print(x, y, w, h)
        self.region = Region(x=x,
                             y=y,
                             w=w,
                             h=h,
                             detected_text=detected_text)

        entry.focus()

    def set_text(self):
        text = entry.get()
        self.region.detected_text = text
        self.image_regions.append(self.region)
        self.image_item.regions = self.image_regions
        self.image_item.dumpy2json()
        entry.delete(0, END)
        messagebox.showinfo("Result", "BBox Added!, Thank you Sara :*")
        print('New bbox added')

    def on_close(self):
        self.image_item.dumpy2json()
        entry.destroy()
        root.destroy()

    def on_quit(self):
        self.image_item.dumpy2json()
        entry.destroy()
        root.destroy()
        sys.exit()


def loadjson(json_path):
    with open(json_path, encoding='utf-8') as json_file:
        data = json.load(json_file)

    regions = []
    fn = os.path.splitext(data['file_name'])
    for idx, rg in enumerate(data['regions']):
        regions.append(Region(
            x=rg['bbox'][0], y=rg['bbox'][1], w=rg['bbox'][2], h=rg['bbox'][3],
            r_class=rg['class'],
            legibility=rg['legibility'],
            detected_text=rg['detected_text'],
            r_id='{}_{}{}xxx'.format(fn[0], idx, fn[1])
        ))

    img_item = ImageItem(file_name=data['file_name'],
                         width=data['width'],
                         height=data['height'],
                         category=data['category'],
                         boxes_regions=len(regions),
                         regions=regions)
    return img_item


if __name__ == "__main__":

    with open(INPUT_JSON_PATH) as json_file:
        data = json.load(json_file)
        for img in data:
            if not os.path.exists(os.path.join(ROOT_IMAGE_PATH, img['file_name'])):
                continue
            root = Tk()
            app = ExampleApp(root, img)
            app.pack()

            entry = tk.Entry(root)
            entry.pack()
            Button(root, text="Set Text", command=lambda: app.set_text()).pack()
            Button(root, text="Close", command=lambda: app.on_close()).pack()
            Button(root, text="Quit", command=lambda: app.on_quit()).pack()

            root.mainloop()
            print('next image')
