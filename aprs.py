from dotenv import load_dotenv
import pyfiglet
import threading
import os
import socket
import time

stop_flag = False

def createDatabase(CALLSIGN, SSID, SERVER, LAT, LON, TABLE, SYMBOL, COMMENT, INTERVAL):
    with open('.env', 'w') as f:
        f.write(f"CALLSIGN={CALLSIGN}\n")
        f.write(f"SSID={SSID}\n")
        f.write(f"SERVER={SERVER}\n")
        f.write(f"LAT={LAT}\n")
        f.write(f"LON={LON}\n")
        f.write(f"SYMBOL_TABLE={TABLE}\n")
        f.write(f"SYMBOL={SYMBOL}\n")
        f.write(f"COMMENT={COMMENT}\n")
        f.write(f"INTERVAL={INTERVAL}")

def CreateDtForm():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Create User APRS Config")
    callsign = input("callsign>> ")
    ssid = input("ssid>> ")
    comment = input("comment>> ")
    symboltable = input("symbol table>> ")
    symbol = input("symbol>> ")
    latitude = float(input("latitude>> "))
    longitude = float(input("longitude>> "))
    interval = int(input("interval (60-900)>>"))
    server = int(input("Servers:<\n1. Worldwide\n2. North America\n3. South America\n4. Europe/Africa\n5. Asia\n6. Oceania\n>> "))
    print("--------------------")
    print(f"Callsign: {callsign}-{ssid}")
    if server is 1: print("Server Worldwide: rotate.aprs2.net")
    elif server is 2: print("Server North America: noam.aprs2.net")
    elif server is 3: print("Server South America: soam.aprs2.net")
    elif server is 4: print("Server Europe/Africa: euro.aprs2.net")
    elif server is 5: print("Server Asia: asia.aprs2.net")
    elif server is 6: print("Server Oceania: aunz.aprs2.net")
    print(f"Comment: {comment}")
    print(f"latitude: {latitude}")
    print(f"longitude: {longitude}")
    print(f"Symbol: {symboltable} {symbol}")
    print(f"Interval: {interval}")
    save = input("Save to database? (Y/N) >> ")
    if save == "Y":
        createDatabase(callsign, ssid, server, latitude, longitude, symboltable, symbol, comment, interval)

def sendAprsPosition(serverId, callsign, ssid, passcode, latitude, longitude, symbol_table, symbol, comment="Python via APRS"):
    server = "rotate.aprs2.net"
    if serverId is 1: server = "rotate.aprs2.net"
    elif serverId is 2: server = "noam.aprs2.net"
    elif serverId is 3: server = "soam.aprs2.net"
    elif serverId is 4: server = "euro.aprs2.net"
    elif serverId is 5: server = "asia.aprs2.net"
    elif serverId is 6: server = "aunz.aprs2.net"
    else: server = "rotate.aprs2.net"

    port = 14580

    lat_str = aprs_lat_format(latitude)
    lon_str = aprs_lon_format(longitude)
    
    aprs_position = f"{callsign}-{ssid}>APRS,TCPIP*:!{lat_str}{symbol_table}{lon_str}{symbol}{comment}\n"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server, port))
        
        # APRS sunucusuna oturum aç
        login_cmd = f"user {callsign} pass {passcode} vers PythonClient 1.0\n"
        s.sendall(login_cmd.encode('utf-8'))

        # Konum bilgisini gönder
        s.sendall(aprs_position.encode('utf-8'))
        
        # Sunucudan gelen yanıtı al
        response = s.recv(1024).decode('utf-8')
        response = response.rstrip("\n")
        print(f"Running, Server response: {response}")
        
def aprs_lat_format(latitude):
    lat_deg = int(abs(latitude))
    lat_min = (abs(latitude) - lat_deg) * 60
    direction = 'N' if latitude >= 0 else 'S'
    return f"{lat_deg:02d}{lat_min:05.2f}{direction}"

def aprs_lon_format(longitude):
    lon_deg = int(abs(longitude))
    lon_min = (abs(longitude) - lon_deg) * 60
    direction = 'E' if longitude >= 0 else 'W'
    return f"{lon_deg:03d}{lon_min:05.2f}{direction}"

def passcode_convert(callsign):
    assert isinstance(callsign, str)

    callsign = callsign.split('-')[0].upper()

    code = 0x73e2
    for i, char in enumerate(callsign):
        code ^= ord(char) << (8 if not i % 2 else 0)

    return code & 0x7fff

def check_for_exit():
    global stop_flag
    while not stop_flag:
        user_input = input("\nPress 'q' to stop APRS.\n")
        if user_input == 'q':
            stop_aprs()

def loopSharePos():
    global stop_flag
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Start APRS...")
    load_dotenv()
    INTERVAL = int(os.getenv('INTERVAL'))
    if INTERVAL < 60: INTERVAL = 60
    elif INTERVAL > 900: INTERVAL = 900

    SERVER = os.getenv('SERVER')
    CALLSIGN = os.getenv('CALLSIGN')
    SSID = os.getenv('SSID')
    LAT = float(os.getenv('LAT'))
    LON = float(os.getenv('LON'))
    SYMBOL_TABLE = os.getenv('SYMBOL_TABLE')
    SYMBOL = os.getenv('SYMBOL')
    COMMENT = os.getenv('COMMENT')
    PASSCODE = passcode_convert(CALLSIGN)

    elapsed_time = INTERVAL
    while not stop_flag:
        if elapsed_time >= INTERVAL:
            os.system('cls' if os.name == 'nt' else 'clear')
            sendAprsPosition(SERVER, CALLSIGN, SSID, PASSCODE, LAT, LON, SYMBOL_TABLE, SYMBOL, COMMENT)
            print("Press 'q' + 'enter' to stop APRS.")
            elapsed_time = 0
        time.sleep(1)
        elapsed_time += 1

def start_aprs():
    global stop_flag
    stop_flag = False
    
    # APRS işlemine başlamak için iş parçacığı
    aprs_thread = threading.Thread(target=loopSharePos)
    aprs_thread.start()
    
    # Çıkış için kontrol yapan iş parçacığı
    exit_thread = threading.Thread(target=check_for_exit)
    exit_thread.start()

    # APRS ve çıkış iş parçacıklarını bekle
    aprs_thread.join()
    exit_thread.join()

def stop_aprs():
    global stop_flag
    stop_flag = True

while True:
    os.system('cls' if os.name == 'nt' else 'clear')
    ascii_art = pyfiglet.figlet_format("DESK APRS")
    print(ascii_art, end="")
    print("Developer by Uğur ALTINSOY")
    print("1. Start APRS")
    print("2. Create Database")
    print("3. Delete Database")
    print("4. Exit App")

    operator = int(input(">> "))

    if operator is 1:
        if os.path.exists('.env'): aprs_thread = start_aprs()
    elif operator is 2: CreateDtForm()
    elif operator is 3:
        delete = input("Delete to database? (Y/N) >> ")
        if delete == "Y" and os.path.exists('.env'):
            os.remove('.env')
            print("Successfully deleted to database")
    elif operator is 4: 
        stop_aprs()
        break







