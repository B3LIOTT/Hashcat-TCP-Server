import socket
import sys
import os
from dotenv import load_dotenv


def send_hashcat_params(s, cypher_type:int, attack_type:int):
    try:
        s.sendall(cypher_type.to_bytes(4, byteorder='big'))
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

    HOST = os.environ.get("CLIENT_HOST")
    PORT = int(os.environ.get("CLIENT_PORT"))

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        cypher_type = input('Veuillez entrer le type de chiffrement : ')
        attack_type = input('Veuillez entrer le type d\'attaque : ')
        try:
            s.connect((HOST, PORT))
            send_hashcat_params(s, int(cypher_type), int(attack_type))

            filename = input('Veuillez entrer le nom du fichier à envoyer : ')
            send_file_to_server(s, filename)

            data = s.recv(2048).decode()
            print("Résultat Hashcat:")
            print(data)

        except Exception as e:
            sys.stderr.write(f"Erreur: {e}")
            sys.exit(1)
