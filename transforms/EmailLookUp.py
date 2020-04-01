from maltego_trx.entities import Person, Email, Phrase
from maltego_trx.transform import DiscoverableTransform
from maltego_trx.maltego import UIM_PARTIAL

import re, urllib.request
from html2json import collect
import json
from bs4 import BeautifulSoup


trns={"name": "Nombre",
      "centro": "Centro",
      "area":"Area de Conocimiento",
      "unidad":"Unidad Organizativa",
      "phone": "Teléfono",
      "postaladdress": "Dirección postal",
      "position": "Puesto",
      "office": "Despacho",
      "filiation":"Filiación",
      "web":"Web personal institucional"
      }


class EmailLookUp(DiscoverableTransform):
    """
    Lookup the name associated with a phone number.
    """
    EMAIL_REGEX = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
    @classmethod
    def create_entities(cls, request, response):
        email = request.Value
        try:
            res = EmailLookUp.EMAIL_REGEX.findall(email)
            if len(res) == 0:
                response.addUIMessage(f'This {email} is not a valid email from UM.', messageType=UIM_PARTIAL)
            else:
                email = res[0].split("@")[0]
                match = EmailLookUp.find(email)
                if len(match) == 0:
                    response.addUIMessage("The email given did not match any")    
                else:
                    ent = response.addEntity('um.PersonUM')
                    
                    ent.addProperty('name','Nombre','strict',match[trns["name"]])
                    ent.addProperty('centro','Centro','strict',match[trns["centro"]])
                    ent.addProperty('area','Área de Conocimiento','strict',match[trns["area"]])
                    ent.addProperty('unidad','Unidad Organizativa','strict',match[trns["unidad"]])
                    ent.addProperty('phone','Teléfono','strict',match[trns["phone"]])
                    ent.addProperty('postaladdress','Dirección postal','strict',match[trns["postaladdress"]])
                    ent.addProperty('position','Puesto','strict',match[trns["position"]])
                    ent.addProperty('office','Despacho','strict',match[trns["office"]])
                    ent.addProperty('filiation','Filiación','strict',match[trns["filiation"]])
                    ent.addProperty('filiation','Filiación','strict',email)
                    
        except IOError:
            response.addUIMessage("An error occurred", messageType=UIM_PARTIAL)
            
    
    @staticmethod
    def find(email):
        URL_QUERY="https://www.um.es/atica/directorio/index.php?usuario="+ email + ".RC&lang=0&vista=unidades&search="
        data = None
        req = urllib.request.Request(URL_QUERY)
        resp = urllib.request.urlopen(req)
        
        web = resp.read()
        data = BeautifulSoup(web, 'html5lib')
        person = dict()
        print(URL_QUERY)
        for ch in data.find_all("table", attrs={'class':"infoElem"}):
            for tup in ch.find_all("tr"):
                td = tup.find_all("td")
                if len(td) > 1:    
                    if td[0].text == "Correo electrónico:":
                        #print(td[1])
                        pass
                    elif td[0].text == "Web personal institucional:":
                        tmp =  td[1].find('a').attrs["href"]
                        person[td[0].text] = tmp[:len(tmp)-1]
                    else:
                        person[td[0].text[:len(td[0].text)-1]] = td[1].text
        return person

    
if __name__ == "__main__":
#    EmailLookUp.create_entities(sys.argv, None)
    EmailLookUp.create_entities("felixgm@um.es", None)
    