A simple script that will make a request to an API endpoint and write values to the PLC. 

What it does
    Makes a Request to an API
    Gets data from API and makes a JSON of it 
    Creates lists of the data and puts them in to a List set or Dict List set
        This allows to easily send the data to the PLC
    Makes a connection to the PLC via IP address
    Sets PLC values to 0 "ZERO" 
    Then pushes data to PLC 

