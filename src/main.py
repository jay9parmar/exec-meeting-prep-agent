#!/usr/bin/env python3
"""
Exec Meeting Prep Agent - Main Entry Point
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path


class SimpleTracker:
    """Simple tracker that works without external APIs"""

    def __init__(self):
        self.tracker_file = Path(__file__).parent.parent / 'data' / 'tracker.json'
        self._ensure_tracker()

    def _ensure_tracker(self):
        if not self.tracker_file.exists():
            initial_data = {
                "meetings": [],
                "last_updated": datetime.now().isoformat(),
                "instructions": "Edit this file manually or use GitHub Actions to update automatically"
            }
            self.tracker_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.tracker_file, 'w') as f:
                json.dump(initial_data, f, indent=2)

    def load(self):
        with open(self.tracker_file, 'r') as f:
            return json.load(f)

    def save(self, data):
        with open(self.tracker_file, 'w') as f:
            json.dump(data, f, indent=2)

    def update_meeting(self, meeting_id, status):
        data = self.load()
        found = False
        for m in data['meetings']:
            if m.get('id') == meeting_id:
                m.update(status)
                found = True
                break
        if not found:
            status['id'] = meeting_id
            data['meetings'].append(status)
        data['last_updated'] = datetime.now().isoformat()
        self.save(data)
        print(f"✅ Updated meeting {meeting_id}")


def get_next_meeting_id(data):
    """Generate sequential meeting ID"""
    meeting_ids = []
    for meeting in data.get('meetings', []):
        meeting_id = meeting.get('id', '')
        if isinstance(meeting_id, str) and meeting_id.startswith('meeting_'):
            try:
                meeting_ids.append(int(meeting_id.split('_', 1)[1]))
            except ValueError:
                continue
    next_id = max(meeting_ids, default=0) + 1
    return f"meeting_{next_id:03d}"


def manual_entry_mode():
    """Allow manual entry of meetings via command line"""
    print("\n📝 Manual Meeting Entry Mode")
    print("============================")

    tracker = SimpleTracker()

    while True:
        print("\nWhat would you like to do?")
        print("1. Add a new meeting")
        print("2. Update an existing meeting")
        print("3. View all meetings")
        print("4. Generate SbS for a meeting")
        print("5. Exit")

        try:
            choice = input("\nEnter choice (1-5): ").strip()
        except EOFError:
            print("\n⚠️ No input detected. Exiting.")
            break

        if choice == '1':
            data = tracker.load()
            meeting_id = get_next_meeting_id(data)
            
            try:
                meeting = {
                    'title': input("Meeting title: "),
                    'date': input("Date (YYYY-MM-DD HH:MM): "),
                    'bm_email': input("BM email: "),
                    'agenda_ready': input("Agenda ready? (y/n): ").lower() == 'y',
                    'slides_ready': input("Slides ready? (y/n): ").lower() == 'y',
                    'bm_confirmed': input("BM confirmed? (y/n): ").lower() == 'y'
                }
            except EOFError:
                print("⚠️ Input error. Returning to menu.")
                continue

            meeting['id'] = meeting_id
            meeting['all_ready'] = meeting['agenda_ready'] and meeting['slides_ready'] and meeting['bm_confirmed']
            meeting['missing_items'] = []
            if not meeting['agenda_ready']:
                meeting['missing_items'].append('agenda')
            if not meeting['slides_ready']:
                meeting['missing_items'].append('slides')
            if not meeting['bm_confirmed']:
                meeting['missing_items'].append('BM confirmation')

            tracker.update_meeting(meeting_id, meeting)
            print(f"✅ Meeting added with ID: {meeting_id}")

        elif choice == '2':
            data = tracker.load()
            if not data['meetings']:
                print("⚠️ No meetings to update.")
                continue
            
            print("\nExisting meetings:")
            for i, m in enumerate(data['meetings']):
                print(f"{i+1}. {m.get('title', 'No title')} - Ready: {m.get('all_ready', False)}")

            try:
                idx = int(input("\nSelect meeting number: ")) - 1
            except (ValueError, EOFError):
                print("Invalid input.")
                continue
            
            if 0 <= idx < len(data['meetings']):
                meeting = data['meetings'][idx]
                print(f"\nUpdating: {meeting['title']}")
                
                try:
                    agenda_input = input(f"Agenda ready? (y/n) current: {meeting.get('agenda_ready', False)}: ").lower()
                    if agenda_input:
                        meeting['agenda_ready'] = agenda_input == 'y'
                    
                    slides_input = input(f"Slides ready? (y/n) current: {meeting.get('slides_ready', False)}: ").lower()
                    if slides_input:
                        meeting['slides_ready'] = slides_input == 'y'
                    
                    bm_input = input(f"BM confirmed? (y/n) current: {meeting.get('bm_confirmed', False)}: ").lower()
                    if bm_input:
                        meeting['bm_confirmed'] = bm_input == 'y'
                except EOFError:
                    print("Input error. Returning to menu.")
                    continue
                
                meeting['all_ready'] = meeting['agenda_ready'] and meeting['slides_ready'] and meeting['bm_confirmed']
                meeting['missing_items'] = []
                if not meeting['agenda_ready']:
                    meeting['missing_items'].append('agenda')
                if not meeting['slides_ready']:
                    meeting['missing_items'].append('slides')
                if not meeting['bm_confirmed']:
                    meeting['missing_items'].append('BM confirmation')

                tracker.save(data)
                print("✅ Meeting updated")

        elif choice == '3':
            data = tracker.load()
            print("\n📊 All Meetings:")
            print("=" * 60)
            for m in data['meetings']:
                status = "✅ READY" if m.get('all_ready') else "⚠️ PENDING"
                print(f"\n{status} - {m.get('title', 'No title')}")
                print(f"  Date: {m.get('date', 'Not set')}")
                print(f"  BM: {m.get('bm_email', 'Not set')}")
                if not m.get('all_ready'):
                    print(f"  Missing: {', '.join(m.get('missing_items', []))}")

        elif choice == '4':
            data = tracker.load()
            if not data['meetings']:
                print("⚠️ No meetings available.")
                continue
            
            print("\nSelect meeting for SbS:")
            for i, m in enumerate(data['meetings']):
                print(f"{i+1}. {m.get('title', 'No title')}")
            
            try:
                idx = int(input("Choice: ")) - 1
            except (ValueError, EOFError):
                print("Invalid input.")
                continue
            
            if 0 <= idx < len(data['meetings']):
                meeting = data['meetings'][idx]
                sbs = generate_sbs(meeting)
                print("\n" + "="*60)
                print(sbs)
                print("="*60)

                output_file = Path(__file__).parent.parent / 'outputs' / f"sbs_{meeting.get('title', 'meeting').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                output_file.parent.mkdir(exist_ok=True)
                with open(output_file, 'w') as f:
                    f.write(sbs)
                print(f"\n💾 Saved to {output_file}")

        elif choice == '5':
            break
        else:
            print("Invalid choice. Please select 1-5.")


def generate_sbs(meeting):
    """Generate Summary by Speaker for a meeting"""
    title = meeting.get('title', 'Meeting')
    date = meeting.get('date', 'TBD')
    agenda_ready = meeting.get('agenda_ready', False)
    slides_ready = meeting.get('slides_ready', False)
    bm_confirmed = meeting.get('bm_confirmed', False)
    all_ready = meeting.get('all_ready', False)
    missing_items = meeting.get('missing_items', [])

    sbs = f"""# Summary by Speaker - {title}

**Date:** {date}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Readiness Status
- Agenda: {"✅ Ready" if agenda_ready else "❌ Missing"}
- Slides: {"✅ Ready" if slides_ready else "❌ Missing"}
- BM Confirmation: {"✅ Confirmed" if bm_confirmed else "❌ Pending"}

## Overall Status: {"🟢 READY" if all_ready else "🔴 NOT READY"}

## Missing Items
{chr(10).join(['- ' + item for item in missing_items]) if missing_items else "- None"}

## Draft Notes
[To be filled during meeting]

---
*Generated by Exec Meeting Prep Agent*
*Ask Copilot to help expand this summary*
"""
    return sbs


def check_readiness():
    """Check readiness of all meetings"""
    print("🔍 Running readiness check...")
    tracker = SimpleTracker()
    data = tracker.load()

    if not data['meetings']:
        print("⚠️ No meetings found.")
        return

    print(f"\n📊 Found {len(data['meetings'])} meetings:")
    ready_count = 0
    for meeting in data['meetings']:
        status = "✅ READY" if meeting.get('all_ready') else "⚠️ PENDING"
        print(f"  {status} - {meeting.get('title')}")
        if meeting.get('all_ready'):
            ready_count += 1

    print(f"\n📈 Summary: {ready_count}/{len(data['meetings'])} meetings ready")

    # Create summary file
    summary_lines = [
        '# Meeting Readiness Summary',
        f'**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}',
        f'**Total Meetings:** {len(data["meetings"])}',
        f'**Ready:** {ready_count}',
        f'**Pending:** {len(data["meetings"]) - ready_count}',
        '',
        '## Pending Meetings:',
    ]

    for meeting in data['meetings']:
        if not meeting.get('all_ready'):
            summary_lines.append(f"- **{meeting.get('title')}**: Missing {', '.join(meeting.get('missing_items', []))}")

    summary_lines.append('')
    summary_lines.append('## Ready Meetings:')
    for meeting in data['meetings']:
        if meeting.get('all_ready'):
            summary_lines.append(f"- **{meeting.get('title')}** - All set for {meeting.get('date')}")

    output_path = Path(__file__).parent.parent / 'outputs'
    output_path.mkdir(exist_ok=True)
    summary_path = output_path / f"readiness_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(summary_path, 'w') as f:
        f.write('\n'.join(summary_lines))

    print(f"\n📄 Readiness summary saved to {summary_path}")


def generate_sbs_for_title(title):
    """Generate SbS for a meeting by title"""
    tracker = SimpleTracker()
    data = tracker.load()
    
    title_lower = title.lower()
    meeting = None
    for m in data['meetings']:
        if title_lower in m.get('title', '').lower():
            meeting = m
            break

    if not meeting:
        print(f"❌ Meeting '{title}' not found.")
        return

    sbs = generate_sbs(meeting)
    print(sbs)

    output_file = Path(__file__).parent.parent / 'outputs' / f"sbs_{meeting.get('title', 'meeting').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(sbs)
    print(f"\n💾 Saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Exec Meeting Prep Agent')
    parser.add_argument('--check-readiness', action='store_true', help='Check readiness of all meetings')
    parser.add_argument('--generate-sbs', type=str, help='Generate SbS for a specific meeting by title')
    parser.add_argument('--manual-trigger', action='store_true', help='Run check for GitHub Actions')
    args = parser.parse_args()

    if args.check_readiness:
        check_readiness()
    elif args.generate_sbs:
        generate_sbs_for_title(args.generate_sbs)
    elif args.manual_trigger:
        check_readiness()
    elif os.environ.get('GITHUB_ACTIONS') == 'true':
        check_readiness()
    else:
        manual_entry_mode()


if __name__ == '__main__':
    main()
