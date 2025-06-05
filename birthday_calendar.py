import requests
from requests.auth import HTTPDigestAuth
import vobject
from datetime import datetime, timedelta
import argparse
import os
import uuid
from typing import List, Optional

# Constants
DEFAULT_BDAY_YEAR = 1604
VCF_EXT = '.vcf'
ICS_EXT = '.ics'


def check_required_args(args: argparse.Namespace, required_fields: list[str]) -> None:
    missing = [field for field in required_fields if not getattr(args, field)]
    if missing:
        print(f"Error: Missing required arguments: {', '.join(missing)}")
        exit(1)


def parse_date(date_str: str) -> datetime:
    """Parse a date string using several common formats."""
    for date_fmt in ('%Y-%m-%d', '%Y%m%d', '--%m%d'):
        try:
            return datetime.strptime(date_str, date_fmt)
        except Exception:
            pass
    raise ValueError(f"Could not parse date {date_str}")


def list_webdav_files(url: str, user: str, password: str, extension: str) -> List[str]:
    """List all files with the given extension at the WebDAV URL."""
    response = requests.request(
        method='PROPFIND',
        url=url,
        auth=HTTPDigestAuth(user, password),
        headers={'Depth': '1'}
    )
    if response.status_code != 207:
        raise Exception(f"Failed to list files: {response.status_code} {response.reason}")
    from xml.etree import ElementTree as ET
    ns = {'d': 'DAV:'}
    tree = ET.fromstring(response.content)
    files = []
    for resp in tree.findall('d:response', ns):
        href = resp.find('d:href', ns)
        if href is not None and href.text.endswith(extension):
            files.append(href.text.split('/')[-1])
    return files


def download_vcf(url: str, filename: str, user: str, password: str) -> bytes:
    """Download a .vcf file from the given WebDAV URL."""
    file_url = url.rstrip('/') + '/' + filename
    response = requests.get(file_url, auth=HTTPDigestAuth(user, password))
    response.raise_for_status()
    return response.content


def delete_calendar_events(calendar_url: str, user: str, password: str, dry_run: bool = False) -> None:
    """Delete all .ics events from the CalDAV calendar, showing progress."""
    ics_files = list_webdav_files(calendar_url, user, password, extension=ICS_EXT)
    for idx, ics_file in enumerate(ics_files, start=1):
        print(f"Deleting event {idx}/{len(ics_files)}")
        file_url = calendar_url.rstrip('/') + '/' + ics_file
        if not dry_run:
            del_resp = requests.delete(file_url, auth=HTTPDigestAuth(user, password))
            if del_resp.status_code not in (200, 204):
                print(f"Failed to delete {ics_file}: {del_resp.status_code}")


def create_birthday_events(contacts_url: str, user: str, password: str, years: int = 2,
                           show_skipped: bool = True) -> vobject.iCalendar:
    """Create birthday events for all contacts with birthdays."""
    calendar = vobject.iCalendar()
    vcf_files = list_webdav_files(contacts_url, user, password, VCF_EXT)
    for vcf_file in vcf_files:
        vcf_data = download_vcf(contacts_url, vcf_file, user, password)
        contacts = vobject.readComponents(vcf_data.decode('utf-8'))
        for contact in contacts:
            if not hasattr(contact, 'bday'):
                if show_skipped:
                    print(f"Skipping {contact.fn.value}")
                continue
            try:
                bday = parse_date(contact.bday.value)
                print(f"Birthday found: {contact.fn.value} ({bday})")
                for i in range(years):
                    bday_year = datetime(day=bday.day, month=bday.month, year=datetime.now().year + i)
                    age = None
                    if bday.year != DEFAULT_BDAY_YEAR:
                        age = round((bday_year - bday).days / 365.25)
                    summary = f"{contact.fn.value}"
                    if age:
                        summary += f" ({age} years)"
                    uid = uuid.UUID(int=uuid.UUID(contact.uid.value).int + bday_year.year)
                    event = calendar.add('vevent')
                    event.add('summary').value = summary
                    event.add('dtstart').value = bday_year
                    event.add('dtend').value = bday_year + timedelta(days=1)
                    event.add('uid').value = str(uid)
            except ValueError as e:
                print(f"{e}: {contact.fn.value}")
                continue
    return calendar


def upload_events(calendar: vobject.iCalendar, calendar_url: str, user: str, password: str,
                  dry_run: bool = False) -> None:
    """Upload each event in the calendar as a separate .ics file."""
    for idx, event in enumerate(calendar.vevent_list, start=1):
        single_cal = vobject.iCalendar()
        single_cal.add('vevent').copy(event)
        ics_data = single_cal.serialize().replace('\n', '\r\n')
        event_uid = event.uid.value
        event_url = calendar_url.rstrip('/') + f'/{event_uid}.ics'
        print(f"Uploading event {idx}/{len(calendar.vevent_list)}")
        if not dry_run:
            put_resp = requests.put(
                event_url,
                data=ics_data.encode('utf-8'),
                headers={'Content-Type': 'text/calendar; charset=utf-8'},
                auth=HTTPDigestAuth(user, password)
            )
            if put_resp.status_code not in (200, 201, 204):
                print(f"Failed to upload event {event_uid}: {put_resp.status_code} {put_resp.reason} \n{put_resp.text}")


def main():
    parser = argparse.ArgumentParser(description='Birthday Calendar Sync')
    parser.add_argument('--contacts_url', default=os.environ.get('CONTACTS_URL'))
    parser.add_argument('--calendar_url', default=os.environ.get('CALENDAR_URL'))
    parser.add_argument('--user', default=os.environ.get('USER'))
    parser.add_argument('--password', default=os.environ.get('PASSWORD'))
    parser.add_argument('--show-skipped', default=os.environ.get('SHOW_SKIPPED'))
    parser.add_argument('--years', default=os.environ.get('YEARS'))
    parser.add_argument('--dry-run', default=os.environ.get('DRY_RUN'))
    args = parser.parse_args()

    # Check required fields
    check_required_args(args, ['contacts_url', 'calendar_url', 'user', 'password'])

    dry_run: bool = (args.dry_run or '').lower() == 'true'
    show_skipped: bool = (args.show_skipped or '').lower() == 'true'

    if dry_run:
        print("Running in dry run mode. No changes will be made.")

    print("\nCreating birthday events from contacts...")
    calendar = create_birthday_events(
        args.contacts_url,
        args.user,
        args.password,
        years=int(args.years) if args.years is not None else 2,
        show_skipped=show_skipped
    )

    print("\nAll contacts processed. Deleting all current events...")
    delete_calendar_events(args.calendar_url, args.user, args.password, dry_run=dry_run)

    print("\nAll events deleted. Uploading new events...")
    upload_events(calendar, args.calendar_url, args.user, args.password, dry_run=dry_run)

    print("\nAll done.")

    if dry_run:
        print("Dry run completed. No changes have been made.")


if __name__ == '__main__':
    main()
