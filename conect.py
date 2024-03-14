import pyodbc
import sqlserverport
servername = 'myserver'
serverspec = '{0},{1}'.format(
    servername,
    sqlserverport.lookup(servername, 'SQLEXPRESS'))
conn = pyodbc.connect('DRIVER=ODBC Driver 17 for SQL Server;SERVER={};...'.format(serverspec))