if [ ! -f ../config.json ]
then
  curdir=$(pwd)

  echo
  echo "Enter the url where you will access the server functionality minus"
  echo "the domain (something like /~username/shiftspace/server). It will be"
  echo "saved in ../config.json"
  echo
  
  read ss_url

  echo {                                                                > config.json
  echo   \"script_name\": \"$ss_url/\",                                >> config.json
  echo   \"tools.sessions.storage_path\": \"$curdir/sessions\"         >> config.json
  echo }                                                               >> config.json
fi