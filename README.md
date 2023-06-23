# DB-Backup

Ein Python Script welches ein Dump-File von einer angegeben Datenbank macht, diese dann auch auf einem bestimmten Pfad abspeichert.
Damit wir zurück verfolgen können wann jeweils ein Backup gemacht wurden, soll es nach dem Backup auch in der Datenbank einen Datensatz hinzufügen, mit dem aktuellen Datum von letztem Backup. 
Im Anschluss wird man noch gefragt, ob man eine Bestätigungsemail will.

Zeile 81 & 91 müssen mit der Mail Addresse angepasst werden, diese Mail wird dazu verwendet um das Bestätigungsmail abzusenden.
