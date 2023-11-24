# LED68 : A TLC59116 LED module for MONAC-002/MONAC-003 driver library
# (C)2021-2023 @kani7     https://github.com/kani7/LED68
# forked from RB-TLC59116 https://github.com/robs-code/TLC59116-RPi

# TLC59116のレジスタ番地
TLC_PWM_BASE        = 0x02  # PWM0(LED0の輝度設定)レジスタが0x02で、PWM15が0x11
TLC_GROUP_PWM       = 0x12  # グループPWMのデューティ比
TLC_GROUP_FREQ      = 0x13  # グループPWMの周波数
TLC_LED_OUTPUT_BASE = 0x14  # LEDOUT0(LED0～3の点灯設定)レジスタが0x14で、LEDOUT3(LED12～15の点灯制御)が0x17
TLC_IREF            = 0x1C  # IREFレジスタ
TLC_ERROR_FLAG1     = 0x1D
TLC_ERROR_FLAG2     = 0x1E

TLC_IREF_MAX     = 0x7f
TLC_IREF_DEFAULT = 0x3f
#TLC_RESET        = 0x6B

# LEDOUT0～LEDOUT3がとり得る値
# LED3,7,11,15は未接続なので上位2bitは常に0
LED_OFF   = 0b00000000
LED_ON    = 0b00101010  # 実際には点灯ではなくPWM制御に従う
LED_GROUP = 0b00111111  # 調色した状態でグループPWMに従って点滅

class LED68:

  # いわゆるコンストラクタ的な
  #   引数  address :I2Cスレーブアドレス
  #         bus     :I2Cバス(別途smbusライブラリで得た値を用いる)
  #         iref    :IREFレジスタ(0x1C番地)の値
  #   警告  IREFレジスタの値は0x7Fを超えてはならない 推奨は0x3F以下
  #         0x3Fを超えた値を設定するのであれば、
  #         setColor()のRGB各輝度の合計が255以下になるようディレーティングすること
  def __init__(self, address, bus, iref=TLC_IREF_DEFAULT):
    self.TLC_ADDR = address
    self.bus = bus
    if iref > TLC_IREF_MAX :
      print("WARNING: IREF must be under " + hex(TLC_IREF_MAX) + ". Using " + hex(TLC_IREF_DEFAULT) + " insted.")
      self.iref = TLC_IREF_DEFAULT
    else:
      self.iref = iref
    self.writeToDevice(TLC_IREF, self.iref)
    self.turnOffAllLEDs
    self.ERR_FLAG = 0xFFFF
    self.groupMode = 0

  # I2C経由でレジスタに値を書き込む
  #   引数 reg  :レジスタの番地
  #        val  :レジスタに書き込む値
  def writeToDevice(self, reg, val):
    try: 
      self.bus.write_byte_data(self.TLC_ADDR, reg, val)
    except IOError:
      print("Could not write to device " + hex(self.TLC_ADDR))

  # I2C経由でレジスタの値を読み出す
  #   引数 reg  :レジスタの番地
  def readFromDevice(self, reg):
    try:
      return self.bus.read_byte_data(self.TLC_ADDR, reg)
    except IOError:
      return -1

  # LEDの状態を変更する
  #   引数 LED  :基板上のLED番号(1～4)
  #              レジスタ番号やTLC591xxの端子名OUTx(LEDx)の事ではないので注意
  # --------------------------------------------------------
  def modifyLEDOutputState(self, LED, state) :
    self.writeToDevice(TLC_LED_OUTPUT_BASE + LED -1, state)

  def LEDOff(self, LED):
    self.modifyLEDOutputState(LED, LED_OFF)

  def LEDOn(self, LED):
    self.modifyLEDOutputState(LED, LED_ON)

  def LEDGroup(self, LED):
    self.modifyLEDOutputState(LED, LED_GROUP)
  # --------------------------------------------------------

  # LEDの色を調整する
  #   引数 LED    :基板上のLED番号(1～4)
  #        red    :赤の輝度(0～255)
  #        green  :緑の輝度(0～255)
  #        blue   :青の輝度(0～255)
  #   備考 全てを最大輝度にすると廃熱が追いつかない懸念があるため
  #        ディレーティングを考慮すること
  def setColor(self, LED, red, green, blue):
    if (self.iref > 0x3f) and ((red + green + blue) > 255) :
      print("WARNING: You should consider derating for LED" + str(LED))
    self.writeToDevice(TLC_PWM_BASE + (LED -1) * 4, red)
    self.writeToDevice(TLC_PWM_BASE + (LED -1) * 4 +1, green)
    self.writeToDevice(TLC_PWM_BASE + (LED -1) * 4 +2, blue)

  # 点滅周期とデューティ比を設定する
  #   引数 freq       :GRPFREQ(0x13番地)の値
  #                   (GRPFREQ + 1)/24 秒が点滅周期になる、すなわち
  #                   0x00 を入れると41msec間隔で点滅(24Hz)
  #                   0xFF を入れると10.73sec間隔で点滅する
  #        dutyCycle :GRPPWM(0x12番地)の値
  #                   GRPPWM/256 が点灯時間の比率(デューティー比)となる、すなわち
  #                   0x00 を入れると消灯したままになる
  #                   0xFF を入れると99.6%の期間は点灯し、残り0.4%の期間は消灯する
  #   備考 X680x0実機ではRTCの仕様により、
  #       POWER LEDは1Hzか16Hzのいずれかで点滅する
  def setGroupBlink(self, freq, dutyCycle):
    self.writeToDevice(TLC_GROUP_PWM, dutyCycle)
    self.writeToDevice(TLC_GROUP_FREQ, freq)

  # TLC59116のエラー処理関連
  # --------------------------------------------------------
  def clearErrors(self):
    self.writeToDevice(0x01, 0xA0)
    self.writeToDevice(0x01, 0x20)

  def checkErrors(self):
    flag1 = self.readFromDevice(TLC_ERROR_FLAG1)
    flag2 = self.readFromDevice(TLC_ERROR_FLAG2)
    self.ERR_FLAG = (flag2 << 8) + flag1
    if self.ERR_FLAG == 0xFFFF:
      return False
    return True

  def reportErrors(self):
    if self.ERR_FLAG == 0xFFFF:
      print("No errors detected.")
      return False
    elif self.ERR_FLAG == -0x101:
      print("Could not read from device: "+ hex(self.TLC_ADDR)) 
    else:
      for i in range(0,16):
        if (not((self.ERR_FLAG >> i) & 0x1)):
          print("Device " + hex(self.TLC_ADDR)+ ": LED" + str(i) + " disconnected/overheated")
    self.clearErrors()
  # --------------------------------------------------------

  # 初期化関連
  # --------------------------------------------------------
  def enable(self):
    self.writeToDevice(0x00, 0x01)          # start OSC, enables auto-increment and all-call-address
    self.writeToDevice(TLC_IREF,self.iref)  # limits LED current
    self.writeToDevice(0x01, 0x20)          # blink mode

  def resetDriver(self):
    self.turnOffAllLEDs()
    self.enable()

  def turnOffAllLEDs(self):
    self.LEDOff(1)
    self.LEDOff(2)
    self.LEDOff(3)
    self.LEDOff(4)

  # resetDriver()を推奨
  # 以下の関数では自身以外のTLC591xxを巻き込んでリセットしてしまうのに加え、
  # 自身以外のIREFを再設定できないため非推奨
  def resetAllTLCs(self):
    self.bus.write_byte_data(0x6B, 0xA5, 0x5A)
    self.writeToDevice(TLC_IREF,self.iref)
