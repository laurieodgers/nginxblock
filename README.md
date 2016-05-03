# NginxBlock

NginxBlock is a class for python to facilitate reading and writing of nginx config files. It was written to work on any entire nginx configurations, and also subsets of an nginx configurations, such as those usually implemented within includes files. It may also work with config files of a similar structure but is untested. 

Note that NginxBlock will only deal with one file at a time; include files are loaded in as attributes.

## Data Structure
The data structure forms a recursive heirarchy of NginxBlock objects addressable by the order that they appear within the loaded file.
```
NginxBlock()
│   error_log[0] = logs/error.log
│   pid[0] = logs/nginx.pid
│
└───http[0]
    │   include[0] = conf/mime.types
    │   index[0] = index.html index.htm index.php
    │
    ├───server[0]
    │   │   listen[0] = 80
    │   │   server_name[0] = example.com
    │   └──location['/']
    │      └──proxy_pass[0] = http://127.0.0.1:8080;
    └───server[1]
        │   listen[0] = 443
        │   server_name[0] = example.2com
        └──location['/']
           └──proxy_pass[0] = http://127.0.0.1:8080;
```

### Version
0.1.0

## License
MIT License

## Contributing
Contributions are always welcome; if you fix a bug or implement some extra functionality please issue a PR back to this repo.

## Features
  - Provides access to the config block title structure in a heirarchical format. 
  - Works with "include" files that only include a subset of nginx configuration data
  - Reads and writes nginx configuration files


### Usage

To load an nginx config:
```
nginxConfig = NginxBlock()
nginxConfig.openFile("./nginx.conf")
````

To save an nginx config:
```
nginxConfig = NginxBlock()
nginxConfig.saveFile("./nginx.conf")
````

To access the listen attribute from the first server block in the first http block
```
nginxConfig = NginxBlock()
print(nginxConfig.http[0].server[0].listen[0])
````
Or the second includes line
```
nginxConfig = NginxBlock()
print(nginxConfig.http[0].server[0].includes[1])
````

To access/print out location "/" from the second server block in the first http block
```
nginxConfig = NginxBlock()
print(nginxConfig.http[0].server[1].location['/'].toString())
```

