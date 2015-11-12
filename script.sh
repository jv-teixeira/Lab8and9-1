#!/bin/bash

function press_enter {
	printf "\n"
	printf "Press Enter to continue"
	read
	clear
}

selection=
until [ "$selection" = "0" ]; do
	printf "Select from the menu: \n\n" 
	printf "  1) VM Connection Test\n"
	printf "  2) List all Containers\n"
	printf "  3) List Running Containers\n"
	printf "  4) Inspect a Container\n"
	printf "  5) Delete a Container\n"
	printf "  6) Delete all Containers\n"
	printf "  7) Create a Container from an Image\n"
	printf "  8) Restart a Container\n"
	printf "  9) Stop a Container\n"
	printf " 10) Show Logs from a Container\n"
	printf " 11) List all Images\n"
	printf " 12) Delete an Image\n"
	printf " 13) Delete all Images\n"
	printf " 14) TAG an Image\n"
	printf " 15) Create Docker Images from Local Dockerfile\n"
	printf " \n 99) Exit\n"

	printf "\nSelection: "
	read selection

	case $selection in
		1 ) printf "You entered one\n"
			;;
		99) exit
			;;
		* ) printf "You did not choose a valid option!\n"
	esac
done

printf "\n"
