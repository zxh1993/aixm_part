```shell
rm -rf dist
python3.12 -m build
rm -rf dist/*tar.gz

# https://pypi.org/manage/account/token/

python3.12 -m twine upload dist/*
```
