#!/usr/bin/env python3
"""
Exec Meeting Prep Agent - Main Entry Point
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

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
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            data = tracker.load()
            existing_ids = [int(m['id'].split('_')[1]) for m in data['meetings'] if m['id'].startswith('meeting_')]
            next_id = max(existing_ids) + 1 if existing_ids else 1
            meeting_id = f"meeting_{next_id:03d}"
            
            meeting = {
                'title': input("Meeting title: "),
                'date': input("Date (YYYY-MM-DD HH:MM): "),
                'bm_email': input("BM email: "),
                'agenda_ready': input("Agenda ready? (y/n): ").lower() == 'y',
                'slides_ready': input("Slides ready? (y/n): ").lower() == 'y',
                'bm_confirmed': input("BM confirmed? (y/n): ").lower() == 'y'
            }
            
            meeting['id'] = meeting_id
            meeting['all_ready'] = meeting['agenda_ready'] and meeting['slides_ready'] and meeting['bm_confirmed']
            meeting['missing_items'] = []
            if not meeting['agenda_ready']: meeting['missing_items'].append('agenda')
            if not meeting['slides_ready']: meeting['missing_items'].append('slides')
            if not meeting['bm_confirmed']: meeting['missing_items'].append('BM confirmation')
            
            tracker.update_meeting(meeting_id, meeting)
            print(f"✅ Meeting added with ID: {meeting_id}")
            
        elif choice == '2':
            data = tracker.load()
            print("\nExisting meetings:")
            for i, m in enumerate(data['meetings']):
                print(f"{i+1}. {m.get('title', 'No title')} - Ready: {m.get('all_ready', False)}")
            
            idx = int(input("\nSelect meeting number: ")) - 1
            if 0 <= idx < len(data['meetings']):
                meeting = data['meetings'][idx]
                print(f"\nUpdating: {meeting['title']}")
                meeting['agenda_ready'] = input(f"Agenda ready? (y/n) current: {meeting.get('agenda_ready', False)}: ").lower() == 'y'
                meeting['slides_ready'] = input(f"Slides ready? (y/n) current: {meeting.get('slides_ready', False)}: ").lower() == 'y'
                meeting['bm_confirmed'] = input(f"BM confirmed? (y/n) current: {meeting.get('bm_confirmed', False)}: ").lower() == 'y'
                meeting['all_ready'] = meeting['agenda_ready'] and meeting['slides_ready'] and meeting['bm_confirmed']
                meeting['missing_items'] = []
                if not meeting['agenda_ready']: meeting['missing_items'].append('agenda')
                if not meeting['slides_ready']: meeting['missing_items'].append('slides')
                if not meeting['bm_confirmed']: meeting['missing_items'].append('BM confirmation')
                
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
            print("\nSelect meeting for SbS:")
            for i, m in enumerate(data['meetings']):
                print(f"{i+1}. {m.get('title', 'No title')}")
            idx = int(input("Choice: ")) - 1
            if 0 <= idx < len(data['meetings']):
                meeting = data['meetings'][idx]
                sbs = generate_sbs(meeting)
                print("\n" + "="*60)
                print(sbs)
                print("="*60)
                
                output_file = Path(__file__).parent.parent / 'outputs' / f"sbs_{meeting.get('title', 'meeting').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.md"
                output_file.parent.mkdir(exist_ok=True)
                with open(output_file, 'w') as f:
                    f.write(sbs)
                print(f"\n💾 Saved to {output_file}")
                
        elif choice == '5':
            break


def generate_sbs(meeting):
    """Generate Summary"""
    title = meeting.get('title', 'No title')
    date = meeting.get('date', 'Not set')
    bm_email = meeting.get('bm_email', 'Not set')
    agenda_ready = meeting.get('agenda_ready', False)
    slides_ready = meeting.get('slides_ready', False)
    bm_confirmed = meeting.get('bm_confirmed', False)
    
    sbs = f"# Meeting Summary: {title}\n\n"
    sbs += f"**Date:** {date}\n\n"
    sbs += f"**BM Email:** {bm_email}\n\n"
    
    if agenda_ready and slides_ready and bm_confirmed:
        sbs += "✅ All items are ready for the meeting.\n\n"
        sbs += "### Agenda:\n- Item 1\n- Item 2\n- Item 3\n\n"
        sbs += "### Slides:\n- Slide 1\n- Slide 2\n- Slide 3\n\n"
        sbs += "### BM Confirmation:\n- BM has confirmed attendance and is ready to present.\n"
    else:
        sbs += "⚠️ The following items are pending:\n"
        if not agenda_ready:
            sbs += "- Agenda is not ready.\n"
        if not slides_ready:
            sbs += "- Slides are not ready.\n"
        if not bm_confirmed:
            sbs += "- BM has not confirmed attendance.\n"
    
    return sbs


def check_readiness():
    """Check readiness of all meetings"""
    tracker = SimpleTracker()
    data = tracker.load()
    
    print("\n📊 Meeting Readiness Check:")
    print("=" * 60)
    
    ready_count = 0
    total = len(data['meetings'])
    
    for m in data['meetings']:
        status = "✅ READY" if m.get('all_ready') else "⚠️ PENDING"
        print(f"\n{status} - {m.get('title', 'No title')}")
        if m.get('all_ready'):
            ready_count += 1
        else:
            print(f"  Missing: {', '.join(m.get('missing_items', []))}")
    
    print(f"\nSummary: {ready_count}/{total} meetings are ready.")


def generate_sbs_for_title(title):
    """Generate SbS for a meeting by title"""
    tracker = SimpleTracker()
    data = tracker.load()
    
    for m in data['meetings']:
        if m.get('title') == title:
            sbs = generate_sbs(m)
            print(sbs)
            
            output_file = Path(__file__).parent.parent / 'outputs' / f"sbs_{title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.md"
            output_file.parent.mkdir(exist_ok=True)
            with open(output_file, 'w') as f:
                f.write(sbs)
            print(f"\n💾 Saved to {output_file}")
            return
    
    print(f"Meeting '{title}' not found.")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Exec Meeting Prep Agent')
    parser.add_argument('--check-readiness', action='store_true', help='Check readiness of all meetings')
    parser.add_argument('--generate-sbs', type=str, help='Generate SbS for a specific meeting by title')
    parser.add_argument('--manual-trigger', action='store_true', help='Run manual trigger mode')
    
    args = parser.parse_args()
    
    if args.check_readiness:
        check_readiness()
    elif args.generate_sbs:
        generate_sbs_for_title(args.generate_sbs)
    elif args.manual_trigger:
        manual_entry_mode()
    else:
        manual_entry_mode()
        print(f"✅ Updated meeting {meeting_id}")


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
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            meeting = {
                'title': input("Meeting title: "),
                'date': input("Date (YYYY-MM-DD HH:MM): "),
                'bm_email': input("BM email: "),
                'agenda_ready': input("Agenda ready? (y/n): ").lower() == 'y',
                'slides_ready': input("Slides ready? (y/n): ").lower() == 'y',
                'bm_confirmed': input("BM confirmed? (y/n): ").lower() == 'y'
            }
            
            meeting_id = f"meeting_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
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
            print("\nExisting meetings:")
            for i, m in enumerate(data['meetings']):
                print(f"{i+1}. {m.get('title', 'No title')} - Ready: {m.get('all_ready', False)}")
            
            idx = int(input("\nSelect meeting number: ")) - 1
            if 0 <= idx < len(data['meetings']):
                meeting = data['meetings'][idx]
                print(f"\nUpdating: {meeting['title']}")
                agenda_input = input(f"Agenda ready? (y/n) current: {meeting.get('agenda_ready', False)}: ").lower()
                meeting['agenda_ready'] = agenda_input == 'y' if agenda_input else meeting.get('agenda_ready', False)
                
                slides_input = input(f"Slides ready? (y/n) current: {meeting.get('slides_ready', False)}: ").lower()
                meeting['slides_ready'] = slides_input == 'y' if slides_input else meeting.get('slides_ready', False)
                
                bm_input = input(f"BM confirmed? (y/n) current: {meeting.get('bm_confirmed', False)}: ").lower()
                meeting['bm_confirmed'] = bm_input == 'y' if bm_input else meeting.get('bm_confirmed', False)
                
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
            print("\nSelect meeting for SbS:")
            for i, m in enumerate(data['meetings']):
                print(f"{i+1}. {m.get('title', 'No title')}")
            idx = int(input("Choice: ")) - 1
            if 0 <= idx < len(data['meetings']):
                meeting = data['meetings'][idx]
                sbs = generate_sbs(meeting)
                print("\n" + "="*60)
                print(sbs)
                print("="*60)
                
                output_file = Path(__file__).parent.parent / 'outputs' / f"sbs_{meeting.get('title', 'meeting').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.md"
                output_file.parent.mkdir(exist_ok=True)
                with open(output_file, 'w') as f:
                    f.write(sbs)
                print(f"\n💾 Saved to {output_file}")
                
        elif choice == '5':
            break


def generate_sbs(meeting):
    """Generate Summary by Speaker"""
    return f"""# Summary by Speaker - {meeting.get('title', 'Meeting')}

**Date:** {meeting.get('date', 'TBD')}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Readiness Status
- Agenda: {"✅ Ready" if meeting.get('agenda_ready') else "❌ Missing"}
- Slides: {"✅ Ready" if meeting.get('slides_ready') else "❌ Missing"}
- BM Confirmation: {"✅ Confirmed" if meeting.get('bm_confirmed') else "❌ Pending"}

## Overall Status: {"🟢 READY" if meeting.get('all_ready') else "🔴 NOT READY"}

## Missing Items
{chr(10).join(['- ' + item for item in meeting.get('missing_items', [])]) if meeting.get('missing_items') else '- None'}

## Draft Notes
[To be filled during meeting]

---
*Generated by Exec Meeting Prep Agent*
*Ask Copilot to help expand this summary*
"""


def main():
    print("""
    ╔══════════════════════════════════════╗
    ║   Exec Meeting Prep Agent            ║
    ║   GitHub + Copilot Compatible        ║
    ╚══════════════════════════════════════╝
    """)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--check-readiness':
            print("🔍 Running readiness check...")
            tracker = SimpleTracker()
            data = tracker.load()
            
            if not data['meetings']:
                print("⚠️ No meetings found. Use manual entry mode to add meetings.")
                print("Run: python src/main.py")
            else:
                print(f"\n📊 Found {len(data['meetings'])} meetings:")
                ready_count = 0
                for meeting in data['meetings']:
                    status = "✅ READY" if meeting.get('all_ready') else "⚠️ PENDING"
                    print(f"  {status} - {meeting.get('title')}")
                    if meeting.get('all_ready'):
                        ready_count += 1
                
                print(f"\n📈 Summary: {ready_count}/{len(data['meetings'])} meetings ready")
                
                # Create summary file for Copilot
                summary = f"""# Meeting Readiness Summary
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Total Meetings:** {len(data['meetings'])}
**Ready:** {ready_count}
**Pending:** {len(data['meetings']) - ready_count}

## Pending Meetings:
"""
                for meeting in data['meetings']:
                    if not meeting.get('all_ready'):
                        summary += f"\n- **{meeting.get('title')}**: Missing {', '.join(meeting.get('missing_items', []))}"
                
                # Add ready meetings section
                summary += "\n## Ready Meetings:\n"
                for meeting in data['meetings']:
                    if meeting.get('all_ready'):
                        summary += f"\n- **{meeting.get('title')}** - All set for {meeting.get('date')}"
                
                output_path = Path(__file__).parent.parent / 'outputs'
                output_path.mkdir(exist_ok=True)
                summary_path = output_path / f"readiness_summary_{datetime.now().strftime('%Y%m%d')}.md"
                with open(summary_path, 'w') as f:
                    f.write(summary)
                print(f"\n📄 Readiness summary saved to {summary_path}")
                
        elif sys.argv[1] == '--generate-sbs' and len(sys.argv) > 2:
            meeting_title = ' '.join(sys.argv[2:])
            print(f"📝 Generating SbS for: {meeting_title}")
            tracker = SimpleTracker()
            data = tracker.load()
            
            meeting = None
            for m in data['meetings']:
                if meeting_title.lower() in m.get('title', '').lower():
                    meeting = m
                    break
            
            if meeting:
                sbs = generate_sbs(meeting)
                print("\n" + sbs)
            else:
                print(f"❌ Meeting '{meeting_title}' not found")
                
        elif sys.argv[1] == '--manual-trigger':
            print("🎯 Running all checks...")
            tracker = SimpleTracker()
            data = tracker.load()
            print(f"\n📊 Status: {len(data['meetings'])} meetings tracked")
            print("✅ Manual check complete")
        else:
            print("Unknown command. Use --check-readiness, --generate-sbs 'title', or --manual-trigger")
    else:
        manual_entry_mode()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Exec Meeting Prep Agent')
    parser.add_argument('--check-readiness', action='store_true', help='Check readiness of all meetings')
    parser.add_argument('--generate-sbs', type=str, help='Generate SbS for a specific meeting by title')
    parser.add_argument('--manual-trigger', action='store_true', help='Run manual trigger mode')
    
    args = parser.parse_args()
    
    if args.check_readiness:
        check_readiness()
    elif args.generate_sbs:
        generate_sbs_for_title(args.generate_sbs)
    elif args.manual_trigger:
        manual_entry_mode()
    else:
        manual_entry_mode()