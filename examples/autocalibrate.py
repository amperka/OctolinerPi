from octoliner import Octoliner


# Create an object for working with 8-channel line sensor.
octo = Octoliner()


def main():
    try:
        while True:
            print(
                'Please enter the command "calc" to calculate the sensitivity',
                'or Ctrl^C to exit.'
            )
            command = input()
            if command == "calc":
                # Optimal sensitivity calculation.
                octo.optimize_sensitivity_on_black()
                print("Optimal sensitivity: %.2f\n" % octo.get_sensitivity())
            else:
                print("Command is invalid")
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
