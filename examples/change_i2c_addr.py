# A command line utility that allows you to change the I2C address of the
# Octoliner board.
#
# You can use it as follows:
# $ python3 change_i2c_addr.py <old_i2c_address> <new_i2c_address>
import argparse

import octoliner


def main():
    # Create command line arguments parser.
    parser = argparse.ArgumentParser(
        description="The program changes the I2C address of the Octoliner."
    )
    # Add two positional arguments to parser.
    parser.add_argument(
        "old_addr",
        type=int,
        help="Old I2C address of the Octoliner.",
        action="store",
    )
    parser.add_argument(
        "new_addr",
        type=int,
        help="New I2C address of the Octoliner.",
        action="store",
    )
    # Parse arguments.
    args = parser.parse_args()
    # Change the I2C address of the Octoliner.
    change_i2c_addr(args.old_addr, args.new_addr)


def change_i2c_addr(old_addr, new_addr):
    octo = octoliner.Octoliner(old_addr)
    octo.change_address(new_addr)
    octo.save_address()
    print("I2C address successfully changed.")


if __name__ == "__main__":
    main()
