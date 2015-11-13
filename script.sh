#!/bin/bash

function press_enter {
	printf "\n"
	printf "Press Enter to continue"
	read
	clear
}

selection=
until [ "$selection" = "0" ]; do
	printf "\nSelect from the menu: \n\n" 
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
		1  ) 	telnet snf-35216.vm.okeanos-global.grnet.gr 8080 
			;;
		2  )   	curl -s -X GET -H 'Accept: application/json' http://snf-35216.vm.okeanos-global.grnet.gr:8080/containers | python -mjson.tool
			;;
		3  ) 	curl -s -X GET -H 'Accept: application/json' http://snf-35216.vm.okeanos-global.grnet.gr:8080/containers?state=running | python -mjson.tool
			;;
		4  ) 	curl -s -X GET -H 'Accept: application/json' http://snf-35216.vm.okeanos-global.grnet.gr:8080/containers/id | python -mjson.tool
			;;
		5  ) 	curl -s -X DELETE -H 'Accept: application/json' http://snf-35216.vm.okeanos-global.grnet.gr:8080/containers/contid | python -mjson.tool
			;;
		6  ) 	curl -s -X DELETE -H 'Accept: application/json' http://snf-35216.vm.okeanos-global.grnet.gr:8080/containersDel | python -mjson.tool
			;;
		7  ) 	curl -X POST -H 'Content-Type: application/json' http://snf-35216.vm.okeanos-global.grnet.gr:8080 -d '{"image": "imgID"}' | python -mjson.tool
			;;
		8  )	curl -X PATCH -H 'Content-Type: application/json' http://snf-35216.vm.okeanos-global.grnet.gr:8080/containers/b6cd8ea512c8 -d '{"state": "running"}'
			;;
		9  ) 	curl -X PATCH -H 'Content-Type: application/json' http://snf-35216.vm.okeanos-global.grnet.gr:8080/containers/b6cd8ea512c8 -d '{"state": "stopped"}'
			;;
		10 )	curl -s -X GET -H 'Accept: application/json' http://snf-35216.vm.okeanos-global.grnet.gr:8080/containers/id/logs | python -mjson.tool 
			;;
		11 )	curl -s -X GET -H 'Accept: application/json' http://snf-35216.vm.okeanos-global.grnet.gr:8080/images | python -mjson.tool
			;;
		12 )	curl -s -X DELETE -H 'Accept: application/json' http://snf-35216.vm.okeanos-global.grnet.gr:8080/images/imgID | python -mjson.tool
			;;
		13 )	curl -s -X DELETE -H 'Accept: application/json' http://snf-35216.vm.okeanos-global.grnet.gr:8080/containersDel | python -mjson.tool
			;;
		14 )	curl -s -X PATCH -H 'Content-Type: application/json' http://snf-35216.vm.okeanos-global.grnet.gr:8080/images/id -d '{"tag": "test:1.0"}'
			;;
		15 )	curl -H 'Accept: application/json' -F file=@Dockerfile http://snf-35216.vm.okeanos-global.grnet.gr:8080/images | python -mjson.tool
			;;
		99) exit
			;;
		* ) printf "You did not choose a valid option!\n"
	esac
done

printf "\n"
