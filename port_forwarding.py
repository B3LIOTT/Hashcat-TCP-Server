import upnpy
from logger import *
import socket
from time import sleep


def find_router_by_ip():
    upnp = upnpy.UPnP()
    
    # Découverte des appareils UPnP sur le réseau local
    devices = upnp.discover()
    basic_info(f'{len(devices)} appareils UPnP détectés')

    if len(devices) == 0:
        return None
    
    device = devices[0]
    basic_info(f"Appareil UPnP choisi: {device}")

    return device['WANIPConn1']

def forward_port(port: int):
    service = find_router_by_ip()
    if service is None:
        raise Exception(f"Aucun routeur UPnP trouvé")

    # Obtenir l'adresse IP locale
    local_ip = socket.gethostbyname(socket.gethostname())

    external_port = port
    internal_port = port
    protocol = 'TCP'
    description = 'Hashcat port forwarding'

    try:
        service.AddPortMapping(NewRemoteHost='',
                               NewExternalPort=external_port,
                               NewProtocol=protocol,
                               NewInternalPort=internal_port,
                               NewInternalClient=local_ip,
                               NewEnabled=1,
                               NewPortMappingDescription=description,
                               NewLeaseDuration=3600)
        basic_info(f"Redirection de port ajoutée: {external_port} -> {local_ip}:{internal_port} ({protocol})")
    
    except Exception as e:
        raise Exception(f"Erreur lors de l'ajout de la redirection de port: {e}")

    # Vérification
    try:
        mapping = service.GetSpecificPortMappingEntry(NewRemoteHost='',
                                                      NewExternalPort=external_port,
                                                      NewProtocol=protocol)
        basic_info(f"Redirection de port vérifiée: {mapping}")
    except Exception as e:
        raise Exception(f"Erreur lors de la vérification de la redirection de port: {e}")
    
    return service, external_port, protocol
    

def remove_forwarding(service, external_port: int, protocol: str):
    try:
        service.DeletePortMapping(NewRemoteHost='',
                                  NewExternalPort=external_port,
                                  NewProtocol=protocol)
        basic_info(f"Redirection de port supprimée: {external_port} ({protocol})")
    except Exception as e:
        raise Exception(f"Erreur lors de la suppression de la redirection de port: {e}")

