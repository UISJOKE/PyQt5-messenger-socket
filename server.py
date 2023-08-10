import socket
from threading import Thread


IP = socket.gethostbyname(socket.gethostname())
PORT = 8000
separator_token = "<SEP>"

client_sockets = set()

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((IP, PORT))

s.listen(5)


def procces():

	def listen_for_client(cs):
		while True:
			try:
				msg = cs.recv(1024).decode()
			except Exception as e:
				print(f'[*] Error: {e}')
				client_sockets.remove(cs)
			else:
				msg = msg.replace(separator_token, ": ")

			for client_socket in client_sockets:
				client_socket.send(msg.encode())

	while True:
		print('Запущен!')
		client_socket, client_address = s.accept()
		print(f'[*] {client_address} подключен.')

		client_sockets.add(client_socket)

		t = Thread(target=listen_for_client, args=(client_socket,))
		t.daemon = True
		t.start()
