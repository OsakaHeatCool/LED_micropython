# LED_utils

## 概要
LEDを光らせます

## 目次
- [必須条件](#必須条件)
- [使い方](#使い方)
- [注意](#注意)
- [その他の例](#その他の例)

### 必要条件
- https://pypi.org/project/easing-functions/
    - https://note.com/kiyo_ai_note/n/n967ed9adbb09
    の"外部ライブラリインストール方法：Thonny"を参考してインストールしました。

## 使い方
関数setup()またはloop()内で、配列light_unit_listにlight_unitから派生したクラスのインスタンスを追加するとLEDを光らせることができます。各インスタンスの生成には辞書形式で引数を指定してください。
startで指定した時刻(ms)までは無効で、end(ms)を超えるとインスタンスは破棄されます。

light_unitから派生したクラス一覧
- beam
    - 一定の幅を持った光が一定の速度で移動します

- beam_position_easing
    - beamの持つ座標(0~1.0)に対してイージング関数を適用します。
- entireEffect
    - LEDテープ全体に適応されるエフェクトを追加します。
    - エフェクトは、colorfuncによって指定します。
    - colorfuncは座標dist(0~1.0)と時刻t(ms)を引数に持ち、返り値に[r,g,b](0~255)を持つような関数です。
![](https://OsakaHeatCool/LED_micropython/edit/main/pic/pic1.png "pic1")
![](https://OsakaHeatCool/LED_micropython/edit/main/pic/pic2.png "pic2")
```python
# beamの追加例
argument={
        'start':300,#開始(ms)
        'end':100000,#終了(ms)
        'velocity':1,#一秒にLED列を何周するかで指定(float)
        'rgb':[100,0,0],#色(int)
        'start_position':0.5,#初期位置。0以上1未満の範囲で指定
        'width_int':3,#幅,LED何個分か
        'edge_management':'loop',#LEDの両端での処理(loop or mirror or その他)
        }

light_unit_list.append(beam_position_easing(**argument))
```
```python
# beam_position_easingの追加例
argument={
        'start':0,#開始(ms)
        'end':100000,#終了(ms)
        'velocity':1,#一秒にLED列を何周するかで指定(float)
        'rgb':[0,100,0],#色(int)
        'start_position':0.0,#初期位置。0以上1未満の範囲で指定
        'width_int':1,#幅,LED何個分か
        'edge_management':'loop',#LEDの両端での処理(loop or mirror or その他)
        'easing_function':CircularEaseInOut(start=0, end=1.0,duration=1.0)#easing_functionに実装されたイージング関数から指定する。
        }

light_unit_list.append(beam_position_easing(**argument))
```
```python
# entireEffectの追加例
argument={
        'start':0,#開始(ms)
        'end':100000,#終了(ms)
        'edge_management':'loop',#LEDの両端での処理(loop or mirror or その他)
        'colorfunc':lambda t,dist:hsv2rgb_int([int(360*(1-math.sin(t/1000))),100,int(100*(1-math.sin(dist*50+t)))])
        }
light_unit_list.append(entireEffect(**argument))
```
## 注意
- テープライトを光らせる位置が被った場合、LEDテープライトの色は後に処理したインスタンスによって上書きされます
## その他の例
```python
argument={
        'start':0,#開始(ms)
        'end':100000,#終了(ms)
        'velocity':1,#一秒にLED列を何周するかで指定(float)
        'rgb':[100,0,0],#色(int)
        'start_position':0.0,#0以上1未満の範囲で指定
        'width_int':1,#幅,LED何個分か
        'edge_management':'loop',#LEDの両端での処理(loop or mirror or その他)
        'easing_function':CircularEaseInOut(start=0, end=1.0,duration=1.0)
    }

    light_unit_list.append(beam_position_easing(**argument))

    argument['easing_function']=LinearInOut(start=0, end=1.0,duration=1.0)
    argument['rgb']=[0,100,0]
    light_unit_list.append(beam_position_easing(**argument))

    argument['easing_function']=QuadEaseInOut(start=0, end=1.0,duration=1.0)
    argument['rgb']=[0,0,100]
    light_unit_list.append(beam_position_easing(**argument))

    argument['easing_function']=CubicEaseInOut(start=0, end=1.0,duration=1.0)
    argument['rgb']=[100,0,100]
    light_unit_list.append(beam_position_easing(**argument))

    argument['easing_function']=QuarticEaseInOut(start=0, end=1.0,duration=1.0)
    argument['rgb']=[100,100,0]
    light_unit_list.append(beam_position_easing(**argument))

    argument['easing_function']=QuinticEaseInOut(start=0, end=1.0,duration=1.0)
    argument['rgb']=[0,100,100]
    light_unit_list.append(beam_position_easing(**argument))

    argument['easing_function']=SineEaseInOut(start=0, end=1.0,duration=1.0)
    argument['rgb']=[0,100,100]
    light_unit_list.append(beam_position_easing(**argument))
```
