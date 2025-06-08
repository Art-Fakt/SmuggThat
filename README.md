# SmuggThat

**SmuggThat** is an automated tool designed for detecting HTTP Request Smuggling vulnerabilities in web applications. This vulnerability, also known as HTTP Desync Attack, occurs due to discrepancies in the processing of HTTP requests between front-end and back-end servers. The tool automates the detection and exploitation process, making it easier for penetration testers and security researchers to identify these critical vulnerabilities in their target web applications.

The tool is only based on the difference of the time reponse to detect suspicious behaviour. I will improve detection method as soon as possible, PR are welcome ;). If you test with the proxy option -p and you have smuggling detection, confirm the detection without proxy option.
All suspicious vulnerable requests are save in Reports directory so you can test each requests in context of the vulnerable web application with a tool like BurpSuite.

## Features

SmuggThat offers several core features designed to simplify the process of identifying and exploiting HTTP Request Smuggling vulnerabilities:

- **Automatic HTTP Request Smuggling Detection**: The tool uses pre-built payloads to automatically detect if a target is vulnerable to HTTP Request Smuggling attacks. It works by sending crafted requests with each payloads to the server and analyzing its time responses.
  
- **Payload Customization**: The tool comes with a default set of payloads in `payloads.json`, but users can modify or add their own payloads based on specific requirements. This makes the tool versatile in testing various server configurations.

- **Collaborator/Interact OOB Support**: The `-x` option allows you to pass a collaborator/interact.sh URL to test TE.0-redirect and other out-of-band payloads. These tests are only enabled if a collaborator/interact.sh URL is passed with the `-x` option.

- **Request Methods Customization**: The tool supports sending requests with GET, POST, PUT, and OPTIONS methods.

- **Proxy Support**: The `-p` option allows you to route all requests through an HTTP proxy (host:port).

- **Verbose Output**: Provides detailed output about the attack attempts, including HTTP responses, headers, and any signs of vulnerability detected.

- **Log and Report Generation**: Automatically generates a detailed log of each scanning session, which can be used for further analysis or reporting purposes.

## Installation

### Prerequisites

```bash
pip install -r requirements.txt
```
Clone this repository to your local machine:
```
$ git clone https://github.com/Art-Fakt/SmuggThat.git
$ cd SmuggThat
$ python3 smuggle.py -u https://target.com
```
The tool will automatically attempt various HTTP Request Smuggling techniques on the provided URL. You can also provide additional options for more advanced usage:
 - `-v`: Verbose mode, provides detailed output of each request and response.
 - `-p`: Specify a custom payload file if you want to use your own set of payloads.

## Usage

You can provide additional options for more advanced usage:

| Option         | Description                                                                                 |
|----------------|---------------------------------------------------------------------------------------------|
| `-u`           | Set the target URL (e.g., `-u https://target.com`)                                          |
| `-urls`        | Set a list of target URLs from a file (e.g., `-urls urls.txt`)                              |
| `-t`           | Set socket timeout in seconds (default: 10)                                                 |
| `-m`           | Set HTTP method (GET, POST, PUT, OPTIONS; default: POST)                                    |
| `-r`           | Set the retry count to re-execute each payload (default: 2)                                 |
| `-p`           | Set a proxy (host:port) for requests (e.g., `-p http://127.0.0.1:8080`)                     |
| `-x`           | Set collaborator/interact.sh server for OOB payloads (enables TE.0-redirect tests)          |
| `-v`           | Verbose mode, provides detailed output of each request and response                         |
| `-payloads`    | Specify a custom payload file if you want to use your own set of payloads                   |
| `-a`           | Add User-Agent and Content-type headers to each tested requests                             |

**Example:**
```bash
python3 smuggle.py -u https://target-website.com -m POST -r 3 -t 15 -p http://127.0.0.1:8080 -x https://your-collaborator-url/
```

## Payloads

The tool comes with a default set of payloads located in the `payloads.json` file. These payloads are specifically crafted to test different variations of HTTP Request Smuggling attacks. Users can modify this file to add more payloads or adjust existing ones to suit the specific environment they are testing.

Here’s an example structure of a payload:
```json
{
    "type": "CL.TE",
    "content_length_key": "Content-Length: 13",
    "transfer_encoding": {
        "te_key": "Transfer-Encoding:",
        "te_value": "chunked"
    },
    "payload": "0\r\n\r\nG"
}
```
Each payload includes the following fields:
 - **type:** A descriptive name for the payload.
 - **content_length_key:** The Content-Length header and value.
 - **transfer_encoding:** The Transfer-Encoding header and value.
 - **payload:** The body of the HTTP request.

### Supported Smuggling Techniques

The tool supports and tests for a wide range of HTTP Request Smuggling techniques, including but not limited to:
- **CL.TE**: Content-Length then Transfer-Encoding
- **TE.CL**: Transfer-Encoding then Content-Length
- **TE.TE**: Duplicate/obfuscated Transfer-Encoding headers
- **CL.0**: Content-Length set to 0
- **TE.0**: Transfer-Encoding chunked with 0-length chunk
- **TE.0-redirect**: Out-of-band redirect payloads (requires `-x` option)
- **TE.spaceobs, TE.unicode, TE.comment, TE.duplicate**: Various obfuscation and bypass techniques

You can add your own payloads to `payloads.json` to test new or custom techniques.

## Output

- Results are saved in the `Reports/` directory, organized by target and HTTP method (e.g., `Reports/POST/target.com/`).
- Each detected vulnerability or interesting response is logged with the payload used for further analysis.

## Disclaimer

This tool is intended for educational and authorized security testing purposes only. Do not use it against systems you do not have explicit permission to test.

---
