import requests

from argparse import ArgumentParser

from terminal import terminal

if __name__ == '__main__':
    # Get arguments from command line
    parser = ArgumentParser()
    # Get list of ids from command line as only argument
    parser.add_argument(nargs='+', dest="terminal_id",
                        help="Argument to get terminal id", metavar="terminal_id")
    args = vars(parser.parse_args())
    input_id = args['terminal_id']

    # Iterate over id list
    for get_id in input_id:
        # Request to get terminal data
        response = requests.get('https://api.tport.online/v2/public-stations/%s' % get_id)
        json_response = response.json()
        response_code = response.status_code
        # If response code is not 200, skip this if with an error
        if response_code != 200:
            print("Could not get terminal info by id. Id is: %s. Response code: %s" % (str(get_id), str(response_code)))
            continue
        # Initialise terminal object with json data
        current_terminal = terminal(json_response)
        status = current_terminal.get_status()
        print("Current terminal id is %s. Current terminal status is %s" %
              (str(get_id), str(status)))
        # Check if terminal is working right now
        is_working = current_terminal.is_working()
        if is_working == 1:
            print("Current terminal is working at this hours")
        elif is_working == 0:
            print("Current terminal is not working at this hours")
        else:
            print("Working hours data is not find for current terminal")
