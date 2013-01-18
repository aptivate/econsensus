Setup
-----
* pip install pytest (http://pytest.org/)
* pip install pytest-mozwebqa (https://github.com/davehunt/pytest-mozwebqa)

To run the tests
----------------
Assuming you have firefox on your local machine
Edit the credentials.yaml file with the staging admin password

 py.test --driver=firefox --credentials=credentials.yaml
