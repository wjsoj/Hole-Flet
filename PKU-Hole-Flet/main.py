import flet as ft
from flet import theme,margin
import requests
from random import randint
import time
import base64
import os
import threading as th
from math import ceil
import re
from retrying import retry

if os.path.exists(__file__[:-7]+'README.md'):
    with open(__file__[:-7]+'README.md','rb') as f:
        about_md = f.read().decode()
else:
    about_md = '# 广告位招租'

headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
}
cookies = 0
login_status = 0
is_loading=1
bg_colors = {
    'dark': [ft.colors.CYAN_900,ft.colors.BLUE_300,ft.colors.BLUE_GREY_300,ft.colors.BROWN_300,ft.colors.DEEP_ORANGE_400,ft.colors.DEEP_PURPLE_200,ft.colors.GREEN_400,ft.colors.LIGHT_GREEN_500,ft.colors.INDIGO_300,ft.colors.PINK_400,ft.colors.PURPLE_300,ft.colors.TEAL_300],
    'light': [ft.colors.CYAN_100,ft.colors.BLUE_100,ft.colors.BLUE_GREY_50,ft.colors.BROWN_50,ft.colors.DEEP_ORANGE_100,ft.colors.DEEP_PURPLE_50,ft.colors.GREEN_50,ft.colors.LIGHT_GREEN_100,ft.colors.INDIGO_50,ft.colors.PINK_100,ft.colors.PURPLE_100,ft.colors.TEAL_100]
}
ref_color = {
    'light': ft.colors.LIME_100,
    'dark': ft.colors.BLUE_GREY_600
}

g_loading = ft.ProgressRing(width=20,height=20)

def main(page: ft.Page):
    
    def get_bar():
        res = requests.get(url='https://treehole.pku.edu.cn/api/course/score',headers=headers).json()
        switch = ['Score','GPA']
        is_score = page.client_storage.get('is_score')
        
        def change_color(e):
            page.client_storage.set('is_score',is_score^1)
            route_change(page.route)
        
        fab = ft.FloatingActionButton(
            text='Switch to '+switch[is_score]+' mode',
            on_click= change_color,
            width=180
        )
        page.views[-1].floating_action_button = fab
        
        # res = {'data' : {'score' : {'jbxx': {'xm':'hahaha'},'cjxx' : [{'ywmc' : 'test1','skjsxm' : 'teacher','xqcj' : '95','jd' : '3.94'},{'ywmc' : 'test2','skjsxm' : 'teacher','xqcj' : '85','jd' : '3.84'},{'ywmc' : 'test3','skjsxm' : 'teacher','xqcj' : '75','jd' : '3.74'},{'ywmc' : 'test4','skjsxm' : 'teacher','xqcj' : '65','jd' : '3.54'},{'ywmc' : 'test5','skjsxm' : 'teacher','xqcj' : '55','jd' : '3.24'},{'ywmc' : 'test6','skjsxm' : 'teacher','xqcj' : '45','jd' : '2.54'},{'ywmc' : 'test7','skjsxm' : 'teacher','xqcj' : '35','jd' : '2.04'},{'ywmc' : 'test8','skjsxm' : 'teacher','xqcj' : '25','jd' : '1.24'},],'gpa': {'gpa':'3.930'}}}}
        
        def cal_color(n,limit,pf=0):
            if pf==1:
                return '#00FF00'
            if pf==-1:
                return '#FF0000'
            if n<limit:
                return '#FF0000'
            rr = hex(int(255*(100-n)/(100-limit)))[2:]
            gg = hex(int(255*(n-limit)/(100-limit)))[2:]
            if len(rr)<2:
                rr = '0'+rr
            if len(gg)<2:
                gg = '0'+gg
            return '#'+rr+gg+'00'
        
        def load(row,cj,jd,flag):
            pf = 0
            if cj=='合格':
                score = 100
                gpa = 100
                pf = 1
            elif cj=='不合格':
                score = 100
                gpa = 100
                pf = -1
            else:
                score = int(cj)
                gpa = float(jd)/4*100
            pb = row.controls[0]
            if flag:
                for s in range(0,101):
                    pb.value = score/10000*s
                    pb.color = cal_color(score/100*s,50,pf)
                    time.sleep(0.01)
                    page.update()
            else:
                for s in range(0,101):
                    pb.value = gpa/10000*s
                    pb.color = cal_color(gpa/100*s,25,pf)
                    time.sleep(0.01)
                    page.update()
            if pf == 0:
                row.controls.append(ft.Column([ft.Text(cj+'/100',size=18),ft.Text(jd+'/4.00',size=18)]))
            else:
                row.controls.append(ft.Text(cj,size=20,width=80))
            page.update()
        
        def total_gpa():
            pb = ft.ProgressBar(width=800,bar_height=60,bgcolor=ft.colors.BLUE)
            head = ft.Column(
                [
                    ft.Text('Your Name: '+res['data']['score']['jbxx']['xm'],size=20),
                ]
            )
            page.views[-1].controls.append(head)
            score = float(res['data']['score']['gpa']['gpa'])/4*100
            main = ft.Row([pb,],alignment='center')
            page.views[-1].controls.append(main)
            for s in range(0,101):
                pb.value = score/10000*s
                pb.color = cal_color(score/100*s,50)
                time.sleep(0.005)
                page.update()
            main.controls.append(ft.Column([ft.Text('Total GPA:',size=18),ft.Text(res['data']['score']['gpa']['gpa']+'/4.00',size=18)]))
            page.update()
        
        total_gpa()
        time.sleep(0.5)
        for course in res['data']['score']['cjxx']:
            pb = ft.ProgressBar(width=800,bar_height=60,bgcolor=ft.colors.BLUE)
            name = course['ywmc']
            teacher = ' '.join(re.findall('[^0-9,-]*?\$.*?\$[^0-9,-]*',course["skjsxm"]))
            head = ft.Column(
                [
                    ft.Text('Course Name: '+name,size=20),
                    ft.Text('Teacher: '+teacher,size=18),
                ]
            )
            main = ft.Row([pb,],alignment='center')
            page.views[-1].controls.append(head)
            page.views[-1].controls.append(main)
            page.update()
            load_t = th.Thread(target=load,daemon=True,args=[main,course['xqcj'],course['jd'],is_score])
            load_t.start()
    
    def card_click(src,pid):
        global g_loading
        page.set_clipboard(src)
        for url in re.findall('https{0,1}[//:a-zA-Z/.%&=0-9-?+_]*',src):
            os.system('start '+url)
        hole_list = ft.ListView(
            expand=1,
            spacing=10,
            padding=20,
        )
        flag=0
        for j in re.findall('\d{7}',src):
            g_loading.visible = True
            page.update()
            if int(j)>=2000000 and int(j)<int(pid):
                flag=1
                resss = requests.get(url='https://treehole.pku.edu.cn/api/pku/'+j,headers=headers).json()
                if 'data' in resss:
                    hole_list.controls.append(
                        ft.Card(
                            content=get_main_hole(resss['data']),
                        )
                    )
                else:
                    hole_list.controls.append(
                        ft.Card(
                            content=ft.Text('   Cannot Find the Hole Mentioned Above.',size=18)
                        )
                    )
        g_loading.visible = False
        if flag:
            page.views.append(
                ft.View(
                    '/detail',
                    [
                        ft.AppBar(title=ft.Text("Hole Mentioned"),center_title=False,bgcolor=ft.colors.BACKGROUND),
                        hole_list,
                    ],
                )
            )
            page.update()
        page.snack_bar = ft.SnackBar(ft.Text('Content has been copied to clipboard'))
        page.snack_bar.open=True
        page.update()
    
    def logout(e):
        def close_reply_dlg(e):
            dlg_warning.open =False
            page.update()
        
        def restored(e):
            page.client_storage.remove('uid')
            page.client_storage.remove('password')
            close_reply_dlg(e)
            page.go('/login')
        dlg_warning = ft.AlertDialog(
            modal = True,
            title=ft.Text('Are You sure to Log out?'),
            content=ft.Text('You need to login again.',size=18),
            actions=[
                ft.TextButton('Confirm',on_click=restored),
                ft.TextButton('Cancel',on_click=close_reply_dlg)
            ],
            actions_alignment='end',
            on_dismiss=close_reply_dlg
        )
        page.dialog = dlg_warning
        dlg_warning.open = True
        page.update()
    
    def restore(e):
        def close_reply_dlg():
            dlg_warning.open =False
            page.update()
        
        def restored(e):
            global login_status
            page.client_storage.clear()
            login_status = 0
            page.snack_bar = ft.SnackBar(ft.Text('Default Settings Restored,Please Login'))
            page.snack_bar.open=True
            close_reply_dlg()
            ini()
        dlg_warning = ft.AlertDialog(
            modal = True,
            title=ft.Text('Are You sure to Restore Default Settings?'),
            content=ft.Text('Attention,This operation is irreversible!',size=18),
            actions=[
                ft.TextButton('Confirm',on_click=restored),
                ft.TextButton('Cancel',on_click=close_reply_dlg)
            ],
            actions_alignment='end',
            on_dismiss=close_reply_dlg
        )
        page.dialog = dlg_warning
        dlg_warning.open = True
        page.update()
    
    def add_hole(e):
        def close_reply_dlg(e):
            dlg_reply.open =False
            page.update()
        
        def send_reply(e):
            data = {'type':'text','text':reply_text.value}
            res = requests.post('https://treehole.pku.edu.cn/api/pku_store',data=data,headers=headers).json()
            page.snack_bar = ft.SnackBar(ft.Text('Add Complete '+res['message']))
            page.snack_bar.open=True
            close_reply_dlg(e)
            route_change(page.route)
        reply_text = ft.TextField(label='Content',hint_text='Only Text is Supported',multiline=True)
        dlg_reply = ft.AlertDialog(
            modal = True,
            title=ft.Text('Add a Hole:'),
            content=ft.Container(
                content=reply_text,
                width=600,
                height=150,
            ),
            actions=[
                ft.TextButton('Confirm',on_click=send_reply),
                ft.TextButton('Cancel',on_click=close_reply_dlg)
            ],
            actions_alignment='end',
            on_dismiss=close_reply_dlg
        )
        page.dialog = dlg_reply
        dlg_reply.open = True
        page.update()
    
    def search_hole(e):
        def search_init(e):
            page.client_storage.set('keyword',search_text.value)
            dlg_reply.open =False
            if page.route=='/locate':
                route_change(page.route)
            else:
                page.go('/locate')
        def close_reply_dlg(e):
            dlg_reply.open =False
            page.update()
        search_text = ft.TextField(label='Search',hint_text='Only Text is Supported',multiline=True)
        dlg_reply = ft.AlertDialog(
            modal = True,
            title=ft.Text('Search in Holes'),
            content=ft.Container(
                content=search_text,
                width=350,
            ),
            actions=[
                ft.TextButton('Search',on_click=search_init),
                ft.TextButton('Cancel',on_click=close_reply_dlg)
            ],
            actions_alignment='end',
            on_dismiss=close_reply_dlg
        )
        page.dialog = dlg_reply
        dlg_reply.open = True
        page.update()
    
    def show_image(src):
        def close_image_dlg(e):
            dlg_image.open =False
            page.update()
        dlg_image = ft.AlertDialog(
            modal = True,
            title=ft.Text('Image'),
            content=ft.Column(
                [ft.Image(src_base64=src)],
                scroll='auto',
                # width = 800,
            ),
            actions=[
                ft.TextButton('Close',on_click=close_image_dlg)
            ],
            actions_alignment='end',
            on_dismiss=close_image_dlg
        )
        page.dialog = dlg_image
        dlg_image.open = True
        page.update()
    
    def Like(pid):
        res = requests.post('https://treehole.pku.edu.cn/api/pku_attention/'+str(pid),headers=headers).json()
        page.snack_bar = ft.SnackBar(ft.Text(str(pid)+': '+res['data']+' '+res['message']))
        page.snack_bar.open=True
        page.update()
    
    def Reply(pid):
        def close_reply_dlg(e):
            dlg_reply.open =False
            page.update()
        
        def send_reply(e):
            data = {'pid':pid,'text':reply_text.value}
            res = requests.post('https://treehole.pku.edu.cn/api/pku_comment',data=data,headers=headers).json()
            page.snack_bar = ft.SnackBar(ft.Text('Reply to '+str(pid)+': '+res['message']))
            page.snack_bar.open=True
            close_reply_dlg(e)
        reply_text = ft.TextField(label='Reply',hint_text='Only Text is Supported',multiline=True)
        dlg_reply = ft.AlertDialog(
            modal = True,
            title=ft.Text(f'Reply to hole {pid}:'),
            content=ft.Container(
                content=reply_text,
                width=500,
                height=120,
            ),
            actions=[
                ft.TextButton('Reply',on_click=send_reply),
                ft.TextButton('Cancel',on_click=close_reply_dlg)
            ],
            actions_alignment='end',
            on_dismiss=close_reply_dlg
        )
        page.dialog = dlg_reply
        dlg_reply.open = True
        page.update()

    def get_time(stamp):
        return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(stamp))
    
    def get_main_comment(i,pid):
        adjustment = 75*(len(i['text'])//50)
        ffff = ft.Container(
            content=ft.Column(
                [
                    ft.Text('#'+str(i['cid'])+'   '+get_time(i['timestamp']),size=12),
                    ft.Text(i['text'],weight=page.client_storage.get('weight'),size=page.client_storage.get('size'))
                ],
                scroll='auto',
            ),
            width=min(220+adjustment,1000),
            padding=10,
            bgcolor=bg_colors[page.client_storage.get('theme_mode')][randint(0,11)],
            border_radius=ft.border_radius.all(12),
            on_click= lambda e: card_click(str(i['text']),int(pid))
        )
        if len(i['text'])>600:
            ffff.height=330
        return ffff
    
    def get_main_hole(i,flag=0):
        if flag:
            return ft.Container(
                content=get_hole(i),
                padding=10,
                bgcolor=ref_color[page.client_storage.get('theme_mode')],
                border_radius=15,
                on_click=lambda _: card_click(str(i['text']),i['pid'])
            )
        else:
            return ft.Container(
                content=get_hole(i),
                padding=10,
                on_click=lambda _: card_click(str(i['text']),i['pid'])
            )
    
    @retry(stop_max_attempt_number=3,wait_random_min=3,wait_random_max=5)
    def get_comment(pid,num):
        if num==0:
            return ft.Text('No Comment Yet...')
        comments_list = ft.Row(
            spacing=10,
            scroll='adaptive',
        )
        response = requests.get(url='https://treehole.pku.edu.cn/api/pku_comment/'+pid+'?limit=50000',headers=headers).json()
        for i in response['data']['data']:
            comments_list.controls.append(
                ft.Card(
                    content=get_main_comment(i,pid),
                )
            )
        return comments_list
    
    @retry(stop_max_attempt_number=3,wait_random_min=3,wait_random_max=5)
    def get_hole(i):
        s = str(i['text'])
        if s=='None':
            ss = ''
        else:
            ss = s.replace('\r','',s.count('\r'))
        if i['type']=='text':
            LT = ft.ListTile(
                title=ft.Text(str(i['pid']),size=page.client_storage.get('size')+2,weight=page.client_storage.get('weight')),
                subtitle=ft.Text(ss,weight=page.client_storage.get('weight'),size=page.client_storage.get('size')+1)
            )
        else:
            response = requests.get(url='https://treehole.pku.edu.cn/api/pku_image/'+str(i['pid']),headers=headers)
            LT = ft.Column(
                [ft.ListTile(
                    title=ft.Text(str(i['pid']),size=page.client_storage.get('size')+4,weight=page.client_storage.get('weight')),
                    subtitle=ft.Text(ss,weight=page.client_storage.get('weight'),size=page.client_storage.get('size')+1)
                ),
                ft.Container(
                    content=ft.Image(
                    src_base64=base64.b64encode(response.content).decode('ascii'),
                    width=400,
                    ),
                    padding=15,
                    on_click=lambda _: show_image(base64.b64encode(response.content).decode('ascii'))
                ),
                ]
            )
        ans = ft.Column(
            [
                LT,
                ft.Row(
                    [
                        ft.Text(get_time(i['timestamp'])),
                        ft.TextButton('Like: '+str(i['likenum']),on_click=lambda _: Like(i['pid'])),
                        ft.TextButton('Reply: '+str(i['reply']),on_click=lambda _: Reply(i['pid']))
                    ],
                    alignment='end'
                ),
                get_comment(str(i['pid']),i['reply']),
            ]
        )
        return ans
    
    def ini():
        global cookies,login_status
        if not page.client_storage.contains_key('theme_mode'):
            page.client_storage.set('theme_mode','dark')
        if not page.client_storage.contains_key('opacity'):
            page.client_storage.set('opacity',0.95)
        if not page.client_storage.contains_key('loading'):
            page.client_storage.set('loading',50)
        if not page.client_storage.contains_key('size'):
            page.client_storage.set('size',15)
        if not page.client_storage.contains_key('weight'):
            page.client_storage.set('weight','w600')
        if not page.client_storage.contains_key('is_score'):
            page.client_storage.set('is_score',1)
        page.theme_mode = page.client_storage.get('theme_mode')
        page.window_opacity = page.client_storage.get('opacity')
        page.update()
        if page.client_storage.contains_key('uid') and page.client_storage.get('auto'):
            if time.strftime('%Y-%m-%d',time.localtime(time.time()))==time.strftime('%Y-%m-%d',time.localtime(page.client_storage.get('time'))):
                headers['Authorization']=page.client_storage.get('jwt')
                login_status = 1
                page.go('/home')
            else:
                data = {
                    'uid' : page.client_storage.get('uid'),
                    'password' : page.client_storage.get('password')
                }
                login_url = 'https://treehole.pku.edu.cn/api/login'
                response = requests.post(login_url,data=data,headers=headers)
                if response.json()['success']:
                    headers['Authorization']='Bearer '+response.json()['data']['jwt']
                    page.client_storage.set('jwt',headers['Authorization'])
                    page.client_storage.set('time',time.time())
                    cookies = response.cookies
                    login_status = 1
                    page.go('/home')
                else:
                    page.snack_bar=ft.SnackBar(ft.Text('Login Failed, Return to Login Page.'))
                    page.go('/login')
        else:
            page.go('/login')
    
    def page_resize(e):
        page.snack_bar = ft.SnackBar(ft.Text(
                value = f'Now Page Size: {page.window_width} * {page.window_height}',
                text_align = ft.TextAlign.CENTER,
                size=16,
                weight=ft.FontWeight.W_500
            ))
        page.snack_bar.open = True
        page.update()
    
    def select_theme_mode(e):
        page.client_storage.set('theme_mode',e.control.value)
        page.theme_mode = e.control.value
        page.update()
    
    def slider_changed(e):
        opacity_value=e.control.value/100
        page.window_opacity = opacity_value
        page.client_storage.set('opacity',opacity_value)
        page.update()
    
    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)
    
    def route_change(route):
        if page.route == '/detail':
            return
        hole_list = ft.ListView(
            expand=1,
            spacing=10,
            padding=20,
        )
        
        @retry(stop_max_attempt_number=5,wait_random_min=3,wait_random_max=5)
        def main_hole(flag=0):
            global is_loading,g_loading
            is_loading = 1
            cnt = 0
            maxp = ceil(page.client_storage.get('loading')/25)+1
            for _ in range(1,maxp):
                if flag==1:
                    res = requests.get(url='https://treehole.pku.edu.cn/api/follow?page='+str(_)+'&limit=25',headers=headers).json()
                if flag==0:
                    res = requests.get(url='https://treehole.pku.edu.cn/api/pku_hole?page='+str(_)+'&limit=25',headers=headers).json()
                if flag==2:
                    res = requests.get(url='https://treehole.pku.edu.cn/api/pku_hole?page='+str(_)+'&limit=25&keyword='+page.client_storage.get('keyword'),headers=headers).json()
                if len(res['data']['data'])==0:
                    hole_list.controls.append(
                        ft.Card(
                            content=ft.Text('No Hole Founded. Please Check Whether the Hole Exist.',size=20)
                        )
                    )
                for i in res['data']['data']:
                    hole_list.controls.append(
                        ft.Card(
                            content=get_main_hole(i)
                        )
                    )
                    for j in re.findall('\d{7}',str(i['text'])):
                        if int(j)>=2000000 and int(j)<i['pid']:
                            resss = requests.get(url='https://treehole.pku.edu.cn/api/pku/'+j,headers=headers).json()
                            if 'data' in resss:
                                hole_list.controls.append(
                                    ft.Card(
                                        content=get_main_hole(resss['data'],1),
                                        margin=margin.only(left=100),
                                    )
                                )
                            else:
                                hole_list.controls.append(
                                    ft.Card(
                                        content=ft.Text('   Cannot Find the Hole Mentioned Above.',size=18)
                                    )
                                )
                    cnt+=1
                    if cnt %5 ==0:
                        is_loading = 0
                        page.update()
                if _==res['data']['last_page']:
                    break
                time.sleep(randint(5,10))
            is_loading=0
            g_loading.visible= False
            page.update()
        
        def hole_init():
            while is_loading:
                time.sleep(0.1)
                page.update()
            return hole_list
        
        def close_error_diag(e):
            dlg.open = False
            tlogin1.value = ''
            tlogin2.value = ''
            page.update()
        
        def open_error_diag():
            page.dialog = dlg
            dlg.open = True
            page.update()
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text('An Error Occurred!'),
            content=ft.Text('Please Check Your Input or Server Status'),
            actions=[
                ft.TextButton('Got it!',on_click=close_error_diag),
                ft.TextButton('Fuck You!',on_click=close_error_diag),
            ],
            actions_alignment='end',
            on_dismiss=lambda e: print('Error!')
        )
        
        def login(e):
            global cookies,login_status
            data = {
                'uid' : tlogin1.value,
                'password' : tlogin2.value
            }
            is_auto_login = cblogin.value
            login_url = 'https://treehole.pku.edu.cn/api/login'
            response = requests.post(login_url,data=data,headers=headers)
            if response.json()['success']:
                page.client_storage.set('auto',is_auto_login)
                page.client_storage.set('uid',tlogin1.value)
                page.client_storage.set('password',tlogin2.value)
                headers['Authorization']='Bearer '+response.json()['data']['jwt']
                page.client_storage.set('jwt',headers['Authorization'])
                page.client_storage.set('time',time.time())
                cookies = response.cookies
                login_status = 1
                page.go('/home')
            else:
                open_error_diag()
        
        tlogin1 = ft.TextField(label='User ID',hint_text='Input your Student ID',width=250)
        tlogin2 = ft.TextField(label='Password',password=True,can_reveal_password=True,width=250)
        cblogin = ft.Checkbox(label='Auto Login Next Time',value = False,width= 200)
        
        barbar = ft.AppBar(
            title=ft.Text("PKU Hole Special Edition"),
            center_title=False,
            bgcolor=ft.colors.BACKGROUND,
            actions=[
                ft.Container(content=g_loading,padding=17),
                ft.TextButton(content=ft.Text('Hole',color=ft.colors.ON_SURFACE),on_click=lambda _: page.go('/home')),
                ft.TextButton(content=ft.Text('Score',color=ft.colors.ON_SURFACE),on_click=lambda _: page.go('/score')),
                ft.PopupMenuButton(
                    content=ft.Container(
                        content=ft.Text('Miscellaneous',size=14,weight=ft.FontWeight.W_500),
                        padding=ft.padding.only(top=18,right=10,left=10),
                    ),
                    items=[
                        ft.PopupMenuItem(text='Courses Evaluation',on_click=lambda _:os.system('start https://courses.pinzhixiaoyuan.com/')),
                        ft.PopupMenuItem(text='lib-pku',on_click=lambda _:os.system('start https://lib-pku.github.io/')),
                        ft.PopupMenuItem(text='Web-score old',on_click=lambda _:os.system('start https://pku-score.guyutongxue.site/')),
                        ft.PopupMenuItem(),
                        ft.PopupMenuItem(text='Back')
                    ]
                ),
                ft.IconButton(ft.icons.ADD,on_click=add_hole),
                ft.IconButton(ft.icons.FAVORITE,on_click=lambda _: page.go('/fav')),
                ft.IconButton(ft.icons.SEARCH,on_click=search_hole),
                ft.IconButton(ft.icons.REFRESH,on_click=route_change),
                ft.IconButton(ft.icons.SETTINGS,on_click=lambda _: page.go('/setting')),
                ft.IconButton(ft.icons.INFO,on_click=lambda _: page.go('/about')),
                ft.TextButton(content=ft.Text('Log Out'),on_click=logout),
            ],
        )
        
        def ininin():
            time.sleep(360000)
            return ft.Text('Loading...')
        
        g_loading.visible = True
        page.views.clear()
        if page.route=='/':
            ini()
            page.views.append(
                ft.View(
                    '/',
                    [
                        ininin(),
                    ],
                )
            )
        if page.route=='/score':
            g_loading.visible = True
            page.views.append(
                ft.View(
                    '/score',
                    [
                        barbar,
                    ],
                    vertical_alignment='center',
                    horizontal_alignment='center',
                    scroll='auto',
                )
            )
            get_bar()
            g_loading.visible = False
        if page.route=='/locate':
            hole_list.controls.clear()
            tttt = th.Thread(target=main_hole,daemon=True,args=[2])
            tttt.start()
            page.views.append(
                ft.View(
                    '/locate',
                    [
                        barbar,
                        hole_init(),
                    ],
                )
            )
        if page.route=='/fav':
            hole_list.controls.clear()
            ttt = th.Thread(target=main_hole,daemon=True,args=[1])
            ttt.start()
            page.views.append(
                ft.View(
                    '/fav',
                    [
                        barbar,
                        hole_init(),
                    ],
                )
            )
        if page.route=='/home':
            hole_list.controls.clear()
            tt = th.Thread(target=main_hole,daemon=True)
            tt.start()
            page.views.append(
                ft.View(
                    '/home',
                    [
                        barbar,
                        hole_init(),
                    ],
                )
            )
        if page.route == "/login":
            page.views.append(
                ft.View(
                    '/login',
                    [
                        ft.Text(value='Welcome',size = 40,weight=ft.FontWeight.W_300),
                        ft.Text(value='Please Identify Yourself',size = 20,weight=ft.FontWeight.W_300),
                        tlogin1,
                        tlogin2,
                        cblogin,
                        ft.FilledButton(
                            text='login',
                            width=250,
                            on_click=login
                        ),
                    ],
                    horizontal_alignment='center',
                    vertical_alignment='center',
                )
            )
        if page.route == "/setting":
            g_loading.visible = False
            page.views.append(
                ft.View(
                    '/setting',
                    [
                        barbar,
                        ft.Text('Settings',style=ft.TextThemeStyle.DISPLAY_MEDIUM,weight=ft.FontWeight.W_400,height=75),
                        ft.Row(
                            [
                                ft.Text('Theme mode',size=20),
                                ft.Dropdown(
                                    on_change=select_theme_mode,
                                    label = 'Theme Mode',
                                    options=[
                                        ft.dropdown.Option('light'),
                                        ft.dropdown.Option('dark'),
                                    ],
                                    value = page.client_storage.get('theme_mode'),
                                    width=200,
                                ),
                            ]
                        ),
                        ft.Column(
                            [
                                ft.Text('Opacity',size=20),
                                ft.Slider(
                                    value=page.client_storage.get('opacity')*100,
                                    min=40,max=100,divisions=24,
                                    label='{value}%',
                                    on_change=slider_changed,
                                    width=600,
                                )
                            ],
                        ),
                        ft.Column(
                            [
                                ft.Text('Number of Holes You want to see each time',size=20),
                                ft.Slider(
                                    value=page.client_storage.get('loading'),
                                    min=25,max=300,divisions=11,
                                    label='{value}',
                                    on_change=lambda e: page.client_storage.set('loading',e.control.value),
                                    width=600,
                                )
                            ],
                        ),
                        ft.Column(
                            [
                                ft.Text('Main Text Size',size=20),
                                ft.Slider(
                                    value=page.client_storage.get('size'),
                                    min=10,max=20,divisions=10,
                                    label='{value}',
                                    on_change=lambda e: page.client_storage.set('size',e.control.value),
                                    width=600,
                                )
                            ],
                        ),
                        ft.Row(
                            [
                                ft.Text('Main Text weight',size=20),
                                ft.Dropdown(
                                    on_change=lambda e: page.client_storage.set('weight',e.control.value),
                                    label = 'Font Weight',
                                    options=[
                                        ft.dropdown.Option('normal'),
                                        ft.dropdown.Option('bold'),
                                        ft.dropdown.Option('w100'),
                                        ft.dropdown.Option('w200'),
                                        ft.dropdown.Option('w300'),
                                        ft.dropdown.Option('w400'),
                                        ft.dropdown.Option('w500'),
                                        ft.dropdown.Option('w600'),
                                        ft.dropdown.Option('w700'),
                                        ft.dropdown.Option('w800'),
                                        ft.dropdown.Option('w900'),
                                    ],
                                    value = page.client_storage.get('weight'),
                                    width=200,
                                ),
                            ]
                        ),
                        ft.Row(
                            [
                                ft.FilledButton("Save",on_click=lambda _: page.go('/home'),width=200),
                                ft.FilledButton("Restore Default Settings",on_click=restore,width=200),
                            ]
                        ),
                    ],
                )
            )
        if page.route=='/about':
            g_loading.visible = False
            page.views.append(
                ft.View(
                    '/about',
                    [
                        barbar,
                        ft.Container(
                            content = ft.Markdown(
                                about_md,
                                selectable=True,
                                extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                                on_tap_link=lambda e: page.launch_url(e.data),
                                scale=1.2,
                            ),
                            margin=ft.margin.only(bottom=200,top=200),
                            width=700,
                        ),
                    ],
                    scroll='auto',
                    horizontal_alignment='center',
                )
            )
        page.update()

    page.title = 'HHHHHHH'
    page.on_resize = page_resize

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    page.scroll = "auto"
    page.window_min_height = 500
    page.window_min_width = 700
    page.go(page.route)
    # page.go('/score')

ft.app(target=main)