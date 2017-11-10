# Python Example of data persistence on Heroku and postgres.

Deploy to Heroku and add Config Variables.

* CHANNEL_SECRET => YOUR_CHANNEL_SECRET
* CHANNEL_ACCESS_TOKEN => YOUR_CHANNEL_ACCESS_TOKEN

Get them at [LINE Developers site](https://developers.line.me/), then set endpoint to deployed URL to run.

Then add Postgres Add-on via Resources > Add-ons. Search 'postgres' and provision.

Type following command with terminal to connect to DB.
```
$ heroku psql -a YOUR_HEROKU_APP_NAME
```
Once connected, create table with following command.
```
$ create table users(userid text primary key, lastmessage text);
```
