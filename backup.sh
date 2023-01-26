#! /bin/bash
rm backup.db
sqlite3 xanthippe.db "VACUUM INTO 'backup.db';"
sqlite3 backup.db --csv "SELECT buttons, QUOTE(screen) AS screen, requested FROM sessions ORDER BY LENGTH(buttons), buttons;" | gzip > backup.csv.gz
