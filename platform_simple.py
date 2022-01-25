'''
Для управления платформой используется микроконтроллер Arduino Uno с залитой туда прошивкой 
GRBL v1.1 (https://github.com/gnea/grbl/wiki) + данный Python модуль, который непосредственно взаимодействует 
с микроконтроллером через последовательный порт.
'''


import serial, sys
import time


ser_platform = None


def connect(port_id='COM1', baud=115200):
    global ser_platform
    ser_platform = serial.Serial(port=port_id, baudrate=baud, timeout=2)
    ser_platform.write("\r\n\r\n".encode())
    time.sleep(2)   # Wait for grbl to initialize 
    ser_platform.flushInput()  # Flush startup text in serial input
    print('Platform: ready')


def disconnect():
    global ser_platform
    ser_platform.close()
    ser_platform = None
    print('Platform: disconnected')


def send_data(s=''):
    ''' 
    вспомогательная функция. Получает на вход строку для отправки в плату, преообразует ее в последовательность байтов, 
    и отправляет в плату через последовательный порт
    '''
    global ser_platform
    grbl_out = None
    if ser_platform!= None:
        s_b = (s + '\n').encode() # преобразуем строку в последовательность байтов
        ser_platform.write(s_b) # Send g-code block to grbl
        grbl_out = ser_platform.readline().decode('UTF-8').strip() # Wait for grbl response with carriage return
        ser_platform.flushInput() # !!!_bad
    else:
        print('Platform: No connection to board')
    return grbl_out


def set_position_g(y = 0, speed = 300):
    '''
    движение через G команду. Не используем пока
    '''
    return send_data('G01 Y{} F{}'.format(y, speed))


def set_position(y = 0, speed = 300, wait = False):
    '''
    движение через $J= команду. Используем, т.к. ее легко остановить в нужный момент
    '''
    if wait == False:
        return send_data('$J=Y{} F{}'.format(y, speed))
    else:
        send_data('$J=Y{} F{}'.format(y, speed))
        return wait_move_end()


def get_status():
    '''
    получает информацию о сотоянии платы. Более подробная информация по полям ответа тут: 
    https://github.com/gnea/grbl/wiki/Grbl-v1.1-Interface#real-time-status-reports
    '''
    return send_data('?')


def get_position():
    '''
    запрашивает текущий статус платы и вытаскивает оттуда коррдинату Y (единственную, которую используем)
    '''
    answ = send_data('?')
    try:
        answ = answ.split('|')[1].split(',')[1]
        answ = float(answ)
    except:
        answ = None

    return answ


def get_machine_state():
    '''
    запрашивает текущий статус платы и вытаскивает оттуда состояние контроллера/машины. 
    Варианты состояний: Idle (простаивает/не движется), Run, Hold, Jog (движется в режиме JOG), Alarm, Door, Check, Home, Sleep

    '''
    answ = send_data('?')
    try:
        answ = answ.split('|')[0].strip('<')
    except:
        answ = ''

    return answ


def stop_moving():
    '''
    останавливает движение платформы контроллируемо и плавно (в отличии от аварийного останова). 
    Надо немного подождать, перед запросом координат (ждем пока платформа остановится).
    '''
    return send_data(chr(133))


def wait_move_end(timeout = 5):
    '''
    ждет остановки движения (не дольше, чем указано в параметре timeout). 
    Запрашивает в цикле текущее состояние платы, пока не получит 'Idle'
    '''
    start_time = time.time()

    while (get_machine_state() != 'Idle') and (time.time() - start_time < timeout):
        time.sleep(0.3)
    
    
    return 'move end or timeout'



if __name__ == "__main__":
    '''
    код ниже выполняется, только если данный файл запускается сам по себе отдельно, а не подключается как библиотека
    '''
    print('dsfd')

    connect('COM10')

    print(get_position())

    set_position(30, 500, True)

    print(get_position())
