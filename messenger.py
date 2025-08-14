import argparse
import socket
import threading
import os
import sys
import time

# ------------------------- Общие функции -------------------------

def clear_screen():
    """Очистка экрана в зависимости от ОС"""
    os.system('cls' if os.name == 'nt' else 'clear')

# ------------------------- Серверная часть -------------------------

def start_server(host, port):
    """Запуск сервера мессенджера"""
    clients = {}
    
    def handle_client(client_socket, address):
        nickname = client_socket.recv(1024).decode()
        clients[client_socket] = nickname
        print(f"[+] {nickname} подключился ({address[0]})")
        broadcast(f"{nickname} вошёл в чат!".encode(), sender=None)
        
        while True:
            try:
                message = client_socket.recv(1024)
                if not message:
                    break
                broadcast(message, sender=client_socket, nickname=nickname)
            except:
                break

        del clients[client_socket]
        client_socket.close()
        broadcast(f"{nickname} покинул чат.".encode(), sender=None)

    def broadcast(message, sender=None, nickname=""):
        """Отправка сообщения всем клиентам"""
        if nickname:
            formatted_msg = f"[{nickname}] {message.decode()}".encode()
        else:
            formatted_msg = message
            
        for client in list(clients.keys()):
            if client != sender:
                try:
                    client.send(formatted_msg)
                except:
                    pass

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(10)
    
    print(f"════════════════════════════════════════")
    print(f"🚀 Сервер запущен на {host}:{port}")
    print(f"════════════════════════════════════════")
    print("Ожидание подключений... (Ctrl+C для выхода)")
    
    try:
        while True:
            client_socket, address = server.accept()
            thread = threading.Thread(
                target=handle_client, 
                args=(client_socket, address),
                daemon=True
            )
            thread.start()
    except KeyboardInterrupt:
        print("\nСервер остановлен")
        server.close()

# ------------------------- Клиентская часть -------------------------

def start_client(server_host, server_port):
    """Запуск клиента мессенджера"""
    def receive_messages():
        """Поток для получения сообщений"""
        while True:
            try:
                message = client_socket.recv(1024).decode()
                print(f"\r{message}\n> ", end="")
            except:
                print("\r🔌 Соединение с сервером потеряно")
                os._exit(1)

    clear_screen()
    print("════════════════════════════════════════")
    print("       🚀 ПРОСТОЙ МЕССЕНДЖЕР")
    print("════════════════════════════════════════")
    
    nickname = input("Введите ваш ник: ")
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect((server_host, server_port))
        client_socket.send(nickname.encode())
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return

    receive_thread = threading.Thread(target=receive_messages, daemon=True)
    receive_thread.start()
    
    print("════════════════════════════════════════")
    print("Подключено к серверу! (exit для выхода)")
    print("════════════════════════════════════════")
    
    while True:
        try:
            message = input("> ")
            if message.lower() == 'exit':
                break
            client_socket.send(message.encode())
        except KeyboardInterrupt:
            break

    client_socket.close()
    print("Отключено от сервера")

# ------------------------- Основная программа -------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simple Messenger')
    parser.add_argument('--server', action='store_true', help='Run in server mode')
    parser.add_argument('--client', action='store_true', help='Run in client mode')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Server host (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=65432, help='Server port (default: 65432)')
    
    args = parser.parse_args()
    
    if args.server:
        start_server(args.host, args.port)
    elif args.client:
        server_host = input("Введите IP сервера: ") if not args.host else args.host
        server_port = int(input("Введите порт сервера: ")) if not args.port else args.port
        start_client(server_host, server_port)
    else:
        print("Выберите режим запуска:")
        print("  Сервер: python messenger.py --server")
        print("  Клиент: python messenger.py --client")
        print("\nДополнительные параметры:")
        print("  --host HOST (серверный IP)")
        print("  --port PORT (номер порта)")
