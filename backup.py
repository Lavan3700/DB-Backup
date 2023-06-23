"""
    Autor: Lavan Ananthavel, Leon Good, Yannick Andres, Leart Racaj
    Datum: 05.06.2023
    Ort: Gibb Bern
    Zweck: Ein Python Script welches ein Dump-File von einer angegeben Datenbank macht, diese dann auch auf einem bestimmten Pfad abspeichert. 
    Damit wir zurück verfolgen können wann jeweils ein Backup gemacht wurden, soll es nach dem Backup auch in der Datenbank einen Datensatz 
    hinzufügen, mit dem aktuellen Datum von letztem Backup. Im Anschluss wird man noch gefragt, ob man eine Bestätigungsemail will.  
"""
import os
import re
import mysql.connector
from datetime import datetime
from mysql.connector import Error
from getpass import getpass
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Funktion: Herstellen der Verbindung zur Datenbank
def connect_to_database(host, user, password, database, port):
    try:
        # Verbindung zur MySQL-Datenbank herstellen
        connection = mysql.connector.connect(host=host,
                                             user=user,
                                             password=password,
                                             database=database,
                                             port=port)
        if connection.is_connected():
            print("Erfolgreich mit der Datenbank verbunden")
            return connection
    except Error as e:
        print("Die Verbindung zur Datenbank ist fehlerhaft:", e)

    return None

# Funktion: Erstellen der Backup-Tabelle, falls sie nicht existiert
def create_backup_table_if_not_exists(connection):
    cursor = connection.cursor()
    # SQL-Abfrage zum Erstellen der Backup-Tabelle
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Backups (
        id INT AUTO_INCREMENT PRIMARY KEY,
        backup_date DATETIME NOT NULL
    )
    """)
    connection.commit()

# Funktion: Einfügen des Backup-Datums in die Datenbank
def insert_backup_date(connection):
    cursor = connection.cursor()
    now = datetime.now()
    insert_query = "INSERT INTO Backups (backup_date) VALUES (%s)"
    # SQL-Abfrage zum Einfügen des Backup-Datums
    cursor.execute(insert_query, (now,))
    connection.commit()

# Funktion: Überprüfung der E-Mail-Adresse
def validate_email(email):
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
    if re.search(regex, email):  
        return True  
    else:  
        return False

# Funktion: Überprüfung des Dateipfads
def validate_path(path):
    regex = r'^[a-zA-Z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]*$'
    if re.match(regex, path):
        return True
    else:
        return False

# Funktion: Senden der Bestätigungs-E-Mail
def send_confirmation_email(backup_file):
    to_address = input("Bitte geben Sie Ihre E-Mail-Adresse ein: ")
    while not validate_email(to_address):
        print("Die eingegebene E-Mail-Adresse ist nicht gültig. Bitte versuchen Sie es erneut.")
        to_address = input("Bitte geben Sie Ihre E-Mail-Adresse ein: ")

    msg = MIMEMultipart()
    msg['From'] = 'MAIL@gmail.com' # MAIL SETZEN
    msg['To'] = to_address
    msg['Subject'] = 'Backup erfolgreich erstellt'
    body = f'Das Backup wurde erfolgreich erstellt und ist hier gespeichert: {backup_file}'
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Verbindung zum SMTP-Server herstellen und E-Mail senden
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(msg['From'], 'PASSWORT') # E-MAIL PASSWORT SETZEN
        text = msg.as_string()
        server.sendmail(msg['From'], msg['To'], text)
        server.quit()
        print("Bestätigungs-E-Mail wurde erfolgreich gesendet.")
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten beim Senden der Bestätigungs-E-Mail: {e}")

# Funktion: Durchführen des Datenbank-Backups
def backup_database(connection, database, password):
    while True:
        backup_path = input("Bitte geben Sie den Pfad an, wo das Backup gespeichert werden soll: ")

        if not validate_path(backup_path):
            print("Ungültiger Pfad. Bitte geben Sie einen gültigen Pfad ein.")
            continue

        if not os.path.exists(backup_path):
            print("Pfad nicht vorhanden, bitte neu eingeben.")
            continue

        break

    backup_file = os.path.join(backup_path, f"{database}_backup_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.sql")
    dump_cmd = f"mysqldump -u leon -p{password} {database} > {backup_file}"
    os.system(dump_cmd)

    if os.path.isfile(backup_file):
        print(f"Backup für die Datenbank '{database}' wurde erfolgreich erstellt.")
        insert_backup_date(connection)

        send_email = input("Möchten Sie eine Bestätigungsmail erhalten? (Ja/Nein): ").lower()
        if send_email == "ja" or send_email == "j" or send_email == "y":
            send_confirmation_email(backup_file)
        elif send_email == "nein" or send_email == "n":
            print("Keine Bestätigungsmail wird gesendet.")
        else:
            print("Ungültige Eingabe. Keine Bestätigungsmail wird gesendet.")
        
        os.system(f'explorer {os.path.realpath(backup_path)}')
    else:
        print("Es gab ein Problem beim Erstellen des Backups.")

# Funktion: Anzeigen der vorhandenen Backups
def display_backups(connection):
    cursor = connection.cursor()
    select_query = "SELECT * FROM Backups"
    cursor.execute(select_query)
    
    print("\nBackup-Daten:")
    print("-"*50)
    
    for row in cursor.fetchall():
        print(f"ID: {row[0]}, Backup-Datum: {row[1]}")

# Hauptfunktion
def main():
    host = input("Bitte geben Sie den Host der Datenbank an: ")
    user = input("Bitte geben Sie den Benutzernamen der Datenbank an: ")
    password = getpass("Bitte geben Sie das Passwort der Datenbank an: ")
    database = input("Bitte geben Sie den Namen der Datenbank an: ")
    port = int(input("Bitte geben Sie den Port der Datenbank an: "))

    # Verbindung zur Datenbank herstellen
    connection = connect_to_database(host, user, password, database, port)
    if connection:
        # Backup-Tabelle erstellen, falls sie nicht existiert
        create_backup_table_if_not_exists(connection)

        # Datenbank sichern
        backup_database(connection, database, password)

        # Backups anzeigen
        display_backups(connection) 

        # Verbindung zur Datenbank schließen
        connection.close()

if __name__ == "__main__":
    main()
