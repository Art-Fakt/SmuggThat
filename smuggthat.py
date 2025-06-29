import argparse
import json
import time
import os
import sys
import re
from termcolor import colored
from lib.Utils import Utils
from lib.Constants import Constants
from lib.SocketConnection import SocketConnection
from pathlib import Path
import colorama

colorama.init()

utils = Utils()
constants = Constants()

# Argument parser
parser = argparse.ArgumentParser(description='HTTP Request Smuggling vulnerability detection tool')
parser.add_argument("-u", "--url", help="set the target url")
parser.add_argument("-urls", "--urls", help="set list of target urls, i.e (urls.txt)")
parser.add_argument("-t", "--timeout", help="set socket timeout, default - 10")
parser.add_argument("-m", "--method", help="set HTTP Methods, i.e (GET or POST), default - POST")
parser.add_argument("-r", "--retry", help="set the retry count to re-execute the payload, default - 2")
parser.add_argument("-p", "--proxy", help="set a proxy (host:port) for requests")
parser.add_argument("-x", "--collaborator", help="set collaborator server for out-of-band payloads")
parser.add_argument("-a", "--addheaders", action="store_true", help="add User-Agent and Content-type headers to each request")
args = parser.parse_args()


def hrs_detection(_host, _port, _path, _method, permute_type, content_length_key, te_key, te_value, smuggle_type,
                  content_length, payload, _timeout):
    headers = ''
    headers += '{} {} HTTP/1.1{}'.format(_method, _path, constants.crlf)
    headers += 'Host: {}{}'.format(_host, constants.crlf)
    if args.addheaders:
        headers += 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.122 Safari/537.36' + constants.crlf
        headers += 'Content-type: application/x-www-form-urlencoded; charset=UTF-8' + constants.crlf
    headers += '{} {}{}'.format(content_length_key, content_length, constants.crlf)
    headers += '{}{}{}'.format(te_key, te_value, constants.crlf)
    smuggle_body = headers + payload

    permute_type = "[" + permute_type + "]"
    elapsed_time = "-"

    # Print Styling
    _style_space_config = "{:<30}{:<25}{:<25}{:<25}{:<25}"
    _style_permute_type = colored(permute_type, constants.cyan, attrs=['bold'])
    _style_smuggle_type = colored(smuggle_type, constants.magenta, attrs=['bold'])
    _style_status_code = colored("-", constants.blue, attrs=['bold'])
    _style_elapsed_time = "{}".format(colored(elapsed_time, constants.yellow, attrs=['bold']))
    _style_status = colored(constants.detecting, constants.green, attrs=['bold'])

    print(_style_space_config.format(_style_permute_type, _style_smuggle_type, _style_status_code, _style_elapsed_time,
                                     _style_status), end="\r", flush=True)

    start_time = time.time()

    try:
        connection = SocketConnection()
        connection.connect(_host, _port, _timeout)
        connection.send_payload(smuggle_body)

        response = connection.receive_data().decode("utf-8")
        end_time = time.time()

        if len(response.split()) > 0:
            status_code = response.split()[1]
        else:
            status_code = 'NO RESPONSE'
        _style_status_code = colored(status_code, constants.blue, attrs=['bold'])

        # # --- Détection améliorée ---
        # suspicious_codes = ["400", "404", "413", "500", "502", "503"]
        # is_suspicious = any(code in response for code in suspicious_codes)
        # is_short = len(response.strip()) < 20
        # if is_suspicious:
        #     _style_status = colored("Possible Smuggling (HTTP error/short)", constants.red, attrs=['bold'])
        #     _reports = constants.reports + '/{}/{}-{}-suspect{}'.format(_host, permute_type, smuggle_type, constants.extenstion)
        #     utils.write_payload(_reports, smuggle_body)

        connection.close_connection()

        # The detection logic is based on the time delay technique, if the elapsed time is more than the timeout value
        # then the target host status will change to [HRS → Vulnerable], but most of the time chances are it can be
        # false positive So to confirm the vulnerability you can use burp-suite turbo intruder and try your own
        # payloads. https://portswigger.net/web-security/request-smuggling/finding

        elapsed_time = str(round((end_time - start_time) % 60, 2)) + "s"
        _style_elapsed_time = "{}".format(colored(elapsed_time, constants.yellow, attrs=['bold']))

        is_hrs_found = connection.detect_hrs_vulnerability(start_time, _timeout)

        # If HRS found then it will write the payload to the reports directory
        if is_hrs_found:
            _style_status = colored(constants.delayed_response_msg, constants.red, attrs=['bold'])
            #_reports = constants.reports + '/{}/{}-{}{}'.format(_host, permute_type, smuggle_type, constants.extenstion)
            _reports = os.path.join(constants.reports, _host, _method, '{}-{}{}'.format(permute_type, smuggle_type, constants.extenstion))
            utils.write_payload(_reports, smuggle_body)
        else:
            _style_status = colored(constants.ok, constants.green, attrs=['bold'])
    except Exception as exception:
        elapsed_time = str(round((time.time() - start_time) % 60, 2)) + "s"
        _style_elapsed_time = "{}".format(colored(elapsed_time, constants.yellow, attrs=['bold']))

        error = f'{constants.dis_connected} → {exception}'
        _style_status = colored(error, constants.red, attrs=['bold'])

    print(_style_space_config.format(_style_permute_type, _style_smuggle_type, _style_status_code, _style_elapsed_time,
                                     _style_status))

    # There is a delay of 1 second after executing each payload
    time.sleep(1)

def connect_with_proxy(self, proxy_host, proxy_port, target_host, target_port, timeout):
    import socket
    s = socket.create_connection((proxy_host, proxy_port), timeout)
    connect_str = f"CONNECT {target_host}:{target_port} HTTP/1.1\r\nHost: {target_host}:{target_port}\r\n\r\n"
    s.sendall(connect_str.encode())
    resp = s.recv(4096)
    if b"200" not in resp:
        raise Exception("Proxy CONNECT failed")
    self.sock = s

if __name__ == "__main__":
    # If the python version less than 3.x then it will exit
    if sys.version_info < (3, 0):
        print(constants.python_version_error_msg)
        sys.exit(1)

    try:
        # Printing the tool header
        utils.print_header()

        # Both (url/urls) options not allowed at the same time
        if args.urls and args.url:
            print(constants.invalid_url_options)
            sys.exit(1)

        target_urls = list()
        if args.urls:
            urls = utils.read_target_list(args.urls)

            if constants.file_not_found in urls:
                print(f"[{args.urls}] not found in your local directory")
                sys.exit(1)
            target_urls = urls

        if args.url:
            target_urls.append(args.url)

        proxy = None
        if args.proxy:
            proxy_url = args.proxy
            # Enlève le schéma si présent (http:// ou https://)
            if proxy_url.startswith("http://"):
                proxy_url = proxy_url[len("http://"):]
            elif proxy_url.startswith("https://"):
                proxy_url = proxy_url[len("https://"):]
            if ":" not in proxy_url:
                raise Exception("Proxy must be in host:port format")
            proxy_host, proxy_port = proxy_url.split(":", 1)
            proxy_port = int(proxy_port)
            proxy = (proxy_host, proxy_port)

        if proxy:
            def connect_with_proxy_patch(self, host, port, timeout):
                connect_with_proxy(self, proxy[0], proxy[1], host, port, timeout)
            SocketConnection.connect = connect_with_proxy_patch

        for url in target_urls:
            result = utils.url_parser(url)
            try:
                json_res = json.loads(result)
                host = json_res['host']
                port = json_res['port']
                path = json_res['path']

                # If host is invalid then it will exit
                if host is None:
                    print(f"Invalid host - {host}")
                    sys.exit(1)

                method = args.method.upper() if args.method else "POST"
                allowed_methods = ["GET", "POST", "PUT", "OPTIONS"]
                if method not in allowed_methods:
                    print(constants.invalid_method_type)
                    sys.exit(1)

                timeout = int(args.timeout) if args.timeout else 10
                retry = int(args.retry) if args.retry else 2

                # To detect the HRS it requires at least 1 retry count
                if retry == 0:
                    print(constants.invalid_retry_count)
                    sys.exit(1)

                square_left_sign = colored('[', constants.cyan, attrs=['bold'])
                plus_sign = colored("+", constants.green, attrs=['bold'])
                square_right_sign = colored(']', constants.cyan, attrs=['bold'])
                square_sign = "{}{}{:<16}".format(square_left_sign, plus_sign, square_right_sign)

                target_header_style_config = '{:<1}{}{:<25}{:<16}{:<10}'
                print(target_header_style_config.format('', square_sign,
                                                        colored("Target URL", constants.magenta, attrs=['bold']),
                                                        colored(":", constants.magenta, attrs=['bold']),
                                                        colored(url, constants.blue, attrs=['bold'])))
                print(target_header_style_config.format('', square_sign,
                                                        colored("Method", constants.magenta, attrs=['bold']),
                                                        colored(":", constants.magenta, attrs=['bold']),
                                                        colored(method, constants.blue, attrs=['bold'])))
                print(target_header_style_config.format('', square_sign,
                                                        colored("Retry", constants.magenta, attrs=['bold']),
                                                        colored(":", constants.magenta, attrs=['bold']),
                                                        colored(retry, constants.blue, attrs=['bold'])))
                print(target_header_style_config.format('', square_sign,
                                                        colored("Timeout", constants.magenta, attrs=['bold']),
                                                        colored(":", constants.magenta, attrs=['bold']),
                                                        colored(timeout, constants.blue, attrs=['bold'])))

                reports = os.path.join(str(Path().absolute()), constants.reports, host)
                print(target_header_style_config.format('', square_sign,
                                                        colored("Payloads reports", constants.magenta, attrs=['bold']),
                                                        colored(":", constants.magenta, attrs=['bold']),
                                                        colored(reports, constants.blue, attrs=['bold'])))
                print()

                payloads = open('payloads.json')
                data = json.load(payloads)

                payload_list = list()

                for permute in data[constants.permute]:
                    # Skip TE.0-redirect payloads if no collaborator is set
                    if permute.get("type", "").startswith("TE.0-redirect"):
                        if not args.collaborator:
                            continue  # skip ce payload si pas de -x
                        # Remplace l'URL dans le payload par la valeur de args.collaborator
                        if "payload" in permute:
                            permute["payload"] = permute["payload"].replace("http://collaborator/", args.collaborator)

                    results = []
                    for d in data[constants.detection]:
                        if d["type"].startswith("TE.TE") and not permute["type"].startswith("TE.TE"):
                            continue
                        if not d["type"].startswith("TE.TE") and permute["type"].startswith("TE.TE"):
                            continue
                        # Skip TE.0-redirect payloads if no collaborator is set
                        if d.get("type", "").startswith("TE.0-redirect"):
                            if not args.collaborator:
                                continue  # Ne teste pas ce payload si -x n'est pas fourni
                            # Remplace l'URL dans le payload par la valeur de args.collaborator
                            if "payload" in d:
                                d["payload"] = d["payload"].replace("http://collaborator/", args.collaborator)

                        # Based on the retry value it will re-execute the same payload again
                        for _ in range(retry):
                            transfer_encoding_obj = permute[constants.transfer_encoding]
                            hrs_detection(host, port, path, method, permute[constants.type],
                                          permute[constants.content_length_key],
                                          transfer_encoding_obj[constants.te_key],
                                          transfer_encoding_obj[constants.te_value],
                                          d[constants.type],
                                          d.get(constants.content_length, ""),
                                          d.get(constants.payload, ""),
                                          timeout)

                        print("-" * 60)

            except ValueError as _:
                print(result)
    except KeyboardInterrupt as e:
        print(e)
