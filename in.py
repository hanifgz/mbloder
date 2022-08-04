# Aplikasi Parkir #
__Author__ = 'Novi Cahyo R'

import RPi.GPIO as GPIO
import MySQLdb as mdb
import datetime
from time import sleep
import pygame.mixer
import pygame.camera
import sys
import subprocess
import serial
import binascii
import logging
import ConfigParser
from escpos import *
from reader import *
import subprocess
import os.path
import random

inpLoop1 = 22
inpLoop2 = 24
inpTombol = 26
outLoop1 = 23
outLoop2 = 25
outTombol = 27
openGate = 16


def __init__():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    inp_ = [inpLoop1, inpLoop2, inpTombol]  # Loop1,Loop2,Tombol
    # Loop1,Loop2,Tombol,Opengate
    out_ = [outLoop1, outLoop2, outTombol, openGate]
    for loop in inp_:
        GPIO.setup(loop, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    for loop in out_:
        GPIO.setup(loop, GPIO.OUT, initial=GPIO.HIGH)

    subprocess.call(['amixer', 'sset', 'PCM,0', '100%'], shell=False)
    subprocess.call(['mount', '-a'], shell=False)
    if (Screen == True):
        print('Screen')
        subprocess.call(['./omx.sh'], shell=False)
    pygame.mixer.init(44100, -16, 2, 1024)
    pygame.camera.init()
    thermal.hw('INIT')


def getField(sql):
    rslt = ''
    with conn:
        rs = conn.cursor()
        rs.execute(sql)
        rslt = rs.fetchone()
        rs.close()
        if rslt[0] == None:
            return ''
        return rslt[0]


def dateMysql():
    return getField("select DATE_FORMAT(now(),'%d/%m/%Y %H:%i:%s') as Tgl")


def hourMysql():
    jam_ = getField("select DATE_FORMAT(now(),'%H:%i:%s') as Tgl")
    return datetime.datetime.strptime(jam_, '%H:%M:%S')


def getUID():
    try:
        str = open('/sys/block/mmcblk0/device/cid').read()
        ID_ = str[0:32]
    except:
        ID_ = ''
    return ID_


def getIDD():
    try:
        str = open('/etc/hostname').read()
        IDD_ = str.rstrip('\n')
    except:
        IDD_ = ''
    return IDD_


def getVehc():
    return getField("Select desc3 from parameters where kode='GATE' and topik='PM' and desc1='%s'" % (IDD))


def simpanDB():
    vehc = getVehc()
    iduser = getField(
        "select id from users where sta=0 and web=0 and level=8 and username='%s'" % (IDD))
    pathImage = getField(
        "select desc1 from parameters where kode='COMP' and topik='Path Image'")
    pathImg = pathImage.replace('\\', '\\\\')
    if (camera1 == True and camera2 == True):
        add_trans = "INSERT INTO trans (vehc,timein,pm_user_id,in_img1,in_img2,day) \
    values ('%s',CURRENT_TIMESTAMP(),%s,'%s','%s',CURDATE())" % (vehc, iduser, pathImg, pathImg)
    elif (camera1 == True and camera2 == False):
        add_trans = "INSERT INTO trans (vehc,timein,pm_user_id,in_img1,day) \
    values ('%s',CURRENT_TIMESTAMP(),%s,'%s',CURDATE())" % (vehc, iduser, pathImg)
    elif (camera1 == False and camera2 == True):
        add_trans = "INSERT INTO trans (vehc,timein,pm_user_id,in_img2,day) \
    values ('%s',CURRENT_TIMESTAMP(),%s,'%s',CURDATE())" % (vehc, iduser, pathImg)
    else:
        add_trans = "INSERT INTO trans (vehc,timein,pm_user_id,day) \
    values ('%s',CURRENT_TIMESTAMP(),%s,CURDATE())" % (vehc, iduser)
    with conn:
        rs = conn.cursor()
        rs.execute(add_trans)
        id_ = rs.lastrowid
        rs.close()
        return int(id_)


def cetak(comp, loc, disp, pesan1, pesan2, pesan3, header, footer, id, eject=False):
    compdisp = comp.ljust(39-len(disp))+disp
    # waktu     = dateMysql() #datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    waktu = getField(
        "select DATE_FORMAT(timein,'%%d/%%m/%%Y %%H:%%i:%%s') as Tgl from trans where id=%f" % (id))
    jam = waktu[11:19]  # datetime.datetime.now().strftime('%d-%m-%Y')
    dino = waktu[:10]  # datetime.datetime.now().strftime('%H:%M:%S')
    wektu = dino.ljust(39-len(jam))+jam
    thermal.upsidedown('ON')
    thermal.cpi(1)
    thermal.leftmargin(30, 0)
    if (footer <> ''):
        thermal.text('%39s\n\n' % (footer), align='left', type='U2I')
    if (pesan3 <> ''):
        thermal.text('%s\n' % (pesan3), align='center', type='I')
    if (pesan2 <> ''):
        thermal.text('%s\n' % (pesan2), align='center', type='I')
    thermal.text('%s\n\n' % (pesan1), align='center', type='I')
    thermal.barcode(str(id).zfill(9), 'CODE128-B', 2, 100, '', font='B')
    thermal.text('\n%-39s\n' % (wektu), align='left', type='B')
    thermal.text('%-39s\n' % (compdisp), align='left', type='I')
    thermal.text('%-39s\n' % (loc), align='left', type='BU2')
    if (header == True):
        thermal.text('\nTIKET PARKIR\n\n\n\n\n', align='center',
                     type='B', width=1, height=2)
    thermal.cut()
    if (eject == True):
        print('eject')
        thermal.eject('PRODUCED')


if __name__ == '__main__':
    version = '1.11.0'
    cfg = ConfigParser.RawConfigParser(allow_no_value=True)
    cfg.read('in.conf')
    server = cfg.get('SERVER', 'IP')
    db = cfg.get('SERVER', 'DB')
    port = int(cfg.get('SERVER', 'Port'))
    if (cfg.get('SETTING', 'Screen') == 'True'):
        Screen = True
    else:
        Screen = False
    tm = cfg.get('SETTING', 'Printer').split(',')
    if (tm[0] == 'USB'):
        thermal = printer.Usb(tm[1], int(tm[2], 0), int(
            tm[3], 0), int(tm[4]), int(tm[5], 0), int(tm[6], 0))
        #thermal  = printer.Usb(tm[1],int(tm[2],0),int(tm[3],0))
        if (tm[7] == 'True'):
            eject = True
        else:
            eject = False
        if (tm[8] == 'True'):
            header = True
        else:
            header = False
    elif (tm[0] == 'SERIAL'):
        thermal = printer.Serial(tm[1], tm[2], baudrate=int(tm[3]))
        if (tm[4] == 'True'):
            eject = True
        else:
            eject = False
        if (tm[5] == 'True'):
            header = True
        else:
            header = False
    pagi = cfg.get('SOUNDS', 'Pagi').split(',')
    siang = cfg.get('SOUNDS', 'Siang').split(',')
    sore = cfg.get('SOUNDS', 'Sore').split(',')
    malam = cfg.get('SOUNDS', 'Malam').split(',')
    tunggu = cfg.get('SOUNDS', 'Tunggu')
    ambil = cfg.get('SOUNDS', 'Ambil')
    silahkan = cfg.get('SOUNDS', 'Silahkan')
    # print header
    __init__()
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%d %b %Y %H:%M:%S',
                        filename='log/'+datetime.datetime.now().strftime('%d-%m-%Y')+'.log')
    voice = pygame.mixer.Channel(2)
    reader_ = cfg.get('SETTING', 'Reader').split(',')
    _reader = None
    delayVoicedefault = 250
    delayVoicereader = 5
    delayVoice = delayVoicedefault
    if (reader_[0] == 'Proximity'):
        if (reader_[1] == 'SERIAL'):
            _reader = reader.proximity('ttyUSB0', 9600)
            delayVoice = delayVoicereader
    kamera1 = cfg.get('SETTING', 'Cam1').split(',')
    kamera2 = cfg.get('SETTING', 'Cam2').split(',')
    camera1 = False
    camera2 = False
    if (kamera1[0] == 'USB' or kamera2[0] == 'USB'):
        camList = pygame.camera.list_cameras()
        if (kamera1[0] == 'USB' and len(camList) > 0):
            camera1 = True
            cam1 = pygame.camera.Camera(
                camList[0], (int(kamera1[1]), int(kamera1[2])))
            cam1.start()
        if (kamera2[0] == 'USB' and len(camList) > 0):
            if (len(camList) > 1):
                camera2 = True
                cam2 = pygame.camera.Camera(
                    camList[1], (int(kamera2[1]), int(kamera2[2])))
                cam2.start()
            elif (kamera2[0] <> 'USB'):
                camera2 = True
                cam2 = pygame.camera.Camera(
                    camList[0], (int(kamera2[1]), int(kamera2[2])))
                cam2.start()
    if (kamera1[0] == 'IP' or kamera2[0] == 'IP'):
        if (kamera1[0] == 'IP'):
            camera1 = True
            cam1 = kamera[1]
        if (kamera2[0] == 'IP' and kamera2[0] <> kamera1[0]):
            camera2 = True
            cam2 = kamera2[1]
    pins = [inpLoop1, inpLoop2, inpTombol]
    inputsLast = []
    onProgress = False
    firstVoice = 1
    sound = ''
    thermalSta = thermal.status()
    warn = False
    err = False
    loop1 = False
    tombol = False
    printed = False
    taken = False
    loop2 = False
    lastlog = datetime.datetime.now().strftime('%d-%m-%Y')
    pwd = getUID()
    IDD = getIDD()
    try:
        conn = mdb.connect(server, IDD, pwd, db, port)
        logging.info('Mulai System Masuk Parkir')
        sound = pygame.mixer.Sound('sounds/door.wav')
        voice.play(sound)
        sleep(2)
        jam = hourMysql()
        comp = getField(
            "select desc2 from parameters where kode='COMP' and topik='Nama'")
        lokasi = getField(
            "select desc2 from parameters where kode='COMP' and topik='Lokasi'")
        pesan1 = getField(
            "select desc1 from parameters where kode='MSG' and topik='IN'")
        pesan2 = getField(
            "select desc2 from parameters where kode='MSG' and topik='IN'")
        pesan3 = getField(
            "select desc3 from parameters where kode='MSG' and topik='IN'")
        while True:
            if (thermalSta <> 'X'):
                if (thermalSta == 32 and eject == True and onProgress == False):
                    thermal.eject()
                if (lastlog <> datetime.datetime.now().strftime('%d-%m-%Y')):
                    logging.basicConfig(level=logging.DEBUG,
                                        format='%(asctime)s %(levelname)-8s %(message)s',
                                        datefmt='%d %b %Y %H:%M:%S',
                                        filename='log/'+datetime.datetime.now().strftime('%d-%m-%Y')+'.log')
                    lastlog = datetime.datetime.now().strftime('%d-%m-%Y')
                # if (thermalMsg<>'' and onProgress==False and warn==False):
                # logging.info('Start Parking System')
                # sound=pygame.mixer.Sound('sounds/alarm.wav')
                # warn = True
                # if (voice.get_busy()==False):
                #   voice.play(sound)
                #   firstVoice = 1
                #   err = False
                elif (onProgress == True and loop1 == True and tombol == True):
                    if (thermalSta == 32 and printed == False and eject == True):
                        printed = True
                    elif (eject == False and printed == False):
                        printed = True
                        if (eject == False):
                            GPIO.output(openGate, False)
                            sleep(1)
                            GPIO.output(openGate, True)
                            logging.info('Buka Gate')
                            sound = pygame.mixer.Sound('sounds/'+silahkan)
                            if (voice.get_busy() == True):
                                voice.stop()
                            # voice.play(sound)
                            firstVoice = 1
                            delayVoice = 20000
                            taken = True
                    if (printed == True and thermalSta <> 32 and taken == False and eject == True):
                        logging.info('Taken Tiket Masuk')
                        GPIO.output(openGate, False)
                        sleep(1)
                        GPIO.output(openGate, True)
                        logging.info('Buka Gate')
                        sound = pygame.mixer.Sound('sounds/'+silahkan)
                        if (voice.get_busy() == True):
                            voice.stop()
                        # voice.play(sound)
                        firstVoice = 1
                        delayVoice = 20000
                        taken = True
                # elif (thermalMsg==''):
                #   warn = False
                #   err  = False
                # print thermalSta
                inputs = []
                for pin in pins:
                    inputs.append(GPIO.input(pin))

                if (err == False):
                    sleep(0.3)
                    if (inputs <> inputsLast):
                        print('Loop 1 : %s, Loop2 : %s, Tombol : %s' %
                              (inputs[0], inputs[1], inputs[2]))
                        logging.info('Loop 1 : %s, Loop2 : %s, Tombol : %s' % (
                            inputs[0], inputs[1], inputs[2]))
                        inputsLast = inputs
                        if (onProgress == False):
                            firstVoice = 1
                            jam = hourMysql()

                    if (onProgress == True and loop1 == True and tombol == True and taken == False):
                        thermalSta, thermalMsg = thermal.status()

                    if (inputs[0] == 0 and inputs[1] == 0 and inputs[2] == 0 and onProgress == False):
                        thermalSta = thermal.status()
                        if (warn == False):
                            voice.stop()
                            sound = ''
                    elif (inputs[0] == GPIO.input(outLoop1) and inputs[1] == 0 and inputs[2] == 0 and onProgress == False):
                        if (jam >= datetime.datetime.strptime(pagi[0], '%H:%M:%S') and jam <= datetime.datetime.strptime(pagi[1], '%H:%M:%S')):
                            sound = pygame.mixer.Sound('sounds/'+pagi[2])
                        elif (jam >= datetime.datetime.strptime(siang[0], '%H:%M:%S') and jam <= datetime.datetime.strptime(siang[1], '%H:%M:%S')):
                            sound = pygame.mixer.Sound('sounds/'+siang[2])
                        elif (jam >= datetime.datetime.strptime(sore[0], '%H:%M:%S') and jam <= datetime.datetime.strptime(sore[1], '%H:%M:%S')):
                            sound = pygame.mixer.Sound('sounds/'+sore[2])
                        elif (jam >= datetime.datetime.strptime(malam[0], '%H:%M:%S') and jam <= datetime.datetime.strptime(malam[1], '%H:%M:%S')):
                            sound = pygame.mixer.Sound('sounds/'+malam[2])
                        if (loop1 == False):
                            loop1 = True
                            if (_reader <> None):
                                _reader.flush()
                            firstVoice = 1
                            if (voice.get_busy() == True):
                                voice.stop()
                        elif (_reader <> None):
                            kartu = _reader.read()
                            if (len(kartu) >= 10):
                                print kartu
                                logging.info('Kartu %s' % (kartu))
                                onProgress = True
                                GPIO.output(openGate, False)
                                sleep(1)
                                GPIO.output(openGate, True)
                                logging.info('Buka Gate')
                                sound = pygame.mixer.Sound('sounds/'+silahkan)
                                if (voice.get_busy() == True):
                                    voice.stop()
                                # voice.play(sound)
                                firstVoice = 1
                                delayVoice = 20000
                                taken = True
                    # elif (inputs[0]==0 and inputs[1]==1 and inputs[2]==0 and onProgress==False):
                    elif (inputs[0] == GPIO.input(outLoop1) and inputs[2] == GPIO.input(outLoop2) and onProgress == False):
                        _id = simpanDB()
                        sound = pygame.mixer.Sound('sounds/'+ambil)
                        onProgress = True
                        if (tombol == False):
                            tombol = True
                            firstVoice = 1
                            #delayVoice = 25
                            if (voice.get_busy() == True):
                                voice.stop()
                        cetak(comp.upper(), lokasi.upper(), IDD, pesan1, pesan2,
                              pesan3, header, 'www.rightparking.co.id', id=_id, eject=eject)
                        taken = True
                        #cetakIyos(comp.upper(),'SELAMAT DATANG',IDD,pesan1,pesan2,pesan3,header,'',id=_id,nonota=random.randrange(0,99999,5),eject=eject)
                        logging.info('Cetak Tiket Masuk')
                        if (kamera1[0] == 'USB' or kamera2[0] == 'USB'):
                            if (kamera1[0] == 'USB' and camera1 == True):
                                img_driver = cam1.get_image()
                                pygame.image.save(
                                    img_driver, 'images/' + str(_id) + 'W.jpg')
                                logging.info('Capture Driver')
                            if (kamera2[0] == 'USB' and camera2 == True):
                                img_plat = cam2.get_image()
                                pygame.image.save(
                                    img_driver, 'images/' + str(_id) + 'X.jpg')
                                logging.info('Capture Plat')
                        if (kamera1[0] == 'IP' or kamera2[0] == 'IP'):
                            if (kamera1[0] == 'IP' and camera1 == True):
                                subprocess.call(
                                    ['wget', '-O', 'images/' + str(_id) + 'W.jpg', '-t', '1', cam1], shell=False)
                                logging.info('Capture Driver')
                            if (kamera2[0] == 'IP' and camera2 == True):
                                subprocess.call(
                                    ['wget', '-O', 'images/' + str(_id) + 'X.jpg', '-t', '1', cam2], shell=False)
                                logging.info('Capture Plat')
                    elif (inputs[2] == 0 and onProgress == True and loop2 == False):
                        loop2 = True
                    elif (inputs[2] == 0 and onProgress == True and taken == True and loop2 == True):
                        onProgress = False
                        loop1 = False
                        tombol = False
                        printed = False
                        taken = False
                        loop2 = False
                        if (_reader <> None):
                            delayVoice = delayVoicereader
                        else:
                            delayVoice = delayVoicedefault
                    elif (inputs[0] == 0 and onProgress == True and taken == True and loop2 == False):
                        if (voice.get_busy() == True):
                            voice.stop()
                        sound = ''
                        firstVoice = 1
                else:
                    thermalStatus = thermal.status()

                # print datetime.datetime.now().strftime('%H:%M:%S')
                # print firstVoice,delayVoice
                if (voice.get_busy() == False and sound <> ''):
                    if (firstVoice == 1):
                        voice.play(sound)
                        firstVoice = 2
                    else:
                        if (firstVoice <= delayVoice):
                            firstVoice = firstVoice+1
                        else:
                            firstVoice = 1
            else:
                print('Printer Not Connect')
                logging.error('Printer Not Connect')
                thermal.hw('INIT')
                thermalSta, thermalMsg = thermal.status()
                if (thermalSta == 32 and eject == True):
                    thermal.eject()

    except (KeyboardInterrupt, SystemExit):
        logging.info('Keyboard Interrupt')
        logging.info('End System Masuk Parkir')
    except mdb.Error, e:
        logging.error('%s : %s' % (e.args[0], e.args[1]))
        logging.info('End System Masuk Parkir')
    except (SystemExit):
        GPIO.cleanup()
        if conn:
            conn.close()
        thermal.hw()
        if (_reader <> None):
            _reader.unInit()
        if (kamera1[0] == 'USB' or kamera2[0] == 'USB'):
            if (kamera1[0] == 'USB' and camera1 == True):
                cam1.stop()
            if (kamera2[0] == 'USB' and camera2 == True):
                cam2.stop()
            sound = pygame.mixer.Sound('sounds/shutdown.wav')
            voice.play(sound)
            if (Screen == True):
                subprocess.call(['killall', 'omxplayer.bin'], shell=False)
                subprocess.call(['killall', 'screen'], shell=False)
            sleep(3)
            quit()
