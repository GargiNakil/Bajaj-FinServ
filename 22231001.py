import pandas as pd
import re

def track_student_attendance():
    """
    Analyzes student attendance, identifies prolonged absences, and prepares messages 
    for parents with valid email addresses.
    """

    # Let's pretend we have some attendance records...
    attendance_data = {
        'student_id': [1, 1, 1, 1, 1, 2, 2, 2, 2, 2],
        'attendance_date': pd.to_datetime(['2025-03-01', '2025-03-02', '2025-03-03', '2025-03-04', '2025-03-05',
                                           '2025-03-01', '2025-03-02', '2025-03-03', '2025-03-04', '2025-03-05']),
        'status': ['Present', 'Absent', 'Absent', 'Absent', 'Present', 'Absent', 'Absent', 'Absent', 'Absent', 'Present']
    }
    attendance_df = pd.DataFrame(attendance_data)

    # First, we need to find those pesky absence streaks.
    def spot_absence_streaks(attendance_records):
        attendance_records['was_absent'] = attendance_records['status'] == 'Absent'
        attendance_records['absence_group'] = (attendance_records['was_absent'] != attendance_records['was_absent'].shift()).cumsum()
        absence_periods = attendance_records[attendance_records['was_absent']].groupby(['student_id', 'absence_group']).agg(
            start_date=('attendance_date', 'min'),
            end_date=('attendance_date', 'max'),
            days_missed=('attendance_date', 'count')
        ).reset_index()
        return absence_periods[absence_periods['days_missed'] > 3]

    long_absences = spot_absence_streaks(attendance_df)

    # Now, let's get the student info, including their parents' emails.
    student_info = {
        'student_id': [1, 2],
        'student_name': ['John Doe', 'Jane Smith'],
        'parent_email': ['parent1@gmail.com', 'invalidemail@.com']
    }
    students_df = pd.DataFrame(student_info)

    # We should probably make sure those emails are actually valid...
    def check_email(email_address):
        email_pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*@[a-zA-Z0-9]+\.com$'
        return bool(re.match(email_pattern, email_address))

    students_df['email_ok'] = students_df['parent_email'].apply(check_email)

    # Time to put it all together!
    combined_data = pd.merge(long_absences, students_df, on='student_id')
    combined_data['contact_email'] = combined_data['parent_email'].where(combined_data['email_ok'], None)

    # And finally, let's write some messages for the parents.
    def craft_message(student_record):
        if student_record['contact_email']:
            return f"Dear Parent, your child {student_record['student_name']} was absent from {student_record['start_date'].date()} to {student_record['end_date'].date()} for {student_record['days_missed']} days. Please help them catch up."
        return None

    combined_data['message'] = combined_data.apply(craft_message, axis=1)

    # Show us the results!
    final_report = combined_data[['student_id', 'start_date', 'end_date', 'days_missed', 'contact_email', 'message']]
    return final_report

# Let's run the whole thing.
attendance_report = track_student_attendance()
print(attendance_report)