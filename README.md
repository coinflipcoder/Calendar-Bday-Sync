# Calendar Bday Sync

This is a simple script to add birthday events of your carddav contacts to your caldav calendar.

## Variables
| Variable     | Description                                    | Required | Default |
|--------------|------------------------------------------------|----------|---------|
| CONTACTS_URL | The URL to your CardDAV contacts address book. | Yes      | None    |
| CALENDAR_URL | The URL to your CalDAV calendar.               | Yes      | None    |
| USER         | Your username for CardDAV and CalDAV.          | Yes      | None    |
| PASSWORD     | Your password for CardDAV and CalDAV.          | Yes      | None    |
| YEARS        | How many years should be generated.            | No       | 2       |
| SHOW_SKIPPED | If the log should include skipped contacts.    | No       | false   |
| DRY_RUN      | Does not make any changes.                     | No       | false   |

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
