import socket
import sys
import os
from dotenv import load_dotenv


def send_hashcat_params(s):
    try:
        shutdown = input('Voulez-vous arrêter le serveur ? (O/N) : ').capitalize()
        s.sendall(shutdown.encode())
        if shutdown == 'O':
            sys.exit(0)

        cypher_type = int(input('Veuillez entrer le type de chiffrement : '))
        s.sendall(cypher_type.to_bytes(4, byteorder='big'))

        attack_type = int(input('Veuillez entrer le type d\'attaque : '))
        s.sendall(attack_type.to_bytes(4, byteorder='big'))
        print('Paramètres envoyé avec succès au serveur')

    except Exception as e:
        sys.stderr.write(f"Erreur: {e}")
        sys.exit(1)


def send_file_to_server(s, filename:str):
    try:
        with open(filename, 'rb') as file:
            file_data = file.read()
            file_size = len(file_data)
            s.sendall(file_size.to_bytes(4, byteorder='big'))
            s.sendall(file_data)
        print('Fichier envoyé avec succès au serveur')

    except Exception as e:
        sys.stderr.write(f"Erreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    load_dotenv()

    HOST = os.environ.get("SERVER_HOST")
    PORT = int(os.environ.get("SERVER_PORT"))

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            send_hashcat_params(s)

            filename = input('Veuillez entrer le nom du fichier à envoyer : ')
            send_file_to_server(s, filename)

            data = s.recv(4096).decode()
            print("\n\nRésultat Hashcat:")
            
            while data:
                print(data)
                data = s.recv(4096).decode()

        except Exception as e:
            sys.stderr.write(f"Erreur: {e}")
            sys.exit(1)
