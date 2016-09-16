## Background
This Python Flask app aims to provide a interface to examine the relationship between a predictive model of football matches and the likely gains accured through varying the model parameters. There are four levers, 

- Prob Win - the predicted probability of a win according to the predictive model.
- Util - the difference between the bookies odds and the predictive model. 
- Bet Type - the type of bet being placed, currently limited to a series of accumulators or single bets.
- Util Type - the bookies odds used to calculate the util value, currently limited to Best, Avg and Worst bookies odds. 

Filling in these parameters will produce a gains chart as you see below. 

![Alt text](static/imgs/gains.png?raw=true "Title")

The goal is finding a set of parameters which provide a consistently rising set of gains. 

## Installation
The installation requires mostly Python 2.7.x and a suitable version of the Pip package manager. The application has been tested on Ubuntu 14.04 LTS, on a fairly modest server. To assist with deployment, and to allow the system to be deployable using [a dedicated web server](http://flask.pocoo.org/docs/0.11/deploying/mod_wsgi/), it is recommended to use the *virtualenv* environment. 

```bash
apt-get install python-dev libmysqlclient-dev
pip install MySQL-python
sudo pip install virtualenv
virtualenv venv
. venv/bin/activate
pip install Flask 
deactivate
```

### Running the web front end
To run the web-front end (it should run once you've all the libraries downloaded), 

### Supporting Libraries
The following libraries are bundled with the repository, however, if you need to check out or update the code, you can download them here. 

#### Materialize CSS
```bash
wget http://materializecss.com/bin/materialize-v0.97.7.zip
```

#### NVD3.js Library
```bash
wget https://github.com/novus/nvd3/tarball/master
```
