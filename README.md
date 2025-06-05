# ContactsBDayCalendar

This is a simple script to add birthday events of your carddav contacts to your caldav calendar.

## Usage

### Command Line

#### Nextcloud (untested)
```
python birthday_calendar.py --contacts_url https://HOST/remote.php/dav/addressbooks/users/USER/contacts/ --calendar_url https://HOST/remote.php/dav/calendars/USER/CALENDAR/ --user USER --password PASSWORD
```
#### Radicale (untested)
```
python birthday_calendar.py --contacts_url https://HOST/USER/ADDRESSBOOK-UID/ --calendar_url https://HOST/USER/CALENDAR-UID/ --user USER --password PASSWORD
```
#### Baikal
```
python birthday_calendar.py --contacts_url https://HOST/dav.php/addressbooks/USER/ADDRESSBOOK/ --calendar_url https://HOST/dav.php/calendars/USER/CALENDAR/ --user USER --password PASSWORD
```

### Docker

You can also run this script in a Docker container

```
docker run ghcr.io/coinflipcoder/calendar_bday_sync:latest --contacts_url https://HOST/remote.php/dav/addressbooks/users/USER/contacts/ --calendar_url https://HOST/remote.php/dav/calendars/USER/CALENDAR/ --user USER --password PASSWORD
```
Or with environment variables
```
docker run --env CONTACTS_URL=https://HOST/remote.php/dav/addressbooks/users/USER/contacts/ --env CALENDAR_URL=https://HOST/remote.php/dav/calendars/USER/CALENDAR/ --env USER=USER --env PASSWORD=PASSWORD ghcr.io/coinflipcoder/calendar_bday_sync:latest
```
