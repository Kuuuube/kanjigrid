LINUX_DIRECTORY=~/.local/share/Anki2/addons21/1610304449/
MACOS_DIRECTORY=~/Library/Application\ Support/Anki2/addons21/1610304449/

PATHS_TO_COPY="src/*.py src/config.json data LICENSE README.md"

if [ -d "$LINUX_DIRECTORY" ]; then
  cp -r $PATHS_TO_COPY $LINUX_DIRECTORY
elif [ -d "$MACOS_DIRECTORY" ]; then
  cp -r $PATHS_TO_COPY "$MACOS_DIRECTORY"
else
  echo "Failed to send to Anki"
fi