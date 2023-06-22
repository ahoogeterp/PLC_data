import json
from pylogix import PLC
import requests
import time as tii
from datetime import datetime, time as ti
import gc

int_zero = [0]
str_zero = ["0"]

# The processing
# While True keeps the process alive 
while True:
    # tii.sleep set for 300 seconds or 5 minutes This is only the time i use for it to Request API data
    # tii.sleep(300)
    # Formatting date and time 
    now = datetime.now()
    _year_ = str(now.year).zfill(4)
    _month_ = str(now.month).zfill(2)
    _day_ = str(now.day).zfill(2)
    _hour_ = str(now.hour).zfill(2)
    _hour_1 = (now.hour-2)
    _hour_2 = str(_hour_1).zfill(2)
    _min_ = str(now.minute).zfill(2)
    _sec_ = str(now.second).zfill(2)
    #--------------------------------------------------------------------------------------------------------------------------------------------
    # Connecting to the API to pull Foss data 
    try:
        gc.collect()
        print("here we go")
        #--------------------------------------------------------------------------------------------------------------------------------------------
        try:
            # API Vars
            api_code = "Put your API code here " # .env can be used to hide sensitive info
            api_network_id = "Put your API network id here "
            endpoint_var = "225"
            start_time1 = f'{_year_}-{_month_}-{_day_}T{_hour_2}:{_min_}:{_sec_}Z'
            stop_time1 = f'{_year_}-{_month_}-{_day_}T{_hour_}:{_min_}:{_sec_}Z'
            dest_file = f'where_to_save_file/json_data/{_year_+_month_+_day_+_hour_+_min_+_sec_}_data.json' # destination file location
            
           
            # API endpoint request
            api_endpoint2 = requests.get(f'https://your-api.endpoint.net/api/Samples/{api_network_id}?from={start_time1}&to={stop_time1}&groupIds={endpoint_var}&code={api_code}')
            
            #---------------------
            # Dumping data in to JSON file 
            with open(dest_file, 'w', encoding='utf-8') as f:
                json.dump(api_endpoint2.json(), f,
                        ensure_ascii=False, indent=4)
            #---------------------
                
        except Exception as e:
            print("API_ERROR", e)
            break
        #--------------------------------------------------------------------------------------------------------------------------------------------



        #--------------------------------------------------------------------------------------------------------------------------------------------
        # Making lists of the data from the JSON sheet 
        try:
            pre_list = [('M1 FEED', 'M1_FEED'),
                        ('M1 CON', 'M1_CON'), 
                        ('M1 PERM', 'M1_PERM'), 
                        ('M2 FEED', 'M2_FEED'), 
                        ('M2 perm', 'M2_CON'), 
                        ('M2 CON', 'M2_PERM'), 
                        ('R1 CON', 'R1_CON'), 
                        ('R2 CON', 'R2_CON'), 
                        ('R3 FEED', 'R3_FEED'), 
                        ('R3 CON', 'R3_CON'), 
                        ('SI', 'SI'), 
                        ('TAN', 'TAN')]

            # Opening JSON file 
            dest_file = 'PLC_data/sample_json/sample.json' # sample used for testing, Comment out if wanting to use file made from API request 
            f = open(dest_file)

            # returns JSON object as a dictionary
            json_file = json.load(f)
            data = json_file["data"] # the name of the dict section in the sample json file.

            # Create a dictionary to store the lists
            list_dict = {}
            for p in pre_list:
                list_dict[p[1] + "_sam_string"] = []
                list_dict[p[1] + "_time_string"] = []
                list_dict[p[1] + "_type_string"] = []
                list_dict[p[1] + "_value_float"] = []

            EXTRA_sam_string = []
            EXTRA_time_string = []
            EXTRA_type_string = []
            EXTRA_value_float = []


            #---------------------
            try:
                for i in data:
                    match = False
                    for p in pre_list:
                        if i['sampleNumber'].lower().startswith(p[0].lower()):
                            # Append to the list using the dictionary
                            list_dict[p[1] + "_sam_string"].append(i['sampleNumber'])
                            list_dict[p[1] + "_time_string"].append(i['timestamp'])
                            match = True
                            for d in i['values']:
                                list_dict[p[1] + "_type_string"].append(d['name'])
                                list_dict[p[1] + "_value_float"].append(d['value'])
                    if not match:
                        EXTRA_sam_string.append(i['sampleNumber'])
                        EXTRA_time_string.append(i['timestamp'])
                        for foo in i['values']:
                            EXTRA_type_string.append(foo['name'])
                            EXTRA_value_float.append(foo['value'])

                plc_string_tag_write_values = []
                for key, value in list_dict.items():
                    if key.endswith("_sam_string"):
                        tag_name = "PLC_TAG_" + key
                        time_key = key[:-11] + "_time_string"
                        type_key = key[:-11] + "_type_string"
                        time_value = list_dict.get(time_key, [])
                        type_value = list_dict.get(type_key, [])
                        plc_string_tag_write_values.append((tag_name, value))
                        plc_string_tag_write_values.append(("PLC_TAG_" + time_key, time_value))
                        plc_string_tag_write_values.append(("PLC_TAG_" + type_key, type_value))
                
                plc_float_tag_write_values = []
                for key, value in list_dict.items():
                    if key.endswith("_value_float"):
                        tag_name = "PLC_TAG_" + key[:-12] + "_value_float"
                        plc_float_tag_write_values.append((tag_name, value))

                plc_string_tag_write_zero = []
                for key, value in list_dict.items():
                    if key.endswith("_sam_string"):
                        tag_name = "PLC_TAG_" + key
                        time_key = key[:-11] + "_time_string"
                        type_key = key[:-11] + "_type_string"
                        time_value = list_dict.get(time_key, [])
                        type_value = list_dict.get(type_key, [])
                        plc_string_tag_write_zero.append((tag_name, str_zero*10))
                        plc_string_tag_write_zero.append(("PLC_TAG_" + time_key, str_zero*10))
                        plc_string_tag_write_zero.append(("PLC_TAG_" + type_key, str_zero*10))

                plc_float_tag_write_zero = []
                for key, value in list_dict.items():
                    if key.endswith("_value_float"):
                        tag_name1 = "PLC_TAG_" + key
                        plc_float_tag_write_zero.append((tag_name1, int_zero*10))

                f.close()
                gc.collect()
                print(plc_string_tag_write_values,plc_float_tag_write_values)
            #---------------------
                # break
            except Exception as e:
                print("Error:", e)
                break
            #--------------------------------------------------------------------------------------------------------------------------------------------



            #--------------------------------------------------------------------------------------------------------------------------------------------
            # Sending data to PLC 
            try:
                ip = "xxx.xxx.xxx.xxx"
                with PLC() as comm:
                    PLC_TAG_EXTRA_wright = (("PLC_TAG_EXTRA_sam_string", EXTRA_sam_string),
                                        ("PLC_TAG_EXTRA_time_string", EXTRA_time_string),
                                        ("PLC_TAG_EXTRA_type_string", EXTRA_type_string),
                                        ("PLC_TAG_EXTRA_value_float", EXTRA_value_float))
                    # Connecting to PLC 
                    comm.IPAddress = ip
                    # writing zeros to the PLC tags
                    print()

                    comm.Write(PLC_TAG_EXTRA_wright)


                    for dt in  plc_string_tag_write_zero:
                        # print(dt)
                        comm.Write(dt[0],str_zero*10)
                    # print("Starting zero #2")

                    # comm.Write(plc_string_tag_write_zero)
                    comm.Write(plc_float_tag_write_zero)
                    tii.sleep(2)
                    # Writing data to PLC tags, lists stated up above 
                    comm.Write(plc_string_tag_write_values)
                    comm.Write(plc_float_tag_write_values)
                    comm.Close()
                    gc.collect()
                # clearing lists to keep from adding to them when pulling data from the JSON and keeping memory usage down
                EXTRA_sam_string.clear()
                EXTRA_time_string.clear()
                EXTRA_type_string.clear()
                EXTRA_value_float.clear()
                # break


            except Exception as e:
                print("PLC_ERROR", e)
                break
            #--------------------------------------------------------------------------------------------------------------------------------------------
        except Exception as e:
            print("JSON_ERROR", e)
            break
        #--------------------------------------------------------------------------------------------------------------------------------------------

    except Exception as e:
        print("Other error happened", e)
        break
    #--------------------------------------------------------------------------------------------------------------------------------------------
# TODO: Add logging to log file rather then printing everything to terminal. 
# TODO: Define functions for a more modular approach