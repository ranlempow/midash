pushd %~dp0
python "docgen\gen.py" > doc\api\readme.md
popd