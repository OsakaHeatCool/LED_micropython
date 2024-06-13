from machine import Pin  
import time
import neopixel
import array
from easing_functions import * #pypyのライブラリであるがおそらく互換性には問題なし
import math
import random

PIN=4
NUMPIXELS=100#使用するLED数

np = neopixel.NeoPixel(machine.Pin(PIN), NUMPIXELS) 

#関数rgb_to_hsv,hsv_to_rgbは以下のページから引用
#https://github.com/python/cpython/blob/3.12/Lib/colorsys.py

def rgb_to_hsv(r, g, b):
    maxc = max(r, g, b)
    minc = min(r, g, b)
    rangec = (maxc-minc)
    v = maxc
    if minc == maxc:
        return 0.0, 0.0, v
    s = rangec / maxc
    rc = (maxc-r) / rangec
    gc = (maxc-g) / rangec
    bc = (maxc-b) / rangec
    if r == maxc:
        h = bc-gc
    elif g == maxc:
        h = 2.0+rc-bc
    else:
        h = 4.0+gc-rc
    h = (h/6.0) % 1.0
    return h, s, v

def hsv_to_rgb(h, s, v):
    if s == 0.0:
        return v, v, v
    i = int(h*6.0) # XXX assume int() truncates!
    f = (h*6.0) - i
    p = v*(1.0 - s)
    q = v*(1.0 - s*f)
    t = v*(1.0 - s*(1.0-f))
    i = i%6
    if i == 0:
        return v, t, p
    if i == 1:
        return q, v, p
    if i == 2:
        return p, v, t
    if i == 3:
        return p, q, v
    if i == 4:
        return t, p, v
    if i == 5:
        return v, p, q

def rgb2hsv_int(c):
    """
    0~255表記の[r,g,b]を[h(0~360),s(0~100),v(0~100)]に変換する
    
    Parameters
    ----------
    [r,g,b] : int

    Returns
    -------
    [h,s,v] : int
    """
    r,g,b=[x/255.0 for x in c]
    h,s,v=rgb_to_hsv(r, g, b)
    return [int(h*360),int(s*100),int(v*100)]

def hsv2rgb_int(c):
    """
    [h(0~360),s(0~100),v(0~100)]を0~255表記の[r,g,b]値をに変換する
    
    Parameters
    ----------
    [r,g,b] : int

    Returns
    -------
    [h,s,v] : int
    """
    h,s,v=c
    h/=360.0
    s/=100.0
    v/=100.0
    r,g,b=hsv_to_rgb(h,s,v)
    return [int(r*255),int(g*255),int(b*255)]

def mod_loop(t,A):
    return ((t%A)+A)%A

def mod_mirror(t,A):
    cnt=abs(t)//A
    r=mod_loop(t,A)
    return r if cnt%2==0 else (A-r if r!=0 else 0)
 
def fmod_loop(t,A):
    #Aは0以上
    #返り値は0~A
    return math.fmod((math.fmod(t,A)+A),A)

def fmod_mirror(t,A):
    cnt=math.floor(abs(t))//A
    r=math.fmod((math.fmod(t,A)+A),A)
    return r if cnt%2==0 else (A-r if r!=0.0 else 0)

def transformRto0A(t,A,edge_management):
    """
    tが0~Aの範囲外になったときにに、どのような振る舞いをするか
    management="loop"のとき座標0とAがつながっている
    management="mirror"のとき座標0とAで反射する
    それ以外のときは何もしない
    
    Parameters
    ----------
    t:float
    A:float

    Returns
    -------
    t' : float
    """
    if edge_management=='loop':
        return fmod_loop(t,A)
    elif edge_management=='mirror':
        return fmod_mirror(t,A)
    else:
        return t

class light_unit:
    def __init__(self, start: int = 0, end: int = 2**31-1,edge_management:str='loop'):
        self.start = start
        self.end = end
        self.position = 0.0 
        self.range=[0]
        self.rgb=[0,0,0]
        self.edge_management=edge_management

    def position_func(self, t: int):
        raise NotImplementedError
    def range_func(self, t: int):
        raise NotImplementedError
    def color_func(self, t: int,dist: float):
        raise NotImplementedError
    def update(self,t,array_ref):
        if self.start>t:
            return
        
        self.position=transformRto0A(self.position_func(t),1.0,self.edge_management)
    
        if(self.position<0 or self.position>=1):
            self.end=0#範囲外に出たらインスタンスを削除(現状だと中心が外に出ただけで削除されてしまう)

        #現在地を整数で取得
        position_center_int=int(self.position*(NUMPIXELS))
        self.range=self.range_func(t)
        for i in self.range:
            k=position_center_int+i
            if self.edge_management=='loop':
                k=mod_loop(k,NUMPIXELS)
            elif self.edge_management=='mirrror':
                k=mod_mirror(k,NUMPIXELS)

            if k<0 or k>=NUMPIXELS:
                continue
            
            distance_k=(k-position_center_int)/NUMPIXELS
            array_ref[3*k],array_ref[3*k+1],array_ref[3*k+2]=self.color_func(t,distance_k)

        
class beam(light_unit):
    def __init__(self, start: int = 0, end: int = 2**31-1, velocity:float=0,rgb:array=[0,0,0],start_position:float=0.0, width_int:int=1,edge_management='loop'):
        super().__init__(start, end,edge_management)
        self.velocity=(velocity/1000)
        self.rgb=rgb
        self.position=start_position
        self.start_position=start_position
        self.range=[i for i in range(-width_int//2+1,width_int//2+1,1)]#0を中心とした長さwidthの配列
    def position_func(self, t: int):
        return self.start_position+t*(self.velocity)#一次関数的に移動する
    def range_func(self,t: int):
        return self.range#初期値から範囲は変えない
    def color_func(self, t: int,dist: float):
        return self.rgb#初期値から色は変えない

class beam_position_easing(beam):
    def __init__(self,easing_function, start: int = 0, end: int = 2**31-1, velocity:float=0,rgb:array=[0,0,0],start_position:float=0.0, width_int:int=1,edge_management='loop'):
        super().__init__(start, end,velocity,rgb,start_position,width_int,edge_management)
        self.easing_function=easing_function
    def position_func(self, t: int):
        return self.easing_function(transformRto0A(self.start_position+t*(self.velocity),1.0,self.edge_management))

class beam_change_color(beam):
    def __init__(self,colorfunc, start: int = 0, end: int = 2**31-1, velocity:float=0,rgb:array=[0,0,0],start_position:float=0.0, width_int:int=1,edge_management='loop'):
        super().__init__(start, end,velocity,rgb,start_position,width_int,edge_management)
        self.colorfunc=colorfunc
    def color_func(self, t: int,dist: float):
        return self.colorfunc(t,dist)

class entireEffect(light_unit):
    def __init__(self, colorfunc,start: int = 0, end: int = 2**31-1,edge_management:str='loop'):
        super().__init__(start, end,edge_management)
        self.range=range(0,NUMPIXELS)
        self.colorfunc=colorfunc
    def position_func(self, t: int):
        return self.position
    def range_func(self,t: int):
        return range(0,NUMPIXELS)#常に全体
    def color_func(self, t: int,dist: float):
        return self.colorfunc(t,dist)



def setup():
    global start_time_milli
    global RGBTable
    start_time_milli=time.ticks_ms()
    RGBTable=array.array('I',[0] * (3*NUMPIXELS))
    global b
    #start:input=0の時の値　end:input=durationのときの値

    global light_unit_list
    light_unit_list=[]
    argument={
        'start':0,#開始(ms)
        'end':100000,#終了(ms)
        'velocity':1,#一秒にLED列を何周するかで指定(float)
        'start_position':0.5,#初期位置。0以上1未満の範囲で指定
        'width_int':3,#幅,LED何個分か
        'edge_management':'loop',#LEDの両端での処理(loop or mirror or その他)
        'colorfunc':lambda t,dist:hsv2rgb_int([100,100,int(100*(-math.cos(2*math.pi*(t/2))+1)/2)])
        }

    light_unit_list.append(beam_change_color(**argument))

def loop():
    while 1:
        RGBTable = [0 for _ in range(3 * NUMPIXELS)]
        #経過時間(ミリ秒)
        now_time_milli=time.ticks_diff(time.ticks_ms(), start_time_milli)

        for i in range(len(light_unit_list)-1,-1,-1):
            light_unit_list[i].update(now_time_milli,RGBTable)
            if light_unit_list[i].end<=now_time_milli:
                del light_unit_list[i]

        for i in range(NUMPIXELS):
            np[i] = RGBTable[i*3:i*3+3]
        np.write()
        time.sleep_ms(5)

setup()
loop()