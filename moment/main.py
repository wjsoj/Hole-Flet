import flet as ft
import threading as th
import os
from time import sleep
from math import ceil
from urllib import parse
import requests
import re
import cv2
import numpy as np
from PIL import Image, ImageDraw
import sys

path = os.path.dirname(os.path.realpath(sys.argv[0]))+'/HeadPhoto'
if not os.path.exists(path):
    os.mkdir(path)

def main(page: ft.Page):
    page.title = '朋友圈集赞截图生成'
    
    def generate(file_path,wanted,mode,pb,tip):
        color = {'dark': (32,32,32),'light': (247,247,247)}
        def add_rectangle(needed):
            global x,y,w,h
            img =cv2.imread(file_path)
            mask = cv2.inRange(img,np.array(color[mode]),np.array(color[mode]))
            (contours, hierarchy) = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                xx,yy,ww,hh = cv2.boundingRect(contour)
                tmp = 9999
                
                if ww>900 and xx:
                    # rectangle = cv2.rectangle(img,(xx,yy),(xx+ww,yy+hh),(0,255,0),3)
                    if yy<tmp:
                        x=xx;y=yy;w=ww;h=hh
                        tmp=yy
                    # cv2.namedWindow("img",0)
                    # cv2.imshow('img',rectangle)
                    # cv2.waitKey()
                    # input()
            rectangle = cv2.rectangle(img,(x+70,y+25),(x+w,y+30+(100)),color[mode],-1)
            if y+40+(100)*(needed)<=2100:
                rectangle = cv2.rectangle(rectangle,(x,y+25+100),(x+w,y+40+(100)*(needed)),color[mode],-1)
            else:
                rectangle = cv2.rectangle(rectangle,(x,y+25+100),(x+w,2100),color[mode],-1)
                bottom = rectangle[2100:,:,]
                addition = rectangle[y+150:y+150+100,:,]
                rectangle = rectangle[:2100,:,]
                # print(addition.shape,rectangle.shape)
                for i in range((((y+40+(100)*(needed))-2100)//100)):
                    rectangle = np.vstack((rectangle,addition))
                rectangle = np.vstack((rectangle,addition[:(((y+40+(100)*(needed))-2100)%100),:,]))
                rectangle = np.vstack((rectangle,bottom))
            cv2.imwrite(os.path.dirname(os.path.realpath(sys.argv[0]))+'/out.jpg',rectangle)

        def add_alpha_channel(img):
            b,g,r = cv2.split(img)
            alpha = np.ones(b.shape,dtype=b.dtype)*255
            return cv2.merge((b,g,r,alpha))

        def add_photo(photo,cnt):
            img =cv2.imread(os.path.dirname(os.path.realpath(sys.argv[0]))+'/out.jpg')
            img = add_alpha_channel(img)
            inn = cv2.resize(photo, (85,85), interpolation= cv2.INTER_LINEAR)
            # img[y+30:y+120,x+200:x+290]=inn
            y1 = y+33+(cnt//9)*100
            y2 = y1+85
            x1 = x+86+(cnt%9)*102
            x2 = x1+85
            alpha_png = inn[:,:,3]/255
            alpha_jpg = 1 - alpha_png
            trans = [2,1,0,3]
            for c in range(3):
                img[y1:y2,x1:x2,c] = (alpha_jpg*img[y1:y2,x1:x2,c])+(alpha_png*inn[:,:,trans[c]])
            cv2.imwrite(os.path.dirname(os.path.realpath(sys.argv[0]))+'/out.jpg',img)

        def circle_corner(img, radii):
            circle = Image.new('L', (radii * 2, radii * 2), 0)  # 创建黑色方形
            draw = ImageDraw.Draw(circle)
            draw.ellipse((0, 0, radii * 2, radii * 2), fill=255)  # 黑色方形内切白色圆形

            img = img.convert("RGBA")
            w, h = img.size

            alpha = Image.new('L', img.size, 255)
            alpha.paste(circle.crop((0, 0, radii, radii)), (0, 0))  # 左上角
            alpha.paste(circle.crop((radii, 0, radii * 2, radii)),
                        (w - radii, 0))  # 右上角
            alpha.paste(circle.crop((radii, radii, radii * 2, radii * 2)),
                        (w - radii, h - radii))  # 右下角
            alpha.paste(circle.crop((0, radii, radii, radii * 2)),
                        (0, h - radii))  # 左下角
            img.putalpha(alpha)  # 白色区域透明可见，黑色区域不可见
            return img
        
        add_rectangle(ceil(wanted/9))
        radii = 35  # 圆角大小
        file = os.path.dirname(os.path.realpath(sys.argv[0]))+'/HeadPhoto'
        cnt = 0
        for root, dirs, files in os.walk(file):
            for file in files:
                path = os.path.join(root, file)
                img = Image.open(path)
                img = circle_corner(img, radii)
                add_photo(np.array(img),cnt)
                cnt+=1
                pb.value = cnt/wanted
                tip.value = f'Generating {cnt} of {wanted}...'
                page.update()
                if cnt==wanted:
                    page.go('/finish')
                    return
    
    def finish(e):
        # page.client_storage.remove('avatar')
        page.client_storage.remove('download_num')
        # page.client_storage.remove('wechat_mode')
        page.window_destroy()
    
    def downloader(num,pb,tip,kind,lv):
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/78.0.3904.108 Safari/537.36",
        }
        url_base = 'https://www.woyaogexing.com/touxiang'
        pb.value = 0
        tip.value = f'Downloading 0 of {num}...'
        global cnt
        cnt = 0
        
        def get_url():
            ans = []
            first = {'Default': '','Girls': '/nv','Boys': '/nan','Scenery': '/fengjing','Comic': '/katong'}
            for i in range(ceil(num/180)):
                if i==0:
                    ans.append(url_base+first[kind]+'/index.html')
                else:
                    ans.append(url_base+first[kind]+f'/index_{i+1}.html')
            return ans
        
        def get_pic(urlnow):
            global cnt,flag
            response2 = requests.get(url=urlnow, headers=headers)
            response2.encoding = response2.apparent_encoding
            html2 = response2.text
            # with open('html.txt','w',encoding='utf-8') as fw:
            #     fw.write(html2)
            pics = re.findall('<a href="//(.*?)" class="swipebox">', html2)
            for picc in pics:
                cnt+=1
                sleep(0.1)
                file_name = picc.split('/')[-1]
                response = requests.get(url='http://'+picc, headers=headers)
                # 以二进制形式存储
                with open(path + '/' + file_name, mode='wb') as f:
                    f.write(response.content)
                    lv.controls.append(ft.Text('Saving  '+file_name))
                pb.value = cnt/(num)
                tip.value = f'Downloading {cnt} of {num}...'
                page.update()
                if cnt==num:
                    return
        
        urll = get_url()
        for url_ in urll:
            response = requests.get(url=url_, headers=headers)
            response.encoding = response.apparent_encoding
            html = response.text
            # with open('html.txt','w',encoding='utf-8') as fw:
            #     fw.write(html)

            urls = re.findall('<a href="(.*?)" class="img" target="_blank"', html)
            titles = re.findall('class="img" target="_blank" title="(.*?)">', html)
            for url,title in zip(urls,titles):
                # 加一秒延迟
                sleep(0.1)
                # 拼接域名，如果存在则忽略
                url = parse.urljoin('https://www.woyaogexing.com/', url)
                lv.controls.append(ft.Text(title+url))
                get_pic(url)
                if cnt==num:
                    page.go('/second')
                    return
    
    def open_confirm_diag(e):
        def close_dlg(f):
            dlg.open = False
            page.update()
            sleep(0.2)
            page.go('/first')
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Attention!",size=20),
            content=ft.Text("The effect of this program differ from different phone models.\nIt highly depends on resolution ratio of the screenshot you provide.\nThe width of 1080px is recommended.",size=16),
            actions=[
                ft.TextButton("Confirm", on_click=close_dlg)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )
        page.dialog = dlg
        dlg.open = True
        page.update()
    
    def route_change(route):
        wanted = ft.TextField(label='The number of avatars you want to download.',hint_text='Please be patient.',width=350,autofocus=True)
        need = ft.TextField(label='The number of likes you want to generate.',hint_text='Please be patient.',width=350,autofocus=True)
        
        def download_pre(e):
            page.client_storage.set('download_num',wanted.value)
            page.go('/download')
        def on_dialog_result(e: ft.FilePickerResultEvent):
            try:
                x = e.files[-1]
            except:
                return
            page.views[-1].controls.clear()
            pb = ft.ProgressBar(width=480,height=15)
            tip = ft.Text(f'Generating 0 of {int(need.value)}...',size=25)
            tt = th.Thread(target=generate,daemon=True,args=[e.files[-1].path,int(need.value),page.client_storage.get('wechat_mode'),pb,tip])
            tt.start()
            page.views[-1].controls.append(pb)
            page.views[-1].controls.append(tip)
            page.update()
        
        file_picker = ft.FilePicker(on_result=on_dialog_result)
        page.overlay.append(file_picker)
        
        page.views.clear()
        if page.route=='/':
            page.views.append(
                ft.View(
                    '/',
                    [
                        ft.Text('Initialize',size=28),
                        ft.Dropdown(
                            on_change= lambda e: page.client_storage.set('wechat_mode',e.control.value),
                            label='Choose Wechat Theme Mode',
                            hint_text = 'Choose Wechat Theme Mode',
                            options=[
                                ft.dropdown.Option('light'),
                                ft.dropdown.Option('dark')
                            ],
                            width=300,
                            autofocus=True
                        ),
                        ft.Dropdown(
                            on_change= lambda e: page.client_storage.set('avatar',e.control.value),
                            label='Choose Avatar Category',
                            hint_text = 'Choose Avatar Category',
                            options=[
                                ft.dropdown.Option('Default'),
                                ft.dropdown.Option('Girls'),
                                ft.dropdown.Option('Boys'),
                                ft.dropdown.Option('Scenery'),
                                ft.dropdown.Option('Comic')
                            ],
                            width=300,
                            autofocus=True
                        ),
                        ft.FilledButton('Start',width=200,on_click=open_confirm_diag),
                    ],
                    spacing=30,
                    horizontal_alignment='center',
                    vertical_alignment='center'
                )
            )
        if page.route == '/first':
            page.views.append(
                ft.View(
                    '/first',
                    [
                        ft.Text(f'{len(os.listdir(path))} Files Detected.',size=22),
                        wanted,
                        ft.Row([ft.ElevatedButton('Skip',width=100,on_click=lambda _: page.go('/second')),ft.FilledButton('Download',width=100,on_click=download_pre)],alignment='center')
                    ],
                    horizontal_alignment='center',
                    vertical_alignment='center',
                    spacing=30
                )
            )
        if page.route=='/second':
            page.views.append(
                ft.View(
                    '/second',
                    [
                        ft.Text('How many Likes do you need?',size=22),
                        need,
                        ft.ElevatedButton('Choose and Generate',icon=ft.icons.UPLOAD_FILE,on_click=lambda _: file_picker.pick_files(allow_multiple=False)),
                    ],
                    horizontal_alignment='center',
                    vertical_alignment='center',
                    spacing=30
                )
            )
        if page.route=='/download':
            pb = ft.ProgressBar(width=480,height=15)
            lv = ft.ListView(expand=1, spacing=10, padding=20,auto_scroll=True)
            num = int(page.client_storage.get('download_num'))
            tip = ft.Text(f'Downloading 0 of {num}...',size=25)
            tt = th.Thread(target=downloader,daemon=True,args=[num,pb,tip,page.client_storage.get('avatar'),lv])
            tt.start()
            
            page.views.append(
                ft.View(
                    '/download',
                    [
                        pb,
                        tip,
                        ft.Container(
                            content=lv,
                            height=250,
                            alignment=ft.alignment.center,
                        )
                    ],
                    horizontal_alignment='center',
                    vertical_alignment='center',
                    spacing=30
                )
            )
        if page.route=='/finish':
            page.views.append(
                ft.View(
                    '/finish',
                    [
                        ft.Column([ft.Image(src='/out.jpg',height=page.window_height-130)],scroll='auto'),
                        ft.FilledButton('Done!',on_click=finish,width=200)
                    ],
                    horizontal_alignment='center',
                    vertical_alignment='center',
                    spacing=15
                )
            )
        page.update()
    
    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)
    
    page.theme_mode = 'system'
    page.window_opacity = 0.95
    page.window_width = 600
    
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    page.go(page.route)
    # page.go('/finish')

ft.app(target=main,assets_dir=os.path.dirname(os.path.realpath(sys.argv[0])))