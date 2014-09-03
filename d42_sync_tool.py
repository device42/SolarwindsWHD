import sys
import os
import json
import hashlib
import codecs
import base64
import requests
import ConfigParser
from urllib import quote
from datetime import datetime

DIR = os.path.dirname(__file__)
CONFIG_FILE = os.path.join(DIR, 'settings.cfg')



class Logger():
    def __init__(self, ):
        pass


    def writer(self, msg):    
        with codecs.open(LOGFILE, 'a', encoding = 'utf-8') as f:
            f.write(msg.strip()+'\r\n')
        if DEBUG == 'True':
            try:
                print msg
            except:
                print msg.encode('ascii', 'ignore') + ' # < non-ASCII chars detected! >'

    

class Uploader():
    def upload_data(self, path, data):
        #url = SW_URL+':8081/helpdesk/WebObjects/Helpdesk.woa/ra/Locations/?username='+SW_USER+'&password='+SW_PWD
        url = '%s:8081/helpdesk/WebObjects/Helpdesk.woa/ra/%s/?username=%s&password=%s' % (SW_URL, path, SW_USER,  SW_PWD )
        r = requests.post(url, data=data)
        if DEBUG:
            print '\tHTTP Status Code: %s\nResponse: %s' % (r.status_code,  r.text)
        elif r.status_code == 400:
            print '\tHTTP Status Code: %s\n\t%s' % (r.status_code, r.text)

    def update_data(self, path, data):
        #url = SW_URL+':8081/helpdesk/WebObjects/Helpdesk.woa/ra/Locations/?username='+SW_USER+'&password='+SW_PWD
        url = '%s:8081/helpdesk/WebObjects/Helpdesk.woa/ra/%s/?username=%s&password=%s' % (SW_URL, path, SW_USER,  SW_PWD )
        r = requests.put(url, data=data)
        if DEBUG:
            print '\tHTTP Status Code: %s\nResponse: %s' % (r.status_code,  r.text)
        else:
            print '\tHTTP Status Code: %s' % r.status_code
        
    def delete_data(self, id):
        url = SW_URL+':8081/helpdesk/WebObjects/Helpdesk.woa/ra/Locations/%s?username='+SW_USER+'&password='+SW_PWD % id
        r = requests.delete(url)
        if DEBUG:
            print '\tHTTP Status Code: %s\nResponse: %s' % (r.status_code,  r.text)
        else:
            print '\tHTTP Status Code: %s' % r.status_code
        


class Reader():
    def get_d42_data(self, url):
        headers = {
            'Authorization': 'Basic ' + base64.b64encode(D42_USER + ':' + D42_PWD),
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        r = requests.get(url, headers=headers, verify=False)
        msg = 'Status code: %s' % str(r.status_code)
        logger.writer(msg)
        if DEBUG:
            msg = str(r.text)
            logger.writer(msg)
        return r.text


    def search_sw_data(self, path, filter, what):
        url = '%s:8081/helpdesk/WebObjects/Helpdesk.woa/ra/%s/?qualifier=(%s %s "%s")&username=%s&password=%s' \
                % (SW_URL, path, filter, quote("="),  what, SW_USER, SW_PWD)
        r = requests.get(url)
        result = json.loads(r.text)
        #print '\n----------------------------------'
        #print result
        return result
        
    def get_all_manufacturers(self):
        url = '%s:8081/helpdesk/WebObjects/Helpdesk.woa/ra/Manufacturers/?username=%s&password=%s' \
                % (SW_URL, SW_USER, SW_PWD)
        r = requests.get(url)
        result = json.loads(r.text)
        #print '\n----------------------------------'
        #print result
        return result
        
    def get_all_types(self):
        url = '%s:8081/helpdesk/WebObjects/Helpdesk.woa/ra/AssetTypes/?username=%s&password=%s' \
                % (SW_URL, SW_USER, SW_PWD)
        r = requests.get(url)
        result = r.json()
        #print '\n----------------------------------'
        #print result
        return result
        
    def get_all_locations(self):
        url = '%s:8081/helpdesk/WebObjects/Helpdesk.woa/ra/Locations/?username=%s&password=%s' \
                % (SW_URL, SW_USER, SW_PWD)
        r = requests.get(url)
        result = r.json()
        #print '\n----------------------------------'
        #print result
        return result
        
        
    


class Utility():
    def read_config(self):
        if not os.path.exists(CONFIG_FILE):
            msg = '\n[!] Cannot find config file.Exiting...'
            print msg
            sys.exit()
            
        else:
            cc = ConfigParser.RawConfigParser()
            cc.readfp(open(CONFIG_FILE,"r"))
            
            # ------------------------------------------------------------------------
            # Device42
            D42_USER   = cc.get('device42', 'username')
            D42_PWD    = cc.get('device42', 'password')
            D42_URL     = cc.get('device42', 'url')
            
            # SolarWinds
            SW_USER   = cc.get('solarwinds', 'username')
            SW_PWD    = cc.get('solarwinds', 'password')
            SW_KEY     = cc.get('solarwinds', 'apikey')
            SW_URL     = cc.get('solarwinds', 'url')
            
            #Other
            DRY_RUN     = cc.getboolean('other', 'dry_run')
            DEBUG        = cc.getboolean('other', 'debug')
            LOGGING     = cc.getboolean('other', 'logging')
            LOGFILE      = cc.get('other', 'logfile')
            # ------------------------------------------------------------------------
            
            return D42_USER, D42_PWD, D42_URL,  SW_USER, SW_PWD, SW_KEY, SW_URL,\
                      DRY_RUN, DEBUG, LOGGING,  os.path.join(DIR, LOGFILE)


def sync_buildings():
    """
    Name mappings:
    Device42   : "Buildings"
    Solarwinds : "Locations"
    """
    buildings = reader.get_d42_data(D42_URL+'/api/1.0/buildings/')
    for building in json.loads(buildings)['buildings']:
        data = {}
        name = building['name'].lower()
        data.update({'address'        :building['address']})
        data.update({'locationName':name})
        data.update({'note'             :building['notes']})
        data.update({'phone'            :building['contact_phone']})

        result = reader.search_sw_data('Locations','locationName', name)

        if result:
            print '[!] Location "%s" already exists. Updating...' % name
            uploader.update_data('Locations',  json.dumps(data))
        else:
            print '[!] Location "%s" does not exist. Creating...' % name
            uploader.upload_data('Locations', json.dumps(data))



def sync_manufacturers():
    """
    Name mappings:
    Device42   : "Vendors"
    Solarwinds : "Manufacturers"
    """
    url = D42_URL+'/api/1.0/vendors/'
    vendors = reader.get_d42_data(url)  
    for vendor in json.loads(vendors)['vendors']:
        data = {}
        name = vendor['name'].lower()
        data.update({"fullName" : name})
        data.update({"url" : vendor['home_page']})

        try:
            result = reader.search_sw_data('Manufacturers','fullName', name)
            exists = True
            id       = json.loads(json.dumps(result))[0]['id']

        except:
            exists = None
            id = None
    
        if bool(exists) == False:
            print '[!] Manufacturer "%s" does not exist. Creating...' % name
            uploader.upload_data('Manufacturers', json.dumps(data))
        else:
            print '[!] Manufacturer "%s" already exists. Updating...' % name
            uploader.update_data('Manufacturers', json.dumps(data))



def sync_asset_types():
    """
    Name mappings:
    Device42   : "Type"
    Solarwinds : "Asset Type"
    """
    categories = [
                    u'unknown', 
                    'physical', 
                    'virtual', 
                    'blade', 
                    'cluster', 
                    'other'
                    ]
    #get existing categories
    result = reader.get_all_types()
    sw_types = [x['assetType'] for x in result]
    # get diff
    diff = set(categories) - set(sw_types)
    for type in diff:
        uploader.upload_data('AssetTypes', json.dumps({'assetType':type}))


    
def sync_models():
    """
    Name mappings:
    Device42   : "Hardware"
    Solarwinds : "Models"
    """
    # get list of known manufacturers
    result = reader.get_all_manufacturers()    
    all_manufacturers = {}
    for manufacturer in result:
        name  = manufacturer['fullName']
        if name:
            name = name.lower()
        manid = manufacturer['manufacturerId']
        all_manufacturers.update({name:manid})
    
    #get all asset types from solarwind
    types = reader.get_all_types()
    all_types = {}
    for type in types:
        t = type['assetType']
        i  = type['id']
        all_types.update({t:i})


    url = D42_URL+'/api/1.0/hardwares/'
    result = json.loads(reader.get_d42_data(url))
    models = result['models']
    
    for model in models:
        name            = model['name'].lower()
        manufacturer = model['manufacturer'].lower()
        type             = model['type'].lower()
        if type != '':
            typeid           = all_types[type]
        else:
            type = 'unknown'
            typeid = all_types[type]
        
        manid           = all_manufacturers.get(manufacturer)
        data = {"modelName"     : name,
                    "assettype"     : {"id":typeid, "type": type},
                    "manufacturer": { "id": manid, "type": manufacturer }
                    }
        
        #print data
        print '[!] Syncing model "%s"' % name
        uploader.upload_data('Models', json.dumps(data))


class Asset():
    """
    {  
    "macAddress": "macAddress", 
    "networkAddress": "networkAddress", 
    "notes": "notes", 
    "serialNumber": "serialNumber", 
    "location": { "id": 1 }, 
    "model": { "id": 1 }
    }
    """
    def __init__(self):
        pass
        
    
    def get_devices_from_d42(self):
        device_names = []
        
        url = D42_URL+'/api/1.0/hardwares/'
        result = json.loads(reader.get_d42_data(url))
        
        url = D42_URL + '/api/1.0/devices/'
        r = reader.get_d42_data(url)
        response = json.loads(r)['Devices']
        
        locations = self.get_locations_from_sw()
        
        for r in response:
            device_names.append(r['name'])
            
        for dev in device_names:
            url = D42_URL + '/api/1.0/devices/name/%s' % dev
            device = json.loads(reader.get_d42_data(url))
            if DEBUG:
                print '\n-------------------------------------------'
                print json.dumps(device, indent=4, sort_keys=True)
                print '-------------------------------------------\n'
            data = {}
            model_name = device['hw_model']
            device_name = device['name']
            if not device_name:
                print '[!] Cannot import device(asset) without name!'
                break
            if model_name:
                hwid = self.get_hwid(model_name.lower())
                data.update({'model': {'id':hwid}})
                try:
                    mac = device['ip_addresses'][0]['macaddress']
                    data.update({'macAddress':mac})
                except KeyError:
                    pass
                try:
                    ip    = device['ip_addresses'][0]['ip']
                    data.update({'networkAddress':ip})
                except KeyError:
                    pass
                try:
                    d42loc = data['location']
                    loc_id = locations[d42loc]
                    data.update({'location': {'id':loc_id}})
                except KeyError:
                    pass
                
                data.update({'notes': device['notes']})
                data.update({'serialNumber': device['serial_no']})

                data.update({'assetNumber' : device_name})
                
                self.create_asset(data, device_name)
            
            else:
                '[!] Cannot create asset without model name!'
                
  
    def get_locations_from_sw(self):
        raw = reader.get_all_locations()
        locations = {}
        for x in raw:
            location = x['locationName']
            id          = x['id'] 
            locations.update({location : id})
        return locations
        

    def get_hwid(self, model_name):
        """
        Get hardware model ID from WHD by name.
        """
        raw = reader.search_sw_data('Models', 'modelName', model_name)
        return raw[0]['id']


    def create_asset(self, data, asset_no):
        print '[!] Creating asset with asset number: "%s"' % asset_no
        uploader.upload_data('Assets', json.dumps(data))





def main():
    print '\n'
    sync_buildings()
    sync_manufacturers()
    sync_asset_types()
    sync_models()
    asset = Asset()
    asset.get_devices_from_d42()
    

if __name__ == '__main__':
    logger = Logger()
    utility  = Utility()
    reader = Reader()
    uploader = Uploader()
    
    D42_USER, D42_PWD, D42_URL,  \
    SW_USER, SW_PWD, SW_KEY, SW_URL,\
    DRY_RUN, DEBUG, LOGGING,  LOGFILE = utility.read_config()

    #print D42_USER, D42_PWD, D42_URL,  SW_USER, SW_PWD, SW_URL, DRY_RUN, DEBUG, LOGGING,  LOGFILE
    
    main()
    
    sys.exit()
