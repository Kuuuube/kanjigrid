rm -f kanjigrid_kuuuube_0.0.0.zip
# Remove directories
zip -j kanjigrid_kuuuube_0.0.0.zip src/*.py src/config.json LICENSE README.md manifest.json
# Keep directories
zip kanjigrid_kuuuube_0.0.0.zip data/*
