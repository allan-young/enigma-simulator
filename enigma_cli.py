#!/usr/bin/env python
"""Python script used to provide a command line interface for the
github hosted NSA enigma-simulator Python implementation.

MIT License, see the file LICENSE for details.

Copyright 2020
"""
from __future__ import print_function

import argparse
import sys
import textwrap

import machine

DESCRIPTION = textwrap.dedent("""

This Python script is provided as a convenience to run the
enigma-simulator Python implementation from the command line.  The
original project was intended to be run in a Jupyter Notebook
environment.""")

EPILOG = textwrap.dedent("""

Note that the enigma support provided allows you to select the wheels,
their order & initial letter position and also set plugboard values.
Under the covers a B reflector is used and the wheel rings are AAA.
Output is delivered to standard out (stdout).

Example usage from the command line, first using the optional "-p"
argument to prompt the user for input and the second delivering the
input text via stdin:
    $ ./enigma_cli.py -w 312 -m XYZ -s EDCTAB -p
    Enter your text and press <Enter>: ENIGMACRYPTO
    AFMCXZJQIVZA
    $ echo AFMCXZJQIVZA | ./enigma_cli.py -w 312 -m XYZ -s EDCTAB
    ENIGMACRYPTO
    $
""")

# The underlying implementation expects the wheel number to be
# provided as a list of Roman numerals.  The following is used to
# convert our decimal values.
WHEELS_DICT = {'1': 'I', '2': 'II', '3': 'III', '5': 'V'}


def process_request(args):
    """Run the provided text and key settings through the enigma, output
    results to standard out.
    """

    order = [WHEELS_DICT.get(rotor) for rotor in args.w]
    enigma = machine.Enigma(key=args.m.upper(), rotor_order=order)

    if args.s is not None:
        # Need to convert plugboard swap parameter into a list of
        # pairs.
        swaps = [args.s[i:i + 2] for i in range(0, len(args.s), 2)]
        enigma.set_plugs(swaps)

    # Check if we prompt the user for input or read from stdin.
    if args.p:
        input_buffer = raw_input("Enter your text and press <Enter>: ")
    else:
        input_buffer = ''
        for line in sys.stdin.read():
            input_buffer += line
            if input_buffer.endswith('\n'):
                input_buffer = input_buffer[:-1]

    print(enigma.encipher(input_buffer))


def valid_plugboard(plug_info):
    """Return True if the plugboard parameter looks reasonable.

    Perform a few plugboard sanity checks and return True if they
    pass, otherwise return False.  We expect the plugboard values to
    be passed as pairs of letters, all pairs packed together into a
    single string.  The underlying implementation supports a maximum
    of 6 pairs of letters.
    """
    length = len(plug_info)
    if not plug_info.isalpha() or not 2 <= length <= 12 or length % 2 == 1:
        return False

    # No letter can be used more than once, check for duplicates.
    bit_map = 0
    for character in plug_info:
        bit_offset = ord(character.upper()) - ord('A')
        if bit_map & (1 << bit_offset):
            # We've seen this offset/letter before.
            return False
        bit_map |= (1 << bit_offset)
    return True


def valid_wheel_info(wheel_info):
    """Return True if the wheel_info looks reasonable.

    Each of the three wheel values in the wheel_info string needs to
    be a digit and the only valid wheel digits will be defined in
    WHEELS_DICT.  Note that we do not check for duplicate wheels.
    """

    if len(wheel_info) != 3:
        return False
    if not wheel_info.isdigit():
        return False

    for wheel in wheel_info:
        if WHEELS_DICT.get(wheel) is None:
            return False
    return True


def main():
    """The main program, used to provide a command line interface for the
    enigma-simulator Python implementation."""

    # Leverage argparse for our argument processing needs.
    formatter = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(formatter_class=formatter,
                                     description=DESCRIPTION,
                                     epilog=EPILOG)
    parser.add_argument('-w', metavar="wheel_order", default="123",
                        help=("the 3-digit wheel order from left to right, "
                              "default is 123; each digit represents the "
                              "corresponding enigma wheel number, supported "
                              "wheel values are 1, 2, 3, and 5"))
    parser.add_argument('-m', metavar="message_key", default='AAA',
                        help=("the initial 3-letter wheel setting from "
                              "left wheel to right wheel; default is AAA"))
    parser.add_argument('-s', metavar="plugboard_pairs",
                        help=("single string consisting of one to six pairs "
                              "of letters to swap through the plugboard "
                              "(steckerbrett), default is no pairs swapped; "
                              "for example to swap A & Z and Y & B use \"-s "
                              "AZYB\""))
    parser.add_argument('-p', action='store_true',
                        help=("prompt user for text input, default is to read "
                              "directly from standard input (stdin)"))
    args = parser.parse_args()

    # Perform some elementary input value sanity checks.
    if len(args.m) != 3 or not args.m.isalpha():
        print("Invalid -m parameter, expected three letters.")
        sys.exit(1)
    if not valid_wheel_info(args.w):
        print("Invalid -w parameter, expected a three digit number. Valid "
              "digits are\n1, 2, 3, and 5.")
        sys.exit(1)
    if args.s is not None and not valid_plugboard(args.s):
        print("Invalid -s parameter, expected single string with an even "
              "number of\nletters with no duplicates, maximum letter "
              "count is 12.")
        sys.exit(1)
    process_request(args)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Ctrl-c detected, terminating program.")
        sys.exit(1)
