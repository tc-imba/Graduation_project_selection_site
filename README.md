# Graduation_project_selection_site

The site for graduation project selection in UM-SJTU JI.

The program is using python3.

## Auto install

Clone the git
```
git clone https://github.com/dbshch/Graduation_project_selection_site.git
cd Graduation_project_selection_site
```

Run the install script
```
# ./install.sh
```

Then install and config the program as the instruction.
After installation, run
```python
./main.py
```
Now you can visit <http://localhost:portnumber>. The port is set in `config.yaml`.

## Dependencies

We need

- MySQL
- Python3
- Tornado
- mysql.connector
- openpyxl
- PyYaml

To manually install them,

```python
pip install tornado openpyxl PyYaml mysql-connector-python
```


## Manual run

Firstly, clone the repo. We do not need `npm` now since dependencies have been added into this repo now (will be removed).

```
git clone https://github.com/dbshch/Graduation_project_selection_site.git
cd Graduation_project_selection_site
```

Secondly, specify your database and localhost config.

```
cp config.yaml.example config.yaml
vim config.yaml
```

and type your own config. Then use the sample.dump file to recover the sql server. For example:

```bash
mysql -uyouraccountname -ppassword database < ./sample.dump 
```

Now, you can run the server

```
python main.py
```

and visit <http://localhost:8080>. The port is set in `config.yaml`.

## Deployment

See the nginx.conf as the sample of configuration and config the /etc/nginx/nginx.conf file as needed.
