import curses
import calendar
from datetime import datetime
import textwrap
import json
import os

NOTES_FILE = "notes.json"

def load_notes():
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "r") as f:
            return json.load(f)
    return {}

def save_notes(notes):
    with open(NOTES_FILE, "w") as f:
        json.dump(notes, f)

def get_date_string(year, month, day):
    return f"{year:04d}-{month:02d}-{day:02d}"

def prompt_input(stdscr, prompt_text):
    curses.echo()
    stdscr.move(curses.LINES - 2, 0)
    stdscr.clrtoeol()
    stdscr.addstr(curses.LINES - 2, 0, prompt_text)
    input_str = stdscr.getstr(curses.LINES - 2, len(prompt_text)).decode("utf-8")
    curses.noecho()
    return input_str

def prompt_note_index(stdscr, notes_list):
    if not notes_list:
        return None
    prompt = f"Select note number (1–{len(notes_list)}): "
    while True:
        index_str = prompt_input(stdscr, prompt)
        try:
            index = int(index_str) - 1
            if 0 <= index < len(notes_list):
                return index
        except ValueError:
            pass

def draw_calendar(stdscr, year, month, selected_day, notes):
    stdscr.clear()
    curses.curs_set(0)
    today = datetime.now().date()
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]

    stdscr.addstr(0, 0, f"{month_name} {year}".center(28), curses.A_BOLD)
    days = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
    for i, day in enumerate(days):
        stdscr.addstr(2, i * 4, day, curses.A_UNDERLINE)

    for row_idx, week in enumerate(cal):
        for col_idx, day in enumerate(week):
            if day == 0:
                continue
            y, x = 3 + row_idx, col_idx * 4
            attr = curses.A_NORMAL
            date_obj = datetime(year, month, day).date()
            if date_obj == today:
                attr = curses.A_REVERSE
            if day == selected_day:
                attr |= curses.A_STANDOUT
            stdscr.addstr(y, x, f"{day:2}", attr)

    selected_date = get_date_string(year, month, selected_day)
    stdscr.addstr(10, 0, f"Selected: {selected_date}", curses.A_BOLD)

    # Show notes
    row = 12
    if selected_date in notes and notes[selected_date]:
        stdscr.addstr(row, 0, "Notes:")
        for idx, note in enumerate(notes[selected_date]):
            wrapped = textwrap.wrap(note, 50)
            stdscr.addstr(row + 1, 2, f"{idx + 1}. {wrapped[0]}")
            for i, w in enumerate(wrapped[1:], 1):
                stdscr.addstr(row + 1 + i, 6, w)
            row += len(wrapped) + 1
    else:
        stdscr.addstr(row, 0, "No notes for this date.")

    stdscr.addstr(curses.LINES - 1, 0, "←↑→↓: Move  a: Add  m: Modify  d: Delete  q: Quit")
    stdscr.refresh()

def calendar_app(stdscr):
    notes = load_notes()
    now = datetime.now()
    year, month = now.year, now.month
    selected_day = now.day

    while True:
        draw_calendar(stdscr, year, month, selected_day, notes)
        key = stdscr.getch()
        max_day = calendar.monthrange(year, month)[1]

        if key == curses.KEY_RIGHT and selected_day < max_day:
            selected_day += 1
        elif key == curses.KEY_LEFT and selected_day > 1:
            selected_day -= 1
        elif key == curses.KEY_UP:
            selected_day = max(1, selected_day - 7)
        elif key == curses.KEY_DOWN:
            selected_day = min(max_day, selected_day + 7)
        elif key == ord('a'):
            date_str = get_date_string(year, month, selected_day)
            if datetime(year, month, selected_day).date() >= datetime.now().date():
                note = prompt_input(stdscr, "Add note: ")
                if note.strip():
                    notes.setdefault(date_str, []).append(note.strip())
                    save_notes(notes)
        elif key == ord('m'):
            date_str = get_date_string(year, month, selected_day)
            if datetime(year, month, selected_day).date() >= datetime.now().date():
                if date_str in notes and notes[date_str]:
                    index = prompt_note_index(stdscr, notes[date_str])
                    if index is not None:
                        new_note = prompt_input(stdscr, "Modify note: ")
                        if new_note.strip():
                            notes[date_str][index] = new_note.strip()
                            save_notes(notes)
        elif key == ord('d'):
            date_str = get_date_string(year, month, selected_day)
            if datetime(year, month, selected_day).date() >= datetime.now().date():
                if date_str in notes and notes[date_str]:
                    index = prompt_note_index(stdscr, notes[date_str])
                    if index is not None:
                        del notes[date_str][index]
                        if not notes[date_str]:
                            del notes[date_str]
                        save_notes(notes)
        elif key == ord('q'):
            break

if __name__ == "__main__":
    curses.wrapper(calendar_app)
