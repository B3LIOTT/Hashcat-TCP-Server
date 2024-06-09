import os
import socket
import subprocess
import re
import sys
from logger import *
from dotenv import load_dotenv



def getHashcatParams(conn):
    cypher_type_bytes = conn.recv(4)
    cypher_type = int.from_bytes(cypher_type_bytes, byteorder='big')

    attack_type_bytes = conn.recv(4)
    attack_type = int.from_bytes(attack_type_bytes, byteorder='big')

    return cypher_type, attack_type


def hashcat_exec(conn, cypher_type: int, attack_type: int, hash_file: str, dico: str):
    try:
        file_size_bytes = conn.recv(4)
        file_size = int.from_bytes(file_size_bytes, byteorder='big')

        if file_size > 0:
            with open(hash_file, 'wb') as file:
                remaining_bytes = file_size
                while remaining_bytes > 0:
                    chunk = conn.recv(min(remaining_bytes, 4096))
                    if not chunk:
                        break
                    file.write(chunk)
                    remaining_bytes -= len(chunk)

            basic_info(f'Fichier reçu avec succès et enregistré sous data.txt')
            basic_info('----------Lancement de Hashcat----------\n\n')

            result = subprocess.run(f"hashcat.exe -m {cypher_type} -a {attack_type} "
                                    f"{hash_file} "
                                    f"{dico}",
                                    shell=True, capture_output=True, text=True)

            res = result.stdout
            already_donne_pattern = r"Use --show to display them"
            if re.search(already_donne_pattern, res):
                basic_info('Hash déjà cracké, affichage des résultats...')
                result = subprocess.run(f"hashcat.exe -m {cypher_type} -a {attack_type} "
                                        f"{hash_file} "
                                        f"{dico} --show",
                                        shell=True, capture_output=True, text=True)
            
            res = result.stdout
            print(res)
            res_encoded = res.encode()
            for i in range(0, len(res_encoded), 4096):
                conn.sendall(res_encoded[i:i+4096])

        else:
            error("Taille de fichier reçue nulle")

    except Exception as e:
        error(f'Une erreur est survenue: {e}')
        conn.sendall(b'ERROR')


if __name__ == "__main__":
    load_dotenv()

    HOST = socket.gethostbyname(socket.gethostname())
    PORT = int(os.environ.get("PORT"))

    HASH = os.environ.get("HASH")
    DICO = os.environ.get("DICO")
    HASHCAT_PATH = os.environ.get("HASHCAT_PATH")

    os.chdir(HASHCAT_PATH)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((HOST, PORT))
            s.listen()
            basic_info('Serveur en attente de connexion...')

            while True:
                conn, addr = s.accept()
                with conn:
                    basic_info(f'Connexion établie avec {addr}')
                    cypher_type, attack_type = getHashcatParams(conn)
                    hashcat_exec(conn, cypher_type, attack_type, HASH, DICO)

        except KeyboardInterrupt:
            severe_info('Arrêt du serveur...')
            sys.exit(0)
        except Exception as e:
            error(e)
